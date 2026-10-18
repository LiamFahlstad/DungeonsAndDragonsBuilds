from Core.Definitions import WIZARD_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class DivinationSavant(Feature):
    def __init__(self):
        super().__init__(name="Divination Savant", origin="Diviner Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add Divination spells to your spellbook for free."),
            Facts(
                (
                    (
                        "Now",
                        "Two Wizard Divination spells, each no higher than level 2",
                    ),
                    (
                        "New spell slot levels",
                        "Whenever you gain access to a new level of spell slots in this class, one Wizard Divination spell of a level you have slots for",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Divination school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Divination school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class Portent(Feature):
    def __init__(self):
        super().__init__(
            name="Portent", origin="Diviner Wizard Level 3", usage_tags=["buff"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Glimpses of the future press on your awareness."),
            Facts(
                (
                    (
                        "Foretelling rolls",
                        "When you finish a Long Rest, roll two d20s and record them (three from Wizard level 14, Greater Portent)",
                    ),
                    (
                        "Use",
                        "Replace a D20 Test made by you or a creature you can see with one of them, choosing before the roll",
                    ),
                    ("Limit", "Once per turn; each roll can be used only once"),
                    ("Expiry", "Unused rolls are lost when you finish a Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Glimpses of the future begin to press on your awareness. Whenever you finish a Long Rest, roll two d20s and record the numbers rolled. You can replace any D20 Test made by you or a creature that you can see with one of these foretelling rolls. You must choose to do so before the roll, and you can replace a roll in this way only once per turn.\n"
            "Each foretelling roll can be used only once. When you finish a Long Rest, you lose any unused foretelling rolls."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class ExpertDivination(Feature):
    def __init__(self):
        super().__init__(name="Expert Divination", origin="Diviner Wizard Level 6")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a Divination spell using a level 2+ spell slot",
                    ),
                    (
                        "Effect",
                        "Regain one expended spell slot of a lower level than the one you used, no higher than level 5",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Casting Divination spells comes so easily to you that it expends only a fraction of your spellcasting efforts. When you cast a Divination spell using a level 2+ spell slot, you regain one expended spell slot. The slot you regain must be of a level lower than the slot you expended and can't be higher than level 5.\n"
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.OTHER


class TheThirdEye(Feature):
    def __init__(self):
        super().__init__(
            name="The Third Eye",
            origin="Diviner Wizard Level 10",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="Until Short or Long Rest"
            ),
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Increase your powers of perception."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Duration", "Until you start a Short or Long Rest"),
                    ("Limit", "Once per Short or Long Rest"),
                )
            ),
            Option(
                "Benefits (choose one)",
                (
                    Facts(
                        (
                            ("Darkvision", "Darkvision with a range of 120 feet"),
                            ("Greater Comprehension", "You can read any language"),
                            (
                                "See Invisibility",
                                "Cast See Invisibility without expending a spell slot",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can increase your powers of perception. As a Bonus Action, choose one of the following benefits, which lasts until you start a Short or Long Rest. You can't use this feature again until you finish a Short or Long Rest.\n"
            "    * Darkvision: You gain Darkvision with a range of 120 feet.\n"
            "    * Greater Comprehension: You can read any language.\n"
            "    * See Invisibility: You can cast See Invisibility without expending a spell slot."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class GreaterPortent(Feature):
    def __init__(self):
        super().__init__(
            name="Greater Portent",
            origin="Diviner Wizard Level 14",
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "The visions in your dreams intensify and paint a more accurate picture in your mind of what is to come. Roll three d20s for your Portent feature rather than two."
        return description
