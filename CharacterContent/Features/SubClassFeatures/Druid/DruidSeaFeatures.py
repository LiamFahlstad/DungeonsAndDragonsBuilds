from Core.Definitions import (
    DRUID_HIT_DIE,
    Ability,
)
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula


class CircleOfTheSeaSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Circle of the Sea Spells", origin="Circle of the Sea Druid Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Druid level shown, you always have these spells prepared."
            ),
            Table(
                ("Druid level", "Spells"),
                (
                    (
                        "3",
                        "Fog Cloud, Gust of Wind, Ray of Frost, Thunderwave",
                    ),
                    ("5", "Lightning Bolt, Water Breathing"),
                    ("7", "Control Water, Ice Storm"),
                    ("9", "Conjure Elemental, Hold Monster"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you reach a Druid level specified in the Circle of the Sea Spells table, you thereafter always have the listed spells prepared."
        return description


class WrathOfTheSea(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Sea",
            origin="Circle of the Sea Druid Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="10 Minutes or Until Dismissed/Incapacitated",
                range="5-Foot Emanation",
            ),
            usage_tags=["damage", "control"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.WISDOM)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Surround yourself with a churning aura of ocean spray."),
            Facts(
                (
                    ("Cost", "One use of Wild Shape"),
                    ("Action", "Bonus Action"),
                    ("Area", "5-foot Emanation"),
                    (
                        "Duration",
                        "10 minutes; ends early if you dismiss it (no action required), manifest it again or are Incapacitated",
                    ),
                )
            ),
            Option(
                "Crashing spray",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "When you manifest it, and as a Bonus Action on your later turns",
                            ),
                            ("Target", "Another creature you can see in the Emanation"),
                            (
                                "Save",
                                f"Constitution save against your spell save DC ({dc_formula(Ability.WISDOM)})",
                            ),
                            (
                                "Failed",
                                "Cold damage: a number of d6s equal to your Wisdom modifier (minimum 1d6). A Large or smaller target is pushed up to 15 feet away from you.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can expend a use of your Wild Shape to manifest a 5-foot Emanation that takes the form of ocean spray that surrounds you for 10 minutes. It ends early if you dismiss it (no action required), manifest it again, or have the Incapacitated condition.\n"
            "When you manifest the Emanation and as a Bonus Action on your subsequent turns, you can choose another creature you can see in the Emanation. The target must succeed on a Constitution saving throw against your spell save DC or take Cold damage and, if the creature is Large or smaller, be pushed up to 15 feet away from you. To determine this damage, roll a number of d6s equal to your Wisdom modifier (minimum of one die)."
        )
        return description


class AquaticAffinity(Feature):
    def __init__(self):
        super().__init__(
            name="Aquatic Affinity",
            origin="Circle of the Sea Druid Level 6",
            usage_tags=["buff", "utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Wrath of the Sea", "Its Emanation grows to 10 feet"),
                    ("Swim Speed", "Equal to your Speed"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The size of the Emanation created by your Wrath of the Sea increases to 10 feet.\n"
            "In addition, you gain a Swim Speed equal to your Speed."
        )
        return description


class Stormborn(Feature):
    def __init__(self):
        super().__init__(
            name="Stormborn",
            origin="Circle of the Sea Druid Level 10",
            usage_tags=["buff", "utility"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("While your Wrath of the Sea is active:"),
            Facts(
                (
                    ("Flight", "A Fly Speed equal to your Speed"),
                    ("Resistance", "Cold, Lightning and Thunder damage"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Wrath of the Sea confers two more benefits while active, as detailed below.\n"
            "Flight. You gain a Fly Speed equal to your Speed.\n"
            "Resistance. You have Resistance to Cold, Lightning, and Thunder damage."
        )
        return description


class OceanicGift(Feature):
    def __init__(self):
        super().__init__(
            name="Oceanic Gift",
            origin="Circle of the Sea Druid Level 14",
            activation=FeatureActivation(range="60 Feet"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Gift",
                        "Manifest the Wrath of the Sea Emanation around one willing creature within 60 feet instead of yourself",
                    ),
                    (
                        "Their aura",
                        "They gain all its benefits, using your spell save DC and Wisdom modifier",
                    ),
                    (
                        "Both of you",
                        "Expend two uses of Wild Shape instead of one to manifest it around both of you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Instead of manifesting the Emanation of Wrath of the Sea around yourself, you can manifest it around one willing creature within 60 feet of yourself. That creature gains all the benefits of the Emanation and uses your spell save DC and Wisdom modifier for it.\n"
            "In addition, you can manifest the Emanation around both the other creature and yourself if you expend two uses of your Wild Shape instead of one when manifesting it."
        )
        return description
