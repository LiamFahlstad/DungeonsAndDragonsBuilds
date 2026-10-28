"""Lifetime player statistics: the stats (the report tool and the in-app
Players tabs) read every entry of the player log, the events of the encounter
logs those entries point to, and the archives older long rests made."""

import json
import sys

import pytest

import Combat.Scenarios as Scenarios
from Combat.CombatUIQt.rest import apply_long_rest
from Combat.CombatUIQt.stats import (
    compute_player_log_stats,
    long_rest_archive_sessions,
    player_log_history,
)
from Combat.Definitions import Action
from Combat.Tools import create_player_statistics_report as report
from tests._combat_ui import make_ui


def _session(started_at: str, attacker: str, dmg: int) -> dict:
    return {
        "type": "encounter",
        "scenario": "test_fight",
        "started_at": started_at,
        "round_1": [
            {
                "text": f"{attacker} hits",
                "character": "Goblin",
                "action": Action.DAMAGE,
                "value": {
                    "hp_delta": -dmg,
                    "temp_delta": 0,
                    "dmg": dmg,
                    "damage_type": "Slashing",
                    "source_name": attacker,
                    "target_name": "Goblin",
                    "knockout": False,
                },
            }
        ],
    }


def _write(path, *sessions):
    path.write_text(json.dumps({"sessions": list(sessions)}))


@pytest.fixture
def party_log(tmp_path):
    """main_party.json after two long rests, archived out of order on disk."""
    log = tmp_path / "main_party.json"
    _write(
        tmp_path / "main_party_long_rest_20261010_193313.json", _session("2", "A", 5)
    )
    _write(
        tmp_path / "main_party_long_rest_20260908_220000.json", _session("1", "A", 3)
    )
    _write(log, _session("3", "B", 7))
    # Not archives of this log: another party's, and another rest kind.
    _write(
        tmp_path / "other_party_long_rest_20261010_193313.json", _session("x", "A", 100)
    )
    _write(
        tmp_path / "main_party_short_rest_20261010_193313.json", _session("y", "A", 100)
    )
    return log


def test_archives_are_read_oldest_first(party_log):
    sessions = long_rest_archive_sessions(party_log)
    assert [s["started_at"] for s in sessions] == ["1", "2"]


def test_history_is_the_archives_then_the_log(party_log):
    history = player_log_history(party_log)
    assert [s["started_at"] for s in history["sessions"]] == ["1", "2", "3"]


def test_lifetime_stats_count_archived_sessions(party_log):
    stats = compute_player_log_stats(player_log_history(party_log))
    assert stats["A"]["damage_dealt"] == 8
    assert stats["B"]["damage_dealt"] == 7
    assert stats["Goblin"]["damage_taken"] == 15


def test_a_real_long_rest_keeps_the_history(tmp_path):
    log = tmp_path / "main_party.json"
    _write(log, _session("1", "A", 3), _session("2", "A", 4))
    before = compute_player_log_stats(player_log_history(log))
    apply_long_rest(str(log))
    sessions = json.loads(log.read_text())["sessions"]
    assert [s["type"] for s in sessions] == ["encounter", "encounter", "long_rest"]
    assert compute_player_log_stats(player_log_history(log)) == before


def test_stats_read_the_encounter_logs_entries_point_to(tmp_path):
    log = tmp_path / "PlayerLogs" / "main_party.json"
    fight = tmp_path / "CombatLogs" / "fight.json"
    fight.parent.mkdir()
    fight.write_text(
        json.dumps(
            {k: v for k, v in _session("1", "A", 6).items() if k.startswith("round_")}
        )
    )
    log.parent.mkdir()
    _write(
        log,
        {"type": "encounter", "scenario": "fight", "log": "../CombatLogs/fight.json"},
    )
    stats = compute_player_log_stats(player_log_history(log))
    assert stats["A"]["damage_dealt"] == 6


def test_in_app_player_stats_include_archives(tmp_path, party_log):
    ui = make_ui(tmp_path)
    ui.player_log_file = party_log
    ui.player_log_data = json.loads(party_log.read_text())
    ui.player_log_data["sessions"].append(_session("4", "B", 1))  # this session
    stats = ui._compute_player_log_stats()
    assert stats["A"]["damage_dealt"] == 8
    assert stats["B"]["damage_dealt"] == 8


def test_report_covers_the_campaign_history(tmp_path, monkeypatch):
    campaign = Scenarios.CAMPAIGNS["time_loop_pr"]
    first, second = report.player_roster(campaign)[:2]
    log = tmp_path / "main_party.json"
    _write(
        tmp_path / "main_party_long_rest_20261010_193313.json",
        _session("2026-10-01T19:00:00", first, 11),
    )
    _write(log, _session("2026-10-20T19:00:00", second, 13))
    output = tmp_path / "report.html"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "report",
            "--campaign",
            "time_loop_pr",
            "--log",
            str(log),
            "--output",
            str(output),
        ],
    )

    report.main()

    html = output.read_text(encoding="utf-8")
    assert "Player Statistics — Time Loop PR (Main Party)" in html
    assert "Sessions: 2" in html and "Long rests: 1" in html
    assert "First session: 2026-10-01" in html
    assert f"<span>{first}</span>" in html and ">11</span>" in html
    assert f"<span>{second}</span>" in html and ">13</span>" in html


def test_report_without_a_player_log_says_so(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["report", "--campaign", "grims_castle", "--log", str(tmp_path / "none.json")],
    )
    with pytest.raises(SystemExit, match="No player log for campaign 'grims_castle'"):
        report.main()
