"""Extra damage that comes with a hit (Notes/combat-effects-plan.md, step
3.4): ExtraDamageFrom on a target (Hunter's Mark: "you deal an extra 1d6
Force damage to the target whenever you hit it with an attack roll") and
ExtraDamageOnHit on an attacker (Divine Favor: "your attacks with weapons
deal an extra 1d4 Radiant damage on a hit"), as data, as the interpreter
reads them, and in the rolls the combat window makes.

Expected values come from those two descriptions and the Rules Glossary: a
Critical Hit rolls "all of the attack's damage dice twice"; Resistance halves
"damage of that type" (round down), once to an instance of damage; "a weapon
attack is an attack roll made with a weapon", which an Unarmed Strike isn't
("instead of using a weapon")."""

import json
import random

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTreeWidget,
    QWidget,
)

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import BugbearWarrior, Pirate, Tiger
from Combat.CombatUIQt.monster_actions import DamageRoll, MonsterAction
from Combat.CombatUIQt.saves import (
    ATTACK_ROLL,
    FEATURE,
    SPELL,
    CustomEffect,
    EffectOption,
    roll_extra_damage,
    with_extra_damage,
)
from Combat.Effects.active_effects import find_effect, give_modifiers, note_origin
from Combat.Effects.modifiers import HitPlan, hit_extras, hit_plan
from Combat.EncounterLogs import PUBLIC_KEY
from Core.Definitions import DamageType
from Model.Content.CombatModifiers import (
    AttackKind,
    ExtraDamageFrom,
    ExtraDamageOnHit,
    modifier_from_dict,
    modifier_to_dict,
)
from tests._combat_ui import make_ui, open_dialog

MARK = ExtraDamageFrom("1d6", DamageType.FORCE)
FAVOR = ExtraDamageOnHit("1d4", DamageType.RADIANT, AttackKind.WEAPON)


def _with_badge(name: str, badge: str, modifier, caster: str | None = None) -> dict:
    char = {"name": name, "conditions": [badge]}
    give_modifiers(char, badge, (modifier,))
    note_origin(char, badge, source=badge, caster=caster)
    return char


# ---------------------------------------------------------------------------
# As data


@pytest.mark.parametrize(
    "modifier",
    [
        MARK,
        FAVOR,
        ExtraDamageFrom("1d6", DamageType.NECROTIC, when="it's the Hex's target"),
        ExtraDamageOnHit("2", DamageType.SLASHING),
    ],
)
def test_extra_damage_reads_back_as_it_was_written(modifier):
    data = modifier_to_dict(modifier)
    assert json.loads(json.dumps(data)) == data
    assert modifier_from_dict(data) == modifier


def test_extra_damage_is_written_with_only_what_isnt_default():
    assert modifier_to_dict(MARK) == {
        "type": "ExtraDamageFrom",
        "amount": "1d6",
        "damage_type": "Force",
    }
    assert modifier_to_dict(FAVOR) == {
        "type": "ExtraDamageOnHit",
        "amount": "1d4",
        "damage_type": "Radiant",
        "attacks": "weapon attack",
    }


@pytest.mark.parametrize(
    "data",
    [
        {"type": "ExtraDamageFrom", "amount": "1d6"},  # no damage type
        {"type": "ExtraDamageFrom", "damage_type": "Force"},  # no amount
        {"type": "ExtraDamageFrom", "amount": "1d6", "damage_type": "Forse"},
        {"type": "ExtraDamageFrom", "amount": "1d6", "damage_type": ["Force"]},
        {"type": "ExtraDamageFrom", "amount": "d6", "damage_type": "Force"},
        {"type": "ExtraDamageFrom", "amount": "-1d6", "damage_type": "Force"},
        {"type": "ExtraDamageFrom", "amount": "0", "damage_type": "Force"},
        {"type": "ExtraDamageFrom", "amount": 6, "damage_type": "Force"},
        {"type": "ExtraDamageFrom", "amount": "1d6", "damage_type": "Force", "x": 1},
        {
            "type": "ExtraDamageOnHit",
            "amount": "1d4",
            "damage_type": "Radiant",
            "attacks": "weapons",
        },
        {"type": "ExtraDamage", "amount": "1d4", "damage_type": "Radiant"},
    ],
)
def test_extra_damage_that_isnt_one_is_refused(data):
    with pytest.raises(ValueError, match="Invalid modifier of Hunter's Mark"):
        modifier_from_dict(data, "Hunter's Mark")


