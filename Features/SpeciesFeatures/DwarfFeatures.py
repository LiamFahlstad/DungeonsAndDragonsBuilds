from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill, CreatureSize
from Features.BaseFeatures import CharacterFeature, TextFeature


SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Orc Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 120 feet."


class DwarvenResilience(TextFeature):
    def __init__(self):
        super().__init__(name="Dwarven Resilience", origin="Dwarf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Poison damage. You also have Advantage on saving throws you make to avoid or end the Poisoned condition."


class DwarvenToughness(CharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_level = character_stat_block.character_level
        character_stat_block.combat.hit_points_bonus += character_level


class Stonecunning(TextFeature):
    def __init__(self):
        super().__init__(name="Stonecunning", origin="Dwarf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        text = (
            "As a Bonus Action, you gain Tremorsense with a range of 60 feet for 10 minutes. You must be on a stone surface or touching a stone surface to use this Tremorsense. The stone can be natural or worked.\n"
            f"You can use this Bonus Action a number of times equal to your Proficiency Bonus ({proficiency_bonus}), and you regain all expended uses when you finish a Long Rest."
        )
        return text
