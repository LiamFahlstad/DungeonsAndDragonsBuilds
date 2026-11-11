"""What a creature answers being hit or damaged with (Notes/combat-effects-plan.md,
step 6.5): HIT_BY rows asked as a hit lands, before its damage (Shield,
Deflect Attacks, Stone's Endurance), TAKES_DAMAGE rows asked after damage from
a creature (Hellish Rebuke, Storm's Thunder), the Reaction they spend, and
CombatEffect.damage_reduction.

Expected values come from the rules text:
- Shield (2024): "Reaction, which you take when you are hit by an attack
  roll ... Until the start of your next turn, you have a +5 bonus to AC,
  including against the triggering attack."
- Deflect Attacks (Monk 3): "When an attack roll hits you and its damage
  includes Bludgeoning, Piercing, or Slashing damage, you can take a
  Reaction to reduce the attack's total damage against you. The reduction
  equals 1d10 plus your Dexterity modifier and Monk level." Kivi (Monk 4,
  DEX +4): 1d10 + 8.
- Stone's Endurance (Goliath): "When you take damage, you can take a
  Reaction to roll 1d12. Add your Constitution modifier to the number
  rolled and reduce the damage by that total."
- Hellish Rebuke: "Reaction, which you take in response to taking damage
  from a creature that you can see within 60 feet ... It makes a Dexterity
  saving throw, taking 2d10 Fire damage on a failed save or half as much
  damage on a successful one."
- Reaction (Rules Glossary): one per round, regained at the start of your
  turn; an Incapacitated creature can't take one.

Clover (Curse of the Lich, a Valor Bard) knows Shield, has AC 18 and two
level 1 slots left of 4. Kivi has AC 17. The Ogre's Greatclub is +6, 2d8 + 4
Bludgeoning."""

import random
from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

import Combat.CombatUIQt.turn_panel_mixin as turn_panel
from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder as Clover,
)
from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder as Kivi,
)
from CharacterContent.Features.SpeciesFeatures.GoliathFeatures import (
    GiantAncestry,
    GiantAncestryType,
)
from CharacterContent.Spells.SpellClasses.Level1 import HellishRebuke, Shield
from Combat.CombatUIQt.attack_rolls import parse_attack_roll
from Combat.CombatUIQt.effect_options import effect_options, triggered_rows
from Combat.CombatUIQt.monster_actions import parse_action
from Combat.CombatUIQt.saves import CustomEffect
from Combat.Effects.triggers import (
    AttackOutcome,
    DamageOutcome,
    TriggerChoice,
    TriggerMode,
    hit_by_firings,
    outcome_firings,
    reaction_lack,
    reduced_damage,
    still_hits,
)
from Combat.Monsters.CR_2.monsters import Ogre
from Core.Definitions import DamageType
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from tests._combat_ui import make_ui

# ---------------------------------------------------------------------------
# As data


def test_a_damage_reduction_reads_back_as_it_was_written():
    effect = CombatEffect(
        name="Deflect Attacks",
        trigger=CombatTrigger(TriggerEvent.HIT_BY),
        damage_reduction="1d10 + 8",
    )
    data = effect.to_dict()
    assert data["damage_reduction"] == "1d10 + 8"
    assert CombatEffect.from_dict(data) == effect


@pytest.mark.parametrize(
    "make",
    [
        lambda: CombatEffect(damage_reduction="1d10 + 8"),
        lambda: CombatEffect(
            damage_reduction="1d10 + 8", trigger=CombatTrigger(TriggerEvent.HIT)
        ),
        lambda: CombatEffect(
            damage_reduction="a lot", trigger=CombatTrigger(TriggerEvent.HIT_BY)
        ),
    ],
)
def test_a_damage_reduction_answers_a_hit_and_is_dice(make):
    with pytest.raises(ValueError):
        make()


def test_shield_is_asked_as_its_caster_is_hit():
    (effect,) = Shield().combat_effects()
    assert effect.trigger == CombatTrigger(TriggerEvent.HIT_BY)


def test_hellish_rebuke_answers_damage_from_a_creature():
    (effect,) = HellishRebuke().combat_effects()
    assert effect.trigger is not None
    assert effect.trigger.event is TriggerEvent.TAKES_DAMAGE
    assert effect.save_ability is not None and effect.half_on_success
    assert [(d.dice, d.damage_type, d.upcast) for d in effect.damage] == [
        ("2d10", DamageType.FIRE, "1d10")
    ]


