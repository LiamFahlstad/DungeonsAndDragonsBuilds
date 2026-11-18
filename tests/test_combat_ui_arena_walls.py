"""Walls on the battle map (Notes/combat-arena-plan.md, step 25): a Wall
aimed in the area bar by its two ends (a ring by its middle), Wall of
Force blocking movement and giving Total Cover while it lasts without being
written into the map, and Wall of Fire's damaging side, picked by a third
click, acting on who ends a turn by it."""

from functools import cache

import pytest
from PyQt6.QtWidgets import QCheckBox, QDialog, QPushButton, QSpinBox

from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.areas import AreaShape
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import AREA_KEY, AreaPrompt, lasting_areas
from Combat.CombatUIQt.effect_options import effect_options
from Combat.Combatants import Pirate
from Combat.EncounterLogs import TURN_PREFIX
from Combat.Monsters.CR_1.monsters import Tiger
from tests._combat_ui import answer_out_of_resources, make_ui, qapp
from tests._snapshot_helpers import build

DRUID = "Y2024DruidLandRowanThistledownCharacterBuilder"
ROWAN = "Rowan Thistledown"


@cache
def _builds():
    return (build(DRUID),)


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Rowan (on its turn) at E6, the Pirate at I6, the Tiger at O9; the
    map in use. "Out of resources ... anyway?" is answered Yes."""
    answer_out_of_resources(monkeypatch)
    ui = make_ui(tmp_path, [Pirate(), Tiger()], list(_builds()))
    rolls = {ROWAN: "20", "Pirate": "15", "Tiger": "10"}
    for char in ui.characters:
        ui._initiative_inputs[id(char)].setText(rolls[char["name"]])
    ui._start_combat()
    rowan, pirate, tiger = (_named(ui, n) for n in (ROWAN, "Pirate", "Tiger"))
    rowan[POSITION_KEY] = [4, 5]
    pirate[POSITION_KEY] = [8, 5]
    tiger[POSITION_KEY] = [14, 8]
    ui.arena_settings.in_use = True
    ui._select_character(rowan)
    ui._set_targets([])
    ui._refresh_views()
    return ui, rowan, pirate, tiger


def _option(char: dict, name: str):
    return next(
        option
        for _, options in effect_options(char)
        for option in options
        if option.name == name
    )


def _logged(ui) -> list[str]:
    data = ui._read_log()
    lines = []
    for key, events in data.items():
        if key.startswith("round_") and isinstance(events, list):
            for event in events:
                match = TURN_PREFIX.match(str(event["text"]))
                lines.append(match.group(2) if match else str(event["text"]))
    return lines


def _applies(monkeypatch):
    """The dialog that opens again is applied as it opens."""
    monkeypatch.setattr(
        QDialog,
        "exec",
        lambda dlg: dlg.findChild(QPushButton, "primaryBtn").click() or 0,
    )


def _click(ui, cell: Cell):
    ui._arena_view.aim_area(cell)
    ui._area_picked(cell)


def _wall_entry(ui, caster: dict, name: str) -> dict:
    qapp().processEvents()  # the dialog opens again once the click is over
    (entry,) = [e for e in caster["active_spells"] if e["name"] == name]
    return entry


def _put_wall_of_force(ui, monkeypatch, rowan) -> dict:
    """Wall of Force down column G, from G1 to G16: between Rowan and the
    Pirate, across the whole map."""
    _applies(monkeypatch)
    assert ui._start_area_targeting(_option(rowan, "Wall of Force"))
    _click(ui, Cell(6, 0))
    _click(ui, Cell(6, 15))
    return _wall_entry(ui, rowan, "Wall of Force")


def test_a_wall_is_aimed_by_its_two_ends(fight, monkeypatch):
    ui, rowan, *_ = fight
    _applies(monkeypatch)
    assert ui._start_area_targeting(_option(rowan, "Wall of Force"))
    assert ui._area_shape.currentData() is AreaShape.WALL
    assert ui._area_size.value() == 100, "ten 10-foot panels"
    assert not ui._area_bar.findChild(QCheckBox, "areaRing").isHidden()
    assert ui._area_bar.findChild(QSpinBox, "areaWidth").isHidden()
    ui._arena_view.aim_area(Cell(6, 0))
    assert "click one end." in ui._area_label.text()
    ui._area_picked(Cell(6, 0))
    assert ui._area_targeting is not None, "still aiming: one end down"
    ui._arena_view.aim_area(Cell(6, 3))
    assert "click its other end (20 ft. long)." in ui._area_label.text()
    assert ui._arena_view.area_shown() == {Cell(6, r) for r in range(4)}
    ui._area_picked(Cell(6, 15))
    assert ui._area_targeting is None
    entry = _wall_entry(ui, rowan, "Wall of Force")
    record = entry[AREA_KEY]
    assert entry["concentration"]
    assert record["aim"] == [6, 0] and record["end"] == [6, 15]
    assert sorted(record["cells"]) == [[6, r] for r in range(16)]
    assert record["terrain"]["blocks"] and record["terrain"]["cover"] == "total"


def test_wall_of_force_blocks_and_covers_while_it_lasts(fight, monkeypatch):
    ui, rowan, pirate, _ = fight
    _put_wall_of_force(ui, monkeypatch, rowan)
    assert ui._map_settings().terrain.blocks(Cell(6, 5))
    assert not ui.arena_settings.terrain.blocks(Cell(6, 5)), "not painted in"
    reach = ui._arena_reach(ROWAN)
    assert reach and all(cell.col < 6 for cell in reach), "nothing past the wall"
    reading = ui._map_cover(rowan, pirate)
    assert reading.total and reading.by.startswith("Wall of Force at G")
    assert "Total Cover from Wall of Force" in ui._distance_note(pirate)
    ui._move_combatant(pirate, Cell(5, 5))  # no walk there: it went round
    assert any(
        "goes from I6 to F6, with no way to walk there" in l for l in _logged(ui)
    )
    # The fight's saved map has no wall in it.
    assert "terrain" not in (ui._read_log().get("arena") or {})


def test_ending_it_takes_the_wall_away_and_undo_brings_it_back(fight, monkeypatch):
    ui, rowan, pirate, _ = fight
    _put_wall_of_force(ui, monkeypatch, rowan)
    ui._select_character(rowan)
    ui._shortcut_remove_concentration()
    assert not ui._map_settings().terrain.blocks(Cell(6, 5))
    assert not ui._map_cover(rowan, pirate)
    assert any(c.col > 6 for c in ui._arena_reach(ROWAN))
    ui._undo_last()
    assert ui._map_settings().terrain.blocks(Cell(6, 5))
    ui._undo_last()  # and the cast itself
    assert not ui._map_settings().terrain.blocks(Cell(6, 5))


def test_wall_of_fire_picks_its_damaging_side_by_a_third_click(fight, monkeypatch):
    ui, rowan, pirate, tiger = fight
    _applies(monkeypatch)
    assert ui._start_area_targeting(_option(rowan, "Wall of Fire"))
    assert ui._area_size.value() == 60
    _click(ui, Cell(6, 0))
    _click(ui, Cell(6, 15))  # past its 60 ft.: it stops at G12
    assert ui._area_targeting is not None, "the side is still to pick"
    ui._arena_view.aim_area(Cell(9, 5))
    text = ui._area_label.text()
    assert "click the side that deals damage (the east side)" in text, text
    assert Cell(8, 5) in ui._arena_view.area_shown(), "the side shaded to pick"
    ui._area_picked(Cell(6, 5))  # on the wall's line: refused
    assert ui._area_targeting is not None
    assert "off the wall's line" in ui._status_label.text()
    _click(ui, Cell(9, 5))
    entry = _wall_entry(ui, rowan, "Wall of Fire")
    record = entry[AREA_KEY]
    assert sorted(record["cells"]) == [[6, r] for r in range(12)]
    assert record["side"] != 0
    near = {tuple(c) for c in record["side_cells"]}
    assert {(7, 5), (8, 5)} <= near and not {(5, 5), (9, 5), (6, 5)} & near
    assert "terrain" not in record, "fire doesn't block or cover"
    (area,) = lasting_areas(ui.characters, ui._map_settings())
    assert Cell(8, 5) in area.side
    if not ui._arena_shown():
        ui._toggle_view()
    ui._select_area(area.key)
    assert "the east side deals damage" in ui._area_panel_title.text()
    assert "from G1 to G12" in ui._area_panel_title.text()
    assert ui._area_panel.findChild(QPushButton, "areaPanelMoveBtn").isHidden()

    # The Pirate, 10 ft. from the damaging side, ends its turn there.
    ui._advance_turn()
    assert ui._current_turn_group()[0] is pirate
    ui._advance_turn()
    prompts = [p for p in ui._turn_prompts if isinstance(p, AreaPrompt)]
    (prompt,) = prompts
    assert prompt.target is pirate and prompt.beside
    assert prompt.prompt == (
        f"{ROWAN}'s Wall of Fire on Pirate (ended its turn by its damaging side)"
    )
    # The Tiger walks into the wall itself.
    ui._move_combatant(tiger, Cell(6, 8))
    entering = [
        p for p in ui._hit_prompts if isinstance(p, AreaPrompt) and p.target is tiger
    ]
    assert [p.when for p in entering] == ["enters"]


def test_a_ring_is_aimed_by_its_middle(fight, monkeypatch):
    ui, rowan, pirate, _ = fight
    _applies(monkeypatch)
    assert ui._start_area_targeting(_option(rowan, "Wall of Force"))
    ui._area_bar.findChild(QCheckBox, "areaRing").setChecked(True)
    assert ui._area_size.value() == 20, "a globe with a radius of up to 10 feet"
    ui._arena_view.aim_area(Cell(8, 5))
    assert "click its middle." in ui._area_label.text()
    ui._area_picked(Cell(8, 5))
    entry = _wall_entry(ui, rowan, "Wall of Force")
    record = entry[AREA_KEY]
    assert record["ring"] and record["end"] is None
    assert len(record["cells"]) == 8
    assert [8, 5] not in record["cells"], "the Pirate is inside, not in it"
    reach = ui._arena_reach("Pirate")
    assert set(reach) <= {Cell(8, 5), Cell(7, 5), Cell(9, 5), Cell(8, 4), Cell(8, 6)}
