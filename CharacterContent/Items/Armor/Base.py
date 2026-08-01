from abc import ABC, abstractmethod
from typing import Optional
from Core.Definitions import Ability
from CharacterContent.Features.Core.Improvements import (
    ArmorClassBonus,
    ItemImprovement,
    SetArmorClass,
    StealthDisadvantage,
    StrengthRequirement,
    CharacterImprovement,
)
from CharacterContent.Items.Items import Item, ItemCategory, ItemRarity
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbstractArmor(Item, ABC):
    """Abstract base class for armor. Armor is a wearable item: its effects (AC
    and improvements) only apply while worn (is_wearing).

    Two independent ways to attach behavior to an armor:
    - `improvements=[...]` (list[CharacterImprovement], defined in CharacterContent.Features.Core.Improvements):
      character-affecting effects, applied to the wearer's stat block while
      worn - e.g. DragonscalePlate granting +1 Constitution, the same
      mechanism RingOfIntelligence uses in CharacterContent.Items.Items.
    - `armor_improvements=[...]` (list[ItemImprovement], defined below and in
      CharacterContent.Features.Core.Improvements): typically an ArmorImprovement - an
      armor-only effect that modifies the armor itself (AC, ability used for
      AC, Strength requirement, Stealth disadvantage, ...), not applicable to
      any other item type - but also accepts the generic ItemImprovements
      (Reskin, SetItemName, ...). See the ArmorImprovement showcase further down."""

    # Required fields every base_stats() must set; declared here (with no
    # class-level value) purely so static type checkers know they exist.
    name: str
    base_ac: int
    ac_ability: Optional[Ability]

    def __init__(
        self,
        is_wearing: bool = True,
        slots: int = 1,
        improvements: Optional[list[CharacterImprovement]] = None,
        armor_improvements: Optional[list[ItemImprovement]] = None,
    ):
        # Defaults for the fields a concrete armor's base_stats() may leave
        # unset; required fields (name, base_ac, ac_ability) have no default
        # and must always be set.
        self.is_shield: bool = False
        self.ac_bonus: int = 0
        self.strength_requirement: Optional[int] = None
        self.stealth_disadvantage: bool = False
        self.description_text: str = ""
        self.weight: Optional[float] = None
        self.value: Optional[float] = None
        self.is_homebrew: bool = False
        self.rarity: ItemRarity = ItemRarity.COMMON
        self.requires_attunement: bool = False
        # Character-affecting CharacterImprovements innate to this armor (e.g. a +1
        # bonus granted by owning Dragonscale Plate). Distinct from
        # ArmorImprovement, which modifies the armor itself, not the wearer.
        self.character_improvements: list[CharacterImprovement] = []

        self.base_stats()

        for armor_improvement in armor_improvements or []:
            self.add_armor_improvement(armor_improvement)
        self.setup_improvements()

        super().__init__(
            name=self.name,
            rarity=self.rarity,
            requires_attunement=self.requires_attunement,
            category=ItemCategory.ARMOR,
            weight=self.weight,
            slots=slots,
            description_text=self.description_text,
            improvements=self.character_improvements + list(improvements or []),
            is_wearing=is_wearing,
            is_homebrew=self.is_homebrew,
            value=self.value,
        )

    @abstractmethod
    def base_stats(self) -> None:
        """Set this armor's base (pre-improvement) attributes directly
        (self.name, self.base_ac, self.ac_ability, ...). Called once during
        __init__, before any improvement is applied."""
        raise NotImplementedError("Subclasses must implement base_stats().")

    def add_armor_improvement(self, armor_improvement: ItemImprovement) -> None:
        """Attach an ItemImprovement to this armor - typically an
        ArmorImprovement (an armor-only improvement: AC, ability used for
        AC, Strength requirement, Stealth disadvantage, ...), but also
        accepts the generic ones (Reskin, SetItemName, ...) since those
        apply to any item. Named for clarity alongside
        add_character_improvement(), which attaches an effect on the
        wearer instead."""
        self.add_improvement(armor_improvement)

    def apply(self, character_stat_block: CharacterStatBlock):
        super().apply(character_stat_block)  # CharacterImprovements (gated on is_wearing)
        if self.is_wearing:
            self.apply_worn_effects(character_stat_block)

    def apply_worn_effects(self, character_stat_block: CharacterStatBlock):
        """Apply this armor's AC and ability-based effects to the character."""
        if self.strength_requirement is not None:
            StrengthRequirement(self.strength_requirement).apply(character_stat_block)
        if self.stealth_disadvantage:
            StealthDisadvantage(reason=self.name).apply(character_stat_block)
        if self.is_shield:
            if self.ac_bonus:
                ArmorClassBonus(self.ac_bonus).apply(character_stat_block)
        else:
            SetArmorClass(self.base_ac, self.ac_ability).apply(character_stat_block)
            if self.ac_bonus:
                ArmorClassBonus(self.ac_bonus).apply(character_stat_block)


# ──────────────────────────────────────────────────────────────────────────────
# Standard Armor
# ──────────────────────────────────────────────────────────────────────────────
