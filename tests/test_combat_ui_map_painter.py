"""The Map Painter (Notes/map-painter-plan.md): painting with the real mouse
(a drag paints, a right-drag clears, Shift+drag fills a block, Ctrl+Z takes
a stroke back), starting cells, unsaved changes asked about; the window
opening it on the encounter that's open and saving it beside the logs; a
fight starting on the painted map with everyone where the map says, and a
continued fight keeping its own; saving mid-fight as one undo step that
moves whoever stands in a new wall; and the fight's map reading the paint:
the hover, the target label's Obscured, hazard reminders and walls that
refuse a move."""

from dataclasses import replace

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Combat.Arena.arena import ArenaSettings, distance_ft, footprint, position
from Combat.Arena.geometry import Cell
from Combat.Arena.maps import MapDesign, map_path, read_map, write_map
from Combat.Arena.terrain import DARK, WALL, MapObject, Spot
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.map_painter import (
    GROUND_TAB,
    HEIGHT_TAB,
    LIGHT_TAB,
    OBJECT_TAB,
    START_TAB,
    MapPainterDialog,
)
from Combat.Combatants import Pirate
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerLog import is_round_key
from Combat.Scenario import CombatScenario
from tests._combat_ui import open_dialog, qapp

CAVE = CombatScenario(
    name="cave",
    title="The Cave",
    combatants=lambda: [Pirate(), Tiger()],
    players=[],
    monster_summary=["Pirate", "Tiger"],
)
BRIDGE = CombatScenario(
    name="bridge",
    title="The Bridge",
    combatants=lambda: [Pirate()],
    players=[],
    monster_summary=["Pirate"],
)


def _window(tmp_path) -> CombatAppQt:
    qapp()
    ui = CombatAppQt(
        [],
        [],
        combat_log_dir=tmp_path / "CombatLogs",
        scenario_name=None,
        scenarios=[CAVE, BRIDGE],
    )
    ui._build_window()
    return ui


def _cave_map(tmp_path) -> MapDesign:
    """A 12 x 10 cave: a wall at F6, the Pirate starting at D5, the Tiger at
    I3 (covering I3-J4)."""
    design = MapDesign(
        ArenaSettings(width=12, height=10),
        {"Pirate": Cell(3, 4), "Tiger": Cell(8, 2)},
    )
    design.settings.terrain.put(Cell(5, 5), Spot(ground=WALL))
    write_map(map_path(tmp_path / "CombatLogs", "cave"), design)
    return design


def _fight(tmp_path) -> CombatAppQt:
    """The Cave, in combat: the Pirate (15), then the Tiger (10)."""
    ui = _window(tmp_path)
    ui._load_encounter(CAVE, restart=False)
    for char, roll in zip(ui.characters, ("15", "10")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    return ui


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


def _gm_lines(ui) -> list[str]:
    log = ui._read_log()
    return [
        event.get("text", "")
        for key in log
        if is_round_key(key)
        for event in log[key]
        if isinstance(event, dict)
    ]


def _painter(saved: list | None = None, design: MapDesign | None = None, roster=()):
    """A painter on its own, on one encounter, shown so the mouse reaches it."""
    qapp()
    store = {"cave": design or MapDesign(ArenaSettings(width=12, height=10))}

    def save(encounter_id, painted):
        store[encounter_id] = painted
        if saved is not None:
            saved.append((encounter_id, painted))

    dialog = MapPainterDialog(
        None,
        [("cave", "The Cave"), ("bridge", "The Bridge")],
        "cave",
        lambda encounter_id: (
            store.get(encounter_id, MapDesign()).copy(),
            list(roster),
        ),
        save,
    )
    dialog.show()
    qapp().processEvents()
    return dialog


def _drag(dialog, cells, button=Qt.MouseButton.LeftButton, modifiers=None):
    """A real drag over `cells`, pressed on the first, let go on the last."""
    modifiers = modifiers or Qt.KeyboardModifier.NoModifier
    view = dialog.view
    viewport = view.viewport()
    points = [view.cell_center(cell).toPoint() for cell in cells]
    QTest.mousePress(viewport, button, modifiers, points[0])
    for point in points[1:]:
        QTest.mouseMove(viewport, point)
    QTest.mouseRelease(viewport, button, modifiers, points[-1])
    qapp().processEvents()


@pytest.fixture(autouse=True)
def nothing_asked(monkeypatch):
    """Unsaved changes are kept unless a test answers otherwise."""
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No
    )


