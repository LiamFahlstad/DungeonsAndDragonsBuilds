from enum import Enum
from typing import Any, Optional

import Core.Definitions as Definitions
from Core.Definitions import Ability, CharacterClass, Skill
from Core.SpellcastingRules import CasterType
from StatBlocks.AbilityRequirements import AbilityRequirements
from StatBlocks.AbilityScores import AbilityScores
from StatBlocks.ArmorClass import ArmorClass
from StatBlocks.Bonuses import DerivedBonus
from StatBlocks.CarryingCapacity import CarryingCapacity
from StatBlocks.ClassLevels import ClassLevels
from StatBlocks.Defenses import Defenses
from StatBlocks.EquipmentTraining import EquipmentTraining
from StatBlocks.HitPoints import HitPoints
from StatBlocks.Initiative import Initiative
from StatBlocks.Languages import Languages
from StatBlocks.SavingThrows import SavingThrows
from StatBlocks.Senses import Senses
from StatBlocks.Skills import Skills
from StatBlocks.Speed import Speed
from StatBlocks.Spellcasting import Spellcasting
from StatBlocks.WornArmor import WornArmor

# DerivedBonus is imported above from StatBlocks/Bonuses.py (not defined
# here) so every part can use the type without importing this module, which
# would be circular since this module imports the parts.


