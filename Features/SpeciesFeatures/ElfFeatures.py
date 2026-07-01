from Definitions import CreatureSize, Skill
from Features.BaseFeatures import Feature
from Features.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(Feature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Elf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FeyAncestry(Feature):
    def __init__(self):
        super().__init__(name="Fey Ancestry", origin="Elf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = f"You have Advantage on saving throws you make to avoid or end the Charmed condition."
        return text


class KeenSenses(Feature):
    def __init__(self, skill: Skill):
        self._choice = SkillProficiencyChoice(
            [skill],
            [Skill.SURVIVAL, Skill.PERCEPTION, Skill.INSIGHT],
            count=1,
            error_prefix="KeenSenses",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)


class Trance(Feature):
    def __init__(self):
        super().__init__(name="Trance", origin="Elf Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = "You don't need to sleep, and magic can't put you to sleep. You can finish a Long Rest in 4 hours if you spend those hours in a trancelike meditation, during which you retain consciousness."
        return text