# ---------------------------------------------------------------------------
# Painting


def test_a_drag_paints_walls_and_a_right_drag_clears_them():
    dialog = _painter()
    terrain = dialog.design.settings.terrain
    dialog.tabs.setCurrentIndex(GROUND_TAB)
    dialog.pick_choice(WALL)
    _drag(dialog, [Cell(2, 2), Cell(3, 2), Cell(4, 2)])
    assert {c for c in terrain.cells if terrain.blocks(c)} == {
        Cell(2, 2),
        Cell(3, 2),
        Cell(4, 2),
    }
    assert dialog.dirty and dialog.windowTitle().endswith("*")
    _drag(dialog, [Cell(3, 2)], Qt.MouseButton.RightButton)
    assert set(dialog.design.settings.terrain.cells) == {Cell(2, 2), Cell(4, 2)}
    dialog.view.hover(Cell(2, 2))
    assert dialog.view.hover_text() == "C3 · Wall"


def test_shift_drag_fills_a_block_shown_while_it_is_dragged():
    dialog = _painter()
    dialog.tabs.setCurrentIndex(LIGHT_TAB)
    dialog.pick_choice(DARK)
    view, viewport = dialog.view, dialog.view.viewport()
    shift = Qt.KeyboardModifier.ShiftModifier
    start, end = view.cell_center(Cell(1, 5)).toPoint(), view.cell_center(Cell(3, 6))
    QTest.mousePress(viewport, Qt.MouseButton.LeftButton, shift, start)
    QTest.mouseMove(viewport, end.toPoint())
    assert len(view.block_shown()) == 6
    assert not dialog.design.settings.terrain, "nothing painted until let go"
    QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, shift, end.toPoint())
    terrain = dialog.design.settings.terrain
    assert len(terrain.cells) == 6
    assert all(terrain.at(c).light == DARK for c in terrain.cells)
    assert not view.block_shown()


