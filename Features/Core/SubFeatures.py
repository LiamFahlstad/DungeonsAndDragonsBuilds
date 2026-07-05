from abc import ABC, abstractmethod
from typing import Optional

from Definitions import Ability, DiceRollCondition, Skill
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class SubFeature(ABC):
    """Base class for all SubFeatures. Override apply() to modify the stat block."""

    @abstractmethod
    def apply(self, character_stat_block: CharacterStatBlock):
        pass


def _validate_pool(items, pool, count: int, error_prefix: str):
    """Shared validation for pool-based choices: correct count, no duplicates, all in pool."""
    if len(items) != count:
        raise ValueError(f"{error_prefix}: expected {count}, got {len(items)}.")
    if len(items) != len(set(items)):
        raise ValueError(f"{error_prefix}: duplicates provided.")
    for item in items:
        if item not in pool:
            raise ValueError(f"{error_prefix}: {item} is not in the allowed pool.")


# ── Skill proficiency ─────────────────────────────────────────────────────────

class SkillProficiency(SubFeature):
    """Grants proficiency in a fixed list of skills."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.add_skill_proficiency(skill)


class SkillProficiencyChoice(SkillProficiency):
    """Grants proficiency in user-chosen skills, validated against a pool."""

    def __init__(self, skills: list[Skill], pool: list[Skill], count: int, error_prefix: str = "Invalid skill choice"):
        _validate_pool(skills, pool, count, error_prefix)
        super().__init__(skills)


# ── Skill expertise ───────────────────────────────────────────────────────────

class SkillExpertise(SubFeature):
    """Grants expertise in a fixed list of skills."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.add_skill_expertise(skill)


class SkillExpertiseChoice(SkillExpertise):
    """Grants expertise in user-chosen skills, validated against a pool."""

    def __init__(self, skills: list[Skill], pool: list[Skill], count: int, error_prefix: str = "Invalid skill choice"):
        _validate_pool(skills, pool, count, error_prefix)
        super().__init__(skills)


# ── Saving throw proficiency ──────────────────────────────────────────────────

class SavingThrowProficiency(SubFeature):
    """Grants saving throw proficiency for a fixed list of abilities."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_proficiency(ability)


class SavingThrowProficiencyChoice(SavingThrowProficiency):
    """Grants saving throw proficiency for user-chosen abilities, validated against a pool."""

    def __init__(self, abilities: list[Ability], pool: list[Ability], count: int, error_prefix: str = "Invalid saving throw choice"):
        _validate_pool(abilities, pool, count, error_prefix)
        super().__init__(abilities)


# ── Saving throw advantage ────────────────────────────────────────────────────

class SavingThrowAdvantage(SubFeature):
    """Grants advantage on saving throws for one or more abilities."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_advantage(ability)


# ── Ability scores ────────────────────────────────────────────────────────────

class AbilityScoreBonus(SubFeature):
    """Applies (Ability, bonus) pairs, validated to sum to `total`."""

    def __init__(self, bonuses: list[tuple[Ability, int]], total: int, error_prefix: str = "Invalid ability bonus"):
        if sum(b[1] for b in bonuses) != total:
            raise ValueError(f"{error_prefix}: bonuses must sum to {total}.")
        self.bonuses = bonuses

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)


# ── Armor class ───────────────────────────────────────────────────────────────

class SetArmorClass(SubFeature):
    """Sets base AC and replaces the ability modifier with a single ability (None = no modifier)."""

    def __init__(self, base: int, ability: Optional[Ability]):
        self.base = base
        self.ability = ability

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(self.base)
        character_stat_block.combat.change_armor_class_ability(self.ability)


class MultiAbilityArmorClass(SubFeature):
    """Sets base AC and adds multiple ability modifiers (e.g. unarmored defense formulas)."""

    def __init__(self, base: int, abilities: list[Ability]):
        self.base = base
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(self.base)
        for ability in self.abilities:
            character_stat_block.combat.add_armor_class_ability(ability)


class ArmorClassBonus(SubFeature):
    """Adds a flat bonus to AC."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.increase_armor_class(self.bonus)


# ── Skill roll conditions ─────────────────────────────────────────────────────

class SkillRollCondition(SubFeature):
    """Applies a roll condition (advantage/disadvantage/neutral) to a specific skill."""

    def __init__(self, skill: Skill, condition: DiceRollCondition):
        self.skill = skill
        self.condition = condition

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.set_skill_roll_condition(self.skill, self.condition)


class StealthDisadvantage(SkillRollCondition):
    """Imposes disadvantage on Stealth checks."""

    def __init__(self):
        super().__init__(Skill.STEALTH, DiceRollCondition.DISADVANTAGE)


# ── Initiative ────────────────────────────────────────────────────────────────

class InitiativeProficiency(SubFeature):
    """Grants proficiency bonus to initiative rolls."""

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_initiative_proficiency()


class InitiativeRollCondition(SubFeature):
    """Applies a roll condition (e.g. advantage) to initiative rolls."""

    def __init__(self, condition: DiceRollCondition):
        self.condition = condition

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_initiative_roll_condition(self.condition)


# ── Hit points ────────────────────────────────────────────────────────────────

class HitPointsPerLevelBonus(SubFeature):
    """Adds `multiplier × character_level` to the hit points bonus."""

    def __init__(self, multiplier: int):
        self.multiplier = multiplier

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.hit_points_bonus += self.multiplier * character_stat_block.character_level


# ── Skill modifiers ───────────────────────────────────────────────────────────

class SkillBonus(SubFeature):
    """Adds a flat bonus to a specific skill."""

    def __init__(self, skill: Skill, bonus: int):
        self.skill = skill
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.skills.add_skill_bonus(self.skill, self.bonus)


class SkillToAbilityOverride(SubFeature):
    """Remaps one or more skills to use a different ability score."""

    def __init__(self, skills: list[Skill], ability: Ability):
        self.skills = skills
        self.ability = ability

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.update_skill_to_ability(skill, self.ability)


class JackOfAllTradesBonus(SubFeature):
    """Adds half proficiency bonus to every skill the character lacks proficiency in."""

    def apply(self, character_stat_block: CharacterStatBlock):
        half_proficiency = character_stat_block.get_proficiency_bonus() // 2
        for skill in Skill:
            if not character_stat_block.skills.is_proficient(skill):
                character_stat_block.skills.add_skill_bonus(skill, half_proficiency)


# ── Movement ──────────────────────────────────────────────────────────────────

class SpeedBonus(SubFeature):
    """Increases the character's movement speed by a flat amount."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.speed += self.bonus


# ── Prerequisites ─────────────────────────────────────────────────────────────

class StrengthRequirement(SubFeature):
    """Raises ValueError if the character's Strength score is below the minimum."""

    def __init__(self, min_score: int):
        self.min_score = min_score

    def apply(self, character_stat_block: CharacterStatBlock):
        if character_stat_block.get_ability_score(Ability.STRENGTH) < self.min_score:
            raise ValueError(f"Strength score must be at least {self.min_score}.")
