"""Lasting effects on a combatant (Combat/Effects/active_effects.py): one
char["active_effects"] list of plain dicts in place of the seven keys fight
logs kept them in before, and those older logs still replaying the same."""

import copy
import json
import random

import pytest
from PyQt6.QtWidgets import QLabel

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Combatants import Tiger
from Combat.Effects.active_effects import (
    CUSTOM,
    FEATURE,
    KEY,
    OLD_KEYS,
    SPELL,
    active_effects,
    describe,
    drop_repeat_save,
    duration_entry,
    effect_for,
    ending_conditions,
    find_effect,
    link_concentration,
    new_effect,
    note_origin,
    remove_effect,
    repeat_saves,
    set_duration,
    set_repeat_save,
    tick,
    timed_effects,
    timers,
    upgrade_old_keys,
)
from Combat.CombatUIQt.saves import CustomEffect
from Combat.EncounterLogs import PLAYER_FIGHT_STATE_KEY
from Combat.PlayerLog import is_round_key
from tests._combat_ui import make_ui

SAVE = {
    "ability": "WIS",
    "dc": 15,
    "mode": "Neutral",
    "use_legendary_resistance": False,
    "also": ["Prone"],
}

# ---------------------------------------------------------------------------
# The record and its helpers
# ---------------------------------------------------------------------------


def test_an_effect_says_where_it_came_from_and_how_it_ends():
    char: dict = {}
    describe(char, "Bless", "<b>Bless</b>", "#123456", SPELL)
    note_origin(char, "Bless", source="Bless", caster="Edmund")
    link_concentration(char, "Bless", "Edmund")
    assert active_effects(char) == [
        {
            **new_effect("Bless"),
            "source": "Bless",
            "caster": "Edmund",
            "concentration": "Edmund",
            "tooltip": "<b>Bless</b>",
            "tooltip_from": SPELL,
            "color": "#123456",
        }
    ]
    # Plain data: what a fight log writes and reads back.
    assert json.loads(json.dumps(char)) == char


def test_note_origin_only_fills_in_an_effect_there_is():
    char: dict = {}
    note_origin(char, "Hexed", source="Hex", caster="Kivi")
    assert KEY not in char
    effect_for(char, "Hexed")
    note_origin(char, "Hexed", caster="Kivi")
    note_origin(char, "Hexed", source="Hex")
    effect = find_effect(char, "Hexed")
    assert effect is not None
    assert (effect["source"], effect["caster"]) == ("Hex", "Kivi")


def test_a_spells_card_stays_over_the_notes_typed_for_it():
    """The order _give_effect_condition writes them in: the pick's card,
    then the notes. The card used to win by its map coming first."""
    char: dict = {}
    describe(char, "Bless", "notes + card", "#123456", SPELL)
    describe(char, "Bless", "notes", None, CUSTOM)
    effect = find_effect(char, "Bless")
    assert effect is not None
    assert (effect["tooltip"], effect["color"]) == ("notes + card", "#123456")


def test_a_higher_kind_replaces_a_lower_one_and_its_colour():
    char: dict = {}
    describe(char, "Marked", "typed", None, CUSTOM)
    describe(char, "Marked", "feature", "#4c7ac9", FEATURE)
    describe(char, "Marked", "spell", "#123456", SPELL)
    effect = find_effect(char, "Marked")
    assert effect is not None
    assert (effect["tooltip"], effect["tooltip_from"], effect["color"]) == (
        "spell",
        SPELL,
        "#123456",
    )


def test_the_same_kind_without_a_colour_keeps_the_colour():
    """A monster action's rules text (a feature tooltip with no colour) over
    a feature's badge kept the feature's colour."""
    char: dict = {}
    describe(char, "Grappled", "feature", "#4c7ac9", FEATURE)
    describe(char, "Grappled", "action text", None, FEATURE)
    effect = find_effect(char, "Grappled")
    assert effect is not None
    assert (effect["tooltip"], effect["color"]) == ("action text", "#4c7ac9")


def test_a_lower_kind_over_nothing_brings_no_colour():
    char: dict = {}
    describe(char, "Grappled", "action text", None, FEATURE)
    effect = find_effect(char, "Grappled")
    assert effect is not None
    assert effect["color"] is None


