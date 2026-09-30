"""Improvements: the reusable effects Features are composed of
(CharacterImprovement), plus composable modifiers applied directly to items
at construction time (ItemImprovement and its weapon-/armor-specific
subclasses - see CharacterContent.Items.Weapons/Armor).

Ordering contract
-----------------
apply() only RECORDS a fact, on the write-only Effects record
(StatBlocks/Effects.py); the Character works every value out when it's read.
Effects has no way to read anything back, so features, extensions, armor,
weapons, items and fighting styles can apply in any order and give the same
character:

- Flat facts (proficiencies, +N bonuses, resistances, senses) just add up.
- A bonus whose size depends on other stats ("equal to your Wisdom
  modifier", "while you aren't wearing Heavy armor", "equal to your Sorcerer
  level") is a formula - the Value type below, `lambda character: ...` -
  evaluated against the finished Character when it's read.
- Ability increases are recorded with their cap and resolved on read, lowest
  cap first (AbilityScores) - "to a maximum of 20" no longer depends on
  what applied before.
- Alternatives ("if you already have this proficiency, choose another") are
  recorded as conditional grants and resolved on read against every other
  grant (SavingThrowProficiencyOrAlternative).
- Competing formulas never overwrite each other: every AC formula is kept and
  the best applicable one is used (SetArmorClass, MultiAbilityArmorClass);
  roll conditions collect their sources and cancel out on read.
- Requirements (expertise needs proficiency, an armor's Strength) are
  recorded and checked by Character.validate() once everything has applied,
  so what meets them may be granted before or after.

tests/test_feature_apply_order.py enforces this: it applies every effect of
every build in shuffled orders and requires the same character.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, Optional

from Core.Definitions import (
    Ability,
    ArmorType,
    Condition,
    DamageType,
    DiceRollCondition,
    Language,
    Sense,
    Skill,
)
from StatBlocks.ArmorClass import ArmorClassFormula
from StatBlocks.Character import Character
from StatBlocks.Effects import Effects
from StatBlocks.WeaponBonuses import WeaponBonus, WeaponFilter

# A flat bonus, or a formula evaluated against the finished Character at read
# time (see the ordering contract above).
Value = int | Callable[[Character], int]


class CharacterImprovement(ABC):
    """Base class for all CharacterImprovements. Override apply() to record
    this improvement's effects."""

    @abstractmethod
    def apply(self, effects: Effects):
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


class SkillProficiency(CharacterImprovement):
    """Grants proficiency in a fixed list of skills (idempotent flag set)."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def apply(self, effects: Effects):
        for skill in self.skills:
            effects.add_skill_proficiency(skill)


class SkillProficiencyChoice(SkillProficiency):
    """Grants proficiency in user-chosen skills, validated against a pool."""

    def __init__(
        self,
        skills: list[Skill],
        pool: list[Skill],
        count: int,
        error_prefix: str = "Invalid skill choice",
    ):
        _validate_pool(skills, pool, count, error_prefix)
        super().__init__(skills)


class SkillExpertise(CharacterImprovement):
    """Grants expertise in a fixed list of skills.

    Ordering: order-insensitive - the proficiency it requires may be granted
    before or after it; the stat block validates the pairing once every
    feature has applied (Skills.validate)."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def apply(self, effects: Effects):
        for skill in self.skills:
            effects.add_skill_expertise(skill)


class SkillExpertiseChoice(SkillExpertise):
    """Grants expertise in user-chosen skills, validated against a pool."""

    def __init__(
        self,
        skills: list[Skill],
        pool: list[Skill],
        count: int,
        error_prefix: str = "Invalid skill choice",
    ):
        _validate_pool(skills, pool, count, error_prefix)
        super().__init__(skills)


