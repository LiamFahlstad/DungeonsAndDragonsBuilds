"""The one object a character is: the player's decisions and the sources they
grant (features, spells, fighting styles, inventory), plus every stat worked
out from them.

Evaluation is internal and lazy. The first query after any change builds a
fresh Effects record (StatBlocks/Effects.py) by applying every feature, armor,
weapon, item and fighting style in iter_stat_effects(), then answers queries
from it until the sources change again. A version counter decides when that
is (see _get_effects).

This module is the model: it imports nothing from CharacterContent at
runtime (features, items and fighting styles appear in annotations only), so
CharacterContent can import it without a cycle. CharacterStatBlock
(StatBlocks/CharacterStatBlock.py) and CharacterSheetData
(Builds/CharacterSheetAccumulator.py) are aliases of Character, kept so the
existing imports keep working.
"""

from __future__ import annotations

import copy
from contextlib import contextmanager
from enum import Enum
from typing import TYPE_CHECKING, Any, Iterator, Optional

import attr

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
from StatBlocks.Effects import Effects
from StatBlocks.EquipmentTraining import EquipmentTraining
from StatBlocks.HitPoints import HitPoints
from StatBlocks.Initiative import Initiative
from StatBlocks.Inventory import Inventory
from StatBlocks.Languages import Languages
from StatBlocks.SavingThrows import SavingThrows
from StatBlocks.Senses import Senses
from StatBlocks.Skills import Skills
from StatBlocks.Speed import Speed
from StatBlocks.Spellcasting import Spellcasting
from StatBlocks.WeaponBonuses import WeaponBonuses
from StatBlocks.WornArmor import WornArmor

if TYPE_CHECKING:
    from CharacterContent.Features.CharacterFeats.OriginFeats import OriginFeat
    from CharacterContent.Features.CombatFeatures.FightingStyles import (
        FightingStyle,
    )
    from CharacterContent.Features.Core.BaseFeatures import Feature
    from CharacterContent.Items.Armor import AbstractArmor
    from CharacterContent.Items.Items import Item
    from CharacterContent.Items.Weapons import AbstractWeapon

MAX_ATTUNED_ITEMS = 3

# How many times any feature, anywhere, has gained an extension. A feature
# can't reach the Character(s) it was granted to, so Feature.extend_feature()
# bumps this and every Character treats its cached evaluation as out of date.
_feature_extensions = 0


def note_feature_extended() -> None:
    """Called by Feature.extend_feature() - see _feature_extensions."""
    global _feature_extensions
    _feature_extensions += 1


def _count_change(character: "Character", attribute: Any, value: Any) -> Any:
    """attrs on_setattr hook: assigning any public field is a change to the
    character's sources."""
    if not attribute.name.startswith("_"):
        object.__setattr__(character, "_version", character._version + 1)
    return value


