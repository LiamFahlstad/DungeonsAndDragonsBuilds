"""The battle map in the combat window (Notes/combat-arena-plan.md, steps
3-5): positions and the map's settings are saved with a fight in progress and
come back when it's continued, players' too, undo puts a token back, and the
feet moved reset as a combatant's turn starts; tokens start on the map as the
fight does, are drawn from token rows, select and target as cards do, and G
switches between the cards and the map during combat only."""

from functools import cache

from PyQt6.QtCore import Qt

from Combat.Arena.arena import MOVED_KEY, POSITION_KEY, ArenaSettings, footprint
from Combat.Arena.geometry import Cell
from Combat.CombatUIQt.arena_mixin import ARENA_PAGE, CARDS_PAGE
from Combat.CombatUIQt.arena_view import TokenRow, token_label, token_rows
from Combat.Combatants import Pirate
from Combat.CombatUIQt.undo import UndoPoint
from Combat.EncounterLogs import ARENA_KEY
from Combat.LogFiles import read_json, write_json
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