class SavingThrowProficiency(CharacterImprovement):
    """Grants saving throw proficiency for a fixed list of abilities."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, effects: Effects):
        for ability in self.abilities:
            effects.add_saving_throw_proficiency(ability)


class SavingThrowProficiencyChoice(SavingThrowProficiency):
    """Grants saving throw proficiency for user-chosen abilities, validated against a pool."""

    def __init__(
        self,
        abilities: list[Ability],
        pool: list[Ability],
        count: int,
        error_prefix: str = "Invalid saving throw choice",
    ):
        _validate_pool(abilities, pool, count, error_prefix)
        super().__init__(abilities)


class SavingThrowProficiencyOrAlternative(CharacterImprovement):
    """Grants saving throw proficiency in `ability` - or, if the character is
    proficient in it from anything else, in the first of `alternatives` they
    lack ("If you already have this proficiency, you instead gain...").

    Resolved on read against every other grant, whether it applied before or
    after this one (SavingThrows.add_proficiency_or_alternative)."""

    def __init__(self, ability: Ability, alternatives: list[Ability]):
        self.ability = ability
        self.alternatives = alternatives

    def apply(self, effects: Effects):
        effects.add_saving_throw_proficiency_or_alternative(
            self.ability, self.alternatives
        )


class GrantWeaponProficiency(CharacterImprovement):
    """Grants proficiency with weapons, by WeaponProficiency value (a category
    such as Martial weapons, or a single kind such as the Scimitar). Every
    weapon works out whether it's covered when it's read, so the grant may
    apply before or after the weapon is added."""

    def __init__(self, weapon_proficiencies: list[Enum]):
        self.weapon_proficiencies = weapon_proficiencies

    def apply(self, effects: Effects):
        for weapon_proficiency in self.weapon_proficiencies:
            effects.add_weapon_proficiency(weapon_proficiency)


class GrantArmorTraining(CharacterImprovement):
    """Grants training with armor types (Light, Medium, Heavy, Shield)."""

    def __init__(self, armor_types: list[ArmorType]):
        self.armor_types = armor_types

    def apply(self, effects: Effects):
        for armor_type in self.armor_types:
            effects.add_armor_training(armor_type)


class GrantToolProficiency(CharacterImprovement):
    """Grants proficiency with tools (ToolProficiency instances)."""

    def __init__(self, tool_proficiencies: list):
        self.tool_proficiencies = tool_proficiencies

    def apply(self, effects: Effects):
        for tool_proficiency in self.tool_proficiencies:
            effects.add_tool_proficiency(tool_proficiency)


class SavingThrowAdvantage(CharacterImprovement):
    """Grants advantage on saving throws for one or more abilities."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, effects: Effects):
        for ability in self.abilities:
            effects.add_saving_throw_advantage(ability)


class SavingThrowBonus(CharacterImprovement):
    """Adds a bonus to saving throws for one or more abilities - flat, or a
    formula evaluated at read time (e.g. "equal to your Charisma modifier")."""

    def __init__(self, abilities: list[Ability], bonus: Value):
        self.abilities = abilities
        self.bonus = bonus

    def apply(self, effects: Effects):
        for ability in self.abilities:
            if callable(self.bonus):
                effects.add_derived_saving_throw_bonus(ability, self.bonus)
            else:
                effects.add_saving_throw_bonus(ability, self.bonus)


class AbilityScoreBonus(CharacterImprovement):
    """Applies (Ability, bonus) pairs, validated to sum to `total`.

    max_per_ability: largest combined increase one ability may get (e.g. 2 for
        an ASI's "+2 to one or +1 to two", or a background's "+2/+1 or
        +1/+1/+1"). None means unchecked.
    max_score: "to a maximum of N" - an increase never raises a score above
        this, but also never lowers a score something else already pushed
        past it. Resolved on read, lowest cap first, so it doesn't matter
        which increase applied first (see AbilityScores). None means an
        uncapped equipment bonus (a magic item): it applies on top of the
        character's own score and doesn't count toward requirements.
    """

    def __init__(
        self,
        bonuses: list[tuple[Ability, int]],
        total: int,
        error_prefix: str = "Invalid ability bonus",
        max_per_ability: Optional[int] = None,
        max_score: Optional[int] = None,
    ):
        if any(bonus <= 0 for _, bonus in bonuses):
            raise ValueError(f"{error_prefix}: bonuses must be positive.")
        if sum(b[1] for b in bonuses) != total:
            raise ValueError(f"{error_prefix}: bonuses must sum to {total}.")
        if max_per_ability is not None:
            per_ability: dict[Ability, int] = {}
            for ability, bonus in bonuses:
                per_ability[ability] = per_ability.get(ability, 0) + bonus
            if any(b > max_per_ability for b in per_ability.values()):
                raise ValueError(
                    f"{error_prefix}: at most +{max_per_ability} to any one ability."
                )
        self.bonuses = bonuses
        self.max_score = max_score

    def apply(self, effects: Effects):
        for ability, bonus in self.bonuses:
            effects.add_ability_bonus(ability, bonus, max_score=self.max_score)