@attr.s(auto_attribs=True, on_setattr=_count_change)
class Character:
    character_name: Optional[str] = None
    is_example: bool = False
    # Levels, level-by-level history, base class and subclasses - see
    # StatBlocks/ClassLevels.py. character_subclass/base_class/
    # level_per_class/class_by_character_level below are thin delegating
    # properties kept for the many existing readers of those names.
    class_levels: ClassLevels = attr.Factory(ClassLevels)
    # The player's ability scores before any increase. Effects work on a
    # copy (see abilities).
    base_abilities: Optional[AbilityScores] = None
    # Walking speed given by the species, before any bonus (see speed).
    base_speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None

    # Every feature in the order it was granted. The order only decides how
    # the sheet lists them: no stat depends on it (see _get_effects).
    features: list[Feature] = attr.Factory(list)
    invocations: list[str] = attr.Factory(list)
    spells: list[tuple[str, Ability, Optional[str], int]] = attr.Factory(list)
    spell_casting_ability: Optional[Ability] = None
    # Spell slots set outright rather than worked out from caster levels.
    fixed_spell_slots: dict[int, int] = attr.Factory(dict)

    weapon_masteries: list[AbstractWeapon] = attr.Factory(list)
    fighting_styles: list[FightingStyle] = attr.Factory(list)
    # Armor, weapons and items, grouped into labeled entries (Starting
    # Equipment, then adventuring gear added later), plus starting and
    # current gold - see StatBlocks/Inventory.py. CharacterBuilder.build()
    # gives each character its own copy of the builder's inventory.
    # armors/weapons/items below are its flat views, which AC, attacks and
    # carrying capacity read.
    inventory: Inventory = attr.Factory(Inventory)
    experience_points: int = 0

    # Goes up on every change to the sources above (every add_*/set_* call,
    # and any field assignment - see _count_change). Together with the
    # inventory's own version and _feature_extensions it decides when the
    # cached evaluation is out of date.
    _version: int = attr.ib(default=0, init=False, eq=False, repr=False)
    _effects: Optional[Effects] = attr.ib(
        default=None, init=False, eq=False, repr=False
    )
    _effects_key: Optional[tuple[int, int, int]] = attr.ib(
        default=None, init=False, eq=False, repr=False
    )
    # Class-relative level currently being applied by
    # BaseClassLevelFeatures.add_features, used to tag each spell/cantrip
    # with the level it was granted on (see set_current_grant_level). Defaults
    # to 1, matching the convention _feature_level uses for features whose
    # origin can't be parsed - this covers spells granted outside the
    # per-level class flow (species spells, origin feat spells via
    # add_origin_feat, etc).
    _current_grant_level: int = attr.ib(default=1, init=False, eq=False, repr=False)
    # Index into spells where the duplicate check starts - see
    # separate_spell_source.
    _duplicate_spell_check_start: int = attr.ib(
        default=0, init=False, eq=False, repr=False
    )

    # ── Sources: what the character has ──────────────────────────────────────

    def _changed(self) -> None:
        """Record a change to the sources, so the next query re-evaluates."""
        self._version += 1

    @property
    def character_subclass(self) -> Optional[str]:
        return self.class_levels.character_subclass

    @character_subclass.setter
    def character_subclass(self, value: Optional[str]) -> None:
        self._changed()
        self.class_levels.character_subclass = value

    @property
    def base_class(self) -> Optional[CharacterClass]:
        return self.class_levels.base_class

    @base_class.setter
    def base_class(self, value: Optional[CharacterClass]) -> None:
        self._changed()
        self.class_levels.base_class = value

    @property
    def level_per_class(self) -> dict[CharacterClass, int]:
        return self.class_levels.level_per_class

    @level_per_class.setter
    def level_per_class(self, value: dict[CharacterClass, int]) -> None:
        self._changed()
        self.class_levels.level_per_class = value

    @property
    def class_by_character_level(self) -> dict[int, CharacterClass]:
        return self.class_levels.class_by_character_level

    @class_by_character_level.setter
    def class_by_character_level(self, value: dict[int, CharacterClass]) -> None:
        self._changed()
        self.class_levels.class_by_character_level = value

    @property
    def character_level(self) -> int:
        return self.class_levels.character_level

    @property
    def armors(self) -> list[AbstractArmor]:
        return self.inventory.armors

    @property
    def weapons(self) -> list[AbstractWeapon]:
        return self.inventory.weapons

    @property
    def items(self) -> list[tuple[Item, int]]:
        """(item, quantity), with same-type stacks merged."""
        return self.inventory.items

    def add_feature(self, feature: Feature):
        self._changed()
        self.features.append(feature)

    def remove_features(self, should_remove) -> None:
        """Remove every feature for which `should_remove(feature)` is true."""
        self.features = [f for f in self.features if not should_remove(f)]

    def iter_features_with_extensions(self) -> Iterator[Feature]:
        """Every granted feature followed by its extensions (depth-first).
        Extensions are real features: their apply() runs like any other's."""

        def walk(features: list[Feature]) -> Iterator[Feature]:
            for feature in features:
                yield feature
                yield from walk(feature.extensions)

        return walk(self.features)

    def add_origin_feat(self, origin_feat: OriginFeat):
        self.add_feature(origin_feat)
        for spell in origin_feat.get_spells():
            self.add_spell(spell, origin_feat.get_spell_casting_ability())

    def get_features_by_type(self, feature_type: type) -> list[Any]:
        return [
            feature for feature in self.features if isinstance(feature, feature_type)
        ]

    def get_level_for_class(self, character_class: CharacterClass) -> int:
        return self.class_levels.get_class_level(character_class)

    def record_class_level(self, character_level: int, character_class: CharacterClass):
        self._changed()
        self.class_levels.record_class_level(character_level, character_class)

    def set_class_level(self, character_class: CharacterClass, level: int) -> None:
        """Set the character's total level in `character_class` (a builder
        resuming a class states the class's final total level)."""
        self._changed()
        self.class_levels.level_per_class[character_class] = level

    def set_current_grant_level(self, level: int) -> None:
        """Set the class-relative level that subsequent add_spell/add_cantrip
        calls will be tagged with. Called by BaseClassLevelFeatures.add_features
        right before invoking each per-level add_features method."""
        self._current_grant_level = level

    def add_armor(self, armor: AbstractArmor):
        """Add armor outside starting equipment and adventuring gear (see
        Inventory.add_armor)."""
        self.inventory.add_armor(armor)

    def add_weapon(self, weapon: AbstractWeapon):
        # Proficiency isn't decided here: the weapon works it out on read
        # against every proficiency (AbstractWeapon.is_proficient).
        self.inventory.add_weapon(weapon)

    def add_weapon_mastery(self, weapon: AbstractWeapon):
        self._changed()
        self.weapon_masteries.append(weapon)

    def add_fighting_style(self, fighting_style: FightingStyle):
        self._changed()
        self.fighting_styles.append(fighting_style)

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        spell_casting_ability = self._resolve_spell_casting_ability(
            spell_casting_ability
        )

        if spell in self._spell_names_checked_for_duplicates():
            raise ValueError(f"Spell {spell} already added.")
        self._changed()
        self.spells.append(
            (spell, spell_casting_ability, additional_ruling, self._current_grant_level)
        )

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        spell_casting_ability = self._resolve_spell_casting_ability(
            spell_casting_ability
        )
        if cantrip in self._spell_names_checked_for_duplicates():
            raise ValueError(f"Cantrip {cantrip} already added.")
        self._changed()
        self.spells.append(
            (
                cantrip,
                spell_casting_ability,
                additional_ruling,
                self._current_grant_level,
            )
        )

    def _spell_names_checked_for_duplicates(self) -> list[str]:
        return [s[0] for s in self.spells[self._duplicate_spell_check_start :]]

    @contextmanager
    def separate_spell_source(self) -> Iterator[None]:
        """Spells and cantrips added inside this block are only checked for
        duplicates against each other, not against spells granted before
        it. Species spells use this: a species granting a spell the
        character's class also grants (Rock Gnome Prestidigitation on a
        Wizard) lists it from both sources rather than failing the build."""
        self._duplicate_spell_check_start = len(self.spells)
        try:
            yield
        finally:
            self._duplicate_spell_check_start = 0

    def replace_spells(self, replace_spells: dict[str, str]):
        for old_spell, new_spell in replace_spells.items():
            self.replace_spell(old_spell, new_spell)

    def replace_spell(
        self,
        old_spell: str,
        new_spell: str,
        new_spell_ability: Optional[Ability] = None,
        new_additional_ruling: Optional[str] = None,
    ):
        new_spells = []
        success = False
        for spell_name, spell_ability, additional_ruling, grant_level in self.spells:
            if spell_name == old_spell:
                new_spells.append(
                    (
                        new_spell,
                        new_spell_ability or spell_ability,
                        (
                            new_additional_ruling
                            if new_additional_ruling is not None
                            else additional_ruling
                        ),
                        grant_level,
                    )
                )
                success = True
            else:
                new_spells.append(
                    (spell_name, spell_ability, additional_ruling, grant_level)
                )
        if not success:
            raise ValueError(f"Spell {old_spell} not found to replace.")
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self._changed()
        self.invocations.append(invocation)

    def add_item(self, item: Item, quantity: int = 1):
        self.inventory.add_item(item, quantity)

    def _resolve_spell_casting_ability(
        self, spell_casting_ability: Optional[Ability]
    ) -> Ability:
        if spell_casting_ability is not None:
            return spell_casting_ability
        if self.spell_casting_ability is None:
            raise ValueError(
                "Spell casting ability must be provided if not already set."
            )
        return self.spell_casting_ability

    # ── Evaluation ───────────────────────────────────────────────────────────

    def iter_stat_effects(self, features: Optional[list[Feature]] = None) -> list[Any]:
        """Everything that records effects: features and their extensions,
        armor, weapons, items and fighting styles with a computed effect
        (Defense, Archery, Dueling, ...). Each has apply(character_stat_block);
        the order is irrelevant. (Proficiencies come from features too - e.g.
        ClassProficiencies.) Weapons are never changed: bonuses the wielder
        brings to them are recorded in weapon_bonuses."""
        if features is None:
            features = list(self.iter_features_with_extensions())
        return [
            *features,
            *self.armors,
            *self.weapons,
            *(item for item, _quantity in self.items),
            # Only fighting styles with a computed effect (FightStyleModifier)
            # have apply(); the rest are descriptions.
            *(style for style in self.fighting_styles if hasattr(style, "apply")),
        ]

    def _get_effects(self) -> Effects:
        """The evaluated effects: cached, and rebuilt from the sources on the
        first query after any change to them. Requirements aren't checked
        here - validate() (and setup_character_stat_block()) does that,
        against the complete set of effects."""
        key = (self._version, self.inventory.version, _feature_extensions)
        if self._effects is not None and self._effects_key == key:
            return self._effects

        if self.base_abilities is None:
            raise ValueError("Character abilities must be set.")
        if self.base_speed is None:
            raise ValueError("Character speed must be set.")
        if self.base_class is None:
            raise ValueError("Character base class must be set.")

        effects = Effects(
            # A copy: effects record their increases on it, and recording
            # them on the base scores would stack them on every rebuild.
            abilities=copy.deepcopy(self.base_abilities),
            base_speed=self.base_speed,
            spellcasting=Spellcasting(
                ability=self.spell_casting_ability, fixed_slots=self.fixed_spell_slots
            ),
        )
        # Cached before any effect applies: apply() records through this
        # character's part attributes (skills, armor_class, ...), which must
        # reach the record being built rather than start another build.
        self._effects, self._effects_key = effects, key
        try:
            # Ordering contract (see CharacterContent/Features/Core/Improvements.py):
            # every effect only records facts, and every value is worked out
            # when it's read - so features, armor, weapons, items and fighting
            # styles may apply in any order. tests/test_feature_apply_order.py
            # shuffles iter_stat_effects() to prove it.
            for effect in self.iter_stat_effects(
                list(self.iter_features_with_extensions())
            ):
                effect.apply(self)
        except BaseException:
            self._effects = None
            raise
        return effects

    def _validate_sources(self) -> None:
        """Checks that need no evaluation: every field a finished character
        needs is set (builders fill them in piecemeal, so most are Optional
        while a build is in progress), at most one worn body armor, and the
        attunement limit."""
        if self.character_name is None:
            raise ValueError("Character name must be set.")
        if self.character_subclass is None:
            raise ValueError("Character subclass must be set.")
        if self.base_abilities is None:
            raise ValueError("Character abilities must be set.")
        if self.base_speed is None:
            raise ValueError("Character speed must be set.")
        if self.size is None:
            raise ValueError("Character size must be set.")
        if self.base_class is None:
            raise ValueError("Character base class must be set.")

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

        # Attunement: a creature can be attuned to at most three magic items.
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

    def validate(self) -> None:
        """The single validation entry point: the sources (required fields,
        one worn armor, attunement), then every requirement against the
        complete set of effects (expertise needs proficiency, an armor's
        Strength, multiclass ability minimums)."""
        self._validate_sources()
        self._get_effects().validate(self.class_levels)

    def setup_character_stat_block(self) -> "Character":
        """Kept for existing callers: evaluation is internal and lazy now.
        Validates the character and returns it."""
        self.validate()
        return self

    # ── The evaluated parts ──────────────────────────────────────────────────
    # Each reads one part of the evaluated Effects (StatBlocks/Effects.py).

    @property
    def abilities(self) -> AbilityScores:
        """Ability scores with every increase applied (base_abilities holds
        the scores before them)."""
        return self._get_effects().abilities

    @property
    def speed(self) -> Speed:
        """Base walking speed plus every bonus (the int is calculate_speed())."""
        return self._get_effects().speed

    @property
    def spellcasting(self) -> Spellcasting:
        return self._get_effects().spellcasting

    @property
    def skills(self) -> Skills:
        return self._get_effects().skills

    @property
    def saving_throws(self) -> SavingThrows:
        return self._get_effects().saving_throws

    @property
    def carrying_capacity(self) -> CarryingCapacity:
        return self._get_effects().carrying_capacity

    @property
    def armor_class(self) -> ArmorClass:
        return self._get_effects().armor_class

    @property
    def worn_armor(self) -> WornArmor:
        return self._get_effects().worn_armor

    @property
    def hit_points(self) -> HitPoints:
        return self._get_effects().hit_points

    @property
    def equipment_training(self) -> EquipmentTraining:
        return self._get_effects().equipment_training

    @property
    def languages(self) -> Languages:
        return self._get_effects().languages

    @property
    def defenses(self) -> Defenses:
        return self._get_effects().defenses

    @property
    def senses(self) -> Senses:
        return self._get_effects().senses

    @property
    def ability_requirements(self) -> AbilityRequirements:
        return self._get_effects().ability_requirements

    @property
    def initiative(self) -> Initiative:
        return self._get_effects().initiative

    @property
    def weapon_bonuses(self) -> WeaponBonuses:
        return self._get_effects().weapon_bonuses

    # ── Queries (and the recording methods features call) ───────────────────

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a shield alone doesn't count)."""
        return self.worn_armor.is_wearing_armor

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
