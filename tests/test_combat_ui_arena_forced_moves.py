"""Moves on the battle map that aren't walks (Notes/combat-arena-plan.md,
step 17). Rules Glossary, Teleportation: it "doesn't expend movement unless
a rule tells you otherwise, and teleportation never provokes Opportunity
Attacks"; "if the destination space ... is occupied by another creature or
blocked by a solid obstacle, you instead appear in the nearest unoccupied
space of your choice". A push (a Shove, Thunderwave) isn't the creature's
own movement either: Opportunity Attacks come when a creature leaves a reach
"using its action, its Bonus Action, its Reaction, or one of its speeds".

Shift held as a token is dropped teleports it, Alt pushes it; a plain drop
walks, as before."""

import pytest
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtTest import QTest

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Arena.arena import MOVED_KEY, POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import WALL, MapObject, Spot
from Combat.CombatUIQt.arena_view import MoveKind, move_kind
from Combat.Effects.triggers import OpportunityAttack
from Combat.LogFiles import read_json
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerLog import is_round_key
from tests._combat_ui import make_ui


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path):
    """Edmund (initiative 15, Speed 30 ft.) at F6 next to a Large Tiger (10)
    at G6-H7, Edmund's turn: walking to C6 leaves the Tiger's reach."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    player[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 5]
    return ui, player, tiger


def _events(ui) -> list[dict]:
    data = read_json(ui.log_file)
    keys = sorted((k for k in data if is_round_key(k)), key=lambda k: int(k[6:]))
    return [e for k in keys for e in data[k]]


def _texts(ui) -> list[str]:
    return [e["text"] for e in _events(ui)]


def _opportunity_prompts(ui) -> list[OpportunityAttack]:
    return [p for p in ui._hit_prompts if isinstance(p, OpportunityAttack)]


def _at(char) -> Cell:
    return Cell.of(char[POSITION_KEY])


def test_a_walk_out_of_reach_still_spends_movement_and_offers_the_attack(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(2, 5))
    assert player[MOVED_KEY] == 15
    [prompt] = _opportunity_prompts(ui)
    assert prompt.attacker is tiger
    assert any("Edmund moves from F6 to C6 (15 ft.;" in t for t in _texts(ui))
    assert any("leaves Tiger's reach" in t for t in _texts(ui))


@pytest.mark.parametrize(
    "kind, line",
    [
        (
            MoveKind.TELEPORT,
            "Edmund teleports from F6 to C6 (15 ft.; no movement spent).",
        ),
        (MoveKind.PUSH, "Edmund is pushed from F6 to C6 (15 ft.; no movement spent)."),
    ],
)
def test_a_teleport_or_a_push_spends_no_movement_and_provokes_nothing(
    tmp_path, kind, line
):
    ui, player, tiger = _fight(tmp_path)
    player[MOVED_KEY] = 10  # walked before, on this turn
    ui._move_combatant(player, Cell(2, 5), kind)
    assert _at(player) == Cell(2, 5)
    assert player[MOVED_KEY] == 10, "no movement spent"
    assert _opportunity_prompts(ui) == []
    texts = _texts(ui)
    assert not any("reach" in t for t in texts), "no Opportunity Attack reminded of"
    [logged] = [e for e in _events(ui) if e["text"].endswith(line)]
    assert not logged.get("public"), "GM-only"
    assert "action" not in logged, "nothing replays from it"
    assert not any(" moves from " in t for t in texts), "not the walk's line"
    assert line in ui._status_label.text()


def test_a_long_teleport_isnt_warned_about_the_speed(tmp_path):
    """Misty Step's 30 feet after a full walk: nothing is past the Speed."""
    ui, player, tiger = _fight(tmp_path)
    player[MOVED_KEY] = 30
    ui._move_combatant(player, Cell(5, 11), MoveKind.TELEPORT)
    assert player[MOVED_KEY] == 30
    assert "Speed" not in ui._status_label.text()