class SetArmorClass(CharacterImprovement):
    """Worn body armor's AC: `base` + the modifier of `ability` (None = no
    modifier), capped at `ability_modifier_cap`.

    Adds an armor formula (StatBlocks.ArmorClass.ArmorClassFormula) that,
    while worn, replaces every unarmored formula such as Unarmored Defense -
    whether the armor applies before or after the feature."""

    def __init__(
        self,
        base: int,
        ability: Optional[Ability],
        ability_modifier_cap: Optional[int] = None,
    ):
        self.base = base
        self.ability = ability
        # e.g. Medium armor: "add your Dexterity modifier, to a maximum of
        # +2". None means uncapped (Light armor, or no ability at all).
        self.ability_modifier_cap = ability_modifier_cap

    def apply(self, effects: Effects):
        effects.add_armor_class_formula(
            ArmorClassFormula(
                base=self.base,
                abilities=frozenset([self.ability] if self.ability else []),
                ability_modifier_cap=self.ability_modifier_cap,
                is_armor=True,
            )
        )


class MultiAbilityArmorClass(CharacterImprovement):
    """An unarmored AC formula: `base` + the summed modifiers of `abilities`
    (e.g. Unarmored Defense: 10 + DEX + CON).

    Adds a formula instead of overwriting AC: the character uses the best
    applicable one, so two such features (a Barbarian/Monk multiclass) never
    stack, and worn armor replaces them. allows_shield=False for formulas that
    stop working while a Shield is wielded."""

    def __init__(self, base: int, abilities: list[Ability], allows_shield: bool = True):
        self.base = base
        self.abilities = abilities
        self.allows_shield = allows_shield

    def apply(self, effects: Effects):
        effects.add_armor_class_formula(
            ArmorClassFormula(
                base=self.base,
                abilities=frozenset(self.abilities),
                allows_shield=self.allows_shield,
            )
        )


class ArmorClassBonus(CharacterImprovement):
    """Adds a bonus to AC - flat, or a formula evaluated at read time (e.g.
    "+1 while wearing Heavy armor")."""

    def __init__(self, bonus: Value):
        self.bonus = bonus

    def apply(self, effects: Effects):
        if callable(self.bonus):
            effects.add_derived_armor_class_bonus(self.bonus)
        else:
            effects.add_armor_class_bonus(self.bonus)


# ── Weapon attack and damage bonuses ──────────────────────────────────────────


class WeaponAttackBonus(CharacterImprovement):
    """+`value` to attack rolls with every weapon `applies_to` accepts (e.g.
    Archery: Ranged weapons). Recorded on the stat block, never written into
    the weapon, so which weapons it covers is checked on read."""

    def __init__(self, applies_to: WeaponFilter, value: int, source: str):
        self.bonus = WeaponBonus(applies_to, value, source)

    def apply(self, effects: Effects):
        effects.add_weapon_attack_bonus(self.bonus)


class WeaponDamageBonus(CharacterImprovement):
    """+`value` to damage rolls with every weapon `applies_to` accepts (e.g.
    Dueling: one-handed Melee weapons). See WeaponAttackBonus."""

    def __init__(self, applies_to: WeaponFilter, value: int, source: str):
        self.bonus = WeaponBonus(applies_to, value, source)

    def apply(self, effects: Effects):
        effects.add_weapon_damage_bonus(self.bonus)


# ── Skill roll conditions ─────────────────────────────────────────────────────


class SkillRollCondition(CharacterImprovement):
    """Applies a roll condition (advantage/disadvantage/neutral) to a specific skill.
    `reason` names where the condition comes from (e.g. the item or feature name)
    on the character sheet."""

    def __init__(
        self, skill: Skill, condition: DiceRollCondition, reason: Optional[str] = None
    ):
        self.skill = skill
        self.condition = condition
        self.reason = reason

    def apply(self, effects: Effects):
        effects.set_skill_roll_condition(self.skill, self.condition, self.reason)


