"""What the combat UI shows for every build (Combat/PlayerCombatant.py),
against tests/snapshots/combatants.json.

The snapshot keeps the dict's plain values (the objects under "_..." keys
are the Character's own and covered by tests/test_build_snapshots.py) plus
each weapon's summary line. A change that's meant to change what combat
shows regenerates it on purpose:

    UPDATE_SNAPSHOTS=1 pytest tests/test_combatant_snapshots.py
"""

import json

import pytest

from Combat.PlayerCombatant import combatant_from_character, weapon_summary
from tests._snapshot_helpers import (
    BUILD_PARAMS,
    SNAPSHOT_DIR,
    UPDATE_SNAPSHOTS,
    build,
    load,
    save,
)

COMBATANTS_PATH = SNAPSHOT_DIR / "combatants.json"


def snapshot(name: str) -> dict:
    character = build(name)
    combatant = combatant_from_character(character)
    shown = {key: value for key, value in combatant.items() if not key.startswith("_")}
    shown["weapons"] = [
        weapon_summary(weapon, combatant["_stat_block"])
        for weapon in combatant["_weapons_objects"]
    ]
    # Round-trip through JSON so tuples and int keys compare like the golden.
    return json.loads(json.dumps(shown))


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_combatant_unchanged(name):
    shown = snapshot(name)

    if UPDATE_SNAPSHOTS:
        golden = load(COMBATANTS_PATH)
        golden[name] = shown
        save(COMBATANTS_PATH, golden)
        pytest.skip("UPDATE_SNAPSHOTS=1: golden combatant rewritten")

    golden = load(COMBATANTS_PATH)
    assert name in golden, f"No golden combatant for {name!r}."
    expected = golden[name]
    diffs = [
        f"  {key}: golden={expected.get(key)!r} actual={shown.get(key)!r}"
        for key in sorted({*expected, *shown})
        if expected.get(key) != shown.get(key)
    ]
    assert not diffs, f"{name}: combatant changed:\n" + "\n".join(diffs)


@pytest.mark.skipif(UPDATE_SNAPSHOTS, reason="UPDATE_SNAPSHOTS=1")
def test_no_stale_goldens():
    stale = sorted(set(load(COMBATANTS_PATH)) - set(BUILD_PARAMS))
    assert not stale, f"combatants.json has entries for removed builds: {stale}"
