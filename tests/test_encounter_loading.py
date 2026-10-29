"""Encounters: a campaign's encounters.py (Combat/EncounterConfig.py), the
logs prepared from it (Combat/EncounterLogs.py, Combat/Tools/
prepare_encounters.py), and the combat window playing them
(Combat/CombatUIQt/encounters_mixin.py, rests_mixin.py): Load Encounter,
Continue / Restart, End Encounter, the party view between encounters, rests,
and how the encounter logs and the player log (Combat/PlayerLog.py) split the
work."""

import dataclasses
import json
import os
from functools import cache

import pytest
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
)

import Combat.PlayerLog as PlayerLog
import Combat.Scenarios as Scenarios
from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder,
)
from Combat.Campaign import Campaign
from Combat.Combatants import Pirate
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.encounters_mixin import CONTINUE, RESTART
from Combat.CombatUIQt.rest import apply_long_rest
from Combat.EncounterConfig import (
    CampaignSpec,
    CombatantSpec,
    EncounterSpec,
    resolve_players,
    validate,
)
from Combat.EncounterLogs import (
    ENDED_KEY,
    UNDONE_SESSIONS_KEY,
    is_prepared,
    prepare_log,
    prepared_log,
    read_log_status,
    restart_log,
    scenario_log_path,
)
from Combat.Monsters.CR_1.monsters import GoblinBoss, Tiger
from Combat.Scenario import CombatScenario
from Combat.Tools.prepare_encounters import prepare_campaign
from Core.Definitions import DamageType
from tests._combat_ui import open_dialog, qapp
from tests._snapshot_helpers import build

SLASHING = DamageType.SLASHING.value
EDMUND_BUILD = "Y2024_Paladin_Devotion_Edmund"
CLOVER_BUILD = "Y2024_Bard_Valor_Clover"

PIRATES = CombatScenario(
    name="pirate_ambush",
    title="Pirate Ambush",
    combatants=lambda: [Pirate(), Pirate()],
    monster_summary=["2× Pirate"],
)
TIGER = CombatScenario(
    name="tiger_den",
    title="Tiger Den",
    combatants=lambda: [Tiger()],
    players=["Edmund"],
    monster_summary=["Tiger"],
)


@cache
def _sheet(build_name: str):
    return build(build_name)


def _party() -> list:
    return [_sheet(EDMUND_BUILD), _sheet(CLOVER_BUILD)]


def _names() -> list[str]:
    return [cs.character_name for cs in _party()]


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@pytest.fixture
def say_yes(monkeypatch):
    asked = []

    def question(*args, **kwargs):
        asked.append(args[1:3])
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked


# ---------------------------------------------------------------------------
# The encounters config


PARTY = [
    Y2024PaladinDevotionEdmundCharacterBuilder,
    Y2024BardValorCloverCharacterBuilder,
]


def _config(encounters, party=PARTY) -> CampaignSpec:
    return CampaignSpec(
        name="test_campaign",
        title="Test Campaign",
        description="",
        party=list(party),
        encounters=list(encounters),
    )


TIGER_CONFIG = EncounterSpec(
    id="tiger_den",
    title="Tiger Den",
    description="A tiger.",
    players=["Edmund"],
    monsters=[CombatantSpec(Tiger, "Stripes")],
)


@pytest.mark.parametrize("campaign", sorted(Scenarios.CAMPAIGNS))
def test_every_campaign_config_is_valid(campaign):
    campaign = Scenarios.CAMPAIGNS[campaign]
    assert campaign.config is not None
    party = [cs.character_name for cs in campaign.players()]
    assert validate(campaign.config, party) == []


