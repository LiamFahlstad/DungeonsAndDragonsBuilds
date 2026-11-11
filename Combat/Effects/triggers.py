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
from Core.Definitions import Condition
from Model.Content.CombatModifiers import (
    AttackKind,
    AtTurnEnd,
    AtTurnStart,
    Trigger,
    WhoseTurn,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent, size_fits
from Model.Content.RulesConditions import conditions_with

from .modifiers import _effects_with_modifiers, rules_condition, size_in_use


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
    # The roll's total (None: not known, or a natural 20), and the AC it was
    # checked against, with what changes it (None: not checked), for what
    # the target can answer the hit with (Shield's +5).
    total: int | None = None
    armor: int | None = None

    @property
    def hits(self) -> bool:
        """Whether it counts as a hit: a miss is the only thing that isn't."""
        return self.hit is not False


@dataclass(frozen=True)
class DamageOutcome:
    """Damage `source` dealt `target`, as the window dealt it: `taken`
    after Resistance and Immunity (TAKES_DAMAGE: Hellish Rebuke)."""

    source: dict
    target: dict
    taken: int


def still_hits(outcome: AttackOutcome, armor: int | None) -> bool:
    """Whether the attack of `outcome` hits AC `armor` (its target's AC now,
    after it answered the hit): a Critical Hit always does, and a roll or
    an AC that isn't known still hits, as the GM applied it."""
    if outcome.critical or outcome.total is None or armor is None:
        return True
    return outcome.total >= armor


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
    total: int | None = None  # the roll's total, for a target's Shield


@dataclass(frozen=True)
class TriggerRow:
    """A row a combatant has with a trigger, as the picker builds it for
    them now (effect_options.triggered_rows): its name, what it gives (the
    conditions by name, and a line saying what it does: "Prone"), its uses
    (left, at most) if it spends counted ones, whether using it costs
    anything (a use, a cast, a Reaction), and the picker's row itself, which
    the window applies. For a row that answers a hit (HIT_BY): the action it
    takes ("Reaction": not offered once that's used this round), what its
    badges add to its owner's AC (Shield's 5), and the dice it takes off the
    hit's damage (Deflect Attacks')."""

    name: str
    trigger: CombatTrigger
    conditions: tuple[str, ...] = ()
    what: str = ""
    uses: tuple[int, int] | None = None
    costs: bool = False
    option: object = field(default=None, compare=False)
    action: str | None = None
    armor_bonus: int = 0
    damage_reduction: str = ""
    on_self: bool = False  # what it gives goes on its owner (Shield)

    @property
    def takes_reaction(self) -> bool:
        return self.trigger.reaction or self.action == REACTION


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
    # What it answers (an AttackOutcome or a DamageOutcome), for its question.
    outcome: object = field(default=None, compare=False)

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
        Tumble? Prone. 2 of 2 uses left."; for what the owner answers, the
        other way round: "Ogre hits Clover: use Shield? Shield. AC 15 + 5 =
        20: the 17 misses." """
        event = self.row.trigger.event
        owner, target = self.owner["name"], self.target["name"]
        outcome = self.outcome
        if event is TriggerEvent.HIT_BY:
            head = f"{target} hits {owner}"
        elif event is TriggerEvent.TAKES_DAMAGE:
            taken = outcome.taken if isinstance(outcome, DamageOutcome) else None
            amount = f" {taken}" if taken is not None else ""
            head = f"{target} deals {owner}{amount} damage"
        else:
            # The size it has now: Enlarge makes a Medium creature Large.
            size = size_in_use(self.target)
            shown = f" ({size.value})" if size else ""
            verb = "misses" if event is TriggerEvent.MISS else "hits"
            head = f"{owner} {verb} {target}{shown}"
        parts = [f"{head}: use {self.row.name}?"]
        if self.row.what:
            parts.append(f"{self.row.what}.")
        if (
            self.row.armor_bonus
            and isinstance(outcome, AttackOutcome)
            and outcome.armor is not None
            and outcome.total is not None
            and not outcome.critical
        ):
            armor = outcome.armor + self.row.armor_bonus
            verdict = "misses" if outcome.total < armor else "still hits"
            parts.append(
                f"AC {outcome.armor} + {self.row.armor_bonus} = {armor}:"
                f" the {outcome.total} {verdict}."
            )
        if self.row.damage_reduction:
            parts.append(f"Takes {self.row.damage_reduction} off the damage.")
        if self.row.uses is not None:
            left, most = self.row.uses
            parts.append(f"{left} of {most} uses left.")
        if self.why:
            parts.append(f"Check: {self.why}.")
        return " ".join(parts)

    @property
    def prompt(self) -> str:
        """Its button in the turn column: "Ogre: Kivi's Hill's Tumble (on a
        hit)"; "Clover: Clover's Shield (hit by Ogre)"."""
        event = self.row.trigger.event
        why = f"; {self.why}" if self.why else ""
        if event in (TriggerEvent.HIT_BY, TriggerEvent.TAKES_DAMAGE):
            how = "hit by" if event is TriggerEvent.HIT_BY else "damaged by"
            return (
                f"{self.caster}: {self.row.name}" f" ({how} {self.target['name']}{why})"
            )
        on = "a miss" if event is TriggerEvent.MISS else "a hit"
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


REACTION = "Reaction"
# The conditions that give Incapacitated: a creature with one takes no
# Reaction (Paralyzed, Petrified, Stunned, Unconscious too).
_INCAPACITATING = conditions_with(Condition.INCAPACITATED)


def reaction_lack(char: dict) -> str | None:
    """Why char can't take a Reaction now: it's used this round, or char is
    Incapacitated (or worse). None when it can."""
    if (char.get("action_uses") or {}).get(REACTION, 0) >= 1:
        return "Reaction used"
    if any(rules_condition(c) in _INCAPACITATING for c in char.get("conditions", [])):
        return "Incapacitated"
    return None


def _owner_of(outcome: AttackOutcome | DamageOutcome) -> dict:
    """Whose rows come with outcome: the attacker's (HIT, MISS), or those of
    the creature that took the damage (TAKES_DAMAGE)."""
    return outcome.target if isinstance(outcome, DamageOutcome) else outcome.attacker


def outcome_firings(
    outcomes: Iterable[AttackOutcome | DamageOutcome],
    rows_of: Callable[[dict], list[TriggerRow]],
    *,
    is_dead: Callable[[dict], bool] = is_down,
    used_this_turn: Collection[tuple[str, str]] = (),
) -> tuple[list[HitFiring], list[str]]:
    """The triggered rows (`rows_of`, effect_options.triggered_rows) that
    come with `outcomes` (one Apply's: Times 3 is three, Multiattack's two
    attacks two): an attacker's for its hits and misses, and for damage a
    creature took, that creature's (Hellish Rebuke, against the one that
    dealt it). Each once per (owner, target, row), and a once-per-turn row
    once in all, nor if it's in `used_this_turn` ((owner, row) names).

    A row is left out when its event isn't what happened (HIT, MISS,
    TAKES_DAMAGE), it comes `after` another row that it wasn't, its attack
    kind isn't the attack's, it needs a Critical Hit or damage dealt that the
    attack didn't have, the target is bigger than `largest_target`, dead, or
    already has every condition the row gives, or it takes a Reaction its
    owner can't take (used this round, Incapacitated). With no uses left
    it's left out too, and said in the second list ("Hill's Tumble: no uses
    left", Q42).

    A row is AUTO when it isn't optional, has no `when`, costs nothing and
    every gate was checked; otherwise ASK, with `why` for each gate that
    couldn't be (the target's size, the attack's kind, which row hit)."""
    found: list[HitFiring] = []
    spent: list[str] = []
    seen: set[tuple] = set()
    once: set[tuple] = set()
    rows_by_owner: dict[int, list[TriggerRow]] = {}
    for outcome in outcomes:
        owner = _owner_of(outcome)
        if id(owner) not in rows_by_owner:
            rows_by_owner[id(owner)] = rows_of(owner)
        for row in rows_by_owner[id(owner)]:
            firing = _firing(outcome, row, is_dead)
            if firing is None:
                continue
            key = (id(owner), id(firing.target), row.name)
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


def hit_by_firings(
    outcome: AttackOutcome,
    rows_of: Callable[[dict], list[TriggerRow]],
    *,
    is_dead: Callable[[dict], bool] = is_down,
) -> tuple[list[HitFiring], list[str]]:
    """What the creature `outcome` hits can answer the hit with before its
    damage is dealt (HIT_BY: Shield, Deflect Attacks): its rows of that
    event, each firing against the attacker, with the gates checked as in
    outcome_firings (the attack's kind, a Critical Hit, the attacker's size,
    a Reaction it can still take, uses left). They all cost something, so
    they ask. Rows with no uses left are in the second list."""
    owner = outcome.target
    found: list[HitFiring] = []
    spent: list[str] = []
    if not outcome.hits:
        return found, spent
    for row in rows_of(owner):
        firing = _firing(outcome, row, is_dead, before_damage=True)
        if firing is None:
            continue
        if row.uses is not None and row.uses[0] <= 0:
            spent.append(f"{row.name}: no uses left")
            continue
        found.append(firing)
    return found, spent


def _firing(
    outcome: AttackOutcome | DamageOutcome,
    row: TriggerRow,
    is_dead: Callable[[dict], bool],
    *,
    before_damage: bool = False,
) -> HitFiring | None:
    """row's firing for outcome, if its gates let it fire (uses aside).
    `before_damage`: the hit's HIT_BY rows, of the creature hit."""
    trigger = row.trigger
    event = trigger.event
    if isinstance(outcome, DamageOutcome):
        if event is not TriggerEvent.TAKES_DAMAGE or outcome.taken <= 0:
            return None
        owner, target = outcome.target, outcome.source
    elif before_damage:
        if event is not TriggerEvent.HIT_BY or not outcome.hits:
            return None
        owner, target = outcome.target, outcome.attacker
    elif event is TriggerEvent.HIT:
        if not outcome.hits:
            return None
        owner, target = outcome.attacker, outcome.target
    elif event is TriggerEvent.MISS:
        if outcome.hits:
            return None
        owner, target = outcome.attacker, outcome.target
    else:
        return None  # not this outcome's event
    if owner is target:
        return None  # its own damage (Hellish Rebuke answers another's)
    if row.takes_reaction and reaction_lack(owner) is not None:
        return None
    if row.takes_reaction and is_dead(owner):
        return None
    why: list[str] = []
    attack = outcome if isinstance(outcome, AttackOutcome) else None
    if trigger.after and attack is not None:
        if attack.row and attack.row != trigger.after:
            return None
        if not attack.row:
            why.append(f"if it was {trigger.after}")
    if attack is not None:
        fits = kind_fits(trigger.attacks, attack.kind)
        if fits is False:
            return None
        if fits is None:
            why.append(f"if it was {_a(trigger.attacks.value)}")
        if trigger.critical_only and not attack.critical:
            return None
        if trigger.needs_damage:
            if attack.damage_dealt is not None and attack.damage_dealt <= 0:
                return None
            if attack.damage_dealt is None:
                why.append(f"if it dealt {target['name']} damage")
    if trigger.largest_target is not None:
        fits_size = size_fits(size_in_use(target), trigger.largest_target)
        if fits_size is False:
            return None
        if fits_size is None:
            why.append(f"{target['name']}'s size isn't known")
    if is_dead(target):
        return None
    # What it gives lands on its owner (Shield) or its target (Prone).
    gets = owner if row.on_self else target
    conditions = gets.get("conditions") or []
    if row.conditions and all(c in conditions for c in row.conditions):
        return None
    automatic = not (
        trigger.optional or trigger.when or row.costs or row.takes_reaction
    )
    if trigger.when:
        why.insert(0, f"if {trigger.when}")
    mode = TriggerMode.AUTO if automatic and not why else TriggerMode.ASK
    return HitFiring(
        owner=owner,
        target=target,
        row=row,
        mode=mode,
        why="; ".join(why),
        outcome=outcome,
    )


def reduced_damage(
    parts: list[tuple[int, str]], reduction: int
) -> list[tuple[int, str]]:
    """A hit's damage with `reduction` taken off it (Deflect Attacks' roll),
    before Resistance: off its parts in turn, each part left out once it's
    0, so [] when nothing is left."""
    left = []
    for amount, damage_type in parts:
        taken = min(amount, max(reduction, 0))
        reduction -= taken
        if amount - taken > 0:
            left.append((amount - taken, damage_type))
    return left
