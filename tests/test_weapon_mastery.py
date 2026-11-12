"""Weapon Mastery in a fight (Notes/combat-effects-plan.md, step 6.9): a
weapon's mastery property is a row of its own after the weapon's attack
("Longsword: Sap", Model/Content/WeaponMasteryEffects.py), applied or asked
about as the weapon picked in the Custom Effect dialog hits or misses; and
the `once` and `by_caster` modifier fields Sap, Vex, Guiding Bolt and Vicious
Mockery are written with (a badge that counts for one attack roll, and one
that counts only for the creature that gave it).

Expected values come from the rules text (2024 Player's Handbook, Mastery
Properties; MASTERY_RULES) and the party's sheets. Edmund (Curse of the
Lich): Strength +4, Proficiency Bonus 2, Longsword (Sap) and Handaxe (Vex)
mastered; Thum: Shortsword (Vex), so Halfling's Trick, a magic Shortsword,
too; Hanna (Time Loop PR): Longbow (Slow); Obmar: Sulvesburg's Folly (Push),
Dagger and Light Hammer (Nick).
- Topple: "you can force the creature to make a Constitution saving throw
  (DC 8 plus the ability modifier used to make the attack roll and your
  Proficiency Bonus). On a failed save, the creature has the Prone
  condition." Edmund's Battleaxe: DC 8 + 4 + 2 = 14.
- Graze: "If your attack roll with this weapon misses a creature, you can
  deal damage to that creature equal to the ability modifier you used to
  make the attack roll. This damage is the same type dealt by the weapon."
  Edmund's Greatsword: 4 Slashing.
- Cleave: "you can make a melee attack roll with the weapon against a second
  creature ... On a hit, the second creature takes the weapon's damage, but
  don't add your ability modifier ... only once per turn." Edmund's
  Greataxe: +6, 1d12 Slashing.
- Sap: "that creature has Disadvantage on its next attack roll before the
  start of your next turn."
- Vex: "If you hit a creature with this weapon and deal damage to the
  creature, you have Advantage on your next attack roll against that
  creature before the end of your next turn."
- Slow: "If you hit a creature with this weapon and deal damage to it, you
  can reduce its Speed by 10 feet until the start of your next turn ... the
  Speed reduction doesn't exceed 10 feet."
- Push: "you can push the creature up to 10 feet straight away from
  yourself if it is Large or smaller."
- Nick: changes when the Light property's extra attack is made: no row."""

