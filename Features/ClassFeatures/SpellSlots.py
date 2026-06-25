from enum import Enum

from Features.BaseFeatures import CharacterFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class CasterType(Enum):
    FULL_CASTER = 1
    HALF_CASTER = 2
    WARLOCK_CASTER = 3


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


def get_spell_slots_for_level(level: int, caster_type: CasterType) -> list[int]:
    if level < 1 or level > 20:
        raise ValueError("Level must be between 1 and 20")

    if caster_type == CasterType.WARLOCK_CASTER:
        return _WARLOCK_SLOTS[level - 1]

    if caster_type == CasterType.HALF_CASTER:
        level = (level + 1) // 2

    return _FULL_CASTER_SLOTS[level - 1]


class SpellSlots(CharacterFeature):
    def __init__(self, caster_type: CasterType) -> None:
        self.caster_type = caster_type
        super().__init__()

    def modify(self, character_stat_block: CharacterStatBlock):
        spells_slots = get_spell_slots_for_level(
            character_stat_block.character_level, self.caster_type
        )

        spells_slots_dict = {
            i + 1: slots
            for i, slots in enumerate(spells_slots)
            if slots > 0
        }
        character_stat_block.spell_slots = spells_slots_dict
