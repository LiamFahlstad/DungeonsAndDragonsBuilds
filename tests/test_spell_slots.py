"""
Spell slot rules (CharacterContent/Features/ClassFeatures/SpellSlots.py).

Expected values are transcribed independently from the PHB tables, NOT read
back from the engine's own tables, so a typo in either shows up as a failure.

Known engine bugs are marked xfail(strict=True): they keep the suite green
while the bug exists and turn into a failure (prompting removal of the marker)
once it is fixed.
"""

import pytest

from CharacterContent.Features.ClassFeatures.SpellSlots import CasterType, SpellSlots
from Core.Definitions import CharacterClass, CreatureSize
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock

FULL, HALF, THIRD, WARLOCK = (
    CasterType.FULL_CASTER,
    CasterType.HALF_CASTER,
    CasterType.THIRD_CASTER,
    CasterType.WARLOCK_CASTER,
)

# PHB "Multiclass Spellcaster: Spell Slots per Spell Level" (= full caster table).
PHB_FULL_CASTER = {
    1: [2],
    2: [3],
    3: [4, 2],
    4: [4, 3],
    5: [4, 3, 2],
    6: [4, 3, 3],
    7: [4, 3, 3, 1],
    8: [4, 3, 3, 2],
    9: [4, 3, 3, 3, 1],
    10: [4, 3, 3, 3, 2],
    11: [4, 3, 3, 3, 2, 1],
    12: [4, 3, 3, 3, 2, 1],
    13: [4, 3, 3, 3, 2, 1, 1],
    14: [4, 3, 3, 3, 2, 1, 1],
    15: [4, 3, 3, 3, 2, 1, 1, 1],
    16: [4, 3, 3, 3, 2, 1, 1, 1],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}

# 2024 Paladin/Ranger class table.
PHB_HALF_CASTER = {
    1: [2],
    2: [2],
    3: [3],
    4: [3],
    5: [4, 2],
    6: [4, 2],
    7: [4, 3],
    8: [4, 3],
    9: [4, 3, 2],
    10: [4, 3, 2],
    11: [4, 3, 3],
    12: [4, 3, 3],
    13: [4, 3, 3, 1],
    14: [4, 3, 3, 1],
    15: [4, 3, 3, 2],
    16: [4, 3, 3, 2],
    17: [4, 3, 3, 3, 1],
    18: [4, 3, 3, 3, 1],
    19: [4, 3, 3, 3, 2],
    20: [4, 3, 3, 3, 2],
}

# Eldritch Knight / Arcane Trickster table.
PHB_THIRD_CASTER = {
    1: [],
    2: [],
    3: [2],
    4: [3],
    5: [3],
    6: [3],
    7: [4, 2],
    8: [4, 2],
    9: [4, 2],
    10: [4, 3],
    11: [4, 3],
    12: [4, 3],
    13: [4, 3, 2],
    14: [4, 3, 2],
    15: [4, 3, 2],
    16: [4, 3, 3],
    17: [4, 3, 3],
    18: [4, 3, 3],
    19: [4, 3, 3, 1],
    20: [4, 3, 3, 1],
}

# Warlock Pact Magic: level -> (slot count, slot level).
PHB_PACT_MAGIC = {
    1: (1, 1),
    2: (2, 1),
    3: (2, 2),
    4: (2, 2),
    5: (2, 3),
    6: (2, 3),
    7: (2, 4),
    8: (2, 4),
    9: (2, 5),
    10: (2, 5),
    11: (3, 5),
    12: (3, 5),
    13: (3, 5),
    14: (3, 5),
    15: (3, 5),
    16: (3, 5),
    17: (4, 5),
    18: (4, 5),
    19: (4, 5),
    20: (4, 5),
}


def as_slot_dict(slot_list: list[int]) -> dict[int, int]:
    return {level: count for level, count in enumerate(slot_list, start=1)}


