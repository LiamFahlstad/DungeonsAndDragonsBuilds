"""Distances in triggers in the combat window (Notes/combat-arena-plan.md,
step 27): once the battle map is in use, Fire Shield's "it's within 5 feet
of you" is counted from where the Ogre stands as its Greatclub hits, not
asked."""

import random
from dataclasses import replace

import pytest

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Arena.arena import POSITION_KEY
from Combat.CombatUIQt.effect_options import trigger_option
from Combat.CombatUIQt.monster_actions import parse_action
from Combat.Effects.triggers import TriggerChoice
from Combat.Monsters.CR_2.monsters import Ogre
from tests._combat_ui import make_ui


class Answers:
    """Stands in for the pop-up: records each question and applies them all."""

    def __init__(self):
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        return TriggerChoice(apply=tuple(firings))


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Edmund, with Fire Shield's warm flames, against an Ogre on its turn;
    every die rolls its highest; the map in use."""
    ui = make_ui(tmp_path, [Ogre()], [Edmund().build()])
    for char, value in zip(ui.characters, (10, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    edmund = next(c for c in ui.characters if c["name"].startswith("Edmund"))
    ogre = next(c for c in ui.characters if c["name"].startswith("Ogre"))
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    monkeypatch.setattr(random, "randint", lambda low, high: high)
    option = trigger_option(edmund, "Fire Shield", "Fire Shield: warm")
    assert option is not None
    assert ui._apply_row(edmund, edmund, replace(option, counts_uses=False))
    ui.arena_settings.in_use = True
    edmund[POSITION_KEY] = [4, 5]
    return ui, edmund, ogre, answers


def _greatclub(ui, ogre, edmund):
    ui._select_character(ogre)
    ui._set_targets([edmund])
    club = parse_action(next(a for a in ogre["actions"] if a.name == "Greatclub"))
    ui._roll_action(club, ogre)
    ui._apply_damage_checked()


def test_fire_shield_burns_an_ogre_beside_it_without_asking(fight):
    ui, edmund, ogre, answers = fight
    ogre[POSITION_KEY] = [5, 5]  # Large: its cells beside Edmund's
    hp = ogre["hp"]
    _greatclub(ui, ogre, edmund)
    assert answers.asked == []
    assert ogre["hp"] == hp - 16  # 2d8 at their highest


def test_fire_shield_doesnt_burn_an_ogre_10_feet_off(fight):
    ui, edmund, ogre, answers = fight
    ogre[POSITION_KEY] = [6, 5]  # 10 ft. away (the hit warned past its reach)
    hp = ogre["hp"]
    _greatclub(ui, ogre, edmund)
    assert answers.asked == []
    assert ogre["hp"] == hp