def test_each_tab_paints_its_own_layer_and_ctrl_z_takes_strokes_back():
    dialog = _painter()
    cell = Cell(5, 5)
    dialog.tabs.setCurrentIndex(HEIGHT_TAB)
    dialog.height_value.setValue(15)
    dialog.paint([cell])
    dialog.tabs.setCurrentIndex(OBJECT_TAB)
    campfire = MapObject("Campfire", hazard=True)
    dialog.set_object(campfire)
    dialog.paint([cell])
    spot = dialog.design.settings.terrain.at(cell)
    assert (spot.height_ft, spot.thing) == (15, campfire), "the layers stack"
    dialog.paint([cell], erase=True)
    assert dialog.design.settings.terrain.at(cell).height_ft == 15, "only its own"
    QTest.keyClick(dialog, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
    assert dialog.design.settings.terrain.at(cell).thing == campfire
    dialog.undo()
    dialog.undo()
    assert not dialog.design.settings.terrain
    dialog.undo()
    assert dialog.status.text() == "Nothing to undo."


def test_a_smaller_map_crops_what_is_saved():
    saved = []
    dialog = _painter(saved)
    dialog.paint([Cell(10, 8)])  # a wall, the Ground tab's first choice
    dialog.width_spin.setValue(8)
    dialog.save()
    ((_, design),) = saved
    assert design.settings.width == 8
    assert not design.settings.terrain
    assert not dialog.dirty


def test_starting_cells_are_clicked_in_list_order():
    roster = [
        {"name": "Pirate", "size": "Medium"},
        {"name": "Tiger", "size": "Large"},
        {"name": "Clover", "_is_player": True},
    ]
    dialog = _painter(roster=roster)
    dialog.paint([Cell(0, 0)])  # a wall
    dialog.tabs.setCurrentIndex(START_TAB)
    assert dialog.picked_start() == "Pirate"
    _drag(dialog, [Cell(0, 0)])
    assert "can't start there" in dialog.status.text()
    _drag(dialog, [Cell(2, 2), Cell(3, 3)])
    assert dialog.design.starts == {"Pirate": Cell(2, 2)}, "a click, not a drag"
    assert dialog.picked_start() == "Tiger", "the next one not placed"
    _drag(dialog, [Cell(1, 1)])
    assert "someone else's cells" in dialog.status.text(), "a Large one"
    _drag(dialog, [Cell(6, 1)])
    assert dialog.design.starts["Tiger"] == Cell(6, 1)
    rows = {row.name: row for row in dialog.start_rows()}
    assert len(rows["Tiger"].cells) == 4
    assert "Clover" not in rows, "not placed yet"
    _drag(dialog, [Cell(7, 2)], Qt.MouseButton.RightButton)
    assert "Tiger" not in dialog.design.starts, "a right-click on any of its cells"
    _drag(dialog, [Cell(2, 2)])
    assert dialog.picked_start() == "Pirate", "a click on a token picks it"


def test_unsaved_changes_are_asked_about(monkeypatch):
    saved = []
    dialog = _painter(saved)
    dialog.paint([Cell(1, 1)])
    dialog.reject()  # answered No
    assert dialog.isVisible()
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Save
    )
    dialog.encounter_combo.setCurrentIndex(1)
    assert dialog.encounter == "bridge"
    assert [encounter for encounter, _ in saved] == ["cave"]
    assert not dialog.design.settings.terrain, "the Bridge has no map yet"
    dialog.encounter_combo.setCurrentIndex(0)
    assert dialog.design.settings.terrain.blocks(Cell(1, 1)), "saved"


# ---------------------------------------------------------------------------
# The window


def test_the_painter_opens_on_the_encounter_that_is_open(tmp_path, monkeypatch):
    ui = _window(tmp_path)
    dialog = open_dialog(monkeypatch, ui._show_map_painter)
    assert isinstance(dialog, MapPainterDialog)
    assert dialog.encounter == "cave", "none open: the first"
    assert [c["name"] for c in ui._painter_roster("bridge")] == ["Pirate"]
    ui._load_encounter(BRIDGE, restart=False)
    opened: list[QDialog] = []
    monkeypatch.setattr(QDialog, "exec", lambda dlg: opened.append(dlg) or 0)
    ui._map_painter_shortcut.activated.emit()
    (dialog,) = opened
    assert dialog.encounter == "bridge"


def test_saving_puts_the_map_beside_the_logs(tmp_path, monkeypatch):
    ui = _window(tmp_path)
    dialog = open_dialog(monkeypatch, ui._show_map_painter)
    dialog.paint([Cell(4, 4)])
    dialog.save_and_close()
    design = read_map(tmp_path / "Maps" / "cave.json")
    assert design is not None and design.settings.terrain.blocks(Cell(4, 4))


def test_a_fight_starts_on_its_painted_map(tmp_path):
    design = _cave_map(tmp_path)
    ui = _fight(tmp_path)
    # Its starting cells put the map in use (the arena plan's Decision 29).
    assert ui.arena_settings.in_use
    assert replace(ui.arena_settings, in_use=False) == design.settings
    assert position(_named(ui, "Pirate")) == Cell(3, 4)
    assert position(_named(ui, "Tiger")) == Cell(8, 2)
    ui._log_event("Something happens")

    # Painted again later: a fight continued keeps the map it started on.
    changed = design.copy()
    changed.settings.width = 20
    write_map(map_path(tmp_path / "CombatLogs", "cave"), changed)
    again = _window(tmp_path)
    again._load_encounter(CAVE, restart=False)
    assert again.phase == "COMBAT"
    assert again.arena_settings == ui.arena_settings  # in use too


