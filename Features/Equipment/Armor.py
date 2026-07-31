from abc import ABC, abstractmethod
from typing import Optional

from Core.Definitions import Ability, Skill
from Features.Core.Improvements import (
    AbilityScoreBonus,
    AddItemDescription,
    ArmorClassBonus,
    ItemImprovement,
    Reskin,
    SavingThrowAdvantage,
    SetArmorClass,
    SetItemHomebrew,
    SetItemName,
    SetItemValue,
    SkillBonus,
    StealthDisadvantage,
    StrengthRequirement,
    CharacterImprovement,
)
from Features.Items.Items import Item, ItemCategory, ItemRarity
from StatBlocks.CharacterStatBlock import CharacterStatBlock


# ──────────────────────────────────────────────────────────────────────────────
# ArmorImprovement: composable modifiers applied to an armor at construction
# time (e.g. a magic armor variant, or a homebrew reskin). Mirrors
# Features.Core.Improvements.CharacterImprovement, but its apply() mutates the armor
# instance instead of the character stat block, since these improvements
# (AC, ability modifiers, names, descriptions) are properties of the armor
# itself, not of the wielder.
# ──────────────────────────────────────────────────────────────────────────────


class ArmorImprovement(ItemImprovement):
    """Base class for armor improvements. Override apply() to modify the armor."""

    @abstractmethod
    def apply(self, armor: "AbstractArmor") -> None:
        pass


class SetArmorClassBase(ArmorImprovement):
    """Overrides the armor's base AC and ability modifier outright."""

    def __init__(self, base: int, ability: Optional[Ability]):
        self.base = base
        self.ability = ability

    def apply(self, armor: "AbstractArmor") -> None:
        armor.base_ac = self.base
        armor.ac_ability = self.ability


class AddArmorClassBonus(ArmorImprovement):
    """Adds a flat bonus to the armor's AC, stacking on top of its own ac_bonus."""

    def __init__(self, value: int, reason: str = "Bonus"):
        self.value = value
        self.reason = reason

    def apply(self, armor: "AbstractArmor") -> None:
        armor.ac_bonus += self.value


class SetStrengthRequirement(ArmorImprovement):
    """Overrides the armor's Strength requirement. Pass None to remove any requirement."""

    def __init__(self, min_score: Optional[int]):
        self.min_score = min_score

    def apply(self, armor: "AbstractArmor") -> None:
        armor.strength_requirement = self.min_score


class SetStealthDisadvantage(ArmorImprovement):
    """Overrides whether the armor imposes stealth disadvantage."""

    def __init__(self, value: bool = True):
        self.value = value

    def apply(self, armor: "AbstractArmor") -> None:
        armor.stealth_disadvantage = self.value


