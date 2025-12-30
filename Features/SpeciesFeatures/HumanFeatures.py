from Definitions import CreatureSize, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Resourceful(TextFeature):
    def __init__(self):
        super().__init__(name="Resourceful", origin="Human Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain Heroic Inspiration whenever you finish a Long Rest.\n"


class Skillful(CharacterFeature):
    def __init__(self, skill: Skill):
        self.skill = skill

    def validate(self, character_stat_block: CharacterStatBlock):
        assert not character_stat_block.skills.is_proficient(self.skill)

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        return character_stat_block.skills.add_skill_proficiency(self.skill)


class Versatile(TextFeature):
    def __init__(self):
        super().__init__(name="Versatile", origin="Human Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain an Origin feat of your choice (see 'Feats'). Skilled is recommended.\n"
