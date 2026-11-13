"""What lasting effects do as a turn starts or ends (Notes/combat-effects-plan.md,
step 3.5): the AtTurnStart and AtTurnEnd a badge's modifiers hold, as the
records in char["active_effects"] keep them. This finds which come with a
turn; the combat window uses each (TurnPanelMixin): Hit Points it gives
itself, and anything else, or anything with a `when`, is a prompt for the GM.

And what a hit or a miss triggers (Phase 6): the rows with a CombatTrigger an
attacker has (Hill's Tumble), as `outcome_firings` finds them for each
AttackOutcome, with the gates checked here and the mode (AUTO: applied
without asking; ASK: the GM decides) and why it asks. And what Hit Points
reaching 0 triggers (6.6): the rows of a creature damage would drop to 0
(drop_firings: Relentless Endurance, asked before it drops), and of the one
that reduced a creature to 0 (KnockoutOutcome: Dark One's Blessing).

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
    WhenHit,
    WhoseTurn,
)
from Model.Content.CombatTriggers import (
    CombatTrigger,
    TriggerAim,
    TriggerEvent,
    size_fits,
)
from Model.Content.RulesConditions import conditions_with

from .active_effects import ActiveEffect
from .modifiers import (
    _effects_with_modifiers,
    hit_point_maximum,
    rules_condition,
    size_in_use,
)


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
class AttackRollOutcome:
    """`attacker` is about to make an attack roll against `target`, and
    `owner` (anyone else in the fight) can answer it before it's rolled
    (ATTACKS: Warding Flare, against the attacker). One per creature that
    could, made by attack_roll_firings."""

    attacker: dict
    target: dict
    owner: dict


@dataclass(frozen=True)
class DamageOutcome:
    """Damage `source` dealt `target`, as the window dealt it: `taken`
    after Resistance and Immunity (TAKES_DAMAGE: Hellish Rebuke)."""

    source: dict
    target: dict
    taken: int


@dataclass(frozen=True)
class KnockoutOutcome:
    """`source` reduced `target` to 0 Hit Points (REDUCES_TO_ZERO: Dark
    One's Blessing), as the window dealt the damage."""

    source: dict
    target: dict


@dataclass(frozen=True)
class BloodiedOutcome:
    """Damage, from `source` if known, left `target` Bloodied, though it
    wasn't, and not at 0 Hit Points (BLOODIED: Harvest Undead)."""

    target: dict
    source: dict | None = None


@dataclass(frozen=True)
class UsesOutcome:
    """`owner` used its row `row` on `target`, picked and applied in the
    Custom Effect dialog (USES: Ice Knife's explosion after its shard)."""

    owner: dict
    target: dict
    row: str


@dataclass(frozen=True)
class FailedSaveOutcome:
    """`char` failed a DC `dc` save of `ability` ("WIS") the window rolled,
    with `total`, against `against` ("Hold Person", "" if not known)
    (FAILS_SAVE: Indomitable)."""

    char: dict
    ability: str
    dc: int
    total: int
    against: str = ""


@dataclass(frozen=True)
class InitiativeOutcome:
    """`char` rolls Initiative, as the fight starts (ROLLS_INITIATIVE:
    Uncanny Metabolism, Superior Inspiration)."""

    char: dict


@dataclass(frozen=True)
class DropOutcome:
    """`damage` (after Resistance and Temporary Hit Points) would drop
    `target` to 0 Hit Points, with `left_over` of it past 0; from `source`,
    if known (DROPS_TO_ZERO: Relentless Endurance, asked before it drops)."""

    target: dict
    source: dict | None
    damage: int
    left_over: int = 0


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
    drops_to: int = 0  # the Hit Points it drops its owner to instead of 0
    # For a row that only restores (as a fight starts): whether it heals,
    # whether it gives feature uses back, and how many it would now.
    heals: bool = False
    regains: bool = False
    regainable: int = 0
    # A spell's or a weapon's row: what comes `after` a casting (its later
    # step) or a weapon's attack (its mastery) follows only the row picked in
    # the dialog, never a hit typed in (R137, R143).
    picked_only: bool = False
    reroll_save: int | None = None  # the bonus it rerolls a failed save with

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
    # For a row aimed at another creature (TriggerAim), who it can go on: the
    # window fills them in before it asks.
    others: tuple[dict, ...] = field(default=(), compare=False)

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
        if event is TriggerEvent.DROPS_TO_ZERO:
            drop = outcome if isinstance(outcome, DropOutcome) else None
            by = drop.source if drop is not None else None
            amount = f"{drop.damage} damage" if drop is not None else "damage"
            if by is not None and by is not self.owner:
                head = f"{by['name']}'s {amount} would drop {owner} to 0 Hit Points"
            else:
                head = f"{amount.capitalize()} would drop {owner} to 0 Hit Points"
        elif event is TriggerEvent.REDUCES_TO_ZERO:
            head = f"{owner} reduces {target} to 0 Hit Points"
        elif event is TriggerEvent.USES:
            used = outcome.row if isinstance(outcome, UsesOutcome) else "it"
            head = f"{owner} uses {used} on {target}"
        elif event is TriggerEvent.FAILS_SAVE and isinstance(
            outcome, FailedSaveOutcome
        ):
            against = f" against {outcome.against}" if outcome.against else ""
            head = (
                f"{owner} fails a DC {outcome.dc} {outcome.ability} save{against}"
                f" with {outcome.total}"
            )
        elif event is TriggerEvent.FAILS_SAVE:
            head = f"{owner} fails a save"
        elif event is TriggerEvent.ROLLS_INITIATIVE:
            head = f"{owner} rolls Initiative"
        elif event is TriggerEvent.BLOODIED:
            by = outcome.source if isinstance(outcome, BloodiedOutcome) else None
            whose = f"{by['name']}'s damage" if by is not None else "Damage"
            head = f"{whose} leaves {owner} Bloodied"
        elif event is TriggerEvent.HIT_BY:
            head = f"{target} hits {owner}"
        elif event is TriggerEvent.ATTACKS:
            attacked = (
                outcome.target["name"]
                if isinstance(outcome, AttackRollOutcome)
                else "a creature"
            )
            head = f"{target} makes an attack roll against {attacked}"
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
        aim = self.row.trigger.aim
        if aim is TriggerAim.ANOTHER:
            parts.append(f"It goes on another creature near {target}: pick it.")
        elif aim is TriggerAim.ALSO_OTHERS:
            parts.append(f"On {target}, and any creature near it you add.")
        if self.why:
            parts.append(f"Check: {self.why}.")
        return " ".join(parts)

    @property
    def prompt(self) -> str:
        """Its button in the turn column: "Ogre: Kivi's Hill's Tumble (on a
        hit)"; "Clover: Clover's Shield (hit by Ogre)"."""
        event = self.row.trigger.event
        why = f"; {self.why}" if self.why else ""
        if event is TriggerEvent.DROPS_TO_ZERO:
            drop = self.outcome if isinstance(self.outcome, DropOutcome) else None
            by = drop.source if drop is not None else None
            by_whom = (
                f" by {by['name']}" if by is not None and by is not self.owner else ""
            )
            return f"{self.caster}: {self.row.name} (dropped to 0{by_whom}{why})"
        if event is TriggerEvent.REDUCES_TO_ZERO:
            return (
                f"{self.target['name']}: {self.caster}'s {self.row.name}"
                f" (on a knockout{why})"
            )
        if event is TriggerEvent.ROLLS_INITIATIVE:
            return f"{self.caster}: {self.row.name} (on rolling Initiative{why})"
        if event is TriggerEvent.FAILS_SAVE:
            return f"{self.caster}: {self.row.name} (a failed save{why})"
        if event is TriggerEvent.USES:
            return (
                f"{self.target['name']}: {self.caster}'s {self.row.name}"
                f" (after {self.row.trigger.after}{why})"
            )
        if event is TriggerEvent.BLOODIED:
            by = (
                self.outcome.source
                if isinstance(self.outcome, BloodiedOutcome)
                else None
            )
            by_whom = f" by {by['name']}" if by is not None else ""
            return f"{self.caster}: {self.row.name} (Bloodied{by_whom}{why})"
        if event in (TriggerEvent.HIT_BY, TriggerEvent.TAKES_DAMAGE):
            how = "hit by" if event is TriggerEvent.HIT_BY else "damaged by"
            return (
                f"{self.caster}: {self.row.name}" f" ({how} {self.target['name']}{why})"
            )
        if event is TriggerEvent.ATTACKS:
            return (
                f"{self.target['name']}: {self.caster}'s {self.row.name}"
                f" (before its attack roll{why})"
            )
        on = "a miss" if event is TriggerEvent.MISS else "a hit"
        return f"{self.target['name']}: {self.caster}'s {self.row.name} (on {on}{why})"


@dataclass(frozen=True)
class TriggerChoice:
    """What the GM answered the pop-up: the firings to apply now, and those
    to open the Custom Effect dialog for. The rest were declined. `rolled`:
    what was rolled at the table for a firing's own roll (Deflect Attacks'
    1d10 + 8), by firing; the rest are rolled here (plan principle 13)."""

    apply: tuple[HitFiring, ...] = ()
    edit: tuple[HitFiring, ...] = ()
    rolled: tuple[tuple[HitFiring, int], ...] = ()
    # For a firing aimed at other creatures (TriggerAim), those picked.
    aimed: tuple[tuple[HitFiring, tuple[dict, ...]], ...] = ()

    def rolled_for(self, firing: HitFiring) -> int | None:
        """What was rolled at the table for firing, if it was."""
        return next((n for f, n in self.rolled if f is firing), None)

    def aimed_at(self, firing: HitFiring) -> tuple[dict, ...]:
        """The other creatures picked for firing (none if none were)."""
        return next((chars for f, chars in self.aimed if f is firing), ())


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


Outcome = (
    AttackOutcome
    | DamageOutcome
    | KnockoutOutcome
    | BloodiedOutcome
    | InitiativeOutcome
    | UsesOutcome
    | FailedSaveOutcome
    | AttackRollOutcome
)
# The outcomes whose rows are the owner's own and fire on itself.
_OWN = (BloodiedOutcome, InitiativeOutcome, FailedSaveOutcome)


def _owner_of(outcome: Outcome) -> dict:
    """Whose rows come with outcome: the attacker's (HIT, MISS), those of
    the creature that took the damage (TAKES_DAMAGE), or of the one that
    reduced a creature to 0 Hit Points (REDUCES_TO_ZERO)."""
    if isinstance(outcome, DamageOutcome):
        return outcome.target
    if isinstance(outcome, KnockoutOutcome):
        return outcome.source
    if isinstance(outcome, BloodiedOutcome):
        return outcome.target
    if isinstance(outcome, InitiativeOutcome):
        return outcome.char
    if isinstance(outcome, UsesOutcome):
        return outcome.owner
    if isinstance(outcome, FailedSaveOutcome):
        return outcome.char
    if isinstance(outcome, AttackRollOutcome):
        return outcome.owner
    return outcome.attacker


def outcome_firings(
    outcomes: Iterable[Outcome],
    rows_of: Callable[[dict], list[TriggerRow]],
    *,
    is_dead: Callable[[dict], bool] = is_down,
    used_this_turn: Collection[tuple[str, str]] = (),
) -> tuple[list[HitFiring], list[str]]:
    """The triggered rows (`rows_of`, effect_options.triggered_rows) that
    come with `outcomes` (one Apply's: Times 3 is three, Multiattack's two
    attacks two): an attacker's for its hits and misses, for damage a
    creature took, that creature's (Hellish Rebuke, against the one that
    dealt it), for a creature reduced to 0 Hit Points, the one that did
    it (Dark One's Blessing), and for one damage left Bloodied, its own
    (Harvest Undead). Each once per (owner, target, row), and a once-per-turn row
    once in all, nor if it's in `used_this_turn` ((owner, row) names).

    A row is left out when its event isn't what happened (HIT, MISS,
    TAKES_DAMAGE), it comes `after` another row that it wasn't, its attack
    kind isn't the attack's, it needs a Critical Hit or damage dealt that the
    attack didn't have, the target is bigger than `largest_target`, not an
    enemy of the owner (`enemy_only`), dead (but for a knockout's), or
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


def attack_roll_firings(
    attacker: dict,
    target: dict,
    others: Iterable[dict],
    rows_of: Callable[[dict], list[TriggerRow]],
    *,
    is_dead: Callable[[dict], bool] = is_down,
) -> list[HitFiring]:
    """What the creatures in `others` can answer attacker's attack roll
    against target with, before it's rolled (ATTACKS: Warding Flare, "when
    a creature ... makes an attack roll, you can take a Reaction to impose
    Disadvantage on the roll"): their rows of that event, each firing
    against the attacker, with the gates of outcome_firings (an enemy of
    the owner, a Reaction it can still take, uses left). It comes with
    every attack roll the simulator makes, so a row with no uses left is
    left out without a word (not Q42's status line), and only creatures
    that can still take a Reaction are looked at."""
    found: list[HitFiring] = []
    for owner in others:
        if owner is attacker or reaction_lack(owner) is not None or is_dead(owner):
            continue
        outcome = AttackRollOutcome(attacker, target, owner)
        for row in rows_of(owner):
            if row.trigger.event is not TriggerEvent.ATTACKS:
                continue
            if row.uses is not None and row.uses[0] <= 0:
                continue
            firing = _firing(outcome, row, is_dead)
            if firing is not None:
                found.append(firing)
    return found


def badge_hit_firings(
    outcome: AttackOutcome,
    row_of: Callable[[dict, ActiveEffect, WhenHit], TriggerRow | None],
    *,
    is_dead: Callable[[dict], bool] = is_down,
) -> list[HitFiring]:
    """What the badges of the creature `outcome` hits answer the hit with,
    once its damage is dealt (WhenHit, plan Q57: Armor of Agathys' Cold
    damage, Fire Shield's): one firing per WhenHit, its bearer the owner and
    the attacker the target. `row_of(bearer, record, modifier)` is the row
    the modifier names, as its caster has it (None: there's no such row).
    Left out on a miss, against a dead attacker, or for an attack surely
    not of the modifier's kind. AUTO when the kind is surely the modifier's
    and there's no `when`; otherwise ASK, saying why."""
    bearer, attacker = outcome.target, outcome.attacker
    if not outcome.hit or attacker is bearer or is_dead(attacker):
        return []
    found: list[HitFiring] = []
    for record, modifier in _effects_with_modifiers(bearer):
        if not isinstance(modifier, WhenHit):
            continue
        fits = kind_fits(modifier.attacks, outcome.kind)
        if fits is False:
            continue
        row = row_of(bearer, record, modifier)
        if row is None:
            continue
        why = [f"if {modifier.when}"] if modifier.when else []
        if fits is None:
            why.append(f"if it was {_a(modifier.attacks.value)}")
        found.append(
            HitFiring(
                owner=bearer,
                target=attacker,
                row=row,
                mode=TriggerMode.ASK if why else TriggerMode.AUTO,
                why="; ".join(why),
                outcome=outcome,
            )
        )
    return found


def _firing(
    outcome: Outcome,
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
    elif isinstance(outcome, KnockoutOutcome):
        if event is not TriggerEvent.REDUCES_TO_ZERO:
            return None
        owner, target = outcome.source, outcome.target
    elif isinstance(outcome, BloodiedOutcome):
        if event is not TriggerEvent.BLOODIED:
            return None
        owner = target = outcome.target  # it's the owner's own
    elif isinstance(outcome, UsesOutcome):
        if event is not TriggerEvent.USES or trigger.after != outcome.row:
            return None
        owner, target = outcome.owner, outcome.target
    elif isinstance(outcome, FailedSaveOutcome):
        if event is not TriggerEvent.FAILS_SAVE:
            return None
        owner = target = outcome.char
    elif isinstance(outcome, AttackRollOutcome):
        if event is not TriggerEvent.ATTACKS:
            return None
        owner, target = outcome.owner, outcome.attacker
    elif isinstance(outcome, InitiativeOutcome):
        if event is not TriggerEvent.ROLLS_INITIATIVE:
            return None
        owner = target = outcome.char
        if (row.heals or row.regains) and not _restores_anything(owner, row):
            return None  # nothing to regain: keep the use
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
    if owner is target and not isinstance(outcome, _OWN):
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
        if not attack.row and row.picked_only:
            return None  # a casting's later step, a weapon's mastery: picked only
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
    if trigger.enemy_only and on_party_side(owner) == on_party_side(target):
        return None
    # The one a knockout reduced to 0 may well be dead: that's what it's for.
    if is_dead(target) and not isinstance(outcome, KnockoutOutcome):
        return None
    # What it gives lands on its owner (Shield) or its target (Prone).
    gets = owner if row.on_self else target
    conditions = gets.get("conditions") or []
    if row.conditions and all(c in conditions for c in row.conditions):
        return None
    automatic = not (
        trigger.optional
        or trigger.when
        or row.costs
        or row.takes_reaction
        or trigger.aim is not TriggerAim.TARGET
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


def _restores_anything(owner: dict, row: TriggerRow) -> bool:
    """Whether a row that heals or gives feature uses back would give owner
    anything now: Hit Points below its maximum, or a use to regain."""
    hurt = owner.get("hp", 0) < hit_point_maximum(owner)
    return (row.heals and hurt) or row.regainable > 0


def drop_firings(
    outcome: DropOutcome,
    rows_of: Callable[[dict], list[TriggerRow]],
    *,
    maximum: int,
) -> tuple[list[HitFiring], list[str]]:
    """What the creature `outcome`'s damage would drop to 0 Hit Points can
    use instead, before it drops (DROPS_TO_ZERO: Relentless Endurance's "you
    can drop to 1 Hit Point instead"): its rows of that event, each firing
    on itself. None if it's killed outright, the damage past 0 being at
    least its Hit Point maximum `maximum` (the rules' Instant Death, which
    the simulator doesn't apply itself: DI-002), said in the second list as
    rows with no uses left are. A row is AUTO when it isn't optional, has no
    `when` and costs nothing; otherwise ASK."""
    owner = outcome.target
    found: list[HitFiring] = []
    spent: list[str] = []
    for row in rows_of(owner):
        trigger = row.trigger
        if trigger.event is not TriggerEvent.DROPS_TO_ZERO:
            continue
        if row.takes_reaction and reaction_lack(owner) is not None:
            continue
        if outcome.left_over >= maximum > 0:
            spent.append(
                f"{row.name}: not when killed outright ({outcome.left_over}"
                f" damage past 0, Hit Point maximum {maximum})"
            )
            continue
        if row.uses is not None and row.uses[0] <= 0:
            spent.append(f"{row.name}: no uses left")
            continue
        automatic = not (
            trigger.optional or trigger.when or row.costs or row.takes_reaction
        )
        found.append(
            HitFiring(
                owner=owner,
                target=owner,
                row=row,
                mode=TriggerMode.AUTO if automatic else TriggerMode.ASK,
                why=f"if {trigger.when}" if trigger.when else "",
                outcome=outcome,
            )
        )
    return found, spent


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