@pytest.mark.parametrize(
    "make",
    [
        lambda: ExtraDamageFrom("1d6", "Force"),  # pyright: ignore[reportArgumentType]
        lambda: ExtraDamageOnHit("1d6+2", DamageType.FORCE),
        lambda: ExtraDamageOnHit(
            "1d4",
            DamageType.RADIANT,
            "weapon attack",  # pyright: ignore[reportArgumentType]
        ),
    ],
)
def test_extra_damage_that_cant_be_is_refused_in_python(make):
    with pytest.raises(ValueError):
        make()


def _badge(spell: str):
    effects = SpellFactory.create(spell).combat_effects()
    assert effects is not None
    (effect,) = effects
    (condition,) = effect.conditions
    return condition


def test_hunters_mark_and_divine_favor_say_what_their_badges_do():
    mark = _badge("Hunter's Mark")
    assert (mark.name, mark.modifiers) == ("Hunter's Mark", (MARK,))
    favor = _badge("Divine Favor")
    assert (favor.name, favor.modifiers) == ("Divine Favor", (FAVOR,))


# ---------------------------------------------------------------------------
# What a hit deals besides its own damage


def test_hunters_mark_adds_to_its_casters_hits_only():
    tiger = _with_badge("Tiger", "Hunter's Mark", MARK, caster="Hanna")
    hanna, drake = {"name": "Hanna", "conditions": []}, {"name": "Drake"}
    assert hit_plan(hanna, tiger, None) == HitPlan(
        (("Hanna's Hunter's Mark", "1d6", "Force"),)
    )
    assert hit_plan(drake, tiger, True) == HitPlan()
    assert hit_plan(None, tiger, True) == HitPlan(), "no attacker, no caster"
    assert hit_plan(hanna, None, True) == HitPlan(), "a target unknown"


def test_a_mark_with_no_caster_adds_nothing():
    tiger = _with_badge("Tiger", "Hunter's Mark", MARK)
    assert hit_plan({"name": "Hanna"}, tiger, True) == HitPlan()


def test_extra_damage_counts_only_while_its_badge_is_on():
    tiger = _with_badge("Tiger", "Hunter's Mark", MARK, caster="Hanna")
    tiger["conditions"] = []
    assert hit_extras({"name": "Hanna"}, tiger) == []


def test_divine_favor_adds_to_weapon_hits_and_notes_one_it_cant_tell():
    edmund = _with_badge("Edmund", "Divine Favor", FAVOR, caster="Edmund")
    weapon = hit_plan(edmund, None, True)
    assert weapon.extras == (("Edmund's Divine Favor", "1d4", "Radiant"),)
    assert hit_plan(edmund, None, False) == HitPlan(), "an Unarmed Strike, a spell"
    unknown = hit_plan(edmund, None, None)
    assert unknown.extras == ()
    assert unknown.notes == (
        "Edmund's Divine Favor (not counted): +1d4 Radiant on a weapon hit",
    )


def test_extra_damage_with_a_when_is_noted_not_counted():
    when = ExtraDamageOnHit("2", DamageType.SLASHING, when="it uses Strength")
    barbarian = _with_badge("Bror", "Rage", when, caster="Bror")
    assert hit_plan(barbarian, None, True) == HitPlan(
        (), ("Bror's Rage (not counted): +2 Slashing on a hit if it uses Strength",)
    )


def _dice(monkeypatch, d20s=(), **dice):
    """random.randint gives these: each d20 (two an attack roll), then the
    dice of each size given (d6s=..., d4s=...), in order."""
    d20 = iter(d20s)
    others = {int(k[1:-1]): iter(v) for k, v in dice.items()}
    monkeypatch.setattr(
        random,
        "randint",
        lambda low, high: next(d20) if high == 20 else next(others[high]),
    )


def test_a_critical_hit_doubles_the_extra_dice_not_a_number(monkeypatch):
    plan = HitPlan((("Hunter's Mark", "1d6", "Force"), ("Rage", "2", "Slashing")))
    _dice(monkeypatch, d6s=(3, 5))
    parts, lines = roll_extra_damage(plan, critical=True)
    assert parts == [(8, "Force"), (2, "Slashing")]
    assert lines == (
        "Hunter's Mark: +8 Force (2d6, critical hit)",
        "Rage: +2 Slashing",
    )


def test_no_extra_damage_rolls_nothing(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda *a: pytest.fail("rolled"))
    assert roll_extra_damage(HitPlan(), critical=True) == ([], ())


