from typing import Optional

from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import ArmorClassBonus, SetArmorClass, StealthDisadvantage, StrengthRequirement
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbstractArmor(Feature):
    """An abstract class for armor features."""

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description


class LeatherArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Leather Armor")
        self._ac = SetArmorClass(11, Ability.DEXTERITY)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class StuddedLeatherArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Studded Leather Armor")
        self._ac = SetArmorClass(12, Ability.DEXTERITY)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class ChainMailArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Chain Mail Armor")
        self._str_req = StrengthRequirement(13)
        self._stealth = StealthDisadvantage()
        self._ac = SetArmorClass(16, ability=None)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._str_req.apply(character_stat_block)
        self._stealth.apply(character_stat_block)
        self._ac.apply(character_stat_block)


class ShieldArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Shield")
        self._bonus = ArmorClassBonus(2)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._bonus.apply(character_stat_block)
