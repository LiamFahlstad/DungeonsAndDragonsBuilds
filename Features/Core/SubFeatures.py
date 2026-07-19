"""SubFeatures: reusable stat-block mutations composed into Features.

Ordering contract
-----------------
Features apply in two phases (see CharacterSheetData.setup_character_stat_block):
every ApplyWhen.IMMEDIATE feature first, then every ApplyWhen.LAST feature,
each phase in call order. Armors, weapons and items apply after all features.
A SubFeature falls into one of three categories:

- Additive or flag-setting writes (proficiencies, ability/AC/skill/speed
  bonuses): order-insensitive because derived values (AC, skill totals, HP)
  are computed lazily at read time. Safe as IMMEDIATE - and proficiency
  grants MUST stay IMMEDIATE so that phase-LAST readers see them.
- Overwrites (SetArmorClass, MultiAbilityArmorClass, roll conditions):
  last writer wins, so only their order relative to each other matters.
  Armor applying after all features is what lets worn armor override an
  Unarmored Defense formula, matching the game rules.
- Eager readers (SkillExpertise, JackOfAllTradesBonus, StrengthRequirement):
  they read state at apply time, so every write they depend on must already
  have happened. Features carrying these must be added with ApplyWhen.LAST,
  unless the feature itself performs the prerequisite write first (e.g.
  SkillExpert and BlessingsOfKnowledge grant the proficiency before the
  expertise within one apply call).
"""

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
    """Grants proficiency in a fixed list of skills.

    Ordering: idempotent flag set - but keep the owning feature IMMEDIATE,
    since phase-LAST readers (SkillExpertise, JackOfAllTradesBonus) must see
    every proficiency."""

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
    """Grants expertise in a fixed list of skills.

    Ordering: eager reader - raises if the skill isn't already proficient, so
    the owning feature must be added with ApplyWhen.LAST (proficiency can come
    from any builder, including the species, which merges last), unless the
    feature itself grants the proficiency earlier in its own apply()."""

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
    """Sets base AC and replaces the ability modifier with a single ability (None = no modifier).

    Ordering: overwrite - the last SetArmorClass/MultiAbilityArmorClass to
    apply wins the base and ability set. Additive ArmorClassBonus values live
    in a separate accumulator and survive regardless of order. Armors apply
    after all features, so worn armor deliberately overrides feature-provided
    AC formulas such as Unarmored Defense."""

    def __init__(self, base: int, ability: Optional[Ability]):
        self.base = base
        self.ability = ability

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(self.base)
        character_stat_block.combat.change_armor_class_ability(self.ability)


class MultiAbilityArmorClass(SubFeature):
    """Sets base AC and adds multiple ability modifiers (e.g. unarmored defense formulas).

    Ordering: overwrite of the base, but the listed abilities are ADDED to the
    existing ability set (which starts as {DEX}) rather than replacing it - so
    it must not run after a SetArmorClass that cleared or changed the set."""

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
    """Applies a roll condition (advantage/disadvantage/neutral) to a specific skill.
    `reason` names where the condition comes from (e.g. the item or feature name)
    on the character sheet."""

    def __init__(self, skill: Skill, condition: DiceRollCondition, reason: Optional[str] = None):
        self.skill = skill
        self.condition = condition
        self.reason = reason

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.set_skill_roll_condition(self.skill, self.condition, self.reason)


class StealthDisadvantage(SkillRollCondition):
    """Imposes disadvantage on Stealth checks."""

    def __init__(self, reason: Optional[str] = None):
        super().__init__(Skill.STEALTH, DiceRollCondition.DISADVANTAGE, reason)


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
    """Adds a flat bonus to a specific skill. `source` names where the bonus
    comes from (e.g. the item or feature name) on the character sheet."""

    def __init__(self, skill: Skill, bonus: int, source: Optional[str] = None):
        self.skill = skill
        self.bonus = bonus
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        if self.source is not None:
            character_stat_block.skills.add_skill_bonus(self.skill, self.bonus, self.source)
        else:
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
    """Adds half proficiency bonus to every skill the character lacks proficiency in.

    Ordering: eager reader - snapshots is_proficient for every skill, so the
    owning feature must be added with ApplyWhen.LAST, after every proficiency
    grant from every builder."""

    def apply(self, character_stat_block: CharacterStatBlock):
        half_proficiency = character_stat_block.get_proficiency_bonus() // 2
        for skill in Skill:
            if not character_stat_block.skills.is_proficient(skill):
                character_stat_block.skills.add_skill_bonus(
                    skill, half_proficiency, "Jack of All Trades"
                )


# ── Movement ──────────────────────────────────────────────────────────────────

class SpeedBonus(SubFeature):
    """Increases the character's movement speed by a flat amount."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.speed += self.bonus


# ── Carrying capacity ────────────────────────────────────────────────────────

class CarryingCapacityBonus(SubFeature):
    """Increases the character's carrying capacity (in item slots).

    The source label identifies where the extra slots come from
    (e.g. "Backpack") so the character sheet can group them.
    """

    def __init__(self, bonus: int, source: str = "Item"):
        self.bonus = bonus
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.carrying_capacity_sources.append((self.source, self.bonus))


# ── Prerequisites ─────────────────────────────────────────────────────────────

class StrengthRequirement(SubFeature):
    """Raises ValueError if the character's Strength score is below the minimum.

    Ordering: eager reader - validated when armors apply, i.e. after all
    features (so feat/background ability bonuses count) but BEFORE items, so
    a Strength bonus granted by an item cannot satisfy an armor requirement."""

    def __init__(self, min_score: int):
        self.min_score = min_score

    def apply(self, character_stat_block: CharacterStatBlock):
        if character_stat_block.get_ability_score(Ability.STRENGTH) < self.min_score:
            raise ValueError(f"Strength score must be at least {self.min_score}.")
