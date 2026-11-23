"""A fight continued in a new window (the next launch) and the party's history:
what a player keeps of the turn and of the fight's stats (DI-093), a spell's
badge not counted as a condition (DI-094), and damage taken at 0 Hit Points
(DI-003: 2024 rules, Playing the Game, "Damage at 0 Hit Points")."""

from functools import cache

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Combat.CombatUIQt import CombatAppQt
from Combat.Fight.stats import compute_player_log_stats, player_log_history
from Combat.Definitions import Action
from Combat.EncounterConfig import resolve_players
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerLog import is_round_key
from Combat.Scenario import CombatScenario
from tests._combat_ui import make_ui, qapp
from tests._snapshot_helpers import build

# Warlock 3, a player: makes Death Saving Throws at 0 Hit Points.
WARLOCK = "Y2024WarlockArchfeyThistleFeydreamCharacterBuilder"

TIGER = CombatScenario(
    name="tiger_den",
    title="Tiger Den",
    combatants=lambda: [Tiger()],
    players=["Thistle"],
    monster_summary=["Tiger"],
)


@cache
def _sheet(build_name: str):
    return build(build_name)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """Whatever a hit would ask (a reaction, a trigger) is declined."""
    monkeypatch.setattr(QDialog, "exec", lambda dlg: 0)
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.No
    )


def _player(ui) -> dict:
    return next(c for c in ui.characters if c.get("_is_player"))


def _tiger(ui) -> dict:
    return next(c for c in ui.characters if not c.get("_is_player"))


def _damage(ui, source, target, text: str, attack_roll: str = ""):
    ui._select_character(source)
    ui._select_target_character(target)
    ui.attack_roll_input.setText(attack_roll)
    ui.damage_input.setText(text)
    ui._apply_damage()


def _events(ui, action: str) -> list[dict]:
    log = ui._read_log()
    return [
        e
        for key in log
        if is_round_key(key)
        for e in log[key]
        if isinstance(e, dict) and e.get("action") == action
    ]


# ---------------------------------------------------------------------------
# A fight continued in a new window, with the party's player log


def _party_ui(tmp_path) -> CombatAppQt:
    """One run of the window for the Warlock's party, between encounters,
    with the TIGER encounter prepared."""
    qapp()
    logs = tmp_path / "CombatLogs"
    path = scenario_log_path(logs, TIGER.name)
    if not path.exists():
        name = _sheet(WARLOCK).character_name
        assert name is not None
        names = [name]
        prepare_log(path, TIGER, resolve_players(TIGER.players, names))
    ui = CombatAppQt(
        [],
        [_sheet(WARLOCK)],
        combat_log_dir=logs,
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenario_name=None,
        scenarios=[TIGER],
    )
    ui._build_window()
    return ui


def _fight(tmp_path) -> CombatAppQt:
    """The Warlock (initiative 20) against the Tiger (10), round 1."""
    ui = _party_ui(tmp_path)
    ui._load_encounter(TIGER, restart=False)
    player, tiger = _player(ui), _tiger(ui)
    ui._initiative_inputs[id(player)].setText("20")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    return ui


def _reopened(tmp_path) -> CombatAppQt:
    """The next launch: a new window continuing the same fight."""
    ui = _party_ui(tmp_path)
    ui._load_encounter(TIGER, restart=False)
    assert ui.phase == "COMBAT"
    return ui


def _lifetime(ui) -> dict[str, dict]:
    """The Statistics' lifetime (Players) tab's stats, by name."""
    assert ui.player_log_file is not None
    return compute_player_log_stats(player_log_history(ui.player_log_file))


def _fight_stats(char: dict) -> dict:
    return {key: value for key, value in char["stats"].items() if value}


def test_a_continued_fight_keeps_what_a_player_spent_of_the_round(tmp_path):
    ui = _fight(tmp_path)
    player = _player(ui)
    ui._add_action_use("Action", player)
    ui._add_action_use("Reaction", player)
    assert player["action_uses"] == {"Action": 1, "Reaction": 1}

    again = _player(_reopened(tmp_path))
    assert again["action_uses"] == {"Action": 1, "Reaction": 1}
    assert again["action_uses"] == player["action_uses"]


def test_a_continued_fight_keeps_what_attack_rolls_showed_of_a_players_ac(
    tmp_path,
):
    ui = _fight(tmp_path)
    player, tiger = _player(ui), _tiger(ui)
    _damage(ui, tiger, player, "1 slashing", attack_roll="25")  # a hit
    _damage(ui, tiger, player, "1 slashing", attack_roll="2")  # a miss
    assert player["ac_at_most"] == 25
    assert player["ac_above"] == 2

    again = _player(_reopened(tmp_path))
    assert (again.get("ac_above"), again.get("ac_at_most")) == (2, 25)


