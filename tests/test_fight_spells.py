"""Casting a spell without the combat window (Combat/Fight/spells.py,
Notes/combat-ui-refactor-plan.md step 5.3).

A slot of the level asked for is spent (a Warlock's Pact Magic slot when it
has no spell slot of that level); a round is 6 seconds off a spell's timer
(Core/Rules.py); the timer counts on the turn it was cast on."""

from types import SimpleNamespace

from Core.Rules import SECONDS_PER_ROUND
from Combat.Fight.spells import (
    active_spell_record,
    count_spell_cast,
    spell_recipients,
    spend_slot,
    tick,
    ticks_now,
)
from Model.Content.Feature import FeatureTarget


def test_a_spell_slot_of_the_level_is_spent_and_counted():
    wizard = {"name": "Wizard", "spell_slots": {1: 2, 2: 1}}
    spent = spend_slot(wizard, 2)
    assert spent is not None and not spent.pact
    assert wizard["spell_slots"] == {1: 2, 2: 0}
    assert wizard["stats"]["spell_slots_used"] == 1
    assert spend_slot(wizard, 2) is None


def test_a_warlock_spends_pact_magic_when_no_spell_slot_is_left():
    warlock = {"name": "Warlock", "spell_slots": {}, "pact_slots": {2: 2}}
    spent = spend_slot(warlock, 2)
    assert spent is not None and spent.pact and warlock["pact_slots"] == {2: 1}


def test_a_pact_slot_asked_for_is_a_pact_slot():
    both = {"name": "Multi", "spell_slots": {1: 1}, "pact_slots": {1: 1}}
    spent = spend_slot(both, 1, asked_for_pact=True)
    assert spent is not None and spent.pact
    assert both["spell_slots"] == {1: 1} and both["pact_slots"] == {1: 0}


def test_casts_are_counted_by_name():
    cleric: dict = {"name": "Cleric"}
    count_spell_cast(cleric, "Bless")
    count_spell_cast(cleric, "Bless")
    assert cleric["stats"]["spells_cast"] == 2
    assert cleric["stats"]["spells_cast_by_name"] == {"Bless": 2}


def test_who_a_spell_lands_on():
    caster, ogre = {"name": "Caster"}, {"name": "Ogre"}

    def spell(target):
        return SimpleNamespace(target=target)

    assert spell_recipients(spell(FeatureTarget.SELF), caster, [ogre]) == [caster]
    assert spell_recipients(spell(None), caster, [ogre]) == [caster]
    assert spell_recipients(spell(FeatureTarget.AREA), caster, []) == []
    assert spell_recipients(spell(FeatureTarget.CREATURE), caster, [ogre]) == [ogre]
    assert spell_recipients(spell(FeatureTarget.CREATURE), caster, []) is None


def test_a_spells_timer_counts_on_its_casting_turn():
    entry = active_spell_record("Bless", 60, True, [], ticks_on="Cleric")
    in_order = {"Cleric", "Ogre"}
    assert ticks_now(entry, {"Cleric"}, in_order, new_round=False)
    assert not ticks_now(entry, {"Ogre"}, in_order, new_round=True)
    # Its caster gone from the turn order: it counts as each round starts.
    assert ticks_now(entry, {"Ogre"}, {"Ogre"}, new_round=True)
    assert not ticks_now(entry, {"Ogre"}, {"Ogre"}, new_round=False)


def test_a_round_comes_off_the_timer():
    entry = active_spell_record(
        "Shield of Faith", 2 * SECONDS_PER_ROUND, True, [], None
    )
    assert not tick(entry) and entry["time_left"] == SECONDS_PER_ROUND
    assert tick(entry) and entry["time_left"] == 0
