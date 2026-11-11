"""What a lasting effect changes on its bearer while it's on (plan Phase 7,
steps 7.1 and 7.2): its AC worked out from a new base (Mage Armor) or kept
at a floor (Barkskin) beside what adds to it (Shield of Faith, cover), and
damage Immunity and Vulnerability beside Resistance (Stoneskin, Protection
from Energy, Rage). Expected values come from the 2024 rules text: Mage
Armor ("the target's base AC becomes 13 plus its Dexterity modifier"),
Barkskin ("the target has an Armor Class of 17 if its AC is lower than
that"), Shield of Faith ("a +2 bonus to AC"), Rage ("Resistance to
Bludgeoning, Piercing, and Slashing damage", "Advantage on Strength checks
and Strength saving throws") and the Rules Glossary: Combining Game Effects
(the same effect twice doesn't add up), Cover (+2 / +5 to AC) and Damage
Resistance and Vulnerability (Resistance halves, then Vulnerability
doubles; Immunity takes none)."""

import random
from typing import Any

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import Rage
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.player_view import note_damage_defense
from Combat.CombatUIQt.saves import CustomEffect
from Combat.Effects.active_effects import KEY, give_modifiers, new_effect
from Combat.Effects.modifiers import (
    armor_class,
    armor_class_bonus,
    armor_class_notes,
    immune_to_damage,
    resists,
    save_plan,
    vulnerable_to,
)
from Core.Definitions import Ability, DamageType
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatModifiers import (
    ArmorClass,
    ArmorClassBase,
    ArmorClassMinimum,
    DamageImmunity,
    Note,
    Resistance,
    Vulnerability,
    modifier_from_dict,
    modifier_to_dict,
)
from Model.Creatures.Combatants import Visibility
from tests._combat_ui import make_ui

MAGE_ARMOR = ArmorClassBase(13, (Ability.DEXTERITY,))
BARKSKIN = ArmorClassMinimum(17)
SHIELD_OF_FAITH = ArmorClass(2)
HALF = Visibility.HALF_COVER.value
FIRE, POISON, SLASHING = (
    DamageType.FIRE.value,
    DamageType.POISON.value,
    DamageType.SLASHING.value,
)


def _with(badges: dict, **keys: Any) -> dict:
    """A combatant (the Tiger) with each badge in `badges` giving its
    modifiers, and `keys` too."""
    char = {"name": "Tiger", "conditions": list(badges), **keys}
    for badge, modifiers in badges.items():
        give_modifiers(char, badge, modifiers)
    return char


def _effects(spell: str) -> list[CombatEffect]:
    effects = SpellFactory.create(spell).combat_effects()
    assert effects is not None, f"{spell} has no combat effects"
    return effects


def _badge_modifiers(effect) -> tuple:
    (condition,) = effect.conditions
    return condition.modifiers


# ---------------------------------------------------------------------------
# The new modifiers as plain data
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "modifier, data",
    [
        (
            MAGE_ARMOR,
            {"type": "ArmorClassBase", "base": 13, "abilities": ["Dexterity"]},
        ),
        (BARKSKIN, {"type": "ArmorClassMinimum", "value": 17}),
        (
            DamageImmunity((DamageType.POISON,)),
            {"type": "DamageImmunity", "damage_types": ["Poison"]},
        ),
        (Vulnerability(), {"type": "Vulnerability"}),
    ],
)
def test_the_new_modifiers_read_back_as_written(modifier, data):
    written = modifier_to_dict(modifier)
    assert modifier_from_dict(written) == modifier
    assert written == data


@pytest.mark.parametrize(
    "data",
    [
        {"type": "ArmorClassBase", "base": "13"},
        {"type": "ArmorClassBase", "base": True},
        {"type": "ArmorClassMinimum"},
        {"type": "ArmorClassMinimum", "value": 17, "bonus": 2},
        {"type": "Vulnerability", "damage_types": ["Sonic"]},
    ],
)
def test_a_malformed_one_is_refused(data):
    with pytest.raises(ValueError, match="Invalid modifier"):
        modifier_from_dict(data, "a test")


@pytest.mark.parametrize("value", ["17", 17.0, None])
def test_a_floor_or_base_is_a_whole_number(value):
    with pytest.raises(ValueError, match="whole number"):
        ArmorClassMinimum(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="whole number"):
        ArmorClassBase(value)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 7.1: the AC in use
