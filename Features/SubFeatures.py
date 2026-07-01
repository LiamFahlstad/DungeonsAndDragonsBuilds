from Definitions import Skill
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
