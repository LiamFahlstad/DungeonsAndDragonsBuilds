"""Picking the source and targets on the combat UI's cards (WindowMixin). A
left click picks the one source, whatever keys are held. A right click picks
targets the way a Windows list picks items: Ctrl + right click adds or removes
one card, Shift + right click picks every card from the anchor (the last card
right-clicked without Shift) to the clicked one, and Ctrl + Shift + right click
adds that range."""

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent

from Combat.Combatants import Pirate, Tiger
from tests._combat_ui import make_ui

LEFT = Qt.MouseButton.LeftButton
RIGHT = Qt.MouseButton.RightButton


@pytest.fixture
def fight(tmp_path):
    """Pirate, Tiger, Pirate, Tiger (initiative 20, 15, 10, 5) in round 1,
    nothing selected."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), Pirate(), Tiger()])
    for char, initiative in zip(ui.characters, ("20", "15", "10", "5")):
        ui._initiative_inputs[id(char)].setText(initiative)
    ui._start_combat()
    ui._clear_selection()
    return ui


def _click(ui, char, button: Qt.MouseButton, ctrl=False, shift=False):
    """Press the mouse on char's card, the way Qt delivers a real click."""
    modifiers = Qt.KeyboardModifier.NoModifier
    if ctrl:
        modifiers |= Qt.KeyboardModifier.ControlModifier
    if shift:
        modifiers |= Qt.KeyboardModifier.ShiftModifier
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(5, 5),
        QPointF(5, 5),
        button,
        button,
        modifiers,
    )
    ui._card_widgets[id(char)].mousePressEvent(event)


@pytest.mark.parametrize("ctrl, shift", [(False, False), (True, False), (False, True)])
def test_left_click_always_picks_one_source(fight, ctrl, shift):
    ui = fight
    a, _, c, _ = ui.characters
    _click(ui, a, LEFT)
    _click(ui, c, LEFT, ctrl=ctrl, shift=shift)

    assert ui.selected_character is c
    assert ui.selected_label.text() == "Source: Pirate"
    assert [ui._card_state_flags(x)[0] for x in ui.characters] == [
        False,
        False,
        True,
        False,
    ], "only the one source's card is outlined"
    assert ui.target_characters == [], "a left click never picks a target"


def test_a_plain_right_click_picks_only_that_target(fight):
    ui = fight
    a, b, _, _ = ui.characters
    _click(ui, a, RIGHT)
    _click(ui, b, RIGHT)
    assert ui.target_characters == [b]
    assert ui.target_label.text() == "Target: Tiger"


def test_ctrl_right_click_adds_and_removes_one_target(fight):
    ui = fight
    a, b, c, d = ui.characters
    _click(ui, a, RIGHT)
    _click(ui, c, RIGHT, ctrl=True)
    _click(ui, d, RIGHT, ctrl=True)
    assert ui.target_characters == [a, c, d]
    assert ui.target_label.text() == "Targets: Pirate, Pirate, Tiger"
    assert ui.selected_character is None, "a right click never picks the source"

    _click(ui, c, RIGHT, ctrl=True)
    assert ui.target_characters == [a, d]


def test_shift_right_click_picks_the_range_from_the_anchor(fight):
    ui = fight
    a, b, c, d = ui.characters
    _click(ui, a, RIGHT)
    _click(ui, c, RIGHT, shift=True)
    assert ui.target_characters == [a, b, c]

    # The anchor stays put, so a second Shift + right click re-picks from it.
    _click(ui, b, RIGHT, shift=True)
    assert ui.target_characters == [a, b]


def test_shift_right_click_picks_a_range_backwards(fight):
    ui = fight
    a, b, c, d = ui.characters
    _click(ui, d, RIGHT)
    _click(ui, b, RIGHT, shift=True)
    assert ui.target_characters == [d, c, b]


def test_shift_right_click_replaces_ctrl_picks(fight):
    ui = fight
    a, b, c, d = ui.characters
    _click(ui, a, RIGHT)
    _click(ui, d, RIGHT, ctrl=True)  # Ctrl + right click moves the anchor to d
    _click(ui, c, RIGHT, shift=True)
    assert ui.target_characters == [d, c]


def test_ctrl_shift_right_click_adds_the_range(fight):
    ui = fight
    a, b, c, d = ui.characters
    _click(ui, b, RIGHT)
    _click(ui, d, RIGHT, shift=True)
    assert ui.target_characters == [b, c, d]

    # Adds the range b..a; the range goes last so the clicked card ends it.
    _click(ui, a, RIGHT, ctrl=True, shift=True)
    assert ui.target_characters == [c, d, b, a]


def test_shift_right_click_without_an_anchor_is_a_plain_click(fight):
    ui = fight
    _, b, _, _ = ui.characters
    _click(ui, b, RIGHT, shift=True)
    assert ui.target_characters == [b]


def test_picking_the_source_leaves_the_targets_and_anchor_alone(fight):
    ui = fight
    a, b, c, d = ui.characters
    _click(ui, d, RIGHT)
    _click(ui, a, LEFT)
    _click(ui, b, RIGHT, shift=True)
    assert ui.selected_character is a
    assert ui.target_characters == [d, c, b]


def test_undo_drops_a_removed_anchor(fight):
    ui = fight
    a, b, _, _ = ui.characters
    ui._add_ad_hoc_combatant("Wooden Door", hp=15, ac=12)
    door = ui.characters[-1]
    _click(ui, a, RIGHT)
    _click(ui, door, RIGHT, ctrl=True)

    ui._undo_last()

    assert ui.target_characters == [a]
    # The anchor (the door) is gone, so Shift + right click is a plain click.
    _click(ui, b, RIGHT, shift=True)
    assert ui.target_characters == [b]
