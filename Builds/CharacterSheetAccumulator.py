import copy
from contextlib import contextmanager
from typing import Any, Iterator, Optional

import attr

import Core.Definitions as Definitions
from Builds.Inventory import Inventory
from CharacterContent.Features.CharacterFeats import OriginFeats
from CharacterContent.Features.CombatFeatures.FightingStyles import (
    FightingStyle,
    FightStyleModifier,
)
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Items import Items
from CharacterContent.Items.Armor import AbstractArmor
from CharacterContent.Items.Weapons import AbstractWeapon
from Core.Definitions import Ability, CharacterClass
from StatBlocks.AbilityScores import AbilityScores
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.ClassLevels import ClassLevels
from StatBlocks.Spellcasting import Spellcasting

MAX_ATTUNED_ITEMS = 3


@attr.dataclass
class CharacterSheetData:
    character_name: Optional[str] = None
    is_example: bool = False
    # Levels, level-by-level history, base class and subclasses - shared
    # (not copied) with the CharacterStatBlock built from this sheet, see
    # StatBlocks/ClassLevels.py. character_subclass/base_class/
    # level_per_class/class_by_character_level below are thin delegating
    # properties kept for the many existing readers of those names.
    class_levels: ClassLevels = attr.Factory(ClassLevels)
    abilities: Optional[AbilityScores] = None
    speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None

    # Every feature in the order it was granted. The order only decides how
    # the sheet lists them: no stat depends on it (see
    # setup_character_stat_block).
    features: list[Feature] = attr.Factory(list)
    invocations: list[str] = attr.Factory(list)
    spells: list[tuple[str, Ability, Optional[str], int]] = attr.Factory(list)
    spell_casting_ability: Optional[Ability] = None

    spell_slots: dict[int, int] = attr.Factory(dict)

    weapon_masteries: list[AbstractWeapon] = attr.Factory(list)
    fighting_styles: list[FightingStyle] = attr.Factory(list)
    # Armor, weapons and items, grouped into labeled entries (Starting
    # Equipment, then adventuring gear added later), plus starting and
    # current gold - see Builds/Inventory.py. CharacterBuilder.build() gives
    # each sheet its own copy of the builder's inventory. armors/weapons/items
    # below are its flat views, which AC, attacks and carrying capacity read.
    inventory: Inventory = attr.Factory(Inventory)
    experience_points: int = 0
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
    # Index into spells where the duplicate check starts - see
    # separate_spell_source.
    _duplicate_spell_check_start: int = 0

    @property
    def character_subclass(self) -> Optional[str]:
        return self.class_levels.character_subclass

    @character_subclass.setter
    def character_subclass(self, value: Optional[str]) -> None:
        self.class_levels.character_subclass = value

    @property
    def base_class(self) -> Optional[CharacterClass]:
        return self.class_levels.base_class

    @base_class.setter
    def base_class(self, value: Optional[CharacterClass]) -> None:
        self.class_levels.base_class = value

    @property
    def level_per_class(self) -> dict[CharacterClass, int]:
        return self.class_levels.level_per_class

    @level_per_class.setter
    def level_per_class(self, value: dict[CharacterClass, int]) -> None:
        self.class_levels.level_per_class = value

    @property
    def class_by_character_level(self) -> dict[int, CharacterClass]:
        return self.class_levels.class_by_character_level

    @class_by_character_level.setter
    def class_by_character_level(self, value: dict[int, CharacterClass]) -> None:
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
    def items(self) -> list[tuple[Items.Item, int]]:
        """(item, quantity), with same-type stacks merged."""
        return self.inventory.items

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
        return self.class_levels.get_class_level(character_class)

    def record_class_level(self, character_level: int, character_class: CharacterClass):
        self._invalidate_cache()
        self.class_levels.record_class_level(character_level, character_class)

    def set_class_level(self, character_class: CharacterClass, level: int) -> None:
        """Set the character's total level in `character_class` (a builder
        resuming a class states the class's final total level)."""
        self._invalidate_cache()
        self.class_levels.level_per_class[character_class] = level

    def set_current_grant_level(self, level: int) -> None:
        """Set the class-relative level that subsequent add_spell/add_cantrip
        calls will be tagged with. Called by BaseClassLevelFeatures.add_features
        right before invoking each per-level add_features method."""
        self._current_grant_level = level

    def add_armor(self, armor: AbstractArmor):
        """Add armor outside starting equipment and adventuring gear (see
        Inventory.add_armor)."""
        self._invalidate_cache()
        self.inventory.add_armor(armor)

    def add_weapon(self, weapon: AbstractWeapon):
        # Proficiency isn't decided here: the weapon works it out on read
        # against every proficiency on the stat block (AbstractWeapon.is_proficient).
        self._invalidate_cache()
        self.inventory.add_weapon(weapon)

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

        if spell in self._spell_names_checked_for_duplicates():
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
        if cantrip in self._spell_names_checked_for_duplicates():
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
        self._invalidate_cache()
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self._invalidate_cache()
        self.invocations.append(invocation)

    def add_item(self, item: Items.Item, quantity: int = 1):
        self._invalidate_cache()
        self.inventory.add_item(item, quantity)

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
        if self.speed is None:
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
        assert self.speed is not None
        assert self.size is not None
        assert self.base_class is not None

        # Skills, saving throws and every other part hold no state of their
        # own here - every proficiency, expertise and bonus arrives as a
        # feature effect (e.g. ClassProficiencies, ClassSkillChoice,
        # FreeBackgroundSkillProficiency), so the stat block always starts
        # them empty (CharacterStatBlock.__init__). Abilities are still an
        # accumulator field (base scores are a build choice, not a feature
        # grant), and get their own deep copy: features mutate it in place, and
        # sharing the accumulator's instance would re-apply every bonus on the
        # next rebuild after a cache invalidation, or on every build() of the
        # same builder instance (which hands the same AbilityScores to
        # each CharacterSheetData).
        character = CharacterStatBlock(
            # Shared, not copied - see StatBlocks/ClassLevels.py. Name, gold
            # and size stay on this CharacterSheetData only; readers that need
            # them (the sheet writer) already have it.
            class_levels=self.class_levels,
            abilities=copy.deepcopy(self.abilities),
            speed=self.speed,
            spellcasting=Spellcasting(
                ability=self.spell_casting_ability, fixed_slots=self.spell_slots
            ),
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

        self._character_cached = character
        self._cached_feature_ids = feature_ids

        return character

    def iter_stat_effects(self, features: Optional[list[Feature]] = None) -> list[Any]:
        """Everything that records effects on the stat block: features and
        their extensions, armor, weapons, items and fighting styles with a
        computed effect (Defense, Archery, Dueling, ...). Each has
        apply(character_stat_block); the order is irrelevant. (Proficiencies
        come from features too - e.g. ClassProficiencies.) Weapons are never
        changed: bonuses the wielder brings to them are recorded in
        character_stat_block.weapon_bonuses."""
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
