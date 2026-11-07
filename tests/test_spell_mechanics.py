"""Checked spell mechanics (CharacterContent/Spells/spells_<source>_mechanics.json,
read by SpellFactory/Mechanics.py) and how the combat UI's Custom Effect
picker fills its form from them instead of reading the spell's text.

Expected values come from each spell's 2024 rules text, read by hand: Fireball
is a Dexterity save for 8d6 Fire, half on a success, 1d6 more per slot level
above 3; Toll the Dead is 1d8 Necrotic, 3d8 from character level 11; and so on.
"""

import json
import os
import re

import pytest

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory
from CharacterContent.Spells.SpellFactory.Mechanics import (
    SpellMechanics,
    parse_mechanics,
)
from Combat.CombatUIQt.effect_options import (
    ALL_SPELLS,
    effect_options,
    is_applicable,
    read_effect_text,
    spell_option,
)
from Combat.CombatUIQt.saves import ATTACK_ROLL, SAVING_THROW

SOURCE = "CharacterContent/Spells/spells_dnd2024.json"
MECHANICS = SpellFactory.mechanics_path(SOURCE)

# A monster whose Spellcasting says its numbers.
CASTER = {
    "name": "Cultist",
    "actions": [
        {
            "name": "Spellcasting",
            "description": "It casts a spell (spell save DC 15, +7 to hit with spell attacks).",
        }
    ],
}


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _option(name: str, char: dict | None = None):
    return spell_option(SpellFactory.create(name), CASTER if char is None else char)


# ---------------------------------------------------------------------------
# The data file


def _mechanics_files() -> dict[str, dict]:
    """Each source that has a mechanics file, with that file's entries."""
    return {
        source: _load(SpellFactory.mechanics_path(source))
        for source in SpellFactory.json_paths
        if os.path.exists(SpellFactory.mechanics_path(source))
    }


def _all_curated() -> list[str]:
    return sorted(name for entries in _mechanics_files().values() for name in entries)


def test_there_are_mechanics_files():
    assert SOURCE in _mechanics_files()


@pytest.mark.parametrize("source", sorted(_mechanics_files()))
def test_every_entry_is_used(source):
    """An entry is for a spell of its own source that the source wins: one
    for a spell another source wins would never be read."""
    sources = {path: _load(path) for path in SpellFactory.json_paths}
    for name in _mechanics_files()[source]:
        assert name in sources[source], name
        winner = next(path for path in SpellFactory.json_paths if name in sources[path])
        assert winner == source, name


@pytest.mark.parametrize("source", sorted(_mechanics_files()))
def test_entries_are_sorted_by_name(source):
    names = list(_mechanics_files()[source])
    assert names == sorted(names)


@pytest.mark.parametrize("name", _all_curated())
def test_every_entry_parses(name):
    assert isinstance(SpellFactory.create(name).mechanics, SpellMechanics)


@pytest.mark.parametrize("name", _all_curated())
def test_only_cantrips_scale_with_character_level(name):
    spell = SpellFactory.create(name)
    for damage in spell.mechanics.damage:
        if spell.level == 0:
            assert not damage.upcast, name
        else:
            assert not damage.cantrip, name


# ---------------------------------------------------------------------------
# Parsing


def test_a_full_entry():
    mechanics = parse_mechanics(
        "Test",
        {
            "roll": "save",
            "save": {"ability": "DEX", "half_on_success": True, "repeat": True},
            "damage": [
                {
                    "dice": "1d8",
                    "type": "Necrotic",
                    "cantrip": {"5": "2d8", "11": "3d8", "17": "4d8"},
                },
                {
                    "dice": "3d8",
                    "type": None,
                    "choices": ["Acid", "Fire"],
                    "upcast": "1d8",
                },
            ],
            "heal": {"dice": "2d8", "add_modifier": True, "upcast": "2d8"},
            "condition": {
                "name": "Poisoned",
                "alternatives": ["Blinded"],
                "until": ["end", "source"],
            },
            "badge": False,
            "notes": ["A note."],
        },
    )
    assert mechanics.applicable
    assert mechanics.save.ability == "DEX"
    assert mechanics.save.half_on_success and mechanics.save.repeat
    assert mechanics.damage[0].cantrip == ((5, "2d8"), (11, "3d8"), (17, "4d8"))
    assert mechanics.damage[1].damage_type is None
    assert mechanics.damage[1].choices == ("Acid", "Fire")
    assert mechanics.heal.add_modifier
    assert mechanics.condition.until == ("end", "source")
    assert mechanics.badge is False
    assert mechanics.notes == ("A note.",)


