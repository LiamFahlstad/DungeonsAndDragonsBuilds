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
from Core.Definitions import CharacterClass
from Core.SpellcastingRules import calculate_slot_progression
from Model.AbilityScores import AbilityScores
from Model.Character import Character
from Model.CharacterSources import CharacterSources
from Model.ClassLevels import ClassLevels

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
    class's SpellSlots feature in order, as Character does."""
    level_per_class = {cls: level for cls, level, _ in classes}
    sources = CharacterSources(
        class_levels=ClassLevels(
            base_class=classes[0][0], level_per_class=level_per_class
        ),
        base_abilities=AbilityScores(10, 10, 10, 10, 10, 10),
        base_speed=30,
    )
    for cls, _, caster_type in classes:
        sources.add_effect(SpellSlots(caster_type, cls))
    return Character(sources)


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


def gained_at(table: dict[int, list[int]]) -> dict[int, list[int]]:
    """From a PHB slots-per-level table: spell level -> the character level
    each slot of that level is gained at."""
    result: dict[int, list[int]] = {}
    for level in range(1, 21):
        for spell_level, count in enumerate(table[level], start=1):
            gained = result.setdefault(spell_level, [])
            gained += [level] * (count - len(gained))
    return result


class TestSlotProgression:
    def test_full_caster(self):
        progression = calculate_slot_progression(
            {CharacterClass.WIZARD: FULL}, [CharacterClass.WIZARD] * 20
        )
        assert progression.spell_slots == gained_at(PHB_FULL_CASTER)
        # Spelled out from the PHB table, as the sheet prints it.
        assert progression.spell_slots == {
            1: [1, 1, 2, 3],
            2: [3, 3, 4],
            3: [5, 5, 6],
            4: [7, 8, 9],
            5: [9, 10, 18],
            6: [11, 19],
            7: [13, 20],
            8: [15],
            9: [17],
        }
        assert progression.pact_magic_slots == []

    def test_half_caster(self):
        progression = calculate_slot_progression(
            {CharacterClass.PALADIN: HALF}, [CharacterClass.PALADIN] * 20
        )
        assert progression.spell_slots == gained_at(PHB_HALF_CASTER)

    def test_third_caster(self):
        progression = calculate_slot_progression(
            {CharacterClass.FIGHTER: THIRD}, [CharacterClass.FIGHTER] * 20
        )
        assert progression.spell_slots == gained_at(PHB_THIRD_CASTER)

    def test_warlock_pact_magic(self):
        progression = calculate_slot_progression(
            {CharacterClass.WARLOCK: WARLOCK}, [CharacterClass.WARLOCK] * 20
        )
        expected_gained = []
        expected_slot_levels = []
        for level, (count, slot_level) in PHB_PACT_MAGIC.items():
            expected_gained += [level] * (count - len(expected_gained))
            if not expected_slot_levels or expected_slot_levels[-1][1] != slot_level:
                expected_slot_levels.append((level, slot_level))
        assert progression.pact_magic_slots == expected_gained
        assert progression.pact_magic_slot_levels == expected_slot_levels
        assert progression.spell_slots == {}

    def test_class_with_no_levels_yet_adds_no_slots(self):
        """Wizard 1-3, then Warlock: Pact Magic starts at character level 4
        (Warlock 1), and the Warlock levels add no shared slots."""
        progression = calculate_slot_progression(
            {CharacterClass.WIZARD: FULL, CharacterClass.WARLOCK: WARLOCK},
            [CharacterClass.WIZARD] * 3 + [CharacterClass.WARLOCK] * 17,
        )
        assert progression.spell_slots == {1: [1, 1, 2, 3], 2: [3, 3]}
        assert progression.pact_magic_slots == [4, 5, 14, 20]
        assert progression.pact_magic_slot_levels[0] == (4, 1)

    def test_character_carries_on_in_latest_class(self):
        character = apply_casters([(CharacterClass.WIZARD, 3, FULL)])
        for level in (1, 2, 3):
            character.class_levels.record_class_level(level, CharacterClass.WIZARD)
        progression = character.get_slot_progression()
        assert progression is not None
        assert progression.spell_slots == gained_at(PHB_FULL_CASTER)

    def test_character_without_level_history_has_no_progression(self):
        character = apply_casters([(CharacterClass.WIZARD, 3, FULL)])
        assert character.get_slot_progression() is None
