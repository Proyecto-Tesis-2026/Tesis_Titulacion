# Dockerfile minimo para compilar la tesis.
# La imagen texlive/texlive ya trae todo lo necesario (pdflatex, biber, latexmk
# y todos los paquetes biblatex-apa, tikz, listings, xurl, etc.), por lo que
# este Dockerfile es solo un wrapper en caso de querer extenderla con tools
# adicionales (ej. pandoc, pygments para minted, scripts custom).
#
# Uso (sin docker-compose):
#   docker build -t tesis-tex .
#   docker run --rm -v "$PWD":/work -w /work tesis-tex
#
# Pero lo recomendado es usar docker-compose.yml directamente, sin construir
# esta imagen, porque texlive/texlive:latest funciona "as is".

FROM texlive/texlive:latest

WORKDIR /work

# Comando por defecto: compilar tesis.tex con latexmk hacia ./output/.
# Sobrescribir desde la linea de comandos si se quiere otra cosa.
CMD ["latexmk", "-pdf", "-outdir=output", "-interaction=nonstopmode", "tesis.tex"]
