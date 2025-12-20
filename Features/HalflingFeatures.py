from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill, CreatureSize
from Features.BaseFeatures import CharacterFeature, TextFeature


SPEED = 30  # Given by your species
SIZE = CreatureSize.SMALL  # Given by your species


class Brave(TextFeature):
    def __init__(self):
        super().__init__(name="Brave", origin="Halfling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Advantage on saving throws you make to avoid or end the Frightened condition."


class HalflingNimbleness(TextFeature):
    def __init__(self):
        super().__init__(name="Halfling Nimbleness", origin="Halfling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You can move through the space of any creature that is a size larger than you, but you can't stop in the same space."


class Luck(TextFeature):
    def __init__(self):
        super().__init__(name="Luck", origin="Halfling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = "When you roll a 1 on the d20 of a D20 Test, you can reroll the die, and you must use the new roll."
        return text


class NaturallyStealthy(TextFeature):
    def __init__(self):
        super().__init__(name="Naturally Stealthy", origin="Halfling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = "You can take the Hide action even when you are obscured only by a creature that is at least one size larger than you."
        return text