def test_starts_painted_before_the_fight_are_where_it_starts(tmp_path, monkeypatch):
    ui = _window(tmp_path)
    ui._load_encounter(CAVE, restart=False)
    assert ui.phase == "INITIATIVE"
    dialog = open_dialog(monkeypatch, ui._show_map_painter)
    dialog.tabs.setCurrentIndex(START_TAB)
    dialog.pick_start("Tiger")
    dialog.paint([Cell(10, 3)])
    dialog.save_and_close()
    for char, roll in zip(ui.characters, ("15", "10")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    assert position(_named(ui, "Tiger")) == Cell(10, 3)


def test_painting_mid_fight_is_one_undo_step(tmp_path, monkeypatch):
    ui = _fight(tmp_path)  # no map: the default one
    tiger = _named(ui, "Tiger")
    start = position(tiger)
    cells = footprint(tiger, ui.arena_settings.distance_rule)
    dialog = open_dialog(monkeypatch, ui._show_map_painter)
    dialog.paint(cells)  # walls under the Tiger
    dialog.save_and_close()
    assert all(ui.arena_settings.terrain.blocks(cell) for cell in cells)
    moved = footprint(tiger, ui.arena_settings.distance_rule)
    assert all(ui.arena_settings.standable(cell) for cell in moved)
    assert any("Moved to make room: Tiger." in line for line in _gm_lines(ui))
    ui._undo_last()
    assert not ui.arena_settings.terrain
    assert position(tiger) == start
    assert not any("battle map changes" in line for line in _gm_lines(ui))


# ---------------------------------------------------------------------------
# The fight on a painted map


def test_the_hover_names_what_is_painted(tmp_path):
    _cave_map(tmp_path)
    ui = _fight(tmp_path)
    ui._clear_selection()  # the source followed the turn to the Pirate
    assert ui._arena_distance(Cell(5, 5)) == "Wall"
    ui._select_character(_named(ui, "Pirate"))
    assert ui._arena_distance(Cell(5, 5)) == "15 ft. · Wall"


def test_the_target_label_says_when_a_target_is_obscured(tmp_path):
    design = _cave_map(tmp_path)
    design.settings.terrain.put(Cell(3, 4), Spot(light=DARK))
    write_map(map_path(tmp_path / "CombatLogs", "cave"), design)
    ui = _fight(tmp_path)
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    ui._select_character(tiger)
    ui._select_target_character(pirate)
    feet = distance_ft(tiger, pirate, ui.arena_settings)
    assert ui.target_label.text() == f"Target: Pirate ({feet} ft., Heavily Obscured)"


def test_a_hazard_is_a_reminder_on_entering_and_at_a_turn_start(tmp_path):
    design = _cave_map(tmp_path)
    design.settings.terrain.put(
        Cell(6, 2), Spot(thing=MapObject("Campfire", hazard=True))
    )
    write_map(map_path(tmp_path / "CombatLogs", "cave"), design)
    ui = _fight(tmp_path)
    tiger = _named(ui, "Tiger")
    ui._move_combatant(tiger, Cell(6, 2))
    line = "Tiger enters a hazard: Campfire at G3."
    assert line in ui._status_label.text()
    assert any(line in text for text in _gm_lines(ui)), "a GM-only line"
    ui._turn_start_notes.clear()
    ui._remind_lasting_areas([tiger])
    assert ui._turn_start_notes == ["Tiger starts its turn in Campfire at G3."]


def test_a_wall_refuses_a_move(tmp_path):
    _cave_map(tmp_path)
    ui = _fight(tmp_path)
    tiger = _named(ui, "Tiger")
    ui._move_combatant(tiger, Cell(4, 4))  # its 2 x 2 would cover the wall at F6
    assert position(tiger) == Cell(8, 2)
    assert "a wall" in ui._status_label.text()


def test_the_fight_map_draws_the_paint(tmp_path):
    _cave_map(tmp_path)
    ui = _fight(tmp_path)
    ui._toggle_view()
    view = ui._arena_view
    tips = [item.toolTip() for item in view.scene().items()]
    assert "F6\nWall" in tips