def test_removing_the_last_effect_drops_the_key():
    char: dict = {}
    describe(char, "A", "a", None, CUSTOM)
    describe(char, "B", "b", None, CUSTOM)
    remove_effect(char, "A")
    assert [e["name"] for e in active_effects(char)] == ["B"]
    remove_effect(char, "B")
    assert KEY not in char
    remove_effect(char, "B")  # nothing to remove
    assert KEY not in char


def test_a_duration_given_again_goes_last():
    """The card lists timers in the order given, as the timer list did."""
    char: dict = {}
    set_duration(char, "A", {"time_left": 6, "duration": 6, "ticks_on": None})
    set_duration(char, "B", {"time_left": 6, "duration": 6, "ticks_on": None})
    set_duration(char, "A", {"time_left": 60, "duration": 60, "ticks_on": None})
    assert [e["name"] for e in timed_effects(char)] == ["B", "A"]


def test_no_duration_clears_it_and_an_empty_effect_goes():
    char: dict = {}
    set_duration(char, "A", {"time_left": 6, "duration": 6, "ticks_on": None})
    describe(char, "B", "note", None, CUSTOM)
    set_duration(char, "B", {"time_left": 6, "duration": 6, "ticks_on": None})
    set_duration(char, "A", None)
    set_duration(char, "B", None)
    assert find_effect(char, "A") is None  # nothing left in it
    effect = find_effect(char, "B")
    assert effect is not None
    assert (effect["duration"], effect["tooltip"]) == (None, "note")
    set_duration(char, "C", None)  # nothing to clear
    assert find_effect(char, "C") is None


def test_duration_entry():
    assert duration_entry(None, "Pirate", "Tiger", ["Pirate"]) is None
    assert duration_entry({"seconds": 60}, "Pirate", "Tiger", ["Pirate"]) == {
        "time_left": 60,
        "duration": 60,
        "ticks_on": "Pirate",
    }
    outside_combat = duration_entry({"seconds": 6}, None, "Tiger", [])
    assert outside_combat is not None and outside_combat["ticks_on"] is None
    # The end of the source's next turn, given on its turn, is a turn later.
    assert duration_entry(
        {"until": "end", "of": "source"}, "Pirate", "Tiger", ["Pirate"]
    ) == {
        "until": "end",
        "of": "Pirate",
        "turns_left": 2,
        "text": "Until the end of Pirate's next turn",
    }
    start = duration_entry({"until": "start", "of": "target"}, "Pirate", "Tiger", [])
    assert start is not None and (start["of"], start["turns_left"]) == ("Tiger", 1)
    assert duration_entry({"until": "end", "of": "source"}, None, "Tiger", []) is None


def test_tick_a_timer():
    timer = {"time_left": 12, "duration": 12, "ticks_on": "Pirate"}
    assert not tick(timer, {"Tiger"}, {"Pirate"}, False, {"Pirate", "Tiger"})
    assert timer["time_left"] == 6
    assert not tick(timer, {"Pirate"}, {"Tiger"}, False, {"Pirate", "Tiger"})
    assert timer["time_left"] == 6
    # Its combatant has no turn any more: it counts at the round's start.
    assert tick(timer, {"Tiger"}, {"Wolf"}, True, {"Tiger", "Wolf"})


def test_tick_a_turn_edge():
    edge = {"until": "end", "of": "Pirate", "turns_left": 2, "text": ""}
    assert not tick(edge, {"Pirate"}, {"Tiger"}, False, set())
    assert not tick(edge, {"Tiger"}, {"Pirate"}, True, set())
    assert tick(edge, {"Pirate"}, {"Tiger"}, False, set())


def test_a_repeat_save_and_dropping_it():
    char: dict = {}
    set_repeat_save(char, "Paralyzed", "WIS", 15, "Neutral", False, ["Prone"])
    describe(char, "Prone", "note", None, CUSTOM)
    assert [e["name"] for e in repeat_saves(char)] == ["Paralyzed"]
    effect = find_effect(char, "Paralyzed")
    assert effect is not None
    assert effect["repeat_save"] == SAVE
    drop_repeat_save(char, "Paralyzed")
    assert repeat_saves(char) == []
    assert find_effect(char, "Paralyzed") is None
    drop_repeat_save(char, "Prone")  # it has none: its note stays
    assert find_effect(char, "Prone") is not None


def test_ending_conditions():
    char = {
        KEY: [
            {**new_effect("Poisoned"), "duration": {"time_left": 6}},
            {**new_effect("Paralyzed"), "repeat_save": SAVE},
            {**new_effect("Bless"), "tooltip": "card"},
        ]
    }
    assert ending_conditions(char) == {"Poisoned", "Paralyzed", "Prone"}


