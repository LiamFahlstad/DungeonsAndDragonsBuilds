"""The player link (Combat/CombatUIQt/player_server.py): a real server on
127.0.0.1, driven through the real window, polled the way the page polls it.
What's expected of /state comes from the rules for what players may see, in
tests/test_combat_ui_fast_play.py's words, not from the server's output."""

import ast
import http.client
import json
import os
import re
import socket
import threading
from dataclasses import asdict
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlsplit

import pytest
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
)

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt import (
    CombatAppQt,
    dialogs_mixin,
    player_server,
    turn_panel_mixin,
)
from Combat.CombatUIQt.player_server import (
    PLAYER_PORT,
    PlayerFeed,
    PlayerServer,
    PlayerServerError,
    lan_addresses,
    rank_addresses,
)
from Combat.CombatUIQt.player_view import player_view_rows
from Combat.CombatUIQt.saves import CustomEffect
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.PlayerLog import is_round_key
from Combat.Scenario import CombatScenario
from Core.Definitions import DamageType
from tests._combat_ui import make_ui, open_dialog, qapp

PAGE = Path(player_server.__file__).with_name("player_page.html")
WAITING = {"title": "Waiting for the fight to start", "rows": [], "log": []}

TIGER = CombatScenario(
    name="tiger_den",
    title="Tiger Den",
    combatants=lambda: [Tiger()],
    monster_summary=["Tiger"],
)
PIRATE = CombatScenario(
    name="pirate_ambush",
    title="Pirate Ambush",
    combatants=lambda: [Pirate()],
    monster_summary=["Pirate"],
)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@pytest.fixture(autouse=True)
def only_this_pc(monkeypatch):
    """Every server here stays on 127.0.0.1, on a free port (a copy of the app
    may hold the real one), and is stopped after its test."""
    started: list[PlayerServer] = []
    real_start = PlayerServer.start

    def start(self, host, port=0):
        assert host in ("127.0.0.1", "localhost")
        started.append(self)
        real_start(self, host, port)

    monkeypatch.setattr(PlayerServer, "start", start)
    monkeypatch.setattr(turn_panel_mixin, "PLAYER_PORT", 0)
    monkeypatch.setattr(
        dialogs_mixin, "lan_addresses", lambda: ["127.0.0.1", "localhost"]
    )
    yield
    for server in started:
        server.stop()


@pytest.fixture
def say_yes(monkeypatch):
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )


class Reply(NamedTuple):
    status: int
    headers: http.client.HTTPMessage
    body: bytes


def _port(server: PlayerServer) -> int:
    assert server.url is not None
    port = urlsplit(server.url).port
    assert port is not None
    return port


def _ask(port: int, path="/state", method="GET", headers=None) -> Reply:
    """One request, sent as written: nothing tidies up the path."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request(method, path, headers=headers or {})
        response = connection.getresponse()
        return Reply(response.status, response.headers, response.read())
    finally:
        connection.close()


def _poll(ui: CombatAppQt, etag: str | None = None) -> Reply:
    headers = {"If-None-Match": etag} if etag else None
    return _ask(_port(ui._player_server), headers=headers)


def _state(ui: CombatAppQt) -> dict:
    reply = _poll(ui)
    assert reply.status == 200
    return json.loads(reply.body)


def _names(state: dict) -> list[str]:
    return [row["name"] for row in state["rows"]]


def _start(ui, *initiatives: int):
    for char, value in zip(ui.characters, initiatives):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()


def _bandit():
    bandit = Pirate()
    bandit.set_name("Bandit")
    return bandit


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15), a 30 HP Tiger (10) and a Bandit (5), on the Pirate's
    turn, with the link running."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _bandit()])
    _start(ui, 15, 10, 5)
    ui._start_player_server("127.0.0.1")
    return ui, *ui.characters


def _campaign_ui(tmp_path) -> CombatAppQt:
    """The window for a campaign in tmp_path, with both encounters prepared,
    on the party between encounters."""
    qapp()
    logs = tmp_path / "CombatLogs"
    for scenario in (TIGER, PIRATE):
        prepare_log(scenario_log_path(logs, scenario.name), scenario, [])
    ui = CombatAppQt([], [], combat_log_dir=logs, scenarios=[TIGER, PIRATE])
    ui._build_window()
    return ui


# ---------------------------------------------------------------------------
# What /state shows


def _row(
    name: str, details: str, text: str, percent: int, color: str, turn: str
) -> dict:
    return {
        "name": name,
        "details": details,
        "health": [{"name": name, "text": text, "percent": percent, "color": color}],
        "conditions": [],
        "turn": turn,
    }


def _hp(row: dict) -> list[str]:
    return [health["text"] for health in row["health"]]


def test_state_is_the_player_screens_rows(fight):
    ui, _, tiger, _ = fight
    tiger["hp"] = 15
    ui._refresh_views()
    state = _state(ui)
    assert state == {
        "title": "Round 1",
        "rows": [
            _row("Pirate", "AC 14", "33 / 33", 100, "#2ecc71", "now"),
            _row("Tiger", "AC 13", "15 / 30", 50, "#e67e22", "next"),
            _row("Bandit (Pirate)", "AC 14", "33 / 33", 100, "#2ecc71", ""),
        ],
        "log": [],
    }
    filtered = player_view_rows(
        ui.initiative_order,
        ui._current_turn_group(),
        ui._upcoming_turns(),
        ui._char_death_state,
    )
    assert state["rows"] == json.loads(json.dumps([asdict(r) for r in filtered]))


def test_a_players_numbers_size_and_speed_are_on_the_page(fight):
    ui, _, tiger, _ = fight
    tiger.update(_is_player=True, hp=12, temp_hp=4, size="Small", speed=25)
    ui._refresh_views()
    (row,) = [r for r in _state(ui)["rows"] if r["name"] == "Tiger"]
    assert _hp(row) == ["12 / 30 (+4 temp)"]
    assert row["details"] == "Small · AC 13 · Speed 25 ft."


def test_a_monsters_hp_ac_and_speed_are_on_the_page_but_nothing_else(fight):
    ui, _, tiger, _ = fight
    tiger.update(hp=137, max_hp=293, temp_hp=59, ac=471, speed_ground_ft=613)
    tiger["Ability Scores"] = {"STR": 83}
    tiger["Saving Throws"] = {"DEX": 97}
    tiger["actions"] = [{"name": "Secret Bite", "description": "A nasty surprise"}]
    ui._refresh_views()
    body = _poll(ui).body.decode()
    for private in ("83", "97", "Secret Bite", "A nasty surprise"):
        assert private not in body
    state = json.loads(body)
    assert set(state) == {"title", "rows", "log"}
    assert all(
        set(r) == {"name", "details", "health", "conditions", "turn"}
        for r in state["rows"]
    )
    (row,) = [r for r in state["rows"] if r["name"] == "Tiger"]
    assert _hp(row) == ["137 / 293 (+59 temp)"]
    assert row["details"] == "AC 471 · Speed 613 ft."


def test_a_monsters_private_conditions_stay_off_the_page(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"] = ["Prone", "Concentrating", "Bloodied", "Plotting betrayal"]
    ui._refresh_views()
    (row,) = [r for r in _state(ui)["rows"] if r["name"] == "Tiger"]
    assert row["conditions"] == ["Prone"]


def test_a_hidden_monster_isnt_listed_and_its_changes_change_nothing(fight):
    ui, _, tiger, bandit = fight
    tiger["conditions"] = ["Invisible"]
    ui._refresh_views()
    before = _poll(ui)
    assert "Tiger" not in before.body.decode()

    tiger["hp"] = 1
    ui._refresh_views()
    after = _poll(ui)
    assert after.headers["ETag"] == before.headers["ETag"]
    assert after.body == before.body

    bandit["hp"] = 1  # one they can see does
    ui._refresh_views()
    assert _poll(ui).headers["ETag"] != before.headers["ETag"]


def test_text_typed_by_hand_arrives_as_text(fight):
    ui, pirate, *_ = fight
    pirate.update(_is_player=True, conditions=["<img src=x> & Jätte"])
    ui._refresh_views()
    (row,) = [r for r in _state(ui)["rows"] if r["name"] == "Pirate"]
    assert row["conditions"] == ["<img src=x> & Jätte"]


# ---------------------------------------------------------------------------
# The Limited view


@pytest.fixture
def limited(fight):
    """The fight, with the Limited view on. These stat blocks have no speed of
    their own, so they're given one."""
    ui, *_ = fight
    for char in ui.characters:
        char["speed_ground_ft"] = 40
    ui.settings.limited_player_view = True
    ui._refresh_views()
    return fight


