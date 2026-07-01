from Definitions import CreatureSize, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from Features.SubFeatures import SkillProficiencyChoice
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
        self._choice = SkillProficiencyChoice(
            [skill],
            list(Skill),
            count=1,
            error_prefix="Skillful"
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)


class Versatile(TextFeature):
    def __init__(self):
        super().__init__(name="Versatile", origin="Human Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain an Origin feat of your choice (see 'Feats'). Skilled is recommended.\n"
