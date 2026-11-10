"""What a lasting effect does as a turn starts or ends (Notes/combat-effects-plan.md,
step 3.5): AtTurnStart and AtTurnEnd, as data, as Combat/Effects/triggers.py
finds them, and in the combat window.

Expected values come from the two spells' text. Heroism: "Until the spell
ends, the creature is immune to the Frightened condition and gains Temporary
Hit Points equal to your spellcasting ability modifier at the start of each
of its turns." Spirit Guardians: "whenever a creature enters the Emanation or
ends its turn there, the creature must make a Wisdom saving throw. On a
failed save, the creature takes 3d8 Radiant damage ... On a successful save,
the creature takes half as much damage." Where a creature is, the simulator
doesn't know (principle 8), so that one is a prompt. Temporary Hit Points
don't stack: the higher amount is kept (Rules Glossary, Temporary Hit
Points)."""

import json
import random

import pytest
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeWidget,
)

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.PartyAllies import mark
from Combat.CombatUIQt.effect_options import spell_options, trigger_option
from Combat.CombatUIQt.saves import TEMP_HP
from Combat.Effects.active_effects import find_effect, give_modifiers, note_origin
from Combat.Effects.modifiers import immune_to_condition
from Combat.Effects.triggers import firings, on_party_side
from Model.Content.CombatEffect import CombatHitPoints
from Model.Content.CombatModifiers import (
    AtTurnEnd,
    AtTurnStart,
    WhoseTurn,
    modifier_from_dict,
    modifier_to_dict,
)
from tests._combat_ui import make_ui, open_dialog

HEROISM = AtTurnStart("Heroism: Temporary Hit Points")
GUARDIANS = AtTurnEnd(
    "Spirit Guardians: damage",
    WhoseTurn.ENEMY,
    when="it ends its turn in the Emanation",
)

# ---------------------------------------------------------------------------
# As data


@pytest.mark.parametrize("trigger", [HEROISM, GUARDIANS])
def test_a_trigger_reads_back_as_it_was_written(trigger):
    data = modifier_to_dict(trigger)
    assert json.loads(json.dumps(data)) == data
    assert modifier_from_dict(data) == trigger


def test_a_trigger_is_written_with_only_what_isnt_default():
    assert modifier_to_dict(HEROISM) == {
        "type": "AtTurnStart",
        "effect": "Heroism: Temporary Hit Points",
    }
    assert modifier_to_dict(GUARDIANS) == {
        "type": "AtTurnEnd",
        "effect": "Spirit Guardians: damage",
        "whose": "enemy",
        "when": "it ends its turn in the Emanation",
    }


@pytest.mark.parametrize(
    "data",
    [
        {"type": "AtTurnStart"},  # no effect
        {"type": "AtTurnStart", "effect": ""},
        {"type": "AtTurnStart", "effect": 3},
        {"type": "AtTurnEnd", "effect": "x", "whose": "enemies"},
        {"type": "AtTurnEnd", "effect": "x", "turn": "end"},
        {"type": "AtTurnMiddle", "effect": "x"},
    ],
)
def test_a_trigger_that_isnt_one_is_refused(data):
    with pytest.raises(ValueError, match="Invalid modifier of Heroism"):
        modifier_from_dict(data, "Heroism")


def test_a_trigger_needs_a_whose_turn_in_python():
    with pytest.raises(ValueError, match="WhoseTurn"):
        AtTurnEnd("x", "enemy")  # pyright: ignore[reportArgumentType]


def test_hit_points_of_the_modifier_alone_are_allowed():
    assert CombatHitPoints(add_modifier=True).dice == ""


def _badges(spell: str) -> dict:
    return {
        condition.name: condition.modifiers
        for effect in SpellFactory.create(spell).combat_effects() or []
        for condition in effect.conditions
    }


def test_heroism_and_spirit_guardians_say_what_their_badges_do():
    immunity, trigger = _badges("Heroism")["Heroism"]
    assert trigger == HEROISM
    assert immunity.conditions == ("Frightened",)
    assert _badges("Spirit Guardians")["Spirit Guardians"] == (GUARDIANS,)


