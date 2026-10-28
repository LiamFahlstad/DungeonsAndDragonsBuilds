"""Loading an encounter: each scenario's persistent log (Combat/EncounterLogs.py)
and the combat window's Load Encounter / Continue / Restart flow
(Combat/CombatUIQt/encounters_mixin.py), and how the two logs split the work:
the encounter logs hold every event, the player log (Combat/PlayerLog.py)
only where the party has been, and the party's state is replayed from the
first through the second."""

import json
from functools import cache

import pytest
from PyQt6.QtWidgets import (
    QDialog,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
)

import Combat.PlayerLog as PlayerLog
from Combat.Combatants import Pirate
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.encounters_mixin import CONTINUE, RESTART
from Combat.CombatUIQt.rest import apply_long_rest
from Combat.EncounterLogs import (
    EMPTY_LOG,
    ENDED_KEY,
    UNDONE_SESSIONS_KEY,
    read_log_status,
    restart_log,
    scenario_log_path,
)
from Combat.PlayerLog import scenario_title
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.Scenario import CombatScenario
from Core.Definitions import DamageType
from tests._combat_ui import open_dialog, qapp
from tests._snapshot_helpers import build

PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"
SLASHING = DamageType.SLASHING.value

PIRATES = CombatScenario(name="pirate_ambush", combatants=lambda: [Pirate(), Pirate()])
TIGER = CombatScenario(name="tiger_den", combatants=lambda: [Tiger()])


@cache
def _player():
    return build(PLAYER_BUILD)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


def _in_progress_log(path, hp: int = 3, round_number: int = 4):
    path.parent.mkdir(parents=True, exist_ok=True)
    tiger = {"name": "Tiger", "hp": hp, "max_hp": 30, "ac": 12, "conditions": []}
    path.write_text(
        json.dumps(
            {
                "round_number": round_number,
                "combatants": [tiger, {**tiger, "name": "Tiger 2", "hp": 0}],
                "round_1": ["Tiger took 27 damage"],
            }
        )
    )


def _ui(tmp_path, combatants=(), players=(), scenario_name=None) -> CombatAppQt:
    qapp()
    ui = CombatAppQt(
        list(combatants),
        list(players),
        combat_log_dir=tmp_path,
        scenario_name=scenario_name,
        scenarios=[PIRATES, TIGER],
    )
    ui._build_window()
    return ui


# ---------------------------------------------------------------------------
# EncounterLogs


def test_nothing_to_continue_without_a_fight(tmp_path):
    path = tmp_path / "x.json"
    assert read_log_status(path) is None
    path.write_text(json.dumps(EMPTY_LOG))
    assert read_log_status(path) is None
    # Monsters written but no event logged: the fight never got going.
    path.write_text(json.dumps({"round_number": 1, "combatants": [{"hp": 5}]}))
    assert read_log_status(path) is None


def test_status_of_a_fight_in_progress(tmp_path):
    path = tmp_path / "tiger_den.json"
    _in_progress_log(path)
    status = read_log_status(path)
    assert status is not None
    assert (status.round_number, status.standing, status.total) == (4, 1, 2)
    assert status.describe().startswith("Round 4, 1 of 2 standing, last played ")


def test_status_of_a_finished_fight(tmp_path):
    path = tmp_path / "tiger_den.json"
    _in_progress_log(path, hp=0)
    status = read_log_status(path)
    assert status is not None
    assert status.describe().startswith("Round 4, all 2 down, last played ")


def test_scenario_titles():
    assert scenario_title("wrath_of_durmor") == "Wrath of Durmor"
    assert scenario_title("the_drunk_oxe") == "The Drunk Oxe"


def test_restart_backs_up_a_fight_in_progress(tmp_path):
    path = tmp_path / "tiger_den.json"
    _in_progress_log(path)
    old = json.loads(path.read_text())
    backup = restart_log(path)
    assert backup is not None and backup.parent == tmp_path
    assert backup.name.startswith("tiger_den_restarted_")
    assert json.loads(backup.read_text()) == old
    assert json.loads(path.read_text()) == EMPTY_LOG


