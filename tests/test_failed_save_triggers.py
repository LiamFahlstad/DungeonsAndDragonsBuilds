"""What a failed save triggers (Notes/combat-effects-plan.md, step 6.7):
FAILS_SAVE rows, asked as a save the Custom Effect dialog rolls fails, and
CombatEffect.reroll_save. And Ever-Ready Shot as a fight starts.

Expected values come from the rules text:
- Indomitable (Fighter 9): "If you fail a saving throw, you can reroll it
  with a bonus equal to your Fighter level. You must use the new roll, and
  you can't use this feature again until you finish a Long Rest. You can
  use this feature twice before a Long Rest starting at level 13 and three
  times before a Long Rest starting at level 17."
- Ever-Ready Shot (Arcane Archer 10): "When you roll Initiative, you can
  regain one expended use of Arcane Shot."

Sylvaine (an Arcane Archer Fighter 18) has 3 uses of Indomitable, +18."""

import random

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Examples.Y2024_Fighter_ArcaneArcher_SylvaineFarshot import (
    Y2024FighterArcaneArcherSylvaineFarshotCharacterBuilder as Sylvaine,
)
from CharacterContent.Features.ClassFeatures.Fighter.FighterFeatures import (
    Indomitable,
)
from Combat.CombatUIQt.effect_options import triggered_rows
from Combat.CombatUIQt.saves import CustomEffect, save_modifier
from Combat.Effects.triggers import (
    FailedSaveOutcome,
    TriggerChoice,
    TriggerMode,
    outcome_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from tests._combat_ui import make_ui


def test_a_reroll_reads_back_and_answers_a_failed_save():
    effect = CombatEffect(
        targets_self=True,
        trigger=CombatTrigger(TriggerEvent.FAILS_SAVE),
        reroll_save=18,
    )
    assert effect.to_dict()["reroll_save"] == 18
    assert CombatEffect.from_dict(effect.to_dict()) == effect
    for bad in (
        lambda: CombatEffect(reroll_save=18),
        lambda: CombatEffect(
            reroll_save=-1, trigger=CombatTrigger(TriggerEvent.FAILS_SAVE)
        ),
    ):
        with pytest.raises(ValueError):
            bad()


def test_indomitable_rerolls_with_the_fighter_level():
    (effect,) = Indomitable().combat_effects(Sylvaine().build())
    assert effect.trigger == CombatTrigger(TriggerEvent.FAILS_SAVE)
    assert effect.reroll_save == 18


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    def __init__(self, answer="apply"):
        self.answer = answer
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        if self.answer == "apply":
            return TriggerChoice(apply=tuple(firings))
        return TriggerChoice()


@pytest.fixture
def window(tmp_path, monkeypatch):
    """Sylvaine and an Ogre, before the fight starts."""
    ui = make_ui(tmp_path, [Ogre()], [Sylvaine().build()])
    sylvaine, ogre = ui.characters
    for char, value in zip(ui.characters, (5, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    return ui, sylvaine, ogre, answers


def test_indomitable_asks_about_a_failed_save(window):
    ui, sylvaine, _, _ = window
    ui._start_combat()
    failed = FailedSaveOutcome(sylvaine, "WIS", 20, 9, "Hold Person")
    found, _ = outcome_firings([failed], triggered_rows)
    (firing,) = [f for f in found if f.row.name == "Indomitable"]
    assert firing.mode is TriggerMode.ASK
    assert firing.question == (
        f"{sylvaine['name']} fails a DC 20 WIS save against Hold Person with 9:"
        " use Indomitable? Rerolls the save with +18. 3 of 3 uses left."
    )


def _hold_person(ui, target, dc):
    ui._set_targets([target])
    ui._apply_custom_effect(
        CustomEffect(name="Hold Person", condition="Paralyzed", ability="WIS", dc=dc)
    )


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def test_the_reroll_with_18_saves_her(window, monkeypatch):
    ui, sylvaine, ogre, answers = window
    ui._start_combat()
    ui._select_character(ogre)
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 5))
    mod = save_modifier(sylvaine, "WIS")
    dc = 5 + mod + 10  # 5 fails it; 5 + 18 makes it
    _hold_person(ui, sylvaine, dc)
    assert len(answers.asked) == 1
    assert "Paralyzed" not in sylvaine["conditions"]
    assert sylvaine["feature_uses_used"]["Indomitable"] == 1
    total = 5 + mod
    assert (
        f"{sylvaine['name']} rerolls the save with Indomitable: {total} + 18"
        f" = {total + 18}, makes it"
    ) in _lines(ui)


def test_a_reroll_that_still_fails_must_be_kept(window, monkeypatch):
    ui, sylvaine, ogre, _ = window
    ui._start_combat()
    ui._select_character(ogre)
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 5))
    _hold_person(ui, sylvaine, 99)
    assert "Paralyzed" in sylvaine["conditions"]
    assert sylvaine["feature_uses_used"]["Indomitable"] == 1


def test_skip_keeps_the_failure_and_the_use(window, monkeypatch):
    ui, sylvaine, ogre, answers = window
    answers.answer = "skip"
    ui._start_combat()
    ui._select_character(ogre)
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 5))
    _hold_person(ui, sylvaine, 99)
    assert "Paralyzed" in sylvaine["conditions"]
    assert (sylvaine.get("feature_uses_used") or {}).get("Indomitable", 0) == 0


def test_a_save_typed_in_from_the_table_isnt_asked_about(window):
    ui, sylvaine, ogre, answers = window
    ui._start_combat()
    ui._select_character(ogre)
    ui._set_targets([sylvaine])
    ui._apply_custom_effect(
        CustomEffect(
            name="Hold Person",
            condition="Paralyzed",
            ability="WIS",
            dc=99,
            typed_totals={id(sylvaine): 3},
        )
    )
    assert answers.asked == []


def test_ever_ready_shot_asks_with_an_arcane_shot_spent(window):
    ui, sylvaine, _, answers = window
    sylvaine["feature_uses_used"] = {"Arcane Shot": 2}
    ui._start_combat()
    assert len(answers.asked) == 1
    assert answers.asked[0][0].startswith(
        f"{sylvaine['name']} rolls Initiative: use Ever-Ready Shot?"
    )
    assert sylvaine["feature_uses_used"]["Arcane Shot"] == 1  # one, not both


def test_a_reroll_made_at_the_table_counts_as_typed(window, monkeypatch):
    ui, sylvaine, ogre, _ = window
    ui._start_combat()
    ui._select_character(ogre)

    def at_table(firings):
        return TriggerChoice(apply=tuple(firings), rolled=((firings[0], 31),))

    monkeypatch.setattr(ui, "_ask_triggers", at_table)
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 1))
    _hold_person(ui, sylvaine, 30)
    assert "Paralyzed" not in sylvaine["conditions"]
    assert (
        f"{sylvaine['name']} rerolls the save with Indomitable: 31, rolled at the"
        " table, makes it"
    ) in _lines(ui)
