from Definitions import CreatureSize, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class ConstructResilience(TextFeature):
    def __init__(self):
        super().__init__(name="Construct Resilience", origin="Warforged Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Poison damage. You also have Advantage on saving throws to avoid or end the Poisoned condition."


class SentrysRest(TextFeature):
    def __init__(self):
        super().__init__(name="Sentry's Rest", origin="Warforged Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You don’t need to sleep, and magic can’t put you to sleep. You can finish a Long Rest in 6 hours if you spend those hours in an inactive, motionless state. During this time, you appear inert but remain conscious."


class Tireless(TextFeature):
    def __init__(self):
        super().__init__(name="Tireless", origin="Warforged Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You don’t gain Exhaustion levels from dehydration, malnutrition, or suffocation."


class IntegratedProtection(CharacterFeature):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.increase_armor_class(1)


class SpecializedDesign(CharacterFeature):
    def __init__(self, skill: Skill):
        self.skill = skill

    def validate(self, character_stat_block: CharacterStatBlock):
        assert not character_stat_block.skills.is_proficient(self.skill)

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        return character_stat_block.skills.add_skill_proficiency(self.skill)
