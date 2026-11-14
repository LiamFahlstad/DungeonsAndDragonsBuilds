"""The battle map in the combat window (Notes/combat-arena-plan.md, steps
3-5): positions and the map's settings are saved with a fight in progress and
come back when it's continued, players' too, undo puts a token back, and the
feet moved reset as a combatant's turn starts; tokens start on the map as the
fight does, are drawn from token rows, select and target as cards do, and G
switches between the cards and the map during combat only; tokens move by
dragging or by a click on a cell, one undo step each, with the reach shaded,
a GM-only log line, a warning past the Speed, and the "Not on the map"
strip for whoever has no place (step 6); and the target label and a hover
say how far the source is, in either view (step 7). Then the fixes after
the user tried it (R9): an encounter's allies start on the party's side, a
click picks a token up and a click on a cell moves it, the move's line
says from where to where and how much movement is left, whose turn it is
stands on gold, and real clicks and Ctrl+Z work in both views."""

from functools import cache

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    QAbstractGraphicsShapeItem,
    QGraphicsRectItem,
    QPushButton,
)

from Combat.Arena.arena import MOVED_KEY, POSITION_KEY, ArenaSettings, footprint
from Combat.Arena.geometry import Cell
from Combat.CombatUIQt.arena_mixin import ARENA_PAGE, CARDS_PAGE
from Combat.CombatUIQt.arena_view import TokenRow, token_label, token_rows
from Combat.Combatants import Pirate
from Combat.CombatUIQt.undo import UndoPoint
from Combat.EncounterLogs import ARENA_KEY
from Combat.LogFiles import read_json, write_json
from Combat.PlayerLog import is_round_key
from Combat.Monsters.CR_1.monsters import Tiger
from tests._combat_ui import make_ui, qapp
from tests._snapshot_helpers import build

PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"


@cache
def _player():
    return build(PLAYER_BUILD)