def test_each_trigger_names_a_row_of_its_own_spell_that_spends_nothing():
    for spell, trigger in (("Heroism", HEROISM), ("Spirit Guardians", GUARDIANS)):
        rows = {o.name: o for o in spell_options(SpellFactory.create(spell), {})}
        assert trigger.effect in rows
        assert not rows[trigger.effect].counts_uses
        assert rows[trigger.effect].slot_level is None


# ---------------------------------------------------------------------------
# What comes with a turn (plain dicts)


def _with(name: str, badge: str, trigger, caster: str | None, **keys) -> dict:
    char = {"name": name, "conditions": [badge], **keys}
    give_modifiers(char, badge, (trigger,))
    note_origin(char, badge, source=badge, caster=caster)
    return char


def test_a_bearers_trigger_comes_with_its_own_turn_only():
    hero = _with("Edmund", "Heroism", HEROISM, "Edmund", _is_player=True)
    tiger = {"name": "Tiger", "conditions": []}
    chars = [hero, tiger]
    find = {c["name"]: c for c in chars}.get
    (firing,) = firings(chars, [hero], AtTurnStart, find)
    assert (firing.badge, firing.target, firing.caster) == ("Heroism", hero, "Edmund")
    assert not firing.is_prompt
    assert firings(chars, [tiger], AtTurnStart, find) == []
    assert firings(chars, [hero], AtTurnEnd, find) == []


def test_a_trigger_counts_only_while_its_badge_is_on():
    hero = _with("Edmund", "Heroism", HEROISM, "Edmund")
    hero["conditions"] = []
    assert firings([hero], [hero], AtTurnStart, lambda name: hero) == []


def test_an_enemy_turn_trigger_comes_with_each_enemy_of_its_caster_once():
    """Cast Spell puts Spirit Guardians' badge on the enemies it's aimed at:
    each of them asks once at the end of its own turn, and once only."""
    cleric = {"name": "Obmar", "conditions": [], "_is_player": True}
    ally = {"name": "Kivi", "conditions": [], "_is_player": True}
    tiger = _with("Tiger", "Spirit Guardians", GUARDIANS, "Obmar")
    pirate = _with("Pirate", "Spirit Guardians", GUARDIANS, "Obmar")
    chars = [cleric, ally, tiger, pirate]
    find = {c["name"]: c for c in chars}.get
    (firing,) = firings(chars, [tiger], AtTurnEnd, find)
    assert firing.target is tiger
    assert firing.is_prompt
    assert firing.prompt == (
        "Tiger: if it ends its turn in the Emanation,"
        " Obmar's Spirit Guardians: damage"
    )
    assert firings(chars, [ally], AtTurnEnd, find) == []
    assert firings(chars, [cleric], AtTurnEnd, find) == []
    assert firings(chars, [tiger], AtTurnStart, find) == []


def test_an_enemy_turn_trigger_on_its_caster_asks_about_every_enemy():
    cleric = _with("Obmar", "Spirit Guardians", GUARDIANS, "Obmar", _is_player=True)
    summon = {"name": "Wolf", "conditions": [], "summon_of": "Obmar"}
    tiger = {"name": "Tiger", "conditions": []}
    chars = [cleric, summon, tiger]
    find = {c["name"]: c for c in chars}.get
    assert [f.target for f in firings(chars, [tiger], AtTurnEnd, find)] == [tiger]
    assert firings(chars, [summon], AtTurnEnd, find) == []


def test_an_enemy_turn_trigger_without_its_caster_asks_nothing():
    tiger = _with("Tiger", "Spirit Guardians", GUARDIANS, "Obmar")
    assert firings([tiger], [tiger], AtTurnEnd, lambda name: None) == []


