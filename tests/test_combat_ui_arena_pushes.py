"""Pushes from the Use / Cast dialog moved on the battle map
(Notes/combat-arena-plan.md, step 21): a pick with a CombatPush (Thunderwave,
a Shove, the Push mastery) moves each target it lands on straight away from
its source as a Push move (step 17): no movement spent, no Opportunity
Attack, one undo step with the rest of the Apply. Only once the map is in
use (Decision 29)."""

import pytest
from PyQt6.QtWidgets import QCheckBox, QDialog, QPushButton

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Arena.arena import MOVED_KEY, POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import WALL, Spot
from Combat.CombatUIQt.effect_options import effect_options
from Combat.Effects.triggers import OpportunityAttack
from Combat.LogFiles import read_json
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerLog import is_round_key
from Core.Definitions import CreatureSize
from Model.Content.CombatEffect import CombatPush
from Model.Content.UnarmedStrikeEffects import SHOVE_PRONE, SHOVE_PUSH
from tests._combat_ui import make_ui


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path, monkeypatch, fails: bool = True, in_use: bool = True):
    """Edmund at F6, a Large Tiger at G6-H7 next to him, Edmund's turn,
    Edmund the source and the Tiger the target; every save made fails (or
    succeeds)."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    player[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 5]
    ui.arena_settings.in_use = in_use
    ui._select_character(player)
    ui._set_targets([tiger])
    monkeypatch.setattr(
        type(ui), "_roll_effect_save", lambda self, *args, **kwargs: not fails
    )
    return ui, player, tiger


def _texts(ui) -> list[str]:
    data = read_json(ui.log_file)
    keys = sorted((k for k in data if is_round_key(k)), key=lambda k: int(k[6:]))
    return [e["text"] for k in keys for e in data[k]]


def _logged(ui, line: str) -> bool:
    """Whether the log has `line` (after its "[Edmund's turn] ")."""
    return any(t.endswith(line) for t in _texts(ui))


def _at(char) -> Cell:
    return Cell.of(char[POSITION_KEY])


def _row(char: dict, name: str):
    return next(
        option
        for _, options in effect_options(char)
        for option in options
        if option.name == name
    )


def _cast(ui, monkeypatch, pick: str, act=None):
    """Open Use / Cast on `pick` and click Apply, after `act(dlg)`."""

    def fake_exec(dlg):
        if act is not None:
            act(dlg)
        dlg.findChild(QPushButton, "primaryBtn").click()
        return 0

    monkeypatch.setattr(QDialog, "exec", fake_exec)
    ui._show_custom_condition_dialog(pick=pick)


def test_thunderwave_pushes_who_fails_10_feet_away(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    hp = tiger["hp"]
    _cast(ui, monkeypatch, "Thunderwave")
    assert tiger["hp"] < hp, "the damage too"
    assert _at(tiger) == Cell(8, 5)
    line = "Tiger is pushed from G6 to I6 (10 ft.; no movement spent)."
    assert _logged(ui, line)
    assert line in ui._status_label.text()
    assert MOVED_KEY not in tiger, "not its own movement"


def test_who_saves_isnt_pushed(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch, fails=False)
    _cast(ui, monkeypatch, "Thunderwave")
    assert _at(tiger) == Cell(6, 5)
    assert not any("pushed" in t for t in _texts(ui))


def test_nobody_is_pushed_before_the_map_is_in_use(tmp_path, monkeypatch):
    """Decision 29: the made-up starting places don't decide anything, and
    the dialog doesn't offer the push."""
    ui, player, tiger = _fight(tmp_path, monkeypatch, in_use=False)
    seen = {}

    def look(dlg):
        seen["shown"] = not dlg.findChild(QCheckBox, "pushTargets").isHidden()

    _cast(ui, monkeypatch, "Thunderwave", look)
    assert seen["shown"] is False
    assert _at(tiger) == Cell(6, 5)


def test_the_dialog_offers_the_push_and_unticking_it_moves_nobody(
    tmp_path, monkeypatch
):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    seen = {}

    def untick(dlg):
        box = dlg.findChild(QCheckBox, "pushTargets")
        seen.update(shown=not box.isHidden(), ticked=box.isChecked(), text=box.text())
        box.setChecked(False)

    _cast(ui, monkeypatch, "Thunderwave", untick)
    assert seen == {
        "shown": True,
        "ticked": True,
        "text": "Who it lands on is pushed 10 ft. away from Edmund",
    }
    assert _at(tiger) == Cell(6, 5)


def test_the_push_is_undone_with_the_rest_of_the_apply(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    hp = tiger["hp"]
    _cast(ui, monkeypatch, "Thunderwave")
    ui._undo_last()
    assert _at(tiger) == Cell(6, 5)
    assert tiger["hp"] == hp
    assert not any("pushed" in t for t in _texts(ui))


def test_a_push_stopped_by_a_wall_says_so(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui.arena_settings.terrain.put(Cell(9, 5), Spot(ground=WALL))
    _cast(ui, monkeypatch, "Thunderwave")
    assert _at(tiger) == Cell(7, 5)
    line = "Tiger stops after 5 of 10 ft.: a wall or an object."
    assert _logged(ui, line)
    assert line in ui._status_label.text()


def test_a_push_out_of_reach_provokes_no_opportunity_attack(tmp_path, monkeypatch):
    """Pushed out of Edmund's reach on Edmund's turn, and Edmund pushed out
    of the Tiger's on the Tiger's: neither is its own movement."""
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    _cast(ui, monkeypatch, "Thunderwave")
    assert not [p for p in ui._hit_prompts if isinstance(p, OpportunityAttack)]
    assert not any("reach" in t for t in _texts(ui))


def test_an_unarmed_strikes_shove_pushes_5_feet_or_knocks_prone(tmp_path, monkeypatch):
    """Rules Glossary, Unarmed Strike: DC 8 + Strength modifier +
    Proficiency Bonus, "push it 5 feet away or cause it to have the Prone
    condition"."""
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    sheet = player["_stat_block"]
    push = _row(player, SHOVE_PUSH)
    prone = _row(player, SHOVE_PRONE)
    expected_dc = 8 + sheet.get_strength_modifier() + sheet.get_proficiency_bonus()
    assert push.ability == prone.ability == "STR"
    assert push.dc == prone.dc == expected_dc
    assert push.push == CombatPush(5)
    assert "pushed 5 ft." in push.summary
    assert prone.condition == "Prone" and prone.push is None
    assert ui._apply_row(player, tiger, push)
    assert _at(tiger) == Cell(7, 5)
    # Another attack of the same Attack action: the row as it is now.
    assert ui._apply_row(player, tiger, _row(player, SHOVE_PRONE))
    assert "Prone" in tiger["conditions"]
    assert _at(tiger) == Cell(7, 5)


def test_too_big_for_the_push_stays_and_is_logged(tmp_path, monkeypatch):
    """The Push mastery's "if it is Large or smaller", on a Huge Tiger."""
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    tiger["size"] = "Huge"
    mastery = CombatPush(10, up_to=True, largest=CreatureSize.LARGE)
    lines = ui._push_targets(player, mastery, [tiger], "Push")
    assert _at(tiger) == Cell(6, 5)
    assert lines == ["Tiger isn't moved by Push: only Large or smaller is."]
    assert _logged(ui, lines[0])


def test_the_thunderwave_row_carries_its_push(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    thunderwave = _row(player, "Thunderwave")
    assert thunderwave.push == CombatPush(10)
    assert "pushed 10 ft." in thunderwave.summary
    assert "pushed 10 feet" not in thunderwave.note, "said by the push now"
