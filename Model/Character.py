"""The one object a character is: the player's decisions and the sources they
grant (features, spells, fighting styles, inventory), plus every stat worked
out from them.

Evaluation is internal and lazy. The first query after any change builds a
fresh Ledger (Model/Effects.py) by applying every feature, armor, weapon,
item and fighting style in iter_stat_effects() to a write-only Effects view of
it, seals it, then answers queries from it until the sources change again. A
version counter decides when that is (see _get_ledger).

The Model package imports nothing from CharacterContent, not even for type
hints: features, fighting styles, armor, weapons and items are named through
the Protocols in Model/Sources.py, so CharacterContent can import the Model
without a cycle.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Callable, Iterator, Literal, Optional, Sequence

import attr

import Core.Definitions as Definitions
from Core.Definitions import Ability, CharacterClass, Skill
from Core.SpellcastingRules import SlotProgression
from Model.AbilityScores import AbilityScores, ability_modifier
from Model.ClassLevels import ClassLevels
from Model.Effects import Effects, Ledger
from Model.Inventory import Inventory
from Model.Sources import ArmorGear, Effect, Gear, GrantedFeature

MAX_ATTUNED_ITEMS = 3


@attr.s(frozen=True, auto_attribs=True, eq=False)
class FeatureExtension:
    """A feature granted as an extension of another: a rider or upgrade that
    shows on its parent's card and applies like any other feature. Declared,
    not attached - the parent is found when the character is read, so parent
    and extension may be granted in either order.

    parent: a feature type, matched with isinstance against the granted
    top-level features (exactly one must match), or a granted feature
    instance. if_missing: what happens when no parent is granted -
    "error" (the default), "drop" (an upgrade to whichever of two choices
    was made) or "standalone" (shown as a feature of its own)."""

    feature: GrantedFeature
    parent: type | GrantedFeature
    if_missing: Literal["error", "drop", "standalone"] = "error"


def _in_given_order(effects: list[Effect]) -> list[Effect]:
    return effects


def _count_change(character: "Character", attribute: Any, value: Any) -> Any:
    """attrs on_setattr hook: assigning any public field is a change to the
    character's sources."""
    if not attribute.name.startswith("_"):
        object.__setattr__(character, "_version", character._version + 1)
    return value


class SpellSource:
    """Shared `source=` labels for add_spell/add_cantrip (any free text works)."""

    CHOSEN = "Chosen spell"


