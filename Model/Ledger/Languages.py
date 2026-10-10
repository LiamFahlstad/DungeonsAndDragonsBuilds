from Core.Definitions import Language


class Languages:
    """Known languages, each with the sources that granted it.

    Merge rule: set union per language, keeping every source. Reads list
    languages in enum order and sources sorted."""

    def __init__(self):
        self._known: dict[Language, list[str]] = {}

    @property
    def known(self) -> dict[Language, list[str]]:
        return {
            language: sorted(self._known[language])
            for language in Language
            if language in self._known
        }

    def add(self, language: Language, source: str) -> None:
        self._known.setdefault(language, []).append(source)

    def knows(self, language: Language) -> bool:
        return language in self._known

    def sources(self, language: Language) -> list[str]:
        return sorted(self._known.get(language, []))
