"""When one feature changes what using another feature, or casting a spell,
does in a fight: Mindless Rage's Rage gives Immunity to Charmed and
Frightened, Empowered Evocation adds the Intelligence modifier to one
damage roll of an Evocation spell, Supreme Healing uses the dice's highest
number (Notes/combat-effects-plan.md, Phase 10).

A feature says it as data, `Feature.combat_adjustments(character)`: a tuple
of `Adjustment`s, each naming what it `applies` to (its parent, other
features by class, spells that match) and the `changes` it makes. Nothing
here knows feature or spell names, and no feature walks another's effect by
hand: `adjusted` finds every adjustment of a character that applies to one
of its rows and makes the changes, in a fixed order that doesn't depend on
the order the features were granted in (as apply() doesn't):

1. DROP: what an adjustment takes away from the source's own effect (Roving
   Aim: Steady Aim no longer sets Speed to 0). Only from the source's own
   effect, so it never takes away what another adjustment adds.
2. SET: what an adjustment sets (Supreme Healing's highest numbers, an
   action changed). Each says how two of its kind combine (the same twice
   is once); two that can't combine are refused.
3. ADD: notes, damage, healing, a badge's modifiers, the conditions it
   ends, by the adjusting feature's name.

Every reader of a character's effects goes through `adjusted`: the picker's
rows (spells, features, extensions, triggered rows) and the badges given
straight from a card's Use or Cast button.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, ClassVar, Iterable, Protocol

from Core.Definitions import CharacterClass, Condition, DamageType
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
)
from Model.Content.CombatModifiers import Modifier

if TYPE_CHECKING:
    from CharacterContent.Spells.SpellFactory.Enums import School


class Rows(StrEnum):
    """Which of a source's rows an adjustment applies to."""

    # The use or casting itself (CombatEffect.spends_use): Empowered
    # Evocation's "when you cast", not Witch Bolt's later turns.
    CASTING = "casting"
    # Every row, later turns' too (Radiant Soul: "once per turn").
    ALL = "all"


@dataclass(frozen=True)
class Spells:
    """The spells an adjustment applies to: their casting with a slot, or a
    feature's casting of them (a row with `spell=`), unless `with_slot`."""

    school: "School | None" = None
    on_list: CharacterClass | None = None  # on that class's spell list
    min_level: int = 0
    max_level: int = 9
    # Only cast with a spell slot (Disciple of Life), not a feature's free
    # casting.
    with_slot: bool = False

    def __post_init__(self):
        if not 0 <= self.min_level <= self.max_level <= 9:
            raise ValueError(
                f"levels {self.min_level}-{self.max_level} aren't 0-9, lowest first"
            )

    def match(self, spell: "SpellLike", with_slot: bool) -> bool:
        if self.with_slot and not with_slot:
            return False
        if not self.min_level <= spell.level <= self.max_level:
            return False
        if self.school is not None and spell.school != self.school.value:
            return False
        if self.on_list is not None and self.on_list.value not in spell.classes:
            return False
        return True


@dataclass(frozen=True)
class Applies:
    """What an adjustment changes: its `parent`'s rows (the feature it's
    granted as an extension of: Mindless Rage's Rage), rows of `features`
    (by class: Arcane Charge's Action Surge), or castings of `spells`; any
    of them, when several are given. Then only the rows that deal one of
    `deals` (or let it be chosen) and, with `heals`, restore Hit Points."""

    parent: bool = False
    features: tuple[type, ...] = ()
    spells: Spells | None = None
    deals: tuple[DamageType, ...] = ()
    heals: bool = False
    rows: Rows = Rows.CASTING

    def __post_init__(self):
        if not (self.parent or self.features or self.spells):
            raise ValueError("Applies needs parent, features or spells")

    def match(
        self, source: "EffectSource", adjuster, sheet, effect: CombatEffect
    ) -> bool:
        if self.rows is Rows.CASTING and not effect.spends_use:
            return False
        if self.deals and not _deals_any(effect, self.deals):
            return False
        if self.heals and effect.healing is None:
            return False
        return (
            (
                self.parent
                and source.feature is not None
                and any(e is adjuster for e in sheet.extensions_of(source.feature))
            )
            or (
                source.feature is not None
                and bool(self.features)
                and isinstance(source.feature, self.features)
            )
            or (
                self.spells is not None
                and source.spell is not None
                and self.spells.match(source.spell, source.with_slot)
            )
        )