def test_combatant_lines_are_numbered_when_several():
    assert CombatantSpec(GoblinBoss, "Goblin Boss", 2).names() == [
        "Goblin Boss 1",
        "Goblin Boss 2",
    ]
    assert CombatantSpec(Tiger).names() == [None]
    (tiger,) = CombatantSpec(Tiger).build()
    assert tiger.combatant_type == "Tiger" and not tiger.name
    assert CombatantSpec(GoblinBoss, "Goblin Boss", 2).summary() == "2× Goblin Boss"
    # Without a name, several are numbered after the class.
    assert CombatantSpec(Tiger, count=2).names() == ["Tiger 1", "Tiger 2"]


def test_players_match_parts_of_names():
    party = ["Edmund", "Clover", "Kivi Jätti", "Gabriel Greybeard"]
    assert resolve_players(None, party) == party
    assert resolve_players(["kivi", "Edmund"], party) == ["Edmund", "Kivi Jätti"]
    with pytest.raises(KeyError):
        resolve_players(["Obmar"], party)
    with pytest.raises(KeyError):
        resolve_players(["e"], party)  # more than one


def test_validate_names_every_problem():
    config = _config(
        [
            EncounterSpec(id="Bad Id", title="x", combatants_per_column=0),
            EncounterSpec(
                id="twice", title="", monsters=[CombatantSpec(Tiger, count=0)]
            ),
            EncounterSpec(id="twice", title="y", players=["Obmar"]),
        ]
    )
    problems = validate(config, ["Edmund"])
    expected = [
        "'Bad Id': id must be snake_case",
        "'Bad Id': combatants_per_column must be at least 1",
        "'twice': needs a title",
        "Tiger: count must be at least 1",
        "'twice': id used twice",
        "player 'Obmar' matches no one",
    ]
    for text in expected:
        assert any(text in p for p in problems), (text, problems)


def test_a_campaign_comes_from_its_config(tmp_path):
    campaign = Campaign.from_config(_config([TIGER_CONFIG]), tmp_path)
    (scenario,) = campaign.scenarios
    assert (campaign.name, campaign.title) == ("test_campaign", "Test Campaign")
    assert (scenario.name, scenario.display_title) == ("tiger_den", "Tiger Den")
    assert scenario.players == ["Edmund"]
    assert [c.name for c in scenario.build_combatants()] == ["Stripes"]
    assert [cs.character_name for cs in campaign.players()] == _names()


# ---------------------------------------------------------------------------
# Prepared logs


