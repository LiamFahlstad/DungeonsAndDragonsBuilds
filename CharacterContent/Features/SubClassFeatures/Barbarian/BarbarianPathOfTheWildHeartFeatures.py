from Model.Content.Feature import Feature, FeatureActivation, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class AnimalSpeaker(Feature):
    def __init__(self):
        super().__init__(
            name="Animal Speaker",
            origin="Path Of The Wild Heart Barbarian Level 3",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spells", "Beast Sense and Speak with Animals, only as Rituals"),
                    ("Spellcasting ability", "Wisdom"),
                    (
                        "From Barbarian level 10",
                        "Commune with Nature too (Nature Speaker)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can cast the Beast Sense and Speak with Animals spells but only as Rituals. Wisdom is your spellcasting ability for them."
        return description


class RageOfTheWilds(Feature):
    def __init__(self):
        super().__init__(
            name="Rage of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 3",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Whenever you activate your Rage, choose one:"),
            Option(
                "Bear",
                (
                    Facts(
                        (
                            (
                                "Resistance",
                                "Every damage type except Force, Necrotic, Psychic and Radiant, while raging",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Eagle",
                (
                    Facts(
                        (
                            (
                                "Activate",
                                "Disengage and Dash as part of the Rage's Bonus Action",
                            ),
                            ("While raging", "Bonus Action: Disengage and Dash"),
                        )
                    ),
                ),
            ),
            Option(
                "Wolf",
                (
                    Facts(
                        (
                            (
                                "While raging",
                                "Your allies have Advantage on attack rolls against your enemies within 5 feet of you",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Rage taps into the primal power of animals. Whenever you activate your Rage, you gain one of the following options of your choice.\n"
            "Bear. While your Rage is active, you have Resistance to every damage type except Force, Necrotic, Psychic, and Radiant.\n"
            "Eagle. When you activate your Rage, you can take the Disengage and Dash actions as part of that Bonus Action. While your Rage is active, you can take a Bonus Action to take both of those actions.\n"
            "Wolf. While your Rage is active, your allies have Advantage on attack rolls against any enemy of yours within 5 feet of you."
        )
        return description


class AspectOfTheWilds(Feature):
    def __init__(self):
        super().__init__(
            name="Aspect of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 6",
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Gain one option of your choice. You can change it whenever you finish a Long Rest."
            ),
            Facts(
                (
                    (
                        "Owl",
                        "Darkvision with a range of 60 feet, or +60 feet if you already have it",
                    ),
                    ("Panther", "A Climb Speed equal to your Speed"),
                    ("Salmon", "A Swim Speed equal to your Speed"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain one of the following options of your choice. Whenever you finish a Long Rest, you can change your choice.\n"
            "Owl. You have Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 60 feet.\n"
            "Panther. You have a Climb Speed equal to your Speed.\n"
            "Salmon. You have a Swim Speed equal to your Speed."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class NatureSpeaker(Feature):
    def __init__(self):
        super().__init__(
            name="Nature Speaker",
            origin="Path Of The Wild Heart Barbarian Level 10",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spell", "Commune with Nature, only as a Ritual"),
                    ("Spellcasting ability", "Wisdom"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can cast the Commune with Nature spell but only as a Ritual. Wisdom is your spellcasting ability for it."
        return description


class PowerOfTheWilds(Feature):
    def __init__(self):
        super().__init__(
            name="Power of the Wilds",
            origin="Path Of The Wild Heart Barbarian Level 14",
            activation=FeatureActivation(range="5 Feet"),
            usage_tags=["buff", "control", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Whenever you activate your Rage, choose one (lasts while raging):"
            ),
            Option(
                "Falcon",
                (
                    Facts(
                        (
                            (
                                "Flight",
                                "Fly Speed equal to your Speed if you aren't wearing armor",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Lion",
                (
                    Facts(
                        (
                            (
                                "Menace",
                                "Enemies within 5 feet of you have Disadvantage on attack rolls against anyone but you or another Barbarian with this option",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Ram",
                (
                    Facts(
                        (
                            (
                                "Topple",
                                "When you hit a Large or smaller creature with a melee attack, you can knock it Prone",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you activate your Rage, you gain one of the following options of your choice.\n"
            "Falcon. While your Rage is active, you have a Fly Speed equal to your Speed if you aren’t wearing any armor.\n"
            "Lion. While your Rage is active, any of your enemies within 5 feet of you have Disadvantage on attack rolls against targets other than you or another Barbarian who has this option active.\n"
            "Ram. While your Rage is active, you can cause a Large or smaller creature to have the Prone condition when you hit it with a melee attack."
        )
        return description