def test_restart_takes_the_fight_out_of_the_player_log(tmp_path):
    path = tmp_path / "CombatLogs" / "tiger_den.json"
    player_log_path = tmp_path / "PlayerLogs" / "main_party.json"
    _in_progress_log(path)
    sessions = [
        {"type": "adventure", "log": "../CombatLogs/adventure_1.json"},
        # From when the player log embedded its events.
        {"type": "encounter", "scenario": "tiger_den", "round_1": []},
        {"type": "encounter", "scenario": "pirate_ambush", "round_1": []},
        {
            "type": "encounter",
            "scenario": "tiger_den",
            "log": "../CombatLogs/tiger_den.json",
        },
    ]
    player_log = {"sessions": list(sessions)}
    backup = restart_log(path, player_log, player_log_path)
    assert backup is not None
    assert player_log["sessions"] == [sessions[0], sessions[2]]
    undone = json.loads(backup.read_text())[UNDONE_SESSIONS_KEY]
    assert undone == [sessions[1], sessions[3]]


def test_restart_without_a_fight_keeps_no_backup(tmp_path):
    path = tmp_path / "new" / "tiger_den.json"
    assert restart_log(path) is None
    assert json.loads(path.read_text()) == EMPTY_LOG
    assert list(path.parent.iterdir()) == [path]


# ---------------------------------------------------------------------------
# Continue or restart


def test_no_question_when_there_is_nothing_to_continue(tmp_path):
    ui = _ui(tmp_path)
    path = tmp_path / "tiger_den.json"
    assert ui._ask_continue_or_restart(path, "Tiger Den") == RESTART
    assert ui._ask_continue_or_restart(path, "x", can_restart=False) == CONTINUE


@pytest.mark.parametrize(
    "button, expected",
    [("Continue Encounter", CONTINUE), ("Restart Encounter", RESTART), (None, None)],
)
def test_asks_when_a_fight_is_in_progress(tmp_path, monkeypatch, button, expected):
    ui = _ui(tmp_path)
    path = tmp_path / "tiger_den.json"
    _in_progress_log(path)
    shown = []

    def fake_exec(box):
        shown.append([b.text() for b in box.buttons()])
        clicked = next((b for b in box.buttons() if b.text() == button), None)
        monkeypatch.setattr(box, "clickedButton", lambda: clicked)
        return 0

    monkeypatch.setattr(QMessageBox, "exec", fake_exec)
    assert ui._ask_continue_or_restart(path, "Tiger Den") == expected
    assert "Continue Encounter" in shown[0] and "Restart Encounter" in shown[0]


def test_startup_restart_brings_monsters_back_fresh(tmp_path):
    path = tmp_path / "tiger_den.json"
    _in_progress_log(path)
    ui = _ui(tmp_path, [Tiger()], scenario_name="tiger_den")
    ui._open_encounter_log(path, restart=True)
    assert ui.phase == "INITIATIVE"
    assert [(c["name"], c["hp"]) for c in ui.characters] == [("Tiger", 30)]
    assert ui.log_file == path
    assert [c["hp"] for c in json.loads(path.read_text())["combatants"]] == [30]
    assert ui._window.windowTitle() == "DnD Combat Engine — Tiger Den"


# ---------------------------------------------------------------------------
# Load Encounter


def test_load_encounter_swaps_the_monsters_and_keeps_the_party(tmp_path):
    ui = _ui(tmp_path, [Pirate()], [_player()], scenario_name="pirate_ambush")
    player = ui.characters[0]
    player["hp"] -= 5
    ui._load_encounter(TIGER, restart=True)
    assert ui.characters[0] is player
    assert [c["name"] for c in ui.characters[1:]] == ["Tiger"]
    assert ui.phase == "INITIATIVE"
    assert set(ui._initiative_inputs) == {id(c) for c in ui.characters}
    assert ui.log_file == scenario_log_path(tmp_path, "tiger_den")
    assert ui._scenario_name == "tiger_den"


