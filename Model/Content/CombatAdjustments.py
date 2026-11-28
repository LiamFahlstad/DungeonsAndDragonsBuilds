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
   action changed). The same change twice is made once; two that can't
   both be made (`Change.conflicts`: two different actions) keep the first
   by its feature's name, and the row says which one wasn't made.
3. ADD: notes, damage, healing, a badge's modifiers, the conditions it
   ends, by the adjusting feature's name.

A change decides from the row as its phase found it (`AdjustContext.before`)
and writes onto the row as it goes, so within a phase no change sees what
another made: Elemental Affinity's "one damage roll" is one of the spell's
own, never a part another feature added in the same phase. That, and not
the sort by name, is what makes the result independent of the order.

An adjustment changes the row itself, or, with `variant=`, adds a row of
its own next to it, which stays as it was: another way to use the source
(Fleet Step: Step of the Wind right after another Bonus Action, with no
action of its own). A variant row is the row with every in-place change
and the variant's own, made together in the one order above; variants
don't combine with each other.

Every reader of a character's effects goes through `adjusted`: the picker's
rows (spells, features, extensions, triggered rows; `Adjusted.rows` gives
the variants too) and the badges given straight from a card's Use or Cast
button (`adjusted_effects`: the row itself, never a variant).
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
    """What a change is made for: the character, the source of the row, the
    adjusting feature's name (for notes), and the row as the change's phase
    found it, which is what a change decides from (the module docstring)."""

    character: object
    source: "EffectSource"
    by: str
    before: CombatEffect


class Change:
    """One change to an effect. `phase` says when it's made. A SET change
    that can't be made together with another says so (`conflicts`) and
    what it would make the row (`describe`), for the note on the row."""

    phase: ClassVar[Phase]

    def make(self, effect: CombatEffect, context: AdjustContext) -> CombatEffect:
        raise NotImplementedError

    def conflicts(self, other: "Change") -> bool:
        """Whether this SET change and `other` can't both be made: each would
        set the same thing to something else (two different actions).
        Changes that commute (MaximizeDice's healing and its damage) don't."""
        return False

    def describe(self) -> str:
        """What this change makes the row, for the note when it conflicts
        ("a Bonus Action")."""
        return type(self).__name__


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
    """Using it takes `action` instead (a casting as a Bonus Action), or
    none (ActionType.NO_ACTION: Fleet Step's Step of the Wind, as part of
    another Bonus Action). Two different actions on one row conflict."""

    action: ActionType
    phase: ClassVar[Phase] = Phase.SET

    def make(self, effect, context):
        return replace(effect, action_type=self.action)

    def conflicts(self, other):
        return isinstance(other, CostsAction) and other.action != self.action

    def describe(self):
        if self.action is ActionType.NO_ACTION:
            return "take no action"
        return f"a {self.action.value.replace('_', ' ').title()}"


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
        # The row's own damage rolls, not a part another ADD change made.
        parts = [part for part in context.before.damage if not part.when]
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
    matches. With `variant`, the changes make a row of their own instead,
    named "<row> (<variant>)", next to the row, which stays as it was:
    another way to use it (Fleet Step's Step of the Wind with no action).
    The variant row spends what its row spends."""

    applies: Applies
    changes: tuple[Change, ...]
    variant: str = ""

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
    """An effect as the character's features change it, which features did,
    and the rows their variants add (each an Adjusted of its own)."""

    effect: CombatEffect
    by: tuple[str, ...] = ()
    variants: tuple["Adjusted", ...] = ()

    @property
    def rows(self) -> tuple["Adjusted", ...]:
        """The row, then its variants' rows: what the picker lists."""
        return (self, *self.variants)

    @property
    def changed_by(self) -> str:
        """The line a row's tooltip ends with ("" when nothing changed it)."""
        return f"\n\nChanged by {', '.join(self.by)}." if self.by else ""


class _Sheet(Protocol):
    def iter_features_with_extensions(self) -> Iterable: ...

    def extensions_of(self, feature) -> list: ...


_Found = list[tuple[str, Change]]  # (the adjusting feature's name, a change)


def adjusted(
    sheet: _Sheet | None, source: EffectSource, effect: CombatEffect
) -> Adjusted:
    """`effect`, a row of `source`, with every change the features of
    `sheet` (a character's stat block) make to it, in the order the module
    docstring gives, and a row for each variant that applies to it."""
    if sheet is None:
        return Adjusted(effect)
    found: _Found = []
    variants: list[tuple[str, _Found]] = []
    for feature in sheet.iter_features_with_extensions():
        for adjustment in feature.combat_adjustments(sheet):
            if not adjustment.applies.match(source, feature, sheet, effect):
                continue
            pairs = [(feature.name, c) for c in adjustment.changes]
            if adjustment.variant:
                variants.append((adjustment.variant, pairs))
            else:
                found.extend(pairs)
    row = _changed(sheet, source, effect, found)
    rows = []
    for variant, pairs in sorted(variants, key=lambda v: (v[0], v[1][0][0])):
        own = _changed(sheet, source, effect, found + pairs)
        name = f"{effect.name or source.name} ({variant})"
        rows.append(replace(own, effect=replace(own.effect, name=name)))
    return replace(row, variants=tuple(rows))


def _changed(
    sheet: _Sheet, source: EffectSource, effect: CombatEffect, found: _Found
) -> Adjusted:
    """`effect` with the changes `found` makes, phase by phase."""
    if not found:
        return Adjusted(effect)
    found = sorted(found, key=lambda pair: (pair[1].phase, pair[0]))
    found, notes = _settle_sets(found)
    done: set[Change] = set()
    phase, before = None, effect
    for by, change in found:
        if change.phase is not phase:
            phase, before = change.phase, effect
        if change.phase is Phase.SET:
            if change in done:
                continue  # the same twice is once
            done.add(change)
        effect = change.make(effect, AdjustContext(sheet, source, by, before))
    if notes:
        effect = replace(effect, notes=effect.notes + notes)
    return Adjusted(effect, tuple(dict.fromkeys(by for by, _ in found)))


def _settle_sets(found: _Found) -> tuple[_Found, tuple[str, ...]]:
    """`found` (sorted) without the SET changes that conflict with one before
    them (`Change.conflicts`), and a note on each that wasn't made."""
    kept: _Found = []
    notes = []
    for by, change in found:
        if change.phase is Phase.SET:
            clash = next(
                (pair for pair in kept if change.conflicts(pair[1])),
                None,
            )
            if clash is not None:
                notes.append(
                    f"{clash[0]} makes it {clash[1].describe()}; {by} would make"
                    f" it {change.describe()}. Check which applies."
                )
                continue
        kept.append((by, change))
    return kept, tuple(notes)


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
