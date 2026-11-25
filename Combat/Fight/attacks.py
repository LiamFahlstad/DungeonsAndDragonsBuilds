"""An attack roll checked against its target, Qt-free
(Notes/combat-ui-refactor-plan.md, step 5.3, attack rolls): the target's AC
with its cover and the modifiers its conditions and badges give, whether
the roll hits, and what a hit is (a Critical Hit, what the GM should check).
resolve_attack_roll logs it, notes it for the players and uses up the
badges the roll used (R46), and settle_answered_hit does what the target's
answers to a hit did. Asking for those answers, and applying them, is still
the window's (TurnPanelMixin._before_hit), as a trigger's row applies
through its Use / Cast apply path."""

from collections.abc import Callable
from dataclasses import dataclass

from Combat.Effects.modifiers import hit_notes, makes_critical_hit, used_up_by_attack
from Combat.Effects.triggers import AttackOutcome, HitFiring, still_hits

from .attack_rolls import (
    AttackRoll,
    armor_bonus,
    armor_in_use,
    cover_bonus,
    note_attack_roll,
    stored_armor,
)
from .cascade import remove_condition
from .fight import Fight
from .monster_actions import first_number, roll_dice
from .player_knowledge import _player_names, _seen
from .step import Step


@dataclass(frozen=True)
class AttackCheck:
    """How an attack roll went against one target."""

    # Whether it hit; None when the target has no AC to check against.
    hit: bool | None
    # The target as the roll read it: its own cover and the map's.
    seen: dict
    # Its stored AC (None: none), and what its cover, conditions and badges
    # add to it.
    armor: int | None
    bonus: int
    critical: bool
    # How it was rolled, then what the GM should check about a hit.
    notes: tuple[str, ...]


def check_attack(
    fight: Fight,
    target: dict,
    roll: AttackRoll,
    source: dict | None,
    notes: tuple[str, ...] = (),
    ignores_cover: bool = False,
) -> AttackCheck:
    """`roll` by source against target's AC, with its cover (its own, and
    the map's from source) and modifiers. A hit, or a roll that can't be
    checked, notes what the GM should check (hit_notes) and is a Critical
    Hit on a natural 20 or by what the target has from within 5 feet
    (Paralyzed, Unconscious). `ignores_cover`: the attack ignores Half and
    Three-Quarters Cover."""
    seen = fight.covered(source, target, ignores_cover=ignores_cover)
    armor = stored_armor(seen)
    bonus = armor_bonus(seen)
    hit = roll.hits(None if armor is None else armor + bonus)
    critical = roll.is_critical
    if hit is not False:
        feet = fight.distance_ft(source, target)
        notes = (*notes, *hit_notes(target, feet))
        critical = critical or makes_critical_hit(target, feet)
    return AttackCheck(hit, seen, armor, bonus, critical, notes)


# ---- The roll made, logged ----

# How an attack roll went, as the log says it; None is no AC to check against.
_VERDICTS: dict[bool | None, str] = {
    True: "hits",
    False: "misses",
    None: "can't be checked against",
}


def resolve_attack_roll(
    step: Step,
    target: dict,
    roll: AttackRoll,
    source: dict | None,
    notes: tuple[str, ...] = (),
    ignores_cover: bool = False,
) -> tuple[bool | None, str]:
    """Check `roll` against target's AC, with its cover (its own, and the
    map's from source: Fight.covered) and modifiers, and log how it went, with
    `notes` on how it was rolled (attack_plan's) and what the GM should
    check about a hit. `ignores_cover`: the attack ignores Half and
    Three-Quarters Cover. Returns whether it hit, None with no AC to
    check, and how it went against the AC, for the status line (Total
    Cover warned about there, not refused). The log doesn't say the AC, as the Limited view's players read
    it too. They don't learn from a hidden attacker's roll, which they
    never saw."""
    check = check_attack(step.fight, target, roll, source, notes, ignores_cover)
    seen, armor, bonus, hit = check.seen, check.armor, check.bonus, check.hit
    # A player's summon is seen as its owner is, even while Invisible.
    if source is None or _seen(source, _player_names(step.fight.characters)):
        # Noted against the stored AC's first number, so a Shield set
        # down counts as what changed it, like cover.
        first = first_number(target.get("ac"))
        seen_bonus = bonus if armor is None or first is None else armor + bonus - first
        note_attack_roll(target, roll, hit, seen_bonus)
    is_critical, notes = check.critical, check.notes
    name = target["name"]
    attacker = f"{source['name']}'s attack roll" if source else "Attack roll"
    critical = " (critical hit)" if is_critical else ""
    noted = f", {', '.join(notes)}" if notes else ""
    step.log(
        f"{attacker} of {roll.text} {_VERDICTS[hit]} {name}{critical}{noted}",
        character=name,
    )
    use_up_badges(step, source, target)
    warning = step.fight.cover_warning(source, target)
    if warning:
        notes = (*notes, warning)
    why = f" ({'; '.join(notes)})" if notes else ""
    if armor is None:
        return hit, f"{name} has no AC to check{why}"
    cover = " with cover" if cover_bonus(seen) else ""
    faced = f"AC {armor + bonus}{cover}"
    word = "hit" if hit else "miss"
    return hit, f"{name}: {roll.text} vs {faced}, {word}{why}"


def use_up_badges(
    step: Step,
    attacker: dict | None,
    target: dict | None,
    remove: Callable[[dict, str], object] | None = None,
):
    """End the badges an attack roll by attacker against target has used
    up (used_up_by_attack: Sap's Disadvantage, Vex's and Guiding Bolt's
    Advantage, each for one roll), a log line each, in the roll's undo
    step. Called once the roll is made, in each path that makes one.
    `remove` takes a badge off instead of remove_condition: the window's
    @undoable one, for a monster's action button, whose roll has no undo
    step of its own (DamageMixin._use_up_badges)."""
    for char, name in used_up_by_attack(attacker, target):
        if name not in char.get("conditions", []):
            continue
        step.log(f"{char['name']}'s {name} is used up", character=char["name"])
        if remove is None:
            remove_condition(step, char, name)
        else:
            remove(char, name)
        step.result.change(char)


# ---- What the one hit answered it with ----


def settle_answered_hit(
    step: Step,
    outcome: AttackOutcome,
    answered: list[tuple[HitFiring, int | None]],
    notes: list[str],
) -> tuple[bool, int]:
    """What the target's answers to a hit did, once applied (the window
    asks and applies them: TurnPanelMixin._before_hit): the damage each
    takes off (Deflect Attacks' roll, or what was rolled at the table for
    it), logged, and whether the attack still hits, checked against the AC
    the answers left (Shield's +5). Adds a line to `notes` when it's a miss
    now. Returns (still hits, the damage to take off)."""
    reduction = 0
    target = outcome.target
    for firing, at_table in answered:
        dice = firing.row.damage_reduction
        if dice:
            amount = roll_dice(dice) if at_table is None else at_table
            how = dice if at_table is None else f"{dice}, rolled at the table"
            reduction += amount
            step.log(
                f"{target['name']}'s {firing.row.name} takes {amount} off"
                f" the damage ({how})",
                character=target["name"],
            )
    hits = still_hits(
        outcome, armor_in_use(step.fight.covered(outcome.attacker, target))
    )
    if not hits:
        step.log(
            f"{outcome.attacker['name']}'s attack roll now misses" f" {target['name']}",
            character=target["name"],
        )
        notes.append(f"{target['name']}: now a miss")
    return hits, reduction
