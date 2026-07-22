from Core.Definitions import CreatureSize, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Resourceful(Feature):
    def __init__(self):
        super().__init__(name="Resourceful", origin="Human Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain Heroic Inspiration whenever you finish a Long Rest.\n"


class Skillful(Feature):
    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(name="Skillful", origin="Human Trait")
        self._choice = SkillProficiencyChoice(
            [skill], list(Skill), count=1, error_prefix="Skillful"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."


class Versatile(Feature):
    def __init__(self):
        super().__init__(name="Versatile", origin="Human Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain an Origin feat of your choice (see 'Feats'). Skilled is recommended.\n"
