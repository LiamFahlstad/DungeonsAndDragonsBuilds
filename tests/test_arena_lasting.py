"""Areas that stay on the battle map (Combat/Arena/lasting.py; Notes/
combat-arena-plan.md, step 11), on plain combatant dicts: what an active
spell keeps, the cells it covers as its caster moves, who stands in it and
who walked in."""

import json

from Combat.Arena.areas import AreaOfEffect, AreaShape, area_cells
from Combat.Arena.arena import POSITION_KEY, ArenaSettings
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import (
    AREA_KEY,
    DEFAULT_AREA_COLOR,
    LastingArea,
    area_record,
    area_key,
    areas_at,
    areas_holding,
    entered,
    find_area,
    lasting_areas,
    record_area,
    time_left_text,
    who_is_in,
)

SETTINGS = ArenaSettings()
MOONBEAM = AreaOfEffect(AreaShape.CYLINDER, 5)
GUARDIANS = AreaOfEffect(AreaShape.EMANATION, 15)


def _at(name: str, col: int, row: int, **more) -> dict:
    return {"name": name, POSITION_KEY: [col, row], "conditions": [], **more}


def _holding(caster: dict, name: str, record: dict, concentration=True) -> dict:
    caster.setdefault("active_spells", []).append(
        {"name": name, "concentration": concentration, AREA_KEY: record}
    )
    return caster


def test_an_aimed_area_keeps_the_cells_it_was_put_on():
    cleric = _at("Clover", 2, 2)
    record = area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS, "#3498db")
    assert record["follows"] is False
    assert record["aim"] == [8, 8]
    assert record["color"] == "#3498db"
    assert record_area(record) == MOONBEAM
    _holding(cleric, "Moonbeam", record)
    cleric[POSITION_KEY] = [15, 3]  # the caster walks off; the beam stays
    (area,) = lasting_areas([cleric], SETTINGS)
    assert area == LastingArea(
        "Clover",
        "Moonbeam",
        frozenset({Cell(8, 8), Cell(7, 8), Cell(9, 8), Cell(8, 7), Cell(8, 9)}),
        "#3498db",
        True,
        record["key"],
    )
    assert area.title == "Clover's Moonbeam"
    json.dumps(cleric)  # what the fight state saves, as plain JSON


def test_an_emanation_follows_its_caster_and_leaves_it_out():
    cleric = _at("Clover", 5, 5)
    record = area_record(GUARDIANS, cleric, None, SETTINGS)
    assert record["follows"] is True
    assert record["cells"] == []
    assert record["color"] == DEFAULT_AREA_COLOR
    _holding(cleric, "Spirit Guardians", record)
    (here,) = lasting_areas([cleric], SETTINGS)
    assert Cell(5, 5) not in here.cells
    assert Cell(8, 5) in here.cells and Cell(9, 5) not in here.cells
    cleric[POSITION_KEY] = [12, 5]
    (there,) = lasting_areas([cleric], SETTINGS)
    assert Cell(8, 5) not in there.cells
    assert there.cells == frozenset(
        area_cells(GUARDIANS, cleric, None, SETTINGS)
    ), "worked out from where the caster is now"


def test_an_area_whose_caster_is_off_the_map_isnt_drawn():
    cleric = {"name": "Clover", "conditions": []}
    _holding(cleric, "Spirit Guardians", area_record(GUARDIANS, None, None, SETTINGS))
    assert lasting_areas([cleric], SETTINGS) == []


def test_an_active_spell_without_an_area_is_not_on_the_map():
    cleric = _at("Clover", 5, 5)
    cleric["active_spells"] = [{"name": "Bless", "concentration": True}]
    assert lasting_areas([cleric], SETTINGS) == []


def test_who_stands_in_an_area_by_any_of_their_cells():
    cleric = _at("Clover", 2, 2)
    _holding(cleric, "Moonbeam", area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS))
    ogre = _at("Ogre", 6, 7, size="Large")  # G8, H8, G9, H9: H9 is in the beam
    goblin = _at("Goblin", 12, 12)
    areas = lasting_areas([cleric, ogre, goblin], SETTINGS)
    assert [a.name for a in areas_holding(ogre, areas, SETTINGS)] == ["Moonbeam"]
    assert areas_holding(goblin, areas, SETTINGS) == []
    assert [a.name for a in areas_at(Cell(8, 9), areas)] == ["Moonbeam"]
    assert areas_at(Cell(10, 10), areas) == []


def test_entered_names_who_is_in_an_area_now_and_wasnt_before():
    cleric = _at("Clover", 5, 5)
    _holding(cleric, "Spirit Guardians", area_record(GUARDIANS, cleric, None, SETTINGS))
    goblin = _at("Goblin", 12, 5)
    orc = _at("Orc", 6, 5)
    chars = [cleric, goblin, orc]
    before = who_is_in(chars, SETTINGS)
    assert before == {
        "Clover": set(),
        "Goblin": set(),
        "Orc": {("Clover", "Spirit Guardians")},
    }
    cleric[POSITION_KEY] = [9, 5]  # the Emanation moves onto the goblin
    after = who_is_in(chars, SETTINGS)
    assert entered(before, after) == [("Goblin", ("Clover", "Spirit Guardians"))]
    assert entered(after, after) == []


def test_each_kept_area_has_a_key_to_find_it_by():
    cleric = _at("Clover", 2, 2)
    one = area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS, pick="Moonbeam")
    two = area_record(MOONBEAM, cleric, Cell(3, 9), SETTINGS)
    assert one["key"] != two["key"]
    assert one["pick"] == "Moonbeam"
    _holding(cleric, "Moonbeam", one)
    _holding(cleric, "Grease", two, concentration=False)
    first, second = lasting_areas([cleric], SETTINGS)
    assert (first.key, second.key) == (one["key"], two["key"])
    assert not first.selected
    caster, entry = find_area([cleric], two["key"])
    assert caster is cleric and entry["name"] == "Grease"
    assert find_area([cleric], "gone") is None


def test_a_kept_area_without_a_key_is_found_by_its_names():
    cleric = _at("Clover", 2, 2)
    record = area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS)
    del record["key"]
    _holding(cleric, "Moonbeam", record)
    assert area_key(cleric, cleric["active_spells"][0]) == "Clover/Moonbeam"
    assert find_area([cleric], "Clover/Moonbeam") is not None


def test_time_left_reads_in_the_biggest_unit_that_fits():
    assert time_left_text(3600) == "1 hour left"
    assert time_left_text(600) == "10 minutes left"
    assert time_left_text(60) == "1 minute left"
    assert time_left_text(54) == "9 rounds left"
    assert time_left_text(6) == "1 round left"
    assert time_left_text(0) == ""
    assert time_left_text(None) == ""
