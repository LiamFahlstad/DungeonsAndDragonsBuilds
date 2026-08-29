from Core.Definitions import RANGER_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class HuntersLore(Feature):
    def __init__(self):
        super().__init__(name="Hunter's Lore", origin="Hunter Ranger Level 3", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can call upon the forces of nature to reveal certain strengths and weaknesses of your prey. While a creature is marked by your Hunter's Mark, you know whether the creature has any Immunities, Resistances, or Vulnerabilities, and if the creature has any, you know what they are."
        return description


class ColossusSlayer(Feature):
    def __init__(self):
        super().__init__(name="Colossus Slayer", origin="Hunter Ranger Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your tenacity can wear down even the most resilient foes. When you hit a creature with a weapon, the weapon deals an extra 1d8 damage to the target if it's missing any of its Hit Points. You can deal this extra damage only once per turn."
        return description


class HordeBreaker(Feature):
    def __init__(self):
        super().__init__(name="Horde Breaker", origin="Hunter Ranger Level 3", activation=FeatureActivation(range="5 Feet"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once on each of your turns when you make an attack with a weapon, you can make another attack with the same weapon against a different creature that is within 5 feet of the original target, that is within the weapon's range, and that you haven't attacked this turn."
        return description


class EscapeTheHorde(Feature):
    def __init__(self):
        super().__init__(name="Escape the Horde", origin="Hunter Ranger Level 7", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Opportunity Attacks have Disadvantage against you."
        return description


class MultiattackDefense(Feature):
    def __init__(self):
        super().__init__(name="Multiattack Defense", origin="Hunter Ranger Level 7", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When a creature hits you with an attack roll, that creature has Disadvantage on all other attack rolls against you this turn."
        return description


class SuperiorHuntersPrey(Feature):
    def __init__(self):
        super().__init__(name="Superior Hunter's Prey", origin="Hunter Ranger Level 11", activation=FeatureActivation(range="30 Feet"), usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn when you deal damage to a creature marked by your Hunter's Mark, you can also deal that spell's extra damage to a different creature that you can see within 30 feet of the first creature."
        return description


class SuperiorHuntersDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Superior Hunter's Defense", origin="Hunter Ranger Level 15", activation=FeatureActivation(action_type="reaction", duration="Until End of Current Turn"), usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage, you can take a Reaction to give yourself Resistance to that damage and any other damage of the same type until the end of the current turn."
        return description
