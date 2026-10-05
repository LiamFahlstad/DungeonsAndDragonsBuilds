from abc import abstractmethod
from typing import Optional

import Core.Definitions as Definitions
from Model.Character import Character
from Model.Grants import Grants


class SpeciesBuilder:
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    def build(self, data: Optional[Character] = None) -> Character:
        """Grant this species' traits (speed, size, features, spells) straight
        into `data` - a fresh sheet if none is given - and return it."""
        if data is None:
            data = Character()
        # Species spells aren't granted at a class level; they're stamped
        # level 1, like every other grant outside the per-level class flow,
        # and listed under the species - so a spell the class also grants
        # (Rock Gnome Prestidigitation on a Wizard) appears for both.
        self._grant(Grants(data, 1, self.name))
        return data

    @abstractmethod
    def _grant(self, data: Grants) -> None:
        pass

    def set_spell_casting_ability(self, ability: Definitions.Ability):
        self.spell_casting_ability = ability

    def set_character_level(self, level: int):
        self.character_level = level
