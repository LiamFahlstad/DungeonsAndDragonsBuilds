"""The battle map in the combat window (Notes/combat-arena-plan.md, step 3):
positions and the map's settings are saved with a fight in progress and come
back when it's continued, players' too, undo puts a token back, and the feet
moved reset as a combatant's turn starts."""

from functools import cache

from Combat.Arena.arena import MOVED_KEY, POSITION_KEY, ArenaSettings
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
    assert POSITION_KEY not in _named(fresh, "Tiger"), "not on the map"
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