def test_load_encounter_continues_where_the_log_stopped(tmp_path):
    _in_progress_log(scenario_log_path(tmp_path, "tiger_den"), hp=3, round_number=4)
    ui = _ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    ui._load_encounter(TIGER, restart=False)
    assert ui.phase == "COMBAT"
    assert ui.round_number == 4
    assert [(c["name"], c["hp"]) for c in ui.characters] == [
        ("Tiger", 3),
        ("Tiger 2", 0),
    ]


def test_load_encounter_from_combat_back_to_initiative(tmp_path):
    ui = _ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    ui._initiative_inputs[id(ui.characters[0])].setText("10")
    ui._start_combat()
    ui.round_number = 3
    ui._load_encounter(TIGER, restart=True)
    assert ui.phase == "INITIATIVE"
    assert ui.round_number == 1
    assert ui.history == []
    assert ui._scroll_area.widget() is ui._initiative_widget
    assert ui._next_turn_btn.isHidden()


def test_load_encounter_without_a_player_log_tracks_nothing(tmp_path):
    ui = _ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    ui._load_encounter(TIGER, restart=True)
    assert ui.player_log_data == {"sessions": []}
    assert ui._player_log_session is None


# ---------------------------------------------------------------------------
# The player log and the encounter logs


def _tracked_ui(
    tmp_path, combatants=(), scenario_name="tiger_den", restart=True
) -> CombatAppQt:
    """One run of a window tracking one player, laid out like a campaign
    folder: tmp_path/PlayerLogs/main_party.json and tmp_path/CombatLogs/."""
    qapp()
    ui = CombatAppQt(
        list(combatants),
        [_player()],
        combat_log_dir=tmp_path / "CombatLogs",
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenario_name=scenario_name,
        scenarios=[PIRATES, TIGER],
    )
    ui._build_window()
    path = scenario_log_path(tmp_path / "CombatLogs", scenario_name)
    ui._open_encounter_log(path, restart=restart)
    if ui.phase == "INITIATIVE":
        for i, char in enumerate(ui.characters):
            ui._initiative_inputs[id(char)].setText(str(20 - i))
        ui._start_combat()
    return ui


def _hit(ui, source, target, amount: int):
    ui._select_character(source)
    ui._select_target_character(target)
    ui.damage_type_combo.setCurrentIndex(ui.damage_type_combo.findData(SLASHING))
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def _journal(tmp_path) -> list[dict]:
    path = tmp_path / "PlayerLogs" / "main_party.json"
    return json.loads(path.read_text())["sessions"] if path.exists() else []


def test_the_player_log_says_where_the_party_has_been(tmp_path):
    ui = _tracked_ui(tmp_path, [Tiger(), Pirate()])
    player, tiger, pirate = ui.characters
    _hit(ui, pirate, tiger, 4)
    _hit(ui, tiger, player, 5)
    ui._select_character(player)
    ui._add_action_use("Action")

    (entry,) = _journal(tmp_path)
    assert entry == {
        "type": "encounter",
        "scenario": "tiger_den",
        "log": "../CombatLogs/tiger_den.json",
        "started_at": entry["started_at"],
    }
    # Every event is in the encounter log, players' with what changed.
    events = json.loads(ui.log_file.read_text())["round_1"]
    assert len(events) == 3
    assert events[1]["character"] == player["name"]
    assert events[1]["action"] == "damage"
    assert events[1]["value"]["hp_delta"] == -5


def test_nothing_is_written_for_an_encounter_where_nothing_happened(tmp_path):
    ui = _tracked_ui(tmp_path, [Tiger()])
    ui._load_encounter(PIRATES, restart=True)
    assert _journal(tmp_path) == []