def test_stones_endurance_and_storms_thunder_have_triggers():
    sheet = Kivi().build()
    stone = GiantAncestry(GiantAncestryType.STONE_GIANT).combat_effects(sheet)[0]
    storm = GiantAncestry(GiantAncestryType.STORM_GIANT).combat_effects(sheet)[0]
    assert stone.trigger == CombatTrigger(TriggerEvent.HIT_BY)
    con = sheet.get_constitution_modifier()
    assert stone.damage_reduction == f"1d12 + {con}" if con > 0 else "1d12"
    assert storm.trigger is not None
    assert storm.trigger.event is TriggerEvent.TAKES_DAMAGE


def test_reduced_damage_comes_off_the_parts_in_turn():
    assert reduced_damage([(13, "Bludgeoning")], 9) == [(4, "Bludgeoning")]
    assert reduced_damage([(5, "Slashing"), (4, "Fire")], 7) == [(2, "Fire")]
    assert reduced_damage([(5, "Slashing")], 12) == []


@pytest.mark.parametrize(
    "critical, total, armor, hits",
    [
        (False, 20, 23, False),
        (False, 23, 23, True),
        (True, None, 23, True),  # a Critical Hit always hits
        (False, None, 23, True),  # a roll not known: as the GM applied it
        (False, 20, None, True),
    ],
)
def test_still_hits(critical, total, armor, hits):
    outcome = AttackOutcome({}, {}, True, critical=critical, total=total)
    assert still_hits(outcome, armor) is hits


# ---------------------------------------------------------------------------
# The interpreter


