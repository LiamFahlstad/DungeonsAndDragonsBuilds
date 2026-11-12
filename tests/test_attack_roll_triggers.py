"""What answers an attack roll before it's rolled (Notes/combat-effects-plan.md,
Q65): TriggerEvent.ATTACKS, asked of everyone else in the fight as the
Custom Effect dialog or a monster's action button is about to roll one.
Gabriel's Warding Flare is the source. Its rules text (Light Domain Cleric
level 3): "When a creature that you can see within 30 feet of yourself makes
an attack roll, you can take a Reaction to impose Disadvantage on the attack
roll, causing light to flare before it hits or misses. You can use this
feature a number of times equal to your Wisdom modifier (minimum of once)."

Gabriel's Wisdom modifier is +4 at level 4: 4 uses. Clover has AC 18. The
Ogre's Greatclub is +6."""

import random
from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder as Clover,
)
from Builds.Characters.Y2024_Cleric_Light_GabrielGreybeard import (
    Y2024ClericLightGabrielGreybeardCharacterBuilder as Gabriel,
)
from Combat.CombatUIQt.attack_rolls import parse_attack_roll
from Combat.CombatUIQt.effect_options import effect_options, triggered_rows
from Combat.CombatUIQt.monster_actions import parse_action
from Combat.CombatUIQt.saves import CustomEffect
from Combat.Effects.triggers import TriggerChoice, TriggerMode, attack_roll_firings
from Combat.Monsters.CR_2.monsters import Ogre
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatModifiers import AttackKind
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from tests._combat_ui import make_ui

FLARE = "Warding Flare"

# ---------------------------------------------------------------------------
# As data


def test_an_attacks_trigger_reads_back_as_it_was_written():
    trigger = CombatTrigger(TriggerEvent.ATTACKS, enemy_only=True, when="you see it")
    effect = CombatEffect(trigger=trigger)
    assert CombatEffect.from_dict(effect.to_dict()) == effect
    assert effect.to_dict()["trigger"] == {
        "event": "attacks",
        "enemy_only": True,
        "when": "you see it",
    }


def test_an_attacks_trigger_has_no_attack_kind_yet():
    # The roll isn't made: whether it hits, or its kind, isn't asked.
    with pytest.raises(ValueError):
        CombatTrigger(TriggerEvent.ATTACKS, attacks=AttackKind.MELEE)


# ---------------------------------------------------------------------------
# The interpreter


@pytest.fixture
def party(tmp_path):
    """An Ogre, Gabriel and Clover in a fight, on the Ogre's turn."""
    ui = make_ui(tmp_path, [Ogre()], [Gabriel().build(), Clover().build()])
    gabriel, clover, ogre = ui.characters
    for char, value in zip(ui.characters, (5, 3, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(ogre)
    return ui, gabriel, clover, ogre


def _firings(ui, attacker, target):
    return attack_roll_firings(attacker, target, ui.characters, triggered_rows)


def test_warding_flare_is_asked_as_an_enemy_attacks_an_ally(party):
    ui, gabriel, clover, ogre = party
    (firing,) = _firings(ui, ogre, clover)
    assert firing.owner is gabriel and firing.target is ogre
    assert firing.mode is TriggerMode.ASK
    assert firing.question == (
        "Ogre makes an attack roll against Clover: use Warding Flare? Warding"
        " Flare. 4 of 4 uses left. Check: if you can see it within 30 feet of"
        " you."
    )


def test_and_as_it_attacks_gabriel_himself(party):
    ui, gabriel, _, ogre = party
    (firing,) = _firings(ui, ogre, gabriel)
    assert firing.owner is gabriel


def test_not_as_an_ally_attacks_an_enemy(party):
    ui, _, clover, ogre = party
    assert _firings(ui, clover, ogre) == []


def test_not_with_the_reaction_used(party):
    ui, gabriel, clover, ogre = party
    gabriel["action_uses"] = {"Reaction": 1}
    assert _firings(ui, ogre, clover) == []


def test_not_while_incapacitated(party):
    ui, gabriel, clover, ogre = party
    gabriel["conditions"] = ["Stunned"]
    assert _firings(ui, ogre, clover) == []


def test_not_with_no_uses_left(party):
    ui, gabriel, clover, ogre = party
    gabriel["feature_uses_used"] = {FLARE: 4}
    assert _firings(ui, ogre, clover) == []


# ---------------------------------------------------------------------------
# The window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    """Stands in for the pop-up: records each question, gives `answer`."""

    def __init__(self, answer: str = "apply"):
        self.answer = answer
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.row.name for f in firings])
        if self.answer == "apply":
            return TriggerChoice(apply=tuple(firings))
        return TriggerChoice()