# ---------------------------------------------------------------------------


def test_mage_armor_gives_13_plus_dex_when_that_is_better():
    """DEX 16 is +3: a creature with AC 12 has 16, one in plate (18) keeps 18."""
    scores = {"Ability Scores": {"DEX": 16}}
    assert armor_class(_with({"Mage Armor": (MAGE_ARMOR,)}, **scores), 12) == 16
    assert armor_class(_with({"Mage Armor": (MAGE_ARMOR,)}, **scores), 18) == 18


def test_mage_armor_without_ability_scores_counts_no_modifier():
    assert armor_class(_with({"Mage Armor": (MAGE_ARMOR,)}), 10) == 13


def test_barkskin_is_a_floor_not_a_bonus():
    """AC 13 becomes 17; Shield of Faith's +2 on 13 is 15, still under 17;
    on 16 it is 18, above it."""
    assert armor_class(_with({"Barkskin": (BARKSKIN,)}), 13) == 17
    both = _with({"Barkskin": (BARKSKIN,), "Shield of Faith": (SHIELD_OF_FAITH,)})
    assert armor_class(both, 13) == 17
    assert armor_class(both, 16) == 18
    assert armor_class(_with({"Barkskin": (BARKSKIN,)}), 19) == 19


def test_cover_adds_to_whatever_the_ac_is():
    char = _with({"Barkskin": (BARKSKIN,)}, visibility_states=[HALF])
    assert armor_class(char, 13) == 19


def test_mage_armor_and_shield_of_faith_add_up():
    char = _with(
        {"Mage Armor": (MAGE_ARMOR,), "Shield of Faith": (SHIELD_OF_FAITH,)},
        **{"Ability Scores": {"DEX": 14}},
    )
    assert armor_class(char, 11) == 17  # 13 + 2, then + 2


def test_the_same_effect_twice_doesnt_add_up():
    """Two records of Shield of Faith (two casters) give +2, not +4."""
    char = {"name": "Tiger", "conditions": ["Shield of Faith"]}
    for _ in range(2):
        effect = new_effect("Shield of Faith")
        effect["modifiers"] = [modifier_to_dict(SHIELD_OF_FAITH)]
        char.setdefault(KEY, []).append(effect)
    assert armor_class(char, 15) == 17


def test_the_bonus_is_what_the_modifiers_add_to_the_stored_ac():
    """What the players' known-AC notes take off a roll (note_attack_roll)."""
    char = _with({"Barkskin": (BARKSKIN,)}, visibility_states=[HALF])
    assert armor_class_bonus(char, 13) == 6
    assert armor_class_bonus(char) == 2, "with no AC, only what adds to one"


def test_a_badge_that_is_off_changes_nothing():
    char = _with({"Barkskin": (BARKSKIN,)})
    char["conditions"].remove("Barkskin")
    assert armor_class(char, 13) == 13


def test_the_dialog_notes_say_what_changes_the_ac():
    char = _with(
        {
            "Mage Armor": (MAGE_ARMOR,),
            "Barkskin": (BARKSKIN,),
            "Shield of Faith": (SHIELD_OF_FAITH,),
        },
        visibility_states=[HALF],
    )
    assert armor_class_notes(char) == [
        "Mage Armor: base AC 13 + DEX",
        "Barkskin: AC at least 17",
        "Shield of Faith: +2 AC",
    ]


def test_the_spells_give_these_badges():
    (mage_armor,) = _effects("Mage Armor")
    assert _badge_modifiers(mage_armor) == (MAGE_ARMOR,)
    (barkskin,) = _effects("Barkskin")
    assert _badge_modifiers(barkskin) == (BARKSKIN,)


# ---------------------------------------------------------------------------
# 7.2: Immunity and Vulnerability beside Resistance
# ---------------------------------------------------------------------------


def test_immunity_and_vulnerability_from_a_badge():
    char = _with(
        {
            "Feast": (DamageImmunity((DamageType.POISON,)),),
            "Cursed": (Vulnerability((DamageType.FIRE,)),),
        }
    )
    assert immune_to_damage(char, POISON) and not immune_to_damage(char, FIRE)
    assert vulnerable_to(char, FIRE) and not vulnerable_to(char, POISON)
    assert vulnerable_to(_with({"Doom": (Vulnerability(),)}), SLASHING)


