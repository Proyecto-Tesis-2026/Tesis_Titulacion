"""Ingestor de YouTube via yt-dlp (extracto)."""

class YoutubeIngestor(Ingestor):
    fuente: ClassVar[TipoFuente] = TipoFuente.YOUTUBE
    raw_subdir: ClassVar[str] = "youtube"
    MIN_DURATION_SEC: ClassVar[int] = 60

    def to_documento(self, item, run_id: str | None) -> Documento:
        """Concatena titulo+descripcion+transcript limpio en el Documento."""
        video = item.video
        title = collapse_whitespace(video.title)
        description = collapse_whitespace(video.description)
        # Transcripcion automatica (cuando esta disponible)
        if video.transcript.available:
            transcript_raw = video.transcript.full_text
        else:
            transcript_raw = None
        transcript = _clean_transcript(transcript_raw, self._name_replacements)
        cuerpo = collapse_whitespace(
            " ".join(p for p in (title, description, transcript) if p)
        )
        return Documento(
            id=stable_uid("youtube", video.video_id),
            fuente_tipo=TipoFuente.YOUTUBE,
            fuente_nombre="YouTube",
            fuente_cuenta=item.channel_name or video.channel,
            url=video.url,
            titulo=title,
            cuerpo=cuerpo,
            fecha_publicacion=to_utc(video.upload_date_iso),
            n_vistas=video.view_count,
            n_likes=video.like_count,
            n_comentarios=video.comment_count,
            metadata={
                "video_id": video.video_id,
                "duration_seconds": video.duration_seconds,
                "transcript_disponible": video.transcript.available,
                "transcript_auto_generado": video.transcript.is_auto_generated,
            },
            run_id=item.run_id or run_id,
        )

    def filter_pre_llm(self, doc: Documento) -> str | None:
        """Descarta videos sin transcripcion o con duracion fuera de rango."""
        meta = doc.metadata
        if not meta.get("transcript_disponible"):
            return "youtube_sin_transcript"
        dur = meta.get("duration_seconds")
        if isinstance(dur, int) and dur < self.MIN_DURATION_SEC:
            return f"youtube_muy_corto_<{self.MIN_DURATION_SEC}s"
        return None