def _fight(tmp_path):
    """Draven (20), the Pirate (15) and the Tiger (10), in combat."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()], [_player()])
    for char, roll in zip(ui.characters, ("20", "15", "10")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    return ui


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


def test_a_continued_fight_has_its_positions_and_map_back(tmp_path):
    ui = _fight(tmp_path)
    draven = next(c for c in ui.characters if c.get("_is_player"))
    draven[POSITION_KEY] = [0, 7]
    draven[MOVED_KEY] = 15
    _named(ui, "Pirate")[POSITION_KEY] = [23, 7]
    del _named(ui, "Tiger")[POSITION_KEY]  # as a log from before the map
    ui.arena_settings = ArenaSettings(width=30, height=20)
    ui._log_event("Something happens")  # a fight in progress is saved
    ui._save_fight_state()
    assert ui._read_log()[ARENA_KEY] == {
        "width": 30,
        "height": 20,
        "cell_ft": 5,
        "rule": "manhattan",
    }

    fresh = make_ui(tmp_path, [], [_player()])
    fresh._load_log_from_path(str(ui.log_file))
    assert fresh.phase == "COMBAT"
    player = next(c for c in fresh.characters if c.get("_is_player"))
    assert player[POSITION_KEY] == [0, 7]
    assert player[MOVED_KEY] == 15
    assert _named(fresh, "Pirate")[POSITION_KEY] == [23, 7]
    # Placed as the fight continues, against the right edge of its map (a
    # Large Tiger: its anchor is a column in).
    tiger_cells = footprint(_named(fresh, "Tiger"), fresh.arena_settings.distance_rule)
    assert max(c.col for c in tiger_cells) == 29
    assert fresh.arena_settings == ArenaSettings(width=30, height=20)


def test_a_log_without_a_map_gets_the_default_one(tmp_path):
    ui = _fight(tmp_path)
    ui._log_event("Something happens")
    data = read_json(ui.log_file)
    del data[ARENA_KEY]  # as a log from before the map has it
    write_json(ui.log_file, data)
    fresh = make_ui(tmp_path, [], [_player()])
    fresh.arena_settings = ArenaSettings(width=3, height=3)
    fresh._load_log_from_path(str(ui.log_file))
    assert fresh.arena_settings == ArenaSettings()


def test_undo_puts_a_token_back(tmp_path):
    ui = _fight(tmp_path)
    pirate = _named(ui, "Pirate")
    pirate[POSITION_KEY] = [5, 5]
    point = UndoPoint.capture(ui)
    pirate[POSITION_KEY] = [8, 5]
    pirate[MOVED_KEY] = 15
    assert point.changed_since(ui)
    point.restore(ui)
    assert pirate[POSITION_KEY] == [5, 5]
    assert MOVED_KEY not in pirate

    tiger = _named(ui, "Tiger")
    del tiger[POSITION_KEY]
    point = UndoPoint.capture(ui)
    tiger[POSITION_KEY] = [1, 1]
    point.restore(ui)
    assert POSITION_KEY not in tiger, "put on the map, then off it again"


def test_the_feet_moved_reset_as_its_turn_starts(tmp_path):
    ui = _fight(tmp_path)
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    pirate[MOVED_KEY] = 30
    tiger[MOVED_KEY] = 10
    ui._pass_turn()  # the Pirate's turn
    assert MOVED_KEY not in pirate
    assert tiger[MOVED_KEY] == 10, "the Tiger's turn hasn't started"


# ---------------------------------------------------------------------------
# Steps 4-5: the view and the switch


def test_starting_the_fight_puts_everyone_on_the_map(tmp_path):
    ui = _fight(tmp_path)
    rule = ui.arena_settings.distance_rule
    draven = next(c for c in ui.characters if c.get("_is_player"))
    assert draven[POSITION_KEY][0] == 0, "the party along the left edge"
    for name in ("Pirate", "Tiger"):  # against the right edge
        cells = footprint(_named(ui, name), rule)
        assert max(c.col for c in cells) == ui.arena_settings.width - 1
    cells = [cell for c in ui.characters for cell in footprint(c, rule)]
    assert len(cells) == len(set(cells)) == 1 + 1 + 4, "the Tiger is Large"


def test_token_letters():
    assert token_label("Goblin 2") == "G2"
    assert token_label("(1) Accursed Group of 5") == "A1"
    assert token_label("Accursed Group of 3") == "AG", "how many, not which"
    assert token_label("Hanna's Drake Companion") == "HD"
    assert token_label("Ogre") == "OG"


def test_token_rows_carry_what_the_cards_show():
    settings = ArenaSettings()
    hero = {"name": "Hero", "_is_player": True, "hp": 10, "max_hp": 20}
    hero[POSITION_KEY] = [0, 0]
    ogre = {"name": "Ogre", "size": "Large", "hp": 0, "max_hp": 59}
    ogre[POSITION_KEY] = [5, 5]
    ghost = {"name": "Ghost", "hp": 5, "max_hp": 5, "hidden_from_players": True}
    ghost[POSITION_KEY] = [9, 9]
    away = {"name": "Away", "hp": 5, "max_hp": 5}  # not on the map
    rows = token_rows([hero, ogre, ghost, away], settings, [hero], ogre, [ghost])
    assert [r.name for r in rows] == ["Hero", "Ogre", "Ghost"]
    by_name = {r.name: r for r in rows}
    assert by_name["Hero"] == TokenRow(
        name="Hero",
        label="HE",
        cells=(Cell(0, 0),),
        party=True,
        hp_fraction=0.5,
        turn=True,
    )
    assert len(by_name["Ogre"].cells) == 4
    assert by_name["Ogre"].source and by_name["Ogre"].down
    assert not by_name["Ogre"].party
    assert by_name["Ghost"].target and by_name["Ghost"].hidden


def test_g_switches_views_in_combat_only(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger()], [_player()])
    ui._toggle_view()  # on the initiative screen: nothing
    assert ui._view_stack.currentIndex() == CARDS_PAGE
    assert not ui.arena_view_on
    for char, roll in zip(ui.characters, ("20", "15", "10")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    assert ui._view_stack.currentIndex() == CARDS_PAGE
    ui._toggle_view()
    assert ui._view_stack.currentIndex() == ARENA_PAGE
    assert ui.arena_view_on, "remembered"
    assert ui._view_toggle_btn.text() == "Cards"
    assert len(ui._arena_view.rows) == 3
    ui._toggle_view()
    assert ui._view_stack.currentIndex() == CARDS_PAGE
    assert ui._view_toggle_btn.text() == "Arena"


def test_a_fight_opens_on_the_view_last_used(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger()], [_player()])
    ui.arena_view_on = True
    assert ui._view_stack.currentIndex() == CARDS_PAGE, "initiative is cards-only"
    for char, roll in zip(ui.characters, ("20", "15", "10")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    assert ui._view_stack.currentIndex() == ARENA_PAGE


def test_clicking_tokens_selects_and_targets_as_the_cards_do(tmp_path):
    ui = _fight(tmp_path)
    ui._toggle_view()
    rows = {r.name: r for r in ui._arena_view.rows}
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    none = Qt.KeyboardModifier.NoModifier
    ui._arena_view.click(rows["Pirate"], Qt.MouseButton.LeftButton, none)
    assert ui.selected_character is pirate
    ui._arena_view.click(rows["Tiger"], Qt.MouseButton.RightButton, none)
    assert ui.target_characters == [tiger]
    ctrl = Qt.KeyboardModifier.ControlModifier
    ui._arena_view.click(rows["Pirate"], Qt.MouseButton.RightButton, ctrl)
    assert ui.target_characters == [tiger, pirate]
    ui._refresh_views()
    shown = {r.name: r for r in ui._arena_view.rows}
    assert shown["Pirate"].source and shown["Pirate"].target
    assert shown["Tiger"].target and not shown["Tiger"].source


def test_a_click_finds_the_token_under_it(tmp_path):
    ui = _fight(tmp_path)
    ui._toggle_view()
    row = next(r for r in ui._arena_view.rows if r.name == "Tiger")
    shape = ui.arena_settings.distance_rule.shape
    x, y = shape.center(row.cells[0], 40.0)
    assert ui._arena_view.token_at(x, y) == row
    assert ui._arena_view.token_at(x - 5 * 40.0, y) is None


# ---------------------------------------------------------------------------
# Step 6: moving


def _arena_fight(tmp_path):
    """_fight on the Arena view, nobody selected."""
    ui = _fight(tmp_path)
    ui._toggle_view()
    ui.selected_character = None
    return ui


def _events(ui) -> list[dict]:
    data = read_json(ui.log_file)
    keys = sorted((k for k in data if is_round_key(k)), key=lambda k: int(k[6:]))
    return [e for k in keys for e in data[k]]


def _at(char) -> Cell:
    return Cell.of(char[POSITION_KEY])


def _shifted(ui, cell: Cell, cols: int, rows: int = 0) -> Cell:
    return ui.arena_settings.distance_rule.shape.offset(cell, cols, rows)


def _row(ui, name: str) -> TokenRow:
    ui._refresh_views()
    return next(r for r in ui._arena_view.rows if r.name == name)


def test_dragging_a_token_shades_its_reach_and_moves_it(tmp_path):
    ui = _arena_fight(tmp_path)
    tiger = _named(ui, "Tiger")  # Speed 40 ft.
    start = _at(tiger)
    ui._arena_view.pick_up(_row(ui, "Tiger"))
    reach = ui._arena_view.reach_shown()
    assert reach[start] == 0
    assert reach[_shifted(ui, start, -2)] == 10
    assert max(reach.values()) == 40
    ui._arena_view.drop(_shifted(ui, start, -2))
    assert _at(tiger) == _shifted(ui, start, -2)
    assert tiger[MOVED_KEY] == 10
    assert ui._arena_view.reach_shown() == {}, "put down"
    (line,) = [e for e in _events(ui) if "moves" in e["text"]]
    name = ui.arena_settings.distance_rule.shape.cell_name
    assert line["text"].endswith(
        f"Tiger moves from {name(start)} to {name(_shifted(ui, start, -2))}"
        " (10 ft.; 30 of 40 ft. left this turn)."
    )
    assert "action" not in line, "nothing replays from it"
    assert not line.get("public"), "GM-only"
    # Less is left of its Speed for the next one.
    ui._arena_view.pick_up(_row(ui, "Tiger"))
    assert max(ui._arena_view.reach_shown().values()) == 30


def test_no_speed_no_reach(tmp_path):
    """The Pirate is a plain combatant with no Speed: it reaches nothing,
    but the GM can still move it."""
    ui = _arena_fight(tmp_path)
    pirate = _named(ui, "Pirate")
    start = _at(pirate)
    ui._arena_view.pick_up(_row(ui, "Pirate"))
    assert ui._arena_view.reach_shown() == {start: 0}
    ui._arena_view.drop(_shifted(ui, start, -2))
    assert pirate[MOVED_KEY] == 10


def test_a_move_is_one_undo_step(tmp_path):
    ui = _arena_fight(tmp_path)
    pirate = _named(ui, "Pirate")
    start = _at(pirate)
    ui._move_combatant(pirate, _shifted(ui, start, -3))
    ui._undo_last()
    assert _at(pirate) == start
    assert MOVED_KEY not in pirate
    assert not [e for e in _events(ui) if "moves" in e["text"]]


def test_a_click_on_an_empty_cell_moves_nobody_by_itself(tmp_path):
    """Not even the source: a stray click mustn't move whoever's turn it
    is (R9)."""
    ui = _arena_fight(tmp_path)
    draven = _draven(ui)
    ui._select_character(draven)
    start = _at(draven)
    ui._arena_cell(_shifted(ui, start, 4))
    assert _at(draven) == start
    assert "Click a combatant, then the cell" in ui._status_label.text()


def test_a_token_picked_up_moves_to_the_cell_clicked(tmp_path):
    ui = _arena_fight(tmp_path)
    view, draven = ui._arena_view, _draven(ui)
    start = _at(draven)
    ui._arena_select(draven["name"])
    view.pick(draven["name"])
    assert view.reach_shown()[_shifted(ui, start, 4)] == 20, "its reach shaded"
    view.move_picked(_shifted(ui, start, 4))
    assert _at(draven) == _shifted(ui, start, 4)
    assert draven[MOVED_KEY] == 20
    assert view.picked is None and view.reach_shown() == {}, "put down"


def test_a_move_cant_end_on_someone_else(tmp_path):
    ui = _arena_fight(tmp_path)
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    start = _at(pirate)
    ui._move_combatant(pirate, _at(tiger))
    assert _at(pirate) == start
    assert "can't end a move there" in ui._status_label.text()
    assert not ui.history, "nothing to undo"


def test_going_past_the_speed_is_warned_about_not_refused(tmp_path):
    """Dash, a shove or Misty Step move a creature further (the plan's Q2)."""
    ui = _arena_fight(tmp_path)
    tiger = _named(ui, "Tiger")
    start = _at(tiger)
    ui._move_combatant(tiger, _shifted(ui, start, -9))
    assert _at(tiger) == _shifted(ui, start, -9)
    assert tiger[MOVED_KEY] == 45
    assert "Tiger moved 45 ft., Speed 40 ft." in ui._status_label.text()


def test_a_prone_creature_crawls(tmp_path):
    ui = _arena_fight(tmp_path)
    tiger = _named(ui, "Tiger")
    tiger["conditions"].append("Prone")
    start = _at(tiger)
    ui._arena_view.pick_up(_row(ui, "Tiger"))
    reach = ui._arena_view.reach_shown()
    assert reach[_shifted(ui, start, -4)] == 40
    assert _shifted(ui, start, -5) not in reach, "half as far"
    ui._arena_view.drop(_shifted(ui, start, -2))
    assert tiger[MOVED_KEY] == 20
    assert "crawls" in ui._status_label.text()


def test_whoever_has_no_place_is_put_on_the_map_from_the_strip(tmp_path):
    ui = _arena_fight(tmp_path)
    tiger = _named(ui, "Tiger")
    del tiger[POSITION_KEY]
    ui._refresh_views()
    buttons = ui._off_map_strip.findChildren(QPushButton)
    assert [b.text() for b in buttons] == ["Tiger"]
    assert not ui._off_map_strip.isHidden()
    buttons[0].click()
    assert ui.selected_character is tiger
    assert ui._arena_view.picked == "Tiger"
    ui._arena_view.move_picked(Cell(10, 4))
    assert _at(tiger) == Cell(10, 4)
    assert MOVED_KEY not in tiger, "placing isn't moving"
    ui._refresh_views()
    assert ui._off_map_strip.isHidden()
    ui._undo_last()
    assert POSITION_KEY not in tiger


def test_a_token_put_on_someone_goes_to_the_nearest_free_cell(tmp_path):
    ui = _arena_fight(tmp_path)
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    del pirate[POSITION_KEY]
    ui._move_combatant(pirate, _at(tiger))
    rule = ui.arena_settings.distance_rule
    assert not set(footprint(pirate, rule)) & set(footprint(tiger, rule))
    assert ui.arena_settings.on_map(_at(pirate))


def test_a_large_token_moves_by_the_cell_its_held_by(tmp_path):
    ui = _arena_fight(tmp_path)
    tiger = _named(ui, "Tiger")  # Large: 2 x 2
    start = _at(tiger)
    row = _row(ui, "Tiger")
    corner = _shifted(ui, start, 1, 1)  # its bottom-right cell
    assert corner in row.cells
    ui._arena_view.pick_up(row, corner)
    ui._arena_view.drop(_shifted(ui, corner, -3))
    assert _at(tiger) == _shifted(ui, start, -3)


def test_the_mouse_drags_a_token(tmp_path):
    """The view's own mouse handling: press on a token, move past the drag
    distance, release on a cell."""
    ui = _arena_fight(tmp_path)
    view = ui._arena_view
    view.resize(1000, 700)
    view.show()
    ui._refresh_views()
    pirate = _named(ui, "Pirate")
    start = _at(pirate)
    target = _shifted(ui, start, -3)
    viewport = view.viewport()
    assert viewport is not None
    begin = view.cell_center(start).toPoint()
    end = view.cell_center(target).toPoint()
    QTest.mousePress(
        viewport, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, begin
    )
    assert ui.selected_character is pirate, "a press selects, as a click does"
    QTest.mouseMove(viewport, begin + QPoint(10, 0))
    QTest.mouseMove(viewport, end)
    QTest.mouseRelease(
        viewport, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, end
    )
    assert _at(pirate) == target
    assert pirate[MOVED_KEY] == 15
    view.hide()


# ---------------------------------------------------------------------------
# Step 7: distances in the UI


def _placed(ui, name: str, cell: Cell) -> dict:
    char = _named(ui, name) if name != "Draven" else _draven(ui)
    char[POSITION_KEY] = cell.to_list()
    return char


def _draven(ui) -> dict:
    return next(c for c in ui.characters if c.get("_is_player"))


def test_the_target_label_says_how_far_the_target_is(tmp_path):
    ui = _fight(tmp_path)  # the Cards view: the label says it there too
    draven = _placed(ui, "Draven", Cell(2, 2))
    pirate = _placed(ui, "Pirate", Cell(5, 3))
    tiger = _placed(ui, "Tiger", Cell(2, 6))  # Large: (2..3, 6..7)
    ui._select_character(draven)
    ui._select_target_character(pirate)
    assert ui.target_label.text() == "Target: Pirate (20 ft.)"
    ui._select_target_character(tiger, ctrl=True)
    assert ui.target_label.text() == "Targets: Pirate (20 ft.), Tiger (20 ft.)"
    ui._select_target_character(draven)
    assert ui.target_label.text() == f"Target: {draven['name']}", "itself"


def test_the_target_label_follows_a_move(tmp_path):
    ui = _arena_fight(tmp_path)
    draven = _placed(ui, "Draven", Cell(2, 2))
    pirate = _placed(ui, "Pirate", Cell(8, 2))
    ui._select_character(draven)
    ui._select_target_character(pirate)
    assert ui.target_label.text() == "Target: Pirate (30 ft.)"
    ui._move_combatant(draven, Cell(6, 2))
    assert ui.target_label.text() == "Target: Pirate (10 ft.)"
    ui._undo_last()
    assert ui.target_label.text() == "Target: Pirate (30 ft.)"


def test_no_distance_without_a_source_or_off_the_map(tmp_path):
    ui = _fight(tmp_path)
    pirate = _named(ui, "Pirate")
    ui._clear_selection()
    ui._select_target_character(pirate)
    assert ui.target_label.text() == "Target: Pirate"
    ui._select_character(_draven(ui))
    del pirate[POSITION_KEY]
    ui._refresh_views()
    assert ui.target_label.text() == "Target: Pirate"


def test_hovering_says_how_far_from_the_source(tmp_path):
    ui = _arena_fight(tmp_path)
    draven = _placed(ui, "Draven", Cell(2, 2))
    _placed(ui, "Tiger", Cell(6, 2))  # Large: (6..7, 2..3)
    ui._refresh_views()
    view = ui._arena_view
    view.hover(Cell(4, 4))
    assert view.hover_text() is None, "no source yet"
    ui._select_character(draven)
    view.hover(Cell(4, 4))
    assert view.hover_text() == "20 ft."
    view.hover(Cell(7, 3))
    assert view.hover_text() == "20 ft.", "the Tiger: its nearest cell, (6, 2)"
    view.hover(Cell(2, 2))
    assert view.hover_text() is None, "the source itself"


# ---------------------------------------------------------------------------
# After the user tried it (R9)


def _click(ui, cell: Cell, button=Qt.MouseButton.LeftButton, modifiers=None):
    """A real click on `cell` of the shown map."""
    modifiers = modifiers or Qt.KeyboardModifier.NoModifier
    view = ui._arena_view
    viewport = view.viewport()
    assert viewport is not None
    QTest.mouseClick(viewport, button, modifiers, view.cell_center(cell).toPoint())
    qapp().processEvents()


def _shown_arena(tmp_path):
    ui = _arena_fight(tmp_path)
    ui._window.resize(1600, 1000)
    ui._window.show()
    qapp().processEvents()
    return ui


def test_a_click_picks_a_token_up_and_a_click_on_a_cell_moves_it(tmp_path):
    ui = _shown_arena(tmp_path)
    view, pirate = ui._arena_view, _named(ui, "Pirate")
    start = _at(pirate)
    _click(ui, start)
    assert ui.selected_character is pirate and view.picked == "Pirate"
    assert view.reach_shown() == {start: 0}, "no Speed: only its own cell"
    _click(ui, _shifted(ui, start, -3))
    assert _at(pirate) == _shifted(ui, start, -3)
    assert view.picked is None
    # Picked up and put down again, by a second click on it: nothing moves.
    _click(ui, _at(pirate))
    assert view.picked == "Pirate"
    _click(ui, _at(pirate))
    assert view.picked is None
    _click(ui, _shifted(ui, _at(pirate), -2))
    assert _at(pirate) == _shifted(ui, start, -3)
    ui._window.hide()


def test_another_source_or_escape_puts_the_token_down(tmp_path):
    ui = _shown_arena(tmp_path)
    view = ui._arena_view
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    _click(ui, _at(pirate))
    _click(ui, _at(tiger))
    assert view.picked == "Tiger", "the other one is picked up instead"
    ui._select_character(pirate)  # as Next Turn's source does
    ui._refresh_views()
    assert view.picked is None
    _click(ui, _at(tiger))
    ui._escape_pressed()
    ui._refresh_views()
    assert view.picked is None
    ui._window.hide()


def test_ctrl_z_takes_back_a_move_made_by_clicks(tmp_path):
    ui = _shown_arena(tmp_path)
    draven = _draven(ui)
    start = _at(draven)
    _click(ui, start)
    _click(ui, _shifted(ui, start, 2))
    assert _at(draven) == _shifted(ui, start, 2)
    QTest.keyClick(ui._window, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
    qapp().processEvents()
    assert _at(draven) == start
    assert MOVED_KEY not in draven
    assert _row(ui, draven["name"]).cells[0] == start, "the map shows it back"
    assert not [e for e in _events(ui) if "moves" in e["text"]]
    ui._window.hide()


def test_real_clicks_select_and_target_in_both_views(tmp_path):
    ui = _shown_arena(tmp_path)
    pirate, tiger = _named(ui, "Pirate"), _named(ui, "Tiger")
    ctrl = Qt.KeyboardModifier.ControlModifier
    _click(ui, _at(pirate))
    _click(ui, _at(tiger), Qt.MouseButton.RightButton)
    assert ui.selected_character is pirate and ui.target_characters == [tiger]
    _click(ui, _at(pirate), Qt.MouseButton.RightButton, ctrl)
    assert ui.target_characters == [tiger, pirate]
    # A quick second click is a double-click to Qt: it still counts.
    view = ui._arena_view
    viewport = view.viewport()
    assert viewport is not None
    QTest.mouseDClick(
        viewport,
        Qt.MouseButton.RightButton,
        ctrl,
        view.cell_center(_at(pirate)).toPoint(),
    )
    assert ui.target_characters == [tiger], "the second Ctrl+click took it off"

    ui._toggle_view()  # the cards
    card = ui._card_widgets[id(tiger)]
    QTest.mouseClick(card, Qt.MouseButton.LeftButton)
    QTest.mouseClick(ui._card_widgets[id(pirate)], Qt.MouseButton.RightButton)
    qapp().processEvents()
    assert ui.selected_character is tiger and ui.target_characters == [pirate]
    ui._toggle_view()  # and the map shows the same
    ui._refresh_views()
    rows = {r.name: r for r in ui._arena_view.rows}
    assert rows["Tiger"].source and rows["Pirate"].target
    ui._window.hide()


def test_whose_turn_it_is_stands_on_gold(tmp_path):
    """As the active card has a gold border on a gold tint."""
    from Combat.CombatUIQt.arena_view import _TURN, _TURN_CELL

    ui = _arena_fight(tmp_path)
    ui._refresh_views()
    view = ui._arena_view
    scene = view.scene()
    assert scene is not None
    shapes = [
        item for item in scene.items() if isinstance(item, QAbstractGraphicsShapeItem)
    ]
    tinted = [item for item in shapes if item.brush().color() == _TURN_CELL]
    (turn,) = [r for r in view.rows if r.turn]
    assert len(tinted) == len(turn.cells) == 1, "Draven's turn: his one cell"
    edged = [
        item
        for item in shapes
        if isinstance(item, QGraphicsRectItem)
        and item.pen().color() == _TURN
        and item.pen().widthF() == 2.0
    ]
    assert edged, "edged gold"


def test_an_encounters_allies_start_on_the_partys_side(tmp_path):
    """Greypaw and Harat fight alongside the party in Wrath of Durmor."""
    from Combat.Campaigns.CurseOfTheLich.encounters import CONFIG as CAMPAIGN
    from Combat.EncounterLogs import encounter_ally_names, prepared_log
    from Combat.Effects.triggers import on_party_side
    from Combat.Scenario import CombatScenario

    spec = next(e for e in CAMPAIGN.encounters if e.id == "wrath_of_durmor")
    scenario = CombatScenario.from_spec(spec, CAMPAIGN.party_spec)
    log = prepared_log(scenario, [])
    allies = encounter_ally_names(scenario)
    assert [n.split(" (")[0] for n in allies] == ["Greypaw", "Harat"]
    sides = {c["name"]: on_party_side(c) for c in log["combatants"]}
    assert all(sides[name] for name in allies)
    assert not sides["Goblin King"]

    from Combat.Arena.arena import place_new

    settings = ArenaSettings()
    place_new(log["combatants"], settings)
    by_name = {c["name"]: c for c in log["combatants"]}
    rule = settings.distance_rule
    for name in allies:
        assert min(c.col for c in footprint(by_name[name], rule)) == 0, name
    king = footprint(by_name["Goblin King"], rule)
    assert max(c.col for c in king) == settings.width - 1


def test_a_log_from_before_the_mark_gets_its_allies_marked(tmp_path):
    from Combat.Campaigns.CurseOfTheLich.encounters import CONFIG as CAMPAIGN
    from Combat.Effects.triggers import on_party_side
    from Combat.EncounterLogs import prepared_log, write_log
    from Combat.PartyAllies import ENCOUNTER_ALLY_KEY
    from Combat.Scenario import CombatScenario

    spec = next(e for e in CAMPAIGN.encounters if e.id == "wrath_of_durmor")
    scenario = CombatScenario.from_spec(spec, CAMPAIGN.party_spec)
    log = prepared_log(scenario, [])
    for char in log["combatants"]:
        char.pop(ENCOUNTER_ALLY_KEY, None)
    path = tmp_path / "old.json"
    write_log(path, log)
    ui = make_ui(tmp_path, [], [])
    ui._scenarios = [scenario]
    ui._load_log_from_path(str(path))
    greypaw = next(c for c in ui.characters if c["name"].startswith("Greypaw"))
    assert on_party_side(greypaw)
    assert not on_party_side(_named(ui, "Goblin King"))


def test_the_move_line_says_from_where_to_where_and_what_is_left():
    from Combat.CombatUIQt.arena_mixin import move_line

    settings = ArenaSettings()
    clover = {"name": "Clover", MOVED_KEY: 10}
    a1, b2 = Cell(0, 0), Cell(1, 1)
    assert (
        move_line(clover, a1, b2, 10, True, 30, settings)
        == "Clover moves from A1 to B2 (10 ft.; 20 of 30 ft. left this turn)."
    )
    clover[MOVED_KEY] = 30
    assert move_line(clover, a1, b2, 10, True, 30, settings).endswith(
        "(10 ft.; all of its 30 ft. Speed used)."
    )
    clover[MOVED_KEY] = 35
    assert move_line(clover, a1, b2, 10, True, 30, settings).endswith(
        "(10 ft.; 5 ft. past its 30 ft. Speed)."
    )
    assert (
        move_line(clover, a1, b2, 10, False, None, settings)
        == "Clover goes from A1 to B2, with no way to walk there"
        " (10 ft. in a straight line)."
    )
