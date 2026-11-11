"""What lasting effects do as a turn starts or ends (Notes/combat-effects-plan.md,
step 3.5): the AtTurnStart and AtTurnEnd a badge's modifiers hold, as the
records in char["active_effects"] keep them. This finds which come with a
turn; the combat window uses each (TurnPanelMixin): Hit Points it gives
itself, and anything else, or anything with a `when`, is a prompt for the GM.

And what a hit or a miss triggers (Phase 6): the rows with a CombatTrigger an
attacker has (Hill's Tumble), as `outcome_firings` finds them for each
AttackOutcome, with the gates checked here and the mode (AUTO: applied
without asking; ASK: the GM decides) and why it asks.

A trigger of WhoseTurn.BEARER comes with each turn of whoever has the badge
(Heroism's target). One of WhoseTurn.ENEMY comes with each turn of every
creature not on the side of the badge's caster (Spirit Guardians'), once
however many creatures have the badge: Cast Spell puts it on the targets a
spell is aimed at, the Custom Effect dialog on whoever is targeted, and
neither says where the Emanation is. A trigger counts only while its badge is
on, as a modifier does. Nothing here imports Qt."""

from collections.abc import Callable, Collection, Iterable
from dataclasses import dataclass, field
from enum import StrEnum

from Combat.PartyAllies import is_party_ally
from Combat.Summons import owner_name
from Model.Content.CombatModifiers import (
    AttackKind,
    AtTurnEnd,
    AtTurnStart,
    Trigger,
    WhoseTurn,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent, size_fits

from .modifiers import _effects_with_modifiers, size_in_use


@dataclass(frozen=True)
class Firing:
    """One trigger coming with one creature's turn: the badge's `bearer`
    has `badge` (its record's `source` and `caster`, if known), and
    `trigger` happens to `target`, whose turn it is."""

    bearer: dict
    badge: str
    source: str | None
    caster: str | None
    trigger: Trigger
    target: dict

    @property
    def is_prompt(self) -> bool:
        """Whether the GM decides it: it has a `when` (where creatures are)."""
        return bool(self.trigger.when)

    @property
    def prompt(self) -> str:
        """The question the turn column asks about it: "Tiger: if it ends its
        turn in the Emanation, Edmund's Spirit Guardians: damage"."""
        whose = f"{self.caster}'s " if self.caster else ""
        when = f"if {self.trigger.when}, " if self.trigger.when else ""
        return f"{self.target['name']}: {when}{whose}{self.trigger.effect}"

    @property
    def pick(self) -> str:
        """The row its prompt's button picks in the Custom Effect dialog."""
        return self.trigger.effect


def on_party_side(char: dict) -> bool:
    """Whether char fights on the party's side: a player, a party ally, or a
    player's summon."""
    return bool(
        char.get("_is_player") or is_party_ally(char) or owner_name(char) is not None
    )


def firings(
    chars: Iterable[dict],
    turn: Iterable[dict],
    kind: type[AtTurnStart] | type[AtTurnEnd],
    find: Callable[[str], dict | None],
) -> list[Firing]:
    """The triggers of `kind` that come with the turn of the creatures in
    `turn`, from the badges every one of `chars` has. `find` gives a
    combatant by name (the caster of an enemy-turn trigger, to know its
    side); a trigger of a caster that isn't in the fight comes with no
    enemy's turn."""
    chars = list(chars)
    turn = list(turn)
    found: list[Firing] = []
    seen: set[tuple] = set()
    for bearer in chars:
        for effect, modifier in _effects_with_modifiers(bearer):
            if not isinstance(modifier, kind):
                continue
            caster = effect.get("caster")
            if modifier.whose is WhoseTurn.BEARER:
                targets = [c for c in turn if c is bearer]
            else:
                whose = find(caster) if caster else None
                if whose is None:
                    continue
                targets = [
                    c
                    for c in turn
                    if c is not whose and on_party_side(c) != on_party_side(whose)
                ]
            for target in targets:
                key = (caster, effect["name"], modifier, target["name"])
                if modifier.whose is WhoseTurn.ENEMY and key in seen:
                    continue
                seen.add(key)
                found.append(
                    Firing(
                        bearer=bearer,
                        badge=effect["name"],
                        source=effect.get("source"),
                        caster=caster,
                        trigger=modifier,
                        target=target,
                    )
                )
    return found


# ---------------------------------------------------------------------------
# What a hit or a miss triggers (Phase 6)


@dataclass(frozen=True)
class AttackOutcome:
    """One attack roll's outcome against one target, as a hit path saw it:
    `hit` (None: it couldn't be checked, so the GM applied it as a hit),
    a Critical Hit, the attack's `kind` (None: not known, as for a typed
    roll or a monster's attack), the `row` it was made with ("" if not
    known), and the damage the target took after Resistance and Immunity
    (None: not known)."""

    attacker: dict
    target: dict
    hit: bool | None
    critical: bool = False
    kind: AttackKind | None = None
    row: str = ""
    damage_dealt: int | None = None

    @property
    def hits(self) -> bool:
        """Whether it counts as a hit: a miss is the only thing that isn't."""
        return self.hit is not False


@dataclass(frozen=True)
class PendingAttack:
    """An attack roll made in one step whose damage is applied in the next
    (a monster's action button, the main window's Attack roll field): who
    rolled it, whether it was a Critical Hit, the row it was made with, and
    the targets it hit (None: whoever is targeted as the damage is applied).
    `step` is the undo step that rolled it, to tell it's still the last."""

    attacker: dict
    critical: bool = False
    row: str = ""
    kind: AttackKind | None = None
    targets: tuple[dict, ...] | None = None
    step: object = field(default=None, compare=False)


@dataclass(frozen=True)
class TriggerRow:
    """A row a combatant has with a trigger, as the picker builds it for
    them now (effect_options.triggered_rows): its name, what it gives (the
    conditions by name, and a line saying what it does: "Prone"), its uses
    (left, at most) if it spends counted ones, whether using it costs
    anything (a use, a cast, a Reaction), and the picker's row itself, which
    the window applies."""

    name: str
    trigger: CombatTrigger
    conditions: tuple[str, ...] = ()
    what: str = ""
    uses: tuple[int, int] | None = None
    costs: bool = False
    option: object = field(default=None, compare=False)


class TriggerMode(StrEnum):
    """AUTO: applied without asking (the rules say it happens, every gate
    is checked, nothing is spent). ASK: the GM decides."""

    AUTO = "auto"
    ASK = "ask"


@dataclass(frozen=True)
class HitFiring:
    """One triggered row of `owner` coming with an attack on `target`, how
    it's used (`mode`) and, when it asks because a gate couldn't be checked,
    why ("Ogre's size isn't known")."""

    owner: dict
    target: dict
    row: TriggerRow
    mode: TriggerMode
    why: str = ""

    @property
    def caster(self) -> str:
        """Who uses it (a turn-column prompt's source)."""
        return self.owner["name"]

    @property
    def pick(self) -> str:
        """The row the Custom Effect dialog starts with picked (Edit)."""
        return self.row.name

    @property
    def question(self) -> str:
        """Its line in the pop-up: "Kivi hits Ogre (Large): use Hill's
        Tumble? Prone. 2 of 2 uses left." """
        # The size it has now: Enlarge makes a Medium creature Large.
        size = size_in_use(self.target)
        shown = f" ({size.value})" if size else ""
        verb = "misses" if self.row.trigger.event is TriggerEvent.MISS else "hits"
        parts = [
            f"{self.owner['name']} {verb} {self.target['name']}{shown}:"
            f" use {self.row.name}?"
        ]
        if self.row.what:
            parts.append(f"{self.row.what}.")
        if self.row.uses is not None:
            left, most = self.row.uses
            parts.append(f"{left} of {most} uses left.")
        if self.why:
            parts.append(f"Check: {self.why}.")
        return " ".join(parts)

    @property
    def prompt(self) -> str:
        """Its button in the turn column: "Ogre: Kivi's Hill's Tumble (on a
        hit)"."""
        on = "a miss" if self.row.trigger.event is TriggerEvent.MISS else "a hit"
        why = f"; {self.why}" if self.why else ""
        return f"{self.target['name']}: {self.caster}'s {self.row.name} (on {on}{why})"


@dataclass(frozen=True)
class TriggerChoice:
    """What the GM answered the pop-up: the firings to apply now, and those
    to open the Custom Effect dialog for. The rest were declined."""

    apply: tuple[HitFiring, ...] = ()
    edit: tuple[HitFiring, ...] = ()


# For an attack of a known kind (the key), the kinds a trigger can ask for
# that it surely is, and those it surely isn't; the rest can't be told (a
# weapon attack may be melee or ranged).
_KINDS: dict[AttackKind, tuple[set[AttackKind], set[AttackKind]]] = {
    AttackKind.WEAPON: ({AttackKind.WEAPON}, {AttackKind.UNARMED, AttackKind.SPELL}),
    AttackKind.UNARMED: (
        {AttackKind.UNARMED, AttackKind.MELEE},
        {AttackKind.WEAPON, AttackKind.SPELL, AttackKind.RANGED},
    ),
    AttackKind.SPELL: ({AttackKind.SPELL}, {AttackKind.WEAPON, AttackKind.UNARMED}),
    AttackKind.MELEE: ({AttackKind.MELEE}, {AttackKind.RANGED}),
    AttackKind.RANGED: (
        {AttackKind.RANGED},
        {AttackKind.MELEE, AttackKind.UNARMED},
    ),
}


def kind_fits(wanted: AttackKind, kind: AttackKind | None) -> bool | None:
    """Whether an attack of `kind` is one of the `wanted` kind; None when
    that can't be told (the kind isn't known, or doesn't say: a weapon
    attack asked about being melee)."""
    if wanted is AttackKind.ANY or wanted is kind:
        return True
    if kind is None or kind is AttackKind.ANY:
        return None
    surely, never = _KINDS[kind]
    if wanted in surely:
        return True
    if wanted in never:
        return False
    return None


def _a(text: str) -> str:
    return f"an {text}" if text[:1] in "aeiou" else f"a {text}"


def is_down(char: dict) -> bool:
    """Whether char is dead, as far as these plain dicts tell: at 0 HP and
    not one who makes Death Saving Throws (CardsMixin._char_death_state)."""
    if char.get("hp", 1) > 0 or char.get("max_hp", 1) <= 0:
        return False
    if char.get("_is_player") or char.get("death_saves", False):
        return char.get("death_saves_fail", 0) >= 3
    return True


def outcome_firings(
    outcomes: Iterable[AttackOutcome],
    rows_of: Callable[[dict], list[TriggerRow]],
    *,
    is_dead: Callable[[dict], bool] = is_down,
    used_this_turn: Collection[tuple[str, str]] = (),
) -> tuple[list[HitFiring], list[str]]:
    """The attackers' triggered rows (`rows_of`, effect_options.triggered_rows)
    that come with `outcomes` (one Apply's: Times 3 is three, Multiattack's
    two attacks two), each once per (owner, target, row), and a once-per-turn
    row once in all, nor if it's in `used_this_turn` ((owner, row) names).

    A row is left out when its event isn't what happened (HIT, MISS), it
    comes `after` another row that it wasn't, its attack kind isn't the
    attack's, it needs a Critical Hit or damage dealt that the attack didn't
    have, the target is bigger than `largest_target`, dead, or already has
    every condition the row gives. With no uses left it's left out too, and
    said in the second list ("Hill's Tumble: no uses left", Q42).

    A row is AUTO when it isn't optional, has no `when`, costs nothing and
    every gate was checked; otherwise ASK, with `why` for each gate that
    couldn't be (the target's size, the attack's kind, which row hit)."""
    found: list[HitFiring] = []
    spent: list[str] = []
    seen: set[tuple] = set()
    once: set[tuple] = set()
    rows_by_owner: dict[int, list[TriggerRow]] = {}
    for outcome in outcomes:
        owner = outcome.attacker
        if id(owner) not in rows_by_owner:
            rows_by_owner[id(owner)] = rows_of(owner)
        for row in rows_by_owner[id(owner)]:
            firing = _firing(outcome, row, is_dead)
            if firing is None:
                continue
            key = (id(owner), id(outcome.target), row.name)
            once_key = (owner["name"], row.name)
            if key in seen or (row.trigger.once_per_turn and once_key in once):
                continue
            if row.trigger.once_per_turn and once_key in used_this_turn:
                continue
            if row.uses is not None and row.uses[0] <= 0:
                line = f"{row.name}: no uses left"
                if line not in spent:
                    spent.append(line)
                continue
            seen.add(key)
            once.add(once_key)
            found.append(firing)
    return found, spent


def _firing(
    outcome: AttackOutcome, row: TriggerRow, is_dead: Callable[[dict], bool]
) -> HitFiring | None:
    """row's firing for outcome, if its gates let it fire (uses aside)."""
    trigger = row.trigger
    target = outcome.target
    if trigger.event is TriggerEvent.HIT:
        if not outcome.hits:
            return None
    elif trigger.event is TriggerEvent.MISS:
        if outcome.hits:
            return None
    else:
        return None  # not an attack's event
    why: list[str] = []
    if trigger.after:
        if outcome.row and outcome.row != trigger.after:
            return None
        if not outcome.row:
            why.append(f"if it was {trigger.after}")
    fits = kind_fits(trigger.attacks, outcome.kind)
    if fits is False:
        return None
    if fits is None:
        why.append(f"if it was {_a(trigger.attacks.value)}")
    if trigger.critical_only and not outcome.critical:
        return None
    if trigger.needs_damage:
        if outcome.damage_dealt is not None and outcome.damage_dealt <= 0:
            return None
        if outcome.damage_dealt is None:
            why.append(f"if it dealt {target['name']} damage")
    if trigger.largest_target is not None:
        fits_size = size_fits(size_in_use(target), trigger.largest_target)
        if fits_size is False:
            return None
        if fits_size is None:
            why.append(f"{target['name']}'s size isn't known")
    if is_dead(target):
        return None
    conditions = target.get("conditions") or []
    if row.conditions and all(c in conditions for c in row.conditions):
        return None
    automatic = not (trigger.optional or trigger.when or row.costs or trigger.reaction)
    if trigger.when:
        why.insert(0, f"if {trigger.when}")
    mode = TriggerMode.AUTO if automatic and not why else TriggerMode.ASK
    return HitFiring(
        owner=outcome.attacker,
        target=target,
        row=row,
        mode=mode,
        why="; ".join(why),
    )
