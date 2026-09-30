"""Spell slot tables and the multiclass caster-level rule.

Plain rules data with no dependency on features or stat blocks, so the stat
block can work out slots on read from whichever casters have been registered
(Character.register_caster) - in any order.
"""

from enum import Enum

import Core.Definitions as Definitions


class CasterType(Enum):
    FULL_CASTER = 1
    HALF_CASTER = 2
    WARLOCK_CASTER = 3
    THIRD_CASTER = 4


_FULL_CASTER_SLOTS = [
    [2, 0, 0, 0, 0, 0, 0, 0, 0],  # level 1
    [3, 0, 0, 0, 0, 0, 0, 0, 0],  # level 2
    [4, 2, 0, 0, 0, 0, 0, 0, 0],  # level 3
    [4, 3, 0, 0, 0, 0, 0, 0, 0],  # level 4
    [4, 3, 2, 0, 0, 0, 0, 0, 0],  # level 5
    [4, 3, 3, 0, 0, 0, 0, 0, 0],  # level 6
    [4, 3, 3, 1, 0, 0, 0, 0, 0],  # level 7
    [4, 3, 3, 2, 0, 0, 0, 0, 0],  # level 8
    [4, 3, 3, 3, 1, 0, 0, 0, 0],  # level 9
    [4, 3, 3, 3, 2, 0, 0, 0, 0],  # level 10
    [4, 3, 3, 3, 2, 1, 0, 0, 0],  # level 11
    [4, 3, 3, 3, 2, 1, 0, 0, 0],  # level 12
    [4, 3, 3, 3, 2, 1, 1, 0, 0],  # level 13
    [4, 3, 3, 3, 2, 1, 1, 0, 0],  # level 14
    [4, 3, 3, 3, 2, 1, 1, 1, 0],  # level 15
    [4, 3, 3, 3, 2, 1, 1, 1, 0],  # level 16
    [4, 3, 3, 3, 2, 1, 1, 1, 1],  # level 17
    [4, 3, 3, 3, 3, 1, 1, 1, 1],  # level 18
    [4, 3, 3, 3, 3, 2, 1, 1, 1],  # level 19
    [4, 3, 3, 3, 3, 2, 2, 1, 1],  # level 20
]

_WARLOCK_SLOTS = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0],  # level 1
    [2, 0, 0, 0, 0, 0, 0, 0, 0],  # level 2
    [0, 2, 0, 0, 0, 0, 0, 0, 0],  # level 3
    [0, 2, 0, 0, 0, 0, 0, 0, 0],  # level 4
    [0, 0, 2, 0, 0, 0, 0, 0, 0],  # level 5
    [0, 0, 2, 0, 0, 0, 0, 0, 0],  # level 6
    [0, 0, 0, 2, 0, 0, 0, 0, 0],  # level 7
    [0, 0, 0, 2, 0, 0, 0, 0, 0],  # level 8
    [0, 0, 0, 0, 2, 0, 0, 0, 0],  # level 9
    [0, 0, 0, 0, 2, 0, 0, 0, 0],  # level 10
    [0, 0, 0, 0, 3, 0, 0, 0, 0],  # level 11
    [0, 0, 0, 0, 3, 0, 0, 0, 0],  # level 12
    [0, 0, 0, 0, 3, 0, 0, 0, 0],  # level 13
    [0, 0, 0, 0, 3, 0, 0, 0, 0],  # level 14
    [0, 0, 0, 0, 3, 0, 0, 0, 0],  # level 15
    [0, 0, 0, 0, 3, 0, 0, 0, 0],  # level 16
    [0, 0, 0, 0, 4, 0, 0, 0, 0],  # level 17
    [0, 0, 0, 0, 4, 0, 0, 0, 0],  # level 18
    [0, 0, 0, 0, 4, 0, 0, 0, 0],  # level 19
    [0, 0, 0, 0, 4, 0, 0, 0, 0],  # level 20
]

