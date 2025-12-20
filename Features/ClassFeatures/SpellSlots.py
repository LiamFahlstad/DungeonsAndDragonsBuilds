from enum import Enum
from Features.BaseFeatures import CharacterFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class CasterType(Enum):
    FULL_CASTER = 1
    HALF_CASTER = 2


def get_spell_slots_for_level(level: int, caster_type: CasterType) -> list[int]:

    if caster_type == CasterType.FULL_CASTER:
        pass
    if caster_type == CasterType.HALF_CASTER:
        level = (level + 1) // 2

    if level < 1 or level > 20:
        raise ValueError("Level must be between 1 and 20")

    if level == 1:
        return [2, 0, 0, 0, 0, 0, 0, 0, 0]
    elif level == 2:
        return [3, 0, 0, 0, 0, 0, 0, 0, 0]
    elif level == 3:
        return [4, 2, 0, 0, 0, 0, 0, 0, 0]
    elif level == 4:
        return [4, 3, 0, 0, 0, 0, 0, 0, 0]
    elif level == 5:
        return [4, 3, 2, 0, 0, 0, 0, 0, 0]
    elif level == 6:
        return [4, 3, 3, 0, 0, 0, 0, 0, 0]
    elif level == 7:
        return [4, 3, 3, 1, 0, 0, 0, 0, 0]
    elif level == 8:
        return [4, 3, 3, 2, 0, 0, 0, 0, 0]
    elif level == 9:
        return [4, 3, 3, 3, 1, 0, 0, 0, 0]
    elif level == 10:
        return [4, 3, 3, 3, 2, 0, 0, 0, 0]
    elif level == 11:
        return [4, 3, 3, 3, 2, 1, 0, 0, 0]
    elif level == 12:
        return [4, 3, 3, 3, 2, 1, 0, 0, 0]
    elif level == 13:
        return [4, 3, 3, 3, 2, 1, 1, 0, 0]
    elif level == 14:
        return [4, 3, 3, 3, 2, 1, 1, 0, 0]
    elif level == 15:
        return [4, 3, 3, 3, 2, 1, 1, 1, 0]
    elif level == 16:
        return [4, 3, 3, 3, 2, 1, 1, 1, 0]
    elif level == 17:
        return [4, 3, 3, 3, 2, 1, 1, 1, 1]
    elif level == 18:
        return [4, 3, 3, 3, 3, 1, 1, 1, 1]
    elif level == 19:
        return [4, 3, 3, 3, 3, 2, 1, 1, 1]
    else:  # level == 20
        return [4, 3, 3, 3, 3, 2, 2, 1, 1]


class SpellSlots(CharacterFeature):
    def __init__(self, caster_type: CasterType) -> None:
        self.caster_type = caster_type
        super().__init__()

    def modify(self, character_stat_block: CharacterStatBlock):

        spells_slots = get_spell_slots_for_level(
            character_stat_block.character_level, self.caster_type
        )

        spells_slots_dict = {}
        for i, slots in enumerate(spells_slots):
            if slots <= 0:
                continue
            spell_level = i + 1
            spells_slots_dict[spell_level] = slots
        character_stat_block.spell_slots = spells_slots_dict