def _row_of(ui, name: str) -> dict:
    (row,) = [r for r in _state(ui)["rows"] if r["name"] == name]
    return row


@pytest.mark.parametrize(
    "hp, word",
    [
        (100, "Healthy"),
        (76, "Healthy"),
        (75, "Injured"),
        (51, "Injured"),
        (50, "Bloodied"),
        (26, "Bloodied"),
        (25, "Dying"),
        (1, "Dying"),
        (0, "Defeated"),
    ],
)
def test_limited_says_a_monsters_hp_as_a_word(limited, hp, word):
    ui, _, tiger, _ = limited
    tiger.update(hp=hp, max_hp=100)
    ui._refresh_views()
    assert _hp(_row_of(ui, "Tiger")) == [word]


@pytest.mark.parametrize("hp, word", [(16, "Bloodied"), (17, "Injured")])
def test_limited_bloodied_is_half_or_fewer_of_an_odd_maximum(limited, hp, word):
    ui, _, tiger, _ = limited
    tiger.update(hp=hp, max_hp=33)
    ui._refresh_views()
    assert _hp(_row_of(ui, "Tiger")) == [word]


def test_limited_says_bloodied_when_the_condition_arrives(limited):
    ui, pirate, tiger, _ = limited
    _hit(ui, pirate, tiger, 14)  # 16 of 30 left
    assert "Bloodied" not in tiger["conditions"]
    assert _hp(_row_of(ui, "Tiger")) == ["Injured"]
    _hit(ui, pirate, tiger, 1)  # 15 of 30 left
    assert "Bloodied" in tiger["conditions"]
    assert _hp(_row_of(ui, "Tiger")) == ["Bloodied"]


def test_a_players_numbers_stay_on_limited(limited):
    """They can tell each other all of it anyway."""
    ui, pirate, *_ = limited
    pirate.update(
        _is_player=True,
        hp=5,
        max_hp=40,
        temp_hp=4,
        size="Small",
        ac="18 (with Shield) and 16 (without Shield)",
        speed=25,
        speed_ground_ft=None,
        conditions=["Bloodied", "Blessed"],
    )
    ui._refresh_views()
    assert _row_of(ui, "Pirate") == {
        "name": "Pirate",
        "details": "Small · AC 18 · Speed 25 ft.",
        "health": [
            {
                "name": "Pirate",
                "text": "5 / 40 (+4 temp)",
                "percent": 13,
                "color": "#e74c3c",
            }
        ],
        "conditions": ["Bloodied", "Blessed"],
        "turn": "now",
    }


@pytest.mark.parametrize(
    "state",
    [
        {"hp": 33},
        {"hp": 5},
        {"hp": 0, "death_saves_fail": 1, "death_saves_success": 2},
        {"hp": 0, "death_saves_success": 3},
        {"hp": 0, "death_saves_fail": 3},
    ],
)
def test_a_players_row_is_the_same_in_both_views(fight, state):
    ui, pirate, *_ = fight
    pirate.update(_is_player=True, **state)
    ui._refresh_views()
    informative = _row_of(ui, "Pirate")
    ui.settings.limited_player_view = True
    ui._refresh_views()
    assert _row_of(ui, "Pirate") == informative


@pytest.mark.parametrize(
    "fails, saves, word", [(1, 2, "Dying"), (0, 3, "Stable"), (3, 0, "Defeated")]
)
def test_limited_for_a_monster_that_makes_death_saves(limited, fails, saves, word):
    ui, _, tiger, _ = limited
    tiger.update(
        death_saves=True, hp=0, death_saves_fail=fails, death_saves_success=saves
    )
    ui._refresh_views()
    assert _hp(_row_of(ui, "Tiger")) == [word]
    assert _row_of(ui, "Tiger")["health"][0]["percent"] == 0


def test_limited_doesnt_call_a_summon_with_no_hp_yet_dying(limited):
    ui, _, tiger, _ = limited
    tiger.update(hp=0, max_hp=0)
    ui._refresh_views()
    assert _hp(_row_of(ui, "Tiger")) == ["Healthy"]


def test_limited_gives_each_member_of_a_group_its_own_word(tmp_path):
    def tiger(name):
        combatant = Tiger()
        combatant.set_name(name)
        combatant.initiative_group = "Tigers"
        return combatant

    ui = make_ui(tmp_path, [tiger("One"), tiger("Two")])
    _start(ui, 9)
    ui.settings.limited_player_view = True
    ui._start_player_server("127.0.0.1")
    ui.characters[0]["speed_ground_ft"] = 40
    ui.characters[1].update(speed_ground_ft=40, hp=1)
    ui._refresh_views()
    (row,) = _state(ui)["rows"]
    assert [(h["name"], h["text"]) for h in row["health"]] == [
        ("One (Tiger) · 0 damage taken", "Healthy"),
        ("Two (Tiger) · 0 damage taken", "Dying"),
    ]
    assert row["details"] == "Speed 40 ft."

    _hit(ui, ui.characters[0], ui.characters[1], 2)
    (row,) = _state(ui)["rows"]
    assert [h["name"] for h in row["health"]] == [
        "One (Tiger) · 0 damage taken",
        "Two (Tiger) · 2 damage taken",
    ]


def test_limited_says_the_damage_each_one_has_taken(limited):
    ui, pirate, tiger, bandit = limited
    assert _row_of(ui, "Tiger")["details"] == "0 damage taken · Speed 40 ft."
    _hit(ui, pirate, tiger, 3)
    _hit(ui, bandit, tiger, 4)
    _hit(ui, tiger, pirate, 5)
    assert _row_of(ui, "Tiger")["details"] == "7 damage taken · Speed 40 ft."
    assert _row_of(ui, "Pirate")["details"].startswith("5 damage taken")
    assert _row_of(ui, "Bandit (Pirate)")["details"].startswith("0 damage taken")


def test_damage_taken_counts_a_hit_of_several_types_in_full(limited):
    ui, pirate, tiger, _ = limited
    ui._select_character(pirate)
    ui._set_targets([tiger])
    ui.damage_input.setText("7 sl + 3 fi")
    ui._apply_damage()
    QApplication.processEvents()
    assert _row_of(ui, "Tiger")["details"].startswith("10 damage taken")


def test_healing_doesnt_take_damage_taken_back(limited):
    ui, pirate, tiger, _ = limited
    _hit(ui, pirate, tiger, 10)
    ui._select_character(pirate)
    ui._set_targets([tiger])
    ui.heal_input.setText("10")
    ui._apply_heal()
    QApplication.processEvents()
    assert tiger["hp"] == 30
    assert _row_of(ui, "Tiger")["details"].startswith("10 damage taken")


