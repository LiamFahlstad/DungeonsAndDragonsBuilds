"""Running out in the combat UI (Combat/CombatUIQt/resources.py): using
something the source has none left of asks the GM first, instead of
refusing. Yes uses it anyway; No leaves everything as it was, with no undo
step. The other resources (slots, feature uses, recharges, legendary
actions, Wild Shape, summons) are tested beside the rest of their own
behavior; this file covers the action economy and the question itself."""

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.resources import action_lack
from tests._combat_ui import answer_out_of_resources, make_ui


@pytest.fixture(autouse=True)
def _no_other_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (initiative 15) and a Tiger (10) in round 1, the Pirate's
    turn, the Pirate the source."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _uses_logged(ui, action_type: str) -> int:
    return sum(
        event["text"].endswith(f"uses {action_type}")
        for event in ui._read_log()["round_1"]
    )


def test_the_first_of_each_action_asks_nothing(fight, monkeypatch):
    ui, pirate, _ = fight
    asked = answer_out_of_resources(monkeypatch, yes=False)
    for action_type in ("Action", "Bonus Action", "Reaction"):
        ui._add_action_use(action_type)
    assert asked == []
    assert pirate["action_uses"] == {"Action": 1, "Bonus Action": 1, "Reaction": 1}


def test_a_second_action_asks_and_no_logs_nothing(fight, monkeypatch):
    ui, pirate, _ = fight
    ui._add_action_use("Action")
    steps = len(ui.history)
    asked = answer_out_of_resources(monkeypatch, yes=False)
    ui._add_action_use("Action")
    assert asked == [
        "Pirate is out of:\n\n•  Action: already used this turn\n\n"
        "Log another Action anyway?"
    ]
    assert pirate["action_uses"] == {"Action": 1}
    assert _uses_logged(ui, "Action") == 1
    assert len(ui.history) == steps  # nothing to undo
    assert ui._status_label.text() == "Nothing done: Pirate is out of resources."


def test_a_second_action_with_yes_is_logged(fight, monkeypatch):
    # Action Surge, Haste: the UI doesn't know, so the GM says yes.
    ui, pirate, _ = fight
    ui._add_action_use("Action")
    answer_out_of_resources(monkeypatch, yes=True)
    ui._add_action_use("Action")
    assert pirate["action_uses"] == {"Action": 2}
    assert _uses_logged(ui, "Action") == 2
    ui._undo_last()
    assert pirate["action_uses"] == {"Action": 1}


def test_a_used_reaction_says_when_it_comes_back(fight):
    _, pirate, _ = fight
    pirate["action_uses"] = {"Reaction": 1}
    assert action_lack(pirate, "Reaction") == (
        "Reaction: already used (it comes back at the start of their turn)"
    )
    assert action_lack(pirate, "Action") is None
    assert action_lack(pirate, None) is None


def test_a_new_turn_gives_the_actions_back(fight, monkeypatch):
    ui, pirate, _ = fight
    ui._add_action_use("Action")
    ui._advance_turn()  # the Tiger's turn
    ui._advance_turn()  # the Pirate's again
    ui._select_character(pirate)
    asked = answer_out_of_resources(monkeypatch, yes=False)
    ui._add_action_use("Action")
    assert asked == []
    assert pirate["action_uses"] == {"Action": 1}


def test_a_cast_with_its_action_used_asks(fight, monkeypatch):
    ui, pirate, tiger = fight
    pirate["action_uses"] = {"Action": 1}
    asked = answer_out_of_resources(monkeypatch, yes=False)
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    assert "Action: already used this turn" in asked[0]
    assert "Cast Hold Person anyway?" in asked[0]
    assert "Hold Person" not in tiger["conditions"]
    assert "Concentrating" not in pirate["conditions"]
