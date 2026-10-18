from Core.Definitions import DRUID_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class CircleForms(Feature):
    def __init__(self):
        super().__init__(
            name="Circle Forms",
            origin="Circle of the Moon Druid Level 3",
            usage_tags=["buff", "heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Channel lunar magic when you assume a Wild Shape form. Your Wild Shape stat blocks already include these."
            ),
            Facts(
                (
                    ("Max Challenge Rating", "Druid level ÷ 3, rounded down"),
                    (
                        "Armor Class",
                        "13 + Wisdom modifier, if higher than the Beast's AC, until you leave the form",
                    ),
                    ("Temporary Hit Points", "Three times your Druid level"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can channel lunar magic when you assume a Wild Shape form, granting you the benefits below.\n"
            "Challenge Rating. The maximum Challenge Rating for the form equals your Druid level divided by 3 (round down).\n"
            "Armor Class. Until you leave the form, your AC equals 13 plus your Wisdom modifier if that total is higher than the Beast's AC.\n"
            "Temporary Hit Points. You gain a number of Temporary Hit Points equal to three times your Druid level."
        )
        return description


class CircleOfTheMoonSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Circle of the Moon Spells", origin="Circle of the Moon Druid Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Druid level shown, you always have these spells prepared. You can cast them while in a Wild Shape form."
            ),
            Table(
                ("Druid level", "Spells"),
                (
                    ("3", "Cure Wounds, Moonbeam, Starry Wisp"),
                    ("5", "Conjure Animals"),
                    ("7", "Fount of Moonlight"),
                    ("9", "Mass Cure Wounds"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Druid level specified in the Circle of the Moon Spells table, you thereafter always have the listed spells prepared.\n"
            "In addition, you can cast the spells from this feature while you're in a Wild Shape form."
        )
        return description


class ImprovedCircleForms(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Circle Forms",
            origin="Circle of the Moon Druid Level 6",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While in a Wild Shape form:"),
            Facts(
                (
                    (
                        "Lunar Radiance",
                        "Each of your attacks can deal its normal damage type or Radiant damage (choose each time you hit)",
                    ),
                    (
                        "Increased Toughness",
                        "Add your Wisdom modifier to your Constitution saving throws",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "While in a Wild Shape form, you gain the following benefits.\n"
            "Lunar Radiance. Each of your attacks in a Wild Shape form can deal its normal damage type or Radiant damage. You make this choice each time you hit with those attacks.\n"
            "Increased Toughness. You can add your Wisdom modifier to your Constitution saving throws."
        )
        return description


class MoonlightStep(Feature):
    def __init__(self):
        super().__init__(
            name="Moonlight Step",
            origin="Circle of the Moon Druid Level 10",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph("Reappear amid a burst of moonlight."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Effect",
                        "Teleport up to 30 feet to an unoccupied space you can see, then have Advantage on your next attack roll this turn",
                    ),
                    (
                        "Uses",
                        "Wisdom modifier (minimum once) per Long Rest; expend a level 2+ spell slot to restore one (no action required)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You magically transport yourself, reappearing amid a burst of moonlight. As a Bonus Action, you teleport up to 30 feet to an unoccupied space you can see, and you have Advantage on the next attack roll you make before the end of this turn.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest. You can also regain uses by expending a level 2+ spell slot for each use you want to restore (no action required)."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class LunarForm(Feature):
    def __init__(self):
        super().__init__(
            name="Lunar Form",
            origin="Circle of the Moon Druid Level 14",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Improved Lunar Radiance",
                        "Once per turn, deal an extra 2d10 Radiant damage to a target you hit with a Wild Shape form's attack",
                    ),
                    (
                        "Shared Moonlight",
                        "When you use Moonlight Step, also teleport one willing creature within 10 feet of you to an unoccupied space you can see within 10 feet of your destination",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The power of the moon suffuses you, granting you the following benefits.\n"
            "Improved Lunar Radiance. Once per turn, you can deal an extra 2d10 Radiant damage to a target you hit with a Wild Shape form's attack.\n"
            "Shared Moonlight. Whenever you use Moonlight Step, you can also teleport one willing creature. That creature must be within 10 feet of you, and you teleport it to an unoccupied space you can see within 10 feet of your destination space."
        )
        return description
