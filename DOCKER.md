# Compilar la tesis con Docker

Esta guía permite compilar `tesis.tex` sin instalar TeX Live ni ningún paquete
LaTeX en tu máquina. Funciona idéntica en **macOS** (Apple Silicon y Intel),
**Linux** (Fedora, Ubuntu, etc.) y **Windows** (con Docker Desktop o WSL2).

## Requisitos

Solo Docker. Instalación según tu sistema:

| SO | Cómo |
|---|---|
| macOS | `brew install --cask docker` y abrir Docker Desktop una vez |
| Fedora | `sudo dnf install docker docker-compose-plugin` y `sudo systemctl enable --now docker` |
| Ubuntu/Debian | `sudo apt install docker.io docker-compose-plugin` |
| Windows | [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye WSL2) |

Verifica con:
```bash
docker --version
docker compose version
```

## Compilar la tesis

Desde la raíz del repo:

```bash
# (solo en Linux/Mac, una vez por sesión, para que el PDF quede como tu usuario)
export UID=$(id -u) GID=$(id -g)

# Compilar
docker compose run --rm build
```

La primera vez tarda **5–10 minutos** porque descarga la imagen
`texlive/texlive:latest` (~5 GB). Las siguientes compilaciones tardan
**30–60 segundos** porque la imagen ya está en caché.

Cuando termina, encontrarás el PDF en `output/tesis.pdf` (no en la raíz, para
mantener limpio el directorio del proyecto). Lo abrís con Preview (Mac),
Evince/Okular (Linux) o Adobe Reader (Windows). Los archivos auxiliares
(`.aux`, `.toc`, `.bbl`, etc.) también quedan en `output/`.

## Modo continuo (recomendado durante la edición)

```bash
docker compose run --rm watch
```

Este modo deja a `latexmk -pvc` corriendo: cada vez que guardás un `.tex`,
recompila automáticamente y actualiza `tesis.pdf`. Para salir: `Ctrl+C`.

## Otros comandos útiles

```bash
# Bash interactivo dentro del contenedor (debug, instalar algo, etc.):
docker compose run --rm shell

# Borrar el directorio output/ entero (PDF + aux files):
docker compose run --rm clean
```

## Qué pasa cuando ejecutás `docker compose run --rm build`

1. **Docker descarga la imagen** `texlive/texlive:latest` (solo la primera vez).
   Es la distribución oficial de TeX Live, multi-arquitectura (corre nativa en
   M1/M2/M3/M4 y en x86_64). Trae:
   - `pdflatex`, `xelatex`, `lualatex`
   - `biber` (backend de bibliografía que usa la tesis)
   - `latexmk` (orquestador de pasadas)
   - Todos los paquetes que la tesis usa: `biblatex-apa`, `tikz`, `pgf`,
     `listings`, `xurl`, `hyperref`, `siunitx`, `mathtools`, `nccmath`, `cool`,
     `babel-spanish`, `mathptmx`, `cool`, etc.

2. **Crea un contenedor temporal** con la imagen y monta el directorio actual
   del proyecto en `/work` dentro del contenedor (bind mount). Así, los
   archivos del repo son visibles dentro del contenedor y los archivos
   generados quedan en el repo cuando termina.

3. **Ejecuta `latexmk -pdf -interaction=nonstopmode tesis.tex`**, que a su vez:
   - Lee `.latexmkrc` (configuración local del proyecto).
   - Corre `pdflatex tesis.tex` (1ª pasada — escribe el `.aux` con labels).
   - Corre `biber tesis` (procesa `biblio/references.bib` y genera `.bbl`).
   - Corre `pdflatex tesis.tex` (2ª pasada — lee `.bbl`, resuelve mitad de refs).
   - Corre `pdflatex tesis.tex` (3ª pasada — resuelve TOC y cross-refs).
   - Repite hasta que todo esté estable.

4. **Genera `output/tesis.pdf`** y los archivos auxiliares (`.aux`, `.toc`,
   `.bbl`, `.bcf`, `.lof`, `.lot`, `.fdb_latexmk`, `.fls`, `.log`,
   `.synctex.gz`) en el subdirectorio `output/`. Todo eso queda en tu
   directorio local gracias al bind mount; `output/` está en `.gitignore`,
   así que no se commitea.

5. **El contenedor termina y se elimina** (`--rm`). La imagen `texlive/texlive`
   queda en caché para la próxima vez.

6. **Vos abrís `tesis.pdf`** con tu visor favorito.

Si modificás cualquier `.tex` o `.bib`, simplemente ejecutás de nuevo
`docker compose run --rm build` y el ciclo se repite (mucho más rápido la
segunda vez porque la imagen ya está descargada).

## Troubleshooting

### "permission denied" o el PDF sale como root (solo Linux)

Asegurate de exportar `UID` y `GID` antes de correr docker compose:
```bash
export UID=$(id -u) GID=$(id -g)
docker compose run --rm build
```

En Mac y Windows esto no es necesario porque Docker Desktop maneja el
mapping internamente.

### Errores "Cannot find file" o paths incorrectos en Windows

Usá PowerShell con el siguiente comando (no CMD):
```powershell
$env:UID="1000"; $env:GID="1000"; docker compose run --rm build
```

O simplemente confiá en los defaults `1000:1000` que vienen en
`docker-compose.yml`.

### La compilación falla con `?? ` en las refs

`latexmk` debería resolver todo en una sola corrida, pero si algo quedó stale:
```bash
docker compose run --rm clean
docker compose run --rm build
```

### Quiero que el PDF salga en otro lado (no `output/`)

Editá `command:` en `docker-compose.yml` cambiando `-outdir=output` por la
ruta que prefieras (relativa al repo). También editá `$out_dir` en
`.latexmkrc` para mantener coherencia si compilás sin Docker.

### Quiero usar otra imagen (más liviana, más reciente, etc.)

Editá la línea `image: texlive/texlive:latest` en `docker-compose.yml`.
Alternativas:
- `texlive/texlive:latest-basic` (~600 MB, hay que instalar paquetes faltantes con `tlmgr`).
- `registry.gitlab.com/islandoftex/images/texlive:latest` (~5 GB, mantenida por la comunidad).

## ¿Por qué Docker en lugar de instalar TeX Live local?

| Aspecto | Docker | Instalación local |
|---|---|---|
| Espacio en disco | 5 GB en caché de Docker | 5 GB en sistema |
| Reproducibilidad | Idéntica entre máquinas | Depende de versiones locales |
| Aislamiento | Sí | No (modifica `/usr/local/texlive`) |
| Velocidad de compilación | ~30–60 s | ~10–30 s (algo más rápido sin overhead) |
| Onboarding nuevos colaboradores | `docker compose run --rm build` | 30 min instalando paquetes |

Si vas a trabajar exclusivamente en una sola máquina y compilar 50 veces al
día, instalación local es más cómoda. Si rotás entre Mac, Fedora y Windows
o querés que cualquiera del equipo compile sin setup, **Docker gana por
goleada**.
