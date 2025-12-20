from enum import Enum
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import CreatureSize
from Features.BaseFeatures import TextFeature


SPEED = 35  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class GiantAncestryType(str, Enum):
    CLOUD_GIANT = "Cloud Giant"
    FIRE_GIANT = "Fire Giant"
    FROST_GIANT = "Frost Giant"
    HILL_GIANT = "Hill Giant"
    STONE_GIANT = "Stone Giant"
    STORM_GIANT = "Storm Giant"


class LargeForm(TextFeature):
    def __init__(self):
        super().__init__(name="Large Form", origin="Goliath Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Starting at character level 5, you can change your size to Large as a Bonus Action if you're in a big enough space. This transformation lasts for 10 minutes or until you end it (no action required). For that duration, you have Advantage on Strength checks, and your Speed increases by 10 feet. Once you use this trait, you can't use it again until you finish a Long Rest."


class PowerfulBuild(TextFeature):
    def __init__(self):
        super().__init__(name="Goliath Nimbleness", origin="Goliath Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Advantage on any ability check you make to end the Grappled condition. You also count as one size larger when determining your carrying capacity."


class GiantAncestry(TextFeature):
    def __init__(self, giant_ancestry_type: GiantAncestryType):
        self.giant_ancestry_type = giant_ancestry_type
        super().__init__(name="Giant Ancestry", origin="Goliath Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = ""
        if self.giant_ancestry_type == GiantAncestryType.CLOUD_GIANT:
            text += "As a Bonus Action, you magically teleport up to 30 feet to an unoccupied space you can see.\n"
        if self.giant_ancestry_type == GiantAncestryType.FIRE_GIANT:
            text += "When you hit a target with an attack roll and deal damage to it, you can also deal 1d10 Fire damage to that target.\n"
        if self.giant_ancestry_type == GiantAncestryType.FROST_GIANT:
            text += "When you hit a target with an attack roll and deal damage to it, you can also deal 1d6 Cold damage to that target and reduce its Speed by 10 feet until the start of your next turn.\n"
        if self.giant_ancestry_type == GiantAncestryType.HILL_GIANT:
            text += "When you hit a Large or smaller creature with an attack roll and deal damage to it, you can give that target the Prone condition.\n"
        if self.giant_ancestry_type == GiantAncestryType.STONE_GIANT:
            text += "When you take damage, you can take a Reaction to roll 1d12. Add your Constitution modifier to the number rolled and reduce the damage by that total.\n"
        if self.giant_ancestry_type == GiantAncestryType.STORM_GIANT:
            text += "When you take damage from a creature within 60 feet of you, you can take a Reaction to deal 1d8 Thunder damage to that creature.\n"
        text += "You can use the benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest"
        return text
