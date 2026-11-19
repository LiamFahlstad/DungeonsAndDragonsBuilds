"""Targets in an area, in the combat window (Notes/combat-arena-plan.md,
step 10): the Custom Effect dialog's "Select targets in area" brings up the
map with the pick's area read from its text, hovering aims it, a click
makes whoever is in it the targets and opens the dialog again on the same
pick, and a right click, Esc or Cancel goes back to the dialog with the
targets it had and the view the GM had."""

from functools import cache

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTreeWidget,
)

from Combat.Arena.areas import AreaOfEffect, AreaShape
from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.CombatUIQt.arena_mixin import ARENA_PAGE, CARDS_PAGE, area_reading
from Combat.CombatUIQt.effect_options import _spell_named, spell_option
from Combat.CombatUIQt.saves import MONSTER_ACTION, SPELL, EffectOption
from Combat.Combatants import Pirate
from Combat.Monsters.CR_0.monsters import IceMephit
from Combat.Monsters.CR_1.monsters import Tiger
from Model.Content.CombatArea import CombatArea, CombatAreaShape
from tests._combat_ui import make_ui, qapp
from tests._snapshot_helpers import build

PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"
BREATH = "Frost Breath"


@cache
def _player():
    return build(PLAYER_BUILD)


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


@pytest.fixture
def fight(tmp_path):
    """The Ice Mephit the source at E6 (col 4, row 5), the Pirate in front of
    it, the Large Tiger 15 ft. away, Draven far off; the Pirate targeted."""
    ui = make_ui(tmp_path, [IceMephit(), Pirate(), Tiger()], [_player()])
    for char, roll in zip(ui.characters, ("20", "15", "10", "5")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    mephit, pirate, tiger = (_named(ui, n) for n in ("Ice Mephit", "Pirate", "Tiger"))
    draven = next(c for c in ui.characters if c.get("_is_player"))
    mephit[POSITION_KEY] = [4, 5]
    pirate[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 6]  # covers G7, H7, G8, H8
    draven[POSITION_KEY] = [20, 12]
    ui._select_character(mephit)
    ui._set_targets([pirate])
    ui._refresh_views()
    return ui, mephit, pirate, tiger, draven


def _row_named(dlg: QDialog, start: str):
    tree = dlg.findChild(QTreeWidget)
    assert tree is not None
    for i in range(tree.topLevelItemCount()):
        category = tree.topLevelItem(i)
        assert category is not None
        for j in range(category.childCount()):
            item = category.child(j)
            assert item is not None
            option = item.data(0, Qt.ItemDataRole.UserRole)
            if option is not None and option.name.startswith(start):
                return tree, item, option
    raise AssertionError(f"no row {start}")


def _exec_doing(monkeypatch, *actions):
    """Make each dialog exec() run the next of `actions` on it (instead of
    blocking), and return the dialogs opened."""
    opened: list[QDialog] = []
    queue = list(actions)

    def fake_exec(self):
        opened.append(self)
        if queue:
            queue.pop(0)(self)
        return 0

    monkeypatch.setattr(QDialog, "exec", fake_exec)
    return opened


def _pick_breath_then_area(dlg: QDialog):
    tree, item, _ = _row_named(dlg, BREATH)
    tree.setCurrentItem(item)
    dlg.findChild(QPushButton, "areaTargetsBtn").click()


def _aim_with_the_breath(ui, monkeypatch, *then):
    opened = _exec_doing(monkeypatch, _pick_breath_then_area, *then)
    ui._show_custom_condition_dialog()
    return opened


def test_the_button_brings_up_the_map_with_the_picks_area(fight, monkeypatch):
    ui, *_ = fight
    assert ui._view_stack.currentIndex() == CARDS_PAGE
    _aim_with_the_breath(ui, monkeypatch)
    assert ui._view_stack.currentIndex() == ARENA_PAGE
    assert ui._arena_view.aiming_area
    assert not ui._area_bar.isHidden()
    assert ui._area_shape.currentData() is AreaShape.CONE
    assert ui._area_size.value() == 15
    assert "Frost Breath" in ui._area_label.text()
    assert "hover" in ui._area_label.text()
    assert ui.arena_view_on is False, "the view the GM picked isn't changed"


def test_aiming_shows_who_is_in_it_and_a_click_targets_them(fight, monkeypatch):
    ui, mephit, pirate, tiger, draven = fight
    opened = _aim_with_the_breath(ui, monkeypatch)
    view = ui._arena_view
    view.aim_area(Cell(10, 5))  # east: F6, G5-G7, H6
    assert view.area_shown() == {
        Cell(5, 5),
        Cell(6, 4),
        Cell(6, 5),
        Cell(6, 6),
        Cell(7, 5),
    }
    assert "Pirate, Tiger" in ui._area_label.text()
    ui._area_picked(Cell(10, 5))
    assert ui.target_characters == [pirate, tiger]
    assert not view.aiming_area
    assert ui._view_stack.currentIndex() == CARDS_PAGE, "back to the cards"
    assert ui._area_bar.isHidden()

    qapp().processEvents()  # the dialog opens again once the click is over
    assert len(opened) == 2
    again = opened[1]
    assert again.findChild(QLineEdit, "effectName").text().startswith(BREATH)
    assert again.findChild(QPushButton, "primaryBtn").toolTip() == (
        "Apply to 2 targets (Ctrl+Enter)"
    )
    assert ui.selected_character is mephit
    assert draven not in ui.target_characters


def test_nobody_in_the_area_changes_nothing(fight, monkeypatch):
    ui, _, pirate, *_ = fight
    opened = _aim_with_the_breath(ui, monkeypatch)
    ui._arena_view.aim_area(Cell(4, 0))  # north: nobody there
    assert "nobody in it" in ui._area_label.text()
    ui._area_picked(Cell(4, 0))
    assert "Nobody is in that area" in ui._status_label.text()
    assert ui._arena_view.aiming_area, "still aiming"
    assert ui.target_characters == [pirate]
    qapp().processEvents()
    assert len(opened) == 1


@pytest.mark.parametrize("how", ["escape", "cancel", "right click", "G"])
def test_cancelling_goes_back_with_the_targets_it_had(fight, monkeypatch, how):
    ui, _, pirate, *_ = fight
    opened = _aim_with_the_breath(ui, monkeypatch)
    ui._arena_view.aim_area(Cell(10, 5))
    if how == "escape":
        ui._escape_pressed()
    elif how == "cancel":
        ui._area_bar.findChild(QPushButton, "areaCancelBtn").click()
    elif how == "right click":
        view = ui._arena_view
        viewport = view.viewport()
        assert viewport is not None
        QTest.mouseClick(
            viewport,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
            view.cell_center(Cell(8, 5)).toPoint(),
        )
    else:
        ui._toggle_view()
    assert not ui._arena_view.aiming_area
    assert ui._view_stack.currentIndex() == CARDS_PAGE
    assert ui.target_characters == [pirate], "Escape didn't clear them"
    assert ui.selected_character is not None
    qapp().processEvents()
    assert len(opened) == 2, "back in the dialog"


def test_changing_the_shape_in_the_bar_aims_that_instead(fight, monkeypatch):
    ui, _, pirate, tiger, _ = fight
    _aim_with_the_breath(ui, monkeypatch)
    view = ui._arena_view
    view.aim_area(Cell(10, 5))
    ui._area_shape.setCurrentIndex(ui._area_shape.findData(AreaShape.LINE))
    assert not ui._area_width.isHidden()
    assert view.area_shown() == {Cell(c, 5) for c in (5, 6, 7)}
    assert "Pirate" in ui._area_label.text()
    assert "Tiger" not in ui._area_label.text()
    ui._area_size.setValue(30)
    assert Cell(10, 5) in view.area_shown()


def test_an_emanation_shows_without_aiming(fight, monkeypatch):
    ui, _, pirate, *_ = fight

    def custom_then_area(dlg):
        dlg.findChild(QPushButton, "areaTargetsBtn").click()

    _exec_doing(monkeypatch, custom_then_area)
    ui._show_custom_condition_dialog()
    assert ui._area_shape.currentData() is AreaShape.SPHERE, "the default"
    ui._area_shape.setCurrentIndex(ui._area_shape.findData(AreaShape.EMANATION))
    ui._area_size.setValue(5)
    assert Cell(4, 5) not in ui._arena_view.area_shown(), "not the source"
    assert "Pirate" in ui._area_label.text()
    ui._area_picked(Cell(0, 0))
    assert ui.target_characters == [pirate]
    qapp().processEvents()  # the dialog it opens again, while exec is faked


def test_the_button_needs_the_source_on_the_map(fight, monkeypatch):
    ui, mephit, *_ = fight
    del mephit[POSITION_KEY]
    seen: list[bool] = []

    def look(dlg):
        seen.append(dlg.findChild(QPushButton, "areaTargetsBtn").isEnabled())

    _exec_doing(monkeypatch, look)
    ui._show_custom_condition_dialog()
    assert seen == [False]


def test_a_real_click_on_the_map_targets_who_is_in_the_area(fight, monkeypatch):
    ui, _, pirate, tiger, _ = fight
    ui._window.resize(1600, 1000)
    ui._window.show()
    qapp().processEvents()
    opened = _aim_with_the_breath(ui, monkeypatch)
    view = ui._arena_view
    viewport = view.viewport()
    assert viewport is not None
    at = view.cell_center(Cell(10, 5)).toPoint()
    QTest.mouseMove(viewport, at)
    QTest.mouseClick(
        viewport, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, at
    )
    qapp().processEvents()
    assert ui.target_characters == [pirate, tiger]
    assert len(opened) == 2
    assert _named(ui, "Pirate")[POSITION_KEY] == [5, 5], "nobody moved"
    ui._window.hide()


def test_the_bar_remembers_the_last_area_for_a_pick_without_one(fight, monkeypatch):
    ui, *_ = fight
    _aim_with_the_breath(ui, monkeypatch)
    ui._area_size.setValue(30)
    ui._escape_pressed()
    qapp().processEvents()  # the dialog it opens again, while exec is faked

    def custom_then_area(dlg):
        dlg.findChild(QPushButton, "areaTargetsBtn").click()

    _exec_doing(monkeypatch, custom_then_area)
    ui._show_custom_condition_dialog()
    assert ui._area_shape.currentData() is AreaShape.CONE
    assert ui._area_size.value() == 30
    assert isinstance(ui._area_bar.findChild(QComboBox, "areaShape"), QComboBox)
    assert isinstance(ui._area_bar.findChild(QSpinBox, "areaSize"), QSpinBox)


def _spell_pick(name: str) -> EffectOption:
    """The picker's row for the spell `name`, cast by a caster with slots."""
    return spell_option(_spell_named(name), {"name": "Caster"})


def test_a_spells_area_and_range_are_its_classs():
    """SpellRules.area, and the range of the spell (Range), or the point
    its area may be centred on."""
    area, range_ft = area_reading(_spell_pick("Fireball"))
    assert area == AreaOfEffect(AreaShape.SPHERE, 20)
    assert range_ft == 150
    assert area_reading(_spell_pick("Burning Hands")) == (
        AreaOfEffect(AreaShape.CONE, 15),
        None,
    )
    lure = area_reading(_spell_pick("Lightning Lure"))[0]
    assert lure == AreaOfEffect(AreaShape.SPHERE, 15, 5, True)
    assert area_reading(_spell_pick("Investiture of Wind")) == (
        AreaOfEffect(AreaShape.CUBE, 15),
        60,
    ), "a Self range, but the Cube goes at a point within 60 feet"
    assert area_reading(None) == (None, None)


def test_the_bar_says_how_far_the_point_is_against_the_range(fight, monkeypatch):
    """A monster's Sphere "centered on a point within 30 feet": aimed
    within it, the bar says how far; past it, it warns, and a click still
    targets, saying so (as a move past the Speed does)."""
    ui, mephit, pirate, tiger, draven = fight
    burst = EffectOption(
        name="Radiant Burst",
        kind=MONSTER_ACTION,
        tooltip=(
            "Dexterity Saving Throw: DC 10, each creature in a 10-foot-radius"
            " Sphere centered on a point within 30 feet."
        ),
        area=CombatArea(CombatAreaShape.SPHERE, 10, point_within_ft=30),
    )
    assert ui._start_area_targeting(burst)
    view = ui._arena_view
    view.aim_area(Cell(6, 5))  # 10 ft. from the mephit
    assert "Aimed 10 ft. away, range 30 ft." in ui._area_label.text()
    view.aim_area(Cell(20, 12))  # on Draven: 23 steps
    assert "past its 30 ft. range!" in ui._area_label.text()
    monkeypatch.setattr(QDialog, "exec", lambda self: 0)
    ui._area_picked(Cell(20, 12))
    assert ui.target_characters == [draven]
    assert "past its 30 ft. range" in ui._status_label.text()
    qapp().processEvents()


def test_an_area_from_the_source_has_no_range_to_check(fight, monkeypatch):
    ui, *_ = fight
    _aim_with_the_breath(ui, monkeypatch)
    ui._arena_view.aim_area(Cell(20, 5))
    assert "Aimed" not in ui._area_label.text()
