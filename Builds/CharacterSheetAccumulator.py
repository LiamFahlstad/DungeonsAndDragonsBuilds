import copy
from typing import Any, Iterator, Optional

import attr

import Core.Definitions as Definitions
from Builds.EquipmentHandler import EquipmentEntry
from CharacterContent.Features.CharacterFeats import OriginFeats
from CharacterContent.Features.CombatFeatures.FightingStyles import (
    FightingStyle,
    FightStyleModifier,
    FightStyleWeaponFeature,
)
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Items import Items
from CharacterContent.Items.Armor import AbstractArmor
from CharacterContent.Items.Weapons import AbstractWeapon
from Core.Definitions import Ability, CharacterClass
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock

# Scalar values merge_with treats as "not set": an incoming value equal to one
# of these never overwrites an existing value. 0 is included so that e.g. a
# builder that never touched experience_points (int, default 0) cannot reset
# XP accumulated by an earlier builder. All enums used in sheet fields are str
# enums with non-empty values, so none of them compare equal to "" or 0.
_MERGE_EMPTY_VALUES = (None, [], {}, "", 0)

MAX_ATTUNED_ITEMS = 3


@attr.dataclass
class CharacterSheetData:
    character_name: Optional[str] = None
    character_subclass: Optional[str] = None
    base_class: Optional[CharacterClass] = None
    is_example: bool = False
    level_per_class: dict[CharacterClass, int] = attr.Factory(dict)
    # Which class a given total character level was taken in, e.g. {1: FIGHTER,
    # 2: FIGHTER, 3: WIZARD}. Populated by ClassBuilder.create() as builders are
    # applied in order, so it reflects the actual level-by-level pick history
    # (including dips and resumed classes), not just the final per-class totals
    # in level_per_class.
    class_by_character_level: dict[int, CharacterClass] = attr.Factory(dict)
    abilities: Optional[AbilitiesStatBlock] = None
    skills: Optional[SkillsStatBlock] = None
    speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None
    saving_throws: Optional[SavingThrowsStatBlock] = None

    # Every feature in the order it was granted. The order only decides how
    # the sheet lists them: no stat depends on it (see
    # setup_character_stat_block).
    features: list[Feature] = attr.Factory(list)
    invocations: list[str] = attr.Factory(list)
    spells: list[tuple[str, Ability, Optional[str], int]] = attr.Factory(list)
    spell_casting_ability: Optional[Ability] = None

    spell_slots: dict[int, int] = attr.Factory(dict)

    armors: list[AbstractArmor] = attr.Factory(list)
    weapons: list[AbstractWeapon] = attr.Factory(list)
    weapon_masteries: list[AbstractWeapon] = attr.Factory(list)
    fighting_styles: list[FightingStyle] = attr.Factory(list)
    items: list[tuple[Items.Item, int]] = attr.Factory(list)  # (item_name, quantity)
    # Same gear as armors/weapons/items above, grouped into labeled batches
    # (Starting Equipment, then whatever adventuring gear was added later via
    # an EquipmentHandler - see Builds/EquipmentHandler.py) so the sheet can
    # show where each item came from. armors/weapons/items stay the flat
    # lists everything else (AC, attacks, carrying capacity) reads.
    equipment_entries: list[EquipmentEntry] = attr.Factory(list)
    experience_points: int = 0
    # GP left over after "buying" the base class's granted starting gear at
    # listed prices, from that class's flat Starting Equipment gold option.
    # Set once, by CharacterBuilder.build() from its EquipmentHandler - a
    # multiclass dip never grants starting gold again.
    starting_gold: Optional[float] = None
    # Running GP total after starting gold plus every gold=/Bought(...)
    # delta recorded via add_adventuring_gear since. Set once by
    # CharacterBuilder.build() from its EquipmentHandler.current_gold - see
    # Builds/EquipmentHandler.py.
    current_gold: Optional[float] = None
    # The entry in equipment_entries representing Starting Equipment
    # specifically, passed to the writer alongside equipment_entries (not put
    # on CharacterStatBlock - that's a StatBlocks-layer class that shouldn't
    # need to import an EquipmentEntry type from the Builds layer) so it can
    # check `entry is starting_equipment_entry` instead of matching on label.
    starting_equipment_entry: Optional[EquipmentEntry] = None
    _character_cached: Optional[CharacterStatBlock] = None
    # Identity of every feature + extension the cached stat block was built
    # from. Extensions apply too, but parent.extend_feature() can't reach
    # this object to invalidate the cache - so the cache is also dropped
    # whenever this set changes.
    _cached_feature_ids: tuple[int, ...] = ()
    # Class-relative level currently being applied by
    # BaseClassLevelFeatures.add_features, used to tag each spell/cantrip
    # with the level it was granted on (see set_current_grant_level). Defaults
    # to 1, matching the convention _feature_level uses for features whose
    # origin can't be parsed - this covers spells granted outside the
    # per-level class flow (species spells, origin feat spells via
    # add_origin_feat, etc).
    _current_grant_level: int = 1
    # {class: subclass} for every class that has reached its subclass level,
    # in the order gained - character_subclass shows them joined with " / ".
    # Maintained by ClassBuilder.create (private, so merge_with skips it).
    _active_subclasses: dict[CharacterClass, str] = attr.Factory(dict)

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

    def _invalidate_cache(self):
        """Drop the cached CharacterStatBlock; any mutation after
        setup_character_stat_block() must call this so the next setup call
        rebuilds instead of returning stale state."""
        self._character_cached = None

    def add_feature(self, feature: Feature):
        self._invalidate_cache()
        self.features.append(feature)

    def remove_features(self, should_remove) -> None:
        """Remove every feature for which `should_remove(feature)` is true."""
        self._invalidate_cache()
        self.features = [f for f in self.features if not should_remove(f)]

    def iter_features_with_extensions(self) -> Iterator[Feature]:
        """Every granted feature followed by its extensions (depth-first).
        Extensions are real features: their apply() runs like any other's."""

        def walk(features: list[Feature]) -> Iterator[Feature]:
            for feature in features:
                yield feature
                yield from walk(feature.extensions)

        return walk(self.features)

    def add_origin_feat(self, origin_feat: OriginFeats.OriginFeat):
        self.add_feature(origin_feat)
        for spell in origin_feat.get_spells():
            self.add_spell(spell, origin_feat.get_spell_casting_ability())

    def get_features_by_type(self, feature_type: type) -> list[Any]:
        return [
            feature for feature in self.features if isinstance(feature, feature_type)
        ]

    def get_level_for_class(self, character_class: CharacterClass) -> int:
        return self.level_per_class.get(character_class, 0)

    def record_class_level(self, character_level: int, character_class: CharacterClass):
        self._invalidate_cache()
        self.class_by_character_level[character_level] = character_class

    def set_current_grant_level(self, level: int) -> None:
        """Set the class-relative level that subsequent add_spell/add_cantrip
        calls will be tagged with. Called by BaseClassLevelFeatures.add_features
        right before invoking each per-level add_features method."""
        self._current_grant_level = level

    def add_armor(self, armor: AbstractArmor):
        self._invalidate_cache()
        self.armors.append(armor)

    def add_weapon(self, weapon: AbstractWeapon):
        # Proficiency isn't decided here: the weapon works it out on read
        # against every proficiency on the stat block (AbstractWeapon.is_proficient).
        self._invalidate_cache()
        self.weapons.append(weapon)

    def add_weapon_mastery(self, weapon: AbstractWeapon):
        self._invalidate_cache()
        self.weapon_masteries.append(weapon)

    def add_fighting_style(self, fighting_style: FightingStyle):
        self._invalidate_cache()
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

        if spell in [s[0] for s in self.spells]:
            raise ValueError(f"Spell {spell} already added.")
        self._invalidate_cache()
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
        if cantrip in [s[0] for s in self.spells]:
            raise ValueError(f"Cantrip {cantrip} already added.")
        self._invalidate_cache()
        self.spells.append(
            (
                cantrip,
                spell_casting_ability,
                additional_ruling,
                self._current_grant_level,
            )
        )

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
        self._invalidate_cache()
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self._invalidate_cache()
        self.invocations.append(invocation)

    def add_item(self, item: Items.Item, quantity: int = 1):
        self._invalidate_cache()
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if type(existing_item) is type(item):
                self.items[i] = (existing_item, existing_quantity + quantity)
                return
        self.items.append((item, quantity))

    def validate(self) -> None:
        """Checks that need no evaluation, run by `setup_character_stat_block()`
        before it builds anything: every field a stat block needs is set
        (builders fill them in piecemeal, so most are `Optional` while a
        build is in progress), at most one worn body armor, and the
        attunement limit. Rules that need evaluated stats are checked by
        `CharacterStatBlock.validate()` once every effect has applied."""
        if self.character_name is None:
            raise ValueError("Character name must be set.")
        if self.character_subclass is None:
            raise ValueError("Character subclass must be set.")
        if self.abilities is None:
            raise ValueError("Character abilities must be set.")
        if self.skills is None:
            raise ValueError("Character skills must be set.")
        if self.speed is None:
            raise ValueError("Character speed must be set.")
        if self.size is None:
            raise ValueError("Character size must be set.")
        if self.base_class is None:
            raise ValueError("Character base class must be set.")
        if self.saving_throws is None:
            raise ValueError("Character saving throws must be set.")

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

    def setup_character_stat_block(self) -> CharacterStatBlock:
        features = list(self.iter_features_with_extensions())
        feature_ids = tuple(id(feature) for feature in features)
        if (
            self._character_cached is not None
            and self._cached_feature_ids == feature_ids
        ):
            return self._character_cached

        self.validate()
        # validate() raises if any of these are None; the asserts below just
        # tell the type checker that too.
        assert self.character_name is not None
        assert self.character_subclass is not None
        assert self.abilities is not None
        assert self.skills is not None
        assert self.speed is not None
        assert self.size is not None
        assert self.base_class is not None
        assert self.saving_throws is not None

        combat = CombatStatBlock(
            speed=self.speed,
            size=self.size,
        )
        # Features mutate these sub-blocks in place (ability bonuses, skill
        # proficiencies, ...), so the stat block gets its own copies. Sharing
        # them would re-apply every bonus on the next rebuild after a cache
        # invalidation, and on every build() of the same builder instance
        # (which hands the same AbilitiesStatBlock to each CharacterSheetData).
        character = CharacterStatBlock(
            name=self.character_name,
            character_subclass=self.character_subclass,
            base_class=self.base_class,
            level_per_class=self.level_per_class,
            class_by_character_level=self.class_by_character_level,
            abilities=copy.deepcopy(self.abilities),
            skills=copy.deepcopy(self.skills),
            combat=combat,
            saving_throws=copy.deepcopy(self.saving_throws),
            spell_casting_ability=self.spell_casting_ability,
            spell_slots=self.spell_slots,
            starting_gold=self.starting_gold,
            current_gold=self.current_gold,
        )

        # Ordering contract (see CharacterContent/Features/Core/Improvements.py):
        # every effect only records facts, and every value is worked out when
        # it's read - so features, armor, weapons, items and fighting styles
        # may apply in any order. tests/test_feature_apply_order.py shuffles
        # iter_stat_effects() to prove it.
        for effect in self.iter_stat_effects(features):
            effect.apply(character)

        # Requirements are checked against the complete set of effects,
        # including multiclass ability prerequisites.
        character.validate()

        # These write into the weapon objects, not the stat block, and read
        # nothing from it - their order doesn't matter either.
        for fighting_style in self.fighting_styles:
            if isinstance(fighting_style, FightStyleWeaponFeature):
                fighting_style.apply(self.weapons)
        for item, _quantity in self.items:
            if item.is_wearing is not False:
                item.apply_to_weapons(self.weapons)
        self._character_cached = character
        self._cached_feature_ids = feature_ids

        return character

    def iter_stat_effects(self, features: Optional[list[Feature]] = None) -> list[Any]:
        """Everything that records effects on the stat block: features and
        their extensions, armor, weapons, items and stat fighting styles
        (Defense). Each has apply(character_stat_block); the order is
        irrelevant. (Proficiencies come from features too - e.g.
        ClassProficiencies.)"""
        if features is None:
            features = list(self.iter_features_with_extensions())
        return [
            *features,
            *self.armors,
            *self.weapons,
            *(item for item, _quantity in self.items),
            *(
                style
                for style in self.fighting_styles
                if isinstance(style, FightStyleModifier)
            ),
        ]

    def get_ability_modifier(self, ability: Ability) -> int:
        character = self.setup_character_stat_block()
        return character.abilities.get_modifier(ability)

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        character = self.setup_character_stat_block()
        return character.calculate_attack_bonus_for_ability(ability)

    def merge_with(self, other: "CharacterSheetData"):
        """Merge another CharacterSheetData into this one.

        Merge rules, by field kind:
        - lists (features, spells, weapons, ...) are
          concatenated, preserving each side's internal order with `other`'s
          entries after `self`'s;
        - dicts (level_per_class, spell_slots) are combined with `other`'s
          entries winning on key collisions. For level_per_class this means a
          later builder redeclaring an existing class states that class's
          final total level (e.g. a starter Paladin 1 resumed by a Paladin 19
          builder ends at 19, not 20);
        - sets are combined with set union;
        - scalars are overwritten only when `other`'s value is actually set
          (see _MERGE_EMPTY_VALUES), so an untouched default never erases an
          earlier builder's value.
        """
        self._invalidate_cache()

        for field_name in vars(self):
            if field_name.startswith("_"):
                continue
            other_value = getattr(other, field_name)
            my_value = getattr(self, field_name)

            if isinstance(my_value, list) and isinstance(other_value, list):
                setattr(self, field_name, my_value + other_value)
                continue

            if isinstance(my_value, dict) and isinstance(other_value, dict):
                combined_dict = my_value.copy()
                combined_dict.update(other_value)
                setattr(self, field_name, combined_dict)
                continue

            if isinstance(my_value, set) and isinstance(other_value, set):
                setattr(self, field_name, my_value.union(other_value))
                continue

            if other_value not in _MERGE_EMPTY_VALUES:
                setattr(self, field_name, other_value)

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
