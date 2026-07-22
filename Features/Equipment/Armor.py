from typing import Optional

from Core.Definitions import Ability
from Features.Core.SubFeatures import (
    ArmorClassBonus,
    SetArmorClass,
    StealthDisadvantage,
    StrengthRequirement,
    SubFeature,
)
from Features.Items.Items import WearableItem
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbstractArmor(WearableItem):
    """Base class for armor. Armor is a wearable item: its effects (AC and
    subfeatures) only apply while it is worn."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        slots: int = 1,
        rarity: str = "common",
        subfeatures: Optional[list[SubFeature]] = None,
        is_shield: bool = False,
        is_wearing: bool = True,
    ):
        super().__init__(
            name=name,
            rarity=rarity,
            category="armor",
            slots=slots,
            description_text=description or "",
            subfeatures=subfeatures or [],
            is_wearing=is_wearing,
        )
        # Keep old interface for backward compatibility
        self.description = description or ""
        self.is_shield = is_shield

    def apply(self, character_stat_block: CharacterStatBlock):
        super().apply(character_stat_block)  # Subfeatures (gated on is_wearing)
        if self.is_wearing:
            self.apply_worn_effects(character_stat_block)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        """Armor-specific effects (AC etc.) that only apply while worn."""


class LeatherArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Leather Armor", slots=1)
        self._ac = SetArmorClass(11, Ability.DEXTERITY)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class StuddedLeatherArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Studded Leather Armor", slots=1)
        self._ac = SetArmorClass(12, Ability.DEXTERITY)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class ChainShirtArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Chain Shirt Armor", slots=1)
        self._ac = SetArmorClass(13, Ability.DEXTERITY)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        self._ac.apply(character_stat_block)


class ChainMailArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Chain Mail Armor", slots=2)  # Heavier armor takes more space
        self._str_req = StrengthRequirement(13)
        self._stealth = StealthDisadvantage(reason=self.name)
        self._ac = SetArmorClass(16, ability=None)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        self._str_req.apply(character_stat_block)
        self._stealth.apply(character_stat_block)
        self._ac.apply(character_stat_block)


class ShieldArmor(AbstractArmor):
    def __init__(self):
        super().__init__("Shield", slots=1, is_shield=True)
        self._bonus = ArmorClassBonus(2)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        self._bonus.apply(character_stat_block)


# ──────────────────────────────────────────────────────────────────────────────
# Magical Armor
# ──────────────────────────────────────────────────────────────────────────────


class ArmorOfProtection(AbstractArmor):
    """Magical chain mail that grants an additional +1 to AC."""

    def __init__(self):
        super().__init__(
            "Armor of Protection",
            slots=2,
            rarity="rare",
            description=(
                "A magical suit of chain mail. While wearing it, you gain a +1 bonus to AC "
                "on top of its base AC of 16."
            ),
        )
        self.requires_attunement = True
        self._str_req = StrengthRequirement(13)
        self._stealth = StealthDisadvantage(reason=self.name)
        self._ac = SetArmorClass(16, ability=None)
        self._ac_bonus = ArmorClassBonus(1)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        self._str_req.apply(character_stat_block)
        self._stealth.apply(character_stat_block)
        self._ac.apply(character_stat_block)
        self._ac_bonus.apply(character_stat_block)