@pytest.fixture
def party(tmp_path):
    """An Ogre (Large, AC 11), Clover (AC 18, Shield) and Kivi (AC 17,
    Deflect Attacks), in a fight, on the Ogre's turn."""
    ui = make_ui(tmp_path, [Ogre()], [Clover().build(), Kivi().build()])
    clover, kivi, ogre = ui.characters
    for char, value in zip(ui.characters, (5, 3, 20)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(ogre)
    return ui, clover, kivi, ogre


def _hit(attacker, target, total=20, **changes) -> AttackOutcome:
    return AttackOutcome(
        attacker, target, True, total=total, armor=changes.pop("armor", 18), **changes
    )


def test_shield_asks_as_clover_is_hit_and_says_the_ac(party):
    _, clover, _, ogre = party
    found, spent = hit_by_firings(_hit(ogre, clover), triggered_rows)
    assert spent == []
    (firing,) = found
    assert firing.mode is TriggerMode.ASK
    assert firing.owner is clover and firing.target is ogre
    assert firing.question == (
        "Ogre hits Clover: use Shield? Shield. AC 18 + 5 = 23: the 20 misses."
    )
    assert firing.prompt == "Clover: Shield (hit by Ogre)"


def test_shield_says_when_the_hit_still_lands(party):
    _, clover, _, ogre = party
    (firing,) = hit_by_firings(_hit(ogre, clover, total=24), triggered_rows)[0]
    assert firing.question.endswith("AC 18 + 5 = 23: the 24 still hits.")


def test_nothing_answers_a_miss(party):
    _, clover, _, ogre = party
    outcome = AttackOutcome(ogre, clover, False, total=10, armor=18)
    assert hit_by_firings(outcome, triggered_rows) == ([], [])


def test_a_used_reaction_asks_no_more(party):
    _, clover, _, ogre = party
    clover["action_uses"] = {"Reaction": 1}
    assert reaction_lack(clover) == "Reaction used"
    assert hit_by_firings(_hit(ogre, clover), triggered_rows) == ([], [])


def test_an_incapacitated_creature_takes_no_reaction(party):
    _, clover, _, ogre = party
    clover["conditions"] = ["Stunned"]
    assert reaction_lack(clover) == "Incapacitated"
    assert hit_by_firings(_hit(ogre, clover), triggered_rows) == ([], [])


def test_shield_isnt_asked_again_while_it_is_on(party):
    _, clover, _, ogre = party
    clover["conditions"] = ["Shield"]
    assert hit_by_firings(_hit(ogre, clover), triggered_rows) == ([], [])


def test_deflect_attacks_asks_with_its_reduction_and_the_damage_type_check(party):
    _, _, kivi, ogre = party
    found, _ = hit_by_firings(_hit(ogre, kivi, armor=17), triggered_rows)
    (firing,) = found
    assert firing.question == (
        "Ogre hits Kivi Jätti: use Deflect Attacks? Takes 1d10 + 8 off the damage."
        " Check: if its damage includes Bludgeoning, Piercing or Slashing damage."
    )


def test_the_attackers_rows_dont_answer_their_own_hit(party):
    """Hit by Kivi, the Ogre has nothing; Kivi's Deflect Attacks isn't asked."""
    _, _, kivi, ogre = party
    assert hit_by_firings(_hit(kivi, ogre, armor=11), triggered_rows) == ([], [])


def _with_hellish_rebuke(char):
    spells = dict(char.get("_spell_objects") or {})
    spells["Hellish Rebuke"] = HellishRebuke()
    char["_spell_objects"] = spells


def test_hellish_rebuke_asks_about_the_creature_that_dealt_the_damage(party):
    _, clover, _, ogre = party
    _with_hellish_rebuke(clover)
    found, _ = outcome_firings([DamageOutcome(ogre, clover, 7)], triggered_rows)
    (firing,) = [f for f in found if f.row.name == "Hellish Rebuke"]
    assert firing.owner is clover and firing.target is ogre
    assert firing.mode is TriggerMode.ASK
    assert firing.question.startswith(
        "Ogre deals Clover 7 damage: use Hellish Rebuke? 2d10 Fire."
    )
    assert firing.question.endswith("Check: if you can see it within 60 feet.")


def test_no_damage_taken_and_its_own_damage_answer_nothing(party):
    _, clover, _, ogre = party
    _with_hellish_rebuke(clover)
    assert outcome_firings([DamageOutcome(ogre, clover, 0)], triggered_rows)[0] == []
    assert outcome_firings([DamageOutcome(clover, clover, 5)], triggered_rows)[0] == []


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
    """Stands in for the pop-up: records each question, gives `answer`."""

    def __init__(self, answer: str = "apply"):
        self.answer = answer
        self.asked: list[list[str]] = []

    def __call__(self, firings):
        self.asked.append([f.question for f in firings])
        if self.answer == "apply":
            return TriggerChoice(apply=tuple(firings))
        return TriggerChoice()


@pytest.fixture
def fight(party, monkeypatch):
    ui, clover, kivi, ogre = party
    answers = Answers()
    monkeypatch.setattr(ui, "_ask_triggers", answers)
    return ui, clover, kivi, ogre, answers


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def _typed_hit(ui, target, roll="20", damage="13 bludgeoning"):
    """The Ogre's attack roll and damage typed in the main window, one Enter."""
    ui._set_targets([target])
    ui.attack_roll_input.setText(roll)
    ui.damage_input.setText(damage)
    ui._apply_damage_checked()


def test_shield_turns_a_20_into_a_miss_and_spends_the_reaction_and_a_slot(fight):
    ui, clover, _, _, answers = fight
    hp, slots = clover["hp"], clover["spell_slots"][1]
    _typed_hit(ui, clover)
    assert answers.asked == [
        ["Ogre hits Clover: use Shield? Shield. AC 18 + 5 = 23: the 20 misses."]
    ]
    assert "Shield" in clover["conditions"]
    assert clover["hp"] == hp
    assert clover["action_uses"]["Reaction"] == 1
    assert clover["spell_slots"][1] == slots - 1
    lines = _lines(ui)
    assert "Clover casts Shield" in lines
    assert lines[-1] == "Ogre's attack roll now misses Clover"
    assert "then a miss" in ui._status_label.text()


def test_a_hit_shield_cant_stop_still_deals_its_damage(fight):
    ui, clover, _, _, answers = fight
    hp = clover["hp"]
    _typed_hit(ui, clover, roll="24")
    assert answers.asked[0][0].endswith("the 24 still hits.")
    assert "Shield" in clover["conditions"]
    assert clover["hp"] == hp - 13


def test_after_shield_the_next_hit_asks_nothing_and_meets_ac_23(fight):
    ui, clover, _, _, answers = fight
    hp = clover["hp"]
    _typed_hit(ui, clover)
    _typed_hit(ui, clover, roll="22")
    assert len(answers.asked) == 1  # the Reaction is spent
    assert clover["hp"] == hp  # 22 misses AC 23


def test_skip_deals_the_hit_and_logs_a_line_for_the_gm(fight):
    ui, clover, _, _, answers = fight
    answers.answer = "skip"
    hp = clover["hp"]
    _typed_hit(ui, clover)
    assert clover["hp"] == hp - 13
    assert "Shield" not in clover["conditions"]
    assert "Clover didn't use Shield on Ogre" in _lines(ui)


def test_one_undo_takes_back_the_hit_and_the_shield(fight):
    ui, clover, _, _, _ = fight
    slots = clover["spell_slots"][1]
    _typed_hit(ui, clover, roll="24")
    ui._undo_last()
    clover = ui._find_character_by_name("Clover")
    assert "Shield" not in clover["conditions"]
    assert clover["spell_slots"][1] == slots
    assert (clover.get("action_uses") or {}).get("Reaction", 0) == 0


def test_with_the_setting_off_it_is_a_turn_column_button(fight):
    ui, clover, _, _, answers = fight
    ui.settings = replace(ui.settings, ask_triggers=False)
    hp = clover["hp"]
    _typed_hit(ui, clover)
    assert answers.asked == []
    assert clover["hp"] == hp - 13
    assert [p.prompt for p in ui._hit_prompts] == ["Clover: Shield (hit by Ogre)"]


def test_deflect_attacks_takes_its_roll_off_the_damage(fight, monkeypatch):
    ui, _, kivi, _, answers = fight
    monkeypatch.setattr(turn_panel, "roll_dice", lambda dice, critical=False: 9)
    hp = kivi["hp"]
    _typed_hit(ui, kivi)
    assert len(answers.asked) == 1
    assert kivi["hp"] == hp - 4  # 13 - 9
    assert kivi["action_uses"]["Reaction"] == 1
    assert "Kivi Jätti's Deflect Attacks takes 9 off the damage (1d10 + 8)" in (
        _lines(ui)
    )


def test_deflect_attacks_can_take_it_all(fight, monkeypatch):
    ui, _, kivi, _, _ = fight
    monkeypatch.setattr(turn_panel, "roll_dice", lambda dice, critical=False: 18)
    hp = kivi["hp"]
    _typed_hit(ui, kivi)
    assert kivi["hp"] == hp
    assert not any(line.startswith("Kivi Jätti takes") for line in _lines(ui))


def test_an_attack_roll_entered_then_its_damage_asks_as_the_damage_lands(fight):
    ui, clover, _, _, answers = fight
    hp = clover["hp"]
    ui._set_targets([clover])
    ui.attack_roll_input.setText("20")
    ui._apply_attack_roll()
    assert answers.asked == []
    ui.damage_input.setText("13 bludgeoning")
    ui._apply_damage_checked()
    assert len(answers.asked) == 1
    assert clover["hp"] == hp


def test_a_monster_buttons_hit_asks_as_enter_deals_it(fight, monkeypatch):
    ui, clover, _, ogre, answers = fight
    monkeypatch.setattr(random, "randint", lambda a, b: min(b, 14))
    ui._set_targets([clover])
    club = parse_action(
        {
            "name": "Greatclub",
            "description": "Melee Attack Roll: +6, reach 5 ft. Hit: 13 (2d8 + 4)"
            " Bludgeoning damage.",
        }
    )
    hp = clover["hp"]
    ui._roll_action(club, ogre)  # 14 + 6 = 20 against AC 18: a hit
    ui._apply_damage_checked()
    assert answers.asked == [
        ["Ogre hits Clover: use Shield? Shield. AC 18 + 5 = 23: the 20 misses."]
    ]
    assert clover["hp"] == hp


def _ogres_club(ogre):
    (option,) = [
        o
        for _, options in effect_options(ogre, ())
        for o in options
        if o.name == "Greatclub"
    ]
    return option


def test_the_dialogs_hit_becomes_a_miss(fight):
    ui, clover, _, ogre, answers = fight
    ui._set_targets([clover])
    attack = parse_attack_roll("20")
    assert attack is not None
    hp = clover["hp"]
    ui._apply_custom_effect(
        CustomEffect(
            name="Greatclub",
            damage=[(13, "Bludgeoning")],
            attack_bonus=6,
            typed_attacks={id(clover): attack},
            pick=_ogres_club(ogre),
        )
    )
    assert len(answers.asked) == 1
    assert "Shield" in clover["conditions"]
    assert clover["hp"] == hp


def test_hellish_rebuke_is_asked_after_the_damage_and_burns_the_ogre(fight):
    ui, clover, _, ogre, answers = fight
    _with_hellish_rebuke(clover)
    answers.answer = "skip"  # no Shield
    asked = []

    def answer(firings):
        asked.append([f.row.name for f in firings])
        names = {f.row.name for f in firings}
        if names == {"Hellish Rebuke"}:
            return TriggerChoice(apply=tuple(firings))
        return TriggerChoice()

    ui._ask_triggers = answer
    ogre_hp, clover_hp = ogre["hp"], clover["hp"]
    _typed_hit(ui, clover, roll="24")
    assert asked == [["Shield"], ["Hellish Rebuke"]]
    assert clover["hp"] == clover_hp - 13
    assert ogre["hp"] < ogre_hp
    assert clover["action_uses"]["Reaction"] == 1
    assert "Clover casts Hellish Rebuke" in _lines(ui)


def test_damage_typed_without_an_attack_roll_still_asks_hellish_rebuke(fight):
    """Damage from a creature, a hit or not: only Hellish Rebuke is asked."""
    ui, clover, _, _, answers = fight
    _with_hellish_rebuke(clover)
    answers.answer = "skip"
    ui._set_targets([clover])
    ui.damage_input.setText("7 fire")
    ui._apply_damage_checked()
    assert len(answers.asked) == 1
    assert answers.asked[0][0].startswith(
        "Ogre deals Clover 7 damage: use Hellish Rebuke?"
    )
