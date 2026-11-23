"""An attack roll checked against its target, Qt-free
(Notes/combat-ui-refactor-plan.md, step 5.3, attack rolls): the target's AC
with its cover and the modifiers its conditions and badges give, whether
the roll hits, and what a hit is (a Critical Hit, what the GM should check).
The combat window logs it and notes it for the players
(DamageMixin._resolve_attack_roll)."""

from dataclasses import dataclass

from Combat.Effects.modifiers import hit_notes, makes_critical_hit

from .attack_rolls import AttackRoll, armor_bonus, stored_armor
from .fight import Fight


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