def apply_casters(classes: list[tuple[CharacterClass, int, CasterType]]):
    """Build a bare stat block with the given class levels and apply each
    class's SpellSlots feature in order, as CharacterSheetData does."""
    level_per_class = {cls: level for cls, level, _ in classes}
    character = CharacterStatBlock(
        name="Test",
        character_subclass="Test",
        base_class=classes[0][0],
        level_per_class=level_per_class,
        abilities=AbilitiesStatBlock(10, 10, 10, 10, 10, 10),
        skills=SkillsStatBlock(),
        combat=CombatStatBlock(speed=30, size=CreatureSize.MEDIUM),
        saving_throws=SavingThrowsStatBlock(),
        spell_slots={},
    )
    for cls, _, caster_type in classes:
        SpellSlots(caster_type, cls).apply(character)
    return character


class TestSingleClassTables:
    @pytest.mark.parametrize("level", range(1, 21))
    def test_full_caster(self, level):
        character = apply_casters([(CharacterClass.WIZARD, level, FULL)])
        assert character.spell_slots == as_slot_dict(PHB_FULL_CASTER[level])

    @pytest.mark.parametrize("level", range(1, 21))
    def test_half_caster(self, level):
        character = apply_casters([(CharacterClass.PALADIN, level, HALF)])
        assert character.spell_slots == as_slot_dict(PHB_HALF_CASTER[level])

    @pytest.mark.parametrize("level", range(1, 21))
    def test_third_caster(self, level):
        character = apply_casters([(CharacterClass.FIGHTER, level, THIRD)])
        assert character.spell_slots == as_slot_dict(PHB_THIRD_CASTER[level])

    @pytest.mark.parametrize("level", range(1, 21))
    def test_warlock_pact_magic(self, level):
        character = apply_casters([(CharacterClass.WARLOCK, level, WARLOCK)])
        count, slot_level = PHB_PACT_MAGIC[level]
        assert character.pact_magic_slots == {slot_level: count}
        assert character.spell_slots == {}


class TestMulticlass:
    @pytest.mark.parametrize(
        "classes,caster_level",
        [
            # Full casters add their levels.
            (
                [(CharacterClass.WIZARD, 3, FULL), (CharacterClass.CLERIC, 2, FULL)],
                5,
            ),
            # Warlock levels never count toward shared slots.
            (
                [
                    (CharacterClass.WIZARD, 3, FULL),
                    (CharacterClass.WARLOCK, 3, WARLOCK),
                ],
                3,
            ),
            # Third casters: one third, rounded down.
            (
                [(CharacterClass.FIGHTER, 3, THIRD), (CharacterClass.WIZARD, 1, FULL)],
                2,
            ),
            (
                [(CharacterClass.FIGHTER, 5, THIRD), (CharacterClass.WIZARD, 2, FULL)],
                3,
            ),
            # Even half-caster levels: rounding direction doesn't matter.
            (
                [(CharacterClass.PALADIN, 4, HALF), (CharacterClass.WIZARD, 3, FULL)],
                5,
            ),
        ],
    )
    def test_combined_caster_level(self, classes, caster_level):
        character = apply_casters(classes)
        assert character.spell_slots == as_slot_dict(PHB_FULL_CASTER[caster_level])

    def test_warlock_multiclass_keeps_pact_magic(self):
        character = apply_casters(
            [(CharacterClass.WIZARD, 3, FULL), (CharacterClass.WARLOCK, 5, WARLOCK)]
        )
        assert character.pact_magic_slots == {3: 2}

    def test_odd_half_caster_level_rounds_up(self):
        character = apply_casters(
            [(CharacterClass.PALADIN, 3, HALF), (CharacterClass.WIZARD, 3, FULL)]
        )
        assert character.spell_slots == as_slot_dict(PHB_FULL_CASTER[5])

    def test_artificer_rounds_up(self):
        character = apply_casters(
            [(CharacterClass.ARTIFICER, 5, HALF), (CharacterClass.WIZARD, 1, FULL)]
        )
        assert character.spell_slots == as_slot_dict(PHB_FULL_CASTER[4])

    def test_two_level_one_half_casters(self):
        character = apply_casters(
            [(CharacterClass.PALADIN, 1, HALF), (CharacterClass.RANGER, 1, HALF)]
        )
        assert character.spell_slots == as_slot_dict(PHB_FULL_CASTER[2])
