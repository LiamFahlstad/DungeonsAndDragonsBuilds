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
from Core.Rules import UNTRAINED_ARMOR_ABILITIES
from Core.SpellcastingRules import CasterType
from Core.Weapons import WeaponProficiency
from Model.AbilityRequirements import AbilityRequirements
from Model.AbilityIncreases import AbilityIncreases
from Model.ArmorClass import ArmorClass, ArmorClassFormula
from Model.CarryingCapacity import CarryingCapacity
from Model.Bonuses import OTHER_SOURCE
from Model.View import CharacterView, Value
from Model.Defenses import Defenses
from Model.EquipmentTraining import EquipmentTraining
from Model.HitPoints import HitPoints
from Model.Initiative import Initiative
from Model.Languages import Languages
from Model.Records.Tools import ToolProficiency
from Model.SavingThrows import SavingThrows
from Model.Senses import Senses
from Model.Skills import Skills
from Model.Speed import Speed
from Model.Spellcasting import Spellcasting
from Model.WeaponBonuses import WeaponBonus, WeaponBonuses
from Model.WornArmor import WornArmor


class Ledger:
    """Everything a Character's features, armor, weapons, items and fighting
    styles record, one part per concern (Model/*.py). Private to
    Character: it fills one once (Character._ledger) and answers every query
    from it. Effects record into it only through the write-only Effects view
    below, and only while the Character fills it.

    Each part owns its own state and the queries on it; see
    Notes/feature-application-model.md. Every part is always present, and
    starts empty: parts hold only what effects record, never a copy of a
    source (base scores, base speed and the spellcasting ability stay on the
    Character, and resolvers read them through the view)."""

    def __init__(self):
        self.ability_increases = AbilityIncreases()
        self.speed = Speed()
        self.spellcasting = Spellcasting()
        self.skills = Skills()
        self.saving_throws = SavingThrows()
        self.carrying_capacity = CarryingCapacity()
        self.armor_class = ArmorClass()
        self.worn_armor = WornArmor()
        self.hit_points = HitPoints()
        self.equipment_training = EquipmentTraining()
        self.languages = Languages()
        self.defenses = Defenses()
        self.senses = Senses()
        self.ability_requirements = AbilityRequirements()
        self.initiative = Initiative()
        self.weapon_bonuses = WeaponBonuses()

    # -- Rules that combine two parts ------------------------------------------
    # Armor training (2024 PHB): "If you wear armor and lack training with it,
    # you have Disadvantage on any D20 Test that involves Strength or
    # Dexterity, and you can't cast spells. If you use a Shield and lack
    # training with it, you don't gain its AC bonus." Worked out on read from
    # the worn armor and the training granted, so it doesn't matter which
    # applied first.

    def is_wearing_untrained_armor(self) -> bool:
        armor_type = self.worn_armor.body_armor_type
        return (
            armor_type is not None
            and armor_type not in self.equipment_training.armor_training
        )

    def has_shield_training(self) -> bool:
        return self.equipment_training.has_shield_training

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        """Disadvantage on D20 Tests with `ability` from untrained armor."""
        return (
            self.is_wearing_untrained_armor() and ability in UNTRAINED_ARMOR_ABILITIES
        )

    def armor_warnings(self) -> list[str]:
        """Legal but bad armor choices the player should know about."""
        warnings = []
        armor_type = self.worn_armor.body_armor_type
        if self.is_wearing_untrained_armor() and armor_type is not None:
            warnings.append(
                f"Wearing {self.worn_armor.body_armor_name or 'armor'} without "
                f"{armor_type.value} armor training: "
                "Disadvantage on every D20 Test that involves Strength or "
                "Dexterity, and you can't cast spells."
            )
        if self.worn_armor.shield_wielded and not self.has_shield_training():
            warnings.append(
                "Wielding a Shield without Shield training: it grants no AC bonus."
            )
        return warnings

    def validate(self, view: CharacterView) -> None:
        """Check every recorded requirement against the complete set of
        effects: expertise needs proficiency, ability minimums (an armor's
        Strength, multiclass prerequisites) need the scores."""
        self.skills.validate()
        self.ability_requirements.validate(view)


