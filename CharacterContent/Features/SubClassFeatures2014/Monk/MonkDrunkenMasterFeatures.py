from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Way of the Drunken Master Monk Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Your martial arts technique mixes combat training with the precision of a dancer and the antics of a jester."
            ),
            Facts(
                (
                    ("Skill proficiency", "Performance, if you don't already have it"),
                    (
                        "Tool proficiency",
                        "Brewer's Supplies, if you don't already have it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency in the Performance skill if you don't already have it. Your martial arts technique mixes combat training with the precision of a dancer and the antics of a jester. You also gain proficiency with brewer's supplies if you don't already have it."
        return description


class DrunkenTechnique(Feature):
    def __init__(self):
        super().__init__(
            name="Drunken Technique",
            origin="Way of the Drunken Master Monk Level 3",
            activation=FeatureActivation(duration="Until End of Current Turn"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Flurry of Blows"),
                    ("Disengage", "You gain the benefit of the Disengage action"),
                    (
                        "Speed",
                        "+10 feet walking speed until the end of the current turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You learn how to twist and turn quickly as part of your Flurry of Blows. Whenever you use Flurry of Blows, you gain the benefit of the Disengage action, and your walking speed increases by 10 feet until the end of the current turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TipsySway(Feature):
    def __init__(self):
        super().__init__(
            name="Tipsy Sway",
            origin="Way of the Drunken Master Monk Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
            usage_tags=["control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You can move in sudden, swaying ways."),
            Option(
                "Leap to Your Feet",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "When you're Prone, stand up by spending 5 feet of movement instead of half your Speed",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Redirect Attack",
                (
                    Facts(
                        (
                            ("Action", "Reaction, spending 1 ki point"),
                            (
                                "Trigger",
                                "A creature misses you with a melee attack roll",
                            ),
                            (
                                "Effect",
                                "The attack hits one creature of your choice, other than the attacker, that you can see within 5 feet of you",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can move in sudden, swaying ways. You gain the following benefits.\n"
            "    * Leap to Your Feet. When you're prone, you can stand up by spending 5 feet of movement, rather than half your speed.\n"
            "    * Redirect Attack. When a creature misses you with a melee attack roll, you can spend 1 ki point as a reaction to cause that attack to hit one creature of your choice, other than the attacker, that you can see within 5 feet of you."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DrunkardsLuck(Feature):
    def __init__(self):
        super().__init__(
            name="Drunkard's Luck",
            origin="Way of the Drunken Master Monk Level 11",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You always seem to get a lucky bounce at the right moment."),
            Facts(
                (
                    (
                        "Trigger",
                        "You make an ability check, attack roll or saving throw with Disadvantage",
                    ),
                    ("Cost", "2 ki points"),
                    ("Effect", "Cancel the Disadvantage for that roll"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You always seem to get a lucky bounce at the right moment. When you make an ability check, an attack roll, or a saving throw and have disadvantage, you can spend 2 ki points to cancel the disadvantage for that roll."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class IntoxicatedFrenzy(Feature):
    def __init__(self):
        super().__init__(
            name="Intoxicated Frenzy",
            origin="Way of the Drunken Master Monk Level 17",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Flurry of Blows"),
                    (
                        "Effect",
                        "Make up to three additional attacks with it (up to five Flurry of Blows attacks in total)",
                    ),
                    (
                        "Requirement",
                        "Each Flurry of Blows attack targets a different creature this turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain the ability to make an overwhelming number of attacks against a group of enemies. When you use your Flurry of Blows, you can make up to three additional attacks with it (up to a total of five Flurry of Blows attacks), provided that each Flurry of Blows attack targets a different creature this turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
