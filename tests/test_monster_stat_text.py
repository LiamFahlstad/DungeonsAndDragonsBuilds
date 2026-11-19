"""A stat block's speed, senses and spellcasting text and the fields the
fight reads instead (Model/Creatures/MonsterStatText.py,
Notes/explicit-attributes-plan.md Phase 4.1)."""

import importlib
import inspect
import pkgutil

import Combat.Monsters
from Combat.PlayerCombatant import combatant_from_stat_block
from Model.Creatures.Combatants import ExtendedCombatantData
from Model.Creatures.MonsterStatText import (
    DEFAULTS,
    STAT_BLOCK_FIELDS,
    read_senses,
    read_speed_text,
    read_spellcasting,
    read_stat_block,
    upgrade_stat_block_keys,
)


def test_speed_text():
    assert read_speed_text("burrow 20 ft.; swim 30 ft.") == {
        "speed_burrow_ft": 20,
        "speed_swim_ft": 30,
    }
    assert read_speed_text("hover; swim 40 ft.") == {
        "speed_swim_ft": 40,
        "hover": True,
    }
    assert read_speed_text("snake form only") == {}


def test_senses_text():
    assert read_senses(
        "Blindsight 30 ft. (blind beyond this radius), Darkvision 120 ft.,"
        " Passive Perception 15"
    ) == {
        "blindsight_ft": 30,
        "blind_beyond": True,
        "darkvision_ft": 120,
        "passive_perception": 15,
    }
    assert read_senses("Truesight 30 ft., Tremorsense 60 ft.") == {
        "truesight_ft": 30,
        "tremorsense_ft": 60,
    }


def test_spellcasting_text_the_first_of_each():
    assert read_spellcasting(
        [
            "Bite. Melee Attack Roll: +5",
            "Wisdom (spell save DC 15, +7 to hit with spell attacks)",
        ]
    ) == {"spell_save_dc": 15, "spell_attack_bonus": 7}
    assert read_spellcasting(["Charisma (spell save DC 13)", "spell save DC 9"]) == {
        "spell_save_dc": 13
    }


def test_an_old_logs_monster_gets_its_fields_once():
    old = {
        "name": "Ghoul",
        "senses": "Darkvision 60 ft., Passive Perception 10",
        "speed_special_rules": "swim 30 ft.",
        "actions": [{"name": "Spellcasting", "description": "spell save DC 12"}],
    }
    upgrade_stat_block_keys(old)
    assert old["darkvision_ft"] == 60
    assert old["speed_swim_ft"] == 30
    assert old["spell_save_dc"] == 12
    assert old["hover"] is False and old["blindsight_ft"] is None
    # One that has its fields keeps them, even where its text differs.
    new = {"senses": "Darkvision 60 ft.", "darkvision_ft": 120}
    assert upgrade_stat_block_keys(dict(new)) == new
    # A player's dict has no stat block text.
    player = {"name": "Kivi", "speed": 30}
    assert upgrade_stat_block_keys(dict(player)) == player


def test_the_combat_dict_carries_every_field():
    char = combatant_from_stat_block(
        ExtendedCombatantData(
            combatant_type="Bat",
            hp=1,
            ac=12,
            temp_hp=0,
            conditions=[],
            blindsight_ft=60,
            passive_perception=11,
        )
    )
    assert {name: char[name] for name in STAT_BLOCK_FIELDS} == {
        **DEFAULTS,
        "blindsight_ft": 60,
        "passive_perception": 11,
    }


def _stat_blocks():
    for info in pkgutil.walk_packages(Combat.Monsters.__path__, "Combat.Monsters."):
        if info.ispkg:
            continue
        module = importlib.import_module(info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__ and issubclass(
                cls, ExtendedCombatantData
            ):
                yield cls()  # pyright: ignore[reportCallIssue]


def test_every_stat_blocks_fields_say_what_its_text_says():
    """The fight reads the fields; the text is shown. A stat block whose
    text gives a speed, sense or spell save DC must have the field too
    (generate_monsters.py writes them; a homebrew one, by hand)."""
    wrong = {}
    for monster in _stat_blocks():
        said = {
            **DEFAULTS,
            **read_stat_block(
                monster.speed_special_rules,
                monster.senses,
                monster,
            ),
        }
        has = {name: getattr(monster, name) for name in STAT_BLOCK_FIELDS}
        if has != said:
            wrong[monster.combatant_type] = {
                k: (has[k], said[k]) for k in said if has[k] != said[k]
            }
    assert not wrong, f"(field, text) where they differ: {wrong}"