@attr.s(auto_attribs=True, on_setattr=_count_change)
class Character:
    character_name: Optional[str] = None
    is_example: bool = False
    # Levels, level-by-level history, base class and subclasses - see
    # Model/ClassLevels.py. character_subclass/base_class/
    # level_per_class/class_by_character_level below are thin delegating
    # properties kept for the many existing readers of those names.
    class_levels: ClassLevels = attr.Factory(ClassLevels)
    # The player's ability scores before any increase - immutable; the final
    # scores are get_ability_score() (see Model/AbilityIncreases.py).
    base_abilities: Optional[AbilityScores] = None
    # Walking speed given by the species, before any bonus (see
    # calculate_speed).
    base_speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None

    # Every feature in the order it was granted. The order only decides how
    # the sheet lists them: no stat depends on it (see _get_ledger).
    features: list[GrantedFeature] = attr.Factory(list)
    # Features granted as extensions of others (add_feature(..., extends=)),
    # in the order they were declared - see extensions_of().
    feature_extensions: list[FeatureExtension] = attr.Factory(list)
    invocations: list[str] = attr.Factory(list)
    spells: list[tuple[str, Ability, Optional[str], int]] = attr.Factory(list)
    # Optional free-text "where did I get this spell" (e.g. "Chosen spell"),
    # keyed by the entry's index in `spells`; absent means untagged. Kept
    # beside `spells` so that tuple's shape is unchanged - read it with
    # get_spell_source().
    spell_sources: dict[int, str] = attr.Factory(dict)
    spell_casting_ability: Optional[Ability] = None
    # Spell slots set outright rather than worked out from caster levels.
    fixed_spell_slots: dict[int, int] = attr.Factory(dict)

    weapon_masteries: list[Gear] = attr.Factory(list)
    fighting_styles: list[Effect] = attr.Factory(list)
    # Armor, weapons and items, grouped into labeled entries (Starting
    # Equipment, then adventuring gear added later), plus starting and
    # current gold - see Model/Inventory.py. CharacterBuilder.build()
    # gives each character its own copy of the builder's inventory.
    # armors/weapons/items below are its flat views, which AC, attacks and
    # carrying capacity read.
    inventory: Inventory = attr.Factory(Inventory)
    experience_points: int = 0
    # Effects granted on their own rather than by a feature or gear: a test
    # or tool recording one improvement on a bare character (add_effect).
    extra_effects: list[Effect] = attr.Factory(list)

    # Goes up on every change to the sources above (every add_*/set_* call,
    # and any field assignment - see _count_change). Together with the
    # inventory's own version and _apply_order it
    # decides when the cached evaluation is out of date.
    _version: int = attr.ib(default=0, init=False, eq=False, repr=False)
    _ledger: Optional[Ledger] = attr.ib(default=None, init=False, eq=False, repr=False)
    _ledger_key: Optional[tuple[Any, ...]] = attr.ib(
        default=None, init=False, eq=False, repr=False
    )
    # ({id(parent): [extension, ...]}, [standalone extension, ...]),
    # resolved from feature_extensions and cached under the version it was
    # resolved at.
    _extension_tree: Optional[
        tuple[dict[int, list[GrantedFeature]], list[GrantedFeature]]
    ] = attr.ib(default=None, init=False, eq=False, repr=False)
    _extension_tree_version: int = attr.ib(default=-1, init=False, eq=False, repr=False)
    # The order iter_stat_effects() applies in: as listed, unless a test
    # reorders it to prove the order doesn't matter (tests/
    # test_feature_apply_order.py, tests/test_order_invariance.py).
    _apply_order: Callable[[list[Effect]], list[Effect]] = attr.ib(
        default=_in_given_order, init=False, eq=False, repr=False
    )
    # Class-relative level currently being applied by
    # BaseClassLevelFeatures.add_features, used to tag each spell/cantrip
    # with the level it was granted on (see set_current_grant_level). Defaults
    # to 1, matching the convention _feature_level uses for features whose
    # origin can't be parsed - this covers spells granted outside the
    # per-level class flow (species spells, origin feat spells via
    # grant_origin_feat, etc).
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
    def armors(self) -> list[ArmorGear]:
        return self.inventory.armors

    @property
    def weapons(self) -> list[Gear]:
        return self.inventory.weapons

    @property
    def items(self) -> list[tuple[Gear, int]]:
        """(item, quantity), with same-type stacks merged."""
        return self.inventory.items

    def add_feature(
        self,
        feature: GrantedFeature,
        extends: type | GrantedFeature | None = None,
        if_missing: Literal["error", "drop", "standalone"] = "error",
    ):
        """Grant `feature` - or, with `extends`, grant it as an extension of
        that feature (a type, or a feature instance): see FeatureExtension."""
        if extends is None:
            if if_missing != "error":
                raise ValueError("if_missing only applies with extends=.")
            self.features.append(feature)
        else:
            self.feature_extensions.append(
                FeatureExtension(feature, extends, if_missing)
            )
        self._changed()

    def top_level_features(self) -> list[GrantedFeature]:
        """The features with a card of their own: every plain grant, then
        every "standalone" extension whose parent isn't granted."""
        return [*self.features, *self._resolved_extensions()[1]]

    def extensions_of(self, feature: GrantedFeature) -> list[GrantedFeature]:
        """The extensions granted onto `feature`, in the order they were
        declared."""
        return list(self._resolved_extensions()[0].get(id(feature), []))

    def iter_features_with_extensions(self) -> Iterator[GrantedFeature]:
        """Every granted feature followed by its extensions (depth-first).
        Extensions are real features: their apply() runs like any other's."""
        tree = self._resolved_extensions()[0]

        def walk(features: Sequence[GrantedFeature]) -> Iterator[GrantedFeature]:
            for feature in features:
                yield feature
                yield from walk(tree.get(id(feature), []))

        return walk(self.top_level_features())

    def _resolved_extensions(
        self,
    ) -> tuple[dict[int, list[GrantedFeature]], list[GrantedFeature]]:
        """({id(parent): [extension, ...]}, [standalone extension, ...]) for
        every declared extension. Raises if an extension's parent isn't
        granted (unless if_missing says otherwise), or if a parent type
        matches more than one granted feature."""
        if self._extension_tree_version == self._version:
            assert self._extension_tree is not None
            return self._extension_tree
        granted = {id(f) for f in self.features} | {
            id(e.feature) for e in self.feature_extensions
        }
        tree: dict[int, list[GrantedFeature]] = {}
        standalone: list[GrantedFeature] = []
        for extension in self.feature_extensions:
            parent = self._extension_parent(extension, granted)
            if parent is not None:
                tree.setdefault(id(parent), []).append(extension.feature)
            elif extension.if_missing == "standalone":
                standalone.append(extension.feature)
        self._extension_tree = (tree, standalone)
        self._extension_tree_version = self._version
        return self._extension_tree

    def _extension_parent(
        self, extension: FeatureExtension, granted: set[int]
    ) -> Optional[GrantedFeature]:
        if isinstance(extension.parent, type):
            label = extension.parent.__name__
            matches = [f for f in self.features if isinstance(f, extension.parent)]
        else:
            label = extension.parent.name
            matches = [extension.parent] if id(extension.parent) in granted else []
        if len(matches) > 1:
            raise ValueError(
                f"{extension.feature.name} extends {label}, but {len(matches)} "
                "granted features match it - extend a specific instance instead."
            )
        if matches:
            return matches[0]
        if extension.if_missing != "error":
            return None
        raise ValueError(
            f"{extension.feature.name} extends {label}, which isn't granted."
        )

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

    def add_armor(self, armor: ArmorGear):
        """Add armor outside starting equipment and adventuring gear (see
        Inventory.add_armor)."""
        self.inventory.add_armor(armor)

    def add_weapon(self, weapon: Gear):
        # Proficiency isn't decided here: the weapon works it out on read
        # against every proficiency (AbstractWeapon.is_proficient).
        self.inventory.add_weapon(weapon)

    def add_weapon_mastery(self, weapon: Gear):
        self._changed()
        self.weapon_masteries.append(weapon)

    def add_fighting_style(self, fighting_style: Effect):
        self._changed()
        self.fighting_styles.append(fighting_style)

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
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
        if source is not None:
            self.spell_sources[len(self.spells) - 1] = source

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
        source: Optional[str] = None,
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
        if source is not None:
            self.spell_sources[len(self.spells) - 1] = source

    def get_spell_source(
        self, spell_entry: tuple[str, Ability, Optional[str], int]
    ) -> Optional[str]:
        """Where the character got this entry of `spells`, or None. Matched by
        identity, so the same spell granted twice (e.g. by class and species)
        keeps each grant's own source."""
        for index, entry in enumerate(self.spells):
            if entry is spell_entry:
                return self.spell_sources.get(index)
        return None

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
        # Positions are unchanged, so the replacement keeps the old spell's
        # source (a swapped chosen spell is still a chosen spell).
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self._changed()
        self.invocations.append(invocation)

    def add_item(self, item: Gear, quantity: int = 1):
        self.inventory.add_item(item, quantity)

    def add_effect(self, effect: Effect) -> None:
        """Grant an effect on its own (anything with apply(effects)), for a
        test or tool recording one improvement on a bare character."""
        self._changed()
        self.extra_effects.append(effect)

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

    def iter_stat_effects(
        self, features: Optional[list[GrantedFeature]] = None
    ) -> list[Effect]:
        """Everything that records effects: features and their extensions,
        armor, weapons, items, fighting styles (only those with a computed
        effect - Defense, Archery, Dueling, ... - record anything) and extra
        effects. Each has apply(effects);
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
            *self.fighting_styles,
            *self.extra_effects,
        ]

    def _get_ledger(self) -> Ledger:
        """The evaluated, sealed Ledger: cached, and rebuilt from the sources
        on the first query after any change to them. Requirements aren't
        checked here - validate() does that, against the complete set of
        effects."""
        key = (
            self._version,
            self.inventory.version,
            self._apply_order,
        )
        if self._ledger is not None and self._ledger_key == key:
            return self._ledger

        if self.base_abilities is None:
            raise ValueError("Character abilities must be set.")
        if self.base_speed is None:
            raise ValueError("Character speed must be set.")
        if self.base_class is None:
            raise ValueError("Character base class must be set.")

        ledger = Ledger()
        effects = Effects(ledger)
        try:
            # Ordering contract (see CharacterContent/Features/Core/Improvements.py):
            # every effect only records facts - Effects is write-only - and
            # every value is worked out when it's read, so features, armor,
            # weapons, items and fighting styles may apply in any order.
            # tests/test_feature_apply_order.py reorders them (_apply_order)
            # to prove it.
            for effect in self._apply_order(self.iter_stat_effects()):
                effect.apply(effects)
        except BaseException:
            self._ledger = None
            raise
        ledger.seal()
        self._ledger, self._ledger_key = ledger, key
        return ledger

    def _validate_sources(self) -> None:
        """Checks that need no evaluation: every field a finished character
        needs is set (builders fill them in piecemeal, so most are Optional
        while a build is in progress), at most one worn body armor, the
        attunement limit, and that every extension's parent is granted."""
        self._resolved_extensions()
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

    def validate(self) -> "Character":
        """The single validation entry point: the sources (required fields,
        one worn armor, attunement), then every requirement against the
        complete set of effects (expertise needs proficiency, an armor's
        Strength, multiclass ability minimums). Returns the character, so a
        build can be checked inline: `builder.build().validate()`."""
        self._validate_sources()
        self._get_ledger().validate(self)
        return self

    # ── The evaluated record ─────────────────────────────────────────────────

    @property
    def ledger(self) -> Ledger:
        """What every effect recorded, one part per concern (Model/Effects.py):
        evaluated on demand and sealed, so it can be read but never written.
        Final values are the queries below, which hand this character to the
        parts' resolvers."""
        return self._get_ledger()

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def is_wearing_armor(self) -> bool:
        """Wearing Light, Medium or Heavy armor (a shield alone doesn't count)."""
        return self.ledger.worn_armor.is_wearing_armor

    @property
    def worn_armor_type(self) -> Optional[Definitions.ArmorType]:
        """The worn body armor's type (None without body armor)."""
        return self.ledger.worn_armor.body_armor_type

    @property
    def is_wielding_shield(self) -> bool:
        return self.ledger.worn_armor.shield_wielded

    @property
    def spell_slots(self) -> Optional[dict[int, int]]:
        return self.ledger.spellcasting.spell_slots(self)

    @property
    def pact_magic_slots(self) -> dict[int, int]:
        return self.ledger.spellcasting.pact_magic_slots(self)

    def get_slot_progression(self, max_level: int = 20) -> Optional[SlotProgression]:
        """When each of this character's slots is gained, up to character
        level `max_level`: the levels taken so far follow the classes
        actually taken, and later levels carry on in the most recently taken
        class. None when the class taken at some level isn't recorded."""
        taken = [
            self.class_by_character_level.get(level)
            for level in range(1, self.character_level + 1)
        ]
        if not taken or None in taken:
            return None
        class_path = taken + [taken[-1]] * (max_level - len(taken))
        return self.ledger.spellcasting.slot_progression(class_path)

    @property
    def initiative_roll_condition(self) -> Definitions.DiceRollCondition:
        return self.ledger.initiative.roll_condition(self)

    # -- Armor training (2024 PHB) - see Ledger ---------------------------------

    @property
    def is_wearing_untrained_armor(self) -> bool:
        return self._get_ledger().is_wearing_untrained_armor()

    @property
    def has_shield_training(self) -> bool:
        return self._get_ledger().has_shield_training()

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        """Disadvantage on D20 Tests with `ability` from untrained armor."""
        return self._get_ledger().has_untrained_armor_disadvantage(ability)

    @property
    def warnings(self) -> list[str]:
        """Legal but bad choices the player should know about."""
        return self._get_ledger().armor_warnings()

    def calculate_initiative(self) -> int:
        return self.ledger.initiative.total(self)

    def calculate_speed(self) -> int:
        return self.ledger.speed.total(self)

    def get_carrying_capacity_sources(self) -> list[tuple[str, int]]:
        """Returns all carrying capacity sources, including the dynamic 'Person' base."""
        return self.ledger.carrying_capacity.sources(self)

    def get_carrying_capacity(self) -> int:
        """Returns the total carrying capacity in item slots (base 3 + STR mod + bonuses)."""
        return self.ledger.carrying_capacity.total(self)

    def _require_spell_casting_ability(self) -> Ability:
        if self.spell_casting_ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        return self.spell_casting_ability

    # ── Sources, read through StatView ───────────────────────────────────────

    def get_base_ability_score(self, ability: Ability) -> int:
        """The player's score before any increase."""
        if self.base_abilities is None:
            raise ValueError("Character abilities must be set.")
        return self.base_abilities.get_score(ability)

    def get_base_speed(self) -> int:
        if self.base_speed is None:
            raise ValueError("Character speed must be set.")
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
        return 2 + (self.character_level - 1) // 4

    def get_ability_score(self, ability: Ability) -> int:
        """The final score: base, every capped increase and equipment bonuses."""
        return self._get_ledger().ability_increases.score(ability, self)

    def get_own_ability_score(self, ability: Ability) -> int:
        """The score without equipment bonuses - what an armor's Strength
        requirement or a multiclass minimum checks."""
        return self._get_ledger().ability_increases.own_score(ability, self)

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
        return self.ledger.skills.is_proficient(skill)

    def has_expertise_in_skill(self, skill: Skill) -> bool:
        return self.ledger.skills.has_expertise(skill)

    def get_skill_ability(self, skill: Skill) -> Ability:
        return self.ledger.skills.ability(skill, self)

    def get_skill_modifier(self, skill: Skill) -> int:
        return self.ledger.skills.modifier(skill, self)

    def get_skill_bonus(self, skill: Skill) -> int:
        return self.ledger.skills.get_total_bonus(skill, self)

    def get_skill_bonus_sources(self, skill: Skill) -> list[tuple[int, str]]:
        return self.ledger.skills.get_all_bonus_sources(skill, self)

    def is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        return self.ledger.saving_throws.is_proficient(ability)

    def has_advantage_in_saving_throw(self, ability: Ability) -> bool:
        return self.ledger.saving_throws.is_advantaged(ability)

    def get_saving_throw_roll_condition(
        self, ability: Ability
    ) -> Definitions.DiceRollCondition:
        return self.ledger.saving_throws.roll_condition(ability, self)

    def get_skill_roll_condition(self, skill: Skill) -> Definitions.DiceRollCondition:
        return self.ledger.skills.roll_condition(skill, self)

    def get_skill_roll_condition_reasons(self, skill: Skill) -> list[str]:
        return self.ledger.skills.roll_condition_reasons(skill, self)

    def get_saving_throw_modifier(self, ability: Ability) -> int:
        return self.ledger.saving_throws.modifier(ability, self)

    def calculate_hit_points(self) -> int:
        return self.ledger.hit_points.total(self)

    def calculate_armor_class(self, ignore_shield: bool = False) -> int:
        """The best applicable AC formula plus every AC bonus. ignore_shield:
        the AC with the Shield set aside (its bonus gone, and formulas it
        disables - Monk's Unarmored Defense - available again)."""
        return self.ledger.armor_class.total(self, ignore_shield)

    def get_spell_casting_ability(self) -> Ability:
        return self._require_spell_casting_ability()

    def calculate_difficulty_class(self) -> int:
        return self.calculate_difficulty_class_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int:
        return self.ledger.spellcasting.difficulty_class(ability, self)

    @property
    def spell_save_dc_bonus(self) -> int:
        """Flat bonus to the spell save DC on top of 8 + ability modifier +
        proficiency bonus (e.g. from an item)."""
        return self.ledger.spellcasting.spell_save_dc_bonus

    def calculate_attack_bonus(self) -> int:
        return self.calculate_attack_bonus_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        return self.ledger.spellcasting.attack_bonus(ability, self)

    def get_spell_slots(self) -> dict[int, int]:
        spell_slots = self.spell_slots
        if spell_slots is None:
            raise ValueError("Character does not have spell slots.")
        return spell_slots

    def is_resistant_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return self.ledger.defenses.is_resistant_to_damage(damage_type)

    def is_immune_to_damage(self, damage_type: Definitions.DamageType) -> bool:
        return self.ledger.defenses.is_immune_to_damage(damage_type)

    def get_damage_resistance_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self.ledger.defenses.get_damage_resistance_sources(damage_type)

    def get_damage_immunity_sources(
        self, damage_type: Definitions.DamageType
    ) -> list[str]:
        return self.ledger.defenses.get_damage_immunity_sources(damage_type)

    def is_immune_to_condition(self, condition: Definitions.Condition) -> bool:
        return self.ledger.defenses.is_immune_to_condition(condition)

    def get_condition_immunity_sources(
        self, condition: Definitions.Condition
    ) -> list[str]:
        return self.ledger.defenses.get_condition_immunity_sources(condition)

    def get_sense_range(self, sense: Definitions.Sense) -> int:
        return self.ledger.senses.get_sense_range(sense)

    def get_sense_sources(self, sense: Definitions.Sense) -> list[tuple[int, str]]:
        return self.ledger.senses.get_sense_sources(sense)

    def knows_language(self, language: Definitions.Language) -> bool:
        return self.ledger.languages.knows(language)

    def get_language_sources(self, language: Definitions.Language) -> list[str]:
        return self.ledger.languages.sources(language)
