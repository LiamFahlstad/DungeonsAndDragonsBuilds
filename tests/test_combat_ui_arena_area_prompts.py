"""Areas that stay, acting (Notes/combat-arena-plan.md, step 24): a
creature entering a kept area, the area moved onto it, or a turn starting
or ending in it, as the area's own text says, gets a turn-column button
that opens Use / Cast on the area's effect with that creature targeted and
nothing spent; and the area panel's Move, which aims a kept Moonbeam or
Flaming Sphere again, keeping its time and concentration."""

import random
from functools import cache

import pytest
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
)

from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import AREA_KEY, AreaPrompt, lasting_areas
from Combat.CombatUIQt.arena_view import MoveKind
from Combat.CombatUIQt.effect_options import effect_options
from Combat.Combatants import Pirate
from Combat.EncounterLogs import TURN_PREFIX
from Combat.Monsters.CR_1.monsters import Tiger
from tests._combat_ui import answer_out_of_resources, make_ui, qapp
from tests._snapshot_helpers import build

DRUID = "Y2024DruidLandRowanThistledownCharacterBuilder"  # Moonbeam, Web
CLERIC = "Y2014ClericDeathMortimerGrimvaleCharacterBuilder"  # Spirit Guardians
ROWAN = "Rowan Thistledown"
MORTIMER = "Mortimer Grimvale"
# Moonbeam's 5-foot-radius Cylinder aimed here covers (10, 5) and the four
# cells beside it.
BEAM = Cell(10, 5)


@cache
def _builds():
    return build(DRUID), build(CLERIC)


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Rowan (a Druid, on its turn) at E6, the Pirate at I6, the Tiger at
    O9, Mortimer (a Cleric) far off at U13; the map in use. An "out of
    resources ... anyway?" question is answered Yes, never left open."""
    answer_out_of_resources(monkeypatch)
    ui = make_ui(tmp_path, [Pirate(), Tiger()], list(_builds()))
    rolls = {ROWAN: "20", "Pirate": "15", "Tiger": "10", MORTIMER: "5"}
    for char in ui.characters:
        ui._initiative_inputs[id(char)].setText(rolls[char["name"]])
    ui._start_combat()
    rowan, pirate, tiger, mortimer = (
        _named(ui, n) for n in (ROWAN, "Pirate", "Tiger", MORTIMER)
    )
    rowan[POSITION_KEY] = [4, 5]
    pirate[POSITION_KEY] = [8, 5]
    tiger[POSITION_KEY] = [14, 8]
    mortimer[POSITION_KEY] = [20, 12]
    ui.arena_settings.in_use = True
    ui._select_character(rowan)
    ui._set_targets([])
    ui._refresh_views()
    return ui, rowan, pirate, tiger, mortimer


def _option(char: dict, name: str):
    return next(
        option
        for _, options in effect_options(char)
        for option in options
        if option.name == name
    )


def _cast_kept(ui, monkeypatch, caster: dict, name: str, cell: Cell, slot=None):
    """Aim caster's `name` (its picker row) at `cell` on the map, click
    there and apply the dialog that opens again: cast and kept on the map,
    at `slot` if given."""

    def apply(dlg: QDialog):
        if slot is not None:
            combo = dlg.findChild(QComboBox, "spellSlot")
            combo.setCurrentIndex(combo.findData(slot))
        dlg.findChild(QPushButton, "primaryBtn").click()

    monkeypatch.setattr(QDialog, "exec", lambda dlg: apply(dlg) or 0)
    ui._select_character(caster)
    assert ui._start_area_targeting(_option(caster, name))
    ui._arena_view.aim_area(cell)
    ui._area_picked(cell)
    qapp().processEvents()  # the dialog opens again once the click is over
    (entry,) = [e for e in caster["active_spells"] if e["name"] == name]
    return entry


def _area_buttons(ui) -> list[AreaPrompt]:
    return [
        p for p in (*ui._turn_prompts, *ui._hit_prompts) if isinstance(p, AreaPrompt)
    ]


def _logged(ui) -> list[str]:
    data = ui._read_log()
    lines = []
    for key, events in data.items():
        if key.startswith("round_") and isinstance(events, list):
            for event in events:
                match = TURN_PREFIX.match(str(event["text"]))
                lines.append(match.group(2) if match else str(event["text"]))
    return lines