_THIRD_CASTER_SLOTS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],  # level 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0],  # level 2
    [2, 0, 0, 0, 0, 0, 0, 0, 0],  # level 3
    [3, 0, 0, 0, 0, 0, 0, 0, 0],  # level 4
    [3, 0, 0, 0, 0, 0, 0, 0, 0],  # level 5
    [3, 0, 0, 0, 0, 0, 0, 0, 0],  # level 6
    [4, 2, 0, 0, 0, 0, 0, 0, 0],  # level 7
    [4, 2, 0, 0, 0, 0, 0, 0, 0],  # level 8
    [4, 2, 0, 0, 0, 0, 0, 0, 0],  # level 9
    [4, 3, 0, 0, 0, 0, 0, 0, 0],  # level 10
    [4, 3, 0, 0, 0, 0, 0, 0, 0],  # level 11
    [4, 3, 0, 0, 0, 0, 0, 0, 0],  # level 12
    [4, 3, 2, 0, 0, 0, 0, 0, 0],  # level 13
    [4, 3, 2, 0, 0, 0, 0, 0, 0],  # level 14
    [4, 3, 2, 0, 0, 0, 0, 0, 0],  # level 15
    [4, 3, 3, 0, 0, 0, 0, 0, 0],  # level 16
    [4, 3, 3, 0, 0, 0, 0, 0, 0],  # level 17
    [4, 3, 3, 0, 0, 0, 0, 0, 0],  # level 18
    [4, 3, 3, 1, 0, 0, 0, 0, 0],  # level 19
    [4, 3, 3, 1, 0, 0, 0, 0, 0],  # level 20
]


def get_spell_slots_for_level(level: int, caster_type: CasterType) -> list[int]:
    if level < 1 or level > 20:
        raise ValueError("Level must be between 1 and 20")

    if caster_type == CasterType.WARLOCK_CASTER:
        return _WARLOCK_SLOTS[level - 1]

    if caster_type == CasterType.THIRD_CASTER:
        return _THIRD_CASTER_SLOTS[level - 1]

    if caster_type == CasterType.HALF_CASTER:
        level = (level + 1) // 2

    return _FULL_CASTER_SLOTS[level - 1]


def _compute_effective_caster_level(registry: dict, level_per_class: dict) -> int:
    non_warlock = {
        cls: ct for cls, ct in registry.items() if ct != CasterType.WARLOCK_CASTER
    }
    if not non_warlock:
        return 0

    # 2024 PHB multiclassing: "half your levels (round up) in Paladin and
    # Ranger" - the same ceiling division that reproduces the single-class
    # half-caster table. (Artificer has always rounded up.) The 2014 PHB
    # rounded Paladin/Ranger down; the base classes here follow 2024.
    total = 0
    for cls, ct in non_warlock.items():
        level = level_per_class.get(cls, 0)
        if ct == CasterType.FULL_CASTER:
            total += level
        elif ct == CasterType.HALF_CASTER:
            total += (level + 1) // 2
        elif ct == CasterType.THIRD_CASTER:
            total += level // 3
    return total


def calculate_spell_slots(
    casters: dict[Definitions.CharacterClass, CasterType],
    level_per_class: dict[Definitions.CharacterClass, int],
) -> tuple[dict[int, int], dict[int, int]]:
    """(shared spell slots, Pact Magic slots) for a character with `casters`,
    each keyed by spell level."""

    def by_spell_level(counts: list[int]) -> dict[int, int]:
        return {i + 1: count for i, count in enumerate(counts) if count > 0}

    pact_magic_slots: dict[int, int] = {}
    for character_class, caster_type in casters.items():
        if caster_type == CasterType.WARLOCK_CASTER:
            warlock_level = level_per_class.get(character_class, 0)
            pact_magic_slots = by_spell_level(_WARLOCK_SLOTS[warlock_level - 1])

    non_warlock = {
        cls: ct for cls, ct in casters.items() if ct != CasterType.WARLOCK_CASTER
    }
    # A lone third-caster doesn't follow the "one third of levels" multiclass rule
    # against the full-caster table (e.g. Monk level 4 gives 2nd-level prepared
    # spells, not the level-1 full-caster slot count) -- it has its own table.
    if len(non_warlock) == 1:
        ((character_class, caster_type),) = non_warlock.items()
        if caster_type == CasterType.THIRD_CASTER:
            third_caster_level = level_per_class.get(character_class, 0)
            return (
                by_spell_level(_THIRD_CASTER_SLOTS[third_caster_level - 1]),
                pact_magic_slots,
            )

    effective_level = _compute_effective_caster_level(casters, level_per_class)
    if effective_level < 1:
        return {}, pact_magic_slots
    return by_spell_level(_FULL_CASTER_SLOTS[effective_level - 1]), pact_magic_slots