def test_a_continued_fight_keeps_the_damage_a_player_dealt(tmp_path):
    ui = _fight(tmp_path)
    player, tiger = _player(ui), _tiger(ui)
    _damage(ui, player, tiger, "7 fire")
    _damage(ui, player, tiger, "3 cold")
    assert player["stats"]["damage_dealt"] == 10
    assert player["stats"]["damage_dealt_fire"] == 7
    assert player["stats"]["damage_dealt_cold"] == 3

    reopened = _reopened(tmp_path)
    again = _player(reopened)
    assert _fight_stats(again) == _fight_stats(player)
    # Not counted twice on the monster, whose stats come with it.
    assert _tiger(reopened)["stats"]["damage_taken"] == 10
    # The Statistics' lifetime tab says the same.
    lifetime = _lifetime(ui)
    assert lifetime[player["name"]]["damage_dealt"] == 10


def test_a_continued_fight_keeps_the_conditions_a_player_gave(tmp_path):
    ui = _fight(tmp_path)
    player, tiger = _player(ui), _tiger(ui)
    ui._add_condition_to(tiger, "Prone", player)
    assert player["stats"]["conditions_given"] == 1

    again = _player(_reopened(tmp_path))
    assert again["stats"]["conditions_given"] == 1
    assert again["stats"]["conditions_given_by_name"] == {"Prone": 1}


# ---------------------------------------------------------------------------
# A spell's badge isn't one more condition, live or replayed


def test_a_spells_badge_counts_in_no_stats_after_replay(tmp_path):
    ui = _fight(tmp_path)
    player, tiger = _player(ui), _tiger(ui)
    ui._add_condition_to(player, "Paralyzed", tiger)
    ui._add_condition_to(player, "Hold Person", tiger, counted=False)
    assert player["stats"]["conditions_received"] == 1
    assert player["stats"]["conditions_received_by_name"] == {"Paralyzed": 1}
    (badge,) = [
        e
        for e in _events(ui, Action.ADD_CONDITION)
        if e["value"]["condition"] == "Hold Person"
    ]
    assert badge["value"]["counted"] is False

    again = _player(_reopened(tmp_path))
    assert "Hold Person" in again["conditions"]
    assert again["stats"]["conditions_received"] == 1
    assert again["stats"]["conditions_received_by_name"] == {"Paralyzed": 1}
    lifetime = _lifetime(ui)
    assert lifetime[player["name"]]["conditions_received"] == 1
    assert lifetime[tiger["name"]]["conditions_given"] == 1
    assert lifetime[tiger["name"]]["conditions_given_by_name"] == {"Paralyzed": 1}


def test_an_older_logs_condition_without_the_key_still_counts():
    event = {
        "text": "Hero gains Prone from Orc",
        "character": "Hero",
        "action": Action.ADD_CONDITION.value,
        "value": {"condition": "Prone", "source_name": "Orc", "target_name": "Hero"},
    }
    stats = compute_player_log_stats({"sessions": [{"round_1": [event]}]})
    assert stats["Hero"]["conditions_received"] == 1
    assert stats["Orc"]["conditions_given"] == 1


# ---------------------------------------------------------------------------
# Damage at 0 Hit Points


@pytest.fixture
def dying(tmp_path):
    """The Warlock at 0 Hit Points, dying, and the Tiger attacking it."""
    ui = make_ui(tmp_path, [Tiger()], [_sheet(WARLOCK)])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("20")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    _damage(ui, tiger, player, f"{player['hp']} slashing")
    assert player["hp"] == 0
    assert ui._char_death_state(player) == "dying"
    assert (player["death_saves_fail"], player["death_saves_success"]) == (0, 0)
    return ui, player, tiger


def test_damage_at_0_hp_is_a_failed_death_save(dying):
    ui, player, tiger = dying
    _damage(ui, tiger, player, "3 slashing")
    assert player["hp"] == 0
    assert player["death_saves_fail"] == 1
    _damage(ui, tiger, player, "2 slashing")
    assert player["death_saves_fail"] == 2


def test_a_critical_hit_at_0_hp_is_two_failed_death_saves(dying):
    ui, player, tiger = dying
    _damage(ui, tiger, player, "3 slashing", attack_roll="nat 20")
    assert player["death_saves_fail"] == 2


