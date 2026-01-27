from abc import abstractmethod

from CharacterSheetCreator import CharacterSheetData


class SpeciesBuilder:
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    @abstractmethod
    def build(self) -> CharacterSheetData:
        pass
