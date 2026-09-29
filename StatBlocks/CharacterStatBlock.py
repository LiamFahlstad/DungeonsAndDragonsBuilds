from enum import Enum
from typing import Any, Callable, Optional

import Core.Definitions as Definitions
from Core.Definitions import Ability, CharacterClass, Skill
from Core.SpellcastingRules import CasterType, calculate_spell_slots
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CombatStatBlock import ArmorClassFormula, CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock

# A bonus whose value depends on other stats (e.g. "equal to your Wisdom
# modifier"). Stored as a formula and evaluated at read time, so it always
# reflects the final stats no matter which feature, armor or item applied
# first - snapshotting such a value inside apply() would freeze it at
# whatever the stat was when that feature happened to run.
DerivedBonus = Callable[["CharacterStatBlock"], int]


class CharacterStatBlock:
    def __init__(
        self,
        name: str,
        character_subclass: str,
        base_class: CharacterClass,
        level_per_class: dict[CharacterClass, int],
        abilities: AbilitiesStatBlock,
        skills: SkillsStatBlock,
        combat: CombatStatBlock,
        saving_throws: SavingThrowsStatBlock,
        spell_casting_ability: Optional[Ability] = None,
        spell_slots: Optional[dict[int, int]] = None,
        class_by_character_level: Optional[dict[int, CharacterClass]] = None,
        starting_gold: Optional[float] = None,
        current_gold: Optional[float] = None,
    ):
        self.name = name
        self.character_subclass = character_subclass
        self.base_class = base_class
        self.level_per_class = level_per_class
        self.class_by_character_level = class_by_character_level or {}
        self.abilities = abilities
        self.skills = skills
        self.combat = combat
        self.saving_throws = saving_throws
        self.spell_casting_ability = spell_casting_ability
        # Slots for a character with no Spell Slots feature (e.g. companions);
        # otherwise worked out from the registered casters - see spell_slots.
        self._fixed_spell_slots = spell_slots
        self._casters: dict[CharacterClass, CasterType] = {}
        self.starting_gold = starting_gold
        self.current_gold = current_gold
        # Set by worn armor as it applies. Armor-conditional effects (Defense
        # fighting style, Unarmored Movement, Fast Movement, ...) read these
        # inside a formula, i.e. once everything has applied.
        self.worn_armor_type: Optional[Definitions.ArmorType] = None
        self.is_wielding_shield = False
        self.initiative_proficiency = False
        self._initiative_roll_conditions: set[Definitions.DiceRollCondition] = set()
        self.initiative_bonus = 0
        # Formula-valued bonuses (see DerivedBonus), resolved on every read.
        self._derived_initiative_bonuses: list[DerivedBonus] = []
        self._derived_armor_class_bonuses: list[DerivedBonus] = []
        self._derived_speed_bonuses: list[DerivedBonus] = []
        self._derived_saving_throw_bonuses: dict[Ability, list[DerivedBonus]] = {}
        self._derived_skill_bonuses: dict[Skill, list[tuple[DerivedBonus, str]]] = {}
        self.spell_save_dc_bonus = 0
        # (source, slots) pairs; bonus sources only (Person is computed dynamically)
        self.carrying_capacity_sources: list[tuple[str, int]] = []
        # (damage_type -> [source, ...]) grants of resistance/immunity to damage
        self.damage_resistances: dict[Definitions.DamageType, list[str]] = {}
        self.damage_immunities: dict[Definitions.DamageType, list[str]] = {}
        # (condition -> [source, ...]) grants of immunity to a condition
        self.condition_immunities: dict[Definitions.Condition, list[str]] = {}
        # Every (range, source) pair granted per sense; the range itself is
        # worked out on read - see senses.
        self.sense_sources: dict[Definitions.Sense, list[tuple[int, str]]] = {}
        # "...or if you already have it, its range increases by N" grants.
        self._sense_extensions: dict[Definitions.Sense, list[tuple[int, str]]] = {}
        # (language -> [source, ...]) grants of a known language
        self.languages: dict[Definitions.Language, list[str]] = {}
        # (ability, minimum score, reason) - checked by validate() once
        # everything has applied, against the character's own score.
        self._ability_requirements: list[tuple[Ability, int, str]] = []
        # Weapon, armor and tool proficiencies from any source (class,
        # subclass, feat, item). A weapon works out whether its wielder is
        # proficient on read, against these (AbstractWeapon.is_proficient).
        # Typed loosely: the WeaponProficiency enum and ToolProficiency live in
        # CharacterContent, which imports this module.
        self.weapon_proficiencies: set[Enum] = set()
        self.armor_training: set[Definitions.ArmorType] = set()
        self.tool_proficiencies: list[Any] = []

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a shield alone doesn't count)."""
        return self.worn_armor_type is not None

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

    @property
    def speed(self) -> int:
        derived = sum(bonus(self) for bonus in self._derived_speed_bonuses)
        return self.combat.speed + derived

    @property
    def spell_slots(self) -> Optional[dict[int, int]]:
        if not self._casters:
            return self._fixed_spell_slots
        return calculate_spell_slots(self._casters, self.level_per_class)[0]

    @property
    def pact_magic_slots(self) -> dict[int, int]:
        return calculate_spell_slots(self._casters, self.level_per_class)[1]

    def register_caster(
        self, character_class: CharacterClass, caster_type: CasterType
    ) -> None:
        self._casters[character_class] = caster_type

    @property
    def initiative_roll_condition(self) -> Definitions.DiceRollCondition:
        # Advantage and Disadvantage from any number of sources cancel out.
        conditions = self._initiative_roll_conditions
        advantage = Definitions.DiceRollCondition.ADVANTAGE in conditions
        disadvantage = Definitions.DiceRollCondition.DISADVANTAGE in conditions
        if advantage == disadvantage:
            return Definitions.DiceRollCondition.NEUTRAL
        if advantage:
            return Definitions.DiceRollCondition.ADVANTAGE
        return Definitions.DiceRollCondition.DISADVANTAGE

    @property
    def initiative(self) -> int:
        modifier = self.abilities.get_modifier(Ability.DEXTERITY)
        if self.initiative_proficiency:
            modifier += self.get_proficiency_bonus()
        derived = sum(bonus(self) for bonus in self._derived_initiative_bonuses)
        return modifier + self.initiative_bonus + derived

    def get_carrying_capacity_sources(self) -> list[tuple[str, int]]:
        """Returns all carrying capacity sources, including the dynamic 'Person' base."""
        person_slots = 3 + self.abilities.get_modifier(Ability.STRENGTH)
        return [("Person", person_slots)] + self.carrying_capacity_sources

    def get_carrying_capacity(self) -> int:
        """Returns the total carrying capacity in item slots (base 3 + STR mod + bonuses)."""
        return sum(slots for _, slots in self.get_carrying_capacity_sources())

    def _require_spell_casting_ability(self) -> Ability:
        if self.spell_casting_ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        return self.spell_casting_ability

    def add_initiative_proficiency(self):
        self.initiative_proficiency = True

    def add_initiative_roll_condition(self, condition: Definitions.DiceRollCondition):
        self._initiative_roll_conditions.add(condition)

    def add_initiative_bonus(self, bonus: int) -> None:
        self.initiative_bonus += bonus

    def add_derived_initiative_bonus(self, bonus: DerivedBonus) -> None:
        self._derived_initiative_bonuses.append(bonus)

    def add_derived_armor_class_bonus(self, bonus: DerivedBonus) -> None:
        self._derived_armor_class_bonuses.append(bonus)

    def add_derived_speed_bonus(self, bonus: DerivedBonus) -> None:
        self._derived_speed_bonuses.append(bonus)

    def add_ability_requirement(
        self, ability: Ability, min_score: int, reason: str
    ) -> None:
        self._ability_requirements.append((ability, min_score, reason))

    def validate(self) -> None:
        """Check every requirement against the complete set of effects. Run
        once everything has applied - a requirement may be met by an effect
        granted before or after the one that imposes it."""
        self.skills.validate()
        for ability, min_score, reason in self._ability_requirements:
            if self.abilities.get_own_score(ability) < min_score:
                raise ValueError(
                    f"{ability.value} score must be at least {min_score} ({reason})."
                )

    def add_derived_saving_throw_bonus(
        self, ability: Ability, bonus: DerivedBonus
    ) -> None:
        self._derived_saving_throw_bonuses.setdefault(ability, []).append(bonus)

    def add_derived_skill_bonus(
        self, skill: Skill, bonus: DerivedBonus, source: str = "Other"
    ) -> None:
        self._derived_skill_bonuses.setdefault(skill, []).append((bonus, source))

    def add_spell_save_dc_bonus(self, bonus: int) -> None:
        self.spell_save_dc_bonus += bonus

    def get_class_level(self, character_class: CharacterClass) -> int:
        return self.level_per_class.get(character_class, 0)

    def get_class_level_segments(self) -> list[tuple[int, int, CharacterClass]]:
        """Contiguous (start_level, end_level, class) ranges describing which
        class was being leveled at each total character level, in
        chronological order. A class taken again after a dip into another
        class (e.g. Artificer 1-7, Wizard 8, Artificer 9-15) appears as two
        separate segments rather than being merged into one."""
        segments: list[tuple[int, int, CharacterClass]] = []
        current_class = None
        start = None
        for level in range(1, self.character_level + 1):
            character_class = self.class_by_character_level.get(level)
            if character_class != current_class:
                if current_class is not None:
                    assert start is not None
                    segments.append((start, level - 1, current_class))
                current_class = character_class
                start = level
        if current_class is not None:
            assert start is not None
            segments.append((start, self.character_level, current_class))
        return segments

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
        return self.skills.bonuses.get(skill, 0) + sum(
            value for value, _source in self._derived_skill_bonus_sources(skill)
        )

    def get_skill_bonus_sources(self, skill: Skill) -> list[tuple[int, str]]:
        return self.skills.get_bonus_sources(skill) + self._derived_skill_bonus_sources(
            skill
        )

    def _derived_skill_bonus_sources(self, skill: Skill) -> list[tuple[int, str]]:
        # A derived bonus that currently evaluates to 0 (e.g. Jack of All
        # Trades on a skill you're proficient in) isn't a source worth listing.
        resolved = [
            (bonus(self), source)
            for bonus, source in self._derived_skill_bonuses.get(skill, [])
        ]
        return [(value, source) for value, source in resolved if value != 0]

    def is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_proficient(ability)

    def add_proficiency_in_saving_throw(self, ability: Ability) -> None:
        self.saving_throws.add_proficiency(ability)

    def has_advantage_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_advantaged(ability)

    def add_advantage_in_saving_throw(self, ability: Ability) -> None:
        self.saving_throws.add_advantage(ability)

    def get_skill_roll_condition(self, skill: Skill):
        return self.skills.get_roll_condition(skill)

    def set_skill_roll_condition(
        self,
        skill: Skill,
        condition: Definitions.DiceRollCondition,
        reason: Optional[str] = None,
    ):
        self.skills.set_roll_condition(skill, condition, reason)

    def get_skill_roll_condition_reasons(self, skill: Skill) -> list[str]:
        return self.skills.get_roll_condition_reasons(skill)

    def get_saving_throw_modifier(self, ability: Ability) -> int:
        base_modifier = self.get_ability_modifier(ability)
        proficiency_bonus = (
            self.get_proficiency_bonus()
            if self.is_proficient_in_saving_throw(ability)
            else 0
        )
        derived = sum(
            bonus(self) for bonus in self._derived_saving_throw_bonuses.get(ability, [])
        )
        return (
            base_modifier
            + proficiency_bonus
            + self.saving_throws.get_bonus(ability)
            + derived
        )

    def calculate_hit_points(self) -> int:
        constitution_modifier = self.get_constitution_modifier()
        return self.combat.calculate_hit_points(
            base_class=self.base_class,
            level_per_class=self.level_per_class,
            constitution_modifier=constitution_modifier,
        )

    def calculate_armor_class(self) -> int:
        """The best applicable AC formula plus every AC bonus."""
        formulas = self.combat.get_applicable_armor_class_formulas(
            self.is_wielding_shield
        )
        base = max(self._armor_class_from(formula) for formula in formulas)
        derived = sum(bonus(self) for bonus in self._derived_armor_class_bonuses)
        return base + self.combat.armor_class_modifier + derived

    def _armor_class_from(self, formula: ArmorClassFormula) -> int:
        ability_modifier = sum(
            self.get_ability_modifier(ability) for ability in formula.abilities
        )
        if formula.ability_modifier_cap is not None:
            ability_modifier = min(ability_modifier, formula.ability_modifier_cap)
        return formula.base + ability_modifier

    def get_spell_casting_ability(self) -> Ability:
        return self._require_spell_casting_ability()

    def calculate_difficulty_class(self) -> int:
        return self.calculate_difficulty_class_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int:
        modifier = self.get_ability_modifier(ability)
        return 8 + self.get_proficiency_bonus() + modifier + self.spell_save_dc_bonus

    def calculate_attack_bonus(self) -> int:
        return self.calculate_attack_bonus_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        ability_modifier = self.get_ability_modifier(ability)
        return self.get_proficiency_bonus() + ability_modifier

    def get_spell_slots(self) -> dict[int, int]:
        spell_slots = self.spell_slots
        if spell_slots is None:
            raise ValueError("Character does not have spell slots.")
        return spell_slots

    def add_damage_resistance(
        self, damage_type: Definitions.DamageType, source: str
    ) -> None:
        self.damage_resistances.setdefault(damage_type, []).append(source)

    def add_damage_immunity(
        self, damage_type: Definitions.DamageType, source: str
    ) -> None:
        self.damage_immunities.setdefault(damage_type, []).append(source)

    def is_resistant_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return damage_type in self.damage_resistances

    def is_immune_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return damage_type in self.damage_immunities

    def get_damage_resistance_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self.damage_resistances.get(damage_type, [])

    def get_damage_immunity_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self.damage_immunities.get(damage_type, [])

    def add_condition_immunity(
        self, condition: Definitions.Condition, source: str
    ) -> None:
        self.condition_immunities.setdefault(condition, []).append(source)

    def is_immune_to_condition(self, condition: Definitions.Condition) -> bool:
        return condition in self.condition_immunities

    def get_condition_immunity_sources(
        self, condition: Definitions.Condition
    ) -> list[str]:
        return self.condition_immunities.get(condition, [])

    def add_sense(self, sense: Definitions.Sense, range_feet: int, source: str) -> None:
        """Grant a sense. The same sense from several sources keeps the best range."""
        self.sense_sources.setdefault(sense, []).append((range_feet, source))

    def add_sense_or_extension(
        self, sense: Definitions.Sense, range_feet: int, source: str
    ) -> None:
        """Grant a sense out to `range_feet` - or, if the character already has
        it, increase its range by `range_feet` (e.g. Umbral Sight)."""
        self._sense_extensions.setdefault(sense, []).append((range_feet, source))

    @property
    def senses(self) -> dict[Definitions.Sense, int]:
        """Range per sense: the best plain grant plus every extension. "Gain it,
        or +N if you already have it" is N on top of whatever else grants it,
        so the result doesn't depend on which applied first."""
        ranges = {}
        for sense in [*self.sense_sources, *self._sense_extensions]:
            best = max((r for r, _ in self.sense_sources.get(sense, [])), default=0)
            extra = sum(r for r, _ in self._sense_extensions.get(sense, []))
            ranges[sense] = best + extra
        return ranges

    def get_sense_range(self, sense: Definitions.Sense) -> int:
        return self.senses.get(sense, 0)

    def get_sense_sources(self, sense: Definitions.Sense) -> list[tuple[int, str]]:
        return self.sense_sources.get(sense, []) + [
            (range_feet, f"{source} (+{range_feet} ft. if already had)")
            for range_feet, source in self._sense_extensions.get(sense, [])
        ]

    def add_weapon_proficiency(self, weapon_proficiency: Enum) -> None:
        self.weapon_proficiencies.add(weapon_proficiency)

    def add_armor_training(self, armor_type: Definitions.ArmorType) -> None:
        self.armor_training.add(armor_type)

    def add_tool_proficiency(self, tool_proficiency: Any) -> None:
        """Proficiency with a tool (a ToolProficiency). The same tool from
        several sources is listed once."""
        if not any(type(t) is type(tool_proficiency) for t in self.tool_proficiencies):
            self.tool_proficiencies.append(tool_proficiency)

    def add_language(self, language: Definitions.Language, source: str) -> None:
        self.languages.setdefault(language, []).append(source)

    def knows_language(self, language: Definitions.Language) -> bool:
        return language in self.languages

    def get_language_sources(self, language: Definitions.Language) -> list[str]:
        return self.languages.get(language, [])