# ---------------------------------------------------------------------------
# Older logs: the seven keys before active_effects
# ---------------------------------------------------------------------------

# A Tiger as the encounter log's combatants kept it before active_effects,
# each key written the way ConditionsMixin, SpellsMixin and FeaturesMixin
# wrote them.
OLD_TIGER_KEYS = {
    "timed_conditions": [
        {"name": "Hexed", "time_left": 6, "duration": 60, "ticks_on": "Edmund"},
        {
            "name": "Sapped",
            "until": "end",
            "of": "Tiger",
            "turns_left": 1,
            "text": "Until the end of Tiger's next turn",
        },
    ],
    "repeat_saves": [
        {
            "condition": "Paralyzed",
            "ability": "WIS",
            "dc": 15,
            "mode": "Neutral",
            "use_legendary_resistance": False,
            "also": ["Prone"],
        }
    ],
    "custom_condition_descriptions": {
        "Hexed": "Extra 1d6 necrotic",
        "Bless": "typed with the spell",
    },
    "spell_condition_descriptions": {"Bless": "<b>Bless</b> card"},
    "spell_condition_colors": {"Bless": "#123456"},
    "feature_condition_descriptions": {"Turned": "<b>Turn Undead</b> card"},
    "feature_condition_colors": {"Turned": "#4c7ac9"},
}
# The same Tiger as active_effects says it.
NEW_TIGER_EFFECTS = [
    {
        **new_effect("Hexed"),
        "duration": {"time_left": 6, "duration": 60, "ticks_on": "Edmund"},
        "tooltip": "Extra 1d6 necrotic",
        "tooltip_from": CUSTOM,
    },
    {
        **new_effect("Sapped"),
        "duration": {
            "until": "end",
            "of": "Tiger",
            "turns_left": 1,
            "text": "Until the end of Tiger's next turn",
        },
    },
    {**new_effect("Paralyzed"), "repeat_save": SAVE},
    {
        **new_effect("Bless"),
        "tooltip": "<b>Bless</b> card",
        "tooltip_from": SPELL,
        "color": "#123456",
    },
    {
        **new_effect("Turned"),
        "tooltip": "<b>Turn Undead</b> card",
        "tooltip_from": FEATURE,
        "color": "#4c7ac9",
    },
]
TIGER_CONDITIONS = ["Hexed", "Sapped", "Paralyzed", "Prone", "Bless", "Turned"]

# A player's part of a fight (PLAYER_FIGHT_STATE_KEY), before and after.
OLD_EDMUND_STATE = {
    "timed_conditions": [
        {"name": "Slowed", "time_left": 60, "duration": 60, "ticks_on": "Edmund"}
    ],
    "custom_condition_descriptions": {"Slowed": "Half speed"},
    "repeat_saves": [
        {
            "condition": "Frightened",
            "ability": "WIS",
            "dc": 13,
            "mode": "Neutral",
            "use_legendary_resistance": False,
        }
    ],
}
NEW_EDMUND_STATE = {
    KEY: [
        {
            **new_effect("Slowed"),
            "duration": {"time_left": 60, "duration": 60, "ticks_on": "Edmund"},
            "tooltip": "Half speed",
            "tooltip_from": CUSTOM,
        },
        {
            **new_effect("Frightened"),
            "repeat_save": {**SAVE, "dc": 13, "also": []},
        },
    ]
}


def test_old_keys_become_effects():
    char = {"name": "Tiger", "hp": 3, **copy.deepcopy(OLD_TIGER_KEYS)}
    assert upgrade_old_keys(char) is char
    assert char == {"name": "Tiger", "hp": 3, KEY: NEW_TIGER_EFFECTS}
    assert upgrade_old_keys(copy.deepcopy(OLD_EDMUND_STATE)) == NEW_EDMUND_STATE


def test_a_dict_without_old_keys_is_left_as_it_is():
    char = {"name": "Tiger", KEY: copy.deepcopy(NEW_TIGER_EFFECTS)}
    assert upgrade_old_keys(char) == {"name": "Tiger", KEY: NEW_TIGER_EFFECTS}