class StealthDisadvantage(SkillRollCondition):
    """Imposes disadvantage on Stealth checks."""

    def __init__(self, reason: Optional[str] = None):
        super().__init__(Skill.STEALTH, DiceRollCondition.DISADVANTAGE, reason)


class InitiativeProficiency(CharacterImprovement):
    """Grants proficiency bonus to initiative rolls."""

    def apply(self, effects: Effects):
        effects.add_initiative_proficiency()


class InitiativeRollCondition(CharacterImprovement):
    """Applies a roll condition (e.g. advantage) to initiative rolls."""

    def __init__(self, condition: DiceRollCondition):
        self.condition = condition

    def apply(self, effects: Effects):
        effects.add_initiative_roll_condition(self.condition)


class InitiativeBonus(CharacterImprovement):
    """Adds a bonus to initiative rolls - flat, or a formula evaluated at read
    time (as distinct from InitiativeProficiency, which adds the full
    proficiency bonus)."""

    def __init__(self, bonus: Value):
        self.bonus = bonus

    def apply(self, effects: Effects):
        if callable(self.bonus):
            effects.add_derived_initiative_bonus(self.bonus)
        else:
            effects.add_initiative_bonus(self.bonus)


class HitPointsBonus(CharacterImprovement):
    """Adds to the hit point maximum - flat, or a formula evaluated at read
    time (e.g. "+1 per Sorcerer level")."""

    def __init__(self, bonus: Value):
        self.bonus = bonus

    def apply(self, effects: Effects):
        if callable(self.bonus):
            effects.add_derived_hit_points_bonus(self.bonus)
        else:
            effects.add_hit_points_bonus(self.bonus)


class HitPointsPerLevelBonus(HitPointsBonus):
    """Adds `multiplier × character level` to the hit point maximum."""

    def __init__(self, multiplier: int):
        self.multiplier = multiplier
        super().__init__(lambda character: multiplier * character.character_level)


class SkillBonus(CharacterImprovement):
    """Adds a bonus to a specific skill - flat, or a formula evaluated at read
    time (e.g. "equal to your Wisdom modifier"). `source` names where the
    bonus comes from (e.g. the item or feature name) on the character sheet."""

    def __init__(self, skill: Skill, bonus: Value, source: Optional[str] = None):
        self.skill = skill
        self.bonus = bonus
        self.source = source

    def apply(self, effects: Effects):
        if callable(self.bonus):
            effects.add_derived_skill_bonus(
                self.skill, self.bonus, self.source or "Other"
            )
        elif self.source is not None:
            effects.add_skill_bonus(self.skill, self.bonus, self.source)
        else:
            effects.add_skill_bonus(self.skill, self.bonus)


class SkillToAbilityOverride(CharacterImprovement):
    """Remaps one or more skills to use a different ability score."""

    def __init__(self, skills: list[Skill], ability: Ability):
        self.skills = skills
        self.ability = ability

    def apply(self, effects: Effects):
        for skill in self.skills:
            effects.add_skill_ability(skill, self.ability)


class JackOfAllTradesBonus(CharacterImprovement):
    """Adds half proficiency bonus to every skill the character lacks proficiency in.

    Ordering: order-insensitive - both proficiency and the bonus are checked
    at read time, so a proficiency granted later (by any builder, the
    species, or an item) correctly switches the bonus off for that skill."""

    def apply(self, effects: Effects):
        for skill in Skill:
            effects.add_derived_skill_bonus(
                skill, self._bonus_for(skill), "Jack of All Trades"
            )

    @staticmethod
    def _bonus_for(skill: Skill) -> Callable[[Character], int]:
        def bonus(character: Character) -> int:
            if character.skills.is_proficient(skill):
                return 0
            return character.get_proficiency_bonus() // 2

        return bonus


