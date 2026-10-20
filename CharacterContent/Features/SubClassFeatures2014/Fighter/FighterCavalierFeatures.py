from Core.Definitions import CharacterClass
from Model.Content.Feature import (
    FeatureUses,
    Feature,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiency", origin="Cavalier Fighter Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Choose one:"),
            Facts(
                (
                    (
                        "Skill proficiency",
                        "Animal Handling, History, Insight, Performance or Persuasion",
                    ),
                    ("Or a language", "One language of your choice"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency in one of the following skills of your choice: Animal Handling, History, Insight, Performance, or Persuasion. Alternatively, you learn one language of your choice."
        return description


class BornToTheSaddle(Feature):
    def __init__(self):
        super().__init__(
            name="Born to the Saddle",
            origin="Cavalier Fighter Level 3",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your mastery as a rider becomes apparent."),
            Facts(
                (
                    ("Advantage", "On saving throws to avoid falling off your mount"),
                    (
                        "Falling",
                        "If you fall off your mount and descend no more than 10 feet, you land on your feet unless you're Incapacitated",
                    ),
                    (
                        "Mount or dismount",
                        "Costs only 5 feet of movement instead of half your Speed",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your mastery as a rider becomes apparent. You have advantage on saving throws made to avoid falling off your mount. If you fall off your mount and descend no more than 10 feet, you can land on your feet if you're not incapacitated.\n"
            "Finally, mounting or dismounting a creature costs you only 5 feet of movement, rather than half your speed."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class UnwaveringMark(Feature):
    def __init__(self):
        super().__init__(
            name="Unwavering Mark",
            origin="Cavalier Fighter Level 3",
            activation=FeatureActivation(
                duration="Until End of Your Next Turn", range="5 Feet"
            ),
            usage_tags=["damage", "control"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Strength modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_strength_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The special attack's uses are in the panel below.
        return [
            Paragraph("Menace your foes and punish them for harming others."),
            Facts(
                (
                    (
                        "Mark",
                        "When you hit a creature with a melee weapon attack, mark it until the end of your next turn. Ends early if you're incapacitated or die, or someone else marks it.",
                    ),
                    (
                        "Marked",
                        "While within 5 feet of you, it has disadvantage on attack rolls that don't target you",
                    ),
                )
            ),
            Option(
                "Special attack",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "A creature you marked deals damage to anyone other than you",
                            ),
                            ("Action", "Bonus Action on your next turn"),
                            (
                                "Attack",
                                "A melee weapon attack against it, with advantage",
                            ),
                            ("Hit", "Extra damage equal to half your Fighter level"),
                            (
                                "Uses",
                                "Strength modifier (minimum once) per long rest, however many creatures you mark",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can menace your foes, foiling their attacks and punishing them for harming others. When you hit a creature with a melee weapon attack, you can mark the creature until the end of your next turn. This effect ends early if you are incapacitated or you die, or if someone else marks the creature.\n"
            "While it is within 5 feet of you, a creature marked by you has disadvantage on any attack roll that doesn't target you.\n"
            "In addition, if a creature marked by you deals damage to anyone other than you, you can make a special melee weapon attack against the marked creature as a bonus action on your next turn. You have advantage on the attack roll, and if it hits, the attack's weapon deals extra damage to the target equal to half your fighter level.\n"
            "Regardless of the number of creatures you mark, you can make this special attack a number of times equal to your Strength modifier (a minimum of once), and you regain all expended uses of it when you finish a long rest."
        )
        level = character.get_class_level(CharacterClass.FIGHTER)
        description += f"\nRight now: {level // 2} extra damage on the special attack."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class WardingManeuver(Feature):
    def __init__(self):
        super().__init__(
            name="Warding Maneuver",
            origin="Cavalier Fighter Level 7",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Constitution modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_constitution_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Reaction, wielding a melee weapon or a shield"),
                    (
                        "Trigger",
                        "You or a creature you can see within 5 feet is hit by an attack",
                    ),
                    (
                        "Effect",
                        "Roll 1d8 and add it to the target's AC against the attack; if it still hits, the target has resistance to its damage",
                    ),
                    ("Uses", "Constitution modifier (minimum once) per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn to fend off strikes directed at you, your mount, or other creatures nearby. If you or a creature you can see within 5 feet of you is hit by an attack, you can roll 1d8 as a reaction if you're wielding a melee weapon or a shield. Roll the die, and add the number rolled to the target's AC against that attack. If the attack still hits, the target has resistance against the attack's damage.\n"
            "You can use this feature a number of times equal to your Constitution modifier (a minimum of once), and you regain all expended uses of it when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class HoldTheLine(Feature):
    def __init__(self):
        super().__init__(
            name="Hold the Line",
            origin="Cavalier Fighter Level 10",
            activation=FeatureActivation(
                duration="Until End of Current Turn", range="5 Feet"
            ),
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You become a master of locking down your enemies."),
            Facts(
                (
                    (
                        "Opportunity Attacks",
                        "Creatures provoke one from you when they move 5 feet or more while within your reach",
                    ),
                    (
                        "On a hit",
                        "The target's Speed is reduced to 0 until the end of the current turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You become a master of locking down your enemies. Creatures provoke an opportunity attack from you when they move 5 feet or more while within your reach, and if you hit a creature with an opportunity attack, the target's speed is reduced to 0 until the end of the current turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class FerociousCharger(Feature):
    def __init__(self):
        super().__init__(
            name="Ferocious Charger",
            origin="Cavalier Fighter Level 15",
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Run down your foes, whether you're mounted or not."),
            Facts(
                (
                    (
                        "Trigger",
                        "You move at least 10 feet in a straight line right before attacking a creature and hit it",
                    ),
                    ("Save", "Strength, DC 8 + Strength modifier + Proficiency Bonus"),
                    ("Failed save", "Knocked Prone"),
                    ("Frequency", "Once on each of your turns"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can run down your foes, whether you're mounted or not. If you move at least 10 feet in a straight line right before attacking a creature and you hit it with the attack, that target must succeed on a Strength saving throw (DC 8 + your proficiency bonus + your Strength modifier) or be knocked prone. You can use this feature only once on each of your turns."
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        strength_modifier = character.get_strength_modifier()
        return 8 + proficiency_bonus + strength_modifier

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class VigilantDefender(Feature):
    def __init__(self):
        super().__init__(
            name="Vigilant Defender",
            origin="Cavalier Fighter Level 18",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You respond to danger with extraordinary vigilance."),
            Facts(
                (
                    (
                        "Special reaction",
                        "In combat, take it once on every creature's turn except your own",
                    ),
                    ("Use", "Only to make an Opportunity Attack"),
                    (
                        "Limit",
                        "Not on the same turn that you take your normal Reaction",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You respond to danger with extraordinary vigilance. In combat, you get a special reaction that you can take once on every creature's turn, except your turn. You can use this special reaction only to make an opportunity attack, and you can't use it on the same turn that you take your normal reaction."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