def test_the_party_comes_back_as_they_left(tmp_path):
    ui = _tracked_ui(tmp_path, [Tiger()])
    player, tiger = ui.characters
    full_hp = player["hp"]
    _hit(ui, tiger, player, 5)

    # The next run continues the fight: the party is replayed from its log,
    # and the fight keeps its one entry.
    ui = _tracked_ui(tmp_path, [Tiger()], restart=False)
    player, tiger = ui.characters
    assert player["hp"] == full_hp - 5
    _hit(ui, tiger, player, 2)
    assert len(_journal(tmp_path)) == 1

    # And an adventure after it starts from there too.
    qapp()
    adventure = CombatAppQt(
        [],
        [_player()],
        combat_log_dir=tmp_path / "CombatLogs",
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
    )
    assert adventure.characters[0]["hp"] == full_hp - 7
    assert adventure.log_file.name.startswith("adventure_")


def test_a_long_rest_restores_the_party(tmp_path):
    ui = _tracked_ui(tmp_path, [Tiger()])
    player, tiger = ui.characters
    full_hp = player["hp"]
    _hit(ui, tiger, player, 5)
    apply_long_rest(str(ui.player_log_file))

    ui = _tracked_ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    player, pirate = ui.characters
    assert player["hp"] == full_hp
    _hit(ui, pirate, player, 3)
    assert [s["type"] for s in _journal(tmp_path)] == [
        "encounter",
        "long_rest",
        "encounter",
    ]
    # The statistics still count the fight before the rest.
    stats = ui._compute_player_log_stats()
    assert stats[player["name"]]["damage_taken"] == 8


def test_empty_entries_are_dropped_when_the_player_log_loads(tmp_path):
    log = tmp_path / "PlayerLogs" / "main_party.json"
    log.parent.mkdir(parents=True)
    (tmp_path / "CombatLogs").mkdir()
    (tmp_path / "CombatLogs" / "empty.json").write_text(json.dumps(EMPTY_LOG))
    kept = [
        {"type": "encounter", "round_1": [{"text": "x"}]},
        {"type": "adventure", "combatants": []},  # old snapshot format
        {"type": "encounter", "log": "../CombatLogs/elsewhere.json"},  # not here
        {"type": "long_rest"},
    ]
    dropped = [
        {"type": "encounter"},
        {"type": "encounter", "log": "../CombatLogs/empty.json"},
    ]
    log.write_text(json.dumps({"sessions": kept[:2] + dropped + kept[2:]}))
    ui = _tracked_ui(tmp_path)
    assert ui.player_log_data["sessions"] == kept


def test_restart_puts_the_party_back_as_before_the_fight(tmp_path):
    ui = _tracked_ui(tmp_path, [Tiger()])
    player, tiger = ui.characters
    full_hp = player["hp"]
    _hit(ui, tiger, player, 7)
    assert player["hp"] == full_hp - 7

    ui._load_encounter(TIGER, restart=True)
    assert player is ui.characters[0]
    assert player["hp"] == full_hp
    assert _journal(tmp_path) == []
    (backup,) = (tmp_path / "CombatLogs").glob("tiger_den_restarted_*.json")
    backup_data = json.loads(backup.read_text())
    assert "takes 7" in backup_data["round_1"][0]["text"]
    assert [s["scenario"] for s in backup_data[UNDONE_SESSIONS_KEY]] == ["tiger_den"]


def test_restart_keeps_what_happened_to_the_party_elsewhere(tmp_path):
    ui = _tracked_ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    player, pirate = ui.characters
    full_hp = player["hp"]
    _hit(ui, pirate, player, 4)
    ui._load_encounter(TIGER, restart=True)
    _hit(ui, ui.characters[1], player, 6)
    ui._load_encounter(TIGER, restart=True)
    assert player["hp"] == full_hp - 4
    assert [s["scenario"] for s in _journal(tmp_path)] == ["pirate_ambush"]


# ---------------------------------------------------------------------------
# End Encounter


@pytest.fixture
def say_yes(monkeypatch):
    asked = []

    def question(*args, **kwargs):
        asked.append(args[1:3])
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked


