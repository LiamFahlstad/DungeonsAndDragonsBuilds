from Definitions import Ability, Skill
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class SkillProficiencyChoice:
    """Grants proficiency in `count` pre-chosen skills, each validated against `pool`."""

    def __init__(self, skills: list[Skill], pool: list[Skill], count: int, error_prefix: str = "Invalid skill choice"):
        if len(skills) != count:
            raise ValueError(f"{error_prefix}: expected {count} skill(s), got {len(skills)}.")
        if len(skills) != len(set(skills)):
            raise ValueError(f"{error_prefix}: duplicate skills provided.")
        for skill in skills:
            if skill not in pool:
                raise ValueError(f"{error_prefix}: {skill} is not in the allowed pool.")
        self.skills = skills

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.add_skill_proficiency(skill)


class SkillExpertiseChoice:
    """Grants expertise in `count` pre-chosen skills, each validated against `pool`."""

    def __init__(self, skills: list[Skill], pool: list[Skill], count: int, error_prefix: str = "Invalid skill choice"):
        if len(skills) != count:
            raise ValueError(f"{error_prefix}: expected {count} skill(s), got {len(skills)}.")
        if len(skills) != len(set(skills)):
            raise ValueError(f"{error_prefix}: duplicate skills provided.")
        for skill in skills:
            if skill not in pool:
                raise ValueError(f"{error_prefix}: {skill} is not in the allowed pool.")
        self.skills = skills

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.add_skill_expertise(skill)


class SavingThrowProficiencyChoice:
    """Grants saving throw proficiency in `count` pre-chosen abilities, each validated against `pool`."""

    def __init__(self, abilities: list[Ability], pool: list[Ability], count: int, error_prefix: str = "Invalid saving throw choice"):
        if len(abilities) != count:
            raise ValueError(f"{error_prefix}: expected {count} ability/abilities, got {len(abilities)}.")
        if len(abilities) != len(set(abilities)):
            raise ValueError(f"{error_prefix}: duplicate abilities provided.")
        for ability in abilities:
            if ability not in pool:
                raise ValueError(f"{error_prefix}: {ability} is not in the allowed pool.")
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_proficiency(ability)
