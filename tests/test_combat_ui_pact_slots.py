"""A Warlock's Pact Magic slots in the combat UI: a pool kept apart from the
spell slots (Combat/PlayerCombatant.py's "pact_slots"), spent by the 1-9
keys, Cast Spell and the Custom Effect dialog, shown on the card, given back
by a Short Rest, and replayed from the player log like spell slots are."""

import json
from functools import cache

import pytest
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox

from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.effect_options import PactSlot, spell_slot_choices
from Combat.Definitions import Action
from Combat.EncounterConfig import resolve_players
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerCombatant import combatant_from_character
from Combat.Scenario import CombatScenario
from tests._combat_ui import make_ui, qapp
from tests._snapshot_helpers import build

# Warlock 3: two level 2 Pact Magic slots, no spell slots.
WARLOCK = "Y2024WarlockArchfeyThistleFeydreamCharacterBuilder"
# Wizard 3 / Warlock 3: spell slots {1: 4, 2: 2} and Pact Magic slots {2: 2}.
MULTICLASS = "SpellSlotTestWizard3Warlock3"

TIGER = CombatScenario(
    name="tiger_den",
    title="Tiger Den",
    combatants=lambda: [Tiger()],
    players=["Thistle"],
    monster_summary=["Tiger"],
)


@cache
def _sheet(build_name: str):
    return build(build_name)


def _start(ui):
    for i, char in enumerate(ui.characters):
        ui._initiative_inputs[id(char)].setText(str(20 - i))
    ui._start_combat()


def _actions(ui, name: str) -> list[tuple[str, object]]:
    return [
        (event["action"], event["value"])
        for event in ui._read_log()["round_1"]
        if event.get("character") == name and event.get("action")
    ]


# ---------------------------------------------------------------------------
# The combatant and its slot choices


def test_a_warlock_brings_its_pact_magic_slots():
    char = combatant_from_character(_sheet(WARLOCK))
    assert char["spell_slots"] == {}
    assert char["pact_slots"] == {2: 2}


def test_the_slot_choices_keep_the_two_pools_apart():
    char = combatant_from_character(_sheet(MULTICLASS))
    choices = spell_slot_choices(char, 2)
    assert [label for label, _ in choices] == [
        "Level 2 slot (2 left)",
        "Level 2 Pact Magic slot (2 left)",
        "No slot (ritual, item or feature)",
    ]
    assert not isinstance(choices[0][1], PactSlot)
    assert isinstance(choices[1][1], PactSlot) and choices[1][1] == 2


def test_a_warlocks_spell_is_paid_with_a_pact_magic_slot():
    char = combatant_from_character(_sheet(WARLOCK))
    label, slot = spell_slot_choices(char, 1)[0]
    assert label == "Level 2 Pact Magic slot (2 left)"
    assert isinstance(slot, PactSlot) and slot == 2


def test_a_warlock_out_of_pact_slots_is_not_untracked():
    char = combatant_from_character(_sheet(WARLOCK))
    char["pact_slots"] = {2: 0}
    assert spell_slot_choices(char, 1) == [("No slot (ritual, item or feature)", None)]


# ---------------------------------------------------------------------------
# Spending and regaining in a fight


