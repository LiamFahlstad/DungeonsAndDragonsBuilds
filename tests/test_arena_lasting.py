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
    DEFAULT_TIMING,
    ENDS,
    ENTERS,
    MOVED_ONTO,
    STARTS,
    AreaPrompt,
    LastingArea,
    MoveRule,
    area_record,
    area_timing,
    area_key,
    areas_at,
    areas_holding,
    entered,
    find_area,
    lasting_areas,
    move_rule,
    record_area,
    record_move,
    record_rules,
    record_timing,
    time_left_text,
    who_is_in,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Model.Content.ActionType import ActionType
from Model.Content.CombatArea import AreaTiming, CombatArea, CombatAreaShape
from Model.Content.CombatAreaText import read_move, read_timing

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


# The spells' own wording (Player's Handbook 2024), as their classes have it.
MOONBEAM_TEXT = (
    "Until the spell ends, Dim Light fills the Cylinder, and you can take a"
    " Magic action on later turns to move the Cylinder up to 60 feet.\nA"
    " creature also makes this save when the spell's area moves into its"
    " space and when it enters the spell's area or ends its turn there."
)
FLAMING_SPHERE_TEXT = (
    "Any creature that ends its turn within 5 feet of the sphere makes a"
    " Dexterity saving throw.\nAs a Bonus Action, you can move the sphere up"
    " to 30 feet, rolling it along the ground. If you move the sphere into a"
    " creature's space, that creature makes the save against the sphere."
)
WEB_TEXT = (
    "The first time a creature enters the webs on a turn or starts its turn"
    " there, it must succeed on a Dexterity saving throw."
)


def _timing(text: str) -> set[str]:
    return {when.value for when in read_timing(text)}


def test_when_an_area_acts_is_drafted_from_its_text():
    """For writing a spell's class (Model/Content/CombatAreaText.py)."""
    assert _timing(MOONBEAM_TEXT) == {ENTERS, MOVED_ONTO, ENDS}
    assert _timing(FLAMING_SPHERE_TEXT) == {MOVED_ONTO, ENDS}
    assert _timing(WEB_TEXT) == {ENTERS, MOVED_ONTO, STARTS}
    assert _timing("Any creature that starts its turn in the area") == {STARTS}
    assert read_timing("") == ()


def test_how_an_area_moves_is_drafted_from_its_text():
    assert read_move(MOONBEAM_TEXT) == (60, ActionType.ACTION)
    assert read_move(FLAMING_SPHERE_TEXT) == (30, ActionType.BONUS_ACTION)
    assert read_move(WEB_TEXT) == (None, None)


def test_when_an_area_acts_is_its_rules():
    moonbeam = SpellFactory.create("Moonbeam").combat_area
    assert area_timing(moonbeam) == {ENTERS, MOVED_ONTO, ENDS}
    sphere = SpellFactory.create("Flaming Sphere").combat_area
    assert area_timing(sphere) == {MOVED_ONTO, ENDS}
    web = SpellFactory.create("Web").combat_area
    assert area_timing(web) == {ENTERS, MOVED_ONTO, STARTS}
    plain = CombatArea(CombatAreaShape.SPHERE, 20)
    assert area_timing(plain) == area_timing(None) == DEFAULT_TIMING
    assert DEFAULT_TIMING == {ENTERS, STARTS}


def test_how_an_area_moves_is_its_rules():
    moonbeam = SpellFactory.create("Moonbeam").combat_area
    assert move_rule(moonbeam) == MoveRule(60, "Action")
    assert move_rule(moonbeam).text == "up to 60 ft., an Action"
    sphere = SpellFactory.create("Flaming Sphere").combat_area
    assert move_rule(sphere) == MoveRule(30, "Bonus Action")
    assert move_rule(sphere).text == "up to 30 ft., a Bonus Action"
    assert move_rule(SpellFactory.create("Web").combat_area) == MoveRule()
    assert move_rule(None) == MoveRule()
    assert MoveRule().text == ""


def test_a_kept_area_keeps_its_rules():
    rules = CombatArea(
        CombatAreaShape.CYLINDER,
        5,
        acts=(AreaTiming.ENDS,),
        move_ft=60,
        move_action=ActionType.ACTION,
    )
    cleric = _at("Clover", 2, 2)
    record = area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS, rules=rules)
    assert json.loads(json.dumps(record)) == record, "plain JSON"
    assert record_rules(record) == rules
    assert record_timing(record) == {ENDS}
    assert record_move(record) == MoveRule(60, "Action")
    bare = area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS)
    assert record_rules(bare) is None and record_timing(bare) == DEFAULT_TIMING


def test_a_kept_area_from_before_its_rules_were_kept_takes_its_spells():
    """A record logged before 2026-11-19 has no "rules": those of the spell
    it was picked as, or its active spell's name."""
    cleric = _at("Clover", 2, 2)
    record = area_record(MOONBEAM, cleric, Cell(8, 8), SETTINGS, pick="Moonbeam")
    del record["rules"]
    assert record_timing(record) == {ENTERS, MOVED_ONTO, ENDS}
    record["pick"] = ""
    assert record_move(record, "Flaming Sphere") == MoveRule(30, "Bonus Action")
    assert record_rules(record, "Not a spell") is None


def test_an_area_prompt_names_whose_area_whom_and_when():
    clover, goblin = {"name": "Clover"}, {"name": "Goblin"}
    prompt = AreaPrompt(clover, goblin, "Moonbeam", "k1", ENTERS)
    assert prompt.caster == "Clover"
    assert prompt.prompt == "Clover's Moonbeam on Goblin (entered it)"
    assert AreaPrompt(clover, goblin, "Web", "k2", STARTS).prompt == (
        "Clover's Web on Goblin (starts its turn in it)"
    )
    assert AreaPrompt(clover, goblin, "Moonbeam", "k1", ENDS).prompt == (
        "Clover's Moonbeam on Goblin (ended its turn in it)"
    )