def test_the_party_side_is_players_allies_and_their_summons():
    assert on_party_side({"_is_player": True})
    assert on_party_side(mark({"name": "Hugo"}))
    assert on_party_side({"summon_of": "Obmar"})
    assert not on_party_side({"name": "Tiger"})


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
    """Edmund (15, a Paladin: Charisma +2), a Tiger (10) and a Pirate (5)."""
    ui = make_ui(tmp_path, [Tiger(), Pirate()], [Edmund().build()])
    edmund, tiger, pirate = ui.characters
    for char, value in zip(ui.characters, (15, 10, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    return ui, edmund, tiger, pirate


def _cast(ui, caster, spell: str, slot: int, *targets):
    ui._select_character(caster)
    ui._set_targets(list(targets))
    ui._apply_cast_spell(SpellFactory.create(spell), slot)


def _round(ui):
    for _ in ui.initiative_order:
        ui._advance_turn()


def _events(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def test_heroisms_temp_hp_row_is_the_casters_modifier(fight):
    _, edmund, _, _ = fight
    option = trigger_option(edmund, "Heroism", HEROISM.effect)
    assert option is not None
    assert (option.amount_kind, option.damage_at(None)) == (TEMP_HP, "2")


def test_a_modifier_alone_not_known_is_typed_in():
    (option,) = [
        o
        for o in spell_options(SpellFactory.create("Heroism"), {})
        if o.name == HEROISM.effect
    ]
    assert option.rolls == ()
    assert "Type in the spellcasting ability modifier" in option.note


def test_heroism_makes_its_target_immune_to_frightened(fight):
    ui, edmund, _, _ = fight
    _cast(ui, edmund, "Heroism", 1, edmund)
    assert immune_to_condition(edmund, "Frightened")
    effect = find_effect(edmund, "Heroism")
    assert effect is not None
    assert modifier_to_dict(HEROISM) in effect["modifiers"]


def test_heroism_gives_temp_hp_at_the_start_of_each_of_its_turns(fight):
    """Cast on Edmund's turn: none then, 2 as his next turn starts, none on
    the others' turns."""
    ui, edmund, tiger, _ = fight
    _cast(ui, edmund, "Heroism", 1, edmund)
    assert edmund.get("temp_hp", 0) == 0
    ui._advance_turn()  # the Tiger's
    ui._advance_turn()  # the Pirate's
    assert edmund.get("temp_hp", 0) == 0
    ui._advance_turn()  # Edmund's
    assert edmund["temp_hp"] == 2
    assert ui._turn_reminders[0] == "Heroism: 2 temp HP for Edmund"
    assert "Edmund gains 2 temp HP from Edmund" in _events(ui)
    assert tiger.get("temp_hp", 0) == 0


def test_heroisms_temp_hp_dont_stack_but_come_back(fight):
    ui, edmund, _, _ = fight
    _cast(ui, edmund, "Heroism", 1, edmund)
    _round(ui)
    edmund["temp_hp"] = 1  # a hit took one
    _round(ui)
    assert edmund["temp_hp"] == 2
    edmund["temp_hp"] = 5  # more from elsewhere: the higher is kept
    _round(ui)
    assert edmund["temp_hp"] == 5


def test_heroism_on_another_gives_them_the_casters_modifier(fight):
    ui, edmund, tiger, _ = fight
    _cast(ui, edmund, "Heroism", 1, tiger)
    ui._advance_turn()  # the Tiger's
    assert tiger["temp_hp"] == 2
    assert "Tiger gains 2 temp HP from Edmund" in _events(ui)


def test_undoing_next_takes_heroisms_temp_hp_back(fight):
    ui, edmund, _, _ = fight
    _cast(ui, edmund, "Heroism", 1, edmund)
    ui._advance_turn()
    ui._advance_turn()
    ui._advance_turn()
    ui._undo_last()
    edmund = ui._find_character_by_name("Edmund")
    assert edmund.get("temp_hp", 0) == 0


def test_heroism_ends_with_its_badge(fight):
    ui, edmund, _, _ = fight
    _cast(ui, edmund, "Heroism", 1, edmund)
    ui._remove_condition_from(edmund, "Heroism")
    _round(ui)
    assert edmund.get("temp_hp", 0) == 0
    assert not immune_to_condition(edmund, "Frightened")


def test_a_broken_concentration_ends_heroism(fight):
    """Concentrating on another spell ends Heroism: no more temp HP (those
    gained stay, as Temporary Hit Points last until they're lost)."""
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Heroism", 1, edmund)
    _round(ui)
    assert edmund["temp_hp"] == 2
    edmund["temp_hp"] = 0
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    _round(ui)
    assert "Heroism" not in edmund["conditions"]
    assert edmund.get("temp_hp", 0) == 0


def test_spirit_guardians_asks_about_each_enemy_ending_its_turn(fight):
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    ui._advance_turn()  # the Tiger's starts: nothing yet
    assert ui._turn_prompts == []
    ui._advance_turn()  # the Tiger's ended
    (prompt,) = ui._turn_prompts
    assert prompt.prompt == (
        "Tiger: if it ends its turn in the Emanation,"
        " Edmund's Spirit Guardians: damage"
    )
    buttons = [
        b.text()
        for b in ui._turn_prompts_box.findChildren(QPushButton)
        if b.isVisibleTo(ui._turn_prompts_box)
    ]
    assert buttons == [prompt.prompt]
    ui._advance_turn()  # the Pirate's ended
    assert [p.target["name"] for p in ui._turn_prompts] == ["Pirate"]
    ui._advance_turn()  # Edmund's ended: he's the caster
    assert ui._turn_prompts == []


def test_spirit_guardians_rolls_nothing_by_itself(fight, monkeypatch):
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    hp = tiger["hp"]
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _round(ui)
    assert tiger["hp"] == hp
    assert not any("Wisdom save" in e or "WIS" in e for e in _events(ui))


def test_spirit_guardians_on_the_caster_asks_about_the_enemies_too(fight):
    """The dialog gives the badge to whoever is targeted: the caster here."""
    ui, edmund, tiger, _ = fight
    give_modifiers(edmund, "Spirit Guardians", (GUARDIANS,))
    note_origin(edmund, "Spirit Guardians", "Spirit Guardians", "Edmund")
    edmund["conditions"].append("Spirit Guardians")
    ui._advance_turn()
    ui._advance_turn()
    assert [p.target for p in ui._turn_prompts] == [tiger]


def test_a_prompt_opens_the_dialog_with_its_row_picked(fight, monkeypatch):
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    ui._advance_turn()
    ui._advance_turn()
    (prompt,) = ui._turn_prompts
    ui._select_character(pirate)
    monkeypatch.undo()  # the dialog's exec, for open_dialog
    dlg = open_dialog(monkeypatch, lambda: ui._use_turn_prompt(prompt))
    assert ui.selected_character is edmund
    assert ui.target_characters == [tiger]
    assert ui._turn_prompts == []
    assert dlg.findChild(QLineEdit, "effectName").text() == ("Spirit Guardians: damage")
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    current = tree.currentItem()
    assert current is not None and current.text(0) == "Spirit Guardians: damage"
    slot = dlg.findChild(QComboBox, "spellSlot")
    assert slot.currentData() is None  # it spends no slot


def test_applying_a_prompts_row_rolls_the_wisdom_save(fight, monkeypatch):
    """A failed save (a 1 on the d20): 3d8 Radiant, every die a 1."""
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    slots = dict(edmund["spell_slots"])
    ui._advance_turn()
    ui._advance_turn()
    (prompt,) = ui._turn_prompts
    monkeypatch.undo()
    dlg = open_dialog(monkeypatch, lambda: ui._use_turn_prompt(prompt))
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    hp = tiger["hp"]
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()
    assert tiger["hp"] == hp - 3
    assert any("fails a DC" in e and "save" in e for e in _events(ui)), _events(ui)
    assert edmund["spell_slots"] == slots


def test_a_prompt_about_a_creature_gone_says_so(fight):
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    ui._advance_turn()
    ui._advance_turn()
    (prompt,) = ui._turn_prompts
    ui.characters.remove(tiger)
    ui._use_turn_prompt(prompt)  # no dialog
    assert ui._turn_prompts == [prompt]


def test_no_prompt_about_a_dead_creature(fight):
    ui, edmund, tiger, pirate = fight
    _cast(ui, edmund, "Spirit Guardians", 3, tiger, pirate)
    ui._advance_turn()
    tiger["hp"] = 0
    assert ui._char_death_state(tiger) == "dead"
    ui._advance_turn()
    assert ui._turn_prompts == []


def test_a_fight_without_triggers_has_no_prompts_or_notes(fight):
    ui, edmund, _, _ = fight
    for _ in ui.initiative_order:
        ui._advance_turn()
        assert ui._turn_prompts == []
        assert not any("temp HP" in r for r in ui._turn_reminders)
    assert edmund.get("temp_hp", 0) == 0