class Effects:
    """The write-only record every apply() gets (features, extensions,
    improvements, armor, weapons, items and fighting styles).

    It can only record: proficiencies, bonuses, formulas, grants and
    requirements. It has no way to read anything back - not a score, not a
    proficiency, not even the character's level - because effects apply in no
    particular order, and a value read while they apply could still change.
    Anything that depends on another stat is a formula (a Formula,
    `lambda character: ...`), evaluated against the finished Character when
    it's read. See Notes/feature-application-model.md."""

    __slots__ = ("_ledger",)

    def __init__(self, ledger: Ledger):
        self._ledger = ledger

    # ── Ability scores ──────────────────────────────────────────────────────

    def add_ability_bonus(
        self, ability: Ability, bonus: int, max_score: Optional[int] = None
    ) -> None:
        """+`bonus` to `ability`, to a maximum of `max_score` (None: an
        uncapped equipment bonus). Caps resolve on read - see AbilityIncreases."""
        self._ledger.ability_increases.add(ability, bonus, max_score=max_score)

    def add_ability_requirement(
        self, ability: Ability, min_score: int, reason: str
    ) -> None:
        """Require `ability` at `min_score`+ (checked by Character.validate())."""
        self._ledger.ability_requirements.add_ability_requirement(
            ability, min_score, reason
        )

    # ── Skills ──────────────────────────────────────────────────────────────

    def add_skill_proficiency(self, skill: Skill) -> None:
        self._ledger.skills.add_skill_proficiency(skill)

    def add_skill_expertise(self, skill: Skill) -> None:
        self._ledger.skills.add_skill_expertise(skill)

    def add_skill_bonus(
        self, skill: Skill, bonus: Value, source: str = OTHER_SOURCE
    ) -> None:
        self._ledger.skills.add_skill_bonus(skill, bonus, source)

    def add_skill_ability(self, skill: Skill, ability: Ability) -> None:
        """`skill` may use `ability` instead (the best one is used on read)."""
        self._ledger.skills.update_skill_to_ability(skill, ability)

    def set_skill_roll_condition(
        self, skill: Skill, condition: DiceRollCondition, reason: Optional[str] = None
    ) -> None:
        self._ledger.skills.set_roll_condition(skill, condition, reason)

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
        self._ledger.saving_throws.add_bonus(ability, bonus)

    # ── Armor Class and worn armor ──────────────────────────────────────────

    def add_armor_class_formula(self, formula: ArmorClassFormula) -> None:
        self._ledger.armor_class.add_armor_class_formula(formula)

    def add_armor_class_bonus(self, bonus: Value) -> None:
        self._ledger.armor_class.add_bonus(bonus)

    def set_worn_armor(self, armor_type: ArmorType, name: str) -> None:
        """Records the worn body armor's type and display name."""
        self._ledger.worn_armor.set_body_armor(armor_type, name)

    def add_shield(self, armor_class_bonus: int) -> None:
        """Wield a Shield granting `armor_class_bonus` (with training)."""
        self._ledger.worn_armor.wield_shield()
        self._ledger.armor_class.add_shield_bonus(armor_class_bonus)

    # ── Hit points, speed, carrying capacity ────────────────────────────────

    def add_hit_points_bonus(self, amount: Value) -> None:
        self._ledger.hit_points.add_bonus(amount)

    def add_speed_bonus(self, bonus: Value) -> None:
        self._ledger.speed.add_bonus(bonus)

    def add_carrying_capacity_bonus(self, source: str, bonus: int) -> None:
        self._ledger.carrying_capacity.add_bonus(source, bonus)

    # ── Initiative ──────────────────────────────────────────────────────────

    def add_initiative_proficiency(self) -> None:
        self._ledger.initiative.add_proficiency()

    def add_initiative_roll_condition(self, condition: DiceRollCondition) -> None:
        self._ledger.initiative.add_roll_condition(condition)

    def add_initiative_bonus(self, bonus: Value) -> None:
        self._ledger.initiative.add_bonus(bonus)

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

    def add_damage_resistance(self, damage_type: DamageType, source: str) -> None:
        self._ledger.defenses.add_damage_resistance(damage_type, source)

    def add_damage_immunity(self, damage_type: DamageType, source: str) -> None:
        self._ledger.defenses.add_damage_immunity(damage_type, source)

    def add_condition_immunity(self, condition: Condition, source: str) -> None:
        self._ledger.defenses.add_condition_immunity(condition, source)

    def add_sense(self, sense: Sense, range_feet: int, source: str) -> None:
        """Grant a sense. The same sense from several sources keeps the best range."""
        self._ledger.senses.add_sense(sense, range_feet, source)

    def add_sense_or_extension(
        self, sense: Sense, range_feet: int, source: str
    ) -> None:
        """Grant a sense out to `range_feet` - or, if the character already has
        it, increase its range by `range_feet` (e.g. Umbral Sight)."""
        self._ledger.senses.add_sense_or_extension(sense, range_feet, source)

    def add_language(self, language: Language, source: str) -> None:
        self._ledger.languages.add(language, source)
