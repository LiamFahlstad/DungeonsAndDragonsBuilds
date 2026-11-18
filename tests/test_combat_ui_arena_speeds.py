"""Speeds on the battle map in the combat window (Notes/combat-arena-plan.md,
step 26): the speed bar picking the speed a creature moves by and how high
it flies, a walk by its Fly Speed, the Fly spell giving one, and a flyer
falling when it can't stay aloft."""

from functools import cache

import pytest
from PyQt6.QtWidgets import QComboBox, QDialog, QPushButton, QSpinBox

from Combat.Arena.arena import MOVED_KEY, POSITION_KEY, distance_ft
from Combat.Arena.geometry import Cell
from Combat.Arena.speeds import ALTITUDE_KEY, FLY, MODE_KEY, WALK, speeds
from Combat.CombatUIQt.arena_view import token_rows
from Combat.CombatUIQt.effect_options import effect_options
from Combat.Combatants import Pirate
from Combat.EncounterLogs import TURN_PREFIX
from Combat.Monsters.CR_1.monsters import GiantEagle
from tests._combat_ui import answer_out_of_resources, make_ui
from tests._snapshot_helpers import build

DRUID = "Y2024DruidLandRowanThistledownCharacterBuilder"
ROWAN = "Rowan Thistledown"
EAGLE = "Giant Eagle"


@cache
def _builds():
    return (build(DRUID),)


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


def _logged(ui) -> list[str]:
    lines = []
    for key, events in ui._read_log().items():
        if key.startswith("round_") and isinstance(events, list):
            for event in events:
                match = TURN_PREFIX.match(str(event["text"]))
                lines.append(match.group(2) if match else str(event["text"]))
    return lines


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """The Giant Eagle (Speed 10 ft., Fly 80 ft.; on its turn) at C6, the
    Pirate at G6, Rowan at C10; the map shown and in use."""
    answer_out_of_resources(monkeypatch)
    ui = make_ui(tmp_path, [GiantEagle(), Pirate()], list(_builds()))
    rolls = {EAGLE: "20", "Pirate": "15", ROWAN: "10"}
    for char in ui.characters:
        ui._initiative_inputs[id(char)].setText(rolls[char["name"]])
    ui._start_combat()
    eagle, pirate, rowan = (_named(ui, n) for n in (EAGLE, "Pirate", ROWAN))
    eagle[POSITION_KEY] = [2, 5]
    pirate[POSITION_KEY] = [6, 5]
    rowan[POSITION_KEY] = [2, 9]
    ui.arena_settings.in_use = True
    if not ui._arena_shown():
        ui._toggle_view()
    ui._select_character(eagle)
    ui._refresh_views()
    return ui, eagle, pirate, rowan


def _bar(ui):
    return (
        ui._speed_bar,
        ui._speed_bar.findChild(QComboBox, "moveMode"),
        ui._speed_bar.findChild(QSpinBox, "moveAltitude"),
    )


def _fly(ui, char: dict):
    _, mode, _ = _bar(ui)
    mode.setCurrentIndex(mode.findData(FLY))
    assert char.get(MODE_KEY) == FLY


def test_the_speed_bar_offers_the_sources_speeds(fight):
    ui, eagle, pirate, _ = fight
    bar, mode, altitude = _bar(ui)
    assert not bar.isHidden()
    assert [mode.itemText(i) for i in range(mode.count())] == [
        "Walk 10 ft.",
        "Fly 80 ft.",
    ]
    assert mode.currentData() == WALK and altitude.isHidden()
    ui._select_character(pirate)  # one speed: no bar
    ui._refresh_views()
    assert bar.isHidden()


def test_flying_moves_by_its_fly_speed(fight):
    ui, eagle, *_ = fight
    assert max(ui._arena_reach(EAGLE).values()) <= 10
    _fly(ui, eagle)
    assert f"{EAGLE} moves by its Fly Speed now (80 ft.; 80 ft. left this turn)." in (
        _logged(ui)
    )
    reach = ui._arena_reach(EAGLE)
    assert Cell(18, 5) in reach, "80 ft. along the row"
    ui._move_combatant(eagle, Cell(12, 5))
    assert any(
        line.startswith(f"{EAGLE} flies from C6 to M6 (50 ft.; 30 of 80 ft. left")
        for line in _logged(ui)
    )
    ui._undo_last()
    ui._undo_last()
    eagle = _named(ui, EAGLE)
    assert MODE_KEY not in eagle and eagle[POSITION_KEY] == [2, 5]