def _in_progress_log(path, hp: int = 3, round_number: int = 4, extra=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    tiger = {"name": "Tiger", "hp": hp, "max_hp": 30, "ac": 12, "conditions": []}
    data = {
        "encounter": path.stem,
        "title": "Tiger Den",
        "players": ["Edmund"],
        "round_number": round_number,
        "combatants": [tiger, {**tiger, "name": "Tiger 2", "hp": 0}],
        "round_1": [{"text": "Tiger took 27 damage"}],
        **(extra or {}),
    }
    path.write_text(json.dumps(data))


def test_a_prepared_log_holds_the_encounter_and_who_takes_part():
    log = prepared_log(TIGER, ["Edmund"])
    assert {k: log[k] for k in ("encounter", "title", "players", "round_number")} == {
        "encounter": "tiger_den",
        "title": "Tiger Den",
        "players": ["Edmund"],
        "round_number": 1,
    }
    (tiger,) = log["combatants"]
    assert (tiger["name"], tiger["hp"], tiger["max_hp"]) == ("Tiger", 30, 30)


def test_preparing_logs(tmp_path):
    path = tmp_path / "tiger_den.json"
    assert not is_prepared(path)
    assert prepare_log(path, TIGER, ["Edmund"], write=False) == "prepared"
    assert not path.exists()
    assert prepare_log(path, TIGER, ["Edmund"]) == "prepared"
    assert is_prepared(path)
    assert prepare_log(path, TIGER, ["Edmund"]) == "unchanged"
    # Not started yet: a change in the config is taken in.
    assert prepare_log(path, TIGER, ["Edmund", "Clover"]) == "updated"
    assert json.loads(path.read_text())["players"] == ["Edmund", "Clover"]


def test_a_fight_in_progress_is_left_alone_but_gets_its_header(tmp_path):
    path = tmp_path / "tiger_den.json"
    _in_progress_log(path)
    old = json.loads(path.read_text())
    for key in ("encounter", "title", "players"):
        del old[key]
    path.write_text(json.dumps(old))
    os.utime(path, (1_700_000_000, 1_700_000_000))

    assert prepare_log(path, TIGER, ["Edmund"]) == "in progress, header added"
    data = json.loads(path.read_text())
    assert data["encounter"] == "tiger_den" and data["players"] == ["Edmund"]
    header = ("encounter", "title", "players")
    assert {k: v for k, v in data.items() if k not in header} == old
    assert path.stat().st_mtime == 1_700_000_000  # last played is kept
    assert prepare_log(path, TIGER, ["Edmund"]) == "in progress"


def test_names_outside_ascii_survive_preparing(tmp_path):
    # Logs are UTF-8 whatever the platform's default encoding (cp1252 on
    # Windows), so "Kivi Jätti" isn't turned into "Kivi JÃ¤tti".
    path = tmp_path / "tiger_den.json"
    event = {"text": "Kivi Jätti takes 3 damage", "character": "Kivi Jätti"}
    log = {"round_number": 1, "combatants": [], "round_1": [event]}
    path.write_bytes(json.dumps(log, ensure_ascii=False).encode("utf-8"))
    assert prepare_log(path, TIGER, ["Kivi Jätti"]) == "in progress, header added"
    data = json.loads(path.read_bytes().decode("utf-8"))
    assert data["round_1"] == [event] and data["players"] == ["Kivi Jätti"]


def test_status_of_a_fight(tmp_path):
    path = tmp_path / "tiger_den.json"
    assert read_log_status(path) is None
    prepare_log(path, TIGER, [])
    assert read_log_status(path) is None  # prepared, not started
    _in_progress_log(path)
    status = read_log_status(path)
    assert status is not None
    assert status.describe().startswith("Round 4, 1 of 2 standing, last played ")
    _in_progress_log(path, hp=0, extra={ENDED_KEY: "2026-10-29T20:00:00"})
    status = read_log_status(path)
    assert status is not None and status.ended
    assert status.describe().startswith("Ended in round 4, all 2 down")


def test_restart_backs_up_the_fight_and_takes_it_out_of_the_player_log(tmp_path):
    path = tmp_path / "CombatLogs" / "tiger_den.json"
    player_log_path = tmp_path / "PlayerLogs" / "main_party.json"
    _in_progress_log(path)
    old = json.loads(path.read_text())
    sessions = [
        {"type": "long_rest"},
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
    fresh = prepared_log(TIGER, ["Edmund"])

    backup = restart_log(path, fresh, player_log, player_log_path)
    assert backup is not None and backup.name.startswith("tiger_den_restarted_")
    assert player_log["sessions"] == [sessions[0], sessions[2]]
    backup_data = json.loads(backup.read_text())
    assert backup_data[UNDONE_SESSIONS_KEY] == [sessions[1], sessions[3]]
    assert backup_data["round_1"] == old["round_1"]
    assert json.loads(path.read_text())["combatants"][0]["hp"] == 30


def test_the_prepare_tool_writes_nothing_while_the_config_has_problems(tmp_path):
    bad = EncounterSpec(id="Bad Id", title="x")
    campaign = Campaign.from_config(_config([TIGER_CONFIG, bad]), tmp_path)
    problems, results = prepare_campaign(campaign)
    assert problems and results == []
    assert not (tmp_path / "CombatLogs").exists()


def test_the_prepare_tool_prepares_each_encounter(tmp_path):
    second = dataclasses.replace(TIGER_CONFIG, id="second_den")
    campaign = Campaign.from_config(_config([TIGER_CONFIG, second]), tmp_path)
    assert prepare_campaign(campaign, write=False) == (
        [],
        [("tiger_den", "prepared"), ("second_den", "prepared")],
    )
    assert prepare_campaign(campaign, only=["tiger_den"]) == (
        [],
        [("tiger_den", "prepared")],
    )
    log = json.loads((tmp_path / "CombatLogs" / "tiger_den.json").read_text())
    assert log["players"] == ["Edmund"]
    assert [c["name"] for c in log["combatants"]] == ["Stripes (Tiger)"]
    assert not (tmp_path / "CombatLogs" / "second_den.json").exists()


# ---------------------------------------------------------------------------
# The window


def _ui(tmp_path, party=None, scenario=None, player_log=True) -> CombatAppQt:
    """One run of the window for a campaign in tmp_path (PlayerLogs/,
    CombatLogs/) with the PIRATES and TIGER encounters, both prepared.
    Without a `scenario` it opens on the party between encounters."""
    qapp()
    logs = tmp_path / "CombatLogs"
    for s in (PIRATES, TIGER):
        path = scenario_log_path(logs, s.name)
        if not path.exists():
            prepare_log(path, s, resolve_players(s.players, _names()))
    ui = CombatAppQt(
        [],
        _party() if party is None else party,
        combat_log_dir=logs,
        log_path=scenario_log_path(logs, scenario.name) if scenario else None,
        player_log_path=(
            str(tmp_path / "PlayerLogs" / "main_party.json") if player_log else None
        ),
        scenario_name=scenario.name if scenario else None,
        scenarios=[PIRATES, TIGER],
    )
    ui._build_window()
    return ui


def _start(ui):
    """Roll initiative and start the fight on the initiative screen."""
    for i, char in enumerate(ui.characters):
        ui._initiative_inputs[id(char)].setText(str(20 - i))
    ui._start_combat()


def _hit(ui, source, target, amount: int):
    ui._select_character(source)
    ui._select_target_character(target)
    ui.damage_type_combo.setCurrentIndex(ui.damage_type_combo.findData(SLASHING))
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def _journal(tmp_path) -> list[dict]:
    path = tmp_path / "PlayerLogs" / "main_party.json"
    return json.loads(path.read_text())["sessions"] if path.exists() else []


def _player(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"].startswith(name))


def _in_fight(tmp_path, scenario=TIGER) -> CombatAppQt:
    ui = _ui(tmp_path)
    ui._load_encounter(scenario, restart=False)
    _start(ui)
    return ui


def test_between_encounters_the_window_shows_the_party_and_logs_nothing(tmp_path):
    ui = _ui(tmp_path)
    assert ui.phase == "PARTY" and ui.log_file is None
    assert [c["name"] for c in ui.characters] == _names()
    view = ui._scroll_area.widget()
    assert view is not None
    texts = [label.text() for label in view.findChildren(QLabel)]
    assert texts[0] == "Between encounters"
    assert any(t.startswith("Edmund:") for t in texts)
    # Nothing can be selected, so nothing changed or logged.
    ui._select_character(ui.characters[0])
    assert ui.selected_character is None
    assert not ui._add_combatant_btn.isEnabled()
    assert not ui._end_encounter_btn.isEnabled()
    assert sorted(p.name for p in (tmp_path / "CombatLogs").iterdir()) == [
        "pirate_ambush.json",
        "tiger_den.json",
    ]


def test_an_unprepared_encounter_cannot_be_loaded(tmp_path, monkeypatch):
    ui = _ui(tmp_path)
    scenario_log_path(tmp_path / "CombatLogs", "tiger_den").unlink()
    warned = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: warned.append(a[2]))
    ui._load_encounter(TIGER, restart=False)
    assert warned and "isn't prepared" in warned[0]
    assert ui.phase == "PARTY"


def test_loading_an_encounter_brings_its_monsters_and_players(tmp_path):
    ui = _ui(tmp_path)
    ui._load_encounter(TIGER, restart=False)
    assert ui.phase == "INITIATIVE"
    assert [c["name"] for c in ui.characters] == ["Edmund", "Tiger"]  # not Clover
    assert ui.log_file == scenario_log_path(tmp_path / "CombatLogs", "tiger_den")
    assert ui._window.windowTitle() == "DnD Combat Engine — Tiger Den"
    assert set(ui._initiative_inputs) == {id(c) for c in ui.characters}

    ui._load_encounter(PIRATES, restart=False)  # the whole party
    assert [c["name"] for c in ui.characters] == [*_names(), "Pirate", "Pirate"]


def test_continuing_a_fight_where_it_stopped(tmp_path):
    ui = _in_fight(tmp_path)
    edmund, tiger = ui.characters
    _hit(ui, edmund, tiger, 7)
    ui._advance_turn()
    ui._advance_turn()  # round 2

    ui = _ui(tmp_path, scenario=TIGER)
    assert ui._encounter_log_to_open is not None
    ui._open_encounter_log(ui._encounter_log_to_open, restart=False)
    assert ui.phase == "COMBAT" and ui.round_number == 2
    assert _player(ui, "Tiger")["hp"] == 23


def test_continuing_a_fight_keeps_the_turn_order_and_whose_turn_it_is(tmp_path):
    pack = CombatScenario(
        name="tiger_pack",
        title="Tiger Pack",
        combatants=lambda: [
            *CombatantSpec(Tiger, "Tiger", count=2, group="Tigers").build(),
            Pirate(),
        ],
        players=["Edmund"],
    )
    path = scenario_log_path(tmp_path / "CombatLogs", pack.name)
    prepare_log(path, pack, ["Edmund"])
    ui = _ui(tmp_path)
    ui._load_encounter(pack, restart=False)
    edmund, tiger1, tiger2, pirate = ui.characters
    for char, roll in ((edmund, 5), (tiger1, 18), (pirate, 12)):
        ui._initiative_inputs[id(char)].setText(str(roll))
    ui._start_combat()
    order = [tiger1, tiger2, pirate, edmund]
    assert ui.initiative_order == order
    ui._advance_turn()  # the Pirate's turn
    _hit(ui, pirate, tiger1, 4)
    ui._advance_turn()  # Edmund's turn, saved though nothing happened in it

    ui = _ui(tmp_path)
    ui._load_encounter(pack, restart=False)
    assert ui.phase == "COMBAT"
    assert [c["name"] for c in ui.initiative_order] == [c["name"] for c in order]
    assert ui.characters == ui.initiative_order  # the cards follow it too
    assert ui._current_turn_name() == "Edmund"
    assert ui._turn_counter_label.text() == "Turn 3 / 3"
    ui._advance_turn()
    assert ui.round_number == 2 and ui._current_turn_name() == "Tigers"


def test_the_startup_question_is_only_asked_for_a_fight_in_progress(tmp_path):
    ui = _ui(tmp_path, scenario=TIGER)
    path = scenario_log_path(tmp_path / "CombatLogs", "tiger_den")
    assert ui._ask_continue_or_restart(path, "Tiger Den") == CONTINUE


@pytest.mark.parametrize(
    "button, expected",
    [("Continue Encounter", CONTINUE), ("Restart Encounter", RESTART), (None, None)],
)
def test_asks_when_a_fight_is_in_progress(tmp_path, monkeypatch, button, expected):
    ui = _ui(tmp_path)
    path = tmp_path / "CombatLogs" / "tiger_den.json"
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


def test_restart_brings_the_prepared_encounter_back_and_undoes_the_fight(tmp_path):
    ui = _in_fight(tmp_path)
    edmund, tiger = ui.characters
    full_hp = edmund["hp"]
    _hit(ui, tiger, edmund, 7)
    assert [s["scenario"] for s in _journal(tmp_path)] == ["tiger_den"]

    ui._load_encounter(TIGER, restart=True)
    assert ui.phase == "INITIATIVE"
    assert _player(ui, "Edmund")["hp"] == full_hp
    assert _player(ui, "Tiger")["hp"] == 30
    assert _journal(tmp_path) == []
    (backup,) = (tmp_path / "CombatLogs").glob("tiger_den_restarted_*.json")
    assert "takes 7" in json.loads(backup.read_text())["round_1"][0]["text"]


def test_the_player_log_says_where_the_party_has_been(tmp_path):
    ui = _in_fight(tmp_path)
    edmund, tiger = ui.characters
    _hit(ui, tiger, edmund, 5)
    (entry,) = _journal(tmp_path)
    assert entry == {
        "type": "encounter",
        "scenario": "tiger_den",
        "log": "../CombatLogs/tiger_den.json",
        "started_at": entry["started_at"],
    }
    # Every detail is in the encounter log.
    assert ui.log_file is not None
    (event,) = json.loads(ui.log_file.read_text())["round_1"]
    assert (event["character"], event["action"], event["value"]["hp_delta"]) == (
        "Edmund",
        "damage",
        -5,
    )


def test_the_party_comes_back_as_they_left(tmp_path):
    ui = _in_fight(tmp_path)
    edmund, tiger = ui.characters
    full_hp = edmund["hp"]
    _hit(ui, tiger, edmund, 5)
    assert _player(_ui(tmp_path), "Edmund")["hp"] == full_hp - 5


def test_end_encounter_records_it_and_goes_back_to_the_party(tmp_path, say_yes):
    ui = _in_fight(tmp_path)
    edmund, tiger = ui.characters
    _hit(ui, tiger, edmund, 5)
    fight_log = ui.log_file
    assert fight_log is not None

    ui._end_encounter()
    fight = json.loads(fight_log.read_text())
    assert fight["round_1"][-1]["text"] == "--- Tiger Den ended ---"
    (entry,) = _journal(tmp_path)
    assert entry[ENDED_KEY] == fight[ENDED_KEY]
    assert ui.phase == "PARTY" and ui.log_file is None
    assert [c["name"] for c in ui.characters] == _names()
    assert _player(ui, "Edmund")["hp"] == edmund["hp"]

    # Continuing it later reopens the fight.
    ui._load_encounter(TIGER, restart=False)
    assert ui.phase == "COMBAT"
    assert ENDED_KEY not in json.loads(fight_log.read_text())
    assert ENDED_KEY not in _journal(tmp_path)[0]


def test_rests_only_between_fights(tmp_path):
    def buttons(ui):
        return ui._short_rest_btn.isEnabled(), ui._long_rest_btn.isEnabled()

    ui = _ui(tmp_path)
    assert buttons(ui) == (True, True)
    ui._load_encounter(TIGER, restart=False)  # loaded, not started
    assert buttons(ui) == (True, True)
    _start(ui)
    assert buttons(ui) == (False, False)
    assert buttons(_ui(tmp_path, player_log=False)) == (False, False)


def test_long_rest_before_starting_an_encounter(tmp_path, say_yes):
    ui = _in_fight(tmp_path, PIRATES)
    edmund = _player(ui, "Edmund")
    full_hp = edmund["hp"]
    _hit(ui, _player(ui, "Pirate"), edmund, 6)

    ui._load_encounter(TIGER, restart=False)
    ui._long_rest()
    assert _player(ui, "Edmund")["hp"] == full_hp
    _start(ui)
    _hit(ui, _player(ui, "Tiger"), _player(ui, "Edmund"), 3)
    assert [s.get("scenario") or s["type"] for s in _journal(tmp_path)] == [
        "pirate_ambush",
        "long_rest",
        "tiger_den",
    ]
    assert _player(_ui(tmp_path), "Edmund")["hp"] == full_hp - 3
    # The statistics still count the fight before the rest.
    stats = _ui(tmp_path)._compute_player_log_stats()
    assert stats["Edmund"]["damage_taken"] == 9


def _heal_in_short_rest(monkeypatch, amount: int):
    """Make the short-rest window heal every player `amount` and close."""

    def exec_(dlg):
        for field in dlg.findChildren(QLineEdit):
            field.setText(str(amount))
        next(b for b in dlg.findChildren(QPushButton) if "Apply" in b.text()).click()
        return 0

    monkeypatch.setattr(QDialog, "exec", exec_)


def test_a_short_rest_is_one_line_in_the_player_log(tmp_path, monkeypatch, say_yes):
    ui = _in_fight(tmp_path)
    edmund = _player(ui, "Edmund")
    full_hp = edmund["hp"]
    _hit(ui, _player(ui, "Tiger"), edmund, 8)
    ui._end_encounter()
    _heal_in_short_rest(monkeypatch, 3)

    ui._short_rest()
    assert _player(ui, "Edmund")["hp"] == full_hp - 5
    rest = _journal(tmp_path)[-1]
    assert rest["type"] == "short_rest" and "log" not in rest
    assert any("Edmund heals 3 HP" in e["text"] for e in rest["events"])
    # No log of its own, and the next run starts from there.
    assert sorted(p.name for p in (tmp_path / "CombatLogs").iterdir()) == [
        "pirate_ambush.json",
        "tiger_den.json",
    ]
    assert _player(_ui(tmp_path), "Edmund")["hp"] == full_hp - 5


def test_a_long_rest_from_the_command_line(tmp_path):
    ui = _in_fight(tmp_path)
    edmund = _player(ui, "Edmund")
    full_hp = edmund["hp"]
    _hit(ui, _player(ui, "Tiger"), edmund, 4)
    apply_long_rest(str(tmp_path / "PlayerLogs" / "main_party.json"))
    assert _player(_ui(tmp_path), "Edmund")["hp"] == full_hp
    assert [s["type"] for s in _journal(tmp_path)] == ["encounter", "long_rest"]


def test_the_load_encounter_dialog_lists_the_campaigns_encounters(
    tmp_path, monkeypatch
):
    ui = _ui(tmp_path)
    scenario_log_path(tmp_path / "CombatLogs", "pirate_ambush").unlink()
    _in_progress_log(tmp_path / "CombatLogs" / "tiger_den.json")
    dlg = open_dialog(monkeypatch, ui._show_load_encounter_dialog)
    (scenario_list,) = dlg.findChildren(QListWidget)
    items = [scenario_list.item(i).text() for i in range(scenario_list.count())]  # type: ignore[union-attr]
    assert items[0] == "Pirate Ambush\n    Not prepared"
    assert items[1].startswith("Tiger Den\n    Round 4, 1 of 2 standing")

    buttons = {b.text(): b for b in dlg.findChildren(QPushButton)}
    assert not buttons["Start Encounter"].isEnabled()
    assert not buttons["Restart Encounter"].isEnabled()
    details = [label.text() for label in dlg.findChildren(QLabel)][-1]
    assert "Players: the whole party" in details and "isn't prepared" in details
    scenario_list.setCurrentRow(1)
    assert buttons["Start Encounter"].text() == "Continue Encounter"
    assert buttons["Start Encounter"].isEnabled()
    assert buttons["Restart Encounter"].isEnabled()


def test_journal_helpers():
    sessions = [{"type": "encounter"}, {"type": "long_rest"}, {"type": "short_rest"}]
    assert PlayerLog.since_long_rest(sessions) == [{"type": "short_rest"}]
    assert PlayerLog.session_rounds({"type": "short_rest", "events": [1]}, ".") == {
        "round_1": [1]
    }
    assert (
        PlayerLog.session_label({"type": "encounter", "scenario": "wrath_of_durmor"})
        == "Encounter: Wrath of Durmor"
    )
