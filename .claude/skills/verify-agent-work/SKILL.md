---
name: verify-agent-work
description: Verify what subagents actually changed before trusting their reports - diff the working tree against the claimed files, compile, check for undefined names, import, check other worktrees, and run tests. Use after any subagent (especially haiku-tier or parallel batches) reports that it finished code or data changes, before telling the user the work is done.
---

# Verify agent work

Agent self-reports in this repo have been wrong in specific ways: files claimed but never touched, shared files rewritten despite being off-limits, imports missing from method bodies, whole scopes reverted while reporting success. A detailed report is not more trustworthy than a vague one. Check the working tree, not the report.

## 1. Run the script

```bash
python .claude/skills/verify-agent-work/verify.py --claimed <files the agent said it changed>
```

Add `--tests` once all agents in a batch are done (the full suite takes a while; don't run it per agent).

It prints: changed files, claimed-vs-actual, compile, pyflakes undefined names, imports, dirty sibling worktrees, and tests. Exit 1 means something failed.

## 2. Checks the script can't do

- **Off-limits files.** If you told agents not to touch shared files (e.g. `Model/Content/Feature.py`, `Model/Ledger/`), run `git diff --stat -- <those files>` and confirm they are unchanged, or changed only by you. Do this again after every resume of an agent, not just after its first run.
- **Skipped items.** If the agent says it skipped N items as "dynamic" or "not applicable", open 2-3 of them and confirm the reason is real.
- **Coverage.** For a migration, re-grep the old pattern and count what's left. Compare that count to what the agent claims.
- **Content judgment.** For tagging or classification work, spot-check about 10 items against the source text. For tests, confirm they call engine code and take expected values from the rules, not from the code.
- **Snapshot failures.** Never accept "the snapshot failures are expected" from an agent. Look at the diff, and regenerate only if the change is intended (`UPDATE_SNAPSHOTS=1 ./run_tests.sh tests/test_build_snapshots.py`).
- **Runtime.** For a method added across many classes, call it on one instance per pattern. Import succeeding does not mean the method runs.

## 3. Report

Tell the user what you verified and what you found, including anything you fixed. If you did not run a check, say so.
