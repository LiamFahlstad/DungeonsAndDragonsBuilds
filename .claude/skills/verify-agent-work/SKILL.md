---
name: verify-agent-work
description: Verify what subagents actually changed before trusting their reports - diff the working tree (or an agent's worktree) against the files it claimed, fail on off-limits files, compile, catch undefined names, import, check sibling worktrees, run tests, and curate what the agent wrote to its memory. Use every time a subagent (especially haiku-tier or a parallel batch) reports finished code or data changes, before telling the user the work is done, and whenever the user asks "did it actually do that?" or "is that agent's work right?".
model: opus
---

# Verify agent work

Agent self-reports in this repo have been wrong in specific, repeatable ways: files claimed but never touched, shared files rewritten despite being off-limits, imports missing from method bodies, whole scopes reverted while reporting success, and failing snapshots waved off as "expected". A detailed, itemized report is **not** more trustworthy than a vague one: the fabricated ones were the most specific. So check the working tree, not the report.

## 1. Run the script

```bash
python .claude/skills/verify-agent-work/verify.py --claimed <files the agent listed> --off-limits <files/folders you fenced off>
```

- `--claimed`: the agent's **Files changed** list. Prints files claimed but unchanged, and files changed but not claimed.
- `--off-limits`: every shared file or folder you told it not to touch (e.g. `Model/Content/Feature.py Model/Ledger`). A hit is a FAIL.
- `--root .claude/worktrees/<agent>`: inspect an agent that ran with `isolation: "worktree"` before you merge it.
- `--tests`: also runs `./run_tests.sh -q -x`. Add it once, after the last agent of a batch; the suite is too slow to run per agent.

It also compiles every changed `.py` file, runs pyflakes for undefined names (a missing import in a method body passes both compile and import), imports every changed module, flags uncommitted changes in other worktrees, and lists changed agent memory separately. Exit 1 means something failed.

Run it again after every **resume** of an agent, not only after its first run. One agent broke an off-limits file on a follow-up turn after a clean first pass.

## 2. Checks a script can't do

- **Skipped items.** If the agent says it skipped N items as "dynamic" or "not applicable", open two or three of them and confirm the reason is real. Abandoned work gets reported as deliberate skips.
- **Coverage.** For a migration, re-grep the old pattern and count what's left. Compare that count with the agent's claim.
- **Content judgment.** For tagging or classification, spot-check about 10 items against the source text. Haiku runs have mis-tagged about half of a sample while reporting success. For tests, confirm they call engine code and take expected values from the rules, not from the code under test.
- **Snapshot failures.** Never accept "the snapshot failures are expected". Look at the diff, and regenerate only if the change is intended (`UPDATE_SNAPSHOTS=1 ./run_tests.sh tests/test_build_snapshots.py`).
- **Runtime.** For a method added across many classes, call it on one instance per pattern. Importing succeeds even when the method body would raise.

## 3. Curate what the agent learned

The script lists changed `.claude/agent-memory/` files separately. Read the diff (`git diff -- .claude/agent-memory/`, or the new file for a first lesson):

- **Delete** lessons that are wrong, guessed, or contradicted by what you just verified. A wrong lesson is worse than none, because it is injected into every future run.
- **Promote** a lesson that has proven itself, or a change the agent proposed under **Lessons**. Edit the agent's prompt or the skill, then delete the lesson from memory.
- **Add** the lesson yourself when your verification caught a mistake the agent didn't notice; agents rarely notice their own fabricated successes.

## 4. Report

Tell the user what you verified and what you found, including anything you fixed or any lesson you deleted. If you skipped a check, say so.