def test_flying_up_spends_movement_and_counts_into_distances(fight):
    ui, eagle, pirate, _ = fight
    _fly(ui, eagle)
    _, _, altitude = _bar(ui)
    assert not altitude.isHidden()
    altitude.setValue(30)
    assert eagle[ALTITUDE_KEY] == 30 and eagle[MOVED_KEY] == 30
    assert f"{EAGLE} flies up 30 ft. (to 30 ft. up; 50 ft. left this turn)." in (
        _logged(ui)
    )
    # Large, its nearest cell 15 ft. from the Pirate, and 30 ft. up.
    assert distance_ft(eagle, pirate, ui._map_settings()) == 15 + 30
    (row,) = [
        r
        for r in token_rows(ui.characters, ui.arena_settings, [], None, [])
        if r.name == EAGLE
    ]
    assert row.altitude_ft == 30
    ui._undo_last()
    eagle = _named(ui, EAGLE)
    assert ALTITUDE_KEY not in eagle and not eagle.get(MOVED_KEY)


def test_it_lands_before_it_walks(fight):
    ui, eagle, *_ = fight
    _fly(ui, eagle)
    _, mode, altitude = _bar(ui)
    altitude.setValue(20)
    mode.setCurrentIndex(mode.findData(WALK))
    assert eagle[MODE_KEY] == FLY, "refused"
    assert "bring it down to 0 ft. to land first" in ui._status_label.text()
    assert mode.currentData() == FLY, "the bar shows it still flying"
    altitude.setValue(0)
    mode.setCurrentIndex(mode.findData(WALK))
    assert MODE_KEY not in eagle


def test_a_prone_flyer_falls(fight):
    ui, eagle, *_ = fight
    _fly(ui, eagle)
    _bar(ui)[2].setValue(30)
    ui._add_condition_to(eagle, "Prone")
    ui._refresh_views()
    assert ALTITUDE_KEY not in eagle and MODE_KEY not in eagle
    line = (
        f"{EAGLE} falls 30 ft. (Prone): 3d6 Bludgeoning damage, and it lands Prone"
        " unless it takes none (Falling)."
    )
    assert line in _logged(ui) and line in ui._status_label.text()
    ui._refresh_views()
    assert _logged(ui).count(line) == 1, "it falls once"


def _cast_fly_on(ui, monkeypatch, caster: dict, target: dict):
    option = next(
        o for _, options in effect_options(caster) for o in options if o.name == "Fly"
    )
    monkeypatch.setattr(
        QDialog,
        "exec",
        lambda dlg: dlg.findChild(QPushButton, "primaryBtn").click() or 0,
    )
    ui._select_character(caster)
    ui._set_targets([target])
    ui._show_custom_condition_dialog(option.name)


def test_the_fly_spell_gives_a_fly_speed_and_falling_follows_its_end(
    fight, monkeypatch
):
    ui, eagle, pirate, rowan = fight
    assert FLY not in speeds(rowan)
    _cast_fly_on(ui, monkeypatch, rowan, rowan)
    assert "Fly" in rowan["conditions"]
    assert speeds(rowan)[FLY] == 60
    ui._select_character(rowan)
    ui._refresh_views()
    _, mode, altitude = _bar(ui)
    assert mode.itemText(mode.findData(FLY)) == "Fly 60 ft. (hover)"
    _fly(ui, rowan)
    altitude.setValue(20)
    ui._add_condition_to(rowan, "Prone")
    ui._refresh_views()
    assert rowan[ALTITUDE_KEY] == 20, "Fly lets it hover"
    ui._remove_condition_from(rowan, "Prone")
    ui._select_character(rowan)
    ui._shortcut_remove_concentration()  # Fly ends
    assert "Fly" not in rowan["conditions"]
    ui._refresh_views()  # as the cards' refresh timer does
    assert ALTITUDE_KEY not in rowan
    line = (
        f"{ROWAN} falls 20 ft. (it can't fly any more): 2d6 Bludgeoning damage,"
        " and it lands Prone unless it takes none (Falling)."
    )
    assert line in _logged(ui)
    ui._undo_last()
    rowan = _named(ui, ROWAN)
    assert rowan[ALTITUDE_KEY] == 20 and "Fly" in rowan["conditions"]
