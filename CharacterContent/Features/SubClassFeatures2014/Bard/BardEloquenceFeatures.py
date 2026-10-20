from Core.Definitions import BARD_HIT_DIE
from Model.Content.Feature import (
    FeatureUses,
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class SilverTongue(Feature):
    def __init__(self):
        super().__init__(
            name="Silver Tongue",
            origin="College of Eloquence Bard Level 3",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You're a master at saying the right thing at the right time."),
            Facts(
                (
                    (
                        "Applies to",
                        "Charisma (Persuasion) and Charisma (Deception) checks",
                    ),
                    ("Effect", "Treat a d20 roll of 9 or lower as a 10"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You are a master at saying the right thing at the right time. When you make a Charisma "
            "(Persuasion) or Charisma (Deception) check, you can treat a d20 roll of 9 or lower as a 10."
        )
        return description


class UnsettlingWords(Feature):
    def __init__(self):
        super().__init__(
            name="Unsettling Words",
            origin="College of Eloquence Bard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Start of Your Next Turn",
                range="60 Feet",
            ),
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Spin words laced with magic that unsettle a creature and cause it to doubt itself."
            ),
            Facts(
                (
                    ("Action", "Bonus Action, expending one use of Bardic Inspiration"),
                    ("Target", "One creature you can see within 60 feet"),
                    ("Effect", "Roll the Bardic Inspiration die"),
                    (
                        "Penalty",
                        "The creature subtracts the roll from the next saving throw it makes before the start of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can spin words laced with magic that unsettle a creature and cause it to doubt itself. "
            "As a bonus action, you can expend one use of your Bardic Inspiration and choose one creature "
            "you can see within 60 feet of you. Roll the Bardic Inspiration die. The creature must subtract "
            "the number rolled from the next saving throw it makes before the start of your next turn."
        )
        return description


class UnfailingInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Unfailing Inspiration",
            origin="College of Eloquence Bard Level 6",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "A creature adds your Bardic Inspiration die to an ability check, attack roll or saving throw and the roll fails",
                    ),
                    ("Effect", "The creature keeps the Bardic Inspiration die"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your inspiring words are so persuasive that others feel driven to succeed. When a creature "
            "adds one of your Bardic Inspiration dice to its ability check, attack roll, or saving throw "
            "and the roll fails, the creature can keep the Bardic Inspiration die."
        )
        return description


class UniversalSpeech(Feature):
    def __init__(self):
        super().__init__(
            name="Universal Speech",
            origin="College of Eloquence Bard Level 6",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Hour", range="60 Feet"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Make your speech intelligible to any creature."),
            Facts(
                (
                    ("Action", "Action"),
                    (
                        "Target",
                        "Up to Charisma modifier (minimum one) creatures within 60 feet",
                    ),
                    (
                        "Effect",
                        "They magically understand you, regardless of the language you speak",
                    ),
                    ("Duration", "1 hour"),
                    ("Recharge", "Expend a spell slot to use it again"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have gained the ability to make your speech intelligible to any creature. As an action, "
            "choose one or more creatures within 60 feet of you, up to a number equal to your Charisma "
            "modifier (minimum of one creature). The chosen creatures can magically "
            "understand you, regardless of the language you speak, for 1 hour.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest, unless you "
            "expend a spell slot to use it again."
        )
        description += (
            f"\nRight now: up to {max(1, character.get_charisma_modifier())} creatures."
        )
        return description


class InfectiousInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Infectious Inspiration",
            origin="College of Eloquence Bard Level 14",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature within 60 feet adds your Bardic Inspiration die to an ability check, attack roll or saving throw and succeeds",
                    ),
                    (
                        "Effect",
                        "Give a Bardic Inspiration die to a different creature (not you) within 60 feet that can hear you, without expending a use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you successfully inspire someone, the power of your eloquence can now spread to someone else. "
            "When a creature within 60 feet of you adds one of your Bardic Inspiration dice to its ability check, "
            "attack roll, or saving throw and the roll succeeds, you can use your reaction to encourage a different "
            "creature (other than yourself) that can hear you within 60 feet of you, giving it a Bardic Inspiration "
            "die without expending any of your Bardic Inspiration uses."
        )
        return description