class SpeedBonus(CharacterImprovement):
    """Increases the character's movement speed - by a flat amount, or a
    formula evaluated at read time (e.g. "+10 feet while you aren't wearing
    Heavy armor")."""

    def __init__(self, bonus: Value):
        self.bonus = bonus

    def apply(self, effects: Effects):
        if callable(self.bonus):
            effects.add_derived_speed_bonus(self.bonus)
        else:
            effects.add_speed_bonus(self.bonus)


class CarryingCapacityBonus(CharacterImprovement):
    """Increases the character's carrying capacity (in item slots).

    The source label identifies where the extra slots come from
    (e.g. "Backpack") so the character sheet can group them.
    """

    def __init__(self, bonus: int, source: str = "Item"):
        self.bonus = bonus
        self.source = source

    def apply(self, effects: Effects):
        effects.add_carrying_capacity_bonus(self.source, self.bonus)


class SpellSaveDCBonus(CharacterImprovement):
    """Adds a flat bonus to spell save DC (calculate_difficulty_class[_for_ability])."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, effects: Effects):
        effects.add_spell_save_dc_bonus(self.bonus)


class StrengthRequirement(CharacterImprovement):
    """Requires a minimum Strength score (house rule: the build is rejected;
    PHB: speed -10 ft instead).

    Recorded, then checked by Character.validate() once everything
    has applied - so every feat/background/ASI increase counts wherever it
    lands in the order. It checks the character's own score: a Strength bonus
    from an item cannot satisfy an armor requirement."""

    def __init__(self, min_score: int, reason: str = "armor requirement"):
        self.min_score = min_score
        self.reason = reason

    def apply(self, effects: Effects):
        effects.add_ability_requirement(Ability.STRENGTH, self.min_score, self.reason)


# ── Resistances, immunities, senses, and languages ────────────────────────────


class DamageResistance(CharacterImprovement):
    """Grants resistance to a damage type. `source` names where the
    resistance comes from (e.g. the feature or item name) on the character
    sheet."""

    def __init__(self, damage_type: DamageType, source: str):
        self.damage_type = damage_type
        self.source = source

    def apply(self, effects: Effects):
        effects.add_damage_resistance(self.damage_type, self.source)


class DamageImmunity(CharacterImprovement):
    """Grants immunity to a damage type. `source` names where the immunity
    comes from on the character sheet."""

    def __init__(self, damage_type: DamageType, source: str):
        self.damage_type = damage_type
        self.source = source

    def apply(self, effects: Effects):
        effects.add_damage_immunity(self.damage_type, self.source)


class ConditionImmunity(CharacterImprovement):
    """Grants immunity to a condition. `source` names where the immunity
    comes from on the character sheet."""

    def __init__(self, condition: Condition, source: str):
        self.condition = condition
        self.source = source

    def apply(self, effects: Effects):
        effects.add_condition_immunity(self.condition, self.source)


class GrantSense(CharacterImprovement):
    """Grants a special sense (e.g. Darkvision) out to `range_feet`. Granting
    the same sense again from a different source keeps the larger range."""

    def __init__(self, sense: Sense, range_feet: int, source: str):
        self.sense = sense
        self.range_feet = range_feet
        self.source = source

    def apply(self, effects: Effects):
        effects.add_sense(self.sense, self.range_feet, self.source)


class GrantOrExtendSense(CharacterImprovement):
    """ "You gain Darkvision with a range of 60 feet. If you already have
    Darkvision, its range increases by 60 feet." Resolved on read: the range
    is the best other grant of the sense plus `range_feet`, whether those
    grants applied before or after this one."""

    def __init__(self, sense: Sense, range_feet: int, source: str):
        self.sense = sense
        self.range_feet = range_feet
        self.source = source

    def apply(self, effects: Effects):
        effects.add_sense_or_extension(self.sense, self.range_feet, self.source)


class GrantLanguage(CharacterImprovement):
    """Grants knowledge of a language. `source` names where the language
    comes from (e.g. species or feat name) on the character sheet."""

    def __init__(self, language: Language, source: str):
        self.language = language
        self.source = source

    def apply(self, effects: Effects):
        effects.add_language(self.language, self.source)


# ── Informational-only item improvements ─────────────────────────────────────
# The mechanics below have no automated hook in this engine: no incoming-
# damage pipeline, no current-HP or "Bloodied" state, no critical-hit-range
# model, no per-target combat state, and no spell-slot expenditure/recovery
# tracking during play (spell_slots is a static max-by-level table, not a
# live tracker). Each still exists as a concrete, named CharacterImprovement -
# so a magic item can reference a real, discoverable class and store its
# flavor parameters - but apply() is intentionally a no-op; the effect must
# be tracked manually at the table. This mirrors the "informational card, no
# computation" pattern used elsewhere for effects this codebase can't compute
# automatically (e.g. FightingStyles.Interception/Protection, both marked
# "(calculate manually)"; SpeciesFeatures.DwarfFeatures.DwarvenResilience,
# a Feature with a description but no apply() override at all).
#
# Note: resistance/immunity to damage types and conditions ARE tracked (see
# DamageResistance/DamageImmunity/ConditionImmunity above) and shown on the
# character sheet - but only as a record of what the character has, not as a
# live incoming-damage pipeline that automatically halves/nullifies damage
# rolled elsewhere in the engine. ElementalResistance below stays
# informational-only rather than reusing DamageResistance because its
# existing call sites (GeneralFeats.ElementalFamiliar) grant resistance to a
# summoned familiar, not the wielding character - applying it to the
# character's own stat block would misattribute the effect.


class InformationalImprovement(CharacterImprovement):
    """Base class for CharacterImprovements with no automated mechanical hook in this
    engine. apply() is intentionally a no-op; track the effect manually."""

    def apply(self, effects: Effects) -> None:
        pass


class SpellResistance(InformationalImprovement):
    """Advantage on saving throws against spells. Not auto-applied: this
    engine's saving-throw advantage (SavingThrowAdvantage) is tracked per
    ability only, with no "was this against a spell" qualifier, so granting
    it here would overreach into advantage on that ability's non-spell
    saves too."""


class ElementalMastery(InformationalImprovement):
    """Deal extra damage of a chosen damage type on your attacks. Not
    auto-applied: this engine has no character-level "bonus damage on every
    attack" hook - only a per-weapon one (Weapons.AddExtraDamage)."""

    def __init__(self, damage_type: DamageType, bonus: int = 1):
        self.damage_type = damage_type
        self.bonus = bonus


