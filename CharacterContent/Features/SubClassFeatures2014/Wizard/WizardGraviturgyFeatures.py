from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Core.Definitions import Ability
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class AdjustDensity(Feature):
    def __init__(self):
        super().__init__(
            name="Adjust Density",
            origin="Graviturgy Wizard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Up To 1 Minute Or Until Concentration Ends",
                range="30 Feet",
            ),
            usage_tags=["buff", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Alter an object's or creature's weight."),
            Facts(
                (
                    ("Action", "Action"),
                    ("Range", "30 feet"),
                    (
                        "Target",
                        "One object or creature you can see: Large or smaller (Huge or smaller from Wizard level 10)",
                    ),
                    ("Duration", "Up to 1 minute, concentrating as if on a spell"),
                )
            ),
            Option(
                "Halve or double its weight",
                (
                    Table(
                        ("Weight", "A creature's speed", "Other effects"),
                        (
                            (
                                "Halved",
                                "+10 feet",
                                "Jumps twice as far; disadvantage on Strength checks and saving throws",
                            ),
                            (
                                "Doubled",
                                "-10 feet",
                                "Advantage on Strength checks and saving throws",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 2nd level, as an action, you can magically alter the weight of one object or creature you can see within 30 feet of you. The object or creature must be Large or smaller. The target's weight is halved or doubled for up to 1 minute or until your concentration ends (as if you were concentrating on a spell).\n"
            "\n"
            "While the weight of a creature is halved by this effect, the creature's speed increases by 10 feet, it can jump twice as far as normal, and it has disadvantage on Strength checks and Strength saving throws.\n"
            "\n"
            "While the weight of a creature is doubled by this effect, the creature's speed is reduced by 10 feet, and it has advantage on Strength checks and Strength saving throws.\n"
            "\n"
            "Upon reaching 10th level in this class, you can target an object or a creature that is Huge or smaller."
        )
        return description


class GravityWell(Feature):
    def __init__(self):
        super().__init__(
            name="Gravity Well",
            origin="Graviturgy Wizard Level 6",
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You cast a spell on a creature"),
                    (
                        "Requirement",
                        "The target is willing to move, the spell hits it with an attack, or it fails a saving throw against the spell",
                    ),
                    (
                        "Effect",
                        "Move the target 5 feet to an unoccupied space of your choice",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you reach 6th level, whenever you cast a spell on a creature, you can move the target 5 feet to an unoccupied space of your choice if the target is willing to move, the spell hits it with an attack, or it fails a saving throw against the spell."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class ViolentAttraction(Feature):
    def __init__(self):
        super().__init__(
            name="Violent Attraction",
            origin="Graviturgy Wizard Level 10",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
            usage_tags=["damage"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph(
                "Use your reaction (Intelligence modifier, minimum once, per long rest) for one:"
            ),
            Option(
                "Velocity",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "A creature you can see within 60 feet hits with a weapon attack",
                            ),
                            (
                                "Effect",
                                "The target takes an extra 1d10 damage of the weapon's type",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Heavy fall",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "A creature within 60 feet takes falling damage",
                            ),
                            ("Effect", "The fall deals an extra 2d10 damage"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 10th level, when another creature that you can see within 60 feet of you hits with a weapon attack, you can use your reaction to increase the attack's velocity, causing the attack's target to take an extra 1d10 damage of the weapon's type.\n"
            "\n"
            "Alternatively, if a creature within 60 feet of you takes damage from a fall, you can use your reaction to increase the fall's damage by 2d10.\n"
            "\n"
            "You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class EventHorizon(Feature):
    def __init__(self):
        super().__init__(
            name="Event Horizon",
            origin="Graviturgy Wizard Level 14",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="1 Minute Or Until Concentration Ends",
                range="30 Feet",
            ),
            usage_tags=["damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-long-rest box is in the panel below.
        return [
            Paragraph("Emit a field of gravitational energy."),
            Facts(
                (
                    ("Action", "Action"),
                    ("Duration", "Up to 1 minute, concentrating as if on a spell"),
                    (
                        "Trigger",
                        "A creature hostile to you starts its turn within 30 feet of you",
                    ),
                    (
                        "Save",
                        "Strength save against your spell save DC (8 + Intelligence modifier + Proficiency Bonus)",
                    ),
                    (
                        "Failed",
                        "2d10 force damage, and its speed is 0 until the start of its next turn",
                    ),
                    (
                        "Succeeded",
                        "Half damage, and each foot it moves this turn costs 2 extra feet",
                    ),
                    (
                        "Recharge",
                        "Once per long rest, or expend a spell slot of 3rd level or higher",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Starting at 14th level, as an action, you can magically emit a powerful field of gravitational energy that tugs at other creatures for up to 1 minute or until your concentration ends (as if you were concentrating on a spell). For the duration, whenever a creature hostile to you starts its turn within 30 feet of you, it must make a Strength saving throw against your spell save DC. On a failed save, it takes 2d10 force damage, and its speed is reduced to 0 until the start of its next turn. On a successful save, it takes half as much damage, and every foot it moves this turn costs 2 extra feet of movement.\n"
            "\n"
            "Once you use this feature, you can't do so again until you finish a long rest or until you expend a spell slot of 3rd level or higher on it."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA
