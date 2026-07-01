from typing import Optional

from Definitions import Ability, DiceRollCondition, Skill
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


class AbilityScoreBonus:
    """Applies a list of (Ability, bonus) pairs, validated to sum to `total`."""

    def __init__(self, bonuses: list[tuple[Ability, int]], total: int, error_prefix: str = "Invalid ability bonus"):
        if sum(b[1] for b in bonuses) != total:
            raise ValueError(f"{error_prefix}: bonuses must sum to {total}.")
        self.bonuses = bonuses

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)


class SetArmorClass:
    """Sets the base AC and the ability modifier that adds to it (None for no modifier)."""

    def __init__(self, base: int, ability: Optional[Ability]):
        self.base = base
        self.ability = ability

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(self.base)
        character_stat_block.combat.change_armor_class_ability(self.ability)


class ArmorClassBonus:
    """Adds a flat bonus to AC."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.increase_armor_class(self.bonus)


class StealthDisadvantage:
    """Imposes disadvantage on Stealth checks."""

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.set_skill_roll_condition(Skill.STEALTH, DiceRollCondition.DISADVANTAGE)


class StrengthRequirement:
    """Raises ValueError if the character's Strength score is below the minimum."""

    def __init__(self, min_score: int):
        self.min_score = min_score

    def apply(self, character_stat_block: CharacterStatBlock):
        if character_stat_block.get_ability_score(Ability.STRENGTH) < self.min_score:
            raise ValueError(f"Strength score must be at least {self.min_score}.")


class SavingThrowAdvantage:
    """Grants advantage on saving throws for one or more abilities."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_advantage(ability)


class HitPointsPerLevelBonus:
    """Adds `multiplier × character_level` to the hit points bonus."""

    def __init__(self, multiplier: int):
        self.multiplier = multiplier

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.hit_points_bonus += self.multiplier * character_stat_block.character_level


class InitiativeRollCondition:
    """Applies a roll condition (e.g. advantage) to initiative rolls."""

    def __init__(self, condition: DiceRollCondition):
        self.condition = condition

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_initiative_roll_condition(self.condition)


class SkillRollCondition:
    """Applies a roll condition (e.g. advantage/disadvantage) to a specific skill."""

    def __init__(self, skill: Skill, condition: DiceRollCondition):
        self.skill = skill
        self.condition = condition

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.set_skill_roll_condition(self.skill, self.condition)


class InitiativeProficiency:
    """Grants proficiency bonus to initiative rolls."""

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_initiative_proficiency()


class JackOfAllTradesBonus:
    """Adds half proficiency bonus to every skill the character lacks proficiency in."""

    def apply(self, character_stat_block: CharacterStatBlock):
        half_proficiency = character_stat_block.get_proficiency_bonus() // 2
        for skill in Skill:
            if not character_stat_block.skills.is_proficient(skill):
                character_stat_block.skills.add_skill_bonus(skill, half_proficiency)


class MultiAbilityArmorClass:
    """Sets base AC and adds multiple ability modifiers (e.g. unarmored defense formulas)."""

    def __init__(self, base: int, abilities: list[Ability]):
        self.base = base
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(self.base)
        for ability in self.abilities:
            character_stat_block.combat.add_armor_class_ability(ability)


class SavingThrowProficiency:
    """Grants saving throw proficiency for a fixed list of abilities (no pool validation)."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_proficiency(ability)


class SkillBonus:
    """Adds a flat bonus to a specific skill."""

    def __init__(self, skill: Skill, bonus: int):
        self.skill = skill
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_bonus(self.skill, self.bonus)


class SkillToAbilityOverride:
    """Remaps one or more skills to use a different ability score."""

    def __init__(self, skills: list[Skill], ability: Ability):
        self.skills = skills
        self.ability = ability

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.update_skill_to_ability(skill, self.ability)


class SpeedBonus:
    """Increases the character's movement speed by a flat amount."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.speed += self.bonus