def test_old_keys_read_as_leniently_as_before():
    """The old readers (Summons, PartyAllies) took entries without their
    other keys."""
    char = {
        "timed_conditions": [{"name": "Frightened"}, {}],
        "repeat_saves": [{"condition": "Restrained"}],
        "custom_condition_descriptions": {"Empty": ""},
    }
    upgrade_old_keys(char)
    assert [e["name"] for e in active_effects(char)] == ["Frightened", "Restrained"]
    assert set(char) == {KEY}


def test_ending_conditions_of_an_old_log_leaves_it_alone():
    old = {"conditions": TIGER_CONDITIONS, **copy.deepcopy(OLD_TIGER_KEYS)}
    before = copy.deepcopy(old)
    assert ending_conditions(old) == {"Hexed", "Sapped", "Paralyzed", "Prone"}
    assert old == before


# ---------------------------------------------------------------------------
# Replaying an older fight log
# ---------------------------------------------------------------------------


def _log_with(tmp_path, tiger_keys: dict, edmund_state: dict) -> str:
    """A fight log on the Tiger's turn of round 1 (Edmund 15, Tiger 10), its
    Tiger with `tiger_keys` and Edmund's part of the fight `edmund_state`."""
    ui = make_ui(tmp_path / "written", [Tiger()], [Edmund().build()])
    edmund, tiger = ui.characters
    ui._initiative_inputs[id(edmund)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._advance_turn()  # the Tiger's turn
    assert ui.log_file is not None
    data = json.loads(ui.log_file.read_text(encoding="utf-8"))
    (saved,) = data["combatants"]
    saved["conditions"] = list(TIGER_CONDITIONS)
    saved.update(copy.deepcopy(tiger_keys))
    data[PLAYER_FIGHT_STATE_KEY] = {"Edmund": copy.deepcopy(edmund_state)}
    path = tmp_path / "fight.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def _events(ui) -> list[str]:
    data = ui._read_log()
    return [
        event["text"]
        for key in sorted((k for k in data if is_round_key(k)), key=lambda k: k)
        for event in data[key]
    ]


def _play(tmp_path, monkeypatch, tiger_keys: dict, edmund_state: dict) -> dict:
    """Continue the log of _log_with and pass two turns: the Tiger's ends
    (its turn-edge timer runs out and it repeats its save), round 2 starts on
    Edmund's turn (the Tiger's one-round timer runs out), and Edmund's ends
    (a reminder of his save). What a GM sees along the way."""
    path = _log_with(tmp_path, tiger_keys, edmund_state)
    monkeypatch.setattr(random, "randint", lambda low, high: high)
    ui = make_ui(tmp_path / "read", [], [Edmund().build()])
    edmund = ui.characters[0]
    edmund["conditions"] += ["Slowed", "Frightened"]
    ui._load_log_from_path(path)
    tiger = next(c for c in ui.characters if c["name"] == "Tiger")
    seen: dict = {
        "effects": [copy.deepcopy(c.get(KEY)) for c in ui.characters],
        "old keys": [sorted(set(OLD_KEYS) & set(c)) for c in ui.characters],
        "badges": {
            cond: ui._condition_description_and_color(tiger, cond)
            for cond in TIGER_CONDITIONS
        },
        "edmund badges": {
            cond: ui._condition_description_and_color(edmund, cond)
            for cond in ("Slowed", "Frightened")
        },
        "tiger card": _card_texts(ui, tiger),
        "edmund card": _card_texts(ui, edmund),
    }
    lines_before = len(_events(ui))
    ui._advance_turn()  # round 2, Edmund's turn
    seen["tiger after its turn"] = list(tiger["conditions"])
    seen["edmund timer"] = [t["time_left"] for t in timers(edmund)]
    ui._advance_turn()  # Edmund's turn ends
    seen["lines"] = _events(ui)[lines_before:]
    seen["reminders"] = ui._turn_reminders_label.text()
    ui._undo_last()
    ui._undo_last()
    seen["undone"] = [copy.deepcopy(c.get(KEY)) for c in ui.characters]
    return seen


def _card_texts(ui, char) -> list[str]:
    ui._rebuild_card(char)
    return [lbl.text() for lbl in ui._card_widgets[id(char)].findChildren(QLabel)]


@pytest.fixture
def old_and_new(tmp_path, monkeypatch):
    old = _play(tmp_path / "old", monkeypatch, OLD_TIGER_KEYS, OLD_EDMUND_STATE)
    new = _play(
        tmp_path / "new",
        monkeypatch,
        {KEY: NEW_TIGER_EFFECTS},
        NEW_EDMUND_STATE,
    )
    return old, new


def test_an_old_fight_log_replays_as_a_new_one(old_and_new):
    old, new = old_and_new
    assert old == new


def _before_modifiers(effects: list[dict]) -> list[dict]:
    """Records as a log from before step 3.3 has them: no `modifiers`."""
    return [{k: v for k, v in e.items() if k != "modifiers"} for e in effects]


def test_a_log_from_before_modifiers_replays_as_a_new_one(
    old_and_new, tmp_path, monkeypatch
):
    """A 3.1 log's records have no `modifiers`: they read as having none,
    so its Bless badge adds nothing, as before."""
    _, new = old_and_new
    before = _play(
        tmp_path / "before",
        monkeypatch,
        {KEY: _before_modifiers(NEW_TIGER_EFFECTS)},
        {KEY: _before_modifiers(NEW_EDMUND_STATE[KEY])},
    )
    assert before == new
    assert all(e["modifiers"] == [] for effects in before["effects"] for e in effects)


def test_an_old_fight_log_reads_as_the_old_code_showed_it(old_and_new):
    """What the old keys meant, as the old card and turn code used them."""
    old, _ = old_and_new
    assert old["old keys"] == [[], []]
    assert old["effects"] == [NEW_EDMUND_STATE[KEY], NEW_TIGER_EFFECTS]
    # A spell's card over the notes typed with it; its colour; a feature's.
    assert old["badges"]["Bless"] == ("<b>Bless</b> card", "#123456")
    assert old["badges"]["Turned"] == ("<b>Turn Undead</b> card", "#4c7ac9")
    assert old["badges"]["Hexed"] == ("Extra 1d6 necrotic", None)
    assert old["edmund badges"]["Slowed"] == ("Half speed", None)
    # The timers, in their order, on the card.
    card = old["tiger card"]
    timers = card[card.index("Timed Conditions:") + 1 :]
    assert timers[:3] == ["Hexed", "Sapped", "Until the end of Tiger's next turn"]
    assert "Timed Conditions:" in old["edmund card"]
    # The turn-edge timer, the save (ending Prone too) and the one-round timer.
    lines = "\n".join(old["lines"])
    assert "Tiger's Sapped expires" in lines
    assert "Tiger ends Paralyzed and Prone with a DC 15 Wisdom save" in lines
    assert "Tiger's Hexed expires" in lines
    assert old["tiger after its turn"] == ["Bless", "Turned"]
    assert old["edmund timer"] == [54]
    assert "Edmund: DC 13 Wisdom save to end Frightened" in old["reminders"]
    # Undo puts back what was read.
    assert old["undone"] == old["effects"]


@pytest.mark.parametrize("modifiers", [{}, {"modifiers": []}], ids=["3.1", "3.3"])
def test_a_mark_from_before_extra_damage_adds_nothing(tmp_path, monkeypatch, modifiers):
    """A Hunter's Mark badge from a 3.1 log (no `modifiers`) or a 3.3 one
    (none yet): its caster's hit deals its own damage only, as it did then,
    and nothing is rolled for the mark."""
    mark = {
        **new_effect("Hunter's Mark"),
        "source": "Hunter's Mark",
        "caster": "Edmund",
        "concentration": "Edmund",
        "tooltip": "<b>Hunter's Mark</b> card",
        "tooltip_from": SPELL,
    }
    mark.pop("modifiers")
    tiger_keys = {"conditions": ["Hunter's Mark"], KEY: [{**mark, **modifiers}]}
    path = _log_with(tmp_path, tiger_keys, {})
    ui = make_ui(tmp_path / "read", [], [Edmund().build()])
    ui._load_log_from_path(path)
    edmund = ui.characters[0]
    tiger = next(c for c in ui.characters if c["name"] == "Tiger")
    hp = tiger["hp"]
    rolled = []
    monkeypatch.setattr(random, "randint", lambda low, high: rolled.append(high) or 15)
    ui._select_character(edmund)
    ui._set_targets([tiger])
    ui._apply_custom_effect(
        CustomEffect(name="Longsword", damage=[(6, "Slashing")], attack_bonus=6)
    )
    assert rolled == [20, 20]
    assert tiger["hp"] == hp - 6
    record = find_effect(tiger, "Hunter's Mark")
    assert record is not None and record["modifiers"] == []