def test_stoneskin_and_protection_from_energy_resist_their_types():
    (stoneskin,) = _effects("Stoneskin")
    char = _with({"Stoneskin": _badge_modifiers(stoneskin)})
    assert all(resists(char, t) for t in ("Bludgeoning", "Piercing", "Slashing"))
    assert not resists(char, FIRE)
    rows = _effects("Protection from Energy")
    assert [row.name for row in rows] == [
        f"Protection from Energy: {t}"
        for t in ("Acid", "Cold", "Fire", "Lightning", "Thunder")
    ]
    fire = _with({"Protection from Energy": _badge_modifiers(rows[2])})
    assert resists(fire, FIRE) and not resists(fire, "Cold")


class _Barbarian:
    def __init__(self, level: int):
        self.level = level

    def get_class_level(self, character_class) -> int:
        return self.level


def test_rage_resists_weapons_and_gives_strength_advantage():
    (row,) = Rage().combat_effects(_Barbarian(5))  # type: ignore[arg-type]
    (condition,) = row.conditions
    assert condition.name == "Rage"
    assert condition.duration_seconds == 600  # "up to 10 minutes"
    raging = _with({"Rage": condition.modifiers})
    assert resists(raging, SLASHING) and not resists(raging, FIRE)
    assert save_plan(raging, "STR", "Neutral").mode == "Advantage"
    assert save_plan(raging, "DEX", "Neutral").mode == "Neutral"
    notes = [m.text for m in condition.modifiers if isinstance(m, Note)]
    assert "+2 damage on attacks using Strength (Rage Damage)" in notes


# ---------------------------------------------------------------------------
# In the window
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (the source) and a Tiger (the target) at AC 13."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    tiger["ac"] = 13
    return ui, pirate, tiger


def _rolls(monkeypatch, *d20s):
    rolls = iter(d20s)
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))


def test_barkskin_raises_the_ac_an_attack_is_compared_with(fight, monkeypatch):
    """10 + 5 hits AC 13, not Barkskin's 17; the miss shows the AC is above
    13 (the roll without the 4 Barkskin adds), which stays true after."""
    ui, pirate, tiger = fight
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Barkskin"))
    assert ui._target_armor() == 17
    _rolls(monkeypatch, 10, 1)
    ui._apply_custom_effect(
        CustomEffect(damage=[(20, "Fire")], attack_bonus=5, name="Fire Bolt")
    )
    assert tiger["hp"] == tiger["max_hp"]
    assert tiger["ac_above"] == 11
    ui._remove_condition_from(tiger, "Barkskin")
    assert ui._target_armor() == 13


def test_mage_armor_uses_the_targets_dexterity(fight):
    ui, pirate, tiger = fight
    tiger["Ability Scores"] = {**tiger.get("Ability Scores", {}), "DEX": 18}
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Mage Armor"))
    assert ui._target_armor() == 17  # 13 + 4


def test_damage_from_a_badge(fight):
    """Stoneskin halves Slashing (11 -> 5); with a Vulnerability as well it
    is halved, then doubled (11 -> 10); Immunity takes it all."""
    ui, pirate, tiger = fight
    for kind in ("damage_resistances", "damage_vulnerabilities", "damage_immunities"):
        tiger[kind] = []
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Stoneskin"))
    assert ui._damage_type_modifier(tiger, 11, SLASHING) == (5, "resisted")
    assert ui._damage_type_modifier(tiger, 11, FIRE) == (11, None)
    tiger["conditions"].append("Cursed")
    give_modifiers(tiger, "Cursed", (Vulnerability((DamageType.SLASHING,)),))
    assert ui._damage_type_modifier(tiger, 11, SLASHING) == (
        10,
        "resisted and vulnerable",
    )
    tiger["conditions"].append("Feast")
    give_modifiers(tiger, "Feast", (DamageImmunity((DamageType.POISON,)),))
    assert ui._damage_type_modifier(tiger, 11, POISON) == (0, "immune")


def test_players_learn_nothing_from_a_defense_a_badge_gives():
    monster = _with(
        {
            "Stoneskin": (Resistance((DamageType.SLASHING,)),),
            "Feast": (DamageImmunity((DamageType.POISON,)),),
        }
    )
    note_damage_defense(monster, SLASHING, "resisted")
    note_damage_defense(monster, POISON, "immune")
    assert "known_resistances" not in monster
    assert "known_immunities" not in monster
    note_damage_defense(monster, FIRE, "resisted")
    assert monster["known_resistances"] == [FIRE]
