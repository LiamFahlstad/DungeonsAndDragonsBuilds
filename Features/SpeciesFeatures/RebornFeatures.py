from Definitions import Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species


class EscapedDeath(TextFeature):
    def __init__(self):
        super().__init__(name="Escaped Death", origin="Reborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Advantage on Death Saving Throws."


class Everlasting(TextFeature):
    def __init__(self):
        super().__init__(name="Everlasting", origin="Reborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You don’t gain Exhaustion levels from dehydration, malnutrition, or suffocation. You don’t need to sleep, and magic can’t put you to sleep. You can finish a Long Rest in 4 hours if you spend those hours in an inactive, motionless state, during which you retain consciousness."
        return description


class RebornKnowledge(TextFeature):
    def __init__(self):
        super().__init__(name="Reborn Knowledge", origin="Reborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain proficiency in one skill of your choice.\n"
            "In addition, you can temporarily peer into the past to aid you in the present. When you fail an ability check, you can roll 1d6 and add the number rolled to the d20, potentially turning the failure into a success. You can do this a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return description


class RebornKnowledgeSkill(CharacterFeature):
    def __init__(self, skill: Skill):
        self.skill = skill

    def validate(self, character_stat_block: CharacterStatBlock):
        assert not character_stat_block.skills.is_proficient(self.skill)

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        return character_stat_block.skills.add_skill_proficiency(self.skill)


class StrangeEndurance(TextFeature):
    def __init__(self):
        super().__init__(name="Strange Endurance", origin="Reborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Resistance to one of the following damage types of your choice: Cold, Necrotic, or Poison."
        return description