class CharacterStatBlock:
    def __init__(
        self,
        class_levels: ClassLevels,
        abilities: AbilityScores,
        speed: int,
        spellcasting: Optional[Spellcasting] = None,
    ):
        # Shared with the CharacterSheetData this character was built from -
        # not a copy - so levels, history and subclass are one source of
        # truth (see StatBlocks/ClassLevels.py). Name, gold, size and the
        # subclass display string stay on CharacterSheetData only; readers
        # that need them (the sheet writer) already have that object.
        self.class_levels = class_levels
        self.abilities = abilities
        self.speed = Speed(speed)
        self.spellcasting = spellcasting if spellcasting is not None else Spellcasting()
        # Parts (StatBlocks/*.py): each owns its own state and the queries on
        # it (see Notes/feature-application-model.md). Always present, even
        # when empty, so nothing here needs an "if part is not None" check.
        # Skills and saving throws hold no state of their own here - every
        # proficiency, expertise and bonus arrives as a feature effect (e.g.
        # ClassProficiencies, ClassSkillChoice, FreeBackgroundSkillProficiency).
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

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a shield alone doesn't count)."""
        return self.worn_armor.is_wearing_armor

    @property
    def character_level(self) -> int:
        return self.class_levels.character_level

    @property
    def level_per_class(self) -> dict[CharacterClass, int]:
        return self.class_levels.level_per_class

    @property
    def base_class(self) -> CharacterClass:
        # Guaranteed set by the time a CharacterStatBlock exists - the
        # CharacterSheetData it was built from validates this before it
        # builds anything (CharacterSheetData.validate()).
        assert self.class_levels.base_class is not None
        return self.class_levels.base_class

    @property
    def spell_casting_ability(self) -> Optional[Ability]:
        return self.spellcasting.ability

    @property
    def spell_slots(self) -> Optional[dict[int, int]]:
        return self.spellcasting.spell_slots(self.class_levels)

    @property
    def pact_magic_slots(self) -> dict[int, int]:
        return self.spellcasting.pact_magic_slots(self.class_levels)

    def register_caster(
        self, character_class: CharacterClass, caster_type: CasterType
    ) -> None:
        self.spellcasting.register_caster(character_class, caster_type)

    @property
    def initiative_roll_condition(self) -> Definitions.DiceRollCondition:
        # Initiative is a Dexterity check, so untrained armor imposes
        # Disadvantage. Advantage and Disadvantage cancel out.
        extra = (
            {Definitions.DiceRollCondition.DISADVANTAGE}
            if self.has_untrained_armor_disadvantage(Ability.DEXTERITY)
            else set()
        )
        return self.initiative.roll_condition(extra)

    # ── Armor training (2024 PHB) ────────────────────────────────────────────
    # "If you wear armor and lack training with it, you have Disadvantage on
    # any D20 Test that involves Strength or Dexterity, and you can't cast
    # spells. If you use a Shield and lack training with it, you don't gain
    # its AC bonus." Worked out on read from the worn armor and the training
    # granted, so it doesn't matter which applied first.

    UNTRAINED_ARMOR_REASON = "Untrained armor"

    @property
    def is_wearing_untrained_armor(self) -> bool:
        return (
            self.worn_armor.body_armor_type is not None
            and self.worn_armor.body_armor_type
            not in self.equipment_training.armor_training
        )

    @property
    def has_shield_training(self) -> bool:
        return self.equipment_training.has_shield_training

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        """Disadvantage on D20 Tests with `ability` from untrained armor."""
        return self.is_wearing_untrained_armor and ability in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        )

    def add_shield(self, armor_class_bonus: int) -> None:
        """Wield a Shield granting `armor_class_bonus` (with training)."""
        self.worn_armor.wield_shield()
        self.armor_class.add_shield_bonus(armor_class_bonus)

    def set_worn_armor(self, armor_type: Definitions.ArmorType, name: str) -> None:
        """Records the worn body armor's type and display name."""
        self.worn_armor.set_body_armor(armor_type, name)

    @property
    def warnings(self) -> list[str]:
        """Legal but bad choices the player should know about."""
        warnings = []
        if self.is_wearing_untrained_armor:
            assert self.worn_armor.body_armor_type is not None
            warnings.append(
                f"Wearing {self.worn_armor.body_armor_name or 'armor'} without "
                f"{self.worn_armor.body_armor_type.value} armor training: "
                "Disadvantage on every D20 Test that involves Strength or "
                "Dexterity, and you can't cast spells."
            )
        if self.worn_armor.shield_wielded and not self.has_shield_training:
            warnings.append(
                "Wielding a Shield without Shield training: it grants no AC bonus."
            )
        return warnings

    def calculate_initiative(self) -> int:
        modifier = self.abilities.get_modifier(Ability.DEXTERITY)
        return modifier + self.initiative.total(self.get_proficiency_bonus(), self)

    def calculate_speed(self) -> int:
        return self.speed.total(self)

    def get_carrying_capacity_sources(self) -> list[tuple[str, int]]:
        """Returns all carrying capacity sources, including the dynamic 'Person' base."""
        return self.carrying_capacity.sources(
            self.abilities.get_modifier(Ability.STRENGTH)
        )

    def get_carrying_capacity(self) -> int:
        """Returns the total carrying capacity in item slots (base 3 + STR mod + bonuses)."""
        return self.carrying_capacity.total(
            self.abilities.get_modifier(Ability.STRENGTH)
        )

    def _require_spell_casting_ability(self) -> Ability:
        return self.spellcasting.require_ability()

    def add_initiative_proficiency(self):
        self.initiative.add_proficiency()

    def add_initiative_roll_condition(self, condition: Definitions.DiceRollCondition):
        self.initiative.add_roll_condition(condition)

    def add_initiative_bonus(self, bonus: int) -> None:
        self.initiative.add_bonus(bonus)

    def add_derived_initiative_bonus(self, bonus: DerivedBonus) -> None:
        self.initiative.add_derived_bonus(bonus)

    def add_derived_armor_class_bonus(self, bonus: DerivedBonus) -> None:
        self.armor_class.add_derived_bonus(bonus)

    def add_derived_speed_bonus(self, bonus: DerivedBonus) -> None:
        self.speed.add_derived_bonus(bonus)

    def add_ability_requirement(
        self, ability: Ability, min_score: int, reason: str
    ) -> None:
        self.ability_requirements.add_ability_requirement(ability, min_score, reason)

    def validate(self) -> None:
        """Check every requirement against the complete set of effects. Run
        once everything has applied - a requirement may be met by an effect
        granted before or after the one that imposes it."""
        self.skills.validate()
        self.ability_requirements.validate(self.abilities, self.class_levels)

    def add_derived_saving_throw_bonus(
        self, ability: Ability, bonus: DerivedBonus
    ) -> None:
        self.saving_throws.add_derived_bonus(ability, bonus)

    def add_derived_skill_bonus(
        self, skill: Skill, bonus: DerivedBonus, source: str = "Other"
    ) -> None:
        self.skills.add_derived_bonus(skill, bonus, source)

    def add_spell_save_dc_bonus(self, bonus: int) -> None:
        self.spellcasting.add_spell_save_dc_bonus(bonus)

    def get_class_level(self, character_class: CharacterClass) -> int:
        return self.class_levels.get_class_level(character_class)

    def get_class_level_segments(self) -> list[tuple[int, int, CharacterClass]]:
        """Contiguous (start_level, end_level, class) ranges describing which
        class was being leveled at each total character level, in
        chronological order. A class taken again after a dip into another
        class (e.g. Artificer 1-7, Wizard 8, Artificer 9-15) appears as two
        separate segments rather than being merged into one."""
        return self.class_levels.get_class_level_segments()

    def get_proficiency_bonus(self) -> int:
        return 2 + (self.character_level - 1) // 4

    def get_ability_score(self, ability: Ability) -> int:
        return self.abilities.get_score(ability)

    def get_ability_modifier(self, ability: Ability) -> int:
        return self.abilities.get_modifier(ability)

    def get_strength_modifier(self) -> int:
        return self.get_ability_modifier(Ability.STRENGTH)

    def get_dexterity_modifier(self) -> int:
        return self.get_ability_modifier(Ability.DEXTERITY)

    def get_constitution_modifier(self) -> int:
        return self.get_ability_modifier(Ability.CONSTITUTION)

    def get_intelligence_modifier(self) -> int:
        return self.get_ability_modifier(Ability.INTELLIGENCE)

    def get_wisdom_modifier(self) -> int:
        return self.get_ability_modifier(Ability.WISDOM)

    def get_charisma_modifier(self) -> int:
        return self.get_ability_modifier(Ability.CHARISMA)

    def is_proficient_in_skill(self, skill: Skill) -> bool:
        return self.skills.is_proficient(skill)

    def has_expertise_in_skill(self, skill: Skill) -> bool:
        return self.skills.has_expertise(skill)

    def get_skill_ability(self, skill: Skill) -> Ability:
        # Several overrides for one skill: use the best (ties keep the first
        # in Ability order, so grant order never decides).
        order = list(Ability)
        return max(
            sorted(self.skills.get_skill_abilities(skill), key=order.index),
            key=self.get_ability_modifier,
        )

    def get_skill_modifier(self, skill: Skill) -> int:
        ability_modifier = self.get_ability_modifier(self.get_skill_ability(skill))
        if self.has_expertise_in_skill(skill):
            proficiency_bonus = self.get_proficiency_bonus() * 2
        elif self.is_proficient_in_skill(skill):
            proficiency_bonus = self.get_proficiency_bonus()
        else:
            proficiency_bonus = 0
        return ability_modifier + proficiency_bonus + self.get_skill_bonus(skill)

    def get_skill_bonus(self, skill: Skill) -> int:
        return self.skills.get_total_bonus(skill, self)

    def get_skill_bonus_sources(self, skill: Skill) -> list[tuple[int, str]]:
        return self.skills.get_all_bonus_sources(skill, self)

    def is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_proficient(ability)

    def add_proficiency_in_saving_throw(self, ability: Ability) -> None:
        self.saving_throws.add_proficiency(ability)

    def has_advantage_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_advantaged(ability)

    def get_saving_throw_roll_condition(
        self, ability: Ability
    ) -> Definitions.DiceRollCondition:
        conditions = set()
        if self.saving_throws.is_advantaged(ability):
            conditions.add(Definitions.DiceRollCondition.ADVANTAGE)
        if self.has_untrained_armor_disadvantage(ability):
            conditions.add(Definitions.DiceRollCondition.DISADVANTAGE)
        return Definitions.combine_roll_conditions(conditions)

    def add_advantage_in_saving_throw(self, ability: Ability) -> None:
        self.saving_throws.add_advantage(ability)

    def _skill_roll_condition_sources(
        self, skill: Skill
    ) -> dict[Definitions.DiceRollCondition, list[str]]:
        sources = self.skills.get_roll_condition_sources(skill)
        if self.has_untrained_armor_disadvantage(self.get_skill_ability(skill)):
            sources.setdefault(Definitions.DiceRollCondition.DISADVANTAGE, []).append(
                self.UNTRAINED_ARMOR_REASON
            )
        return sources

    def get_skill_roll_condition(self, skill: Skill) -> Definitions.DiceRollCondition:
        return Definitions.combine_roll_conditions(
            self._skill_roll_condition_sources(skill)
        )

    def set_skill_roll_condition(
        self,
        skill: Skill,
        condition: Definitions.DiceRollCondition,
        reason: Optional[str] = None,
    ):
        self.skills.set_roll_condition(skill, condition, reason)

    def get_skill_roll_condition_reasons(self, skill: Skill) -> list[str]:
        condition = self.get_skill_roll_condition(skill)
        return self._skill_roll_condition_sources(skill).get(condition, [])

    def get_saving_throw_modifier(self, ability: Ability) -> int:
        base_modifier = self.get_ability_modifier(ability)
        proficiency_bonus = (
            self.get_proficiency_bonus()
            if self.is_proficient_in_saving_throw(ability)
            else 0
        )
        return (
            base_modifier
            + proficiency_bonus
            + self.saving_throws.get_total_bonus(ability, self)
        )

    def calculate_hit_points(self) -> int:
        return self.hit_points.calculate(
            self.class_levels, self.get_constitution_modifier(), self
        )

    def calculate_armor_class(self, ignore_shield: bool = False) -> int:
        """The best applicable AC formula plus every AC bonus. ignore_shield:
        the AC with the Shield set aside (its bonus gone, and formulas it
        disables - Monk's Unarmored Defense - available again)."""
        is_wielding_shield = self.worn_armor.shield_wielded and not ignore_shield
        return self.armor_class.calculate(
            self.abilities, self, is_wielding_shield, self.has_shield_training
        )

    def get_spell_casting_ability(self) -> Ability:
        return self._require_spell_casting_ability()

    def calculate_difficulty_class(self) -> int:
        return self.calculate_difficulty_class_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int:
        return self.spellcasting.difficulty_class(
            self.get_proficiency_bonus(), self.get_ability_modifier(ability)
        )

    def calculate_attack_bonus(self) -> int:
        return self.calculate_attack_bonus_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        return self.spellcasting.attack_bonus(
            self.get_proficiency_bonus(), self.get_ability_modifier(ability)
        )

    def get_spell_slots(self) -> dict[int, int]:
        spell_slots = self.spell_slots
        if spell_slots is None:
            raise ValueError("Character does not have spell slots.")
        return spell_slots

    def add_damage_resistance(
        self, damage_type: Definitions.DamageType, source: str
    ) -> None:
        self.defenses.add_damage_resistance(damage_type, source)

    def add_damage_immunity(
        self, damage_type: Definitions.DamageType, source: str
    ) -> None:
        self.defenses.add_damage_immunity(damage_type, source)

    def is_resistant_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return self.defenses.is_resistant_to_damage(damage_type)

    def is_immune_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return self.defenses.is_immune_to_damage(damage_type)

    def get_damage_resistance_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self.defenses.get_damage_resistance_sources(damage_type)

    def get_damage_immunity_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self.defenses.get_damage_immunity_sources(damage_type)

    def add_condition_immunity(
        self, condition: Definitions.Condition, source: str
    ) -> None:
        self.defenses.add_condition_immunity(condition, source)

    def is_immune_to_condition(self, condition: Definitions.Condition) -> bool:
        return self.defenses.is_immune_to_condition(condition)

    def get_condition_immunity_sources(
        self, condition: Definitions.Condition
    ) -> list[str]:
        return self.defenses.get_condition_immunity_sources(condition)

    def add_sense(self, sense: Definitions.Sense, range_feet: int, source: str) -> None:
        """Grant a sense. The same sense from several sources keeps the best range."""
        self.senses.add_sense(sense, range_feet, source)

    def add_sense_or_extension(
        self, sense: Definitions.Sense, range_feet: int, source: str
    ) -> None:
        """Grant a sense out to `range_feet` - or, if the character already has
        it, increase its range by `range_feet` (e.g. Umbral Sight)."""
        self.senses.add_sense_or_extension(sense, range_feet, source)

    def get_sense_range(self, sense: Definitions.Sense) -> int:
        return self.senses.get_sense_range(sense)

    def get_sense_sources(self, sense: Definitions.Sense) -> list[tuple[int, str]]:
        return self.senses.get_sense_sources(sense)

    def add_weapon_proficiency(self, weapon_proficiency: Enum) -> None:
        self.equipment_training.add_weapon_proficiency(weapon_proficiency)

    def add_armor_training(self, armor_type: Definitions.ArmorType) -> None:
        self.equipment_training.add_armor_training(armor_type)

    def add_tool_proficiency(self, tool_proficiency: Any) -> None:
        """Proficiency with a tool (a ToolProficiency). The same tool from
        several sources is listed once."""
        self.equipment_training.add_tool_proficiency(tool_proficiency)

    def add_language(self, language: Definitions.Language, source: str) -> None:
        self.languages.add(language, source)

    def knows_language(self, language: Definitions.Language) -> bool:
        return self.languages.knows(language)

    def get_language_sources(self, language: Definitions.Language) -> list[str]:
        return self.languages.sources(language)
