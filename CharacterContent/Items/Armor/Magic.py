import Core.Definitions as Definitions
from Core.Definitions import Ability, Skill
from CharacterContent.Features.Core.Improvements import (
    AbilityScoreBonus,
    AddItemDescription,
    Reskin,
    SavingThrowAdvantage,
    SetItemHomebrew,
    SetItemName,
    SetItemValue,
    SkillBonus,
)
from CharacterContent.Items.Items import ItemRarity
from .Base import AbstractArmor
from .Improvements import AddArmorClassBonus, SetArmorClassBase, SetStealthDisadvantage, SetStrengthRequirement
from .Standard import ChainMailArmor, ChainShirtArmor, ShieldArmor


class ArmorOfProtection(AbstractArmor):
    """Magical chain mail that grants an additional +1 to AC."""

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
        self.armor_type = Definitions.ArmorType.HEAVY


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
        self.armor_type = Definitions.ArmorType.MEDIUM
        self.add_character_improvement(
            AbilityScoreBonus(
                [(Ability.CONSTITUTION, 1)],
                total=1,
                error_prefix="Dragonscale Plate bonus",
            )
        )


class SentinelsWatchArmor(ChainShirtArmor):
    """Magical Chain Shirt demonstrating a character-affecting improvement
    (`character_improvements`, i.e. the armor's own `improvements=` - the
    same mechanism RingOfIntellect uses) rather than an ArmorImprovement: it
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
