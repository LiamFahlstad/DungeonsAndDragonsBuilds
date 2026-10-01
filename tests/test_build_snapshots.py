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

To see what changed rather than just which pages, set SNAPSHOT_DUMP_DIR to keep
every rendered page and `diff -r` two dumps (see tests/_snapshot_helpers.py).
"""

import json

import pytest

from tests._snapshot_helpers import (
    BUILD_PARAMS,
    HASHES_PATH,
    STATS_PATH,
    UPDATE_SNAPSHOTS,
    build,
    compute_stats,
    load,
    render_and_hash,
    save,
    sheet_differences,
)


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_build_stats_unchanged(name):
    # Round-trip through JSON so tuples become lists like the golden file -
    # otherwise every tuple-valued stat spuriously "changes" on every run.
    stats = json.loads(json.dumps(compute_stats(build(name))))

    if UPDATE_SNAPSHOTS:
        golden = load(STATS_PATH)
        golden[name] = stats
        save(STATS_PATH, golden)
        pytest.skip("UPDATE_SNAPSHOTS=1: golden stats rewritten")

    golden = load(STATS_PATH)
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
    sheets = render_and_hash(name, tmp_path, dump=True)

    if UPDATE_SNAPSHOTS:
        golden = load(HASHES_PATH)
        golden[name] = sheets
        save(HASHES_PATH, golden)
        pytest.skip("UPDATE_SNAPSHOTS=1: golden sheet hashes rewritten")

    golden = load(HASHES_PATH)
    assert (
        name in golden
    ), f"No golden sheet hashes for {name!r}. Run with UPDATE_SNAPSHOTS=1 to add it."
    problems = sheet_differences(golden[name], sheets)
    assert (
        not problems
    ), f"{name} sheets changed from golden snapshot:\n  " + "\n  ".join(problems)


@pytest.mark.skipif(UPDATE_SNAPSHOTS, reason="UPDATE_SNAPSHOTS=1")
def test_no_stale_goldens():
    for path in (STATS_PATH, HASHES_PATH):
        stale = sorted(set(load(path)) - set(BUILD_PARAMS))
        assert not stale, f"{path.name} has entries for removed builds: {stale}"
