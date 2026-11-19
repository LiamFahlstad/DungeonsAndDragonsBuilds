"""A stat-block ability's recharge, uses per day, legendary cost, turn-start
sentence, the spells it casts and the ability it uses: the MonsterAbility
fields the combat UI acts on, and the reader that fills them from the text
where stat blocks are written (Model/Creatures/MonsterAbilityText.py,
Notes/explicit-attributes-plan.md Phase 4.2)."""

import importlib
import inspect
import json
import pkgutil

import Combat.Monsters
from Combat.CombatUIQt.monster_actions import (
    ABILITY_SECTIONS,
    parse_action,
    start_of_turn_traits,
    upgrade_ability_keys,
)
from Combat.Tools.monster_effect_text import read_ability_fields
from Combat.EncounterLogs import LogJSONEncoder
from Combat.Tools.monster_enum_format import format_ability_list
from Model.Creatures.Combatants import ExtendedCombatantData
from Model.Creatures.MonsterAbilities import MonsterAbility, MonsterCast
from Model.Creatures.MonsterAbilityText import (
    ABILITY_FIELDS,
    DEFAULTS,
    keyword_source,
    read_casts,
    read_costs,
    read_turn_start,
    read_uses,
    spell_name_in_list,
)


def test_costs_from_the_name():
    assert read_costs("Fire Breath (Recharge 5\N{EN DASH}6)", "") == {"recharge": 5}
    assert read_costs("Blinding Breath (Recharge 6)", "") == {"recharge": 6}
    assert read_costs("Fetid Cloud (1/Day)", "") == {"per_day": 1}
    assert read_costs("Wing (Costs 2 Actions)", "") == {"legendary_cost": 2}
    assert read_costs("Lash (Costs 1 Action)", "") == {}
    # A recharge after a rest isn't a d6 one.
    assert read_costs("Fey Step (Recharges after a Long Rest)", "") == {}


def test_the_turn_start_sentence():
    assert read_turn_start(
        "The troll regains 15 Hit Points at the start of each of its turns."
        " If it takes Fire damage, this doesn't work."
    ) == ("The troll regains 15 Hit Points at the start of each of its turns.")
    assert (
        read_turn_start("It glows. At the start of the wight's turn, shadows gather.")
        == "At the start of the wight's turn, shadows gather."
    )
    assert read_turn_start("It sees far.") == ""


def test_the_spells_it_casts():
    assert read_casts(
        "The lich casts Fear, using Spellcasting.", spell_name_in_list
    ) == (MonsterCast("Fear"),)
    assert read_casts(
        "It uses Spellcasting to cast Mind Spike (level 3 version).",
        spell_name_in_list,
    ) == (MonsterCast("Mind Spike", level=3),)
    assert read_casts(
        "It casts one of the following spells (spell save DC 12): At will:"
        " Thaumaturgy. 2/Day each: Hold Person, Silence. 1/Day: Bestow Curse.",
        spell_name_in_list,
    ) == (
        MonsterCast("Thaumaturgy"),
        MonsterCast("Hold Person", per_day=2),
        MonsterCast("Silence", per_day=2),
        MonsterCast("Bestow Curse", per_day=1),
    )
    # Only spells there are, named as the spell list has them.
    assert read_casts("It casts Gloomy Doom.", spell_name_in_list) == ()
    assert read_casts("It casts fear.", spell_name_in_list) == ()


def test_the_ability_it_uses():
    names = {"rend", "dreadful glare"}
    assert read_uses(
        "Pounce",
        "It moves up to half its Speed, and it makes one" " Rend attack.",
        names,
    ) == {
        "uses_ability": "Rend",
        "moves_first": True,
    }
    assert read_uses("Glare", "The mummy uses Dreadful Glare.", names) == {
        "uses_ability": "Dreadful Glare"
    }
    assert read_uses("Tail", "It makes one Tail attack.", names) == {}
    assert read_uses("Rend (Recharge 6)", "It makes one Rend attack.", names) == {}