def test_end_encounter_records_it_and_carries_on_in_an_adventure(tmp_path, say_yes):
    ui = _tracked_ui(tmp_path, [Tiger()])
    player, tiger = ui.characters
    full_hp = player["hp"]
    _hit(ui, tiger, player, 5)
    fight_log = ui.log_file

    ui._end_encounter()
    assert say_yes
    # The fight is ended in its encounter log and in the party's journal.
    fight = json.loads(fight_log.read_text())
    assert ENDED_KEY in fight
    assert fight["round_1"][-1]["text"] == "--- Tiger Den ended ---"
    (entry,) = _journal(tmp_path)
    assert entry[ENDED_KEY] == fight[ENDED_KEY]
    status = read_log_status(fight_log)
    assert status is not None and status.ended
    assert status.describe().startswith("Ended in round 1, 1 of 1 standing")

    # The party carries on, as they are, in an adventure.
    assert ui.characters == [player] and player["hp"] == full_hp - 5
    assert ui._scenario_name is None and ui.phase == "INITIATIVE"
    assert ui.log_file.name.startswith("adventure_")
    assert not ui._end_encounter_btn.isEnabled()
    ui._select_character(player)
    ui._add_action_use("Action")
    assert [s["type"] for s in _journal(tmp_path)] == ["encounter", "adventure"]


def test_continuing_an_ended_encounter_reopens_it(tmp_path, say_yes):
    ui = _tracked_ui(tmp_path, [Tiger()])
    player, tiger = ui.characters
    _hit(ui, tiger, player, 5)
    ui._end_encounter()

    ui._load_encounter(TIGER, restart=False)
    assert ui.phase == "COMBAT"
    assert ENDED_KEY not in json.loads(ui.log_file.read_text())
    assert ENDED_KEY not in _journal(tmp_path)[0]
    assert ui._end_encounter_btn.isEnabled()


def test_ending_an_encounter_where_nothing_happened_records_nothing(tmp_path, say_yes):
    ui = _tracked_ui(tmp_path, [Tiger()])
    ui._end_encounter()
    assert _journal(tmp_path) == []
    assert ENDED_KEY not in json.loads(
        scenario_log_path(tmp_path / "CombatLogs", "tiger_den").read_text()
    )


def test_end_encounter_can_be_cancelled(tmp_path, monkeypatch):
    ui = _tracked_ui(tmp_path, [Tiger()])
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No
    )
    ui._end_encounter()
    assert ui._scenario_name == "tiger_den" and len(ui.characters) == 2


# ---------------------------------------------------------------------------
# Rests


def _adventure_ui(tmp_path) -> CombatAppQt:
    """One run of an adventure session (no scenario) for the tracked player."""
    qapp()
    ui = CombatAppQt(
        [],
        [_player()],
        combat_log_dir=tmp_path / "CombatLogs",
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenarios=[PIRATES, TIGER],
    )
    ui._build_window()
    return ui


def _rest_buttons(ui) -> tuple[bool, bool]:
    return ui._short_rest_btn.isEnabled(), ui._long_rest_btn.isEnabled()


def test_rests_only_between_fights(tmp_path):
    assert _rest_buttons(_adventure_ui(tmp_path)) == (True, True)
    assert _rest_buttons(_ui(tmp_path)) == (False, False)  # no tracked party
    ui = _tracked_ui(tmp_path, [Tiger()])
    assert ui.phase == "COMBAT"
    assert _rest_buttons(ui) == (False, False)
    ui._load_encounter(PIRATES, restart=True)  # loaded, not started
    assert _rest_buttons(ui) == (True, True)


def test_an_adventure_session_leaves_no_empty_log(tmp_path):
    _adventure_ui(tmp_path)
    assert not list((tmp_path / "CombatLogs").glob("*.json"))


def test_long_rest_in_an_adventure(tmp_path, say_yes):
    ui = _adventure_ui(tmp_path)
    (player,) = ui.characters
    full_hp = player["hp"]
    _hit(ui, player, player, 5)
    adventure_log = ui.log_file

    ui._long_rest()
    assert player["hp"] == full_hp
    # What happens next goes in a new log, after the rest.
    assert ui.log_file != adventure_log
    _hit(ui, player, player, 2)
    assert [s["type"] for s in _journal(tmp_path)] == [
        "adventure",
        "long_rest",
        "adventure",
    ]
    assert _adventure_ui(tmp_path).characters[0]["hp"] == full_hp - 2


