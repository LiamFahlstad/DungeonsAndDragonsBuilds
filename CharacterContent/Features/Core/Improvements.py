"""Improvements: reusable stat-block mutations composed into Features
(CharacterImprovement), plus composable modifiers applied directly to items
at construction time (ItemImprovement and its weapon-/armor-specific
subclasses - see CharacterContent.Items.Weapons/Armor).

Ordering contract
-----------------
Features (and their extensions) apply in the order they were granted, then
armor, then armor-conditional effects (Feature.apply_after_armor), then
weapons and items - see CharacterSheetData.setup_character_stat_block. An
improvement must give the same result wherever it lands in that order:

- Writes (proficiencies, flat ability/AC/skill/speed bonuses) are
  order-insensitive because derived values (AC, skill totals, HP) are
  computed at read time.
- A bonus whose size depends on other stats ("equal to your Wisdom
  modifier", "half your Proficiency Bonus") must never be computed inside
  apply() - that freezes it at whatever the stat was when the feature ran,
  missing later ASIs and ability-raising items. Pass a formula instead (the
  Value type below: SkillBonus/SavingThrowBonus/InitiativeBonus accept
  `lambda cs: ...`), which the stat block evaluates at read time.
- Requirements ("expertise needs proficiency") are recorded and validated
  once every feature has applied, so the prerequisite may come from any
  builder or the species, in any order.
- Overwrites (SetArmorClass, MultiAbilityArmorClass, roll conditions): last
  writer wins. Armor applying after all features is what lets worn armor
  override an Unarmored Defense formula, matching the game rules.

The only deliberately order-dependent effects are chronological ones - an
increase "to a maximum of 20" (AbilityScoreBonus.max_score), or "if you're
already proficient, choose another" (SkillExpert, IronMind) - which resolve
against what was granted before them. tests/test_feature_apply_order.py
enforces this: it fails on any other apply() that reads derived stats.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional

from Core.Definitions import (
    Ability,
    Condition,
    DamageType,
    DiceRollCondition,
    Language,
    Sense,
    Skill,
)
from StatBlocks.CharacterStatBlock import CharacterStatBlock

# A flat bonus, or a formula evaluated against the final stat block at read
# time (see the ordering contract above).
Value = int | Callable[[CharacterStatBlock], int]


class CharacterImprovement(ABC):
    """Base class for all CharacterImprovements. Override apply() to modify the stat block."""

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


class SkillProficiency(CharacterImprovement):
    """Grants proficiency in a fixed list of skills (idempotent flag set)."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.add_skill_proficiency(skill)


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
    feature has applied (SkillsStatBlock.validate)."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.add_skill_expertise(skill)


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

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_proficiency(ability)


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


class SavingThrowAdvantage(CharacterImprovement):
    """Grants advantage on saving throws for one or more abilities."""

    def __init__(self, abilities: list[Ability]):
        self.abilities = abilities

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            character_stat_block.saving_throws.add_advantage(ability)


class SavingThrowBonus(CharacterImprovement):
    """Adds a bonus to saving throws for one or more abilities - flat, or a
    formula evaluated at read time (e.g. "equal to your Charisma modifier")."""

    def __init__(self, abilities: list[Ability], bonus: Value):
        self.abilities = abilities
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability in self.abilities:
            if callable(self.bonus):
                character_stat_block.add_derived_saving_throw_bonus(ability, self.bonus)
            else:
                character_stat_block.saving_throws.add_bonus(ability, self.bonus)


class AbilityScoreBonus(CharacterImprovement):
    """Applies (Ability, bonus) pairs, validated to sum to `total`.

    max_per_ability: largest combined increase one ability may get (e.g. 2 for
        an ASI's "+2 to one or +1 to two", or a background's "+2/+1 or
        +1/+1/+1"). None means unchecked.
    max_score: "to a maximum of N" - an increase never raises a score above
        this, but also never lowers a score something else already pushed
        past it. None means uncapped (e.g. magic items with their own rules).
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

    def apply(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            if self.max_score is not None:
                score = character_stat_block.abilities.get_score(ability)
                bonus = min(bonus, max(0, self.max_score - score))
            if bonus:
                character_stat_block.abilities.add_bonus(ability, bonus)


class SetArmorClass(CharacterImprovement):
    """Sets base AC and replaces the ability modifier with a single ability (None = no modifier).

    Ordering: overwrite - the last SetArmorClass/MultiAbilityArmorClass to
    apply wins the base and ability set. Additive ArmorClassBonus values live
    in a separate accumulator and survive regardless of order. Armors apply
    after all features, so worn armor deliberately overrides feature-provided
    AC formulas such as Unarmored Defense."""

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

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(self.base)
        character_stat_block.combat.change_armor_class_ability(self.ability)
        character_stat_block.combat.update_armor_class_ability_modifier_cap(
            self.ability_modifier_cap
        )


class MultiAbilityArmorClass(CharacterImprovement):
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


class ArmorClassBonus(CharacterImprovement):
    """Adds a flat bonus to AC."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.increase_armor_class(self.bonus)


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

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.set_skill_roll_condition(
            self.skill, self.condition, self.reason
        )


class StealthDisadvantage(SkillRollCondition):
    """Imposes disadvantage on Stealth checks."""

    def __init__(self, reason: Optional[str] = None):
        super().__init__(Skill.STEALTH, DiceRollCondition.DISADVANTAGE, reason)


class InitiativeProficiency(CharacterImprovement):
    """Grants proficiency bonus to initiative rolls."""

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_initiative_proficiency()


class InitiativeRollCondition(CharacterImprovement):
    """Applies a roll condition (e.g. advantage) to initiative rolls."""

    def __init__(self, condition: DiceRollCondition):
        self.condition = condition

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_initiative_roll_condition(self.condition)


