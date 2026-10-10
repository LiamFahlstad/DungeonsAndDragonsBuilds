"""LedgerWriter: the write-only door into a Ledger that every apply() gets."""

from typing import Optional

from Core.Definitions import (
    Ability,
    ArmorType,
    CharacterClass,
    Condition,
    DamageType,
    DiceRollCondition,
    Language,
    Sense,
    Skill,
)
from Core.SpellcastingRules import CasterType
from Core.Weapons import WeaponProficiency
from Model.Ledger.ArmorClass import ArmorClassFormula
from Model.Ledger.Ledger import Ledger
from Model.Ledger.WeaponBonuses import WeaponBonus
from Model.Records.Tools import ToolProficiency
from Model.View import Value


class LedgerWriter:
    """The write-only record every apply() gets (features, extensions,
    improvements, armor, weapons, items and fighting styles).

    It can only record: proficiencies, bonuses, formulas, grants and
    requirements. It has no way to read anything back - not a score, not a
    proficiency, not even the character's level - because effects apply in no
    particular order, and a value read while they apply could still change.
    Anything that depends on another stat is a formula (a Formula,
    `lambda character: ...`), evaluated against the finished Character when
    it's read. See Notes/feature-application-model.md.

    Each effect gets its own writer, labeled with that effect's name: every
    bonus, resistance, sense, language, roll condition and requirement it
    records is listed under that name ("Darkvision", "Ring of Investigation"),
    so apply() never passes a label itself. Weapon bonuses are the exception:
    a WeaponBonus carries its own descriptive label."""

    __slots__ = ("_ledger", "_source")

    def __init__(self, ledger: Ledger, source: str):
        self._ledger = ledger
        self._source = source

    # ── Ability scores ──────────────────────────────────────────────────────

    def add_ability_bonus(
        self, ability: Ability, bonus: int, max_score: Optional[int] = None
    ) -> None:
        """+`bonus` to `ability`, to a maximum of `max_score` (None: an
        uncapped equipment bonus). Caps resolve on read - see AbilityIncreases."""
        self._ledger.ability_increases.add(ability, bonus, max_score=max_score)

    def add_ability_requirement(self, ability: Ability, min_score: int) -> None:
        """Require `ability` at `min_score`+ (checked by Character.validate())."""
        self._ledger.ability_requirements.add_ability_requirement(
            ability, min_score, self._source
        )

    # ── Skills ──────────────────────────────────────────────────────────────

    def add_skill_proficiency(self, skill: Skill) -> None:
        self._ledger.skills.add_skill_proficiency(skill)

    def add_skill_expertise(self, skill: Skill) -> None:
        self._ledger.skills.add_skill_expertise(skill)

    def add_skill_bonus(self, skill: Skill, bonus: Value) -> None:
        self._ledger.skills.add_skill_bonus(skill, bonus, self._source)

    def add_skill_ability(self, skill: Skill, ability: Ability) -> None:
        """`skill` may use `ability` instead (the best one is used on read)."""
        self._ledger.skills.update_skill_to_ability(skill, ability)

    def set_skill_roll_condition(
        self, skill: Skill, condition: DiceRollCondition
    ) -> None:
        self._ledger.skills.set_roll_condition(skill, condition, self._source)

    # ── Saving throws ───────────────────────────────────────────────────────

    def add_saving_throw_proficiency(self, ability: Ability) -> None:
        self._ledger.saving_throws.add_proficiency(ability)

    def add_saving_throw_proficiency_or_alternative(
        self, ability: Ability, alternatives: list[Ability]
    ) -> None:
        self._ledger.saving_throws.add_proficiency_or_alternative(ability, alternatives)

    def add_saving_throw_advantage(self, ability: Ability) -> None:
        self._ledger.saving_throws.add_advantage(ability)

    def add_saving_throw_bonus(self, ability: Ability, bonus: Value) -> None:
        self._ledger.saving_throws.add_bonus(ability, bonus, self._source)

    # ── Armor Class and worn armor ──────────────────────────────────────────

    def add_armor_class_formula(self, formula: ArmorClassFormula) -> None:
        self._ledger.armor_class.add_armor_class_formula(formula)

    def add_armor_class_bonus(self, bonus: Value) -> None:
        self._ledger.armor_class.add_bonus(bonus, self._source)

    def set_worn_armor(self, armor_type: ArmorType, name: str) -> None:
        """Records the worn body armor's type and display name."""
        self._ledger.worn_armor.set_body_armor(armor_type, name)

    def add_shield(self, armor_class_bonus: int) -> None:
        """Wield a Shield granting `armor_class_bonus` (with training)."""
        self._ledger.worn_armor.wield_shield()
        self._ledger.armor_class.add_shield_bonus(armor_class_bonus)

    # ── Hit points, speed, carrying capacity ────────────────────────────────

    def add_hit_points_bonus(self, amount: Value) -> None:
        self._ledger.hit_points.add_bonus(amount, self._source)

    def add_speed_bonus(self, bonus: Value) -> None:
        self._ledger.speed.add_bonus(bonus, self._source)

    def add_carrying_capacity_bonus(self, bonus: int) -> None:
        self._ledger.carrying_capacity.add_bonus(bonus, self._source)

    # ── Initiative ──────────────────────────────────────────────────────────

    def add_initiative_proficiency(self) -> None:
        self._ledger.initiative.add_proficiency()

    def add_initiative_roll_condition(self, condition: DiceRollCondition) -> None:
        self._ledger.initiative.add_roll_condition(condition)

    def add_initiative_bonus(self, bonus: Value) -> None:
        self._ledger.initiative.add_bonus(bonus, self._source)

    # ── Spellcasting ────────────────────────────────────────────────────────

    def register_caster(
        self, character_class: CharacterClass, caster_type: CasterType
    ) -> None:
        """Spell slots are worked out on read from every registered caster."""
        self._ledger.spellcasting.register_caster(character_class, caster_type)

    def add_spell_save_dc_bonus(self, bonus: int) -> None:
        self._ledger.spellcasting.add_spell_save_dc_bonus(bonus)

    # ── Weapon, armor and tool training ─────────────────────────────────────

    def add_weapon_proficiency(self, weapon_proficiency: WeaponProficiency) -> None:
        self._ledger.equipment_training.add_weapon_proficiency(weapon_proficiency)

    def add_armor_training(self, armor_type: ArmorType) -> None:
        self._ledger.equipment_training.add_armor_training(armor_type)

    def add_tool_proficiency(self, tool_proficiency: ToolProficiency) -> None:
        """Proficiency with a tool. The same tool from
        several sources is listed once."""
        self._ledger.equipment_training.add_tool_proficiency(tool_proficiency)

    # ── Weapon attack and damage bonuses ────────────────────────────────────

    def add_weapon_attack_bonus(self, bonus: WeaponBonus) -> None:
        self._ledger.weapon_bonuses.add_attack_bonus(bonus)

    def add_weapon_damage_bonus(self, bonus: WeaponBonus) -> None:
        self._ledger.weapon_bonuses.add_damage_bonus(bonus)

    # ── Defenses, senses, languages ─────────────────────────────────────────

    def add_damage_resistance(self, damage_type: DamageType) -> None:
        self._ledger.defenses.add_damage_resistance(damage_type, self._source)

    def add_damage_immunity(self, damage_type: DamageType) -> None:
        self._ledger.defenses.add_damage_immunity(damage_type, self._source)

    def add_condition_immunity(self, condition: Condition) -> None:
        self._ledger.defenses.add_condition_immunity(condition, self._source)

    def add_sense(self, sense: Sense, range_feet: int) -> None:
        """Grant a sense. The same sense from several sources keeps the best range."""
        self._ledger.senses.add_sense(sense, range_feet, self._source)

    def add_sense_or_extension(self, sense: Sense, range_feet: int) -> None:
        """Grant a sense out to `range_feet` - or, if the character already has
        it, increase its range by `range_feet` (e.g. Umbral Sight)."""
        self._ledger.senses.add_sense_or_extension(sense, range_feet, self._source)

    def add_language(self, language: Language) -> None:
        self._ledger.languages.add(language, self._source)