def _press(ui, monkeypatch, prompt: AreaPrompt) -> dict:
    """Press the area's button and look at the dialog it opens; apply it."""
    seen: dict = {}

    def look(dlg: QDialog):
        seen["name"] = dlg.findChild(QLineEdit, "effectName").text()
        slot = dlg.findChild(QComboBox, "spellSlot")
        seen["slot"] = slot.currentData()
        seen["slot enabled"] = slot.isEnabled()
        seen["action"] = dlg.findChild(QComboBox, "actionCost").currentData()
        seen["concentrates"] = dlg.findChild(
            QCheckBox, "sourceConcentrates"
        ).isChecked()
        free = dlg.findChild(QLabel, "keptAreaFree")
        seen["free"] = free.text() if free is not None else ""
        seen["damage"] = dlg.findChild(QLineEdit, "effectDamage")
        seen["damage"] = seen["damage"].text() if seen["damage"] else ""
        dlg.findChild(QPushButton, "primaryBtn").click()
        seen["problem"] = dlg.findChild(QLabel, "statusLabel").text()

    monkeypatch.setattr(QDialog, "exec", lambda dlg: look(dlg) or 0)
    ui._use_turn_prompt(prompt)
    return seen


def test_walking_into_moonbeam_gives_its_button_which_costs_nothing(fight, monkeypatch):
    ui, rowan, pirate, *_ = fight
    entry = _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM)
    assert entry["concentration"]
    slots = dict(rowan["spell_slots"])
    uses = dict(rowan.get("action_uses") or {})
    ui._move_combatant(pirate, Cell(9, 5))
    (prompt,) = _area_buttons(ui)
    assert prompt.prompt == f"{ROWAN}'s Moonbeam on Pirate (entered it)"
    assert prompt in ui._hit_prompts, "a button for the rest of the turn"
    assert f"Pirate enters {ROWAN}'s Moonbeam." in ui._status_label.text()

    hp = pirate["hp"]
    seen = _press(ui, monkeypatch, prompt)
    assert seen["name"] == "Moonbeam"
    assert seen["slot"] is None and not seen["slot enabled"]
    assert seen["action"] is None and not seen["concentrates"]
    assert "costs nothing" in seen["free"], seen
    assert ui.selected_character is rowan and ui.target_characters == [pirate]
    assert pirate["hp"] < hp, "the Pirate takes the beam's damage"
    assert rowan["spell_slots"] == slots, "no slot spent"
    assert dict(rowan.get("action_uses") or {}) == uses, "no action spent"
    (still,) = rowan["active_spells"]
    assert still["name"] == "Moonbeam" and still[AREA_KEY] == entry[AREA_KEY]
    assert _area_buttons(ui) == [], "the button goes once it's used"


def test_undoing_the_walk_takes_the_button_back(fight, monkeypatch):
    ui, rowan, pirate, *_ = fight
    _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM)
    ui._move_combatant(pirate, Cell(9, 5))
    assert len(_area_buttons(ui)) == 1
    ui._move_combatant(pirate, Cell(9, 4))  # still in it: no second button
    assert len(_area_buttons(ui)) == 1
    ui._undo_last()
    ui._undo_last()
    assert _area_buttons(ui) == []


def test_moonbeam_acts_as_a_turn_ends_there_not_as_one_starts(fight, monkeypatch):
    """2024 Moonbeam: "when it enters the spell's area or ends its turn
    there"; nothing as a turn starts."""
    ui, rowan, pirate, *_ = fight
    _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM)
    pirate[POSITION_KEY] = [10, 5]  # put there, not walked in
    ui._advance_turn()  # the Pirate's turn starts in it
    assert ui._current_turn_group()[0] is pirate
    assert _area_buttons(ui) == []
    assert f"Pirate starts its turn in {ROWAN}'s Moonbeam." in _logged(ui)
    ui._advance_turn()  # and ends there: the Tiger's turn shows its button
    (prompt,) = _area_buttons(ui)
    assert prompt.prompt == f"{ROWAN}'s Moonbeam on Pirate (ended its turn in it)"
    assert prompt in ui._turn_prompts
    assert f"Pirate ends its turn in {ROWAN}'s Moonbeam." in _logged(ui)
    ui._advance_turn()
    assert _area_buttons(ui) == [], "gone as the next turn starts"


