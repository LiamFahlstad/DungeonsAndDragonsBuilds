
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

DRUID_HIT_DIE = 8


class CircleOfTheSeaSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Circle of the Sea Spells", origin="Circle of the Sea Druid Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Druid level specified in the Circle of the Sea Spells table, you thereafter always have the listed spells prepared."
        return description


class WrathOfTheSea(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Sea", origin="Circle of the Sea Druid Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can expend a use of your Wild Shape to manifest a 5-foot Emanation that takes the form of ocean spray that surrounds you for 10 minutes. It ends early if you dismiss it (no action required), manifest it again, or have the Incapacitated condition.\n"
            "When you manifest the Emanation and as a Bonus Action on your subsequent turns, you can choose another creature you can see in the Emanation. The target must succeed on a Constitution saving throw against your spell save DC or take Cold damage and, if the creature is Large or smaller, be pushed up to 15 feet away from you. To determine this damage, roll a number of d6s equal to your Wisdom modifier (minimum of one die)."
        )
        return description


class AquaticAffinity(Feature):
    def __init__(self):
        super().__init__(
            name="Aquatic Affinity", origin="Circle of the Sea Druid Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The size of the Emanation created by your Wrath of the Sea increases to 10 feet.\n"
            "In addition, you gain a Swim Speed equal to your Speed."
        )
        return description


class Stormborn(Feature):
    def __init__(self):
        super().__init__(name="Stormborn", origin="Circle of the Sea Druid Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Wrath of the Sea confers two more benefits while active, as detailed below.\n"
            "Flight. You gain a Fly Speed equal to your Speed.\n"
            "Resistance. You have Resistance to Cold, Lightning, and Thunder damage."
        )
        return description


class OceanicGift(Feature):
    def __init__(self):
        super().__init__(name="Oceanic Gift", origin="Circle of the Sea Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Instead of manifesting the Emanation of Wrath of the Sea around yourself, you can manifest it around one willing creature within 60 feet of yourself. That creature gains all the benefits of the Emanation and uses your spell save DC and Wisdom modifier for it.\n"
            "In addition, you can manifest the Emanation around both the other creature and yourself if you expend two uses of your Wild Shape instead of one when manifesting it."
        )
        return description
