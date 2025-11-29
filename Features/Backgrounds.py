from Character import Character
from Definitions import Ability, Skill
from Features.BaseFeatures import CharacterFeature


class FreeBackgroundAbilityBonus(CharacterFeature):
    """Also add either [+1, +1, +1] OR [+2, +1] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self.bonuses = bonuses
        # Validate
        if not (sum([bonus[1] for bonus in self.bonuses]) == 3):
            raise ValueError("Bonuses must sum to 3.")

    def modify(self, character_stat_block: Character):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)


class FreeBackgroundSkillProficiency(CharacterFeature):
    """Also add proficiency in two skills of your choice."""

    def __init__(self, skills: list[Skill]):
        if len(skills) != 2:
            raise ValueError("Must choose exactly two skills for proficiency.")
        self.skills = skills

    def modify(self, character_stat_block: Character):
        for skill in self.skills:
            if character_stat_block.skills.proficiencies.get(skill):
                raise ValueError(f"Character is already proficient in {skill}.")
            character_stat_block.skills.proficiencies[skill] = True