# The adjustment a rider gives its parent most often.
PARENT = Applies(parent=True)


class Phase(IntEnum):
    DROP = 0
    SET = 1
    ADD = 2


@dataclass(frozen=True)
class AdjustContext:
    """What a change is made for: the character, the source of the row, and
    the adjusting feature's name (for notes)."""

    character: object
    source: "EffectSource"
    by: str


class Change:
    """One change to an effect. `phase` says when it's made; a SET change
    also says how two of its kind combine (`merge`)."""

    phase: ClassVar[Phase]

    def make(self, effect: CombatEffect, context: AdjustContext) -> CombatEffect:
        raise NotImplementedError


# DROP ---------------------------------------------------------------------


@dataclass(frozen=True)
class DropModifier(Change):
    """The source's badge (its own name, or `badge`) no longer gives
    modifiers of `kind` (Roving Aim: Steady Aim's Speed(set_to=0))."""

    kind: type
    badge: str = ""
    phase: ClassVar[Phase] = Phase.DROP

    def make(self, effect, context):
        name = self.badge or context.source.name
        return replace(
            effect,
            conditions=tuple(
                (
                    replace(
                        c,
                        modifiers=tuple(
                            m for m in c.modifiers if not isinstance(m, self.kind)
                        ),
                    )
                    if c.name == name
                    else c
                )
                for c in effect.conditions
            ),
        )


# SET ----------------------------------------------------------------------


_AMOUNT = re.compile(r"(?:(\d+d\d+)(?: ([+-]) (\d+))?|(\d+))")


def _split(amount: str) -> tuple[str, int]:
    """An amount ("2d8 + 3", "1d8 - 1", "5", "") as its dice and its flat
    part: ("2d8", 3), ("1d8", -1), ("", 5), ("", 0)."""
    if not amount:
        return "", 0
    match = _AMOUNT.fullmatch(amount)
    if match is None:
        raise ValueError(f"{amount!r} is not dice like '2d8 + 3' or a number")
    dice, sign, flat, number = match.groups()
    if number is not None:
        return "", int(number)
    return dice, (int(flat) if sign == "+" else -int(flat)) if flat else 0


def _join(dice: str, flat: int) -> str:
    """The amount written from its dice and flat part, as the model writes
    amounts: "2d8 + 3", "1d8 - 1", "2d8", "5"."""
    if not dice:
        return str(flat)
    if not flat:
        return dice
    return f"{dice} {'+' if flat > 0 else '-'} {abs(flat)}"


def _plus(amount: str, number: int) -> str:
    """`amount` with `number` more: "2d8" and 3 is "2d8 + 3", "2d8 + 3" and
    3 is "2d8 + 6", "" and 3 is "3"."""
    dice, flat = _split(amount)
    return _join(dice, flat + number)


def _highest(amount: str) -> str:
    """An amount at its dice's highest number: "2d8 + 3" is "19"."""
    dice, flat = _split(amount)
    if not dice:
        return amount
    count, sides = map(int, dice.split("d"))
    return str(count * sides + flat)


@dataclass(frozen=True)
class MaximizeDice(Change):
    """The dice of its healing (Supreme Healing) or damage (Overchannel)
    aren't rolled: each is its highest number, the slot's extra dice too.
    The same twice is once."""

    healing: bool = False
    damage: bool = False
    phase: ClassVar[Phase] = Phase.SET

    def __post_init__(self):
        if not (self.healing or self.damage):
            raise ValueError("MaximizeDice needs healing or damage")

    def make(self, effect, context):
        changes = {}
        if self.healing:
            for name in ("healing", "temp_hp"):
                points = getattr(effect, name)
                if points is not None and points.dice:
                    changes[name] = replace(
                        points,
                        dice=_highest(points.dice),
                        upcast=_highest(points.upcast),
                    )
        if self.damage and effect.damage:
            changes["damage"] = tuple(
                replace(
                    part,
                    dice=_highest(part.dice),
                    upcast=_highest(part.upcast),
                    cantrip=tuple((lvl, _highest(d)) for lvl, d in part.cantrip),
                )
                for part in effect.damage
            )
        return replace(effect, **changes) if changes else effect


