"""Areas that stay on the battle map, in the combat window (Notes/
combat-arena-plan.md, step 11): the area bar's "Keep on the map" and
colour, the Custom Effect opened again with "Keep the area on the map", the
area held by an active spell of the source's (ending with concentration,
its time, or undo), an Emanation following its caster, and the reminders
for whoever walks into one or starts a turn in one."""

from functools import cache

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
)

from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import AREA_KEY, lasting_areas
from Combat.CombatUIQt.arena_mixin import ARENA_PAGE, area_lasts
from Combat.CombatUIQt.effect_options import _spell_named
from Combat.CombatUIQt.saves import MONSTER_ACTION, SPELL, EffectOption
from Combat.Combatants import Pirate
from Combat.EncounterLogs import TURN_PREFIX
from Combat.Monsters.CR_0.monsters import IceMephit
from Combat.Monsters.CR_1.monsters import Tiger
from tests._combat_ui import make_ui, qapp
from tests._snapshot_helpers import build

PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"
CONCENTRATING = "Concentrating"
BLUE = "#3498db"


@cache
def _player():
    return build(PLAYER_BUILD)


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


@pytest.fixture
def fight(tmp_path):
    """The Ice Mephit the source at E6 (col 4, row 5), the Pirate beside it,
    the Large Tiger 15 ft. away, Draven far off; the Pirate targeted."""
    ui = make_ui(tmp_path, [IceMephit(), Pirate(), Tiger()], [_player()])
    for char, roll in zip(ui.characters, ("20", "15", "10", "5")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    mephit, pirate, tiger = (_named(ui, n) for n in ("Ice Mephit", "Pirate", "Tiger"))
    draven = next(c for c in ui.characters if c.get("_is_player"))
    mephit[POSITION_KEY] = [4, 5]
    pirate[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 6]
    draven[POSITION_KEY] = [20, 12]
    ui._select_character(mephit)
    ui._set_targets([pirate])
    ui._refresh_views()
    return ui, mephit, pirate, tiger, draven


def _spell(name: str) -> EffectOption:
    spell = _spell_named(name)
    return EffectOption(
        name=name,
        kind=SPELL,
        tooltip=spell.description,
        concentration=spell.is_concentration,
    )


def _apply_keeping(concentrate: bool, seen: dict):
    """What the dialog opened again does: notes what it offers, names the
    effect (the mephit's picker doesn't list these spells), ticks or leaves
    "Source concentrates on it", and applies."""

    def act(dlg: QDialog):
        keep = dlg.findChild(QCheckBox, "keepArea")
        seen["keep shown"] = not keep.isHidden()
        seen["keep"] = keep.isChecked()
        seen["keep text"] = keep.text()
        seen["apply tip"] = dlg.findChild(QPushButton, "primaryBtn").toolTip()
        name = dlg.findChild(QLineEdit, "effectName")
        if not name.text():
            name.setText(seen["name"])
        dlg.findChild(QCheckBox, "sourceConcentrates").setChecked(concentrate)
        dlg.findChild(QPushButton, "primaryBtn").click()
        seen["problem"] = dlg.findChild(QLabel, "statusLabel").text()

    return act


def _put_down(ui, monkeypatch, name: str, cell: Cell, concentrate: bool) -> dict:
    """Aim spell `name`'s area at `cell`, click there, and apply the dialog
    that opens again; what the dialog showed."""
    seen: dict = {"name": name}
    monkeypatch.setattr(
        QDialog, "exec", lambda dlg: _apply_keeping(concentrate, seen)(dlg) or 0
    )
    assert ui._start_area_targeting(_spell(name))
    ui._arena_view.aim_area(cell)
    seen["bar"] = ui._area_label.text()
    ui._area_picked(cell)
    qapp().processEvents()  # the dialog opens again once the click is over
    return seen


def _show_map(ui):
    ui._toggle_view()
    assert ui._view_stack.currentIndex() == ARENA_PAGE
    qapp().processEvents()


def _without_turn(text: str) -> str:
    match = TURN_PREFIX.match(text)
    return match.group(2) if match else text


def _logged(ui) -> list[str]:
    """Every line in the encounter log, without whose turn it was in."""
    data = ui._read_log()
    return [
        _without_turn(str(event["text"]))
        for key, events in data.items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def _drawn(ui) -> list[str]:
    qapp().processEvents()  # the views' refresh timer
    return [area.name for area in ui._arena_view.lasting]


def test_a_spell_that_lasts_is_kept_by_default_and_an_instant_one_isnt():
    assert area_lasts(_spell("Moonbeam"))
    assert area_lasts(_spell("Grease")), "1 minute, no concentration"
    assert not area_lasts(_spell("Fireball"))
    breath = EffectOption(name="Frost Breath", kind=MONSTER_ACTION)
    assert not area_lasts(breath)
    assert area_lasts(EffectOption(name="Fog", kind=MONSTER_ACTION, concentration=True))
    assert not area_lasts(None)


def test_moonbeam_put_on_empty_ground_lasts_while_its_caster_concentrates(
    fight, monkeypatch
):
    ui, mephit, pirate, *_ = fight
    seen = _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    assert "Click to put it there" in seen["bar"]
    assert seen["keep shown"] and seen["keep"]
    assert seen["keep text"] == "Keep the 5-foot-radius Cylinder on the map"
    assert "no targets" in seen["apply tip"]
    assert ui.target_characters == [], "nobody was in it"
    assert CONCENTRATING in mephit["conditions"]
    (entry,) = mephit["active_spells"]
    assert entry["name"] == "Moonbeam" and entry["concentration"]
    assert entry[AREA_KEY]["aim"] == [12, 2]
    assert "Ice Mephit's Moonbeam stays on the map at M3." in _logged(ui)
    _show_map(ui)
    assert _drawn(ui) == ["Moonbeam"]
    (area,) = ui._arena_view.lasting
    assert area.concentration
    assert Cell(12, 2) in area.cells and Cell(12, 1) in area.cells

    ui._shortcut_remove_concentration()  # Ctrl+C: concentration ends
    assert mephit.get("active_spells") == []
    assert _drawn(ui) == [], "the beam goes with the concentration"
    ui._undo_last()
    mephit = _named(ui, "Ice Mephit")
    assert [e["name"] for e in mephit["active_spells"]] == ["Moonbeam"]
    assert _drawn(ui) == ["Moonbeam"], "and undo puts it back"


def test_a_new_concentration_ends_the_area_of_the_old_one(fight, monkeypatch):
    ui, mephit, *_ = fight
    _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    assert lasting_areas(ui.characters, ui.arena_settings)
    ui._start_concentration(mephit, "Hold Person")
    assert lasting_areas(ui.characters, ui.arena_settings) == []


def test_an_area_without_concentration_lasts_its_spells_time(fight, monkeypatch):
    """Grease (1 minute): put on the Pirate and the Tiger, held by an active
    spell of the mephit's that holds nothing else, and gone after 10
    rounds; the mephit doesn't concentrate."""
    ui, mephit, pirate, tiger, _ = fight
    _put_down(ui, monkeypatch, "Grease", Cell(5, 5), concentrate=False)
    assert ui.target_characters == [pirate, tiger]
    assert CONCENTRATING not in mephit["conditions"]
    (entry,) = mephit["active_spells"]
    assert entry["time_left"] == 60 and not entry["concentration"]
    assert entry["applied"] == []
    assert [a.name for a in lasting_areas(ui.characters, ui.arena_settings)] == [
        "Grease"
    ]
    turn = ui._current_turn_group()  # whose turn it was put down on
    for _ in range(9):
        ui._tick_active_spells(turn, new_round=False)
    assert lasting_areas(ui.characters, ui.arena_settings)
    ui._tick_active_spells(turn, new_round=False)
    assert lasting_areas(ui.characters, ui.arena_settings) == []


def test_without_keep_an_empty_area_still_changes_nothing(fight, monkeypatch):
    ui, _, pirate, *_ = fight
    opened: list = []
    monkeypatch.setattr(QDialog, "exec", lambda dlg: opened.append(dlg) or 0)
    assert ui._start_area_targeting(_spell("Moonbeam"))
    assert ui._area_keep.isChecked()
    ui._area_keep.setChecked(False)
    ui._arena_view.aim_area(Cell(12, 2))
    ui._area_picked(Cell(12, 2))
    assert "Nobody is in that area" in ui._status_label.text()
    assert ui.target_characters == [pirate]
    qapp().processEvents()
    assert opened == []


def test_unticking_keep_in_the_dialog_applies_without_the_area(fight, monkeypatch):
    ui, mephit, pirate, *_ = fight

    def untick(dlg):
        dlg.findChild(QCheckBox, "keepArea").setChecked(False)
        dlg.findChild(QLineEdit, "effectName").setText("Moonbeam")
        dlg.findChild(QPushButton, "primaryBtn").click()

    monkeypatch.setattr(QDialog, "exec", lambda dlg: untick(dlg) or 0)
    assert ui._start_area_targeting(_spell("Moonbeam"))
    ui._area_picked(Cell(5, 5))  # on the Pirate
    qapp().processEvents()
    assert lasting_areas(ui.characters, ui.arena_settings) == []


def test_no_targets_and_no_area_to_keep_is_refused(fight, monkeypatch):
    ui, mephit, *_ = fight
    seen: dict = {}

    def untick(dlg):
        dlg.findChild(QCheckBox, "keepArea").setChecked(False)
        dlg.findChild(QPushButton, "primaryBtn").click()
        seen["problem"] = dlg.findChild(QLabel, "statusLabel").text()

    monkeypatch.setattr(QDialog, "exec", lambda dlg: untick(dlg) or 0)
    assert ui._start_area_targeting(_spell("Moonbeam"))
    ui._area_picked(Cell(12, 2))
    qapp().processEvents()
    assert seen["problem"].startswith("Target missing")
    assert not mephit.get("active_spells")


def test_the_bars_colour_shades_the_aim_and_the_area_kept(fight, monkeypatch):
    ui, *_ = fight
    monkeypatch.setattr(QDialog, "exec", lambda dlg: 0)
    assert ui._start_area_targeting(_spell("Moonbeam"))
    combo = ui._area_color
    combo.setCurrentIndex(combo.findData(BLUE))
    assert ui._arena_view.area_color == BLUE
    ui._cancel_area_targeting()
    qapp().processEvents()
    _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    (area,) = lasting_areas(ui.characters, ui.arena_settings)
    assert area.color == BLUE, "the next area starts with the last colour"


def test_other_asks_for_any_colour(fight, monkeypatch):
    ui, *_ = fight
    assert ui._start_area_targeting(_spell("Moonbeam"))
    combo = ui._area_color
    monkeypatch.setattr(
        QColorDialog, "getColor", staticmethod(lambda *a, **k: QColor("#123456"))
    )
    combo.setCurrentIndex(combo.findData("other"))
    assert combo.currentData() == "#123456"
    assert combo.itemText(combo.count() - 1) == "Other..."
    assert ui._arena_view.area_color == "#123456"
    monkeypatch.setattr(
        QColorDialog, "getColor", staticmethod(lambda *a, **k: QColor())
    )
    combo.setCurrentIndex(combo.findData("other"))
    assert combo.currentData() == "#123456", "cancelled: the colour it had"


def test_spirit_guardians_follows_its_caster_and_says_who_it_reaches(
    fight, monkeypatch
):
    ui, mephit, pirate, tiger, draven = fight
    _put_down(ui, monkeypatch, "Spirit Guardians", Cell(0, 0), concentrate=True)
    assert ui.target_characters == [pirate, tiger]
    (entry,) = mephit["active_spells"]
    assert entry[AREA_KEY]["follows"]
    ui._move_combatant(mephit, Cell(17, 12))  # 15 ft. from Draven
    (area,) = lasting_areas(ui.characters, ui.arena_settings)
    assert Cell(18, 12) in area.cells and Cell(6, 5) not in area.cells
    line = f"{draven['name']} enters Ice Mephit's Spirit Guardians."
    assert line in ui._status_label.text()
    assert line in _logged(ui)


def test_walking_into_an_area_and_starting_a_turn_in_it_are_logged(fight, monkeypatch):
    """Walking in says so; a turn starting in it is a GM-only log line.
    Moonbeam's buttons (on entering, and as the turn ends there: step 24)
    are tests/test_combat_ui_arena_area_prompts.py's."""
    ui, mephit, pirate, *_ = fight
    _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    ui._move_combatant(pirate, Cell(12, 3))
    assert "Pirate enters Ice Mephit's Moonbeam." in ui._status_label.text()
    line = "Pirate starts its turn in Ice Mephit's Moonbeam."
    while ui._current_turn_group()[0] is not pirate:
        ui._advance_turn()
    assert line in _logged(ui)
    assert line not in ui._turn_reminders, "Moonbeam acts as a turn ends"
    ui._advance_turn()  # the Tiger's: not in it
    assert not any("starts its turn in" in r for r in ui._turn_reminders)


def test_hovering_an_area_names_it(fight, monkeypatch):
    ui, *_ = fight
    _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    assert ui._arena_distance(Cell(12, 2)) == "55 ft. · Moonbeam"
    assert ui._arena_distance(Cell(14, 2)) == "65 ft."


# ── Selecting a kept area (step 12) ──────────────────────────────────────────


def _moonbeam_on_the_map(ui, monkeypatch) -> dict:
    """Moonbeam put on M3 by the concentrating mephit, the map shown; its
    active spell."""
    _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    _show_map(ui)
    return _named(ui, "Ice Mephit")["active_spells"][0]


def _panel_shown(ui) -> bool:
    return not ui._area_panel.isHidden()


def test_a_click_on_a_kept_area_selects_it_and_shows_what_it_is(fight, monkeypatch):
    ui, mephit, *_ = fight
    entry = _moonbeam_on_the_map(ui, monkeypatch)
    view = ui._arena_view
    assert not _panel_shown(ui)
    viewport = view.viewport()
    ui._window.resize(1600, 1000)
    ui._window.show()
    qapp().processEvents()
    at = view.cell_center(Cell(12, 1)).toPoint()
    QTest.mouseClick(
        viewport, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, at
    )
    qapp().processEvents()
    assert ui._selected_area == entry[AREA_KEY]["key"]
    assert _panel_shown(ui)
    title = ui._area_panel_title.text()
    assert "Ice Mephit's Moonbeam" in title
    assert "5-foot-radius Cylinder at M3" in title
    assert "Concentration" in title and "left" in title
    assert "silvery beam" in ui._area_panel_text.toPlainText()
    (row,) = view.lasting
    assert row.selected
    assert ui.selected_character is mephit, "an area is never the source"
    ui._window.hide()


def test_a_click_elsewhere_close_or_esc_deselects(fight, monkeypatch):
    ui, *_ = fight
    _moonbeam_on_the_map(ui, monkeypatch)
    view = ui._arena_view
    for how in ("empty cell", "close", "esc"):
        view.click_cell(Cell(12, 2))
        assert _panel_shown(ui)
        if how == "empty cell":
            view.click_cell(Cell(20, 2))
        elif how == "close":
            ui._area_panel.findChild(QPushButton, "areaPanelCloseBtn").click()
        else:
            ui._escape_pressed()
        assert ui._selected_area is None, how
        assert not _panel_shown(ui)
    assert ui.selected_character is not None, "Esc deselected the area only"


def test_clicks_on_overlapping_areas_go_from_one_to_the_next(fight, monkeypatch):
    ui, *_ = fight
    # The mephit's action is spent on Moonbeam: Grease anyway.
    monkeypatch.setattr(
        QMessageBox,
        "question",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes),
    )
    _put_down(ui, monkeypatch, "Moonbeam", Cell(12, 2), concentrate=True)
    _put_down(ui, monkeypatch, "Grease", Cell(12, 2), concentrate=False)
    _show_map(ui)
    view = ui._arena_view
    names = []
    for _ in range(3):
        view.click_cell(Cell(12, 2))
        caster, entry = ui._selected_lasting()
        names.append(entry["name"])
    assert names == ["Moonbeam", "Grease", "Moonbeam"]
    view.click_cell(Cell(12, 1))  # Moonbeam's alone
    assert ui._selected_lasting()[1]["name"] == "Moonbeam"


def test_the_panel_changes_the_areas_colour_as_one_undo_step(fight, monkeypatch):
    ui, *_ = fight
    entry = _moonbeam_on_the_map(ui, monkeypatch)
    ui._arena_view.click_cell(Cell(12, 2))
    combo = ui._area_panel_color
    assert combo.currentData() == "#e67e22"
    combo.setCurrentIndex(combo.findData(BLUE))
    assert entry[AREA_KEY]["color"] == BLUE
    (row,) = ui._arena_view.lasting
    assert row.color == BLUE
    monkeypatch.setattr(
        QColorDialog, "getColor", staticmethod(lambda *a, **k: QColor("#123456"))
    )
    combo.setCurrentIndex(combo.findData("other"))
    assert entry[AREA_KEY]["color"] == "#123456"
    ui._undo_last()
    qapp().processEvents()
    caster, entry = ui._selected_lasting()
    assert entry[AREA_KEY]["color"] == BLUE, "undo goes one colour back"
    assert ui._area_panel_color.currentData() == BLUE


def test_target_whos_in_it(fight, monkeypatch):
    ui, mephit, pirate, *_ = fight
    _moonbeam_on_the_map(ui, monkeypatch)
    ui._arena_view.click_cell(Cell(12, 2))
    button = ui._area_panel.findChild(QPushButton, "areaPanelTargetBtn")
    button.click()
    assert "Nobody is in Ice Mephit's Moonbeam" in ui._status_label.text()
    ui._move_combatant(pirate, Cell(12, 3))
    button.click()
    assert ui.target_characters == [pirate]
    assert ui.selected_character is mephit


def test_end_spell_ends_it_and_its_concentration_and_undo_brings_it_back(
    fight, monkeypatch
):
    ui, mephit, *_ = fight
    _moonbeam_on_the_map(ui, monkeypatch)
    ui._arena_view.click_cell(Cell(12, 2))
    ui._area_panel.findChild(QPushButton, "areaPanelEndBtn").click()
    assert mephit["active_spells"] == []
    assert CONCENTRATING not in mephit["conditions"]
    assert _drawn(ui) == []
    assert not _panel_shown(ui)
    ui._undo_last()
    assert _drawn(ui) == ["Moonbeam"]
    assert CONCENTRATING in _named(ui, "Ice Mephit")["conditions"]


def test_the_panel_goes_when_its_area_ends(fight, monkeypatch):
    ui, *_ = fight
    _moonbeam_on_the_map(ui, monkeypatch)
    ui._arena_view.click_cell(Cell(12, 2))
    ui._shortcut_remove_concentration()
    _drawn(ui)
    assert ui._selected_area is None
    assert not _panel_shown(ui)
