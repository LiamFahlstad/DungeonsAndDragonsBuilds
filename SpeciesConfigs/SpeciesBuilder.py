from abc import abstractmethod

import Definitions
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

    def set_spell_casting_ability(self, ability: Definitions.Ability):
        self.spell_casting_ability = ability

    def set_character_level(self, level: int):
        self.character_level = level
