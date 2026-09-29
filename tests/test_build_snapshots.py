"""Regression safety net for the character-model refactor (see
CharacterContent/temp.plan.md, step 0).

For every build in `RunCharacterCreator.BuildSelector` and `ExampleSelector`,
this test compares two golden snapshots against a fresh build:

- `tests/snapshots/build_stats.json` - every computed stat (ability scores,
  AC, HP, initiative, speed, skills, saves, expertise, spell/pact slots,
  resistances, immunities, senses, weapon attack/damage bonuses, carrying
  capacity).
- `tests/snapshots/sheet_hashes.json` - a sha256 per rendered HTML page, for
  every build rendered in both full mode (`description_mode=None`) and
  `"concise"` mode.

Rendering is deterministic across processes (checked under different
PYTHONHASHSEED values), so pages are hashed as-is. If a page ever flips between
runs, look for iteration over a set of `str` enums (e.g. `Ability`) - string
hashing is randomized per process.

Sheets are rendered into a pytest tmp directory (`HtmlCharacterSheetWriter.
write_character_sheet`'s `output_folder` override is used for the duration of
the test) - never into `Output/`.

Refactor steps that are meant to change no rules should leave both files
untouched. A rules fix that's meant to change output should regenerate the
goldens on purpose:

    UPDATE_SNAPSHOTS=1 pytest tests/test_build_snapshots.py

Each test rewrites its own build's entry, so `-k` limits regeneration to the
matching builds. Entries for builds that no longer exist are not removed
automatically - `test_no_stale_goldens` flags them; delete them by hand.
"""

import hashlib
import json
import os
from pathlib import Path

import pytest

from Core.Definitions import Ability, Skill
from RunCharacterCreator import BuildSelector, ExampleSelector
from Utils.CharacterSheetWriters import HtmlCharacterSheetWriter, get_output_folder

ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}
BUILD_PARAMS = sorted(ALL_BUILDS)

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
STATS_PATH = SNAPSHOT_DIR / "build_stats.json"
HASHES_PATH = SNAPSHOT_DIR / "sheet_hashes.json"

UPDATE_SNAPSHOTS = os.environ.get("UPDATE_SNAPSHOTS") == "1"


def _compute_stats(name: str) -> dict:
    data = type(ALL_BUILDS[name])().build()
    character = data.setup_character_stat_block()
    return {
        "scores": [character.get_ability_score(a) for a in Ability],
        "ac": character.calculate_armor_class(),
        "hp": character.calculate_hit_points(),
        "init": character.initiative,
        "init_roll": str(character.initiative_roll_condition),
        "speed": character.speed,
        "skills": [character.get_skill_modifier(s) for s in Skill],
        "skill_abilities": [str(character.get_skill_ability(s)) for s in Skill],
        "skill_rolls": [
            f"{character.get_skill_roll_condition(s)}"
            f"{character.get_skill_roll_condition_reasons(s)}"
            for s in Skill
        ],
        "skill_sources": [
            sorted(
                f"{value}:{source}"
                for value, source in character.get_skill_bonus_sources(s)
            )
            for s in Skill
        ],
        "saves": [character.get_saving_throw_modifier(a) for a in Ability],
        "save_prof": [character.is_proficient_in_saving_throw(a) for a in Ability],
        "expertise": [character.has_expertise_in_skill(s) for s in Skill],
        "slots": sorted(character.spell_slots.items()) if character.spell_slots else [],
        "pact": sorted(character.pact_magic_slots.items()),
        "resist": sorted(
            (str(damage_type), sorted(sources))
            for damage_type, sources in character.damage_resistances.items()
        ),
        "immune": sorted(
            (str(damage_type), sorted(sources))
            for damage_type, sources in character.damage_immunities.items()
        ),
        "senses": sorted((str(sense), rng) for sense, rng in character.senses.items()),
        "weapons": [
            (
                weapon.name,
                weapon.calculate_total_attack_roll_bonus_int(character),
                weapon.calculate_damage_bonus_int(character),
            )
            for weapon in data.weapons
        ],
        "carry": character.get_carrying_capacity(),
    }


def _hash_tree(root: Path) -> dict[str, str]:
    hashes = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            hashes[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return hashes


def _render_and_hash(name: str, tmp_path: Path) -> dict[str, dict[str, str]]:
    result = {}
    for mode_key, description_mode in (("full", None), ("concise", "concise")):
        data = type(ALL_BUILDS[name])().build()
        folder_name = os.path.basename(get_output_folder(data, description_mode))
        output_folder = tmp_path / folder_name
        HtmlCharacterSheetWriter().write_character_sheet(
            data, description_mode=description_mode, output_folder=str(output_folder)
        )
        result[mode_key] = _hash_tree(output_folder)
    return result


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_build_stats_unchanged(name):
    # Round-trip through JSON so tuples become lists like the golden file -
    # otherwise every tuple-valued stat spuriously "changes" on every run.
    stats = json.loads(json.dumps(_compute_stats(name)))

    if UPDATE_SNAPSHOTS:
        golden = _load(STATS_PATH)
        golden[name] = stats
        _save(STATS_PATH, golden)
        pytest.skip("UPDATE_SNAPSHOTS=1: golden stats rewritten")

    golden = _load(STATS_PATH)
    assert (
        name in golden
    ), f"No golden stats for {name!r}. Run with UPDATE_SNAPSHOTS=1 to add it."
    expected = golden[name]
    if stats != expected:
        diffs = [
            f"  {key}: golden={expected.get(key)!r} actual={stats.get(key)!r}"
            for key in sorted({*expected, *stats})
            if expected.get(key) != stats.get(key)
        ]
        pytest.fail(
            f"{name}: computed stats changed from golden snapshot:\n" + "\n".join(diffs)
        )


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_build_sheets_unchanged(name, tmp_path):
    sheets = _render_and_hash(name, tmp_path)

    if UPDATE_SNAPSHOTS:
        golden = _load(HASHES_PATH)
        golden[name] = sheets
        _save(HASHES_PATH, golden)
        pytest.skip("UPDATE_SNAPSHOTS=1: golden sheet hashes rewritten")

    golden = _load(HASHES_PATH)
    assert (
        name in golden
    ), f"No golden sheet hashes for {name!r}. Run with UPDATE_SNAPSHOTS=1 to add it."
    expected = golden[name]
    for mode_key in ("full", "concise"):
        expected_pages = expected.get(mode_key, {})
        actual_pages = sheets.get(mode_key, {})
        added = sorted(set(actual_pages) - set(expected_pages))
        removed = sorted(set(expected_pages) - set(actual_pages))
        changed = sorted(
            page
            for page in set(actual_pages) & set(expected_pages)
            if actual_pages[page] != expected_pages[page]
        )
        assert not (added or removed or changed), (
            f"{name} ({mode_key} mode) sheets changed from golden snapshot:\n"
            f"  added pages: {added}\n"
            f"  removed pages: {removed}\n"
            f"  changed pages: {changed}"
        )


@pytest.mark.skipif(UPDATE_SNAPSHOTS, reason="UPDATE_SNAPSHOTS=1")
def test_no_stale_goldens():
    for path in (STATS_PATH, HASHES_PATH):
        stale = sorted(set(_load(path)) - set(BUILD_PARAMS))
        assert not stale, f"{path.name} has entries for removed builds: {stale}"
