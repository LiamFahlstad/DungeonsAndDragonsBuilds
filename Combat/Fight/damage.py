"""Damage on a combatant, Qt-free (Notes/combat-ui-refactor-plan.md, step
5.3, damage): what its Immunity, Resistance and Vulnerability make of an
amount, and what taking it does to its Hit Points and the fight's
statistics. The combat window logs it and shows it (DamageMixin)."""

from dataclasses import dataclass

from Combat.Effects.modifiers import immune_to_damage, resists, vulnerable_to

from .stats import _default_stats, damage_dealt_key, damage_taken_key


def _damage_type_value(t) -> str:
    return t.value if hasattr(t, "value") else str(t)


def _entry_damage_types(entry) -> list:
    if isinstance(entry, dict):
        return entry.get("damage_types", [])
    return getattr(entry, "damage_types", [])


def damage_type_modifier(target: dict, dmg: int, damage_type: str):
    """Check target's damage immunities/resistances/vulnerabilities against
    damage_type and return (applied_dmg, outcome), outcome being one of
    'immune', 'resisted', 'vulnerable', 'resisted and vulnerable', or None.
    Immunity zeroes the damage; otherwise Resistance halves it (rounded
    down) and then Vulnerability doubles it, so both can apply."""

    def has_type(entries) -> bool:
        for entry in entries or []:
            if any(
                _damage_type_value(t) == damage_type for t in _entry_damage_types(entry)
            ):
                return True
        return False

    # A condition or a badge can give these too (Petrified's Resistance
    # to all damage, Stoneskin's, Heroes' Feast's Poison).
    if has_type(target.get("damage_immunities")) or immune_to_damage(
        target, damage_type
    ):
        return 0, "immune"
    resisted = has_type(target.get("damage_resistances")) or resists(
        target, damage_type
    )
    vulnerable = has_type(target.get("damage_vulnerabilities")) or vulnerable_to(
        target, damage_type
    )
    if resisted:
        dmg //= 2
    if vulnerable:
        dmg *= 2
    if resisted and vulnerable:
        return dmg, "resisted and vulnerable"
    if resisted:
        return dmg, "resisted"
    if vulnerable:
        return dmg, "vulnerable"
    return dmg, None


def damage_after_defenses(
    target: dict,
    amount: int,
    damage_type: str,
    check_resistance: bool,
    saved: bool,
) -> int:
    """What one damage type of a hit comes to on target: halved first if it
    saved, then its Immunity, Resistance and Vulnerability."""
    dmg = amount // 2 if saved else amount
    if check_resistance:
        dmg, _ = damage_type_modifier(target, dmg, damage_type)
    return dmg


@dataclass(frozen=True)
class DamageTaken:
    """What taking damage did: the damage, the change to Hit Points and to
    Temporary Hit Points, and whether it took the target to 0 Hit Points."""

    dmg: int
    hp_delta: int
    temp_delta: int
    knockout: bool


def take_damage(
    target: dict, dmg: int, damage_type: str, source: dict | None, floor: int = 0
) -> DamageTaken:
    """target takes `dmg` of `damage_type` (already through its defenses):
    its Temporary Hit Points first, and its Hit Points no lower than `floor`
    (what it drops to instead of 0: Relentless Endurance's 1). The target's
    damage taken and the source's damage dealt count it, and a knockout
    counts for both."""
    pre_hp = target["hp"]
    pre_temp = target["temp_hp"]

    temp_reduction = min(target["temp_hp"], dmg)
    target["temp_hp"] -= temp_reduction
    # Hit Points can't go below 0, nor below what it drops to instead.
    target["hp"] = max(floor, target["hp"] - (dmg - temp_reduction))

    knockout = pre_hp > 0 and target["hp"] <= 0

    target.setdefault("stats", _default_stats())
    target["stats"]["damage_taken"] = target["stats"].get("damage_taken", 0) + dmg
    taken_type_key = damage_taken_key(damage_type)
    target["stats"][taken_type_key] = target["stats"].get(taken_type_key, 0) + dmg
    if knockout:
        target["stats"]["times_downed"] = target["stats"].get("times_downed", 0) + 1

    if source is not None:
        source.setdefault("stats", _default_stats())
        source["stats"]["damage_dealt"] = source["stats"].get("damage_dealt", 0) + dmg
        type_key = damage_dealt_key(damage_type)
        source["stats"][type_key] = source["stats"].get(type_key, 0) + dmg
        if knockout:
            source["stats"]["knockouts"] = source["stats"].get("knockouts", 0) + 1

    return DamageTaken(
        dmg=dmg,
        hp_delta=target["hp"] - pre_hp,
        temp_delta=target["temp_hp"] - pre_temp,
        knockout=knockout,
    )