def test_a_third_failure_from_damage_kills(dying):
    ui, player, tiger = dying
    _damage(ui, tiger, player, "3 slashing", attack_roll="nat 20")
    _damage(ui, tiger, player, "3 slashing")
    assert player["death_saves_fail"] == 3
    assert ui._char_death_state(player) == "dead"
    assert player["stats"]["deaths"] == 1


def test_damage_at_0_hp_of_at_least_the_hp_maximum_kills(dying):
    ui, player, tiger = dying
    _damage(ui, tiger, player, f"{player['max_hp']} slashing")
    assert ui._char_death_state(player) == "dead"
    assert player["stats"]["deaths"] == 1


def test_damage_ends_stable(dying):
    ui, player, tiger = dying
    player["death_saves_success"] = 3
    assert ui._char_death_state(player) == "stabilized"
    _damage(ui, tiger, player, "3 slashing")
    assert ui._char_death_state(player) == "dying"
    assert (player["death_saves_fail"], player["death_saves_success"]) == (1, 0)


def test_no_damage_is_no_failed_death_save(dying):
    ui, player, tiger = dying
    _damage(ui, tiger, player, "0 slashing")
    assert player["death_saves_fail"] == 0


def test_undo_takes_back_the_failed_death_save(dying):
    ui, player, tiger = dying
    _damage(ui, tiger, player, "3 slashing", attack_roll="nat 20")
    ui._undo_last()
    assert player["death_saves_fail"] == 0
    assert not _events(ui, Action.DEATH_SAVE_FAIL)


@pytest.mark.parametrize(
    "hits, stable",
    [
        ([("3 slashing", "")], False),
        ([("3 slashing", "nat 20")], False),
        ([("3 slashing", "nat 20"), ("3 slashing", "")], False),
        ([("3 slashing", "")], True),
        ([("999 slashing", "")], False),
    ],
)
def test_the_failed_death_saves_replay(dying, hits, stable):
    ui, player, tiger = dying
    if stable:
        player["death_saves_success"] = 3
    before = {k: player[k] for k in ("death_saves_fail", "death_saves_success")}
    for text, roll in hits:
        _damage(ui, tiger, player, text, attack_roll=roll)
    replayed = dict(player, **before, stats={})
    for event in _events(ui, Action.DEATH_SAVE_FAIL):
        ui._apply_replay_action(replayed, event["action"], event["value"])
    assert replayed["death_saves_fail"] == player["death_saves_fail"]
    assert replayed["death_saves_success"] == player["death_saves_success"]
    assert replayed["stats"].get("deaths", 0) == player["stats"]["deaths"]
    lifetime = compute_player_log_stats(
        {"sessions": [{"round_1": _events(ui, Action.DEATH_SAVE_FAIL)}]}
    )
    deaths = lifetime.get(player["name"], {}).get("deaths", 0)
    assert deaths == player["stats"]["deaths"]


def test_a_monster_at_0_hp_makes_no_death_saves(dying):
    ui, player, tiger = dying
    _damage(ui, player, tiger, f"{tiger['hp']} fire")
    _damage(ui, player, tiger, "3 fire")
    assert all(
        e["character"] == player["name"] for e in _events(ui, Action.DEATH_SAVE_FAIL)
    )
    assert "death_saves_fail" not in tiger or tiger["death_saves_fail"] == 0


def test_a_continued_fight_keeps_the_failed_death_saves(tmp_path):
    ui = _fight(tmp_path)
    player, tiger = _player(ui), _tiger(ui)
    _damage(ui, tiger, player, f"{player['hp']} slashing")
    _damage(ui, tiger, player, "3 slashing", attack_roll="nat 20")
    assert player["death_saves_fail"] == 2

    again = _player(_reopened(tmp_path))
    assert (again["hp"], again["death_saves_fail"]) == (0, 2)


def test_a_continued_fight_keeps_a_players_dash(tmp_path):
    """The Dash action's movement this turn (Combat/Arena/arena.py's
    DASHES_KEY) and its badge come back with the fight."""
    from Combat.Arena.arena import DASHES_KEY, movement_ft

    ui = _fight(tmp_path)
    player = _player(ui)
    speed = movement_ft(player)
    ui._add_condition_to(player, "Dash", player)
    assert movement_ft(player) == 2 * speed
    again = _player(_reopened(tmp_path))
    assert again[DASHES_KEY] == 1
    assert "Dash" in again["conditions"]
    assert movement_ft(again) == 2 * speed
