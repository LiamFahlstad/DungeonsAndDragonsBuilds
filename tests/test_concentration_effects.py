"""Concentration ends every lasting effect it holds (Notes/combat-effects-plan.md,
step 3.6): each record's `concentration` link, as well as the caster's active
spell, says what ends with it.

Expected values come from the 2024 rules. Concentration (Rules Glossary):
"Some spells and other effects require Concentration to remain active ... If
the effect's creator loses Concentration, the effect ends", and it ends when
the creator starts another Concentration effect, has the Incapacitated
condition, dies or fails the Constitution save. Bless: "Each target adds 1d4
to the attack roll or save" for the duration, which is Concentration, up to
1 minute. A creature that leaves the fight (a dismissed or vanished summon)
can't concentrate any more, so what it held ends with it."""

import pytest
from PyQt6.QtWidgets import QMessageBox

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.Effects.active_effects import (
    SPELL,
    describe,
    find_effect,
    held_by_concentration,
    link_concentration,
    unlink_concentration,
)
from Combat.Effects.modifiers import modifiers_on, save_plan
from tests._combat_ui import make_ui

NEUTRAL = "Neutral"


def _named(combatant, name: str):
    combatant.set_name(name)
    return combatant


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """A Pirate and a Bandit (both casters here, with no slots: spending
    one is answered Yes) and two targets, a Tiger and a Cat."""
    monkeypatch.setattr(
        QMessageBox, "question", lambda *a, **k: QMessageBox.StandardButton.Yes
    )
    ui = make_ui(
        tmp_path,
        [Pirate(), Tiger(), _named(Pirate(), "Bandit"), _named(Tiger(), "Cat")],
    )
    for char, value in zip(ui.characters, (15, 10, 5, 3)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    return ui, *ui.characters


def _cast(ui, caster, spell: str, *targets):
    ui._select_character(caster)
    ui._set_targets(list(targets))
    ui._apply_cast_spell(SpellFactory.create(spell))


def _blessed(char) -> bool:
    """Whether char has Bless's badge, its record and its 1d4."""
    bonuses = save_plan(char, "WIS", NEUTRAL).bonuses
    has = "Bless" in char["conditions"]
    assert has == (find_effect(char, "Bless") is not None)
    assert has == (bonuses == (("Bless", "1d4"),))
    return has


def _concentration_of(char, badge: str) -> str | None:
    effect = find_effect(char, badge)
    return effect["concentration"] if effect is not None else None


# ---------------------------------------------------------------------------
# As data


def test_held_by_concentration_finds_every_effect_linked_to_a_concentrator():
    tiger = {"name": "Tiger", "conditions": ["Bless"]}
    cat = {"name": "Cat", "conditions": ["Bless", "Bane"]}
    link_concentration(tiger, "Bless", "Pirate")
    link_concentration(cat, "Bless", "Pirate")
    link_concentration(cat, "Bane", "Bandit")
    found = held_by_concentration([tiger, cat], "Pirate")
    assert [(c["name"], e["name"]) for c, e in found] == [
        ("Tiger", "Bless"),
        ("Cat", "Bless"),
    ]
    assert held_by_concentration([tiger, cat], "Nobody") == []


def test_unlinking_drops_a_record_that_says_nothing_else():
    tiger = {"name": "Tiger", "conditions": ["Bless"]}
    link_concentration(tiger, "Bless", "Pirate")
    unlink_concentration(tiger, "Bless")
    assert find_effect(tiger, "Bless") is None


def test_unlinking_keeps_what_else_the_record_says():
    tiger = {"name": "Tiger", "conditions": ["Bless"]}
    link_concentration(tiger, "Bless", "Pirate")
    describe(tiger, "Bless", "Bless", None, SPELL)
    unlink_concentration(tiger, "Bless")
    effect = find_effect(tiger, "Bless")
    assert effect is not None and effect["concentration"] is None


# ---------------------------------------------------------------------------
# Dropping Bless removes it from every target


def _ctrl_c(ui, pirate):
    ui._select_character(pirate)
    ui._shortcut_remove_concentration()


def _failed_save(ui, pirate):
    pirate.setdefault("concentration_checks", []).append(10)
    ui._settle_concentration(pirate, 10, False)


def _incapacitated(ui, pirate):
    ui._add_condition_to(pirate, "Stunned", source=pirate)


def _another_concentration(ui, pirate):
    _cast(ui, pirate, "Hold Person", ui.characters[1])


def _ended_early(ui, pirate):
    ui._remove_active_spell(pirate, pirate["active_spells"][0])


def _leaves_the_fight(ui, pirate):
    ui._remove_from_fight(pirate)


def _killed(ui, pirate):
    ui._deal_damage(pirate, [(pirate["hp"] * 3, "Slashing")], None, True, False)


@pytest.mark.parametrize(
    "drop",
    [
        _ctrl_c,
        _failed_save,
        _incapacitated,
        _another_concentration,
        _ended_early,
        _leaves_the_fight,
        _killed,
    ],
)
def test_dropping_bless_removes_it_from_every_target(fight, drop):
    ui, pirate, tiger, bandit, cat = fight
    _cast(ui, pirate, "Bless", tiger, bandit, cat)
    assert all(_blessed(c) for c in (tiger, bandit, cat))
    drop(ui, pirate)
    for char in (tiger, bandit, cat):
        assert not _blessed(char), char["name"]
        assert modifiers_on(char) == []
    held = held_by_concentration(ui.characters, "Pirate")
    assert [e["name"] for _, e in held if e["name"] == "Bless"] == []


def test_bless_runs_out_after_a_minute_on_every_target(fight):
    ui, pirate, tiger, _, cat = fight
    _cast(ui, pirate, "Bless", tiger, cat)
    for _ in range(4 * 10):  # ten rounds of four turns
        ui._advance_turn()
    assert not _blessed(tiger) and not _blessed(cat)
    assert "Concentrating" not in pirate["conditions"]


def test_leaving_the_fight_is_logged_as_why_the_spell_ends(fight):
    ui, pirate, tiger, *_ = fight
    _cast(ui, pirate, "Bless", tiger)
    ui._remove_from_fight(pirate)
    log = str(ui._read_log())
    assert "Pirate's Bless ends (Pirate leaves the fight)" in log
    assert "Tiger loses Bless" in log


def test_a_dismissed_summon_ends_what_it_concentrates_on_and_undo_brings_it_back(
    fight,
):
    ui, pirate, tiger, *_ = fight
    _cast(ui, pirate, "Bless", tiger)
    ui._dismiss_summon(pirate)  # as if the Pirate were a summon
    assert not _blessed(tiger)
    ui._undo_last()
    assert _blessed(tiger)
    assert _concentration_of(tiger, "Bless") == "Pirate"


def test_a_creature_leaving_ends_only_its_own_concentration(fight):
    ui, pirate, tiger, bandit, cat = fight
    _cast(ui, pirate, "Bless", tiger)
    _cast(ui, bandit, "Bless", cat)
    ui._remove_from_fight(pirate)
    assert not _blessed(tiger)
    assert _blessed(cat)
    assert _concentration_of(cat, "Bless") == bandit["name"]


def test_a_creature_leaving_that_concentrates_on_nothing_ends_nothing(fight):
    ui, pirate, tiger, bandit, _ = fight
    _cast(ui, pirate, "Bless", tiger)
    ui._remove_from_fight(bandit)
    assert _blessed(tiger)


# ---------------------------------------------------------------------------
# The link: what ends, and who holds a badge two effects gave


def test_an_effect_linked_to_a_concentration_ends_with_it_without_an_active_spell(
    fight,
):
    """The record's link alone is enough: a badge linked to the Pirate's
    concentration ends with it, whatever its active spells say."""
    ui, pirate, tiger, *_ = fight
    ui._add_condition_to(pirate, "Concentrating", source=pirate)
    ui._add_condition_to(tiger, "Restrained", source=pirate)
    link_concentration(tiger, "Restrained", "Pirate")
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Restrained" not in tiger["conditions"]
    assert find_effect(tiger, "Restrained") is None


def test_unconscious_from_0_hp_stays_when_the_concentration_ends(fight):
    ui, pirate, tiger, *_ = fight
    ui._add_condition_to(pirate, "Concentrating", source=pirate)
    tiger["hp"] = 0
    ui._add_condition_to(tiger, "Unconscious", source=pirate)
    link_concentration(tiger, "Unconscious", "Pirate")
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Unconscious" in tiger["conditions"]
    assert _concentration_of(tiger, "Unconscious") is None


def test_a_badge_two_casters_hold_stays_linked_to_the_one_still_concentrating(
    fight,
):
    ui, pirate, tiger, bandit, cat = fight
    _cast(ui, pirate, "Bless", tiger, cat)
    _cast(ui, bandit, "Bless", tiger)
    assert _concentration_of(tiger, "Bless") == bandit["name"]
    ui._remove_condition_from(bandit, "Concentrating", source=bandit)
    assert _blessed(tiger), "the Pirate still holds it"
    assert _concentration_of(tiger, "Bless") == "Pirate"
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert not _blessed(tiger) and not _blessed(cat)


def test_the_first_caster_dropping_leaves_the_badge_to_the_second(fight):
    ui, pirate, tiger, bandit, _ = fight
    _cast(ui, pirate, "Bless", tiger)
    _cast(ui, bandit, "Bless", tiger)
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert _blessed(tiger)
    assert _concentration_of(tiger, "Bless") == bandit["name"]
    ui._remove_from_fight(bandit)
    assert not _blessed(tiger)


def test_a_badge_also_held_without_concentration_is_unlinked(fight):
    """A badge a spell without Concentration holds too stays, and no longer
    ends with anyone's concentration."""
    ui, pirate, tiger, bandit, _ = fight
    _cast(ui, pirate, "Bless", tiger)
    row = {"target": "Tiger", "condition": "Bless"}
    bandit["active_spells"] = [
        {
            "name": "Bless",
            "time_left": 60,
            "duration": 60,
            "concentration": False,
            "applied": [row],
            "ticks_on": None,
        }
    ]
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert _blessed(tiger)
    assert _concentration_of(tiger, "Bless") is None
