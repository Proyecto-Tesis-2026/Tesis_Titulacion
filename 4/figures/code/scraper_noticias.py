"""Ingestor de noticias web (extracto de NoticiaIngestor)."""

class NoticiaIngestor(Ingestor):
    fuente: ClassVar[TipoFuente] = TipoFuente.NOTICIA
    raw_subdir: ClassVar[str] = "noticias"
    MIN_PALABRAS: ClassVar[int] = 50

    def iter_raw_files(self, fecha: date) -> Iterator[Path]:
        """Itera todos los .json en data/raw/noticias/{fecha}/."""
        carpeta = self.day_dir(fecha)
        if not carpeta.is_dir():
            return
        yield from sorted(carpeta.glob("*.json"))

    def to_documento(self, item: NoticiaRaw, run_id: str | None) -> Documento:
        """Limpia HTML, extrae seccion desde URL y arma el Documento canonico."""
        cuerpo = _clean_html(item.cuerpo)
        seccion = item.seccion or _seccion_desde_url(item.url)
        uid = stable_uid("noticia", item.url)
        return Documento(
            id=uid,
            fuente_tipo=TipoFuente.NOTICIA,
            fuente_nombre=item.medio,
            url=item.url,
            titulo=collapse_whitespace(item.titulo),
            cuerpo=cuerpo,
            autor=item.autor,
            fecha_publicacion=to_utc(item.fecha_publicacion),
            metadata={"seccion": seccion},
            raw_id=item.url,
            run_id=run_id,
        )

    def filter_pre_llm(self, doc: Documento) -> str | None:
        """Descarta articulos con menos de MIN_PALABRAS o de seccion no politica."""
        n_palabras = _word_count(doc.cuerpo)
        if n_palabras < self.MIN_PALABRAS:
            return f"texto_corto_<{self.MIN_PALABRAS}p"
        seccion = (doc.metadata or {}).get("seccion") or ""
        return filter_irrelevant_section(seccion, SECCIONES_NO_POLITICAS_DEFAULT)