@dataclass(frozen=True)
class CostsAction(Change):
    """Using it takes `action` instead (a casting as a Bonus Action). When
    two features set different actions on one row, the first by name
    counts and the row says so (`_settle_sets`)."""

    action: ActionType
    phase: ClassVar[Phase] = Phase.SET

    def make(self, effect, context):
        return replace(effect, action_type=self.action)


# ADD ----------------------------------------------------------------------


@dataclass(frozen=True)
class AddNote(Change):
    """A note on the row (Combat Inspiration's two more ways to spend the
    die), after its own."""

    text: str
    phase: ClassVar[Phase] = Phase.ADD

    def make(self, effect, context):
        return replace(effect, notes=effect.notes + (self.text,))


@dataclass(frozen=True)
class AddDamage(Change):
    """A damage part more."""

    part: CombatDamage
    phase: ClassVar[Phase] = Phase.ADD

    def make(self, effect, context):
        return replace(effect, damage=effect.damage + (self.part,))


@dataclass(frozen=True)
class AddToOneDamageRoll(Change):
    """`amount` more on one damage roll of the row, of the type of a part it
    deals (one of `damage_types`, if given): Empowered Evocation's
    Intelligence modifier, Elemental Affinity's Charisma modifier on a spell
    dealing its type. Where the type is the caster's to choose, it counts
    only if that type is chosen; where several types could take it, the
    GM picks. Only against some targets: `when` (Radiant Soul's "one of its
    targets"). A row of several instances (Magic Missile's darts) gets a
    note instead: the amount would count for each. Nothing for an amount of
    0 or less."""

    amount: int
    damage_types: tuple[DamageType, ...] = ()
    when: str = ""
    phase: ClassVar[Phase] = Phase.ADD

    def make(self, effect, context):
        if self.amount <= 0:
            return effect
        parts = [part for part in effect.damage if not part.when]
        wanted = set(self.damage_types)
        dealt = _unique(
            part.damage_type
            for part in parts
            if part.damage_type is not None
            and (not wanted or part.damage_type in wanted)
        )
        chosen = _unique(
            choice
            for part in parts
            if part.damage_type is None
            for choice in part.choices
            if not wanted or choice in wanted
        )
        if not dealt and not chosen:
            return effect
        if effect.instances is not None:
            noun = effect.instances.noun
            roll = f"one {noun}'s damage" if noun else "one damage roll"
            note = f"{context.by}: {self.amount} more on {roll}."
            return replace(effect, notes=effect.notes + (note,))
        when = self.when
        types = dealt
        if not dealt:
            types = chosen
            picked = " or ".join(t.value for t in chosen)
            when = f"you chose {picked} damage" + (f" and {when}" if when else "")
        if len(types) == 1:
            part = CombatDamage(str(self.amount), types[0], when=when)
        else:
            part = CombatDamage(str(self.amount), None, tuple(types), when=when)
        return replace(effect, damage=effect.damage + (part,))


@dataclass(frozen=True)
class AddHealing(Change):
    """The row's healing restores `amount` more, and `per_slot_level` more
    for each level of the slot it's cast with (Disciple of Life: 2 + the
    slot's level). Its spell's own level counts in the amount; the levels
    above it are the row's upcast."""

    amount: int
    per_slot_level: int = 0
    phase: ClassVar[Phase] = Phase.ADD

    def make(self, effect, context):
        points = effect.healing
        if points is None:
            return effect
        spell = context.source.spell
        level = spell.level if spell is not None else 0
        more = self.amount + self.per_slot_level * level
        upcast = points.upcast
        if self.per_slot_level:
            upcast = _plus(upcast, self.per_slot_level)
        return replace(
            effect,
            healing=replace(
                points,
                dice=_plus(points.dice, more),
                upcast=upcast,
            ),
        )


@dataclass(frozen=True)
class AddBadgeModifiers(Change):
    """The source's badge (its own name, or `badge`) also gives `modifiers`
    while it's on (Mindless Rage: ConditionImmunity to Charmed and
    Frightened on Rage)."""

    modifiers: tuple[Modifier, ...]
    badge: str = ""
    phase: ClassVar[Phase] = Phase.ADD

    def make(self, effect, context):
        name = self.badge or context.source.name
        return replace(
            effect,
            conditions=tuple(
                (
                    replace(c, modifiers=c.modifiers + self.modifiers)
                    if c.name == name
                    else c
                )
                for c in effect.conditions
            ),
        )


