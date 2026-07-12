from enum import Enum

import Definitions
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


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

    # Single half-caster: use ceiling division to match the official half-caster table.
    # Multiple casters: PHB multiclass rule says "half your levels (rounded down)".
    single_half_caster = (
        len(non_warlock) == 1
        and next(iter(non_warlock.values())) == CasterType.HALF_CASTER
    )

    total = 0
    for cls, ct in non_warlock.items():
        level = level_per_class.get(cls, 0)
        if ct == CasterType.FULL_CASTER:
            total += level
        elif ct == CasterType.HALF_CASTER:
            total += (level + 1) // 2 if single_half_caster else level // 2
        elif ct == CasterType.THIRD_CASTER:
            total += level // 3
    return total


class SpellSlots(Feature):
    def __init__(
        self, caster_type: CasterType, character_class: Definitions.CharacterClass
    ) -> None:
        self.caster_type = caster_type
        self.character_class = character_class
        super().__init__()

    def apply(self, character_stat_block: CharacterStatBlock):
        character_stat_block._caster_registry[self.character_class] = self.caster_type

        if self.caster_type == CasterType.WARLOCK_CASTER:
            warlock_level = character_stat_block.get_class_level(self.character_class)
            warlock_slots = _WARLOCK_SLOTS[warlock_level - 1]
            character_stat_block.pact_magic_slots = {
                i + 1: count for i, count in enumerate(warlock_slots) if count > 0
            }
            return

        # A lone third-caster doesn't follow the "one third of levels" multiclass rule
        # against the full-caster table (e.g. Monk level 4 gives 2nd-level prepared
        # spells, not the level-1 full-caster slot count) -- it has its own table.
        non_warlock = {
            cls: ct
            for cls, ct in character_stat_block._caster_registry.items()
            if ct != CasterType.WARLOCK_CASTER
        }
        single_third_caster = (
            len(non_warlock) == 1
            and next(iter(non_warlock.values())) == CasterType.THIRD_CASTER
        )
        if single_third_caster:
            third_caster_level = character_stat_block.get_class_level(
                self.character_class
            )
            third_caster_slots = _THIRD_CASTER_SLOTS[third_caster_level - 1]
            character_stat_block.spell_slots = {
                i + 1: count for i, count in enumerate(third_caster_slots) if count > 0
            }
            return

        effective_level = _compute_effective_caster_level(
            character_stat_block._caster_registry,
            character_stat_block.level_per_class,
        )
        if effective_level < 1:
            return
        character_stat_block.spell_slots = {
            i + 1: count
            for i, count in enumerate(_FULL_CASTER_SLOTS[effective_level - 1])
            if count > 0
        }