class ExposedWeakness(InformationalImprovement):
    """Creatures you damage become Vulnerable to a chosen damage type. Not
    auto-applied: it targets an enemy, not the wielder - there's no
    enemy/target state reachable from a CharacterImprovement's apply()."""

    def __init__(self, damage_type: DamageType):
        self.damage_type = damage_type


class ArcaneRecovery(InformationalImprovement):
    """Restore a spell slot, a number of times per day equal to one-third
    of your level (rounded down, minimum 1). Not to be confused with the
    Wizard class feature of the same name (CharacterContent.Features.ClassFeatures.Wizard.
    WizardFeatures.ArcaneRecovery). Not auto-applied: this engine doesn't
    track spell slot expenditure/recovery during play."""


class DamageMitigation(InformationalImprovement):
    """Take reduced damage from a chosen damage type. Not auto-applied: no
    incoming-damage pipeline exists in this engine."""

    def __init__(self, damage_type: DamageType):
        self.damage_type = damage_type


class CollateralDamage(InformationalImprovement):
    """Your attacks also deal damage to creatures near your target, even if
    they aren't the target. Not auto-applied: no per-target combat state
    exists in this engine."""


class DangerousCollateralDamage(InformationalImprovement):
    """Your attacks also deal damage to all creatures near your target
    (except yourself), including allies. Not auto-applied: same limitation
    as CollateralDamage."""


class EmpoweredHealing(InformationalImprovement):
    """Healing you provide restores additional hit points. Not auto-applied:
    no healing pipeline exists in this engine."""


class DamageReduction(InformationalImprovement):
    """Incoming damage is reduced by a flat amount. Not auto-applied: no
    incoming-damage pipeline exists in this engine."""

    def __init__(self, amount: Optional[int] = None):
        self.amount = amount


class ElementalResistance(InformationalImprovement):
    """Resistance to a chosen damage type. Not auto-applied: no
    resistance/vulnerability/immunity tracking exists in this engine."""

    def __init__(self, damage_type: DamageType):
        self.damage_type = damage_type


