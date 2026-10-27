---
name: snapshot-diffs
description: Read what actually changed when a golden snapshot test fails (test_build_snapshots, test_order_invariance) - a script that shows each build's changed stats by ability/skill name and the text diff of every changed sheet page against HEAD, instead of the bare page hashes the test prints - and how to decide whether a change is intended before regenerating with UPDATE_SNAPSHOTS=1. Use whenever a snapshot or build test fails, before updating any golden file, after any change that should (or should not) alter character sheets, when reviewing or committing a change to tests/snapshots/, and whenever someone asks "what did this change on the sheets?", even if they don't say "snapshot".
---

# Snapshot diffs

`tests/test_build_snapshots.py` pins every registered and example build (143 of them) to two goldens:

- `tests/snapshots/build_stats.json`: every computed stat. The test prints changed keys, but per-ability and per-skill stats are bare lists in enum order (`skills: [5, 3, ...]`).
- `tests/snapshots/sheet_hashes.json`: one sha256 per rendered page. The test can only say *which* pages changed.

CLAUDE.md says a failing snapshot is never "expected" until you've read the diff. This script is how you read it.

## Show the diff (run it; don't guess)

```bash
python .claude/skills/snapshot-diffs/snapshot_diff.py                    # every build that differs from its golden (~7 s)
python .claude/skills/snapshot-diffs/snapshot_diff.py Obmar Clover       # only builds whose name contains these
python .claude/skills/snapshot-diffs/snapshot_diff.py Obmar --page level_04 --max-lines 200
python .claude/skills/snapshot-diffs/snapshot_diff.py --stats-only       # fast: stats and changed page names only
```

For each differing build it prints:

- **stats** as `golden -> now`, per ability or skill by name (`skills[ARCANA]: 6 -> 5`);
- **pages added/removed** (a new `fighting_styles.html`, a level page that no longer grants anything);
- **each changed page as a text diff** from `--ref` (default `HEAD`) to the working tree. The page is rendered from an export of that commit, cached under the system temp folder, in a separate process. It never touches your working tree, the index or other agents' worktrees. A change with identical text is labelled *markup-only* and shown as raw HTML.

It ends with the exact `UPDATE_SNAPSHOTS=1` command for the builds that differ. Exit status is 1 when anything differs.

Two outputs mean something other than "your change did this":

- **"renders the same at HEAD, so its golden is stale there"**: HEAD's own goldens were never updated. Your change didn't cause it. Say so, rather than folding it into your commit silently.
- **"no baseline at HEAD"**: the build is new, or failed to build at that commit. Use `--ref <older commit>` or read the page itself.

## Decide: intended or not

Go through every changed line, and explain each one by the change you made:

| Change you made | Expected diff | Suspicious |
|---|---|---|
| Rules text of a feature | That feature's card, on its level page and in `full_character_sheet.html` | Any stat change |
| A feature's mechanics (`apply()`) | The stat it affects, on builds that have the feature | Builds that don't have it |
| Multiclass / level change to one build | That build only: levels, HP, slots, proficiencies, lost ASI (see `multiclass-builds`) | Any other build |
| A shared engine or presentation change | Many builds, all with the same kind of change | One odd build out: look at it |
| A refactor meant to change nothing | **Nothing** | Anything at all |

If a line has no explanation, it's a bug until shown otherwise. Fix it, or report it. Don't regenerate it away.

## Regenerate, then confirm

```bash
UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -k "<build> or <build>"   # the command the script printed
./run_tests.sh -q                                              # the plain rerun must pass
```

- `-k` limits the rewrite to the matching builds. Rewrite only builds whose diff you read.
- The order-invariance tests may fail *during* the update run, because the golden is rewritten under them. They must pass on the plain rerun.
- A removed build leaves its golden entries behind. `test_no_stale_goldens` flags them, and the script lists them. Delete them by hand.
- `git diff tests/snapshots/build_stats.json` after the update should show only the builds you meant.

The other goldens (`combatants.json`, `combat_ui_cards.json`, `combat_ui_more_info.json`) are readable JSON already: regenerate with the same `UPDATE_SNAPSHOTS=1`, then read `git diff tests/snapshots/<file>`.

When committing, a snapshot change belongs in the commit whose change caused it. If one golden file holds changes from two unrelated changes, split the file by build (the `git-commit` agent knows how).
