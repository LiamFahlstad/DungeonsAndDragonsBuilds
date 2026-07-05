from typing import Optional

from Definitions import Ability
from Features.Core.SubFeatures import ArmorClassBonus, SetArmorClass, StealthDisadvantage, StrengthRequirement, SubFeature
from Features.Items.Items import Item
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbstractArmor(Item):
    """Base class for armor, inheriting from Item for shared inventory mechanics."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        slots: int = 1,
        rarity: str = "common",
        subfeatures: Optional[list[SubFeature]] = None,
    ):
        super().__init__(
            name=name,
            rarity=rarity,
            category="armor",
            slots=slots,
            description_text=description or "",
            subfeatures=subfeatures or [],
        )
        # Keep old interface for backward compatibility
        self.description = description or ""


class LeatherArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Leather Armor", slots=1)
        self._ac = SetArmorClass(11, Ability.DEXTERITY)

    def apply(self, character_stat_block: CharacterStatBlock):
        super().apply(character_stat_block)  # Apply Item subfeatures
        self._ac.apply(character_stat_block)


class StuddedLeatherArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Studded Leather Armor", slots=1)
        self._ac = SetArmorClass(12, Ability.DEXTERITY)

    def apply(self, character_stat_block: CharacterStatBlock):
        super().apply(character_stat_block)  # Apply Item subfeatures
        self._ac.apply(character_stat_block)


class ChainMailArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Chain Mail Armor", slots=2)  # Heavier armor takes more space
        self._str_req = StrengthRequirement(13)
        self._stealth = StealthDisadvantage()
        self._ac = SetArmorClass(16, ability=None)

    def apply(self, character_stat_block: CharacterStatBlock):
        super().apply(character_stat_block)  # Apply Item subfeatures
        self._str_req.apply(character_stat_block)
        self._stealth.apply(character_stat_block)
        self._ac.apply(character_stat_block)


class ShieldArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Shield", slots=1)
        self._bonus = ArmorClassBonus(2)

    def apply(self, character_stat_block: CharacterStatBlock):
        super().apply(character_stat_block)  # Apply Item subfeatures
        self._bonus.apply(character_stat_block)