def test_web_acts_as_a_turn_starts_there(fight, monkeypatch):
    """Web: "The first time a creature enters the webs on a turn or starts
    its turn there"."""
    ui, rowan, pirate, *_ = fight
    _cast_kept(ui, monkeypatch, rowan, "Web", Cell(12, 5))
    pirate[POSITION_KEY] = [12, 5]
    ui._advance_turn()
    (prompt,) = _area_buttons(ui)
    assert prompt.prompt == f"{ROWAN}'s Web on Pirate (starts its turn in it)"
    assert not any("Web" in r for r in ui._turn_reminders), "a button, not a line"
    monkeypatch.setattr(random, "randint", lambda low, high: 1)  # it fails
    seen = _press(ui, monkeypatch, prompt)
    assert seen["name"] == "Web" and seen["slot"] is None
    assert "Restrained" in pirate["conditions"]
    (entry,) = rowan["active_spells"]
    assert {"target": "Pirate", "condition": "Restrained"} in entry["applied"]
    ui._select_character(rowan)
    ui._shortcut_remove_concentration()
    assert "Restrained" not in pirate["conditions"], "held by the Web's concentration"


def test_an_area_that_has_ended_says_so(fight, monkeypatch):
    ui, rowan, pirate, *_ = fight
    _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM)
    ui._move_combatant(pirate, Cell(9, 5))
    (prompt,) = _area_buttons(ui)
    ui._select_character(rowan)
    ui._shortcut_remove_concentration()
    opened: list = []
    monkeypatch.setattr(QDialog, "exec", lambda dlg: opened.append(dlg) or 0)
    ui._use_turn_prompt(prompt)
    assert opened == []
    assert f"{ROWAN}'s Moonbeam has ended." in ui._status_label.text()
    assert _area_buttons(ui) == []


def test_an_upcast_area_acts_at_its_slot(fight, monkeypatch):
    ui, rowan, pirate, *_ = fight
    entry = _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM, slot=4)
    assert entry[AREA_KEY]["slot_level"] == 4
    ui._move_combatant(pirate, Cell(9, 5))
    (prompt,) = _area_buttons(ui)
    seen = _press(ui, monkeypatch, prompt)
    assert "at level 4" in seen["free"]
    assert seen["damage"].startswith("4d10"), seen["damage"]


def test_spirit_guardians_on_the_map_asks_through_its_area(fight, monkeypatch):
    """The badge's "if it ends its turn in the Emanation" prompt gives way
    to the area's own button, which only comes for whoever is in it, and
    picks the damage row."""
    ui, rowan, pirate, tiger, mortimer = fight
    mortimer[POSITION_KEY] = [9, 6]  # the Pirate 10 ft. off, the Tiger 40
    _cast_kept(ui, monkeypatch, mortimer, "Spirit Guardians", Cell(9, 6))
    while ui._current_turn_group()[0] is not pirate:
        ui._advance_turn()
    ui._advance_turn()  # the Pirate ended its turn in it
    (prompt,) = _area_buttons(ui)
    assert prompt.target is pirate and prompt.when == "ends"
    assert not [p for p in ui._turn_prompts if not isinstance(p, AreaPrompt)]
    ui._advance_turn()  # the Tiger ended its turn far off: nothing
    assert _area_buttons(ui) == []
    assert not [p for p in ui._turn_prompts if not isinstance(p, AreaPrompt)]
    ui._move_combatant(tiger, Cell(10, 7))  # walks in
    (prompt,) = _area_buttons(ui)
    seen = _press(ui, monkeypatch, prompt)
    assert seen["name"] == "Spirit Guardians: damage"
    assert seen["slot"] is None and seen["action"] is None


def test_an_emanation_moved_onto_someone_gives_its_button(fight, monkeypatch):
    ui, rowan, pirate, tiger, mortimer = fight
    _cast_kept(ui, monkeypatch, mortimer, "Spirit Guardians", Cell(20, 12))
    ui._move_combatant(mortimer, Cell(12, 8), kind=MoveKind.TELEPORT)
    prompts = _area_buttons(ui)
    assert {(p.target["name"], p.when) for p in prompts} == {("Tiger", "moved onto")}


