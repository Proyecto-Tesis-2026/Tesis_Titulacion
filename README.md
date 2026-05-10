# Tesis de Titulación

Repositorio fuente de la tesis en LaTeX. El documento principal es `tesis.tex`
y el PDF compilado se genera en `output/tesis.pdf`.

---

## Compilar con Docker (recomendado)

No requiere instalar TeX Live ni ningún paquete LaTeX. Solo necesitás Docker.

```bash
# Solo en Linux — exportar UID/GID para que el PDF no quede como root
export UID=$(id -u) GID=$(id -g)

# Compilar una vez
docker compose run --rm build

# Recompilar automáticamente al guardar un .tex
docker compose run --rm watch

# Limpiar output/ completo
docker compose run --rm clean
```

El PDF queda en `output/tesis.pdf`. La primera vez tarda 5–10 min descargando
la imagen (~5 GB). Las siguientes compilaciones tardan 30–60 s.

Para más detalle (troubleshooting, opciones, explicación del proceso):
→ [`DOCKER.md`](DOCKER.md)

---

## Compilar sin Docker (instalación local)

### Requisitos

- **TeX Live 2023 o superior** con los esquemas `full` o al menos los paquetes:
  `biblatex`, `biber`, `latexmk`, `babel-spanish`, `mathptmx`, `tikz`,
  `pgf`, `listings`, `xurl`, `hyperref`, `caption`, `subcaption`,
  `booktabs`, `multirow`, `setspace`, `enumitem`, `longtable`, `pdflscape`,
  `adjustbox`, `csquotes`, `etoolbox`, `amssymb`, `eucal`, `nccmath`,
  `cool`, `siunitx`, `mathtools`, `fancyhdr`, `titlesec`, `newclude`

| SO | Instalación |
|---|---|
| macOS | `brew install --cask mactex` (MacTeX completo) |
| Fedora | `sudo dnf install texlive-scheme-full` |
| Ubuntu/Debian | `sudo apt install texlive-full biber` |
| Windows | [MiKTeX](https://miktex.org/) o [TeX Live](https://tug.org/texlive/) |

### Compilar

```bash
latexmk -pdf -outdir=output -interaction=nonstopmode tesis.tex
```

`latexmk` se encarga de correr `pdflatex` + `biber` las veces necesarias
hasta resolver todas las referencias y la bibliografía.

### Limpiar archivos auxiliares

```bash
latexmk -C -outdir=output
```

---

## Estructura del proyecto

```
tesis.tex          # Documento principal
biblio/
  references.bib   # Base de datos bibliográfica
0/–6/              # Capítulos (0 = portada/resumen, 1–6 = cuerpo)
anexos/            # Anexos
images_repo/       # Imágenes estáticas
output/            # PDF y archivos auxiliares generados (gitignoreado)
docker-compose.yml # Servicios Docker (build, watch, shell, clean)
DOCKER.md          # Guía completa de uso con Docker
```

---

## Flujo de trabajo recomendado

1. Editar los `.tex` del capítulo correspondiente
2. Compilar con `docker compose run --rm build` (o `watch` para modo continuo)
3. Revisar `output/tesis.pdf`
4. Commitear solo los `.tex` y `.bib` — el `output/` está en `.gitignore`