def test_damage_taken_counts_what_temp_hp_soaked(limited):
    """Or the total would come up short by the temp HP the view hides."""
    ui, pirate, tiger, _ = limited
    tiger["temp_hp"] = 5
    _hit(ui, pirate, tiger, 3)
    assert tiger["hp"] == 30
    assert _row_of(ui, "Tiger")["details"].startswith("3 damage taken")


def test_undo_takes_damage_taken_back(limited):
    ui, pirate, tiger, _ = limited
    _hit(ui, pirate, tiger, 3)
    ui._undo_last()
    QApplication.processEvents()
    assert _row_of(ui, "Tiger")["details"].startswith("0 damage taken")


def test_two_monsters_of_one_name_keep_their_own_damage_taken(tmp_path):
    ui = make_ui(tmp_path, [Tiger(), Tiger()])
    _start(ui, 15, 10)
    ui.settings.limited_player_view = True
    ui._start_player_server("127.0.0.1")
    first, second = ui.characters
    _hit(ui, second, first, 3)
    assert [r["details"] for r in _state(ui)["rows"]] == [
        "3 damage taken",
        "0 damage taken",
    ]


def test_restarting_a_fight_starts_damage_taken_again(tmp_path):
    ui = _in_tiger_fight(tmp_path)
    ui.settings.limited_player_view = True
    ui._start_player_server("127.0.0.1")
    tiger = ui.characters[0]
    _hit(ui, tiger, tiger, 3)
    ui._load_encounter(TIGER, restart=True)
    _start(ui, 12)
    QApplication.processEvents()
    assert _row_of(ui, "Tiger")["details"] == "0 damage taken"


def test_damage_taken_survives_leaving_a_fight_and_stays_in_it(tmp_path):
    ui = _in_tiger_fight(tmp_path)
    ui.settings.limited_player_view = True
    ui._start_player_server("127.0.0.1")
    tiger = ui.characters[0]
    _hit(ui, tiger, tiger, 3)

    ui._load_encounter(PIRATE, restart=False)
    _start(ui, 9)
    QApplication.processEvents()
    assert _row_of(ui, "Pirate")["details"] == "0 damage taken"

    ui._load_encounter(TIGER, restart=False)
    QApplication.processEvents()
    assert _row_of(ui, "Tiger")["details"] == "3 damage taken"


def test_limited_sends_none_of_a_monsters_hidden_numbers(limited):
    ui, _, tiger, _ = limited
    tiger.update(
        hp=137,
        max_hp=293,
        temp_hp=59,
        ac=471,
        size="Gargantuan",
        speed=613,
        speed_ground_ft=613,
    )
    ui._refresh_views()
    body = _poll(ui).body.decode()
    for secret in ("137", "293", "59", "471", "Gargantuan", "AC"):
        assert secret not in body
    assert _row_of(ui, "Tiger") == {
        "name": "Tiger",
        "details": "0 damage taken · Speed 613 ft.",
        "health": [
            {"name": "Tiger", "text": "Bloodied", "percent": 50, "color": "#e67e22"}
        ],
        "conditions": [],
        "turn": "next",
    }


def test_limited_shows_the_turn_order_and_visible_conditions_still(limited):
    ui, pirate, tiger, bandit = limited
    tiger["conditions"] = ["Prone", "Concentrating", "Bloodied", "Plotting betrayal"]
    ui._refresh_views()
    state = _state(ui)
    assert state["title"] == "Round 1"
    assert _names(state) == ["Pirate", "Tiger", "Bandit (Pirate)"]
    assert [r["turn"] for r in state["rows"]] == ["now", "next", ""]
    assert _row_of(ui, "Tiger")["conditions"] == ["Prone"]


def test_limited_still_hides_a_hidden_monster(limited):
    ui, pirate, tiger, _ = limited
    tiger["conditions"] = ["Invisible"]
    ui._refresh_views()
    before = _poll(ui)
    assert "Tiger" not in before.body.decode()

    _hit(ui, pirate, tiger, 3)
    assert _poll(ui).body == before.body, "Nor does what it takes show"


def test_a_hit_that_doesnt_change_the_word_leaves_the_bar_alone(limited):
    ui, pirate, tiger, _ = limited
    before = _row_of(ui, "Tiger")["health"]
    _hit(ui, pirate, tiger, 3)  # 27 of 30: still Healthy
    assert tiger["hp"] == 27
    assert _row_of(ui, "Tiger")["health"] == before

    _hit(ui, pirate, tiger, 10)  # 17 of 30: Injured
    assert _row_of(ui, "Tiger")["health"] != before


def test_the_log_is_the_same_on_limited(limited):
    ui, pirate, tiger, _ = limited
    _hit(ui, pirate, tiger)
    assert _lines(ui) == ["[Pirate's turn] Tiger takes 3 Slashing damage from Pirate"]

    ui.settings.limited_player_view = False
    ui._refresh_views()
    assert _lines(ui) == ["[Pirate's turn] Tiger takes 3 Slashing damage from Pirate"]


def test_a_hidden_monsters_lines_stay_out_of_the_log_on_limited(limited):
    ui, pirate, tiger, bandit = limited
    tiger["conditions"] = ["Invisible"]
    _hit(ui, tiger, bandit)
    assert "from Tiger" in _gm_log(ui), "The GM's log keeps it"
    assert "Tiger" not in str(_lines(ui))


def test_the_player_screen_shows_the_limited_view_too(limited):
    ui, _, tiger, _ = limited
    tiger["hp"] = 15
    ui._toggle_player_view()
    text = _screen_text(ui)
    assert "Bloodied" in text and "0 damage taken · Speed 40 ft." in text
    assert "15 / 30" not in text and "AC 13" not in text
    ui._toggle_player_view()


def test_the_link_dialog_picks_the_view_and_saves_it(fight, monkeypatch, tmp_path):
    ui, _, tiger, _ = fight
    store = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    ui._settings_store = store
    tiger["hp"] = 15
    ui._refresh_views()
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    combo = dlg.findChild(QComboBox, "playerViewCombo")
    assert combo.currentText() == "Informative"
    assert _hp(_row_of(ui, "Tiger")) == ["15 / 30"]

    combo.setCurrentText("Limited")
    assert ui.settings.limited_player_view is True
    assert store.value("limited_player_view", type=bool) is True
    assert _hp(_row_of(ui, "Tiger")) == ["Bloodied"], "On the phones straight away"

    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    combo = dlg.findChild(QComboBox, "playerViewCombo")
    assert combo.currentText() == "Limited"
    combo.setCurrentText("Informative")
    assert ui.settings.limited_player_view is False
    assert _hp(_row_of(ui, "Tiger")) == ["15 / 30"]


