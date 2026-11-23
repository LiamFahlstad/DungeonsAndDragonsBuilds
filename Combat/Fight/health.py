"""A combatant's health, Qt-free (Notes/combat-ui-refactor-plan.md, step
5.3, damage): whether it's alive, dying, Stable or dead; Hit Points and
Temporary Hit Points regained; and Death Saving Throws, rolled or failed
by damage at 0 Hit Points (2024 rules, Rules Glossary: Death Saving Throws,
Damage at 0 Hit Points, Temporary Hit Points). The combat window logs and
shows what these do (DamageMixin)."""

from dataclasses import dataclass

from Combat.Effects.modifiers import hit_point_maximum

from .stats import _default_stats

ALIVE = "alive"
DYING = "dying"
STABLE = "stabilized"
DEAD = "dead"
DEATH_SAVES_TO_END = 3


def death_state(char: dict) -> str:
    """ALIVE, DYING, STABLE or DEAD. Only player characters, and monsters or
    NPCs that opt in with `death_saves`, make Death Saving Throws; any other
    combatant at 0 Hit Points is dead. A summon whose Hit Points aren't set
    yet (max HP 0, TurnsMixin._hp_not_set) isn't."""
    if char["hp"] > 0 or char.get("max_hp", 1) <= 0:
        return ALIVE
    if not (char.get("_is_player") or char.get("death_saves", False)):
        return DEAD
    if char.get("death_saves_fail", 0) >= DEATH_SAVES_TO_END:
        return DEAD
    if char.get("death_saves_success", 0) >= DEATH_SAVES_TO_END:
        return STABLE
    return DYING


def _count(char: dict, key: str, amount: int):
    char.setdefault("stats", _default_stats())
    char["stats"][key] = char["stats"].get(key, 0) + amount


@dataclass(frozen=True)
class Regained:
    """Hit Points regained: how many, and whether it brought a creature at
    0 Hit Points to."""

    amount: int
    came_to: bool


def regain_hit_points(
    char: dict, heal: int, source: dict | None, *, counted: bool = True
) -> Regained:
    """char regains up to `heal` Hit Points (no more than its maximum),
    counted in both their statistics unless not `counted` (Hit Dice spent
    on a short rest, outside any fight). One at 0 Hit Points comes to, and
    its Death Saving Throws start over. The caller checks char isn't dead: a
    dead creature regains none until it's revived."""
    was_downed = death_state(char) != ALIVE
    pre_hp = char["hp"]
    char["hp"] = min(char["hp"] + heal, hit_point_maximum(char))
    amount = char["hp"] - pre_hp
    if counted:
        _count(char, "healing_received", amount)
        if source is not None:
            _count(source, "healing_done", amount)
    came_to = was_downed and char["hp"] > 0
    if came_to:
        char["death_saves_fail"] = 0
        char["death_saves_success"] = 0
    return Regained(amount, came_to)


def give_temp_hp(target: dict, amount: int, source: dict | None) -> int:
    """target gets `amount` Temporary Hit Points; they don't stack, so it
    keeps the higher of those and what it had. Both statistics count the
    amount given. Returns what it had before."""
    old = target.get("temp_hp", 0)
    target["temp_hp"] = max(old, amount)
    _count(target, "temp_hp_received", amount)
    if source is not None:
        _count(source, "temp_hp_granted", amount)
    return old


def revive(char: dict):
    """char, dead, comes back with 1 Hit Point (Revivify, Raise Dead): its
    Death Saving Throws start over."""
    char["hp"] = 1
    char["death_saves_fail"] = 0
    char["death_saves_success"] = 0


def _fail(char: dict, failures: int) -> bool:
    """char fails `failures` Death Saving Throws; True if that kills it."""
    pre_fail = char.get("death_saves_fail", 0)
    char["death_saves_fail"] = min(pre_fail + failures, DEATH_SAVES_TO_END)
    newly_dead = pre_fail < DEATH_SAVES_TO_END <= char["death_saves_fail"]
    if newly_dead:
        _count(char, "deaths", 1)
    return newly_dead


def fail_death_save(char: dict) -> bool:
    """char fails one Death Saving Throw; True if it's the third."""
    return _fail(char, 1)


def succeed_death_save(char: dict) -> bool:
    """char succeeds on one Death Saving Throw; True if it's the third, and
    char is Stable."""
    char["death_saves_success"] = min(
        char.get("death_saves_success", 0) + 1, DEATH_SAVES_TO_END
    )
    return char["death_saves_success"] >= DEATH_SAVES_TO_END


@dataclass(frozen=True)
class ZeroHitPointDamage:
    """What damage did to a creature already at 0 Hit Points."""

    failures: int  # Death Saving Throws failed: 1, or 2 for a Critical Hit
    massive: bool  # at least its Hit Point maximum: it dies
    ends_stable: bool  # it was Stable, and isn't any more
    newly_dead: bool


def damage_at_zero_hp(char: dict, damage: int, critical: bool) -> ZeroHitPointDamage:
    """char, dying or Stable at 0 Hit Points, takes `damage`: one failed
    Death Saving Throw, two from a Critical Hit, and death if the damage is
    at least its Hit Point maximum. A Stable creature stops being Stable:
    its saves start over with these failures."""
    ends_stable = death_state(char) == STABLE
    if ends_stable:
        char["death_saves_fail"] = char["death_saves_success"] = 0
    failures = 2 if critical else 1
    massive = damage >= hit_point_maximum(char)
    newly_dead = _fail(char, DEATH_SAVES_TO_END if massive else failures)
    return ZeroHitPointDamage(failures, massive, ends_stable, newly_dead)