def test_an_empty_entry_is_a_spell_that_just_happens():
    mechanics = parse_mechanics("Test", {})
    assert mechanics.applicable
    assert mechanics.roll == "none"
    assert mechanics.badge is None


@pytest.mark.parametrize(
    "entry, field",
    [
        ({"roll": "save"}, "save"),  # a save with no ability
        ({"roll": "attack", "save": {"ability": "DEX"}}, "save"),
        ({"roll": "save", "save": {"ability": "Dexterity"}}, "save.ability"),
        ({"roll": "check"}, "roll"),
        ({"damage": [{"dice": "8d6", "type": "Flame"}]}, "damage[0].type"),
        ({"damage": [{"dice": "eight d6", "type": "Fire"}]}, "damage[0].dice"),
        ({"damage": [{"dice": "3d8", "type": None}]}, "damage[0]"),  # no choices
        (
            {"damage": [{"dice": "3d8", "type": "Fire", "choices": ["Acid", "Fire"]}]},
            "damage[0]",
        ),
        (
            {"damage": [{"dice": "1d8", "type": "Fire", "cantrip": {"5": "2d8"}}]},
            "damage[0].cantrip",
        ),
        ({"condition": {"name": "Asleep"}}, "condition.name"),
        ({"condition": {"name": "Prone", "until": ["end"]}}, "condition.until"),
        ({"badge": "yes"}, "badge"),
        ({"notes": "one note"}, "notes"),
        ({"halfOnSave": True}, "entry"),  # a key the schema doesn't have
    ],
)
def test_a_wrong_entry_names_the_spell_and_field(entry, field):
    with pytest.raises(ValueError, match=re.escape(f"'Test', {field}:")):
        parse_mechanics("Test", entry)


# ---------------------------------------------------------------------------
# Loading


def _unchecked_spell():
    """A spell with no entry yet: the first, by name, of those left."""
    return next(
        spell
        for spell in sorted(SpellFactory.all_spells(), key=lambda s: s.name)
        if spell.name not in _all_curated()
    )


def test_a_spell_without_an_entry_has_no_mechanics():
    assert _unchecked_spell().mechanics is None


def test_an_entry_rides_only_on_its_own_sources_record(monkeypatch):
    """An entry is for its source's wording: a 2014 file's Fireball entry
    isn't the 2024 Fireball's, which wins the merge."""
    source_2014 = "CharacterContent/Spells/spells_dnd5e.json"
    entry_2014 = {"roll": "save", "save": {"ability": "CON"}}
    real_load = SpellFactory._load_mechanics.__func__

    def load(cls, path):
        if path == source_2014:
            return {"Fireball": entry_2014}
        return {} if path == SOURCE else real_load(cls, path)

    monkeypatch.setattr(SpellFactory, "_load_mechanics", classmethod(load))
    monkeypatch.setattr(SpellFactory, "_cache", None)
    assert "mechanics" not in SpellFactory._load_json()["Fireball"]
    assert SpellFactory.create("Fireball").mechanics is None


def test_a_wrong_entry_fails_when_read():
    spell = DataSpell(
        dict(SpellFactory._load_json()["Fireball"], mechanics={"roll": "check"})
    )
    with pytest.raises(ValueError, match="Fireball"):
        spell.mechanics


# ---------------------------------------------------------------------------
# The Custom Effect picker


def test_fireball():
    fireball = _option("Fireball")
    assert fireball.is_curated
    assert fireball.roll == SAVING_THROW
    assert fireball.ability == "DEX"
    assert fireball.dc == 15
    assert fireball.half_on_save
    assert fireball.damage == "8d6 Fire"
    assert fireball.damage_at(5) == "10d6 Fire"
    assert fireball.note == ""


def test_hold_person():
    hold = _option("Hold Person")
    assert hold.ability == "WIS"
    assert hold.condition == "Paralyzed"
    assert hold.repeat_save
    assert hold.concentration
    assert hold.damage == ""
    assert "Humanoids" in hold.note


def test_guiding_bolt_is_an_attack():
    bolt = _option("Guiding Bolt")
    assert bolt.roll == ATTACK_ROLL
    assert bolt.bonus == 7
    assert bolt.ability is None
    assert bolt.damage_at(3) == "6d6 Radiant"


def test_ray_of_sickness_poisons_until_the_end_of_the_casters_next_turn():
    ray = _option("Ray of Sickness")
    assert ray.roll == ATTACK_ROLL
    assert ray.condition == "Poisoned"
    assert ray.until == ("end", "source")


def test_sleep_incapacitates_until_the_end_of_the_targets_next_turn():
    sleep = _option("Sleep")
    assert sleep.condition == "Incapacitated"
    assert sleep.until == ("end", "target")
    assert not sleep.repeat_save  # its second save is a different one
    assert "Unconscious" in sleep.note