import random
from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Characters.Y2024_Artificer_Cartographer_ObmarStalskagg import (
    Y2024ArtificerCartographerObmarStalskaggCharacterBuilder as Obmar,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Builds.Characters.Y2024_Ranger_Drakewarden_Hanna import (
    Y2024RangerDrakewardenHannaCharacterBuilder as Hanna,
)
from Builds.Characters.Y2024_Rogue_ArcaneTrickster_ThumSchtock import (
    Y2024RogueArcaneTricksterThumSchtockCharacterBuilder as Thum,
)
from CharacterContent.Items import Weapons
from CharacterContent.Items.Weapons.Magic import HalflingssTrick
from CharacterContent.Spells.SpellClasses.Cantrips import ViciousMockery
from CharacterContent.Spells.SpellClasses.Level1 import GuidingBolt
from Combat.CombatUIQt.attack_rolls import parse_attack_roll
from Combat.CombatUIQt.conditions_mixin import _picked_effect
from Combat.CombatUIQt.monster_actions import parse_action
from Combat.CombatUIQt.effect_options import (
    ATTACKS,
    effect_options,
    triggered_rows,
)
from Combat.Effects.active_effects import find_effect
from Combat.Effects.modifiers import (
    attack_plan,
    speed_in_use,
    used_up_by_attack,
)
from Combat.Effects.triggers import (
    AttackOutcome,
    TriggerChoice,
    TriggerMode,
    outcome_firings,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Combat.Monsters.CR_5.monsters import HillGiant
from Core.Definitions import Ability, Condition, CreatureSize, DamageType
from Core.Weapons import WeaponMastery
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatModifiers import (
    AttacksAgainst,
    D20Mode,
    D20Test,
    RollMode,
    Speed,
    modifier_from_dict,
    modifier_to_dict,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerAim, TriggerEvent
from Model.Content.WeaponMasteryEffects import (
    MASTERY_RULES,
    mastery_effects,
    mastery_note,
)
from tests._combat_ui import make_ui

# ---------------------------------------------------------------------------
# As data


def test_once_and_by_caster_read_back_and_are_checked():
    vex = AttacksAgainst(RollMode.ADVANTAGE, by_caster=True, once=True)
    assert modifier_to_dict(vex) == {
        "type": "AttacksAgainst",
        "mode": "Advantage",
        "by_caster": True,
        "once": True,
    }
    assert modifier_from_dict(modifier_to_dict(vex)) == vex
    sap = D20Mode((D20Test.ATTACK_ROLL,), RollMode.DISADVANTAGE, once=True)
    assert modifier_from_dict(modifier_to_dict(sap)) == sap
    # "Its next attack roll": a D20 Test that isn't one has no "next".
    with pytest.raises(ValueError):
        D20Mode((D20Test.SAVING_THROW,), RollMode.DISADVANTAGE, once=True)
    with pytest.raises(ValueError):
        AttacksAgainst(RollMode.ADVANTAGE, once="yes")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        modifier_from_dict({"type": "AttacksAgainst", "mode": "Advantage", "once": 1})


@pytest.fixture(scope="module")
def edmund_sheet():
    return Edmund().build()  # the combatant's "_stat_block" is the Character


def _effect(weapon, sheet) -> CombatEffect:
    (effect,) = mastery_effects(weapon, sheet)
    return effect


def test_topple_is_a_constitution_save_or_prone(edmund_sheet):
    effect = _effect(Weapons.Battleaxe(), edmund_sheet)
    assert effect == CombatEffect(
        name="Battleaxe: Topple",
        roll=EffectRoll.SAVE,
        save_ability=Ability.CONSTITUTION,
        dc=14,  # 8 + Strength 4 + Proficiency Bonus 2
        conditions=(CombatCondition(Condition.PRONE),),
        spends_use=False,
        trigger=CombatTrigger(TriggerEvent.HIT, after="Battleaxe"),  # "you can"
    )


def test_sap_and_vex_are_badges_for_one_attack_roll(edmund_sheet):
    sap = _effect(Weapons.Longsword(), edmund_sheet)
    assert sap.trigger == CombatTrigger(
        TriggerEvent.HIT, optional=False, after="Longsword"
    )
    assert sap.conditions == (
        CombatCondition(
            "Sap",
            until=(TurnEdge.START, TurnOf.SOURCE),
            modifiers=(
                D20Mode((D20Test.ATTACK_ROLL,), RollMode.DISADVANTAGE, once=True),
            ),
        ),
    )
    vex = _effect(Weapons.Handaxe(), edmund_sheet)
    # "and deal damage to the creature"
    assert vex.trigger == CombatTrigger(
        TriggerEvent.HIT, optional=False, after="Handaxe", needs_damage=True
    )
    assert vex.conditions == (
        CombatCondition(
            "Vex",
            until=(TurnEdge.END, TurnOf.SOURCE),
            modifiers=(AttacksAgainst(RollMode.ADVANTAGE, by_caster=True, once=True),),
        ),
    )


def test_slow_graze_push_and_cleave(edmund_sheet):
    slow = _effect(Weapons.Longbow(), edmund_sheet)
    assert slow.conditions[0].modifiers == (Speed(bonus=-10),)
    assert slow.conditions[0].until == (TurnEdge.START, TurnOf.SOURCE)
    assert slow.trigger == CombatTrigger(
        TriggerEvent.HIT, after="Longbow", needs_damage=True
    )
    graze = _effect(Weapons.Greatsword(), edmund_sheet)
    assert graze.damage == (CombatDamage("4", DamageType.SLASHING),)
    assert graze.trigger == CombatTrigger(TriggerEvent.MISS, after="Greatsword")
    push = _effect(Weapons.Warhammer(), edmund_sheet)
    assert push.trigger == CombatTrigger(
        TriggerEvent.HIT, after="Warhammer", largest_target=CreatureSize.LARGE
    )
    assert push.conditions == () and push.damage == ()
    cleave = _effect(Weapons.Greataxe(), edmund_sheet)
    assert cleave.roll is EffectRoll.ATTACK
    assert cleave.attack_bonus == 6
    assert cleave.damage == (CombatDamage("1d12", DamageType.SLASHING),)  # no +4
    assert cleave.trigger == CombatTrigger(
        TriggerEvent.HIT, after="Greataxe", once_per_turn=True, aim=TriggerAim.ANOTHER
    )
    # Nick changes when an attack is made: a note on the weapon, no row.
    assert mastery_effects(Weapons.Dagger(), edmund_sheet) == []
    assert mastery_note(Weapons.Dagger()).startswith("Nick:")
    assert mastery_note(Weapons.Longsword()) == ""
    assert set(MASTERY_RULES) == set(WeaponMastery)


def test_graze_with_no_modifier_above_0_deals_nothing(edmund_sheet, monkeypatch):
    sword = Weapons.Greatsword()
    monkeypatch.setattr(sword, "attack_ability_modifier", lambda sheet: 0)
    assert mastery_effects(sword, edmund_sheet) == []


def test_a_magic_weapon_is_mastered_with_its_kind():
    assert HalflingssTrick().has_mastery([Weapons.Shortsword()])
    assert not Weapons.Shortsword().has_mastery([Weapons.Scimitar()])


def test_guiding_bolt_and_vicious_mockery_are_badges_for_one_roll():
    (bolt,) = GuidingBolt().combat_effects()
    assert bolt.notes == ()
    assert bolt.conditions == (
        CombatCondition(
            "Guiding Bolt",
            until=(TurnEdge.END, TurnOf.SOURCE),
            modifiers=(AttacksAgainst(RollMode.ADVANTAGE, once=True),),
        ),
    )
    (mockery,) = ViciousMockery().combat_effects()
    assert mockery.notes == ()
    assert mockery.conditions == (
        CombatCondition(
            "Vicious Mockery",
            until=(TurnEdge.END, TurnOf.TARGET),
            modifiers=(
                D20Mode((D20Test.ATTACK_ROLL,), RollMode.DISADVANTAGE, once=True),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# The picker and the interpreter


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


class Answers:
    """Stands in for the pop-up: records each question and applies them all;
    a row aimed at another creature goes on `aim` (a name's start), if it's
    offered."""

    def __init__(self):
        self.asked: list[list[str]] = []
        self.aim = ""

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        aimed = tuple(
            (f, tuple(c for c in f.others if c["name"].startswith(self.aim))[:1])
            for f in firings
            if f.others and self.aim
        )
        return TriggerChoice(apply=tuple(firings), aimed=aimed)


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """Edmund, Thum, Hanna and Obmar against two Ogres (Large, AC 11, Speed
    40) and a Hill Giant (Huge), on Edmund's turn."""
    party = [Edmund().build(), Thum().build(), Hanna().build(), Obmar().build()]
    ui = make_ui(tmp_path, [Ogre(), Ogre(), HillGiant()], party)
    for char, value in zip(ui.characters, (20, 19, 18, 17, 10, 9, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    names = ["Edmund", "Thum", "Hanna", "Obmar"]
    found = {
        n: next(c for c in ui.characters if c["name"].startswith(n)) for n in names
    }
    ogres = [c for c in ui.characters if c["name"].startswith("Ogre")]
    giant = next(c for c in ui.characters if c["name"].startswith("Hill Giant"))
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    ui._select_character(found["Edmund"])
    return ui, found, ogres, giant, answers


def _row(char, name):
    rows = [
        o
        for title, options in effect_options(char, ())
        if title == ATTACKS
        for o in options
        if o.name == name
    ]
    assert rows, f"{char['name']} has no {name!r} row"
    return rows[0]


def test_the_picker_lists_each_mastered_weapons_row(fight):
    _, party, _, _, _ = fight
    names = {who: [r.name for r in triggered_rows(char)] for who, char in party.items()}
    assert names["Edmund"] == ["Longsword: Sap", "Handaxe: Vex"]
    # Halfling's Trick is a Shortsword: Thum's Shortsword mastery covers it.
    assert names["Thum"] == ["Shortsword: Vex", "Halfling's Trick: Vex"]
    assert "Longbow: Slow" in names["Hanna"]
    assert names["Obmar"] == ["Sulvesburg's Folly: Push"]
    # Not mastered: Edmund's Greatsword (Graze) has no row.
    assert all("Greatsword" not in n for n in names["Edmund"])
    assert _row(party["Edmund"], "Longsword: Sap").summary == "Sap  on a hit"
    assert "Nick:" in _row(party["Obmar"], "Dagger").note
    assert _row(party["Edmund"], "Longsword: Sap").tooltip == (
        MASTERY_RULES[WeaponMastery.SAP]
    )


def test_a_mastery_follows_only_its_weapon_picked(fight):
    _, party, ogres, _, _ = fight
    edmund, ogre = party["Edmund"], ogres[0]

    def fired(**outcome):
        found, _ = outcome_firings(
            [AttackOutcome(edmund, ogre, **outcome)], triggered_rows
        )
        return [(f.row.name, f.mode) for f in found]

    assert fired(hit=True, row="Longsword") == [("Longsword: Sap", TriggerMode.AUTO)]
    assert fired(hit=False, row="Longsword") == []
    assert fired(hit=True, row="Handaxe", damage_dealt=0) == []  # Vex needs damage
    assert fired(hit=True, row="Handaxe", damage_dealt=5) == [
        ("Handaxe: Vex", TriggerMode.AUTO)
    ]
    # A hit typed in the main window: which weapon isn't known, so nothing
    # is asked (as a spell's later step, R137).
    assert fired(hit=True) == []


# ---------------------------------------------------------------------------
# In the window


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def _attack_with(ui, char, row_name, target, roll="18"):
    """The Custom Effect dialog's Apply of char's weapon row picked, the
    attack roll typed in its target row."""
    ui._select_character(char)
    ui._set_targets([target])
    attack = parse_attack_roll(roll)
    effect = _picked_effect(_row(char, row_name), {})
    assert effect is not None and attack is not None
    ui._apply_custom_effect(replace(effect, typed_attacks={id(target): attack}))


def test_sap_from_a_longsword_hit_gives_the_ogre_disadvantage_once(fight, monkeypatch):
    ui, party, ogres, _, answers = fight
    edmund, ogre = party["Edmund"], ogres[0]
    _attack_with(ui, edmund, "Longsword", ogre)
    assert answers.asked == []  # it happens: no pop-up
    assert "Sap" in ogre["conditions"]
    record = find_effect(ogre, "Sap")
    assert record is not None and record["caster"] == edmund["name"]
    # Its next attack roll has Disadvantage.
    assert attack_plan(ogre, edmund, "Neutral").mode == "Disadvantage"
    # The Ogre's Greatclub button: rolled with Disadvantage, then Sap is used up.
    ui._select_character(ogre)
    ui._set_targets([edmund])
    rolls = iter([15, 3])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls, 4))
    club = parse_action(next(a for a in ogre["actions"] if a.name == "Greatclub"))
    ui._use_monster_action(ogre, club)
    assert "Sap" not in ogre["conditions"]
    assert "Ogre's Sap is used up" in "\n".join(_lines(ui))
    assert attack_plan(ogre, edmund, "Neutral").mode == "Neutral"
    # One undo takes the roll back, and Sap with it.
    ui._undo_last()
    assert "Sap" in ogre["conditions"]


def test_a_miss_gives_no_sap(fight):
    ui, party, ogres, _, _ = fight
    _attack_with(ui, party["Edmund"], "Longsword", ogres[0], roll="2")
    assert "Sap" not in ogres[0]["conditions"]


def test_vex_counts_only_for_its_wielders_next_roll(fight):
    ui, party, ogres, _, _ = fight
    edmund, thum, ogre = party["Edmund"], party["Thum"], ogres[0]
    _attack_with(ui, thum, "Shortsword", ogre)
    assert "Vex" in ogre["conditions"]
    assert attack_plan(thum, ogre, "Neutral").mode == "Advantage"
    # Not for Edmund, whose roll doesn't use it up.
    assert attack_plan(edmund, ogre, "Neutral").mode == "Neutral"
    assert used_up_by_attack(edmund, ogre) == []
    # With no attacker known, it's the GM's to judge.
    assert any(
        "if the attacker is Thum" in note
        for note in attack_plan(None, ogre, "Neutral").notes
    )
    # Thum's next roll against it uses it up (it hits again: a new Vex).
    _attack_with(ui, thum, "Shortsword", ogre, roll="2")
    assert "Vex" not in ogre["conditions"]


def test_slow_takes_10_feet_once_however_many_hits(fight):
    ui, party, ogres, _, answers = fight
    hanna, ogre = party["Hanna"], ogres[0]
    _attack_with(ui, hanna, "Longbow", ogre)
    assert answers.asked == [
        [f"{hanna['name']} hits Ogre (Large): use Longbow: Slow? Slow."]
    ]
    assert speed_in_use(ogre, 40) == 30
    _attack_with(ui, hanna, "Longbow", ogre)
    assert speed_in_use(ogre, 40) == 30


def test_push_is_asked_for_a_large_ogre_not_a_huge_giant(fight):
    ui, party, ogres, giant, answers = fight
    obmar = party["Obmar"]
    _attack_with(ui, obmar, "Sulvesburg's Folly", giant)
    assert answers.asked == []
    _attack_with(ui, obmar, "Sulvesburg's Folly", ogres[0])
    assert answers.asked == [
        [f"{obmar['name']} hits Ogre (Large): use Sulvesburg's Folly: Push?"]
    ]
    # Moved at the table; the log says it was used.
    assert f"{obmar['name']} uses Sulvesburg's Folly: Push on Ogre" in "\n".join(
        _lines(ui)
    )


def _master(char, weapon):
    """char wields `weapon` with its mastery."""
    char["_weapons_objects"] = [*char["_weapons_objects"], weapon]
    char["_weapon_masteries"] = [*char["_weapon_masteries"], weapon]


def test_topple_knocks_the_ogre_prone_on_a_failed_save(fight, monkeypatch):
    ui, party, ogres, _, answers = fight
    edmund, ogre = party["Edmund"], ogres[0]
    _master(edmund, Weapons.Battleaxe())
    monkeypatch.setattr(random, "randint", lambda low, high: 5 if high == 20 else 1)
    _attack_with(ui, edmund, "Battleaxe", ogre)
    assert answers.asked == [
        ["Edmund hits Ogre (Large): use Battleaxe: Topple? Prone."]
    ]
    # 5 + Constitution 3 = 8, against DC 14.
    assert "Prone" in ogre["conditions"]


def test_graze_deals_the_modifier_on_a_miss(fight):
    ui, party, ogres, _, answers = fight
    edmund, ogre = party["Edmund"], ogres[0]
    _master(edmund, Weapons.Greatsword())
    hp = ogre["hp"]
    _attack_with(ui, edmund, "Greatsword", ogre, roll="2")
    assert answers.asked == [
        ["Edmund misses Ogre (Large): use Greatsword: Graze? 4 Slashing."]
    ]
    assert ogre["hp"] == hp - 4


def test_cleave_attacks_another_creature_once_per_turn(fight, monkeypatch):
    ui, party, ogres, _, answers = fight
    edmund, first, second = party["Edmund"], ogres[0], ogres[1]
    _master(edmund, Weapons.Greataxe())
    monkeypatch.setattr(random, "randint", lambda low, high: 15 if high == 20 else 6)
    hp = second["hp"]
    answers.aim = "Ogre"  # the other Ogre, near the first
    _attack_with(ui, edmund, "Greataxe", first)
    assert len(answers.asked) == 1
    (question,) = answers.asked[0]
    assert question.startswith("Edmund hits Ogre (Large): use Greataxe: Cleave?")
    # 15 + 6 hits AC 11; the weapon's 1d12 without Strength: 6.
    assert second["hp"] == hp - 6
    # Once per turn: a second Greataxe hit asks nothing.
    _attack_with(ui, edmund, "Greataxe", first)
    assert len(answers.asked) == 1
