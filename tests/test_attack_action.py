"""The Attack action's attacks and Action Surge (Notes/combat-effects-plan.md,
step 9.3, Decision 22). The simulator doesn't run the action economy; it
fills in what's known: a weapon row opens with Times at its owner's attacks
per Attack action while its Action is unspent, and Action Surge gives that
Action back.

Expected values are the rules text's:

- Extra Attack (Barbarian, Fighter, Monk, Paladin, Ranger 5, and the
  subclasses that grant it): "You can attack twice instead of once whenever
  you take the Attack action on your turn."
- Two Extra Attacks (Fighter 11): "three times instead of once"; Three Extra
  Attacks (Fighter 20): "four times".
- Action Surge (Fighter 2): "On your turn, you can take one additional
  action, except the Magic action."
"""

from typing import Any, cast

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Examples.Y2024_Fighter_ArcaneArcher_SylvaineFarshot import (
    Y2024FighterArcaneArcherSylvaineFarshotCharacterBuilder as Sylvaine,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Features.ClassFeatures.Ranger import RangerFeatures
from CharacterContent.Features.SubClassFeatures.Artificer import (
    ArtificerArmorerFeatures,
    ArtificerBattleSmithFeatures,
)
from CharacterContent.Features.SubClassFeatures.Bard import BardValorFeatures
from CharacterContent.Features.SubClassFeatures.Wizard import (
    WizardBladesingerFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Bard import BardSwordsFeatures
from Combat.Definitions import ActionCost
from Combat.Fight.attack_action import (
    attack_action_cost,
    attacks_per_attack_action,
    give_back_actions,
)
from Combat.Fight.effect_options import FEATURES, ATTACKS, effect_options
from Combat.Fight.saves import ATTACK_ROLL, CustomEffect
from Combat.Monsters.CR_2.monsters import Ogre
from Combat.PlayerCombatant import combatant_from_character
from Model.Content.Feature import Feature
from Model.View import CharacterView
from tests._combat_ui import make_ui

ACTION = ActionCost.ACTION
# These features' counts and rows don't read the character.
NO_SHEET = cast(CharacterView, None)


class _Log:
    """A Logger that keeps the lines."""

    def __init__(self):
        self.lines: list[str] = []

    def log(
        self,
        text: str,
        *,
        note_turn: bool = True,
        character: str | None = None,
        action: str | None = None,
        value: Any = None,
        public: bool = True,
    ) -> bool:
        self.lines.append(text)
        return public


@pytest.fixture(scope="module")
def sylvaine_sheet():
    return Sylvaine().build()


@pytest.fixture
def sylvaine(sylvaine_sheet) -> dict:
    """A Fighter 18: Extra Attack and its extension Two Extra Attacks."""
    return combatant_from_character(sylvaine_sheet)


# ---------------------------------------------------------------------------
# The features


@pytest.mark.parametrize(
    "module",
    [
        BarbarianFeatures,
        FighterFeatures,
        MonkFeatures,
        PaladinFeatures,
        RangerFeatures,
        ArtificerArmorerFeatures,
        ArtificerBattleSmithFeatures,
        BardValorFeatures,
        WizardBladesingerFeatures,
        BardSwordsFeatures,
    ],
)
def test_extra_attack_attacks_twice(module):
    assert module.ExtraAttack().attacks_per_attack_action(NO_SHEET) == 2


def test_the_fighters_later_extra_attacks():
    assert FighterFeatures.TwoExtraAttacks().attacks_per_attack_action(NO_SHEET) == 3
    assert FighterFeatures.ThreeExtraAttacks().attacks_per_attack_action(NO_SHEET) == 4


def test_a_feature_changes_no_attack_count_unless_it_says_so():
    feature = Feature(name="Anything", origin="Test")
    assert feature.attacks_per_attack_action(NO_SHEET) is None
    assert feature.gives_actions == ()


def test_action_surge_gives_back_the_action_and_a_badge_for_the_turn():
    surge = FighterFeatures.ActionSurge()
    assert surge.gives_actions == ("Action",)
    (effect,) = surge.combat_effects(NO_SHEET)
    assert effect.targets_self
    (badge,) = effect.conditions
    assert badge.name == "Action Surge"


# ---------------------------------------------------------------------------
# How many attacks, and what a weapon row costs


def test_an_extension_counts_the_most_attacks(sylvaine):
    """Two Extra Attacks is granted as an extension of Extra Attack, so it's
    found through the sheet, not the plain features."""
    assert attacks_per_attack_action(sylvaine) == 3


def test_a_creature_without_extra_attack_attacks_once():
    assert attacks_per_attack_action({"name": "Tiger"}) == 1


def test_the_first_attack_costs_the_action_and_opens_with_every_attack(sylvaine):
    assert attack_action_cost(sylvaine) == {"action_cost": ACTION, "instances": 3}


def test_after_the_action_one_more_attack_costs_nothing(sylvaine):
    sylvaine["action_uses"] = {ACTION: 1}
    assert attack_action_cost(sylvaine) == {"action_cost": None, "instances": 1}


def _weapon_rows(char: dict):
    rows = dict(effect_options(char))[ATTACKS]
    return [o for o in rows if o.roll == ATTACK_ROLL and o.name == rows[0].name]


def test_the_pickers_weapon_rows_open_at_the_attack_count(sylvaine):
    row, *_ = _weapon_rows(sylvaine)
    assert (row.instances, row.action_cost) == (3, ACTION)
    sylvaine["action_uses"] = {ACTION: 1}
    row, *_ = _weapon_rows(sylvaine)
    assert (row.instances, row.action_cost) == (1, None)


# ---------------------------------------------------------------------------
# Action Surge


def test_action_surge_after_the_action_gives_it_back(sylvaine):
    sylvaine["action_uses"] = {ACTION: 1}
    log = _Log()
    give_back_actions(log, sylvaine, "Action Surge")
    assert sylvaine["action_uses"][ACTION] == 0
    assert log.lines == [
        f"{sylvaine['name']} gets another Action this turn (Action Surge)"
    ]
    # The next Attack action: the Action again, and every attack.
    assert attack_action_cost(sylvaine) == {"action_cost": ACTION, "instances": 3}


def test_action_surge_before_the_action_leaves_two_to_take(sylvaine):
    sylvaine["action_uses"] = {}
    give_back_actions(_Log(), sylvaine, "Action Surge")
    for _ in range(2):  # two Attack actions, each costing the Action
        assert attack_action_cost(sylvaine)["action_cost"] == ACTION
        sylvaine["action_uses"][ACTION] += 1
    assert attack_action_cost(sylvaine) == {"action_cost": None, "instances": 1}


def test_a_feature_that_gives_no_action_gives_none(sylvaine):
    sylvaine["action_uses"] = {ACTION: 1}
    log = _Log()
    give_back_actions(log, sylvaine, "Second Wind")
    assert sylvaine["action_uses"] == {ACTION: 1}
    assert log.lines == []


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


def test_action_surge_picked_in_the_dialog(tmp_path, sylvaine_sheet):
    """Picked after the Attack action: the Action is hers again, the badge
    is on her, and a use is spent."""
    ui = make_ui(tmp_path, [Ogre()], [sylvaine_sheet])
    char, ogre = ui.characters
    for each, value in zip(ui.characters, (20, 5)):
        ui._initiative_inputs[id(each)].setText(str(value))
    ui._start_combat()
    ui._select_character(char)
    char["action_uses"] = {ACTION: 1}
    (surge,) = [
        o for o in dict(effect_options(char))[FEATURES] if o.name == "Action Surge"
    ]
    ui._set_targets([ogre])
    ui._apply_custom_effect(
        CustomEffect(name="Action Surge", condition="Action Surge", pick=surge)
    )
    assert char["action_uses"][ACTION] == 0
    assert "Action Surge" in char["conditions"]
    assert "Action Surge" not in ogre["conditions"]
    log = str(ui._read_log())
    assert f"{char['name']} uses Action Surge" in log
    assert f"{char['name']} gets another Action this turn (Action Surge)" in log