class AbstractArmor(Item, ABC):
    """Abstract base class for armor. Armor is a wearable item: its effects (AC
    and improvements) only apply while worn (is_wearing).

    Two independent ways to attach behavior to an armor:
    - `improvements=[...]` (list[CharacterImprovement], defined in Features.Core.Improvements):
      character-affecting effects, applied to the wearer's stat block while
      worn - e.g. DragonscalePlate granting +1 Constitution, the same
      mechanism RingOfIntelligence uses in Features.Items.Items.
    - `armor_improvements=[...]` (list[ArmorImprovement], defined below):
      armor-only effects that modify the armor itself (AC, ability used for
      AC, Strength requirement, Stealth disadvantage, ...) - not applicable
      to any other item type. See the ArmorImprovement showcase further down."""

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
        armor_improvements: Optional[list[ArmorImprovement]] = None,
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
        # bonus granted by owning Armor of Protection). Distinct from
        # ArmorImprovement, which modifies the armor itself, not the wearer.
        self._innate_improvements: list[CharacterImprovement] = []

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
            improvements=self._innate_improvements + list(improvements or []),
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

    def add_armor_improvement(self, armor_improvement: "ArmorImprovement") -> None:
        """Attach an ArmorImprovement - an armor-only improvement (AC,
        ability used for AC, Strength requirement, Stealth disadvantage,
        ...) - to this armor. Named for clarity alongside
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


class LeatherArmor(AbstractArmor):
    """Light armor made of hardened leather."""

    def base_stats(self) -> None:
        self.name = "Leather Armor"
        self.base_ac = 11
        self.ac_ability = Ability.DEXTERITY
        self.weight = 10
        self.value = 10


class StuddedLeatherArmor(AbstractArmor):
    """Light armor of leather studded with metal."""

    def base_stats(self) -> None:
        self.name = "Studded Leather Armor"
        self.base_ac = 12
        self.ac_ability = Ability.DEXTERITY
        self.weight = 13
        self.value = 45


class ChainShirtArmor(AbstractArmor):
    """Medium armor made of mail rings sewn into a shirt."""

    def base_stats(self) -> None:
        self.name = "Chain Shirt Armor"
        self.base_ac = 13
        self.ac_ability = Ability.DEXTERITY
        self.weight = 20
        self.value = 50


class ChainMailArmor(AbstractArmor):
    """Heavy armor made of interlocking metal rings."""

    def __init__(self, **kwargs):
        super().__init__(slots=2, **kwargs)  # Heavier armor takes more space

    def base_stats(self) -> None:
        self.name = "Chain Mail Armor"
        self.base_ac = 16
        self.ac_ability = None
        self.strength_requirement = 13
        self.stealth_disadvantage = True
        self.weight = 55
        self.value = 75


class ShieldArmor(AbstractArmor):
    """A wooden or metal shield held in one hand."""

    def base_stats(self) -> None:
        self.name = "Shield"
        self.base_ac = 0
        self.ac_ability = None
        self.is_shield = True
        self.ac_bonus = 2
        self.weight = 6
        self.value = 10


# ──────────────────────────────────────────────────────────────────────────────
# Magical Armor
# ──────────────────────────────────────────────────────────────────────────────


class ArmorOfProtection(AbstractArmor):
    """Magical chain mail that grants an additional +1 to AC."""

    def __init__(self, **kwargs):
        super().__init__(slots=2, **kwargs)

    def base_stats(self) -> None:
        self.name = "Armor of Protection"
        self.base_ac = 16
        self.ac_ability = None
        self.ac_bonus = 1
        self.strength_requirement = 13
        self.stealth_disadvantage = True
        self.weight = 55
        self.rarity = ItemRarity.RARE
        self.requires_attunement = True
        self.description_text = (
            "A magical suit of chain mail. While wearing it, you gain a +1 bonus to AC "
            "on top of its base AC of 16."
        )


class DragonscalePlate(AbstractArmor):
    """Medium armor crafted from dragon scales, granting draconic resilience."""

    def base_stats(self) -> None:
        self.name = "Dragonscale Plate"
        self.base_ac = 14
        self.ac_ability = Ability.DEXTERITY
        self.weight = 45
        self.value = None
        self.rarity = ItemRarity.RARE
        self.requires_attunement = True
        self.description_text = (
            "Fashioned from the scales of an ancient dragon, this armor shimmers "
            "with iridescent light and radiates a faint warmth. A wearer attuned to it "
            "gains a +1 bonus to Constitution and resistance to one damage type of your choice."
        )
        self.add_character_improvement(
            AbilityScoreBonus(
                [(Ability.CONSTITUTION, 1)],
                total=1,
                error_prefix="Dragonscale Plate bonus",
            )
        )


class SentinelsWatchArmor(ChainShirtArmor):
    """Magical Chain Shirt demonstrating a character-affecting improvement
    (`_innate_improvements`, i.e. the armor's own `improvements=` - the same
    mechanism RingOfIntelligence uses) rather than an ArmorImprovement: it
    sharpens the wearer's own senses, not the armor's AC."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.add_character_improvement(
            SkillBonus(Skill.PERCEPTION, 2, source="Sentinel's Watch Armor")
        )

    def setup_improvements(self) -> None:
        self.add_armor_improvement(
            Reskin(
                "Sentinel's Watch Armor",
                "Enchanted mail rings chime faintly at the edge of hearing, sharpening "
                "the wearer's senses. While wearing it, you gain a +2 bonus to Wisdom "
                "(Perception) checks.",
            )
        )


