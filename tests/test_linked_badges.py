"""A spell's or feature's own badge beside the rules conditions it gives
(Notes/combat-effects-plan.md, R125-R126): Friends gives Charmed, and the
card shows "Friends" too, with the spell's card, so it says where the Charmed
is from; Turn Undead gives Frightened and Incapacitated and a "Turn Undead"
badge with the feature's card. The two are one effect: taking either off
takes the other off. A weapon's or a monster's action gets no badge."""

from dataclasses import replace

import pytest

from Builds.Characters.Y2024_Cleric_Light_GabrielGreybeard import (
    Y2024ClericLightGabrielGreybeardCharacterBuilder as Gabriel,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.effect_options import (
    EffectOption,
    effect_options,
    spell_options,
)
from Combat.CombatUIQt.features_mixin import FEATURE_BADGE_COLOR
from Combat.CombatUIQt.saves import MONSTER_ACTION, WEAPON, CustomEffect
from Combat.Effects.active_effects import (
    FEATURE,
    SPELL,
    find_effect,
    is_linked,
    link_badge,
    linked_badges_left_without,
    linked_conditions,
    new_effect,
    says_something,
)
from tests._combat_ui import make_ui


@pytest.fixture
def fight(tmp_path):
    """A Pirate and a Tiger in a fight, the Tiger targeted."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _friends() -> EffectOption:
    """Friends' row as the picker gives it, spending nothing."""
    (option,) = spell_options(SpellFactory.create("Friends"), None)
    return replace(option, counts_uses=False)


def _cast(ui, option: EffectOption, condition: str | None = None, **kwargs):
    ui._apply_custom_effect(
        CustomEffect(
            name=option.name,
            condition=condition or option.condition,
            pick=option,
            **kwargs,
        )
    )


# ---------------------------------------------------------------------------
# The record


def test_a_badge_stands_for_its_conditions_once_each():
    char: dict = {"name": "Tiger", "conditions": []}
    link_badge(char, "Friends", ["Charmed", "Charmed", "Friends"])
    assert linked_conditions(char, "Friends") == ["Charmed"]
    assert is_linked(char, "Charmed")
    assert not is_linked(char, "Friends")


def test_a_badge_left_standing_for_nothing_is_named():
    char: dict = {"name": "Tiger", "conditions": []}
    link_badge(char, "Turn Undead", ["Frightened", "Incapacitated"])
    assert linked_badges_left_without(char, "Frightened") == []
    assert linked_badges_left_without(char, "Incapacitated") == ["Turn Undead"]


def test_a_link_is_something_to_keep_and_an_old_record_has_none():
    effect = new_effect("Friends")
    assert "linked" not in effect
    assert not says_something(effect)
    effect["linked"] = ["Charmed"]
    assert says_something(effect)
    assert linked_conditions({"active_effects": [new_effect("Friends")]}, "X") == []


# ---------------------------------------------------------------------------
# In the combat window


def test_friends_gives_charmed_and_a_badge_with_its_card(fight):
    ui, _, tiger = fight
    _cast(ui, _friends())
    assert tiger["conditions"] == ["Charmed", "Friends"]
    badge = find_effect(tiger, "Friends")
    assert badge is not None
    assert badge.get("linked") == ["Charmed"]
    assert badge["tooltip_from"] == SPELL
    assert "friendship" in (badge["tooltip"] or "")
    assert badge["source"] == "Friends"


def test_the_badge_is_not_one_more_condition_in_the_stats(fight):
    ui, _, tiger = fight
    _cast(ui, _friends())
    assert tiger["stats"]["conditions_received"] == 1
    assert "Friends" not in tiger["stats"].get("conditions_received_by_name", {})


@pytest.mark.parametrize("taken_off", ["Charmed", "Friends"])
def test_taking_either_off_takes_both_off_and_undo_brings_both_back(fight, taken_off):
    ui, _, tiger = fight
    _cast(ui, _friends())
    ui._remove_condition_from(tiger, taken_off)
    assert tiger["conditions"] == []
    assert find_effect(tiger, "Friends") is None
    assert find_effect(tiger, "Charmed") is None
    ui._undo_last()
    assert tiger["conditions"] == ["Charmed", "Friends"]


def test_the_badge_goes_with_the_last_of_several_conditions(fight):
    ui, _, tiger = fight
    _cast(ui, _friends(), "Frightened + Incapacitated")
    assert tiger["conditions"] == ["Frightened", "Incapacitated", "Friends"]
    ui._remove_condition_from(tiger, "Frightened")
    assert tiger["conditions"] == ["Incapacitated", "Friends"]
    ui._remove_condition_from(tiger, "Incapacitated")
    assert tiger["conditions"] == []


def test_taking_the_badge_off_takes_off_all_it_stands_for(fight):
    ui, _, tiger = fight
    _cast(ui, _friends(), "Frightened + Incapacitated")
    ui._remove_condition_from(tiger, "Friends")
    assert tiger["conditions"] == []


def test_a_condition_another_badge_stands_for_stays(fight):
    ui, _, tiger = fight
    _cast(ui, _friends())
    charm = replace(_friends(), name="Charm Person", spell_name="Charm Person")
    _cast(ui, charm)
    assert tiger["conditions"] == ["Charmed", "Friends", "Charm Person"]
    ui._remove_condition_from(tiger, "Friends")
    assert tiger["conditions"] == ["Charmed", "Charm Person"]
    ui._remove_condition_from(tiger, "Charmed")
    assert tiger["conditions"] == []


def test_a_condition_given_by_hand_before_isnt_the_spells_to_take(fight):
    ui, _, tiger = fight
    ui._add_condition_to(tiger, "Charmed")
    _cast(ui, _friends())
    assert tiger["conditions"] == ["Charmed"]


def test_ending_the_concentration_ends_both(fight):
    ui, pirate, tiger = fight
    ui._select_character(pirate)
    _cast(ui, _friends(), concentration=True)
    assert "Concentrating" in pirate["conditions"]
    ui._remove_condition_from(pirate, "Concentrating")
    assert tiger["conditions"] == []


def test_a_successful_save_gives_neither(fight, monkeypatch):
    ui, _, tiger = fight
    monkeypatch.setattr("random.randint", lambda a, b: b)
    _cast(ui, _friends(), ability="WIS", dc=5)
    assert tiger["conditions"] == []


def test_a_spell_whose_badge_is_its_name_gets_no_second_one(fight):
    ui, _, tiger = fight
    bless = EffectOption(name="Bless", kind=SPELL, condition="Bless")
    _cast(ui, bless)
    assert tiger["conditions"] == ["Bless"]


def test_a_spell_giving_only_its_own_badges_gets_none_more(fight):
    ui, _, tiger = fight
    _cast(ui, replace(_friends(), condition="Hexed"))
    assert tiger["conditions"] == ["Hexed"]


def test_an_effect_typed_by_hand_gets_no_badge(fight):
    ui, _, tiger = fight
    ui._apply_custom_effect(CustomEffect(name="Friends", condition="Charmed"))
    assert tiger["conditions"] == ["Charmed"]


# ---------------------------------------------------------------------------
# A feature's badge (R126)


@pytest.fixture
def cleric_fight(tmp_path):
    """Gabriel (Light Domain Cleric) and a Tiger, on Gabriel's turn."""
    ui = make_ui(tmp_path, [Tiger()], [Gabriel().build()])
    gabriel, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(gabriel)
    ui._select_target_character(tiger)
    return ui, gabriel, tiger


def _turn_undead(gabriel) -> EffectOption:
    features = dict(effect_options(gabriel, all_spells=[]))["Features"]
    (option,) = [o for o in features if o.name == "Turn Undead"]
    return replace(option, counts_uses=False)


def test_turn_undead_gives_its_badge_with_the_features_card(cleric_fight):
    ui, gabriel, tiger = cleric_fight
    _cast(ui, _turn_undead(gabriel))
    assert tiger["conditions"] == ["Frightened", "Incapacitated", "Turn Undead"]
    badge = find_effect(tiger, "Turn Undead")
    assert badge is not None
    assert badge.get("linked") == ["Frightened", "Incapacitated"]
    assert badge["tooltip_from"] == FEATURE
    assert badge["color"] == FEATURE_BADGE_COLOR
    assert "Turn Undead" in (badge["tooltip"] or "")
    assert tiger["stats"]["conditions_received"] == 2


def test_taking_the_features_badge_off_takes_its_conditions_off(cleric_fight):
    ui, gabriel, tiger = cleric_fight
    _cast(ui, _turn_undead(gabriel))
    ui._remove_condition_from(tiger, "Turn Undead")
    assert tiger["conditions"] == []
    ui._undo_last()
    assert tiger["conditions"] == ["Frightened", "Incapacitated", "Turn Undead"]


def test_the_features_badge_goes_with_the_last_condition(cleric_fight):
    ui, gabriel, tiger = cleric_fight
    _cast(ui, _turn_undead(gabriel))
    ui._remove_condition_from(tiger, "Incapacitated")
    assert tiger["conditions"] == ["Frightened", "Turn Undead"]
    ui._remove_condition_from(tiger, "Frightened")
    assert tiger["conditions"] == []


@pytest.mark.parametrize("kind", [MONSTER_ACTION, WEAPON])
def test_a_monsters_action_or_a_weapon_gets_no_badge(fight, kind):
    ui, _, tiger = fight
    _cast(ui, EffectOption(name="Tree Club: Prone", kind=kind, condition="Prone"))
    assert tiger["conditions"] == ["Prone"]
