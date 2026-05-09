# Config de latexmk para la tesis.
# Uso: `latexmk -pdf tesis.tex`  (o sin args si esta es la unica raiz).

# Compilador principal
$pdf_mode = 1;          # genera PDF directamente con pdflatex
$pdflatex = 'pdflatex -interaction=nonstopmode -synctex=1 %O %S';

# Backend de bibliografia: biber (no bibtex). biblatex con backend=biber lo exige.
$bibtex_use = 2;        # corre biber/bibtex aunque la BD no haya cambiado si hay refs sin resolver
$biber = 'biber --validate-datamodel %O %S';

# Asegurar pasadas suficientes para resolver refs cruzadas y TOC/LOF/LOT.
$max_repeat = 6;

# Documento principal explicito (por si lo invocan sin argumento)
@default_files = ('tesis.tex');

# Directorio de salida: tesis.pdf y aux files van a ./output/ para mantener
# limpia la raiz del repo. Se respeta tambien con docker-compose.
$out_dir = 'output';

# Extensiones extra a limpiar con `latexmk -c` y `latexmk -C`
# (paquetes locales de la tesis: cool/mathtools producen estos, mas los .pytxcode de pythontex)
$clean_ext = "bbl bbl-SAVE-ERROR run.xml bcf eqflts equ loeqfloat loequcaption lomycapequ pytxcode synctex.gz";