def test_a_teleport_or_a_push_is_one_undo_step(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    for kind in (MoveKind.TELEPORT, MoveKind.PUSH):
        ui._move_combatant(player, Cell(2, 5), kind)
        ui._undo_last()
        assert _at(player) == Cell(5, 5)
        assert MOVED_KEY not in player or player[MOVED_KEY] == 0
        assert not any("from F6 to C6" in t for t in _texts(ui))
    # And a walk afterwards still provokes: the forced moves left nothing.
    ui._move_combatant(player, Cell(2, 5))
    assert len(_opportunity_prompts(ui)) == 1


@pytest.mark.parametrize("kind", [MoveKind.TELEPORT, MoveKind.PUSH])
def test_a_teleport_or_a_push_cant_end_on_someone_or_a_wall(tmp_path, kind):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(7, 6), kind)  # in the Tiger's space
    assert _at(player) == Cell(5, 5)
    assert "someone else's space" in ui._status_label.text()
    ui.arena_settings.terrain.put(Cell(2, 5), Spot(ground=WALL))
    ui._move_combatant(player, Cell(2, 5), kind)
    assert _at(player) == Cell(5, 5)
    assert "a wall" in ui._status_label.text()
    assert not ui.history, "nothing to undo"
    assert not any("from F6" in t for t in _texts(ui))


def test_a_refused_teleport_says_to_pick_the_nearest_unoccupied_space(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(7, 6), MoveKind.TELEPORT)
    status = ui._status_label.text()
    assert "Edmund can't teleport there" in status
    assert "nearest unoccupied space of your choice" in status


def test_a_teleport_onto_a_hazard_is_reminded_of(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui.arena_settings.terrain.put(
        Cell(2, 5), Spot(thing=MapObject("Campfire", hazard=True))
    )
    ui._move_combatant(player, Cell(2, 5), MoveKind.TELEPORT)
    line = "Edmund enters a hazard: Campfire at C6."
    assert line in ui._status_label.text()
    assert any(t.endswith(line) for t in _texts(ui))


def test_the_keys_held_pick_the_move():
    none = Qt.KeyboardModifier.NoModifier
    shift = Qt.KeyboardModifier.ShiftModifier
    alt = Qt.KeyboardModifier.AltModifier
    assert move_kind(none) is MoveKind.WALK
    assert move_kind(shift) is MoveKind.TELEPORT
    assert move_kind(alt) is MoveKind.PUSH
    assert move_kind(shift | alt) is MoveKind.TELEPORT
    assert move_kind(Qt.KeyboardModifier.ControlModifier) is MoveKind.WALK


def _shown(ui):
    ui._toggle_view()
    view = ui._arena_view
    view.resize(1000, 700)
    view.show()
    ui._refresh_views()
    viewport = view.viewport()
    assert viewport is not None
    return view, viewport


def test_shift_held_as_the_mouse_drops_a_token_teleports_it(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    view, viewport = _shown(ui)
    begin = view.cell_center(Cell(5, 5)).toPoint()
    left, plain = Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
    QTest.mousePress(viewport, left, plain, begin)
    QTest.mouseMove(viewport, begin + QPoint(10, 0))
    # Where the cell is once picked up: the hidden test window's view
    # recentres the map as it redraws.
    end = view.cell_center(Cell(2, 5)).toPoint()
    QTest.mouseMove(viewport, end)
    QTest.mouseRelease(viewport, left, Qt.KeyboardModifier.ShiftModifier, end)
    assert _at(player) == Cell(2, 5)
    assert player.get(MOVED_KEY, 0) == 0
    assert _opportunity_prompts(ui) == []
    assert any("Edmund teleports from F6 to C6" in t for t in _texts(ui))
    view.hide()


def test_alt_held_as_the_cell_is_clicked_pushes_the_picked_up_token(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    view, viewport = _shown(ui)
    left, plain = Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier
    token = view.cell_center(Cell(5, 5)).toPoint()
    QTest.mouseClick(viewport, left, plain, token)
    assert view.picked == player["name"]
    cell = view.cell_center(Cell(2, 5)).toPoint()
    QTest.mouseClick(viewport, left, Qt.KeyboardModifier.AltModifier, cell)
    assert _at(player) == Cell(2, 5)
    assert player.get(MOVED_KEY, 0) == 0
    assert _opportunity_prompts(ui) == []
    assert any("Edmund is pushed from F6 to C6" in t for t in _texts(ui))
    view.hide()
