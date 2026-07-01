from Definitions import Ability, Skill
from Features.BaseFeatures import CharacterFeature
from Features.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FreeBackgroundAbilityBonus(CharacterFeature):
    """Also add either [+1, +1, +1] OR [+2, +1] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self.bonuses = bonuses
        # Validate
        if sum(bonus[1] for bonus in self.bonuses) != 3:
            raise ValueError("Bonuses must sum to 3.")

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)


class FreeBackgroundSkillProficiency(CharacterFeature):
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
