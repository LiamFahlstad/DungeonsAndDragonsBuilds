from Core.Definitions import Language


class Languages:
    """Known languages, each with the sources that granted it."""

    def __init__(self):
        self.known: dict[Language, list[str]] = {}

    def add(self, language: Language, source: str) -> None:
        self.known.setdefault(language, []).append(source)

    def knows(self, language: Language) -> bool:
        return language in self.known

    def sources(self, language: Language) -> list[str]:
        return self.known.get(language, [])
