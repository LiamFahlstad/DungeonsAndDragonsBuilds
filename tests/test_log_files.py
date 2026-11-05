"""Combat/LogFiles.py: logs are written all at once (a failed write leaves the
old log as it was) and a log that isn't valid JSON is reported with how to get
it back."""

import json
import os

import pytest

import Combat.LogFiles as LogFiles
from Combat.LogFiles import BrokenLogError, read_json, write_json


def test_a_write_replaces_the_log_and_leaves_no_temporary_file(tmp_path):
    path = tmp_path / "CombatLogs" / "tiger_den.json"
    write_json(path, {"round_number": 1})
    write_json(path, {"round_number": 2})
    assert read_json(path) == {"round_number": 2}
    assert [p.name for p in path.parent.iterdir()] == ["tiger_den.json"]


def test_a_write_that_fails_halfway_leaves_the_old_log(tmp_path, monkeypatch):
    path = tmp_path / "tiger_den.json"
    write_json(path, {"round_number": 1})

    def power_cut(_fd):
        raise OSError("power cut")

    monkeypatch.setattr(os, "fsync", power_cut)
    with pytest.raises(OSError):
        write_json(path, {"round_number": 2, "round_1": ["a long fight"]})
    assert read_json(path) == {"round_number": 1}


def test_a_write_that_cannot_be_encoded_leaves_the_old_log(tmp_path):
    path = tmp_path / "tiger_den.json"
    write_json(path, {"round_number": 1})
    with pytest.raises(TypeError):
        write_json(path, {"round_number": object()})
    assert read_json(path) == {"round_number": 1}


def test_a_log_held_open_for_a_moment_is_still_written(tmp_path, monkeypatch):
    path = tmp_path / "tiger_den.json"
    real_replace = os.replace
    refusals = []

    def busy_once(src, dst):
        if not refusals:
            refusals.append(dst)
            raise PermissionError("in use")
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", busy_once)
    monkeypatch.setattr(LogFiles, "REPLACE_WAIT_SECONDS", 0)
    write_json(path, {"round_number": 3})
    assert refusals and read_json(path) == {"round_number": 3}


def test_a_broken_log_says_which_file_and_how_to_get_it_back(tmp_path):
    path = tmp_path / "tiger_den.json"
    path.write_text('{"round_number": 4, "round_1": [', encoding="utf-8")
    backup = tmp_path / "tiger_den_restarted_2026-11-05_20-00-00.json"
    backup.write_text(json.dumps({"round_number": 1}), encoding="utf-8")
    with pytest.raises(BrokenLogError) as caught:
        read_json(path)
    message = str(caught.value)
    assert caught.value.path == path
    assert str(path) in message
    assert f"git checkout -- {path.as_posix()}" in message
    assert backup.name in message
