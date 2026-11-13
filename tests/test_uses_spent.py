"""A use that spends several of its feature's uses (CombatEffect.uses_spent,
plan Q64): Elemental Burst, "you can expend 2 Focus Points to cause elemental
energy to burst" (Warrior of the Elements Monk 6), spends 2 of Monk's Focus,
its parent's pool, in the picker, the out-of-uses question, the log and the
party's replay."""

from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Examples.Y2024_Monk_Elements_KaidaEmberfist import (
    Y2024MonkElementsKaidaEmberfistCharacterBuilder as Kaida,
)
from Combat.CombatUIQt.effect_options import effect_options
from Combat.CombatUIQt.resources import feature_lack
from Combat.Definitions import Action
from Combat.Monsters.CR_2.monsters import Ogre
from Core.Definitions import DamageType
from Model.Content.CombatEffect import CombatEffect, EffectRoll
from tests._combat_ui import make_ui

FOCUS = "Monk's Focus"
BURST = "Elemental Burst"


def test_uses_spent_reads_back_as_it_was_written():
    effect = CombatEffect(uses_spent=2)
    assert effect.to_dict() == {"uses_spent": 2}
    assert CombatEffect.from_dict({"uses_spent": 2}) == effect
    assert "uses_spent" not in CombatEffect().to_dict()  # 1 is the default


@pytest.mark.parametrize(
    "make",
    [
        lambda: CombatEffect(uses_spent=0),
        lambda: CombatEffect(uses_spent=True),
        lambda: CombatEffect(uses_spent=2, spends_use=False),
        lambda: CombatEffect(name="Free", uses_spent=2, uses_per_long_rest=1),
    ],
)
def test_uses_spent_is_a_count_of_the_features_uses(make):
    with pytest.raises(ValueError):
        make()


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path):
    """Kaida (Monk 17, 17 Focus Points) and an Ogre, between fights."""
    ui = make_ui(tmp_path, [Ogre()], [Kaida().build()])
    kaida = next(c for c in ui.characters if c["name"].startswith("Kaida"))
    ogre = next(c for c in ui.characters if c["name"].startswith("Ogre"))
    return ui, kaida, ogre


def _burst(char, damage_type: DamageType | None = None):
    """char's Elemental Burst row; with `damage_type`, as the dialog's type
    box has it once the GM picks one (Acid, Cold, Fire, Lightning, Thunder)."""
    option = next(
        option
        for _, options in effect_options(char, all_spells=())
        for option in options
        if option.name == BURST
    )
    if damage_type is None:
        return option
    rolls = tuple(replace(roll, damage_type=damage_type.value) for roll in option.rolls)
    return replace(option, rolls=rolls)


def test_elemental_burst_is_a_dexterity_save_for_two_focus_points(fight):
    _, kaida, _ = fight
    burst = _burst(kaida)
    assert burst.feature_name == FOCUS and burst.uses_spent == 2
    assert burst.ability == "DEX"
    # Three rolls of the d12 Martial Arts die at Monk 17, of a type picked.
    assert [roll.dice for roll in burst.rolls] == ["3d12"]
    assert burst.summary.startswith("17/17, 2 a use")
    effect = next(
        e
        for f in kaida["_stat_block"].iter_features_with_extensions()
        if f.name == BURST
        for e in f.combat_effects(kaida["_stat_block"])
    )
    assert effect.roll is EffectRoll.SAVE and effect.half_on_success


def test_using_it_spends_two_and_one_left_isnt_enough(fight):
    ui, kaida, ogre = fight
    assert ui._apply_row(kaida, ogre, _burst(kaida, DamageType.FIRE))
    assert kaida["feature_uses_used"] == {FOCUS: 2}
    assert any(
        event.get("value") == {"feature_name": FOCUS, "count": 2}
        for events in ui._read_log().values()
        if isinstance(events, list)
        for event in events
    )
    kaida["feature_uses_used"] = {FOCUS: 16}
    assert feature_lack(kaida, FOCUS, 2) == f"{FOCUS}: 1 left, 2 needed"
    assert feature_lack(kaida, FOCUS) is None  # Flurry of Blows' 1 is there
    assert _burst(kaida).summary.startswith("1/17, 2 a use")
    assert "2 needed, 1 left." in _burst(kaida).note
    # The picker's own path asks first, so _apply_row refuses it.
    assert not ui._apply_row(kaida, ogre, _burst(kaida, DamageType.FIRE))
    assert kaida["feature_uses_used"] == {FOCUS: 16}


def test_the_party_replay_counts_both(fight, tmp_path):
    ui, kaida, _ = fight
    fresh = make_ui(tmp_path / "fresh", [], [Kaida().build()])
    loaded = fresh.characters[0]
    fresh._apply_replay_action(
        loaded, Action.ENABLE_FEATURE, {"feature_name": FOCUS, "count": 2}
    )
    assert loaded["feature_uses_used"] == {FOCUS: 2}
    # An older log's line, with no count, is one use.
    fresh._apply_replay_action(loaded, Action.ENABLE_FEATURE, {"feature_name": FOCUS})
    assert loaded["feature_uses_used"] == {FOCUS: 3}
