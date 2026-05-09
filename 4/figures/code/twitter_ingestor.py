"""Ingestor asincrono de Twitter via TwitterAPI.io (extracto)."""

class TwitterIngestor(Ingestor):
    fuente: ClassVar[TipoFuente] = TipoFuente.TWITTER
    raw_subdir: ClassVar[str] = "twitter"
    MIN_TEXT_CHARS: ClassVar[int] = 20

    def iter_raw_files(self, fecha: date) -> Iterator[Path]:
        """Itera los .json en data/raw/twitter/{fecha}/."""
        carpeta = self.day_dir(fecha)
        if not carpeta.is_dir():
            return
        yield from sorted(carpeta.glob("*.json"))

    def parse_file(self, path: Path, fecha: date):
        """Extrae todos los tweets del archivo que correspondan a la fecha."""
        raw = self.read_json(path)
        try:
            run = TwitterRunRaw.model_validate(raw)
        except ValidationError as exc:
            return [], [{"path": str(path), "error": str(exc)}]
        items, errors = [], []
        for cuenta in run.accounts:
            for tweet in cuenta.tweets:
                # Filtrado temporal con tolerancia +-1 dia respecto a la fecha objetivo
                if not date_in_range(tweet.createdAt, fecha):
                    continue
                items.append(_ItemConRun(
                    tweet=tweet, run_id=run.run_id, usuario=cuenta.username
                ))
        return items, errors

    def to_documento(self, item, run_id: str | None) -> Documento:
        """Expande URLs t.co y arma el Documento canonico."""
        tweet = item.tweet
        cuerpo = _expand_urls(tweet)
        uid = stable_uid("twitter", tweet.id_str)
        return Documento(
            id=uid,
            fuente_tipo=TipoFuente.TWITTER,
            fuente_cuenta=item.usuario,
            url=f"https://twitter.com/{item.usuario}/status/{tweet.id_str}",
            cuerpo=collapse_whitespace(cuerpo),
            fecha_publicacion=to_utc(tweet.createdAt),
            n_likes=tweet.likeCount,
            n_retweets=tweet.retweetCount,
            tags=tweet.entities.hashtags if tweet.entities else [],
            run_id=item.run_id or run_id,
        )
