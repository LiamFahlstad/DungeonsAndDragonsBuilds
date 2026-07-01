from Definitions import Ability, Skill
from Features.BaseFeatures import Feature
from Features.SubFeatures import AbilityScoreBonus, SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FreeBackgroundAbilityBonus(Feature):
    """Also add either [+1, +1, +1] OR [+2, +1] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self._bonus = AbilityScoreBonus(bonuses, total=3, error_prefix="Free Background Ability Bonus")

    def apply(self, character_stat_block: CharacterStatBlock):
        self._bonus.apply(character_stat_block)


class FreeBackgroundSkillProficiency(Feature):
    """Also add proficiency in two skills of your choice."""

    def __init__(self, skills: list[Skill]):
        self._choice = SkillProficiencyChoice(
            skills,
            list(Skill),
            count=2,
            error_prefix="Free Background Skill Proficiency",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)
