"""Initiative groups: monsters with the same encounters.py "group" share one
initiative roll and take one turn together (TurnsMixin), while each keeps its
own card and stat block."""

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Combat.Combatants import Bull, Pirate, Tiger
from Combat.CombatUIQt.turns_mixin import initiative_units, unit_label
from Combat.EncounterConfig import (
    CampaignSpec,
    CombatantSpec,
    EncounterSpec,
    validate,
)
from Combat.PlayerCombatant import combatant_from_stat_block
from tests._combat_ui import make_ui


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


def _config(monsters, allies=()) -> CampaignSpec:
    encounter = EncounterSpec(
        id="pack", title="Pack", monsters=list(monsters), allies=list(allies)
    )
    return CampaignSpec("test_campaign", "", "", party=[], encounters=[encounter])


def test_a_group_reaches_every_combatant_it_names():
    tigers = CombatantSpec(Tiger, "Tiger", count=3, group="Tigers")
    encounter = EncounterSpec(
        id="pack", title="Pack", monsters=[tigers, CombatantSpec(Bull)]
    )
    assert tigers.summary() == "3× Tiger (one turn: Tigers)"
    chars = [
        combatant_from_stat_block(c) for s in encounter.monsters for c in s.build()
    ]
    assert [c.get("initiative_group") for c in chars] == ["Tigers"] * 3 + [None]
    # A combatant without a group has no key, so older logs stay unchanged.
    assert "initiative_group" not in chars[-1]


def test_validate_rejects_empty_groups_and_groups_across_sides():
    config = _config(
        [CombatantSpec(Tiger, group=""), CombatantSpec(Bull, group="Pack")],
        allies=[CombatantSpec(Tiger, group="Pack")],
    )
    problems = validate(config)
    assert any("group must be a non-empty name" in p for p in problems), problems
    assert any("group 'Pack' has monsters and allies" in p for p in problems)


def test_units_keep_each_group_at_its_first_members_place():
    a, b, c, d = ({"name": n} for n in "abcd")
    a["initiative_group"] = c["initiative_group"] = "Pair"
    assert initiative_units([a, b, c, d]) == [[a, c], [b], [d]]
    assert unit_label([a, c]) == "Pair (2)"
    assert unit_label([b]) == "b"


def _grouped(name: str, group: str):
    tiger = Tiger()
    tiger.set_name(name)
    tiger.initiative_group = group
    return tiger


@pytest.fixture
def fight(tmp_path):
    """Tiger 1 and Tiger 2 (one turn, initiative 12) between a Pirate (15)
    and another Pirate (5), listed so the tigers aren't next to each other."""
    ui = make_ui(
        tmp_path,
        [
            _grouped("Tiger 1", "Tigers"),
            Pirate(),
            _grouped("Tiger 2", "Tigers"),
            Pirate(),
        ],
    )
    tiger1, pirate, tiger2, last = ui.characters
    # One shared input for the whole group.
    assert ui._initiative_inputs[id(tiger1)] is ui._initiative_inputs[id(tiger2)]
    ui._initiative_inputs[id(tiger1)].setText("12")
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(last)].setText("5")
    ui._start_combat()
    return ui, pirate, tiger1, tiger2, last


def test_a_group_sorts_together_and_takes_one_turn(fight):
    ui, pirate, tiger1, tiger2, last = fight
    assert ui.initiative_order == [pirate, tiger1, tiger2, last]
    assert ui._turn_counter_label.text() == "Turn 1 / 3"

    tiger1["action_uses"] = tiger2["action_uses"] = {"Action": 1}
    ui._advance_turn()
    assert ui._current_turn_group() == [tiger1, tiger2]
    assert ui._turn_counter_label.text() == "Turn 2 / 3"
    assert tiger1["action_uses"] == tiger2["action_uses"] == {}
    assert ui._card_state_flags(tiger2)[1] and not ui._card_state_flags(pirate)[1]
    assert ui._current_turn_name() == "Tigers"
    assert ui._next_turn_btn.text() == "Next Combatant"

    ui._advance_turn()
    assert ui._current_turn_group() == [last]
    assert ui._next_turn_btn.text() == "Next Round"
    ui._advance_turn()
    assert (ui.round_number, ui._current_turn_group()) == (2, [pirate])


def test_roll_for_all_rolls_once_per_group(tmp_path, monkeypatch):
    ui = make_ui(
        tmp_path, [_grouped("Tiger 1", "Tigers"), _grouped("Tiger 2", "Tigers")]
    )
    rolls = []
    monkeypatch.setattr(
        "Combat.CombatUIQt.turns_mixin.random.randint",
        lambda a, b: rolls.append(1) or 10,
    )
    assert ui._initiative_widget is not None
    roll_all = next(
        b
        for b in ui._initiative_widget.findChildren(type(ui._start_combat_btn))
        if b.text() == "Roll for All"
    )
    roll_all.click()
    assert len(rolls) == 1
    assert ui._start_combat_btn.isEnabled()
