from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureUses,
    FeatureActivation,
    FeatureTarget,
)
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FiendExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="The Fiend Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Fiend lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Fiend Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tBurning Hands, Command\n"
            "2nd\tBlindness/Deafness, Scorching Ray\n"
            "3rd\tFireball, Stinking Cloud\n"
            "4th\tFire Shield, Wall of Fire\n"
            "5th\tFlame Strike, Hallow"
        )
        return description


class DarkOnesBlessing(Feature):
    def __init__(self):
        super().__init__(
            name="Dark One's Blessing",
            origin="The Fiend Patron Warlock Level 3",
            usage_tags=["heal"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reduce a hostile creature to 0 Hit Points, you gain Temporary Hit Points equal to your Charisma modifier + your Warlock level (minimum of 1)."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DarkOnesOwnLuck(Feature):
    def __init__(self):
        super().__init__(
            name="Dark One's Own Luck",
            origin="The Fiend Patron Warlock Level 6",
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call on your patron to alter fate in your favor. When you make an ability check or a saving throw, you can use this feature to add a d10 to your roll. You can do so after seeing the initial roll but before any of the roll's effects occur.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Ability check or saving throw"),
            ("Effect", "Add d10 to the roll"),
            ("Timing", "After seeing roll, before effects"),
            ("Recharge", "Short or long rest"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FiendishResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Fiendish Resilience",
            origin="The Fiend Patron Warlock Level 10",
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can choose one damage type when you finish a Short or Long Rest. You gain Resistance to that damage type until you choose a different one with this feature. Damage from magical weapons or silver weapons ignores this Resistance."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class HurlThroughHell(Feature):
    def __init__(self):
        super().__init__(
            name="Hurl Through Hell",
            origin="The Fiend Patron Warlock Level 14",
            activation=FeatureActivation(duration="Until End of Next Turn"),
            usage_tags=["damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you hit a creature with an attack, you can use this feature to instantly transport the target through the lower planes. The creature disappears and hurtles through a nightmare landscape.\n"
            "At the end of your next turn, the target returns to the space it previously occupied, or the nearest unoccupied space. If the target is not a fiend, it takes 10d10 Psychic damage as it reels from its horrific experience.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Hit a creature with an attack"),
            ("Effect", "Transport target through lower planes"),
            ("Duration", "Until end of your next turn"),
            ("Damage", "10d10 Psychic if target is not a fiend"),
            ("Recharge", "Long rest"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
