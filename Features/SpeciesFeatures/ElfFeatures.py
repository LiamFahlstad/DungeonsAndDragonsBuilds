from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, DiceRollCondition, Skill, CreatureSize
from Features.BaseFeatures import CharacterFeature, TextFeature


SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(TextFeature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Orc Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FeyAncestry(TextFeature):
    def __init__(self):
        super().__init__(name="Fey Ancestry", origin="Elf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = f"You have Advantage on saving throws you make to avoid or end the Charmed condition."
        return text


class KeenSenses(CharacterFeature):
    def __init__(self, skill: Skill):
        self.skill = skill

    def validate(self, character_stat_block: CharacterStatBlock):
        assert not character_stat_block.skills.is_proficient(self.skill)
        assert self.skill in [Skill.SURVIVAL, Skill.PERCEPTION, Skill.INSIGHT]

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        return character_stat_block.skills.add_skill_proficiency(self.skill)


class Trance(TextFeature):
    def __init__(self):
        super().__init__(name="Trance", origin="Elf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = "You don't need to sleep, and magic can't put you to sleep. You can finish a Long Rest in 4 hours if you spend those hours in a trancelike meditation, during which you retain consciousness."
        return text
