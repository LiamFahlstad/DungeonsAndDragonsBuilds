"""The combatant dict's keys are the ones Combat/Fight/combatant.py declares
(Notes/combat-ui-refactor-plan.md, step 2).

Combatant is a schema the code isn't annotated with yet (its docstring says
why), so these tests stand in for the type checker: what both builders make,
what a fight saves, the key constants, and every literal key the combat code
reads or writes on a combatant must be declared. A new key is declared there,
with what it means, before it's used.
"""

import ast
import re
from pathlib import Path

import pytest

import Combat.Monsters as Monsters
from Combat import PartyAllies, Summons, WildShape
from Combat.Arena import arena, lasting, speeds
from Combat.CombatUIQt import attack_rolls, player_view, turns_mixin
from Combat.Effects import active_effects
from Combat.EncounterLogs import PLAYER_FIGHT_KEYS
from Combat.Fight.combatant import COMBATANT_KEYS, Combatant
from Combat.PlayerCombatant import (
    AC_WITHOUT_SHIELD_KEY,
    combatant_from_character,
    combatant_from_stat_block,
)
from Model.Creatures.Combatants import ExtendedCombatantData
from tests._snapshot_helpers import BUILD_PARAMS, build

REPO = Path(__file__).resolve().parent.parent
REQUIRED = Combatant.__required_keys__

# The names the combat code gives a combatant dict. Every literal key read or
# written on one of these (x["key"], x.get("key"), x.setdefault("key"),
# x.pop("key")) is checked; other dicts (log entries, records) never use them.
_COMBATANT_NAMES = re.compile(
    r"^(char|target|source|owner|caster|combatant|attacker|summon|mover|creature"
    r"|bearer|grappler|viewer|ally|\w+_char|self\.selected_character)$"
)
_SKIPPED = {"Monsters", "Tools", "__pycache__"}


def _undeclared(keys) -> list[str]:
    return sorted(set(keys) - COMBATANT_KEYS)


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_a_players_keys_are_declared(name):
    char = combatant_from_character(build(name))
    assert not _undeclared(char), _undeclared(char)
    assert REQUIRED <= set(char), sorted(REQUIRED - set(char))


def _monsters() -> list[ExtendedCombatantData]:
    made = []
    for value in vars(Monsters).values():
        if (
            isinstance(value, type)
            and issubclass(value, ExtendedCombatantData)
            and value is not ExtendedCombatantData
        ):
            # A catalog monster's class fills in its own stat block, so it
            # takes no arguments; a base class that needs them is skipped.
            try:
                made.append(value())  # pyright: ignore[reportCallIssue]
            except TypeError:
                continue
    return made


def test_every_monsters_keys_are_declared():
    monsters = _monsters()
    assert len(monsters) > 100
    for monster in monsters:
        char = combatant_from_stat_block(monster)
        assert not _undeclared(char), (monster.combatant_type, _undeclared(char))
        assert REQUIRED <= set(char), (monster.combatant_type, REQUIRED - set(char))


def test_the_keys_a_fight_saves_are_declared():
    assert not _undeclared(PLAYER_FIGHT_KEYS)


def test_the_key_constants_are_declared():
    constants = [
        AC_WITHOUT_SHIELD_KEY,
        active_effects.KEY,
        arena.POSITION_KEY,
        arena.MOVED_KEY,
        arena.DASHES_KEY,
        arena.GRAPPLER_KEY,
        lasting.ACTIVE_SPELLS_KEY,
        speeds.MODE_KEY,
        speeds.ALTITUDE_KEY,
        Summons.SUMMON_OF_KEY,
        Summons.SOURCE_KEY,
        Summons.SPEC_KEY,
        Summons.CHOICE_KEY,
        Summons.SLOT_KEY,
        Summons.LIFETIME_KEY,
        Summons.TURN_KEY,
        Summons.ON_ZERO_HP_KEY,
        *Summons.OLD_KEYS,
        WildShape.WILD_SHAPE_KEY,
        PartyAllies.PARTY_ALLY_KEY,
        PartyAllies.ENCOUNTER_ALLY_KEY,
        attack_rolls.SHIELD_OFF,
        turns_mixin.INITIATIVE_KEY,
        *(key for key, _ in player_view._KNOWN_DEFENSES),
    ]
    assert not _undeclared(constants)


def _literal_keys():
    """(where, key) of every literal key the combat code uses on a combatant."""
    for path in sorted((REPO / "Combat").rglob("*.py")):
        if _SKIPPED & set(path.relative_to(REPO / "Combat").parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            base = key = None
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
            ):
                base, key = node.value, node.slice.value
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("get", "setdefault", "pop")
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                base, key = node.func.value, node.args[0].value
            if base is not None and _COMBATANT_NAMES.match(ast.unparse(base)):
                where = f"{path.relative_to(REPO).as_posix()}:{base.lineno}"
                yield where, key


def test_the_combat_code_uses_only_declared_keys():
    found = list(_literal_keys())
    assert len(found) > 500  # the scan still finds the code
    undeclared = [
        f"{where} {key!r}" for where, key in found if key not in COMBATANT_KEYS
    ]
    assert not undeclared, (
        "Keys used on a combatant but not declared in Combat/Fight/combatant.py "
        "(a typo, or a new key to declare there): " + ", ".join(undeclared)
    )