class InitiativeBonus(CharacterImprovement):
    """Adds a bonus to initiative rolls - flat, or a formula evaluated at read
    time (as distinct from InitiativeProficiency, which adds the full
    proficiency bonus)."""

    def __init__(self, bonus: Value):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        if callable(self.bonus):
            character_stat_block.add_derived_initiative_bonus(self.bonus)
        else:
            character_stat_block.add_initiative_bonus(self.bonus)


class HitPointsPerLevelBonus(CharacterImprovement):
    """Adds `multiplier × character_level` to the hit points bonus."""

    def __init__(self, multiplier: int):
        self.multiplier = multiplier

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.hit_points_bonus += (
            self.multiplier * character_stat_block.character_level
        )


class SkillBonus(CharacterImprovement):
    """Adds a bonus to a specific skill - flat, or a formula evaluated at read
    time (e.g. "equal to your Wisdom modifier"). `source` names where the
    bonus comes from (e.g. the item or feature name) on the character sheet."""

    def __init__(self, skill: Skill, bonus: Value, source: Optional[str] = None):
        self.skill = skill
        self.bonus = bonus
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        if callable(self.bonus):
            character_stat_block.add_derived_skill_bonus(
                self.skill, self.bonus, self.source or "Other"
            )
        elif self.source is not None:
            character_stat_block.skills.add_skill_bonus(
                self.skill, self.bonus, self.source
            )
        else:
            character_stat_block.skills.add_skill_bonus(self.skill, self.bonus)


class SkillToAbilityOverride(CharacterImprovement):
    """Remaps one or more skills to use a different ability score."""

    def __init__(self, skills: list[Skill], ability: Ability):
        self.skills = skills
        self.ability = ability

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            character_stat_block.skills.update_skill_to_ability(skill, self.ability)


class JackOfAllTradesBonus(CharacterImprovement):
    """Adds half proficiency bonus to every skill the character lacks proficiency in.

    Ordering: order-insensitive - both proficiency and the bonus are checked
    at read time, so a proficiency granted later (by any builder, the
    species, or an item) correctly switches the bonus off for that skill."""

    def apply(self, character_stat_block: CharacterStatBlock):
        for skill in Skill:
            character_stat_block.add_derived_skill_bonus(
                skill, self._bonus_for(skill), "Jack of All Trades"
            )

    @staticmethod
    def _bonus_for(skill: Skill) -> Callable[[CharacterStatBlock], int]:
        def bonus(character_stat_block: CharacterStatBlock) -> int:
            if character_stat_block.skills.is_proficient(skill):
                return 0
            return character_stat_block.get_proficiency_bonus() // 2

        return bonus


class SpeedBonus(CharacterImprovement):
    """Increases the character's movement speed by a flat amount."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.speed += self.bonus


class CarryingCapacityBonus(CharacterImprovement):
    """Increases the character's carrying capacity (in item slots).

    The source label identifies where the extra slots come from
    (e.g. "Backpack") so the character sheet can group them.
    """

    def __init__(self, bonus: int, source: str = "Item"):
        self.bonus = bonus
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.carrying_capacity_sources.append((self.source, self.bonus))


class SpellSaveDCBonus(CharacterImprovement):
    """Adds a flat bonus to spell save DC (calculate_difficulty_class[_for_ability])."""

    def __init__(self, bonus: int):
        self.bonus = bonus

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_spell_save_dc_bonus(self.bonus)


class StrengthRequirement(CharacterImprovement):
    """Raises ValueError if the character's Strength score is below the minimum.

    Ordering: eager reader - validated when armors apply, i.e. after all
    features (so feat/background ability bonuses count) but BEFORE items, so
    a Strength bonus granted by an item cannot satisfy an armor requirement."""

    def __init__(self, min_score: int):
        self.min_score = min_score

    def apply(self, character_stat_block: CharacterStatBlock):
        if character_stat_block.get_ability_score(Ability.STRENGTH) < self.min_score:
            raise ValueError(f"Strength score must be at least {self.min_score}.")


# ── Resistances, immunities, senses, and languages ────────────────────────────


class DamageResistance(CharacterImprovement):
    """Grants resistance to a damage type. `source` names where the
    resistance comes from (e.g. the feature or item name) on the character
    sheet."""

    def __init__(self, damage_type: DamageType, source: str):
        self.damage_type = damage_type
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_damage_resistance(self.damage_type, self.source)


class DamageImmunity(CharacterImprovement):
    """Grants immunity to a damage type. `source` names where the immunity
    comes from on the character sheet."""

    def __init__(self, damage_type: DamageType, source: str):
        self.damage_type = damage_type
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_damage_immunity(self.damage_type, self.source)


class ConditionImmunity(CharacterImprovement):
    """Grants immunity to a condition. `source` names where the immunity
    comes from on the character sheet."""

    def __init__(self, condition: Condition, source: str):
        self.condition = condition
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_condition_immunity(self.condition, self.source)


class GrantSense(CharacterImprovement):
    """Grants a special sense (e.g. Darkvision) out to `range_feet`. Granting
    the same sense again from a different source keeps the larger range."""

    def __init__(self, sense: Sense, range_feet: int, source: str):
        self.sense = sense
        self.range_feet = range_feet
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_sense(self.sense, self.range_feet, self.source)


class GrantLanguage(CharacterImprovement):
    """Grants knowledge of a language. `source` names where the language
    comes from (e.g. species or feat name) on the character sheet."""

    def __init__(self, language: Language, source: str):
        self.language = language
        self.source = source

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block.add_language(self.language, self.source)


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

    def apply(self, character_stat_block: CharacterStatBlock) -> None:
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
