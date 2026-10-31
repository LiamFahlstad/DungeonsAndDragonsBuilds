"""Casting an area spell (target "area", e.g. Faerie Fire's 20-foot cube) in
the combat UI needs only a caster: the targets, if any are selected, are the
creatures caught in the area."""

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Model.Content.Feature import FeatureTarget
from tests._combat_ui import make_ui


@pytest.fixture
def warnings(monkeypatch):
    """Record warning boxes instead of blocking on them; fail any other
    modal dialog."""
    shown = []

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: shown.append(args))
    return shown


@pytest.fixture
def fight(tmp_path):
    """A Pirate (initiative 15) and a Tiger (10) in round 1, the Pirate's
    turn, the Pirate selected and no target selected."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(pirate)
    return ui, pirate, tiger


def test_faerie_fire_is_an_area_spell():
    assert SpellFactory.create("Faerie Fire").target == FeatureTarget.AREA


def test_an_area_spell_casts_with_no_target_selected(fight, warnings):
    ui, pirate, tiger = fight
    assert not ui.target_characters

    ui._apply_cast_spell(SpellFactory.create("Faerie Fire"))

    assert warnings == []
    assert pirate["stats"]["spells_cast"] == 1
    assert "Concentrating" in pirate["conditions"]
    assert [s["name"] for s in pirate["active_spells"]] == ["Faerie Fire"]
    # Nobody was marked as caught in the area, so nobody gets the badge.
    assert "Faerie Fire" not in pirate["conditions"]
    assert "Faerie Fire" not in tiger["conditions"]


def test_an_area_spell_marks_the_selected_targets(fight, warnings):
    ui, pirate, tiger = fight
    ui._select_target_character(tiger)

    ui._apply_cast_spell(SpellFactory.create("Faerie Fire"))

    assert warnings == []
    assert "Faerie Fire" in tiger["conditions"]
    assert "Faerie Fire" not in pirate["conditions"]


def test_a_creature_spell_still_needs_a_target(fight, warnings):
    ui, pirate, _ = fight
    spell = SpellFactory.create("Hold Person")
    assert spell.target not in (None, FeatureTarget.SELF, FeatureTarget.AREA)

    ui._apply_cast_spell(spell)

    assert "needs a target" in ui._status_label.text()
    assert "Concentrating" not in pirate["conditions"]
