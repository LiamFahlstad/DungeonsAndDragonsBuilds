"""A badge that answers a hit (WhenHit, plan Q57): Armor of Agathys, "If a
creature hits you with a melee attack roll before the spell ends, the
creature takes 5 Cold damage" (5 more per slot level above 1), and Fire
Shield, "whenever a creature within 5 feet of you hits you with a melee
attack roll, ... The attacker takes 2d8 Fire damage from a warm shield or 2d8
Cold damage from a chill shield"."""

import random
from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellClasses.Level1 import ArmorOfAgathys
from CharacterContent.Spells.SpellClasses.Level4 import FireShield
from Combat.CombatUIQt.effect_options import badge_trigger_row, trigger_option
from Combat.CombatUIQt.monster_actions import parse_action
from Combat.Effects.active_effects import give_modifiers
from Combat.Effects.modifiers import rolled_modifiers
from Combat.Effects.triggers import (
    AttackOutcome,
    TriggerChoice,
    TriggerMode,
    badge_hit_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Core.Definitions import DamageType
from Model.Content.CombatEffect import CombatDamage, CombatEffect
from Model.Content.CombatModifiers import (
    AttackKind,
    Resistance,
    WhenHit,
    modifier_from_dict,
    modifier_to_dict,
)
from tests._combat_ui import make_ui

COLD = "Armor of Agathys: Cold damage"


# ---------------------------------------------------------------------------
# As data


def test_when_hit_reads_back_as_it_was_written():
    modifier = WhenHit("Fire Shield: warm flames", when="it's within 5 feet of you")
    data = modifier_to_dict(modifier)
    assert data == {
        "type": "WhenHit",
        "effect": "Fire Shield: warm flames",
        "when": "it's within 5 feet of you",
    }
    assert modifier_from_dict(data) == modifier
    kept = WhenHit(COLD, levels_up=2)
    assert modifier_from_dict(modifier_to_dict(kept)) == kept


@pytest.mark.parametrize(
    "make",
    [
        lambda: WhenHit(""),
        lambda: WhenHit(COLD, attacks="melee"),  # type: ignore[arg-type]
        lambda: WhenHit(COLD, levels_up=-1),
        lambda: WhenHit(COLD, levels_up=True),
    ],
)
def test_when_hit_is_checked(make):
    with pytest.raises(ValueError):
        make()


def test_a_badge_keeps_the_slot_levels_it_was_cast_with():
    # Armor of Agathys with a level 3 slot: 2 levels above its own.
    kept = rolled_modifiers((WhenHit(COLD), Resistance()), 2, lambda dice: 0)
    assert kept == (WhenHit(COLD, levels_up=2), Resistance())


def test_damage_can_upcast_by_a_number():
    assert CombatDamage("5", DamageType.COLD, upcast="5").upcast == "5"
    with pytest.raises(ValueError):
        CombatDamage("5", DamageType.COLD, upcast="5 more")


def test_the_two_spells_are_described():
    armor = ArmorOfAgathys().combat_effects()
    assert [e.name for e in armor] == ["", COLD]
    assert armor[0].temp_hp is not None and armor[0].temp_hp.upcast == "5"
    assert armor[0].conditions[0].modifiers == (WhenHit(COLD),)
    assert armor[1].spends_use is False
    shield = {e.name: e for e in FireShield().combat_effects()}
    warm, chill = shield["Fire Shield: warm"], shield["Fire Shield: chill"]
    assert warm.conditions[0].modifiers[0] == Resistance((DamageType.COLD,))
    assert chill.conditions[0].modifiers[0] == Resistance((DamageType.FIRE,))
    assert shield["Fire Shield: chill flames"].damage[0].damage_type is DamageType.COLD
    for effect in shield.values():
        CombatEffect.from_dict(effect.to_dict())


# ---------------------------------------------------------------------------
# Which hits it answers


def _with_badge(char: dict, name: str, modifiers, source: str, caster: dict):
    char.setdefault("conditions", []).append(name)
    give_modifiers(char, name, modifiers)
    record = next(e for e in char["active_effects"] if e["name"] == name)
    record["source"], record["caster"] = source, caster["name"]


def _row_of(bearer, record, modifier):
    return badge_trigger_row(bearer, record.get("source"), modifier)


def test_a_melee_hit_is_answered_by_itself_a_ranged_one_not_at_all():
    warlock = {"name": "Warlock", "hp": 20, "max_hp": 20, "conditions": []}
    ogre = {"name": "Ogre", "hp": 59, "max_hp": 59, "conditions": []}
    _with_badge(
        warlock, "Armor of Agathys", (WhenHit(COLD),), "Armor of Agathys", warlock
    )

    def fired(**outcome):
        return badge_hit_firings(AttackOutcome(ogre, warlock, **outcome), _row_of)

    (firing,) = fired(hit=True, kind=AttackKind.MELEE)
    assert firing.owner is warlock and firing.target is ogre
    assert firing.mode is TriggerMode.AUTO and firing.row.name == COLD
    assert firing.row.what == "5 Cold"
    assert fired(hit=True, kind=AttackKind.RANGED) == []
    assert fired(hit=False, kind=AttackKind.MELEE) == []
    # A hit typed in that doesn't say its kind: the GM is asked.
    (unknown,) = fired(hit=True)
    assert unknown.mode is TriggerMode.ASK
    assert unknown.why == "if it was a melee attack"


def test_the_damage_counts_the_slot_it_was_cast_with():
    warlock = {"name": "Warlock", "conditions": []}
    row = badge_trigger_row(warlock, "Armor of Agathys", WhenHit(COLD, levels_up=2))
    assert row is not None and row.what == "5 + 10 Cold"


def test_fire_shield_asks_whether_the_attacker_is_within_5_feet():
    wizard = {"name": "Wizard", "hp": 30, "max_hp": 30, "conditions": []}
    ogre = {"name": "Ogre", "hp": 59, "max_hp": 59, "conditions": []}
    warm = WhenHit("Fire Shield: warm flames", when="it's within 5 feet of you")
    _with_badge(wizard, "Fire Shield", (warm,), "Fire Shield", wizard)
    (firing,) = badge_hit_firings(
        AttackOutcome(ogre, wizard, True, kind=AttackKind.MELEE), _row_of
    )
    assert firing.mode is TriggerMode.ASK
    assert firing.question == (
        "Ogre hits Wizard: use Fire Shield: warm flames? 2d8 Fire."
        " Check: if it's within 5 feet of you."
    )


# ---------------------------------------------------------------------------
# In the window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    """Stands in for the pop-up: records each question and applies them all."""

    def __init__(self):
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        return TriggerChoice(apply=tuple(firings))


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Edmund against an Ogre, on the Ogre's turn; every die rolls its
    highest, so the Greatclub hits."""
    ui = make_ui(tmp_path, [Ogre()], [Edmund().build()])
    for char, value in zip(ui.characters, (10, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    edmund = next(c for c in ui.characters if c["name"].startswith("Edmund"))
    ogre = next(c for c in ui.characters if c["name"].startswith("Ogre"))
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    monkeypatch.setattr(random, "randint", lambda low, high: high)
    return ui, edmund, ogre, answers


def _greatclub(ui, ogre, edmund):
    """The Ogre's Greatclub button rolls the hit into the Damage field, and
    Enter deals it."""
    ui._select_character(ogre)
    ui._set_targets([edmund])
    club = parse_action(next(a for a in ogre["actions"] if a.name == "Greatclub"))
    ui._roll_action(club, ogre)
    ui._apply_damage_checked()


def _give(ui, char, spell: str, row: str, free=False):
    """char casts `spell`'s row `row` on itself, as the Custom Effect dialog
    picked and applied would (a level 1 slot spent for Armor of Agathys;
    `free`: no slot, for a spell char has no slot for)."""
    option = trigger_option(char, spell, row)
    assert option is not None
    if free:
        option = replace(option, counts_uses=False)
    assert ui._apply_row(char, char, option)


def test_the_ogre_takes_5_cold_damage_as_its_greatclub_hits(fight):
    ui, edmund, ogre, answers = fight
    _give(ui, edmund, "Armor of Agathys", "Armor of Agathys")
    assert "Armor of Agathys" in edmund["conditions"]
    assert edmund["temp_hp"] == 5
    hp = ogre["hp"]
    _greatclub(ui, ogre, edmund)
    assert answers.asked == []  # a melee hit: it happens
    assert ogre["hp"] == hp - 5
    # One undo takes the hit's damage back, and the Cold damage with it.
    ui._undo_last()
    assert ogre["hp"] == hp
    assert edmund["hp"] == edmund["max_hp"] and edmund["temp_hp"] == 5


def test_fire_shield_is_asked_and_deals_2d8_fire(fight):
    ui, edmund, ogre, answers = fight
    _give(ui, edmund, "Fire Shield", "Fire Shield: warm", free=True)
    hp = ogre["hp"]
    _greatclub(ui, ogre, edmund)
    assert len(answers.asked) == 1
    assert "use Fire Shield: warm flames? 2d8 Fire." in answers.asked[0][0]
    assert ogre["hp"] == hp - 16  # 2d8 at their highest


@pytest.mark.parametrize(
    "description, kind",
    [
        ("Melee Attack Roll: +6, reach 5 ft. Hit: 13 (2d8 + 4)", AttackKind.MELEE),
        (
            "Ranged Attack Roll: +4, range 80/320 ft. Hit: 5 (1d6 + 2)",
            AttackKind.RANGED,
        ),
        ("Melee or Ranged Attack Roll: +5, reach 5 ft. or range 20/60 ft.", None),
    ],
)
def test_a_monsters_attack_says_whether_it_is_melee(description, kind):
    action = parse_action({"name": "Strike", "description": description})
    assert action.to_hit is not None
    assert action.attack_kind is kind
