from Core.Definitions import Ability, CharacterClass, FIGHTER_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
    FeatureDice,
)
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph

SUPERIORITY_DIE = FeatureDice(
    "Superiority Die",
    (
        (3, "d8"),
        (10, "d10"),
        (18, "d12"),
    ),
    CharacterClass.FIGHTER,
)


class SuperiorityDice(Feature):
    def __init__(self):
        self.maneuvers = []
        super().__init__(
            name="Superiority Dice",
            origin="Battle Master Fighter Level 3",
            uses=FeatureUses(
                max_uses=6,
                regain_all_on="short or long rest",
                current_formula="Current amount: 4, increasing to 5 at Fighter level 7 and 6 at Fighter level 15.",
                gained_at=[3, 3, 3, 3, 7, 15],
            ),
            dice=SUPERIORITY_DIE,
        )

    def number_of_uses(self, character: CharacterView) -> int:
        fighter_level = character.get_class_level(CharacterClass.FIGHTER)
        if fighter_level >= 15:
            return 6
        if fighter_level >= 7:
            return 5
        return 4

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The dice, their size by level and their recharge are in the panel
        # below; the maneuvers follow as their own blocks.
        return [
            Paragraph("Expend Superiority Dice to fuel your maneuvers."),
            Facts(
                (
                    (
                        "Maneuver save DC",
                        "8 + Strength or Dexterity modifier (your choice) + Proficiency Bonus",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        if character.get_class_level(CharacterClass.FIGHTER) < 10:
            superiority_die = "1d8"
        elif character.get_class_level(CharacterClass.FIGHTER) < 18:
            superiority_die = "1d10"
        else:
            superiority_die = "1d12"

        base_text = (
            f"These are {superiority_die}s, and you can expend them to fuel your maneuvers.\n"
            "You regain all expended superiority dice when you finish a short or long rest.\n"
            "If a maneuver requires a saving throw, the DC equals 8 plus your Strength or Dexterity modifier (your choice) and Proficiency Bonus.\n"
            "Maneuvers:"
        )

        return base_text

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST


class CombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Combat Superiority", origin="Battle Master Fighter Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The Superiority Dice card has the dice and their boxes.
        return [
            Paragraph("Learn maneuvers fueled by Superiority Dice."),
            Facts(
                (
                    (
                        "Maneuvers known",
                        "3; two more at Fighter levels 7, 10 and 15, when you can also swap one",
                    ),
                    ("Per attack", "One maneuver"),
                    (
                        "Superiority Dice",
                        "Four d8s; five from Fighter level 7, six from 15. Expended when used; all regained on a Short or Long Rest.",
                    ),
                    (
                        "Save DC",
                        "8 + Strength or Dexterity modifier (your choice) + Proficiency Bonus",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your experience on the battlefield has refined your fighting techniques. You learn maneuvers that are fueled by special dice called Superiority Dice.\n"
            "Maneuvers. You learn three maneuvers of your choice from the “Maneuver Options” section later in this subclass’s description. Many maneuvers enhance an attack in some way. You can use only one maneuver per attack.\n"
            "You learn two additional maneuvers of your choice when you reach Fighter levels 7, 10, and 15. Each time you learn new maneuvers, you can also replace one maneuver you know with a different one.\n"
            "Superiority Dice. You have four Superiority Dice, which are d8s. A Superiority Die is expended when you use it. You regain all expended Superiority Dice when you finish a Short or Long Rest.\n"
            "You gain an additional Superiority Die when you reach Fighter levels 7 (five dice total) and 15 (six dice total).\n"
            "Saving Throws. If a maneuver requires a saving throw, the DC equals 8 plus your Strength or Dexterity modifier (your choice) and Proficiency Bonus."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST


class StudentOfWar(Feature):
    def __init__(self):
        super().__init__(name="Student of War", origin="Battle Master Fighter Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Tool proficiency", "One type of Artisan's Tools of your choice"),
                    (
                        "Skill proficiency",
                        "One of your choice from the skills available to Fighters at level 1",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency with one type of Artisan’s Tools of your choice, and you gain proficiency in one skill of your choice from the skills available to Fighters at level 1."
        return description


class KnowYourEnemy(Feature):
    def __init__(self):
        super().__init__(
            name="Know Your Enemy",
            origin="Battle Master Fighter Level 7",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="30 Feet"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Target", "A creature you can see within 30 feet"),
                    (
                        "Effect",
                        "Learn whether it has any Immunities, Resistances or Vulnerabilities, and what they are",
                    ),
                    (
                        "Restore",
                        "Expend one Superiority Die (no action required) to regain the use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can discern certain strengths and weaknesses of a creature you can see within 30 feet of yourself; you know whether that creature has any Immunities, Resistances, or Vulnerabilities, and if the creature has any, you know what they are.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest. You can also restore a use of the feature by expending one Superiority Die (no action required)."
        )
        return description


class ImprovedCombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Combat Superiority", origin="Battle Master Fighter Level 10"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Superiority Die", "d10"),))]

    def get_description(self, character: CharacterView) -> str:
        description = "Your Superiority Die becomes a d10."
        return description


class Relentless(Feature):
    def __init__(self):
        super().__init__(name="Relentless", origin="Battle Master Fighter Level 15")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Frequency", "Once per turn, when you use a maneuver"),
                    (
                        "Effect",
                        "Roll 1d8 and use the number rolled instead of expending a Superiority Die",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Once per turn, when you use a maneuver, you can roll 1d8 and use the number rolled instead of expending a Superiority Die."
        return description


class UltimateCombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Ultimate Combat Superiority", origin="Battle Master Fighter Level 18"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Superiority Die", "d12"),))]

    def get_description(self, character: CharacterView) -> str:
        description = "Your Superiority Die becomes a d12."
        return description
