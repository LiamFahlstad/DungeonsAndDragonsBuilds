"""The battle map in the combat window (Notes/combat-arena-plan.md, steps
3-5): positions and the map's settings are saved with a fight in progress and
come back when it's continued, players' too, undo puts a token back, and the
feet moved reset as a combatant's turn starts; tokens start on the map as the
fight does, are drawn from token rows, select and target as cards do, and G
switches between the cards and the map during combat only; tokens move by
dragging or by a click on a cell, one undo step each, with the reach shaded,
a GM-only log line, a warning past the Speed, and the "Not on the map"
strip for whoever has no place (step 6); and the target label and a hover
say how far the source is, in either view (step 7)."""

from functools import cache

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QPushButton

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
from tests._combat_ui import make_ui
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
    assert line["text"].endswith("Tiger moves 10 ft.")
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


def test_a_click_on_an_empty_cell_moves_the_source(tmp_path):
    ui = _arena_fight(tmp_path)
    ui._arena_cell(Cell(5, 5))
    assert "Select a combatant" in ui._status_label.text()
    draven = next(c for c in ui.characters if c.get("_is_player"))
    ui._select_character(draven)
    start = _at(draven)
    ui._arena_cell(_shifted(ui, start, 4))
    assert _at(draven) == _shifted(ui, start, 4)
    assert draven[MOVED_KEY] == 20


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
    ui._arena_cell(Cell(10, 4))
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
