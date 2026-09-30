from abc import abstractmethod
from typing import Optional

import Core.Definitions as Definitions
from Builds.CharacterSheetAccumulator import CharacterSheetData


class SpeciesBuilder:
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    def build(self, data: Optional[CharacterSheetData] = None) -> CharacterSheetData:
        """Grant this species' traits (speed, size, features, spells) straight
        into `data` - a fresh sheet if none is given - and return it."""
        if data is None:
            data = CharacterSheetData()
        # Species spells aren't granted at a class level; tag them level 1,
        # like every other grant outside the per-level class flow.
        data.set_current_grant_level(1)
        with data.separate_spell_source():
            self._grant(data)
        return data

    @abstractmethod
    def _grant(self, data: CharacterSheetData) -> None:
        pass

    def set_spell_casting_ability(self, ability: Definitions.Ability):
        self.spell_casting_ability = ability

    def set_character_level(self, level: int):
        self.character_level = level