def test_extra_damage_joins_the_hits_damage_of_its_type():
    """Resistance halves a type's damage once, as one instance."""
    damage = [(7, "Slashing"), (3, "Radiant")]
    assert with_extra_damage(damage, [(2, "Radiant"), (4, "Force")]) == [
        (7, "Slashing"),
        (5, "Radiant"),
        (4, "Force"),
    ]
    assert with_extra_damage(damage, []) is damage


# ---------------------------------------------------------------------------
# In the window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15, the source), a Tiger (10, the target, AC 15) and a
    Bugbear Warrior (5), another attacker."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), BugbearWarrior()])
    pirate, tiger, bugbear = ui.characters
    for char, value in zip(ui.characters, (15, 10, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(pirate)
    ui._set_targets([tiger])
    tiger["ac"] = 15
    return ui, pirate, tiger, bugbear


def _events(ui) -> list[str]:
    return [event["text"] for event in ui._read_log()["round_1"]]


def _new_events(ui, before: int) -> list[str]:
    return [line.split("] ", 1)[-1] for line in _events(ui)[before:]]


def _cast(ui, caster, spell: str, *targets):
    ui._select_character(caster)
    ui._set_targets(list(targets))
    ui._apply_cast_spell(SpellFactory.create(spell))


def _mark(ui, pirate, tiger):
    """The Pirate casts Hunter's Mark on the Tiger, and targets it."""
    _cast(ui, pirate, "Hunter's Mark", tiger)
    ui._set_targets([tiger])


def _attack(**kwargs) -> CustomEffect:
    """+5 to hit and 5 Slashing damage, 9 on a Critical Hit."""
    fields = {
        "name": "Scimitar",
        "damage": [(5, "Slashing")],
        "critical_damage": [(9, "Slashing")],
        "attack_bonus": 5,
    }
    return CustomEffect(**{**fields, **kwargs})


def test_cast_hunters_mark_puts_its_extra_damage_on_its_target(fight):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    effect = find_effect(tiger, "Hunter's Mark")
    assert effect is not None
    assert (effect["caster"], effect["modifiers"]) == (
        "Pirate",
        [modifier_to_dict(MARK)],
    )


def test_hunters_mark_adds_1d6_force_to_its_casters_hit(fight, monkeypatch):
    """15 + 5 hits AC 15: 5 Slashing, and the mark's 4 Force."""
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    before = len(_events(ui))
    _dice(monkeypatch, d20s=(15, 1), d6s=(4,))
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5 - 4
    lines = _new_events(ui, before)
    hit = next(i for i, line in enumerate(lines) if "attack roll of 20 hits" in line)
    assert lines[hit + 1 : hit + 4] == [
        "Pirate's Hunter's Mark: +4 Force (1d6)",
        "Tiger takes 5 Slashing damage from Pirate",
        "Tiger takes 4 Force damage from Pirate",
    ]


def test_the_extra_damage_line_is_for_the_gm(fight, monkeypatch):
    """The player link joins a hit's damage to its line: the extra's own
    line stays off it, so nothing comes between them."""
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(15, 1), d6s=(4,))
    ui._apply_custom_effect(_attack())
    events = ui._read_log()["round_1"]
    (extra,) = [e for e in events if "Hunter's Mark: +4" in e["text"]]
    assert PUBLIC_KEY not in extra
    assert any(PUBLIC_KEY in e for e in events if "Force damage" in e["text"])
    hits = [
        line
        for turn in ui._public_log()[0]["turns"]
        for line in turn["lines"]
        if line["kind"] == "hit"
    ]
    assert hits and hits[-1]["amount"] == "5 Slashing + 4 Force"


def test_another_attackers_hit_on_the_marked_target_adds_nothing(fight, monkeypatch):
    ui, pirate, tiger, bugbear = fight
    _mark(ui, pirate, tiger)
    ui._select_character(bugbear)
    _dice(monkeypatch, d20s=(15, 1))  # no d6 to roll
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5


def test_a_miss_adds_nothing(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(2, 1))  # 7 misses AC 15; no d6 to roll
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30


def test_a_save_effect_adds_nothing(fight, monkeypatch):
    """Hunter's Mark is "whenever you hit it with an attack roll"."""
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(2, 1))  # the Tiger fails; no d6 to roll
    ui._apply_custom_effect(
        CustomEffect(name="Burning Hands", damage=[(10, "Fire")], ability="DEX", dc=15)
    )
    assert tiger["hp"] == 30 - 10