def test_long_rest_before_starting_an_encounter(tmp_path, say_yes):
    ui = _tracked_ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    player, pirate = ui.characters
    full_hp = player["hp"]
    _hit(ui, pirate, player, 6)

    ui._load_encounter(TIGER, restart=True)
    ui._long_rest()
    assert player["hp"] == full_hp
    _hit(ui, ui.characters[1], player, 3)
    assert [s.get("scenario") or s["type"] for s in _journal(tmp_path)] == [
        "pirate_ambush",
        "long_rest",
        "tiger_den",
    ]
    ui = _tracked_ui(tmp_path, [Tiger()], restart=False)
    assert ui.characters[0]["hp"] == full_hp - 3


def _heal_in_short_rest(monkeypatch, amount: int):
    """Make the short-rest window heal every player `amount` and close."""

    def exec_(dlg):
        for field in dlg.findChildren(QLineEdit):
            field.setText(str(amount))
        next(b for b in dlg.findChildren(QPushButton) if "Apply" in b.text()).click()
        return 0

    monkeypatch.setattr(QDialog, "exec", exec_)


def test_short_rest_in_an_adventure(tmp_path, monkeypatch):
    ui = _adventure_ui(tmp_path)
    (player,) = ui.characters
    full_hp = player["hp"]
    _hit(ui, player, player, 8)
    _heal_in_short_rest(monkeypatch, 3)

    ui._short_rest()
    assert player["hp"] == full_hp - 5
    journal = _journal(tmp_path)
    assert [s["type"] for s in journal] == ["adventure", "short_rest"]
    assert journal[1]["log"].startswith("../CombatLogs/short_rest_")
    assert ui.log_file.name.startswith("adventure_")
    assert _adventure_ui(tmp_path).characters[0]["hp"] == full_hp - 5


def test_short_rest_before_starting_an_encounter(tmp_path, monkeypatch):
    ui = _tracked_ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    player, pirate = ui.characters
    full_hp = player["hp"]
    _hit(ui, pirate, player, 8)
    ui._load_encounter(TIGER, restart=True)
    tiger_log = ui.log_file
    _heal_in_short_rest(monkeypatch, 4)

    ui._short_rest()
    assert player["hp"] == full_hp - 4
    assert ui.log_file == tiger_log and ui._scenario_name == "tiger_den"
    assert [s["type"] for s in _journal(tmp_path)] == ["encounter", "short_rest"]


def test_journal_helpers():
    sessions = [{"type": "encounter"}, {"type": "long_rest"}, {"type": "adventure"}]
    assert PlayerLog.since_long_rest(sessions) == [{"type": "adventure"}]
    assert PlayerLog.since_long_rest(sessions[:1]) == sessions[:1]
    assert (
        PlayerLog.session_label({"type": "encounter", "scenario": "wrath_of_durmor"})
        == "Encounter: Wrath of Durmor"
    )
    assert PlayerLog.session_label({"type": "short_rest"}) == "Short rest"


def test_load_encounter_dialog_shows_each_scenarios_progress(tmp_path, monkeypatch):
    _in_progress_log(scenario_log_path(tmp_path, "tiger_den"))
    ui = _ui(tmp_path, [Pirate()], scenario_name="pirate_ambush")
    dlg = open_dialog(monkeypatch, ui._show_load_encounter_dialog)
    (scenario_list,) = dlg.findChildren(QListWidget)
    items = [scenario_list.item(i).text() for i in range(scenario_list.count())]  # type: ignore[union-attr]
    assert items[0] == "Pirate Ambush  (current)\n    Not started"
    assert items[1].startswith("Tiger Den\n    Round 4, 1 of 2 standing")

    buttons = {b.text(): b for b in dlg.findChildren(QPushButton)}
    assert "Start Encounter" in buttons
    assert not buttons["Continue Encounter"].isEnabled()
    scenario_list.setCurrentRow(1)
    assert buttons["Continue Encounter"].isEnabled()
    assert buttons["Start Encounter"].text() == "Restart Encounter"