class CriticalFailure(InformationalImprovement):
    """You cannot score critical hits. Not auto-applied: no critical-hit
    computation exists in this engine."""


class CriticalImmunity(InformationalImprovement):
    """Enemies cannot score critical hits against you. Not auto-applied:
    same limitation as CriticalFailure."""


class IronWill(InformationalImprovement):
    """Immunity, or advantage (your choice which), against being Frightened
    or Charmed. Not auto-applied: this engine's saving-throw advantage is
    tracked per ability only, with no per-condition qualifier, so it can't
    be distinguished from blanket Wisdom/Charisma save advantage - applying
    it automatically would overreach."""


class Executioner(InformationalImprovement):
    """Deal increased damage to Bloodied or otherwise low-HP creatures. Not
    auto-applied: this engine doesn't track current/max HP or a "Bloodied"
    threshold for any creature."""


# ──────────────────────────────────────────────────────────────────────────────
# ItemImprovement: composable modifiers applied to an item (weapon, armor, or
# any future equipment type) at construction time - e.g. a magic variant or a
# homebrew reskin. Distinct from CharacterImprovement above: apply() mutates the item
# instance itself (its name, description, GP value, homebrew flag), not the
# wielding character's stat block. Type-specific improvements (e.g. a
# weapon's damage die, an armor's AC) belong in their own equipment module
# (see CharacterContent.Items.Weapons.WeaponImprovement / Armor.ArmorImprovement)
# and should subclass this.
# ──────────────────────────────────────────────────────────────────────────────


class ItemImprovement(ABC):
    """Base class for item improvements. Override apply() to modify the item.

    Expects the target item to already have its base (pre-improvement)
    attributes set - name, description_text, value, is_homebrew - since
    apply() mutates them directly (see AbstractWeapon.__init__ /
    AbstractArmor.__init__: base_stats() runs first, improvements after)."""

    @abstractmethod
    def apply(self, item) -> None:
        pass


class SetItemName(ItemImprovement):
    """Overrides the item's display name."""

    def __init__(self, name: str):
        self.name = name

    def apply(self, item) -> None:
        item.name = self.name


class AddItemDescription(ItemImprovement):
    """Appends text to the item's description."""

    def __init__(self, text: str):
        self.text = text

    def apply(self, item) -> None:
        item.description_text = (
            f"{item.description_text}\n{self.text}"
            if item.description_text
            else self.text
        )


class SetItemDescription(ItemImprovement):
    """Overrides (replaces, rather than appends to) the item's description."""

    def __init__(self, text: str):
        self.text = text

    def apply(self, item) -> None:
        item.description_text = self.text


class SetItemValue(ItemImprovement):
    """Overrides the item's GP value. Pass None to mark it unpriced (e.g. a
    unique magic item that no longer has a standard market price)."""

    def __init__(self, value: Optional[float]):
        self.value = value

    def apply(self, item) -> None:
        item.value = self.value


class SetItemHomebrew(ItemImprovement):
    """Flags the item as homebrew (or, with is_homebrew=False, as official)."""

    def __init__(self, is_homebrew: bool = True):
        self.is_homebrew = is_homebrew

    def apply(self, item) -> None:
        item.is_homebrew = self.is_homebrew


class Reskin(ItemImprovement):
    """Convenience bundle for the common case of rebranding a base item as a
    new named variant: overrides its name and description, unsets its GP
    value (it's no longer standard equipment), and flags it as homebrew.
    Equivalent to combining SetItemName, SetItemDescription,
    SetItemValue(None), and SetItemHomebrew()."""

    def __init__(self, name: str, description: str, is_homebrew: bool = True):
        self.name = name
        self.description = description
        self.is_homebrew = is_homebrew

    def apply(self, item) -> None:
        SetItemName(self.name).apply(item)
        SetItemDescription(self.description).apply(item)
        SetItemValue(None).apply(item)
        SetItemHomebrew(self.is_homebrew).apply(item)


# add_improvement()/setup_improvements() - the access point for composing
# ItemImprovements onto an item - live directly on CharacterContent.Items.Items.Item,
# not here, so that any Item subclass (not just weapons/armor) can use them
# without an extra mixin base class.
