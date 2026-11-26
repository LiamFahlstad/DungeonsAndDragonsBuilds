"""The strikes used right after a hit (Notes/combat-effects-plan.md, step 9.1):
each is asked about as the hit lands, not picked by hand, and its dice are
rolled twice on a Critical Hit by themselves.

Expected values are the rules text's:

- Sneak Attack (Rogue 1): "Once per turn, you can deal an extra 1d6 damage
  to one creature you hit with an attack roll if you have Advantage on the
  roll and the attack uses a Finesse or a Ranged weapon", or an ally is
  within 5 feet of it; "(Rogue level + 1) / 2" d6.
- Divine Smite: "a Bonus Action, which you take immediately after hitting
  a target with a Melee weapon or an Unarmed Strike".
- Ensnaring Strike: "immediately after hitting a creature with a weapon";
  "While Restrained, the target takes 1d6 Piercing damage at the start of
  each of its turns."
- Stunning Strike (Monk 5): "Once per turn when you hit a creature with a
  Monk weapon or an Unarmed Strike, you can expend 1 Focus Point ... a
  Constitution saving throw. On a failed save, the target has the Stunned
  condition until the start of your next turn. On a successful save, the
  target's Speed is halved until the start of your next turn, and the next
  attack roll made against the target before then has Advantage."
- Rules Glossary, Critical Hit: "roll the attack's damage dice twice".
"""

import random
from typing import cast

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Rogue_ArcaneTrickster_ThumSchtock import (
    Y2024RogueArcaneTricksterThumSchtockCharacterBuilder as Thum,
)
from CharacterContent.Features.ClassFeatures.Monk.MonkFeatures import StunningStrike
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Effects.triggers import TriggerChoice
from Combat.Fight.attack_rolls import parse_attack_roll
from Combat.Fight.effect_options import ATTACKS, effect_options
from Combat.Fight.saves import ATTACK_ROLL, CustomEffect
from Combat.Monsters.CR_2.monsters import Ogre
from Core.Definitions import Ability, CharacterClass, Condition, DamageType
from Model.Content.CombatEffect import EffectRoll
from Model.Content.CombatModifiers import (
    AttackKind,
    AttacksAgainst,
    AtTurnStart,
    RollMode,
    Speed,
)
from Model.Content.CombatTriggers import TriggerEvent
from Model.View import CharacterView
from tests._combat_ui import make_ui

# ---------------------------------------------------------------------------
# What each says


def test_divine_smite_is_asked_after_a_melee_hit():
    effects = SpellFactory.create("Divine Smite").combat_effects()
    assert effects is not None
    (effect,) = effects
    assert effect.trigger is not None
    assert (effect.trigger.event, effect.trigger.attacks) == (
        TriggerEvent.HIT,
        AttackKind.MELEE,
    )
    assert effect.trigger.optional


def test_ensnaring_strike_is_asked_after_a_weapon_hit_and_hurts_each_turn():
    effects = SpellFactory.create("Ensnaring Strike").combat_effects()
    assert effects is not None
    cast, damage = effects
    assert cast.trigger is not None
    assert (cast.trigger.event, cast.trigger.attacks) == (
        TriggerEvent.HIT,
        AttackKind.WEAPON,
    )
    restrained, badge = cast.conditions
    assert restrained.name == Condition.RESTRAINED
    assert badge.modifiers == (AtTurnStart("Ensnaring Strike: damage"),)
    assert damage.name == "Ensnaring Strike: damage"
    ((dice, kind),) = [(d.dice, d.damage_type) for d in damage.damage]
    assert (dice, kind, damage.damage[0].upcast) == ("1d6", DamageType.PIERCING, "1d6")
    assert not damage.spends_use


def test_stunning_strike_stuns_on_a_failed_save_once_per_turn():
    failed, saved = StunningStrike().combat_effects(cast(CharacterView, None))
    assert (failed.roll, failed.save_ability) == (EffectRoll.SAVE, Ability.CONSTITUTION)
    (stunned,) = failed.conditions
    assert stunned.name == Condition.STUNNED
    assert failed.trigger is not None and failed.trigger.once_per_turn
    assert failed.trigger.attacks is AttackKind.MELEE
    # On a success: Speed halved, and the next attack against it has Advantage.
    (badge,) = saved.conditions
    assert badge.modifiers == (
        Speed(multiplier=0.5),
        AttacksAgainst(RollMode.ADVANTAGE, once=True),
    )
    assert not saved.spends_use and saved.trigger is None


# ---------------------------------------------------------------------------
# In the window: Thum's Sneak Attack


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    """Stands in for the trigger pop-up: applies what it's asked."""

    def __init__(self):
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.row.name for f in firings])
        return TriggerChoice(apply=tuple(firings))


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Thum (20) against an Ogre (10, AC 11), on Thum's turn, every die a 1."""
    sheet = Thum().build()
    ui = make_ui(tmp_path, [Ogre()], [sheet])
    thum, ogre = ui.characters
    for char, value in zip(ui.characters, (20, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(thum)
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    dice = (sheet.get_class_level(CharacterClass.ROGUE) + 1) // 2
    return ui, thum, ogre, answers, dice


def _weapon_hit(ui, thum, ogre, roll: str):
    """The Use / Cast dialog's Apply of Thum's first weapon, its attack roll
    typed in, 5 Piercing on a hit."""
    row, *_ = [o for o in dict(effect_options(thum))[ATTACKS] if o.roll == ATTACK_ROLL]
    attack = parse_attack_roll(roll)
    assert attack is not None
    ui._set_targets([ogre])
    ui._apply_custom_effect(
        CustomEffect(
            name=row.name,
            damage=[(5, "Piercing")],
            critical_damage=[(5, "Piercing")],
            attack_bonus=row.bonus,
            typed_attacks={id(ogre): attack},
            pick=row,
            weapon_attack=True,
        )
    )


def test_a_weapon_hit_asks_about_sneak_attack_and_deals_its_dice(fight):
    ui, thum, ogre, answers, dice = fight
    hp = ogre["hp"]
    _weapon_hit(ui, thum, ogre, "18")
    assert ["Sneak Attack"] in answers.asked
    assert ogre["hp"] == hp - 5 - dice  # each d6 a 1


def test_a_critical_hit_rolls_sneak_attacks_dice_twice(fight):
    ui, thum, ogre, answers, dice = fight
    hp = ogre["hp"]
    _weapon_hit(ui, thum, ogre, "nat 20")
    assert ["Sneak Attack"] in answers.asked
    assert ogre["hp"] == hp - 5 - 2 * dice


def test_sneak_attack_is_asked_once_a_turn(fight):
    ui, thum, ogre, answers, _ = fight
    _weapon_hit(ui, thum, ogre, "18")
    _weapon_hit(ui, thum, ogre, "18")
    assert [names for names in answers.asked if "Sneak Attack" in names] == [
        ["Sneak Attack"]
    ]
