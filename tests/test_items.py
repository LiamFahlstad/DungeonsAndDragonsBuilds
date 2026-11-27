"""Items in the picker (Notes/combat-effects-plan.md, step 9.8, Decision 24):
an item says what using it does in a fight (Item is a Feature, so its
combat_effects()), and a character's items that do reach the Use / Cast
dialog's picker. Drinking a potion takes a Bonus Action (2024 rules); its
count stays on the sheet.

Expected values are the rules text of the repo's own potions
(CharacterContent/Items/Items/Potions.py):

- Potion of Healing: "You regain 2d4 + 2 Hit Points"; Greater 4d4 + 4,
  Superior 8d4 + 8, Supreme 10d4 + 20.
- Potion of Invisibility: "you become invisible for 1 hour. The effect ends
  if you attack, cast a spell, or become incapacitated."
- Potion of Speed: "+5 feet for 1 hour ... ends early if you become
  incapacitated"; Swiftness and Greater Speed +10.
- Potion of Resistance: "resistance to one non-physical damage type of your
  choice for 1 hour".
- Potion of Guarding: "+2 to your AC until the start of your next turn".
"""

import random
from typing import cast

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder as Kivi,
)
from CharacterContent.Items.Items import Potions
from CharacterContent.Items.Items.Potions import USED_UP
from Combat.Definitions import ActionCost
from Combat.Fight.effect_options import FEATURES, effect_options
from Combat.Fight.picked import picked_effect
from Combat.Monsters.CR_2.monsters import Ogre
from Combat.PlayerCombatant import combatant_from_character
from Core.Definitions import Condition, DamageType
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import TurnEdge, TurnOf
from Model.Content.CombatModifiers import (
    ArmorClass,
    EndEvent,
    EndsWhen,
    Resistance,
    Speed,
)
from Model.Content.Item import Item
from Model.View import CharacterView
from tests._combat_ui import make_ui

NO_SHEET = cast(CharacterView, None)


def _effects(item: Item):
    effects = item.combat_effects(NO_SHEET)
    assert effects is not None
    return effects


@pytest.mark.parametrize(
    "potion, dice",
    [
        (Potions.PotionOfHealing, "2d4 + 2"),
        (Potions.GreaterHealingPotion, "4d4 + 4"),
        (Potions.SuperiorHealingPotion, "8d4 + 8"),
        (Potions.SupremeHealingPotion, "10d4 + 20"),
    ],
)
def test_a_healing_potion_heals_its_dice_as_a_bonus_action(potion, dice):
    (effect,) = _effects(potion())
    assert effect.healing is not None and effect.healing.dice == dice
    assert effect.action_type is ActionType.BONUS_ACTION
    assert USED_UP in effect.notes


def _badge(item: Item, index: int = 0):
    effect = _effects(item)[index]
    assert effect.targets_self and effect.action_type is ActionType.BONUS_ACTION
    return effect.conditions


def test_invisibility_ends_on_an_attack_a_cast_or_incapacitated():
    invisible, badge = _badge(Potions.PotionOfInvisibility())
    assert invisible.name == Condition.INVISIBLE
    assert (invisible.duration_seconds, badge.duration_seconds) == (3600, 3600)
    assert badge.modifiers == (
        EndsWhen((EndEvent.ATTACKS, EndEvent.CASTS_SPELL, EndEvent.INCAPACITATED)),
    )


@pytest.mark.parametrize(
    "potion, feet",
    [
        (Potions.PotionOfSpeed, 5),
        (Potions.GreaterPotionOfSpeed, 10),
        (Potions.PotionOfSwiftness, 10),
    ],
)
def test_speed_potions_add_their_feet_until_incapacitated(potion, feet):
    (badge,) = _badge(potion())
    assert badge.modifiers == (
        Speed(bonus=feet),
        EndsWhen((EndEvent.INCAPACITATED,)),
    )


def test_resistance_is_a_row_per_non_physical_type():
    effects = _effects(Potions.PotionOfResistance())
    kinds = [effect.conditions[0].modifiers for effect in effects]
    assert len(effects) == 9 and len({e.name for e in effects}) == 9
    assert (Resistance((DamageType.FIRE,)),) in kinds
    assert all(
        (Resistance((physical,)),) not in kinds
        for physical in (
            DamageType.BLUDGEONING,
            DamageType.PIERCING,
            DamageType.SLASHING,
        )
    )


def test_guarding_gives_2_ac_until_the_start_of_your_next_turn():
    (badge,) = _badge(Potions.PotionOfGuarding())
    assert badge.modifiers == (ArmorClass(2),)
    assert badge.until == (TurnEdge.START, TurnOf.SOURCE)


def test_an_item_that_says_nothing_has_no_row():
    """Cleansing Potion's "one condition affecting you ends" is the GM's."""
    assert Potions.CleansingPotion().combat_effects(NO_SHEET) is None


# ---------------------------------------------------------------------------
# A character's items in the picker


@pytest.fixture(scope="module")
def kivi_sheet():
    return Kivi().build()


def test_a_characters_described_items_are_picker_rows(kivi_sheet):
    """Kivi carries 2 Potions of Healing, an Invisibility, a Speed and a
    Resistance potion."""
    kivi = combatant_from_character(kivi_sheet)
    assert [item.name for item in kivi["_item_objects"]] == [
        "Potion of Healing",
        "Potion of Invisibility",
        "Potion of Speed",
        "Potion of Resistance",
    ]
    rows = {o.name: o for o in dict(effect_options(kivi))[FEATURES]}
    healing = rows["Potion of Healing"]
    assert healing.action_cost == ActionCost.BONUS_ACTION
    assert healing.damage_at(None) == "2d4 + 2"
    assert "Potion of Resistance: Fire" in rows


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


def test_drinking_a_potion_of_healing_heals_and_spends_the_bonus_action(
    tmp_path, kivi_sheet, monkeypatch
):
    ui = make_ui(tmp_path, [Ogre()], [kivi_sheet])
    kivi = next(c for c in ui.characters if c.get("_is_player"))
    for char in ui.characters:
        ui._initiative_inputs[id(char)].setText("20" if char is kivi else "5")
    ui._start_combat()
    kivi["hp"] = 10
    monkeypatch.setattr(random, "randint", lambda low, high: high)  # 2d4: 8
    row = next(
        o for o in dict(effect_options(kivi))[FEATURES] if o.name == "Potion of Healing"
    )
    effect = picked_effect(row, {})
    assert effect is not None
    ui._select_character(kivi)
    ui._set_targets([kivi])
    ui._apply_custom_effect(effect)
    assert kivi["hp"] == 10 + 8 + 2
    assert kivi["action_uses"][ActionCost.BONUS_ACTION] == 1
    assert f"{kivi['name']} uses Potion of Healing" in str(ui._read_log())