@dataclass(frozen=True)
class AlsoEnds(Change):
    """Using it also ends these conditions on its target (Mindless Rage:
    Charmed and Frightened as the Rage starts)."""

    conditions: tuple[Condition, ...]
    phase: ClassVar[Phase] = Phase.ADD

    def make(self, effect, context):
        ends = tuple(c for c in self.conditions if c not in effect.ends_conditions)
        return replace(effect, ends_conditions=effect.ends_conditions + ends)


@dataclass(frozen=True)
class Adjustment:
    """What a feature changes, and where: `changes` on every row `applies`
    matches."""

    applies: Applies
    changes: tuple[Change, ...]

    def __post_init__(self):
        if not self.changes:
            raise ValueError("an Adjustment needs at least one change")
        for change in self.changes:
            if not isinstance(change, Change):
                raise ValueError(f"{change!r} isn't a Change")


# Applying them ------------------------------------------------------------


@dataclass(frozen=True)
class EffectSource:
    """Where a row comes from: the feature whose row it is (an extension's
    own), the spell it casts (a spell's row, or a feature's `spell=` row),
    and whether that's with a spell slot."""

    name: str
    feature: object | None = None
    spell: "SpellLike | None" = None
    with_slot: bool = False


class SpellLike(Protocol):
    """What an adjustment reads of a spell (CharacterContent's Spell)."""

    @property
    def level(self) -> int: ...

    @property
    def school(self) -> str: ...

    @property
    def classes(self) -> list[str]: ...


@dataclass(frozen=True)
class Adjusted:
    """An effect as the character's features change it, and which did."""

    effect: CombatEffect
    by: tuple[str, ...] = ()


class _Sheet(Protocol):
    def iter_features_with_extensions(self) -> Iterable: ...

    def extensions_of(self, feature) -> list: ...


def adjusted(
    sheet: _Sheet | None, source: EffectSource, effect: CombatEffect
) -> Adjusted:
    """`effect`, a row of `source`, with every change the features of
    `sheet` (a character's stat block) make to it, in the order the module
    docstring gives."""
    if sheet is None:
        return Adjusted(effect)
    found: list[tuple[str, Change]] = []
    for feature in sheet.iter_features_with_extensions():
        for adjustment in feature.combat_adjustments(sheet):
            if adjustment.applies.match(source, feature, sheet, effect):
                found.extend((feature.name, c) for c in adjustment.changes)
    if not found:
        return Adjusted(effect)
    found.sort(key=lambda pair: (pair[1].phase, pair[0]))
    found, notes = _settle_sets(found)
    done: set[Change] = set()
    for by, change in found:
        if change.phase is Phase.SET:
            if change in done:
                continue  # the same twice is once
            done.add(change)
        effect = change.make(effect, AdjustContext(sheet, source, by))
    if notes:
        effect = replace(effect, notes=effect.notes + notes)
    return Adjusted(effect, tuple(dict.fromkeys(by for by, _ in found)))


def _settle_sets(
    found: list[tuple[str, Change]],
) -> tuple[list[tuple[str, Change]], tuple[str, ...]]:
    """The SET changes that can't both be made: of two different actions,
    the first by its feature's name counts, and a note says which didn't."""
    actions = [(by, c) for by, c in found if isinstance(c, CostsAction)]
    if len({c.action for _, c in actions}) < 2:
        return found, ()
    first = actions[0][1]
    dropped = [(by, c) for by, c in actions if c.action != first.action]
    note = (
        f"{actions[0][0]} makes it a {first.action.value};"
        + "".join(f" {by} would make it a {c.action.value}" for by, c in dropped)
        + ". Check which applies."
    )
    return [pair for pair in found if pair not in dropped], (note,)


def adjusted_effects(
    sheet: _Sheet | None, source: EffectSource, effects: list[CombatEffect] | None
) -> list[CombatEffect] | None:
    """Each of a source's described effects as `adjusted` makes it; None
    stays None (not described: nothing to change)."""
    if effects is None:
        return None
    return [adjusted(sheet, source, e).effect for e in effects]


# Helpers ------------------------------------------------------------------


def _unique(values: Iterable) -> list:
    return list(dict.fromkeys(values))


def _deals_any(effect: CombatEffect, types: tuple[DamageType, ...]) -> bool:
    return any(
        part.damage_type in types or any(c in types for c in part.choices)
        for part in effect.damage
    )