def test_keyword_source():
    assert keyword_source(
        {
            "recharge": 5,
            "casts": (MonsterCast("Fear"),),
            "uses_ability": "Rend",
        }
    ) == ["recharge=5", "casts=(MonsterCast('Fear'),)", "uses_ability='Rend'"]
    assert keyword_source(
        {"casts": (MonsterCast("Hold Person", per_day=2), MonsterCast("Silence", 3))}
    ) == [
        "casts=(MonsterCast('Hold Person', per_day=2), MonsterCast('Silence', level=3))"
    ]


def test_the_fields_drive_the_action():
    ability = MonsterAbility(
        "Frightening Gaze",
        "unreadable",
        legendary_cost=2,
        casts=(MonsterCast("Fear"),),
    )
    action = parse_action(ability, legendary=True)
    assert action.legendary_cost == 2
    assert action.casts == (MonsterCast("Fear"),)


def test_a_log_keeps_the_fields_set_and_leaves_out_the_rest():
    ability = MonsterAbility(
        "Spellcasting (2/Day)",
        "x",
        per_day=2,
        casts=(MonsterCast("Hold Person", per_day=2),),
    )
    logged = json.loads(json.dumps(ability, cls=LogJSONEncoder))
    assert logged == {
        "name": "Spellcasting (2/Day)",
        "description": "x",
        "per_day": 2,
        "casts": [{"spell": "Hold Person", "level": None, "per_day": 2}],
    }
    assert parse_action(logged) == parse_action(ability)


def test_an_old_logs_abilities_get_their_fields_once():
    char = {
        "traits": [
            {
                "name": "Regeneration",
                "description": "It heals at the start of its turn.",
            }
        ],
        "actions": [
            {"name": "Rend", "description": "Melee Attack Roll: +5, reach 5 ft."},
            {"name": "Fire Breath (Recharge 5-6)", "description": "x"},
        ],
        "legendary_actions": [
            {"name": "Pounce", "description": "It makes one Rend attack."},
            {"name": "Gaze (Costs 2 Actions)", "description": "It casts Fear."},
        ],
    }
    upgrade_ability_keys(char)
    assert char["actions"][1]["recharge"] == 5
    assert char["legendary_actions"][0]["uses_ability"] == "Rend"
    assert char["legendary_actions"][1]["legendary_cost"] == 2
    assert char["legendary_actions"][1]["casts"] == [
        {"spell": "Fear", "level": None, "per_day": None}
    ]
    assert start_of_turn_traits(char) == [
        ("Regeneration", "It heals at the start of its turn.")
    ]
    # One with a field set is left as it is, even where its text differs.
    kept = {"name": "Breath (Recharge 5-6)", "description": "x", "recharge": 4}
    upgrade_ability_keys({"actions": [kept]})
    assert kept["recharge"] == 4


def test_the_generator_writes_the_fields():
    monster = {
        "actions": [
            {"name": "Rend", "description": "Melee Attack Roll: +5, reach 5 ft."},
            {"name": "Breath (Recharge 5-6)", "description": "It casts Fear."},
        ]
    }
    written = format_ability_list(monster["actions"], "actions", monster)
    assert "recharge=5, casts=(MonsterCast('Fear'),)" in written


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


def test_every_abilitys_fields_say_what_its_text_says():
    """The fight reads the fields; the name and text are shown. An ability
    whose text gives a recharge, uses, cost, spell, ... must have the field
    too (generate_monsters.py writes them; a homebrew one, by hand). It's
    also what lets an old log's abilities be read once as they load
    (upgrade_ability_keys)."""
    wrong = {}
    for monster in _stat_blocks():
        for section in ABILITY_SECTIONS:
            for ability in getattr(monster, section, None) or []:
                said = {**DEFAULTS, **read_ability_fields(monster, ability, section)}
                has = {name: getattr(ability, name) for name in ABILITY_FIELDS}
                if has != said:
                    wrong[f"{monster.combatant_type}: {ability.name}"] = {
                        k: (has[k], said[k]) for k in said if has[k] != said[k]
                    }
    assert not wrong, f"(field, text) where they differ: {wrong}"
