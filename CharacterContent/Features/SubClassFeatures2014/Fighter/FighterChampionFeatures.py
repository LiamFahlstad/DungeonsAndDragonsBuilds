import math

from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ImprovedCritical(Feature):
    def __init__(self):
        super().__init__(name="Improved Critical", origin="Champion Fighter Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Beginning when you choose this archetype at 3rd level, your weapon attacks score a critical hit on a roll of 19 or 20."
        return description


class RemarkableAthlete(Feature):
    def __init__(self):
        super().__init__(name="Remarkable Athlete", origin="Champion Fighter Level 7", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 7th level, you can add half your proficiency bonus (rounded up) to any Strength, Dexterity, or Constitution check you make that doesn't already use your proficiency bonus.\n"
            "\n"
            "In addition, when you make a running long jump, the distance you can cover increases by a number of feet equal to your Strength modifier."
        )
        return description


class AdditionalFightingStyle(Feature):
    def __init__(self):
        super().__init__(
            name="Additional Fighting Style", origin="Champion Fighter Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 10th level, you can choose a second option from the Fighting Style class feature."
        return description


class SuperiorCritical(Feature):
    def __init__(self):
        super().__init__(name="Superior Critical", origin="Champion Fighter Level 15", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 15th level, your weapon attacks score a critical hit on a roll of 18-20."
        return description


class Survivor(Feature):
    def __init__(self):
        super().__init__(name="Survivor", origin="Champion Fighter Level 18", usage_tags=["heal"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 18th level, you attain the pinnacle of resilience in battle. At the start of each of your turns, you regain hit points equal to 5 + your Constitution modifier if you have no more than half of your hit points left. You don't gain this benefit if you have 0 hit points."
        )
        return description