def test_a_critical_hit_doubles_the_marks_dice(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    before = len(_events(ui))
    _dice(monkeypatch, d20s=(20, 1), d6s=(3, 5))
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 9 - 8
    assert "Pirate's Hunter's Mark: +8 Force (2d6, critical hit)" in _new_events(
        ui, before
    )


def test_resistance_to_force_halves_the_extra_part_only(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    tiger["damage_resistances"] = [{"damage_types": ["Force"]}]
    before = len(_events(ui))
    _dice(monkeypatch, d20s=(15, 1), d6s=(5,))
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5 - 2
    lines = _new_events(ui, before)
    assert "Tiger takes 5 Slashing damage from Pirate" in lines
    assert "Tiger takes 2 Force damage from Pirate (resisted)" in lines


def test_each_hit_of_several_gets_its_own_extra_dice(fight, monkeypatch):
    """Times 3 (Scorching Ray's rays, say): each hit is a hit by its caster."""
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    before = len(_events(ui))
    _dice(monkeypatch, d20s=(15, 1, 2, 1, 15, 1), d6s=(2, 6))
    rays = [_attack(name=f"Ray ({n} of 3)") for n in (1, 2, 3)]
    ui._apply_custom_effects(rays)
    assert tiger["hp"] == 30 - 5 - 2 - 5 - 6, "the second ray misses"
    extras = [line for line in _new_events(ui, before) if "Hunter's Mark" in line]
    assert extras == [
        "Pirate's Hunter's Mark: +2 Force (1d6)",
        "Pirate's Hunter's Mark: +6 Force (1d6)",
    ]


def test_a_typed_damage_total_gets_no_extra_damage(fight, monkeypatch):
    """A total rolled at the table stays as typed (Decision 4)."""
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(15, 1))  # no d6 to roll
    ui._apply_custom_effect(_attack(typed_damage=True))
    assert tiger["hp"] == 30 - 5


def test_a_fight_without_extra_damage_rolls_the_same_dice(fight, monkeypatch):
    """Two d20s for the attack roll, and nothing after them, as before 3.4."""
    ui, _, tiger, _ = fight
    rolled = []

    def record(low, high):
        rolled.append(high)
        return 15

    monkeypatch.setattr(random, "randint", record)
    ui._apply_custom_effect(_attack())
    assert rolled == [20, 20]
    assert tiger["hp"] == 30 - 5


def test_divine_favor_adds_1d4_radiant_to_its_casters_weapon_hit(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _cast(ui, pirate, "Divine Favor")  # on its caster
    assert find_effect(tiger, "Divine Favor") is None
    ui._set_targets([tiger])
    before = len(_events(ui))
    _dice(monkeypatch, d20s=(15, 1), d4s=(3,))
    ui._apply_custom_effect(_attack(weapon_attack=True))
    assert tiger["hp"] == 30 - 5 - 3
    lines = _new_events(ui, before)
    assert "Pirate's Divine Favor: +3 Radiant (1d4)" in lines
    assert "Tiger takes 3 Radiant damage from Pirate" in lines


def test_divine_favor_adds_nothing_to_another_attack(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _cast(ui, pirate, "Divine Favor")
    ui._set_targets([tiger])
    _dice(monkeypatch, d20s=(15, 1))  # no d4 to roll
    ui._apply_custom_effect(_attack(weapon_attack=False))
    assert tiger["hp"] == 30 - 5


def test_divine_favor_notes_an_attack_it_cant_tell_is_a_weapons(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _cast(ui, pirate, "Divine Favor")
    ui._set_targets([tiger])
    before = len(_events(ui))
    _dice(monkeypatch, d20s=(15, 1))  # no d4 to roll
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5
    assert (
        "Pirate's Divine Favor (not counted): +1d4 Radiant on a weapon hit"
        in _new_events(ui, before)
    )


def test_the_dialogs_pick_notes_its_caster_for_extra_damage(fight, monkeypatch):
    """A badge given through the dialog: its caster is the source, even
    when only its modifiers made its record (no card to show)."""
    ui, pirate, tiger, _ = fight
    pick = EffectOption(
        name="Mark",
        kind=FEATURE,
        condition="Marked",
        badge_modifiers=(("Marked", (MARK,)),),
    )
    ui._apply_custom_effect(CustomEffect(name="Mark", condition="Marked", pick=pick))
    effect = find_effect(tiger, "Marked")
    assert effect is not None and effect["caster"] == "Pirate"
    _dice(monkeypatch, d20s=(15, 1), d6s=(1,))
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5 - 1


def test_removing_the_mark_by_hand_ends_its_extra_damage(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    ui._remove_condition_from(tiger, "Hunter's Mark")
    _dice(monkeypatch, d20s=(15, 1))
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5


def test_a_broken_concentration_ends_the_marks_extra_damage(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Hunter's Mark" not in tiger["conditions"]
    _dice(monkeypatch, d20s=(15, 1))
    ui._apply_custom_effect(_attack())
    assert tiger["hp"] == 30 - 5


def test_a_badge_whose_timer_runs_out_ends_its_extra_damage(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    favor = EffectOption(
        name="Divine Favor",
        kind=SPELL,
        condition="Divine Favor",
        badge_modifiers=(("Divine Favor", (FAVOR,)),),
    )
    ui._set_targets([pirate])
    ui._apply_custom_effect(
        CustomEffect(
            name="Divine Favor",
            condition="Divine Favor",
            duration={"seconds": 6},
            pick=favor,
        )
    )
    assert hit_extras(pirate, tiger) == [("Pirate's Divine Favor", FAVOR)]
    ui._advance_turn()  # the Tiger's turn
    ui._advance_turn()  # the Bugbear's
    ui._advance_turn()  # round 2: the round given on the Pirate's turn passes
    assert "Divine Favor" not in pirate["conditions"]
    assert hit_extras(pirate, tiger) == []


def test_undo_takes_the_extra_damage_back(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(15, 1), d6s=(4,))
    ui._apply_custom_effects([_attack()])
    ui._undo_last()
    assert tiger["hp"] == 30
    assert not any("Force" in line for line in _events(ui))


def _bite() -> MonsterAction:
    return MonsterAction(
        "Bite", "A bite.", to_hit=5, damage=(DamageRoll("1d6", "Piercing"),)
    )


def test_a_monsters_action_adds_the_mark_to_its_hit(fight, monkeypatch):
    """Its damage goes into the Damage field, the mark's 1d6 rolled after."""
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(15, 1), d6s=(3, 4))
    ui._roll_action(_bite(), pirate)
    assert ui.damage_input.text() == "3 Piercing + 4 Force"
    assert "Pirate's Hunter's Mark: +4 Force (1d6)" in ui._action_result_label.text()


def test_another_monsters_action_adds_nothing(fight, monkeypatch):
    ui, pirate, tiger, bugbear = fight
    _mark(ui, pirate, tiger)
    _dice(monkeypatch, d20s=(15, 1), d6s=(3,))
    ui._roll_action(_bite(), bugbear)
    assert ui.damage_input.text() == "3 Piercing"
    assert "Hunter's Mark" not in ui._action_result_label.text()


def test_a_monsters_action_against_several_targets_adds_no_mark(fight, monkeypatch):
    ui, pirate, tiger, bugbear = fight
    _mark(ui, pirate, tiger)
    ui._set_targets([tiger, bugbear])
    _dice(monkeypatch, d20s=(15, 1), d6s=(3,))
    ui._roll_action(_bite(), pirate)
    assert ui.damage_input.text() == "3 Piercing"


# ---------------------------------------------------------------------------
# The dialog


def _chips(dlg, row: str) -> dict[str, QPushButton]:
    widget = dlg.findChild(QWidget, row)
    return {b.text().replace("&", ""): b for b in widget.findChildren(QPushButton)}


def _rows(dlg) -> list[tuple[str, str]]:
    labels = dlg.findChildren(QLabel, "targetRowInfo")
    return [(lbl.text(), lbl.toolTip()) for lbl in labels if lbl.isVisibleTo(dlg)]


def test_the_dialog_reminds_of_the_marks_extra_damage(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    monkeypatch.undo()  # the dialog's exec, for open_dialog
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "rollKindButtons")[ATTACK_ROLL].click()
    ((text, tooltip),) = _rows(dlg)
    assert text == "AC 15, +1d6 Force on a hit"
    assert "Pirate's Hunter's Mark: +1d6 Force on a hit" in tooltip


def test_the_dialog_shows_no_mark_for_another_source(fight, monkeypatch):
    ui, pirate, tiger, bugbear = fight
    _mark(ui, pirate, tiger)
    ui._select_character(bugbear)
    monkeypatch.undo()
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "rollKindButtons")[ATTACK_ROLL].click()
    ((text, tooltip),) = _rows(dlg)
    assert text == "AC 15"
    assert "Hunter's Mark" not in tooltip


@pytest.fixture
def paladin(tmp_path, monkeypatch):
    """Edmund (15) with Divine Favor cast, the source, targeting a Tiger
    (10, AC 15); every d20 a 15 and every other die a 2."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    edmund, tiger = ui.characters
    ui._initiative_inputs[id(edmund)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    _cast(ui, edmund, "Divine Favor")
    ui._set_targets([tiger])
    tiger["ac"] = 15
    monkeypatch.undo()  # the dialog's exec, for open_dialog
    monkeypatch.setattr(random, "randint", lambda low, high: 15 if high == 20 else 2)
    return ui, edmund, tiger


def _pick(dlg, name: str):
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    rows = [
        tree.topLevelItem(i).child(j)
        for i in range(tree.topLevelItemCount())
        for j in range(tree.topLevelItem(i).childCount())
    ]
    row = next(r for r in rows if r.data(0, Qt.ItemDataRole.UserRole).name == name)
    tree.setCurrentItem(row)


def _apply(dlg):
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()


def _damage_lines(ui) -> list[str]:
    return [line for line in _events(ui) if "Tiger takes" in line]


def test_a_picked_weapons_hit_gets_divine_favor(paladin, monkeypatch):
    """The Longsword's 1d8 + 4 (a 2: 6 Slashing) and Divine Favor's 1d4."""
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    _apply(dlg)
    assert any("Edmund's Divine Favor: +2 Radiant (1d4)" in e for e in _events(ui))
    assert tiger["hp"] == 30 - 6 - 2


def test_an_unarmed_strike_gets_no_divine_favor(paladin, monkeypatch):
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Unarmed Strike")
    _apply(dlg)
    assert not any("Divine Favor" in e for e in _events(ui) if "Radiant" in e)
    assert tiger["hp"] == 30 - 5


def test_a_picks_flat_damage_still_gets_the_mark(paladin, monkeypatch):
    """An Unarmed Strike's 5 has no dice, but it's the pick's, not a total
    typed at the table: Edmund's mark on the Tiger adds its 1d6 (a 2)."""
    ui, edmund, tiger = paladin
    tiger["conditions"].append("Hunter's Mark")
    give_modifiers(tiger, "Hunter's Mark", (MARK,))
    note_origin(tiger, "Hunter's Mark", caster=edmund["name"])
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Unarmed Strike")
    _apply(dlg)
    assert tiger["hp"] == 30 - 5 - 2


def test_a_damage_total_typed_over_the_pick_gets_none(paladin, monkeypatch):
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    dlg.findChild(QLineEdit, "effectDamage").setText("12 slashing")
    _apply(dlg)
    assert tiger["hp"] == 30 - 12
    assert _damage_lines(ui) == [
        "[Edmund's turn] Tiger takes 12 Slashing damage from Edmund"
    ]


def test_each_time_of_a_picked_weapon_gets_divine_favor(paladin, monkeypatch):
    """Times 2: the second attack keeps its pick's weapon, so its hit gets
    Divine Favor too."""
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    dlg.findChild(QSpinBox, "effectTimes").setValue(2)
    _apply(dlg)
    favors = [e for e in _events(ui) if "Divine Favor: +2 Radiant" in e]
    assert len(favors) == 2
    assert tiger["hp"] == 30 - 2 * (6 + 2)


# ---------------------------------------------------------------------------
# A typed attack roll in the main window (Q27): the status line says what to
# add, since a typed damage total gets none of it.


def _typed_attack(ui, text: str) -> str:
    ui.attack_roll_input.setText(text)
    ui._apply_attack_roll()
    return ui._status_label.text()


def test_a_typed_hit_on_the_marked_target_says_the_extra(fight):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    ui._select_character(pirate)
    status = _typed_attack(ui, "17")
    assert "+1d6 Force on a hit (Pirate's Hunter's Mark)" in status
    assert "dice twice" not in status


def test_a_typed_critical_hit_says_to_roll_the_extra_twice(fight):
    ui, pirate, tiger, _ = fight
    _mark(ui, pirate, tiger)
    ui._select_character(pirate)
    status = _typed_attack(ui, "nat 20")
    assert "+1d6 Force on a hit (Pirate's Hunter's Mark), its dice twice" in status


def test_a_typed_miss_or_another_attacker_says_no_extra(fight):
    ui, pirate, tiger, bugbear = fight
    _mark(ui, pirate, tiger)
    ui._select_character(pirate)
    assert "Hunter's Mark" not in _typed_attack(ui, "3")
    ui._select_character(bugbear)
    ui._set_targets([tiger])
    assert "Hunter's Mark" not in _typed_attack(ui, "17")