def test_only_the_part_that_grows_is_upcast():
    storm = _option("Ice Storm")
    assert storm.damage == "2d10 Bludgeoning + 4d6 Cold"
    assert storm.damage_at(6) == "4d10 Bludgeoning + 4d6 Cold"


def test_a_type_to_choose_is_left_to_the_gm():
    orb = _option("Chromatic Orb")
    assert orb.damage == "3d8"
    assert "Acid, Cold, Fire, Lightning, Poison, Thunder" in orb.note


@pytest.mark.parametrize(
    "level, damage",
    [
        (4, "1d8 Necrotic"),
        (5, "2d8 Necrotic"),
        (11, "3d8 Necrotic"),
        (17, "4d8 Necrotic"),
    ],
)
def test_a_cantrip_grows_with_the_characters_level(level, damage):
    caster = dict(CASTER, class_levels={"Cleric": level})
    assert _option("Toll the Dead", caster).damage == damage


def test_a_monsters_cantrip_stays_as_it_is():
    assert _option("Toll the Dead").damage == "1d8 Necrotic"


def test_the_modifier_is_added_when_known_and_asked_for_when_not():
    weapon = _option("Spiritual Weapon")
    assert weapon.damage == "1d8 Force"
    assert "modifier" in weapon.note


def test_healing_is_a_note():
    cure = _option("Cure Wounds")
    assert cure.damage == ""
    assert cure.ability is None
    assert cure.condition == ""  # no badge for healing
    assert "heals 2d8 Hit Points plus" in cure.note
    assert "2d8 more per slot level above 1" in cure.note


def test_a_spell_with_nothing_to_roll_is_its_own_badge():
    bless = _option("Bless")
    assert bless.condition == "Bless"
    assert "1d4" in bless.note


def test_a_badge_can_be_turned_off():
    assert _option("Alarm").condition == ""


def test_a_curated_note_replaces_what_the_text_reading_would_say():
    """Read from its text, Ice Knife says it has a save too and that
    upcasting won't change its damage; its entry says what to do instead."""
    knife = _option("Ice Knife")
    assert knife.damage == "1d10 Piercing"
    assert "second effect" in knife.note
    assert "Upcasting won't" not in knife.note


def test_a_spell_without_an_entry_is_read_from_its_text():
    spell = _unchecked_spell()
    option = spell_option(spell, CASTER)
    assert not option.is_curated
    assert option.ability == read_effect_text(spell.description).ability


def test_a_spell_with_nothing_to_apply_is_left_out_of_all_spells():
    assert not is_applicable(SpellFactory.create("Alarm"))
    assert is_applicable(SpellFactory.create("Fireball"))
    assert is_applicable(_unchecked_spell())
    names = {option.name for option in dict(effect_options(CASTER))[ALL_SPELLS]}
    assert "Alarm" not in names
    assert "Fireball" in names


def test_a_casters_own_spell_with_nothing_to_apply_is_still_listed():
    """Picking it still spends the slot and the action."""
    alarm = SpellFactory.create("Alarm")
    caster = dict(CASTER, _spell_objects={"Alarm": alarm})
    options = dict(effect_options(caster, all_spells=[]))
    assert [option.name for option in options["Cultist's Spells"]] == ["Alarm"]


# ---------------------------------------------------------------------------
# What the text reading got wrong, fixed by an entry


def test_hunters_mark_is_a_badge_not_damage_to_fill_in():
    mark = _option("Hunter's Mark")
    assert mark.condition == "Hunter's Mark"
    assert mark.damage == ""
    assert "1d6 Force" in mark.note


def test_hideous_laughter_incapacitates_and_says_prone_too():
    laughter = _option("Tasha's Hideous Laughter")
    assert laughter.ability == "WIS"
    assert laughter.condition == "Incapacitated"
    assert laughter.repeat_save
    assert "Prone" in laughter.note


def test_true_strike_is_a_weapon_attack():
    strike = _option("True Strike")
    assert strike.roll == ATTACK_ROLL
    assert strike.damage == ""
    assert "weapon" in strike.note


def test_healing_word_heals_with_the_modifier():
    word = _option("Healing Word")
    assert "2d4 Hit Points plus the spellcasting ability modifier" in word.note


def test_an_entry_in_a_2014_file():
    """Absorb Elements is only in the 2014 data, so its entry is in
    spells_dnd5e_mechanics.json."""
    absorb = _option("Absorb Elements")
    assert absorb.is_curated
    assert absorb.damage == ""
    assert "Resistance" in absorb.note