class StalwartsAegis(ChainMailArmor):
    """Magical Chain Mail demonstrating a different character-affecting
    improvement (SavingThrowAdvantage): it steels the wearer's resolve,
    granting Advantage on Wisdom saving throws rather than changing
    anything about the armor's own AC."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.RARE
        self.requires_attunement = True
        self.add_character_improvement(SavingThrowAdvantage([Ability.WISDOM]))

    def setup_improvements(self) -> None:
        self.add_armor_improvement(
            Reskin(
                "Stalwart's Aegis",
                "This breastplate radiates a calm, unshakable resolve. While wearing "
                "it, you have Advantage on Wisdom saving throws.",
            )
        )


# ──────────────────────────────────────────────────────────────────────────────
# ArmorImprovement showcase: one armor per improvement, demonstrating how
# `armor_improvements=[...]` composes on top of an armor's base_stats().
# ──────────────────────────────────────────────────────────────────────────────


class ReinforcedBulwark(ChainMailArmor):
    """A Chain Mail variant demonstrating SetArmorClassBase: overrides AC to a
    fixed value with no ability modifier."""

    def setup_improvements(self) -> None:
        self.add_armor_improvement(SetArmorClassBase(18, ability=None))
        self.add_armor_improvement(
            Reskin(
                "Reinforced Bulwark",
                "Thickened with additional steel plating, this chain mail armor "
                "provides an unvarying AC of 18, independent of your abilities.",
            )
        )


class WardensBuckler(ShieldArmor):
    """A Shield variant demonstrating AddArmorClassBonus: adds a bonus on top
    of the shield's own AC bonus."""

    def setup_improvements(self) -> None:
        self.add_armor_improvement(AddArmorClassBonus(1, "Guardian Blessing"))
        self.add_armor_improvement(
            Reskin(
                "Warden's Buckler",
                "Blessed by a protective deity, this small shield grants +3 to your AC "
                "(the usual +2 from a shield, plus an additional +1 from divine blessing).",
            )
        )


class GiantkinPlate(ChainMailArmor):
    """A Chain Mail variant demonstrating SetStrengthRequirement: raises the
    minimum Strength requirement for a wearer sized for giants."""

    def setup_improvements(self) -> None:
        self.add_armor_improvement(SetStrengthRequirement(15))
        self.add_armor_improvement(
            Reskin(
                "Giantkin Plate",
                "Sized for a wearer of great stature, this armor requires a Strength "
                "score of 15 or higher to wear effectively.",
            )
        )


class ShadowplateMail(ChainMailArmor):
    """A Chain Mail variant demonstrating SetStealthDisadvantage(False): removes
    the Stealth disadvantage normally imposed by heavy armor."""

    def setup_improvements(self) -> None:
        self.add_armor_improvement(SetStealthDisadvantage(False))
        self.add_armor_improvement(
            Reskin(
                "Shadowplate Mail",
                "Crafted from a dark metal that absorbs sound, this chain mail "
                "imposes no disadvantage on Stealth checks despite its weight.",
            )
        )


class VeteransChainShirt(ChainShirtArmor):
    """A Chain Shirt variant demonstrating AddArmorDescription: extra text is
    appended to the base armor's description."""

    def setup_improvements(self) -> None:
        # Use individual improvements rather than Reskin (which replaces
        # description) to preserve and append to the base description.
        self.add_armor_improvement(SetItemName("Veteran's Chain Shirt"))
        self.add_armor_improvement(SetItemValue(None))
        self.add_armor_improvement(SetItemHomebrew())
        self.add_armor_improvement(
            AddItemDescription("Scarred from countless campaigns, this armor bears the marks of an experienced warrior.")
        )
        self.add_armor_improvement(
            AddItemDescription(
                "Once per long rest, you can attune to the armor's memories: ask it one "
                "yes/no question about a creature that wore it previously, and it answers truthfully."
            )
        )
