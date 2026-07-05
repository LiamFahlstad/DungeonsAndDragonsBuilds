from Definitions import CreatureSize, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import ArmorClassBonus, SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class ConstructResilience(Feature):
    def __init__(self):
        super().__init__(name="Construct Resilience", origin="Warforged Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Poison damage. You also have Advantage on saving throws to avoid or end the Poisoned condition."


class SentrysRest(Feature):
    def __init__(self):
        super().__init__(name="Sentry's Rest", origin="Warforged Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You don’t need to sleep, and magic can’t put you to sleep. You can finish a Long Rest in 6 hours if you spend those hours in an inactive, motionless state. During this time, you appear inert but remain conscious."


class Tireless(Feature):
    def __init__(self):
        super().__init__(name="Tireless", origin="Warforged Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You don’t gain Exhaustion levels from dehydration, malnutrition, or suffocation."


class IntegratedProtection(Feature):
    def __init__(self):
        self._bonus = ArmorClassBonus(1)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._bonus.apply(character_stat_block)


class SpecializedDesign(Feature):
    def __init__(self, skill: Skill):
        self._choice = SkillProficiencyChoice(
            [skill], list(Skill), count=1, error_prefix="SpecializedDesign"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)
