"""The one object a character is: the sources it was built from (the player's
choices and every feature, spell, fighting style and item granted - see
Model/CharacterSources.py) plus every stat worked out from them.

A Character is finished and read-only. Builders fill in a CharacterSources
and hand it over: `Character(sources)` keeps its own copy, so nothing can
change it afterwards. Every derived value (the extension tree, the stamps, the
resolved spells and the Ledger) is worked out once, on first use. To get a
variant, build a new one from changed sources:
`Character(attr.evolve(character.sources, ...))`.

Evaluation applies every feature, armor, weapon, item and fighting style in
iter_stat_effects() to a write-only Effects view of a fresh Ledger
(Model/Effects.py) and seals it; queries then answer from it.

The Model package imports nothing from CharacterContent, not even for type
hints: features, fighting styles, armor, weapons and items are the base
classes in Model/Content/, which CharacterContent's concrete content
subclasses - so a Character hands out concrete types and nothing has to
narrow them back.
"""

from __future__ import annotations

import functools
from typing import Callable, Iterator, Optional, Sequence, TypeVar

import Core.Definitions as Definitions
from Core.Definitions import Ability, CharacterClass, Skill
from Core.Rules import MAX_ATTUNED_ITEMS, MAX_LEVEL, ability_modifier, proficiency_bonus
from Core.SpellcastingRules import SlotProgression
from Core.Weapons import WeaponProficiency, WeaponTraits
from Model.AbilityScores import AbilityScores
from Model.CharacterSources import CharacterSources
from Model.ClassLevels import ClassLevels
from Model.Content.Armor import AbstractArmor
from Model.Content.Effect import Effect
from Model.Content.Feature import Feature
from Model.Content.FightingStyle import FightingStyle
from Model.Content.Item import Item
from Model.Content.Weapon import AbstractWeapon
from Model.Effects import Effects, Ledger
from Model.FeatureGrants import ExtensionTree, FeatureGrant
from Model.Inventory import EquipmentEntry
from Model.Records.GrantStamp import GrantStamp
from Model.Records.SourcedValue import SourcedValue
from Model.Records.Tools import ToolProficiency
from Model.Senses import SenseGrant
from Model.Spells import SpellGrant, SpellReplacement, resolve_spells

FeatureT = TypeVar("FeatureT", bound=Feature)
T = TypeVar("T")
ApplyOrder = Callable[[list[Effect]], list[Effect]]


def in_given_order(effects: list[Effect]) -> list[Effect]:
    return effects


def _required(value: Optional[T], name: str) -> T:
    """A source every finished character has; builders fill them in
    piecemeal, so CharacterSources holds them as Optional."""
    if value is None:
        raise ValueError(f"Character {name} must be set.")
    return value


