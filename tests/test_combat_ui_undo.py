"""Undo in the combat UI (LoggingMixin._undo_last), pinned against
tests/snapshots/combat_ui_undo.json: for every kind of history entry, what
undoing it does to the target and source (HP, conditions, slots, death
saves, feature uses, battle stats), the encounter and player logs, and which
cards get rebuilt. A change meant to alter undo regenerates it on purpose:

    UPDATE_SNAPSHOTS=1 pytest tests/test_combat_ui_undo.py
"""

import json

import pytest

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.stats import DICT_STAT_KEYS, STAT_KEYS
from Combat.Definitions import Action
from tests._combat_ui import check_golden, make_ui
from tests._snapshot_helpers import SNAPSHOT_DIR

GOLDEN_PATH = SNAPSHOT_DIR / "combat_ui_undo.json"

_SEEDED_STAT = 3
_SEEDED_NAMED = {"Poisoned": 1, "Bless": 2, "Rage": 1}


class _LimitedFeature:
    name = "Rage"
    uses = 2


def _ui(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    for char in ui.characters:
        char["stats"] = {
            **{key: _SEEDED_STAT for key in STAT_KEYS},
            **{key: dict(_SEEDED_NAMED) for key in DICT_STAT_KEYS},
        }
        char["spell_slots"] = {1: 1, 2: 0}
        char["conditions"] = ["Poisoned"]
        char["death_saves_fail"] = 2
        char["death_saves_success"] = 1
        char["feature_uses_used"] = {"Rage": 1}
        char["_feature_objects"] = [_LimitedFeature()]
    pirate, tiger = ui.characters
    ui.selected_character = pirate
    return ui, pirate, tiger


def _damage(**overrides):
    value = {
        "hp_delta": -5,
        "temp_delta": -2,
        "dmg": 7,
        "damage_type": "Fire",
        "source_name": "Pirate",
        "target_name": "Tiger",
        "knockout": True,
    }
    return (Action.DAMAGE, {**value, **overrides})


def _source_target(action, **value):
    return (
        action,
        {"source_name": "Pirate", "target_name": "Tiger", **value},
    )


CASES = {
    "damage": _damage(),
    "damage_more_than_the_stats_hold": _damage(dmg=9),
    "damage_no_type_no_knockout": _damage(damage_type=None, knockout=False),
    "damage_unknown_source": _damage(source_name="Nobody"),
    "damage_unknown_target": _damage(target_name="Nobody"),
    "damage_legacy_tuple": (Action.DAMAGE, (-5, -2)),
    "heal": _source_target(Action.HEAL, heal=4),
    "heal_more_than_the_stats_hold": _source_target(Action.HEAL, heal=9),
    "heal_without_source": (
        Action.HEAL,
        {"heal": 4, "source_name": None, "target_name": "Tiger"},
    ),
    "heal_legacy_int": (Action.HEAL, 4),
    "add_condition": _source_target(Action.ADD_CONDITION, condition="Poisoned"),
    "add_condition_not_present": _source_target(
        Action.ADD_CONDITION, condition="Prone"
    ),
    "remove_condition_absent": _source_target(
        Action.REMOVE_CONDITION, condition="Prone"
    ),
    "remove_condition_present": _source_target(
        Action.REMOVE_CONDITION, condition="Poisoned"
    ),
    "add_temp_hp": _source_target(Action.ADD_TEMP_HP, amount=4),
    "add_temp_hp_more_than_the_stats_hold": _source_target(
        Action.ADD_TEMP_HP, amount=9
    ),
    "remove_spell_slot": (Action.REMOVE_SPELL_SLOT, 2),
    "add_spell_slot": (Action.ADD_SPELL_SLOT, 1),
    "add_spell_slot_already_empty": (Action.ADD_SPELL_SLOT, 2),
    "cast_spell": (Action.CAST_SPELL, {"spell_name": "Bless"}),
    "cast_spell_by_name": (Action.CAST_SPELL, "Bless"),
    "death_save_fail": (Action.DEATH_SAVE_FAIL, False),
    "death_save_fail_that_killed": (Action.DEATH_SAVE_FAIL, True),
    "death_save_success": (Action.DEATH_SAVE_SUCCESS, None),
    "enable_limited_feature": (Action.ENABLE_FEATURE, {"feature_name": "Rage"}),
    "enable_unknown_feature": (Action.ENABLE_FEATURE, "Second Wind"),
    "regain_feature_charge": (Action.REGAIN_FEATURE_CHARGE, "Rage"),
}


def _changed_stats(stats: dict) -> dict:
    """Only what differs from the seeded stats, to keep goldens readable."""
    changed = {}
    for key, value in stats.items():
        seeded = dict(_SEEDED_NAMED) if key in DICT_STAT_KEYS else _SEEDED_STAT
        if value != seeded:
            changed[key] = value
    return changed


def _state(char: dict) -> dict:
    return {
        "hp": char["hp"],
        "temp_hp": char["temp_hp"],
        "conditions": char["conditions"],
        "spell_slots": char["spell_slots"],
        "death_saves": [char["death_saves_fail"], char["death_saves_success"]],
        "feature_uses_used": char["feature_uses_used"],
        "stats": _changed_stats(char["stats"]),
    }


def _undo(ui, entry, capsys) -> dict:
    ui.history.append(entry)
    ui._log_event("first event", note_turn=False)
    ui._log_event("event to undo", note_turn=False)
    rebuilt = []
    ui._rebuild_card = lambda char: rebuilt.append(char["name"])
    capsys.readouterr()

    ui._undo_last()

    log = json.loads(ui.log_file.read_text())
    return {
        "pirate": _state(ui.characters[0]),
        "tiger": _state(ui.characters[1]),
        "history_left": len(ui.history),
        "round_log": log.get("round_1"),
        "rebuilt": rebuilt,
        "printed": capsys.readouterr().out,
    }


@pytest.mark.parametrize("case", sorted(CASES))
def test_undo_unchanged(tmp_path, capsys, case):
    ui, _, _ = _ui(tmp_path)
    check_golden(GOLDEN_PATH, case, _undo(ui, CASES[case], capsys))


def test_undo_with_nothing_to_undo_does_nothing(tmp_path):
    ui, pirate, tiger = _ui(tmp_path)
    before = [_state(pirate), _state(tiger)]
    ui._undo_last()
    assert [_state(pirate), _state(tiger)] == before


def test_undo_needs_a_selection_for_source_actions(tmp_path):
    ui, pirate, _ = _ui(tmp_path)
    ui.selected_character = None
    ui.history.append((Action.REMOVE_SPELL_SLOT, 1))
    ui._log_event("cast", note_turn=False)
    ui._undo_last()
    assert pirate["spell_slots"] == {1: 1, 2: 0}
    assert len(ui.history) == 1


def test_undo_keeps_history_when_the_round_has_no_log(tmp_path):
    # Nothing logged this round: the entry stays on the history, untouched.
    ui, pirate, _ = _ui(tmp_path)
    ui.history.append((Action.REMOVE_SPELL_SLOT, 1))
    ui._undo_last()
    assert pirate["spell_slots"] == {1: 1, 2: 0}
    assert len(ui.history) == 1


def test_undo_also_pops_the_player_log(tmp_path):
    ui, _, _ = _ui(tmp_path)
    ui.player_log_file = tmp_path / "players.json"
    ui.player_log_data = {"sessions": [{}]}
    ui.history.append((Action.REMOVE_SPELL_SLOT, 1))
    ui._log_event("first", note_turn=False)
    ui._log_event("cast", note_turn=False)
    ui._undo_last()
    assert ui.player_log_data["sessions"][-1]["round_1"] == [{"text": "first"}]