@pytest.fixture
def multiclass(tmp_path):
    ui = make_ui(tmp_path, [Tiger()], [_sheet(MULTICLASS)])
    char, tiger = ui.characters
    ui._initiative_inputs[id(char)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(char)
    return ui, char


def test_a_pact_slot_is_spent_from_its_own_pool(multiclass):
    ui, char = multiclass
    ui._cast_spell_slot_level(PactSlot(2))
    assert char["pact_slots"] == {2: 1}
    assert char["spell_slots"] == {1: 4, 2: 2}
    assert (Action.REMOVE_PACT_SLOT, 2) in _actions(ui, char["name"])
    assert char["stats"]["spell_slots_used"] == 1
    assert char["stats"]["spell_slots_used_2"] == 1


def test_the_number_keys_spend_spell_slots_then_pact_slots(multiclass):
    ui, char = multiclass
    for _ in range(3):
        ui._cast_spell_slot_level(2)
    assert char["spell_slots"][2] == 0
    assert char["pact_slots"][2] == 1


def test_no_pact_slot_left_spends_nothing(multiclass):
    ui, char = multiclass
    char["pact_slots"][2] = 0
    ui._cast_spell_slot_level(PactSlot(2))
    assert char["spell_slots"] == {1: 4, 2: 2}
    assert "no level 2 Pact Magic slots left" in ui._status_label.text()


def test_regain_fills_the_pact_slots_first(multiclass):
    ui, char = multiclass
    ui._cast_spell_slot_level(PactSlot(2))
    ui._cast_spell_slot_level(2)
    ui.spell_combo.setCurrentIndex(1)  # Level 2

    ui._regain_spell_slot()
    assert (char["pact_slots"][2], char["spell_slots"][2]) == (2, 1)
    ui._regain_spell_slot()
    assert (char["pact_slots"][2], char["spell_slots"][2]) == (2, 2)
    assert (Action.ADD_PACT_SLOT, 2) in _actions(ui, char["name"])


def test_undo_gives_a_pact_slot_back(multiclass):
    ui, char = multiclass
    ui._cast_spell_slot_level(PactSlot(2))
    ui._undo_last()
    assert char["pact_slots"] == {2: 2}


def test_the_card_shows_the_pact_slots_on_their_own_row(multiclass):
    ui, char = multiclass
    ui._cast_spell_slot_level(PactSlot(2))
    card = ui._make_card(char)
    texts = [label.text() for label in card.findChildren(QLabel)]
    assert "LV1(4)  LV2(2)" in texts
    assert "Pact: LV2(1)" in texts


# ---------------------------------------------------------------------------
# The party's player log: replay and the Short Rest


@pytest.fixture
def no_modal_dialogs(monkeypatch):
    """The short-rest window closes as soon as it opens; End Encounter's
    question is answered Yes."""
    monkeypatch.setattr(QDialog, "exec", lambda dlg: 0)
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )


def _party_ui(tmp_path) -> CombatAppQt:
    """One run of the window for a party of the Warlock, between encounters,
    with the TIGER encounter prepared."""
    qapp()
    logs = tmp_path / "CombatLogs"
    path = scenario_log_path(logs, TIGER.name)
    if not path.exists():
        names = [_sheet(WARLOCK).character_name]
        prepare_log(path, TIGER, resolve_players(TIGER.players, names))
    ui = CombatAppQt(
        [],
        [_sheet(WARLOCK)],
        combat_log_dir=logs,
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenario_name=None,
        scenarios=[TIGER],
    )
    ui._build_window()
    return ui


def _warlock(ui) -> dict:
    return next(c for c in ui.characters if c.get("_is_player"))


def _spend_pact_slot_in_a_fight(tmp_path) -> CombatAppQt:
    ui = _party_ui(tmp_path)
    ui._load_encounter(TIGER, restart=False)
    _start(ui)
    ui._select_character(_warlock(ui))
    ui._cast_spell_slot_level(2)
    return ui


def test_a_spent_pact_slot_stays_spent_on_the_next_run(tmp_path):
    ui = _spend_pact_slot_in_a_fight(tmp_path)
    assert _warlock(ui)["pact_slots"] == {2: 1}
    assert _warlock(_party_ui(tmp_path))["pact_slots"] == {2: 1}


def test_a_short_rest_gives_the_pact_slots_back(tmp_path, no_modal_dialogs):
    ui = _spend_pact_slot_in_a_fight(tmp_path)
    ui._cast_spell_slot_level(2)
    ui._end_encounter()
    assert _warlock(ui)["pact_slots"] == {2: 0}

    ui._short_rest()
    assert _warlock(ui)["pact_slots"] == {2: 2}
    sessions = json.loads((tmp_path / "PlayerLogs" / "main_party.json").read_text())
    rest = sessions["sessions"][-1]
    assert rest["type"] == "short_rest"
    assert [(e["action"], e["value"]) for e in rest["events"]] == [
        (Action.ADD_PACT_SLOT, 2),
        (Action.ADD_PACT_SLOT, 2),
    ]
    assert _warlock(_party_ui(tmp_path))["pact_slots"] == {2: 2}


def test_a_short_rest_leaves_spell_slots_spent(tmp_path, no_modal_dialogs):
    ui = _party_ui(tmp_path)
    char = _warlock(ui)
    char["spell_slots"] = {1: 0}  # as if a multiclass had spent its slot
    ui._short_rest()
    assert char["spell_slots"] == {1: 0}