class Character:
    def __init__(
        self, sources: CharacterSources, *, apply_order: ApplyOrder = in_given_order
    ):
        """`apply_order`: the order iter_stat_effects() applies in - as listed,
        unless a test reorders them to prove the order doesn't matter
        (tests/test_feature_apply_order.py, tests/test_order_invariance.py)."""
        self._sources = sources.copy()
        self._apply_order = apply_order

    @property
    def sources(self) -> CharacterSources:
        """A copy of the sources this character was built from. Changing it
        changes nothing here: build a new Character from it for a variant."""
        return self._sources.copy()

    # ── Sources: what the character has ──────────────────────────────────────

    @property
    def character_name(self) -> Optional[str]:
        return self._sources.character_name

    @property
    def is_example(self) -> bool:
        return self._sources.is_example

    @property
    def class_levels(self) -> ClassLevels:
        return self._sources.class_levels

    @property
    def base_abilities(self) -> AbilityScores:
        """The player's ability scores before any increase."""
        return _required(self._sources.base_abilities, "abilities")

    @property
    def base_speed(self) -> int:
        """Walking speed given by the species, before any bonus."""
        return _required(self._sources.base_speed, "speed")

    @property
    def size(self) -> Definitions.CreatureSize:
        return _required(self._sources.size, "size")

    @property
    def feature_grants(self) -> list[FeatureGrant]:
        return self._sources.feature_grants

    @property
    def invocations(self) -> list[str]:
        return self._sources.invocations

    @property
    def spell_grants(self) -> list[SpellGrant]:
        return self._sources.spell_grants

    @property
    def spell_replacements(self) -> list[SpellReplacement]:
        return self._sources.spell_replacements

    @property
    def spell_casting_ability(self) -> Optional[Ability]:
        return self._sources.spell_casting_ability

    @property
    def fixed_spell_slots(self) -> dict[int, int]:
        """Spell slots set outright rather than worked out from caster levels."""
        return self._sources.fixed_spell_slots

    @property
    def weapon_masteries(self) -> list[AbstractWeapon]:
        return self._sources.weapon_masteries

    @property
    def fighting_styles(self) -> list[FightingStyle]:
        return self._sources.fighting_styles

    @property
    def experience_points(self) -> int:
        return self._sources.experience_points

    @property
    def extra_effects(self) -> list[Effect]:
        return self._sources.extra_effects

    @property
    def character_subclass(self) -> Optional[str]:
        return self.class_levels.character_subclass

    @property
    def base_class(self) -> Optional[CharacterClass]:
        return self.class_levels.base_class

    @property
    def level_per_class(self) -> dict[CharacterClass, int]:
        return self.class_levels.level_per_class

    @property
    def class_by_character_level(self) -> dict[int, CharacterClass]:
        return self.class_levels.class_by_character_level

    @property
    def character_level(self) -> int:
        return self.class_levels.character_level

    # The inventory is read through these, never handed out: gear added to it
    # after the Ledger was worked out would never reach the stats.

    @property
    def armors(self) -> list[AbstractArmor]:
        return self._sources.inventory.armors

    @property
    def weapons(self) -> list[AbstractWeapon]:
        return self._sources.inventory.weapons

    @property
    def items(self) -> list[tuple[Item, int]]:
        """(item, quantity), with same-type stacks merged."""
        return self._sources.inventory.items

    @property
    def equipment_entries(self) -> list[EquipmentEntry]:
        """Armor, weapons, items and gold in labeled entries, as acquired."""
        return self._sources.inventory.equipment_entries

    @property
    def starting_equipment_entry(self) -> Optional[EquipmentEntry]:
        return self._sources.inventory.starting_equipment_entry

    @property
    def current_gold(self) -> Optional[float]:
        return self._sources.inventory.current_gold

    # ── Features ─────────────────────────────────────────────────────────────

    @property
    def features(self) -> list[Feature]:
        """Every feature granted plainly (not as an extension)."""
        return [g.feature for g in self.feature_grants if g.extends is None]

    def has_granted(self, feature: Feature) -> bool:
        return id(feature) in self._stamps

    def stamp_of(self, feature: Feature) -> GrantStamp:
        """Where `feature` was granted from (a default stamp if it wasn't)."""
        return self._stamps.get(id(feature), GrantStamp())

    @functools.cached_property
    def _stamps(self) -> dict[int, GrantStamp]:
        """{id(feature): stamp}."""
        return {id(g.feature): g.stamp for g in self.feature_grants}

    def top_level_features(self) -> list[Feature]:
        """The features with a card of their own: every plain grant, then
        every "standalone" extension whose parent isn't granted."""
        return [*self.features, *self._extensions.standalone]

    def extensions_of(self, feature: Feature) -> list[Feature]:
        """The extensions granted onto `feature`, by grant level, then name,
        then who granted them - never by the order they were granted in.
        (The sheet orders them its own way: Presentation/FeatureOrder.py.)"""

        def canonical_order(extension: Feature) -> tuple:
            stamp = self.stamp_of(extension)
            return (
                stamp.level,
                extension.name,
                stamp.kind.sheet_rank,
                stamp.granted_by,
            )

        return sorted(self._extensions.children_of(feature), key=canonical_order)

    def iter_features_with_extensions(self) -> Iterator[Feature]:
        """Every granted feature followed by its extensions (depth-first).
        Extensions are real features: their apply() runs like any other's."""
        tree = self._extensions

        def walk(features: Sequence[Feature]) -> Iterator[Feature]:
            for feature in features:
                yield feature
                yield from walk(tree.children_of(feature))

        return walk(self.top_level_features())

    @functools.cached_property
    def _extensions(self) -> ExtensionTree:
        """The extension tree (Model/FeatureGrants.py)."""
        return ExtensionTree.resolve(self.feature_grants)

    def has_feature(self, feature_type: type) -> bool:
        """Whether a feature of `feature_type` is granted plainly (not as an
        extension)."""
        return any(isinstance(f, feature_type) for f in self.features)

    def get_features_by_type(self, feature_type: type[FeatureT]) -> list[FeatureT]:
        return [
            feature for feature in self.features if isinstance(feature, feature_type)
        ]

    # ── Spells ───────────────────────────────────────────────────────────────

    @functools.cached_property
    def spells(self) -> list[SpellGrant]:
        """Every spell known, replacements applied, in canonical order (grant
        level, name, granted_by) - see Model/Spells.py."""
        return resolve_spells(self.spell_grants, self.spell_replacements)

    # ── Weapons ──────────────────────────────────────────────────────────────

    def is_proficient_with_weapon(self, weapon: WeaponTraits) -> bool:
        """Whether any weapon proficiency the character has covers a
        weapon with these traits."""
        return self._ledger.equipment_training.is_proficient_with(weapon)

    def get_weapon_attack_bonuses(self, weapon: WeaponTraits) -> list[tuple[int, str]]:
        """(value, label) for every attack roll bonus the wielder brings to
        a weapon with these traits (e.g. the Archery fighting style)."""
        return self._ledger.weapon_bonuses.attack_bonuses(weapon)

    def get_weapon_damage_bonuses(self, weapon: WeaponTraits) -> list[tuple[int, str]]:
        """(value, label) for every damage roll bonus the wielder brings to
        a weapon with these traits (e.g. the Dueling fighting style)."""
        return self._ledger.weapon_bonuses.damage_bonuses(weapon)

    # ── Evaluation ───────────────────────────────────────────────────────────

    def iter_stat_effects(self) -> list[Effect]:
        """Everything that records effects: features and their extensions,
        armor, weapons, items, fighting styles (only those with a computed
        effect - Defense, Archery, Dueling, ... - record anything) and extra
        effects. Each has apply(effects); the order is irrelevant.
        (Proficiencies come from features too - e.g. ClassProficiencies.)
        Weapons are never changed: bonuses the wielder brings to them are
        recorded in weapon_bonuses."""
        return [
            *self.iter_features_with_extensions(),
            *self.armors,
            *self.weapons,
            *(item for item, _quantity in self.items),
            *self.fighting_styles,
            *self.extra_effects,
        ]

    @functools.cached_property
    def _ledger(self) -> Ledger:
        """What every effect recorded, one part per concern (Model/Effects.py),
        worked out on first use. Private: everything is read through the
        queries below, which hand this character to the parts' resolvers.
        Requirements aren't checked here - validate() does that, against the
        complete set of effects."""
        _required(self._sources.base_abilities, "abilities")
        _required(self._sources.base_speed, "speed")
        _required(self.base_class, "base class")

        ledger = Ledger()
        effects = Effects(ledger)
        # Ordering contract (see Model/Content/Improvements.py): every effect
        # only records facts - Effects is write-only - and every value is
        # worked out when it's read, so features, armor, weapons, items and
        # fighting styles may apply in any order.
        for effect in self._apply_order(self.iter_stat_effects()):
            effect.apply(effects)
        return ledger

    def _validate_sources(self) -> None:
        """Checks that need no evaluation: every field a finished character
        needs is set (builders fill them in piecemeal, so most are Optional
        while a build is in progress), at most one worn body armor, the
        attunement limit, that every extension's parent is granted, and that
        the spells resolve (see Model/Spells.py)."""
        self._extensions
        self.spells
        self._validate_feats_taken_once()
        _required(self.character_name, "name")
        _required(self.character_subclass, "subclass")
        _required(self._sources.base_abilities, "abilities")
        _required(self._sources.base_speed, "speed")
        _required(self._sources.size, "size")
        _required(self.base_class, "base class")

        # Validate one-armor rule: at most one worn non-shield armor
        worn_body_armors = [
            armor for armor in self.armors if not armor.is_shield and armor.is_wearing
        ]
        if len(worn_body_armors) > 1:
            armor_names = ", ".join(armor.name for armor in worn_body_armors)
            raise ValueError(
                f"Character cannot wear multiple armors at once. "
                f"Conflicting armors: {armor_names}. "
                f"(Shields do not count toward this limit.)"
            )

        # Attunement: at most MAX_ATTUNED_ITEMS magic items at once.
        # Unworn gear (is_wearing=False) is carried, not attuned.
        attuned = [
            gear.name
            for gear in [*self.armors, *self.weapons, *(i for i, _ in self.items)]
            if gear.requires_attunement and gear.is_wearing
        ]
        if len(attuned) > MAX_ATTUNED_ITEMS:
            raise ValueError(
                f"Character can attune to at most {MAX_ATTUNED_ITEMS} magic items, "
                f"but is attuned to {len(attuned)}: {', '.join(attuned)}."
            )

    def _validate_feats_taken_once(self) -> None:
        """A feat that isn't Repeatable can be taken only once - from the
        background, the species and every Ability Score Improvement level
        together."""
        grants_by_type: dict[type, list[Feature]] = {}
        for feature in self.iter_features_with_extensions():
            if not feature.repeatable:
                grants_by_type.setdefault(type(feature), []).append(feature)
        for grants in grants_by_type.values():
            if len(grants) > 1:
                raise ValueError(
                    f"{grants[0].name} is granted {len(grants)} times, "
                    "but it isn't Repeatable."
                )

    def validate(self) -> "Character":
        """The single validation entry point: the sources (required fields,
        one worn armor, attunement), then every requirement against the
        complete set of effects (expertise needs proficiency, an armor's
        Strength, multiclass ability minimums). Returns the character, so a
        build can be checked inline: `builder.build().validate()`."""
        self._validate_sources()
        self._ledger.validate(self)
        return self

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a shield alone doesn't count)."""
        return self._ledger.worn_armor.is_wearing_armor

    @property
    def worn_armor_type(self) -> Optional[Definitions.ArmorType]:
        """The worn body armor's type (None without body armor)."""
        return self._ledger.worn_armor.body_armor_type

    @property
    def is_wielding_shield(self) -> bool:
        return self._ledger.worn_armor.shield_wielded

    @property
    def spell_slots(self) -> dict[int, int]:
        return self._ledger.spellcasting.spell_slots(self)

    @property
    def pact_magic_slots(self) -> dict[int, int]:
        return self._ledger.spellcasting.pact_magic_slots(self)

    def get_slot_progression(
        self, max_level: int = MAX_LEVEL
    ) -> Optional[SlotProgression]:
        """When each of this character's slots is gained, up to character
        level `max_level`: the levels taken so far follow the classes
        actually taken, and later levels carry on in the most recently taken
        class. None when the class taken at some level isn't recorded."""
        taken: list[CharacterClass] = []
        for level in range(1, self.character_level + 1):
            character_class = self.class_by_character_level.get(level)
            if character_class is None:
                return None
            taken.append(character_class)
        if not taken:
            return None
        class_path = taken + [taken[-1]] * (max_level - len(taken))
        return self._ledger.spellcasting.slot_progression(class_path)

    @property
    def initiative_roll_condition(self) -> Definitions.DiceRollCondition:
        return self._ledger.initiative.roll_condition(self)

    # -- Armor training (2024 PHB) - see Ledger ---------------------------------

    @property
    def is_wearing_untrained_armor(self) -> bool:
        return self._ledger.is_wearing_untrained_armor()

    @property
    def has_shield_training(self) -> bool:
        return self._ledger.has_shield_training()

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        """Disadvantage on D20 Tests with `ability` from untrained armor."""
        return self._ledger.has_untrained_armor_disadvantage(ability)

    @property
    def warnings(self) -> list[str]:
        """Legal but bad choices the player should know about."""
        return self._ledger.armor_warnings()

    def calculate_initiative(self) -> int:
        return self._ledger.initiative.total(self)

    def calculate_speed(self) -> int:
        return self._ledger.speed.total(self)

    def get_carrying_capacity_sources(self) -> list[SourcedValue]:
        """Returns all carrying capacity sources, including the dynamic 'Person' base."""
        return self._ledger.carrying_capacity.sources(self)

    def get_carrying_capacity(self) -> int:
        """Returns the total carrying capacity in item slots (base 3 + STR mod + bonuses)."""
        return self._ledger.carrying_capacity.total(self)

    def _require_spell_casting_ability(self) -> Ability:
        if self.spell_casting_ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        return self.spell_casting_ability

    # ── Sources, read through CharacterView ───────────────────────────────────────

    def get_base_ability_score(self, ability: Ability) -> int:
        """The player's score before any increase."""
        return self.base_abilities.get_score(ability)

    def get_base_speed(self) -> int:
        return self.base_speed

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
        return proficiency_bonus(self.character_level)

    def get_ability_score(self, ability: Ability) -> int:
        """The final score: base, every capped increase and equipment bonuses."""
        return self._ledger.ability_increases.score(ability, self)

    def get_own_ability_score(self, ability: Ability) -> int:
        """The score without equipment bonuses - what an armor's Strength
        requirement or a multiclass minimum checks."""
        return self._ledger.ability_increases.own_score(ability, self)

    def get_ability_modifier(self, ability: Ability) -> int:
        return ability_modifier(self.get_ability_score(ability))

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
        return self._ledger.skills.is_proficient(skill)

    def has_expertise_in_skill(self, skill: Skill) -> bool:
        return self._ledger.skills.has_expertise(skill)

    def get_skill_ability(self, skill: Skill) -> Ability:
        return self._ledger.skills.ability(skill, self)

    def get_skill_modifier(self, skill: Skill) -> int:
        return self._ledger.skills.modifier(skill, self)

    def get_skill_bonus(self, skill: Skill) -> int:
        return self._ledger.skills.get_total_bonus(skill, self)

    def get_skill_bonus_sources(self, skill: Skill) -> list[SourcedValue]:
        return self._ledger.skills.get_all_bonus_sources(skill, self)

    def is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        return self._ledger.saving_throws.is_proficient(ability)

    def has_advantage_in_saving_throw(self, ability: Ability) -> bool:
        return self._ledger.saving_throws.is_advantaged(ability)

    def get_saving_throw_roll_condition(
        self, ability: Ability
    ) -> Definitions.DiceRollCondition:
        return self._ledger.saving_throws.roll_condition(ability, self)

    def get_skill_roll_condition(self, skill: Skill) -> Definitions.DiceRollCondition:
        return self._ledger.skills.roll_condition(skill, self)

    def get_skill_roll_condition_reasons(self, skill: Skill) -> list[str]:
        return self._ledger.skills.roll_condition_reasons(skill, self)

    def get_saving_throw_modifier(self, ability: Ability) -> int:
        return self._ledger.saving_throws.modifier(ability, self)

    def calculate_hit_points(self) -> int:
        return self._ledger.hit_points.total(self)

    def calculate_armor_class(self, ignore_shield: bool = False) -> int:
        """The best applicable AC formula plus every AC bonus. ignore_shield:
        the AC with the Shield set aside (its bonus gone, and formulas it
        disables - Monk's Unarmored Defense - available again)."""
        return self._ledger.armor_class.total(self, ignore_shield)

    def calculate_difficulty_class(self) -> int:
        return self.calculate_difficulty_class_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int:
        return self._ledger.spellcasting.difficulty_class(ability, self)

    @property
    def spell_save_dc_bonus(self) -> int:
        """Flat bonus to the spell save DC on top of 8 + ability modifier +
        proficiency bonus (e.g. from an item)."""
        return self._ledger.spellcasting.spell_save_dc_bonus

    def calculate_attack_bonus(self) -> int:
        return self.calculate_attack_bonus_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        return self._ledger.spellcasting.attack_bonus(ability, self)

    def is_resistant_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return self._ledger.defenses.is_resistant_to_damage(damage_type)

    def is_immune_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return self._ledger.defenses.is_immune_to_damage(damage_type)

    def get_damage_resistance_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self._ledger.defenses.get_damage_resistance_sources(damage_type)

    def get_damage_immunity_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self._ledger.defenses.get_damage_immunity_sources(damage_type)

    def is_immune_to_condition(self, condition: Definitions.Condition) -> bool:
        return self._ledger.defenses.is_immune_to_condition(condition)

    def get_condition_immunity_sources(
        self, condition: Definitions.Condition
    ) -> list[str]:
        return self._ledger.defenses.get_condition_immunity_sources(condition)

    def get_sense_range(self, sense: Definitions.Sense) -> int:
        return self._ledger.senses.get_sense_range(sense)

    def get_sense_sources(self, sense: Definitions.Sense) -> list[SenseGrant]:
        return self._ledger.senses.get_sense_sources(sense)

    def knows_language(self, language: Definitions.Language) -> bool:
        return self._ledger.languages.knows(language)

    # ── Listings: everything of a kind, each with the sources that granted it ──

    def languages(self) -> dict[Definitions.Language, list[str]]:
        return self._ledger.languages.known

    def senses(self) -> dict[Definitions.Sense, int]:
        """The range in feet of every sense the character has."""
        return self._ledger.senses.ranges

    def damage_resistances(self) -> dict[Definitions.DamageType, list[str]]:
        return self._ledger.defenses.damage_resistances

    def damage_immunities(self) -> dict[Definitions.DamageType, list[str]]:
        return self._ledger.defenses.damage_immunities

    def condition_immunities(self) -> dict[Definitions.Condition, list[str]]:
        return self._ledger.defenses.condition_immunities

    def armor_training(self) -> frozenset[Definitions.ArmorType]:
        return frozenset(self._ledger.equipment_training.armor_training)

    def weapon_proficiencies(self) -> frozenset[WeaponProficiency]:
        return frozenset(self._ledger.equipment_training.weapon_proficiencies)

    def tool_proficiencies(self) -> list[ToolProficiency]:
        return self._ledger.equipment_training.tool_proficiencies

    def get_language_sources(self, language: Definitions.Language) -> list[str]:
        return self._ledger.languages.sources(language)