def _select(ui, caster):
    """Show the map and select caster's one kept area on it."""
    if not ui._arena_shown():
        ui._toggle_view()
    (area,) = [
        a
        for a in lasting_areas(ui.characters, ui.arena_settings)
        if a.caster == caster["name"]
    ]
    ui._select_area(area.key)
    return area


def test_move_aims_moonbeam_again_keeping_its_time_and_concentration(
    fight, monkeypatch
):
    ui, rowan, pirate, tiger, _ = fight
    entry = _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM)
    entry["time_left"] = 30
    rowan["action_uses"] = {}  # a later turn: its Action is free again
    key = entry[AREA_KEY]["key"]
    _select(ui, rowan)
    move = ui._area_panel.findChild(QPushButton, "areaPanelMoveBtn")
    assert not move.isHidden()
    assert "up to 60 ft., an Action" in move.toolTip()
    actions_before = dict(rowan.get("action_uses") or {})
    move.click()
    assert ui._area_targeting is not None and ui._area_targeting["move"] == key
    assert ui._area_keep.isHidden() and not ui._area_shape.isEnabled()
    ui._arena_view.aim_area(Cell(14, 8))  # onto the Tiger, 35 ft. away
    assert "Moves 35 ft., up to 60 ft." in ui._area_label.text()
    assert "onto Tiger" in ui._area_label.text()
    ui._area_picked(Cell(14, 8))
    assert ui._area_targeting is None
    (moved,) = rowan["active_spells"]
    record = moved[AREA_KEY]
    assert record["key"] == key and record["aim"] == [14, 8]
    assert [14, 7] in record["cells"] and [10, 5] not in record["cells"]
    assert moved["time_left"] == 30 and moved["concentration"]
    assert "Concentrating" in rowan["conditions"]
    uses = rowan.get("action_uses") or {}
    assert uses.get("Action", 0) == actions_before.get("Action", 0) + 1
    assert f"{ROWAN}'s Moonbeam moves from K6 to O9 (35 ft.)." in _logged(ui)
    (prompt,) = _area_buttons(ui)
    assert prompt.target is tiger and prompt.when == "moved onto"

    ui._undo_last()
    rowan = _named(ui, ROWAN)
    (back,) = rowan["active_spells"]
    assert back[AREA_KEY]["aim"] == [10, 5]
    assert _area_buttons(ui) == []


def test_moving_past_its_reach_is_warned_and_esc_leaves_it(fight, monkeypatch):
    ui, rowan, *_ = fight
    _cast_kept(ui, monkeypatch, rowan, "Moonbeam", BEAM)
    _select(ui, rowan)
    ui._move_selected_area()
    ui._arena_view.aim_area(Cell(10, 0))
    ui._arena_view.aim_area(Cell(23, 15))  # 115 ft. off
    assert "past its 60 ft.!" in ui._area_label.text()
    opened: list = []
    monkeypatch.setattr(QDialog, "exec", lambda dlg: opened.append(dlg) or 0)
    assert ui._cancel_area_targeting()
    qapp().processEvents()
    assert opened == [], "no dialog: the area just stays"
    (entry,) = rowan["active_spells"]
    assert entry[AREA_KEY]["aim"] == [10, 5]
    ui._move_selected_area()
    ui._area_picked(Cell(23, 15))
    assert "That's past its 60 ft." in ui._status_label.text()


def test_flaming_sphere_moves_with_a_bonus_action(fight, monkeypatch):
    ui, rowan, *_ = fight
    _cast_kept(ui, monkeypatch, rowan, "Flaming Sphere", Cell(6, 2))
    _select(ui, rowan)
    ui._move_selected_area()
    ui._area_picked(Cell(8, 2))
    uses = rowan.get("action_uses") or {}
    assert uses.get("Bonus Action") == 1


def test_an_area_around_its_caster_has_no_move(fight, monkeypatch):
    ui, rowan, pirate, tiger, mortimer = fight
    _cast_kept(ui, monkeypatch, mortimer, "Spirit Guardians", Cell(20, 12))
    _select(ui, mortimer)
    assert ui._area_panel.findChild(QPushButton, "areaPanelMoveBtn").isHidden()