def test_the_settings_checkbox_changes_the_view_too(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["hp"] = 15
    dlg = open_dialog(monkeypatch, ui._show_settings_dialog)
    dlg.findChild(QCheckBox, "limited_player_view").setChecked(True)
    assert _hp(_row_of(ui, "Tiger")) == ["Bloodied"]

    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert dlg.findChild(QComboBox, "playerViewCombo").currentText() == "Limited"


def test_picking_the_view_works_with_the_link_stopped(fight, monkeypatch):
    ui, _, tiger, _ = fight
    ui._player_server.stop()
    tiger["hp"] = 15
    ui._toggle_player_view()
    ui._set_setting("limited_player_view", True)
    assert "Bloodied" in _screen_text(ui)
    ui._toggle_player_view()


# ---------------------------------------------------------------------------
# The encounter log


def _hit(ui, source: dict, target: dict, amount: int = 3):
    ui._select_character(source)
    ui._set_targets([target])
    ui.damage_type_combo.setCurrentIndex(
        ui.damage_type_combo.findData(DamageType.SLASHING.value)
    )
    ui.damage_input.setText(str(amount))
    ui._apply_damage()
    QApplication.processEvents()


def _gm_log(ui) -> str:
    log = ui._read_log()
    events = [event for key in filter(is_round_key, log) for event in log[key]]
    return " ".join(event["text"] for event in events)


def _lines(ui) -> list[str]:
    return [line for round_ in _state(ui)["log"] for line in round_["lines"]]


def test_the_log_says_what_happened(fight):
    ui, pirate, tiger, _ = fight
    _hit(ui, pirate, tiger)
    assert _lines(ui) == ["[Pirate's turn] Tiger takes 3 Slashing damage from Pirate"]


def test_a_line_reaches_the_link_without_a_card_changing(fight):
    ui, *_ = fight
    ui._log_event("Pirate ponders", character="Pirate")
    QApplication.processEvents()
    assert _lines(ui) == ["[Pirate's turn] Pirate ponders"]


def test_undo_takes_a_line_back_off_the_link(fight):
    ui, pirate, tiger, _ = fight
    _hit(ui, pirate, tiger)
    ui._undo_last()
    QApplication.processEvents()
    assert _lines(ui) == []


def test_the_rounds_stay_in_order_past_nine(fight):
    ui, *_ = fight
    data = ui._read_log()
    data["round_2"] = [{"text": "Second", "public": True}]
    data["round_10"] = [{"text": "Tenth", "public": True}]
    ui._write_log(data)
    ui._refresh_views()
    assert _state(ui)["log"] == [
        {"round": 2, "lines": ["Second"]},
        {"round": 10, "lines": ["Tenth"]},
    ]


def test_each_round_is_a_heading_over_its_own_lines(fight):
    ui, pirate, tiger, _ = fight
    _hit(ui, pirate, tiger)
    for _ in range(3):
        ui._advance_turn()  # into round 2, which logs its "--- Round 2 ---"
    _hit(ui, pirate, tiger)
    assert _state(ui)["log"] == [
        {
            "round": 1,
            "lines": ["[Pirate's turn] Tiger takes 3 Slashing damage from Pirate"],
        },
        {
            "round": 2,
            "lines": ["[Pirate's turn] Tiger takes 3 Slashing damage from Pirate"],
        },
    ]


def test_a_round_nothing_public_happened_in_isnt_listed(fight):
    ui, *_ = fight
    for _ in range(3):
        ui._advance_turn()
    QApplication.processEvents()
    assert _state(ui)["log"] == []


def test_a_line_not_marked_public_stays_private(fight):
    """A fight logged before the link could show it, and plain text from an
    older log still: nobody decided these, so nobody reads them."""
    ui, *_ = fight
    data = ui._read_log()
    data["round_1"] = ["Plain old line", {"text": "Old event", "character": "Tiger"}]
    ui._write_log(data)
    ui._refresh_views()
    assert _lines(ui) == []


def test_a_hidden_monster_stays_out_of_lines_about_others(fight):
    ui, pirate, tiger, bandit = fight
    tiger["conditions"] = ["Invisible"]
    _hit(ui, tiger, bandit)
    assert "from Tiger" in _gm_log(ui), "The GM's log keeps it"
    assert "Tiger" not in str(_lines(ui))


def test_a_hidden_monsters_turn_stays_out_of_the_prefix(fight):
    ui, pirate, tiger, _ = fight
    tiger["visibility_states"] = ["Hidden"]
    ui._advance_turn()
    ui._log_event("Pirate uses Reaction", character=pirate["name"])
    QApplication.processEvents()
    assert "Reaction" in _gm_log(ui)
    assert not [line for line in _lines(ui) if "Reaction" in line]


def test_a_hidden_groups_turn_stays_out_of_the_prefix(tmp_path):
    def tiger(name):
        combatant = Tiger()
        combatant.set_name(name)
        combatant.initiative_group = "Tigers"
        return combatant

    ui = make_ui(tmp_path, [tiger("One"), tiger("Two")])
    _start(ui, 9)
    one, two = ui.characters
    ui._start_player_server("127.0.0.1")
    one["conditions"] = ["Invisible"]
    two["conditions"] = ["Invisible"]
    ui._log_event("Something stirs")
    QApplication.processEvents()
    assert _lines(ui) == []

    two["conditions"] = []  # one they can see is enough
    ui._log_event("A tiger growls")
    QApplication.processEvents()
    assert _lines(ui) == ["[Tigers's turn] A tiger growls"]


def test_going_hidden_isnt_announced(fight):
    ui, _, tiger, _ = fight
    ui._select_character(tiger)
    ui.visibility_combo.setCurrentText("Invisible")
    ui._add_visibility()
    QApplication.processEvents()
    assert "gains Invisible" in _gm_log(ui)
    assert _lines(ui) == []


@pytest.mark.parametrize("state", ["Invisible", "Half Cover", "Lightly Obscured"])
def test_a_monsters_visibility_stays_out_of_the_log(fight, state):
    """The page doesn't show it, and losing Invisible says how it was hidden."""
    ui, _, tiger, _ = fight
    ui._select_character(tiger)
    ui.visibility_combo.setCurrentText(state)
    ui._add_visibility()
    ui._remove_visibility()
    QApplication.processEvents()
    assert f"loses {state}" in _gm_log(ui)
    assert _lines(ui) == []


def test_a_players_visibility_is_in_the_log(fight):
    ui, pirate, *_ = fight
    pirate["_is_player"] = True
    ui._select_character(pirate)
    ui.visibility_combo.setCurrentText("Invisible")
    ui._add_visibility()
    QApplication.processEvents()
    assert _lines(ui) == ["[Pirate's turn] Pirate gains Invisible"]


def test_a_newcomer_isnt_announced_before_it_can_be_hidden(fight):
    ui, *_ = fight
    ui._add_ad_hoc_combatant("Assassin in the rafters")
    QApplication.processEvents()
    assert "Assassin" in _gm_log(ui)
    assert _lines(ui) == []


def test_nothing_from_before_the_fight_reaches_the_link(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    ui._start_player_server("127.0.0.1")
    ui._add_ad_hoc_combatant("Assassin in the rafters")
    ui._log_event("Something before the fight")
    QApplication.processEvents()
    assert "Something before" in _gm_log(ui)
    assert _state(ui) == WAITING

    _start(ui, 15, 10)
    QApplication.processEvents()
    assert _lines(ui) == []


def test_the_fights_title_stays_off_the_link(tmp_path, say_yes):
    ui = _in_tiger_fight(tmp_path)
    ui._start_player_server("127.0.0.1")
    tiger = ui.characters[0]
    _hit(ui, tiger, tiger)
    ui._end_encounter()
    ui._load_encounter(TIGER, restart=False)
    QApplication.processEvents()
    assert "ended" in _gm_log(ui)
    assert len(_lines(ui)) == 1 and "ended" not in _lines(ui)[0]


def test_a_line_about_a_hidden_monster_is_private_even_if_it_doesnt_name_it(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"] = ["Invisible"]
    ui._log_event("Something unseen", note_turn=False, character=tiger["name"])
    QApplication.processEvents()
    assert _lines(ui) == []


def test_two_monsters_of_one_name_keep_their_private_conditions(tmp_path):
    ui = make_ui(tmp_path, [Tiger(), Tiger()])
    _start(ui, 15, 10)
    ui._start_player_server("127.0.0.1")
    ui.characters[1]["conditions"] = ["Plotting betrayal"]
    ui._log_event(
        "Tiger's Plotting betrayal expires", note_turn=False, character="Tiger"
    )
    QApplication.processEvents()
    assert _lines(ui) == []


def _effect(name: str) -> dict:
    return {"name": name, "concentration": True, "applied": [], "time_left": 6}


def _next_round(ui, tiger, entry):
    for _ in range(3):
        ui._advance_turn()


@pytest.mark.parametrize(
    "end",
    [
        lambda ui, tiger, entry: ui._remove_active_spell(tiger, entry),
        lambda ui, tiger, entry: ui._end_concentration_spells(tiger),
        lambda ui, tiger, entry: ui._start_concentration(tiger, "Secret pact"),
        _next_round,
    ],
    ids=["dismissed", "concentration lost", "new concentration", "ran out"],
)
def test_a_monsters_effect_ending_stays_out_of_the_log(fight, end):
    """By then the condition's gone, or was never on it: only the call says what
    the line is about."""
    ui, _, tiger, _ = fight
    entry = _effect("Plotting betrayal")
    tiger["active_spells"] = [entry]
    end(ui, tiger, entry)
    QApplication.processEvents()
    assert "Plotting betrayal" in _gm_log(ui)
    assert "Plotting betrayal" not in str(_lines(ui))
    assert "Secret pact" not in str(_lines(ui))


def test_an_effect_ending_on_another_monster_stays_out_of_the_log(fight):
    ui, _, tiger, bandit = fight
    tiger["active_spells"] = [
        {
            "name": "Whispered order",
            "ends_with_conditions": True,
            "applied": [{"target": bandit["name"], "condition": "Whispered order"}],
        }
    ]
    bandit["conditions"] = ["Whispered order"]
    ui._remove_condition_from(bandit, "Whispered order")
    QApplication.processEvents()
    assert "Tiger's Whispered order ends" in _gm_log(ui)
    assert _lines(ui) == []


def test_a_players_effect_ending_is_in_the_log(fight):
    ui, pirate, *_ = fight
    pirate["_is_player"] = True
    entry = _effect("Bless")
    pirate["active_spells"] = [entry]
    ui._remove_active_spell(pirate, entry)
    QApplication.processEvents()
    assert _lines(ui) == ["[Pirate's turn] Pirate's Bless ends early"]


@pytest.mark.parametrize("kept", [True, False])
def test_a_monsters_concentration_stays_out_of_the_log(fight, kept):
    ui, _, tiger, _ = fight
    tiger["conditions"] = ["Concentrating"]
    ui._settle_concentration(tiger, 10, kept, 15)
    QApplication.processEvents()
    assert "concentration (DC 10, rolled 15)" in _gm_log(ui)
    assert _lines(ui) == []


def test_a_players_concentration_is_in_the_log(fight):
    ui, pirate, *_ = fight
    pirate["_is_player"] = True
    pirate["conditions"] = ["Concentrating"]
    ui._settle_concentration(pirate, 10, True, 15)
    QApplication.processEvents()
    assert _lines(ui) == [
        "[Pirate's turn] Pirate keeps concentration (DC 10, rolled 15)"
    ]


def test_a_save_against_a_private_effect_stays_out_of_the_log(fight):
    ui, _, tiger, _ = fight
    effect = CustomEffect("Secret pact", "Bound by pact", ability="WIS", dc=30)
    ui._roll_effect_save(tiger, effect)
    QApplication.processEvents()
    assert "against Secret pact" in _gm_log(ui)
    assert _lines(ui) == []


@pytest.mark.parametrize("condition", ["", "Prone"])
def test_a_save_against_a_visible_effect_is_in_the_log(fight, condition):
    ui, _, tiger, _ = fight
    ui._roll_effect_save(
        tiger, CustomEffect("Fireball", condition, ability="DEX", dc=30)
    )
    QApplication.processEvents()
    assert "against Fireball" in _lines(ui)[0]


def test_casting_is_public_but_the_badge_it_leaves_isnt(fight):
    ui, _, tiger, _ = fight
    ui._log_event("Tiger casts Mage Armor", character=tiger["name"])
    ui._add_condition_to(tiger, "Mage Armor")
    QApplication.processEvents()
    assert "gains Mage Armor" in _gm_log(ui)
    assert _lines(ui) == ["[Pirate's turn] Tiger casts Mage Armor"]


def test_a_line_from_while_it_was_hidden_stays_private_after_the_reveal(fight):
    ui, _, tiger, bandit = fight
    tiger["conditions"] = ["Invisible"]
    _hit(ui, tiger, bandit)
    tiger["conditions"] = []
    ui._refresh_views()
    assert "Tiger" not in str(_lines(ui))


def test_a_line_they_already_read_stays_when_the_monster_hides(fight):
    ui, pirate, tiger, _ = fight
    _hit(ui, pirate, tiger)
    tiger["conditions"] = ["Invisible"]
    ui._refresh_views()
    assert len(_lines(ui)) == 1


@pytest.mark.parametrize("condition", ["Plotting betrayal", "Concentrating", "Bless"])
def test_a_monsters_private_conditions_stay_out_of_the_log(fight, condition):
    ui, _, tiger, _ = fight
    ui._add_condition_to(tiger, condition)
    ui._remove_condition_from(tiger, condition)
    QApplication.processEvents()
    assert condition in _gm_log(ui)
    assert _lines(ui) == []


def test_a_private_condition_expiring_stays_out_of_the_log(fight):
    """This line has no condition in its data: only its text names it."""
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Plotting betrayal")
    ui._log_event(
        "Tiger's Plotting betrayal expires", note_turn=False, character="Tiger"
    )
    QApplication.processEvents()
    assert _lines(ui) == []


@pytest.mark.parametrize("condition", ["Prone", "Bloodied"])
def test_a_monsters_visible_conditions_are_in_the_log(fight, condition):
    ui, _, tiger, _ = fight
    ui._add_condition_to(tiger, condition)
    ui._remove_condition_from(tiger, condition)
    QApplication.processEvents()
    log = _lines(ui)
    assert len(log) == 2
    assert f"Tiger gains {condition}" in log[0]
    assert f"Tiger loses {condition}" in log[1]


def test_a_players_own_custom_condition_is_in_the_log(fight):
    ui, pirate, *_ = fight
    pirate["_is_player"] = True
    ui._add_condition_to(pirate, "Inspired by a song")
    QApplication.processEvents()
    assert "Pirate gains Inspired by a song" in _lines(ui)[0]


# ---------------------------------------------------------------------------
# Keeping it current


def test_the_fight_reaches_the_link_by_itself(fight):
    ui, pirate, tiger, bandit = fight
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    ui.damage_type_combo.setCurrentIndex(
        ui.damage_type_combo.findData(DamageType.SLASHING.value)
    )
    ui.damage_input.setText("20")
    ui._apply_damage()
    QApplication.processEvents()
    assert _hp(_state(ui)["rows"][1]) == ["10 / 30"]

    ui._undo_last()
    QApplication.processEvents()
    assert _hp(_state(ui)["rows"][1]) == ["30 / 30"]

    tiger["conditions"].append("Prone")
    ui._rebuild_card(tiger)
    QApplication.processEvents()
    assert _state(ui)["rows"][1]["conditions"] == ["Prone"]

    ui._advance_turn()
    QApplication.processEvents()
    assert [r["turn"] for r in _state(ui)["rows"]] == ["", "now", "next"]

    ui._advance_turn()
    ui._advance_turn()
    QApplication.processEvents()
    assert _state(ui)["title"] == "Round 2"


def test_starting_the_link_shows_the_fight_as_it_is_now(fight):
    ui, _, tiger, _ = fight
    ui._player_server.stop()
    tiger["hp"] = 15
    ui._refresh_views()
    ui._start_player_server("127.0.0.1")
    assert _hp(_state(ui)["rows"][1]) == ["15 / 30"]


def test_before_the_fight_the_link_waits(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    ui._start_player_server("127.0.0.1")
    assert _state(ui) == WAITING


def test_nothing_listens_until_the_gm_starts_it(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    assert not ui._player_server.running
    assert ui._player_server.url is None
    assert not [t for t in threading.enumerate() if t.name == "player-server"]


def _screen_text(ui) -> str:
    """The Player Screen's title and rows. Not findChildren: the rows it
    replaced stay children until Qt's event loop deletes them."""
    view = ui._player_view
    rows = [
        view._rows_layout.itemAt(i).widget() for i in range(view._rows_layout.count())
    ]
    labels = [view._title] + [l for row in rows for l in row.findChildren(QLabel)]
    bars = [bar for row in rows for bar in row.findChildren(QProgressBar)]
    return " ".join([l.text() for l in labels] + [bar.format() for bar in bars])


def test_the_screen_and_the_link_dont_need_each_other(fight):
    ui, _, tiger, bandit = fight
    ui._toggle_player_view()
    tiger["hp"] = 15
    ui._refresh_views()
    assert _hp(_state(ui)["rows"][1]) == ["15 / 30"]
    assert "15 / 30" in _screen_text(ui)

    ui._toggle_player_view()  # closed: the link carries on
    assert ui._player_view is None
    bandit["hp"] = 1
    ui._refresh_views()
    assert _hp(_state(ui)["rows"][2]) == ["1 / 33"]

    ui._toggle_player_view()  # stopped: the screen carries on, nothing's published
    ui._player_server.stop()
    published = ui._player_server.feed.latest()
    tiger["hp"] = 30
    ui._refresh_views()
    assert "30 / 30" in _screen_text(ui) and "15 / 30" not in _screen_text(ui)
    assert ui._player_server.feed.latest() == published
    ui._toggle_player_view()


# ---------------------------------------------------------------------------
# Leaving and loading encounters


def _in_tiger_fight(tmp_path) -> CombatAppQt:
    ui = _campaign_ui(tmp_path)
    ui._load_encounter(TIGER, restart=False)
    _start(ui, 12)
    QApplication.processEvents()  # no refresh left pending to hide a missing one
    return ui


def test_end_encounter_clears_the_player_screen(tmp_path, say_yes):
    """DI-029: it stayed on the last round, monsters included."""
    ui = _in_tiger_fight(tmp_path)
    ui._toggle_player_view()
    assert "Round 1" in _screen_text(ui) and "Tiger" in _screen_text(ui)
    ui._end_encounter()
    assert _screen_text(ui) == "Waiting for the fight to start"
    ui._toggle_player_view()


def test_end_encounter_clears_the_link(tmp_path, say_yes):
    ui = _in_tiger_fight(tmp_path)
    ui._start_player_server("127.0.0.1")
    assert _names(_state(ui)) == ["Tiger"]
    ui._end_encounter()
    assert _state(ui) == WAITING


def test_load_encounter_takes_the_last_fight_off_the_link(tmp_path):
    ui = _in_tiger_fight(tmp_path)
    ui._start_player_server("127.0.0.1")
    ui._load_encounter(PIRATE, restart=False)
    QApplication.processEvents()
    assert _state(ui) == WAITING
    _start(ui, 9)
    QApplication.processEvents()
    assert _names(_state(ui)) == ["Pirate"]


def test_loading_a_fight_in_progress_shows_it_on_the_link(tmp_path):
    ui = _in_tiger_fight(tmp_path)
    tiger = ui.characters[0]
    ui._select_character(tiger)
    ui._select_target_character(tiger)
    ui.damage_type_combo.setCurrentIndex(
        ui.damage_type_combo.findData(DamageType.SLASHING.value)
    )
    ui.damage_input.setText("1")
    ui._apply_damage()
    ui._advance_turn()  # round 2, with one combatant
    ui._load_encounter(PIRATE, restart=False)
    ui._start_player_server("127.0.0.1")
    QApplication.processEvents()
    assert _state(ui) == WAITING

    ui._load_encounter(TIGER, restart=False)
    QApplication.processEvents()
    state = _state(ui)
    assert state["title"] == "Round 2"
    assert _names(state) == ["Tiger"]


# ---------------------------------------------------------------------------
# The HTTP side


def test_a_repeated_poll_gets_304_until_something_changes(fight):
    ui, _, tiger, _ = fight
    first = _poll(ui)
    assert first.status == 200
    etag = first.headers["ETag"]

    again = _poll(ui, etag)
    assert again.status == 304
    assert again.body == b""

    tiger["hp"] = 15
    ui._refresh_views()
    changed = _poll(ui, etag)
    assert changed.status == 200
    assert changed.headers["ETag"] != etag
    assert b"15 / 30" in changed.body


def test_state_is_never_cached_and_says_its_json(fight):
    ui, *_ = fight
    reply = _poll(ui)
    assert reply.headers["Cache-Control"] == "no-store"
    assert reply.headers["Content-Type"].startswith("application/json")
    assert _poll(ui, reply.headers["ETag"]).headers["Cache-Control"] == "no-store"


def test_the_page_is_served_at_the_root(fight):
    ui, *_ = fight
    reply = _ask(_port(ui._player_server), "/")
    assert reply.status == 200
    assert reply.headers["Content-Type"].startswith("text/html")
    assert reply.body == PAGE.read_bytes()


def test_the_page_is_read_once_when_the_server_starts(fight, monkeypatch, tmp_path):
    ui, *_ = fight
    monkeypatch.setattr(player_server, "_PAGE_PATH", tmp_path / "gone.html")
    assert _ask(_port(ui._player_server), "/").body == PAGE.read_bytes()


def test_a_tracking_parameter_on_the_link_changes_nothing(fight):
    ui, *_ = fight
    port = _port(ui._player_server)
    assert _ask(port, "/?fbclid=abc").body == PAGE.read_bytes()
    assert _ask(port, "/state?x=1").body == _poll(ui).body
    assert _ask(port, "/requirements.txt?x=1").status == 404


@pytest.mark.parametrize(
    "path",
    [
        "/nope",
        "/../requirements.txt",
        "/%2e%2e/requirements.txt",
        "/requirements.txt",
        "/player_page.html",
        "/player_server.py",
        "/Combat/CombatUIQt/player_view.py",
        "/Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json",
        "/index.html",
        "/state/",
        "/state.json",
    ],
)
def test_nothing_else_is_served(fight, path):
    ui, *_ = fight
    reply = _ask(_port(ui._player_server), path)
    assert reply.status == 404
    assert b"PyQt6" not in reply.body and b"import" not in reply.body


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
@pytest.mark.parametrize("path", ["/", "/state"])
def test_it_cant_be_written_to(fight, method, path):
    ui, *_ = fight
    before = _poll(ui).body
    assert _ask(_port(ui._player_server), path, method).status in (405, 501)
    assert _poll(ui).body == before


def test_polls_print_nothing(fight, capfd):
    ui, *_ = fight
    _poll(ui)
    _ask(_port(ui._player_server), "/nope")
    _ask(_port(ui._player_server), "/state", "POST")
    captured = capfd.readouterr()
    assert (captured.out, captured.err) == ("", "")


@pytest.mark.parametrize(
    "error, printed", [(ConnectionResetError(), False), (ValueError("a bug"), True)]
)
def test_a_dropped_phone_is_quiet_but_a_bug_is_not(fight, capsys, error, printed):
    ui, *_ = fight
    http_server = ui._player_server._http
    try:
        raise error
    except type(error):
        http_server.handle_error(None, ("127.0.0.1", 1))
    assert bool(capsys.readouterr().err) == printed


def test_a_client_that_goes_quiet_doesnt_keep_its_thread(fight, monkeypatch):
    ui, *_ = fight
    assert 0 < player_server._Handler.timeout <= 10
    monkeypatch.setattr(player_server._Handler, "timeout", 0.2)
    address = ("127.0.0.1", _port(ui._player_server))
    with socket.create_connection(address, timeout=5) as quiet:
        assert quiet.recv(1) == b"", "The server hangs up on it"


def test_its_threads_die_with_the_app(fight):
    ui, *_ = fight
    _poll(ui)
    (thread,) = [t for t in threading.enumerate() if t.name == "player-server"]
    assert thread.daemon
    assert ui._player_server._http.daemon_threads


def test_starting_needs_no_reverse_dns(monkeypatch):
    def refuse(*args):
        raise AssertionError("a reverse DNS lookup can freeze the window")

    monkeypatch.setattr(socket, "getfqdn", refuse)
    server = PlayerServer()
    server.start("127.0.0.1", 0)
    assert server.running


# ---------------------------------------------------------------------------
# Starting and stopping


def test_stop_closes_the_port_and_it_can_start_again(fight):
    ui, *_ = fight
    server = ui._player_server
    port = _port(server)
    server.stop()
    assert not server.running and server.url is None and server.host is None
    with pytest.raises(OSError):
        _ask(port)
    server.stop()  # twice is fine

    ui._start_player_server("127.0.0.1")
    assert _state(ui)["title"] == "Round 1"


@pytest.mark.skipif(
    os.name != "nt",
    reason="Without reuse-address, POSIX holds a closed port for a minute",
)
def test_a_stopped_server_can_have_its_port_back(fight):
    ui, *_ = fight
    server = ui._player_server
    port = _port(server)
    _poll(ui)
    server.stop()
    server.start("127.0.0.1", port)
    assert _port(server) == port
    assert _state(ui)["title"] == "Round 1"


def test_the_real_port_is_the_one_links_rely_on():
    assert PLAYER_PORT == 8765


def test_a_busy_port_is_a_plain_error():
    with socket.socket() as taken:
        taken.bind(("127.0.0.1", 0))
        taken.listen()
        port = taken.getsockname()[1]
        server = PlayerServer()
        with pytest.raises(PlayerServerError) as caught:
            server.start("127.0.0.1", port)
    assert str(caught.value) == (
        f"Port {port} is already in use on 127.0.0.1, so the link couldn't "
        "start. Is another copy of the combat app running?"
    )
    assert not server.running and server.url is None


def test_a_second_copy_of_the_app_cant_share_the_port():
    """allow_reuse_address would let it, on Windows, and a busy port would look
    like a working one."""
    first = PlayerServer()
    first.start("127.0.0.1", 0)
    port = _port(first)
    second = PlayerServer()
    with pytest.raises(PlayerServerError):
        second.start("127.0.0.1", port)
    assert not second.running
    assert _ask(port).status == 200


def test_any_other_failure_is_a_plain_error_too(monkeypatch, tmp_path):
    monkeypatch.setattr(player_server, "_PAGE_PATH", tmp_path / "gone.html")
    server = PlayerServer()
    with pytest.raises(PlayerServerError, match="The link couldn't start"):
        server.start("127.0.0.1", 0)
    assert not server.running


# ---------------------------------------------------------------------------
# The feed


def test_the_etag_hashes_the_content():
    feed = PlayerFeed()
    feed.publish("Round 1", [{"name": "Tiger"}])
    _, etag = feed.latest()
    feed.publish("Round 2", [{"name": "Tiger"}])
    _, other = feed.latest()
    feed.publish("Round 1", [{"name": "Tiger"}])
    assert other != etag
    assert feed.latest()[1] == etag, "The same content is the same ETag"
    assert re.fullmatch(r'"[^"]{16,}"', etag), "A quoted ETag, not a small counter"


def test_the_feed_keeps_finished_bytes_not_the_rows_it_was_given():
    feed = PlayerFeed()
    rows = [{"name": "Tiger"}]
    feed.publish("Round 1", rows)
    before = feed.latest()
    rows[0]["hp"] = 30
    rows.append({"name": "Hidden"})
    assert feed.latest() == before
    assert isinstance(before[0], bytes)


def test_the_server_never_imports_the_combatants_or_qt():
    tree = ast.parse(Path(player_server.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add("." * node.level + (node.module or ""))
    roots = {name.split(".")[0] for name in imported}
    assert roots <= {
        "collections",
        "errno",
        "hashlib",
        "http",
        "ipaddress",
        "json",
        "pathlib",
        "socket",
        "socketserver",
        "sys",
        "threading",
    }, "the standard library only"


# ---------------------------------------------------------------------------
# Which address to offer


def test_addresses_rank_wifi_first():
    addresses = [
        "172.22.80.1",  # WSL
        "10.5.0.2",  # a VPN
        "192.168.0.143",
        "172.31.0.9",
        "10.0.0.7",
    ]
    assert rank_addresses(addresses) == [
        "192.168.0.143",
        "10.5.0.2",
        "10.0.0.7",
        "172.22.80.1",
        "172.31.0.9",
    ]


def test_a_tailscale_address_is_offered_after_every_other_kind():
    addresses = ["100.101.102.103", "172.22.80.1", "10.5.0.2", "192.168.0.143"]
    assert rank_addresses(addresses) == [
        "192.168.0.143",
        "10.5.0.2",
        "172.22.80.1",
        "100.101.102.103",
    ]


def test_ranking_keeps_the_given_order_within_a_kind():
    assert rank_addresses(["192.168.56.1", "192.168.0.143"]) == [
        "192.168.56.1",
        "192.168.0.143",
    ]


@pytest.mark.parametrize(
    "address",
    [
        "169.254.13.37",  # no network was found
        "127.0.0.1",
        "0.0.0.0",
        "8.8.8.8",  # public: that would face the internet
        "172.15.255.255",  # just outside 172.16-31
        "172.32.0.1",
        "100.63.255.255",  # just outside Tailscale's 100.64-127
        "100.128.0.0",
        "fe80::1",
    ],
)
def test_ranking_drops_what_players_cant_or_shouldnt_reach(address):
    assert rank_addresses([address, "192.168.0.143"]) == ["192.168.0.143"]


def test_ranking_drops_repeats():
    assert rank_addresses(["10.0.0.7", "10.0.0.7"]) == ["10.0.0.7"]


def test_lan_addresses_offers_the_way_out_and_the_adapters_ranked(monkeypatch):
    def adapter(address: str):
        return (socket.AF_INET, socket.SOCK_STREAM, 0, "", (address, 0))

    monkeypatch.setattr(socket.socket, "connect", lambda self, address: None)
    monkeypatch.setattr(socket.socket, "getsockname", lambda self: ("10.5.0.2", 50000))
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a: [
            adapter("172.22.80.1"),
            adapter("192.168.0.143"),
            adapter("169.254.13.37"),
        ],
    )
    assert lan_addresses() == ["192.168.0.143", "10.5.0.2", "172.22.80.1"]


def test_lan_addresses_survives_a_pc_with_no_network(monkeypatch):
    def fail(*args):
        raise OSError("no network")

    monkeypatch.setattr(socket, "getaddrinfo", fail)
    monkeypatch.setattr(socket.socket, "connect", fail)
    assert lan_addresses() == []


# ---------------------------------------------------------------------------
# The Player Link dialog


def _button(parent, text: str) -> QPushButton:
    return next(b for b in parent.findChildren(QPushButton) if b.text() == text)


def _link(dlg) -> str:
    return dlg.findChild(QLabel, "playerLink").text()


def _message(dlg) -> str:
    return dlg.findChild(QLabel, "playerLinkMessage").text()


def test_the_button_starts_the_link_and_shows_it(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, _button(ui._window, "Player Link").click)
    assert ui._player_server.running
    assert ui._player_server.host == "127.0.0.1"
    assert _link(dlg) == ui._player_server.url
    assert _link(dlg).startswith("http://127.0.0.1:")
    assert _message(dlg) == ""
    assert _state(ui) == WAITING
    combo = dlg.findChild(QComboBox)
    assert [combo.itemText(i) for i in range(combo.count())] == [
        "127.0.0.1",
        "localhost",
    ]


def test_copy_puts_the_link_on_the_clipboard(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    _button(dlg, "Copy").click()
    assert QApplication.clipboard().text() == ui._player_server.url
    assert _message(dlg) == "Link copied."


def test_the_main_window_says_the_link_is_on_until_its_stopped(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, _button(ui._window, "Player Link").click)
    _button(dlg, "Close").click()
    assert ui._player_server.running
    assert _button(ui._window, "Player Link (on)") is ui._player_link_btn

    dlg = open_dialog(monkeypatch, ui._player_link_btn.click)
    _button(dlg, "Stop").click()
    assert not ui._player_server.running
    assert _button(ui._window, "Player Link") is ui._player_link_btn


def test_closing_leaves_it_running_and_reopening_shows_the_same_link(
    tmp_path, monkeypatch
):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    url = ui._player_server.url
    _button(dlg, "Close").click()
    assert ui._player_server.url == url
    assert _ask(_port(ui._player_server)).status == 200

    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert ui._player_server.url == url, "On port 0, a restart would change it"
    assert _link(dlg) == url


def test_reopening_shows_the_running_address_not_the_best_one(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    dlg.findChild(QComboBox).setCurrentText("localhost")
    url = ui._player_server.url
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert dlg.findChild(QComboBox).currentText() == "localhost"
    assert ui._player_server.url == url


def test_stop_ends_it_and_the_button_starts_it_again(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    port = _port(ui._player_server)
    _button(dlg, "Stop").click()
    assert not ui._player_server.running
    assert ui._status_label.text() == "Player link stopped."
    with pytest.raises(OSError):
        _ask(port)

    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert ui._player_server.running
    assert _link(dlg) == ui._player_server.url


def test_a_restart_goes_back_to_the_address_the_gm_picked(tmp_path, monkeypatch):
    """Or phones on that link would stay on Lost connection, and the link would
    be back on the address the GM had rejected."""
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    dlg.findChild(QComboBox).setCurrentText("localhost")
    _button(dlg, "Stop").click()

    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert ui._player_server.host == "localhost"
    assert dlg.findChild(QComboBox).currentText() == "localhost"
    assert _link(dlg).startswith("http://localhost:")


def test_a_restart_takes_the_best_address_if_the_picked_one_is_gone(
    tmp_path, monkeypatch
):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    dlg.findChild(QComboBox).setCurrentText("localhost")
    _button(dlg, "Stop").click()

    monkeypatch.setattr(dialogs_mixin, "lan_addresses", lambda: ["127.0.0.1"])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert ui._player_server.host == "127.0.0.1"


def test_picking_another_address_moves_the_link(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    old_port = _port(ui._player_server)
    dlg.findChild(QComboBox).setCurrentText("localhost")
    assert ui._player_server.host == "localhost"
    assert _link(dlg) == ui._player_server.url
    assert _link(dlg).startswith("http://localhost:")
    assert _ask(_port(ui._player_server)).status == 200
    with pytest.raises(OSError):
        _ask(old_port)


def test_a_running_address_the_pc_no_longer_lists_is_still_shown(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    open_dialog(monkeypatch, ui._show_player_link_dialog)
    url = ui._player_server.url
    monkeypatch.setattr(dialogs_mixin, "lan_addresses", lambda: ["localhost"])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert dlg.findChild(QComboBox).currentText() == "127.0.0.1"
    assert ui._player_server.url == url


def test_a_busy_port_is_said_in_the_dialog(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    with socket.socket() as taken:
        taken.bind(("127.0.0.1", 0))
        taken.listen()
        port = taken.getsockname()[1]
        monkeypatch.setattr(turn_panel_mixin, "PLAYER_PORT", port)
        dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert f"Port {port} is already in use" in _message(dlg)
    assert "Traceback" not in _message(dlg) and "Error" not in _message(dlg)
    assert _link(dlg) == "Not running"
    assert not _button(dlg, "Stop").isEnabled()
    assert not _button(dlg, "Copy").isEnabled()
    assert not ui._player_server.running
    assert ui._player_link_btn.text() == "Player Link"

    # The port's free now: picking an address tries again.
    monkeypatch.setattr(turn_panel_mixin, "PLAYER_PORT", 0)
    dlg.findChild(QComboBox).setCurrentText("localhost")
    assert ui._player_server.running
    assert _message(dlg) == ""
    assert _button(dlg, "Stop").isEnabled() and _button(dlg, "Copy").isEnabled()


def test_with_no_network_it_says_so(tmp_path, monkeypatch):
    monkeypatch.setattr(dialogs_mixin, "lan_addresses", lambda: [])
    ui = make_ui(tmp_path, [Pirate()])
    dlg = open_dialog(monkeypatch, ui._show_player_link_dialog)
    assert _link(dlg) == "Not running"
    assert "No network found" in _message(dlg)
    assert not ui._player_server.running
    assert not dlg.findChild(QComboBox).isEnabled()


# ---------------------------------------------------------------------------
# The page (read, not run: a browser would have to run it)


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def test_the_page_needs_nothing_from_the_internet():
    page = _page()
    assert not re.search(r"https?:|[\"'(]//|<link|@import|url\(|src=", page)


def test_the_page_never_builds_html_from_text():
    page = _page()
    assert "textContent" in page
    for risky in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
        assert risky not in page


def test_the_page_is_laid_out_for_a_phone_in_the_player_screens_colors():
    page = _page()
    assert (
        '<meta name="viewport" content="width=device-width, initial-scale=1">' in page
    )
    for color in ("#1a1a2e", "#c9a84c", "#3a2e00", "#0f3460"):
        assert color in page


def test_the_page_polls_without_letting_requests_pile_up():
    page = _page()
    assert "setInterval" not in page
    assert "setTimeout(poll, POLL_MS)" in page
    assert re.search(r"POLL_MS = 1000\b", page)
    assert re.search(r"TIMEOUT_MS = 3000\b", page)
    assert re.search(r"FAILURES_BEFORE_BANNER = 3\b", page)
    assert "visibilitychange" in page
    assert "Lost connection" in page
    assert "If-None-Match" in page
    # Without these, a quiet fight would put the banner on every phone, and the
    # banner would never leave.
    assert "response.status === 304" in page
    assert "banner.hidden = true" in page
    assert "if (polling)" in page


def test_the_log_opens_by_itself_and_stays_open_through_an_update():
    """A <details> needs no script, and only the lines inside it are replaced."""
    page = _page()
    assert re.search(r'<details id="log" hidden>\s*<summary>Encounter log', page)
    assert 'lines.textContent = "";' in page
    assert "log.textContent" not in page