@pytest.fixture
def fight(party, monkeypatch):
    ui, gabriel, clover, ogre = party
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    # Clover's Shield isn't what's tested: her Reaction is spent.
    clover["action_uses"] = {"Reaction": 1}
    return ui, gabriel, clover, ogre, answers


def _dice(monkeypatch, *rolls: int):
    """randint gives `rolls` in turn, then 1s (the damage dice)."""
    left = list(rolls)
    monkeypatch.setattr(random, "randint", lambda a, b: left.pop(0) if left else 1)


CLUB = parse_action(
    {
        "name": "Greatclub",
        "description": "Melee Attack Roll: +6, reach 5 ft. Hit: 13 (2d8 + 4)"
        " Bludgeoning damage.",
    }
)


def _log(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def test_a_monster_buttons_roll_has_disadvantage_once_flared(fight, monkeypatch):
    ui, gabriel, clover, ogre, answers = fight
    ui._set_targets([clover])
    _dice(monkeypatch, 18, 3)  # the lower is kept: 3 + 6 = 9 against AC 18
    ui._use_monster_action(ogre, CLUB)
    assert answers.asked == [[FLARE]]
    assert "MISS" in ui._action_result_label.text()
    assert gabriel["action_uses"]["Reaction"] == 1
    assert gabriel["feature_uses_used"] == {FLARE: 1}
    assert FLARE not in ogre.get("conditions", [])  # used up by the roll
    assert "Ogre's Warding Flare is used up" in _log(ui)


def test_one_undo_takes_back_the_roll_and_the_flare(fight, monkeypatch):
    ui, _, clover, _, _ = fight
    ui._set_targets([clover])
    ogre = ui._find_character_by_name("Ogre")
    _dice(monkeypatch, 18, 3)
    ui._use_monster_action(ogre, CLUB)
    ui._undo_last()
    gabriel = ui._find_character_by_name("Gabriel Greybeard")
    assert not gabriel.get("feature_uses_used")
    assert (gabriel.get("action_uses") or {}).get("Reaction", 0) == 0


def test_skipped_the_roll_is_as_it_was(fight, monkeypatch):
    ui, gabriel, clover, ogre, answers = fight
    answers.answer = "skip"
    ui._set_targets([clover])
    _dice(monkeypatch, 18, 3)  # Neutral keeps the first: 18 + 6 = 24
    ui._use_monster_action(ogre, CLUB)
    assert "HIT" in ui._action_result_label.text()
    assert not gabriel.get("feature_uses_used")
    assert "Gabriel Greybeard didn't use Warding Flare on Ogre" in _log(ui)


def test_with_the_setting_off_nothing_is_asked(fight, monkeypatch):
    ui, _, clover, ogre, answers = fight
    ui.settings = replace(ui.settings, ask_triggers=False)
    ui._set_targets([clover])
    _dice(monkeypatch, 18, 3)
    ui._use_monster_action(ogre, CLUB)
    assert answers.asked == []


def _ogres_club(ogre):
    (option,) = [
        o
        for _, options in effect_options(ogre, ())
        for o in options
        if o.name == "Greatclub"
    ]
    return option


def _dialog_club(ui, ogre, **changes):
    ui._apply_custom_effect(
        CustomEffect(
            name="Greatclub",
            damage=[(13, "Bludgeoning")],
            attack_bonus=6,
            pick=_ogres_club(ogre),
            **changes,
        )
    )


def test_the_dialogs_roll_has_disadvantage_once_flared(fight, monkeypatch):
    ui, gabriel, clover, ogre, answers = fight
    ui._set_targets([clover])
    hp = clover["hp"]
    _dice(monkeypatch, 18, 3)
    _dialog_club(ui, ogre)
    assert answers.asked == [[FLARE]]
    assert clover["hp"] == hp  # 9 misses
    assert gabriel["feature_uses_used"] == {FLARE: 1}


def test_a_roll_typed_into_the_dialog_isnt_asked_about(fight, monkeypatch):
    ui, _, clover, ogre, answers = fight
    ui._set_targets([clover])
    attack = parse_attack_roll("20")
    assert attack is not None
    _dialog_club(ui, ogre, typed_attacks={id(clover): attack})
    assert answers.asked == []
