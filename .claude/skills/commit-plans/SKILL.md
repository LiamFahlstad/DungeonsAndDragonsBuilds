---
name: commit-plans
description: Commit plans - commits written down instead of made, so committing stays safe while many agents edit, stage and commit in the same tree. A plan holds the commit message and, per file, the exact content to commit, recorded by a script that stores everything under .claude/commit-plans/ (git-ignored, shared from worktrees). A later run applies pending plans - it refuses a plan when a file moved since planning, builds the commit in a private index so other agents' staged files can't ride along, and moves HEAD with a compare-and-swap - and a push check prints the exact `git push <hash>:<target>` command when that's safe. Use when committing in this repo (the git-commit agent's plan and apply modes), when asked to "plan a commit", "apply the commit plans", "what's waiting to be committed?", or why a plan is blocked.
---

# Commit plans

Many agents work in this one tree at once. Committing directly means staging in a shared index while others stage too, and pushing `HEAD` while others commit on top. So a commit happens in two steps, usually by two different runs of the `git-commit` agent:

1. **Plan** - decide what belongs together, write the message, record the plan. Nothing is staged, committed or pushed.
2. **Apply** - later, commit the pending plans that still hold, then push if the plan or the caller named a target.

## The script

```bash
S=.claude/skills/commit-plans/commit_plan.py
python $S new --message-file <scratchpad>/msg.txt --by git-commit --push main \
    --path Model/View.py --path tests/test_view.py \
    --content tests/snapshots/sheet_hashes.json=<scratchpad>/sheet_hashes.json \
    --left "Combat/CombatUIQt/app.py: another agent's work in progress"
python $S list                      # pending plans; --state blocked|done|dropped|applying|all
python $S show CP-... --diff        # message, files, +/- lines, history, the full diff
python $S check --all               # dry run: ready / already in HEAD / BLOCKED and why
python $S apply --all               # commit every pending plan that holds, oldest first
python $S push-check --target main <hash>...   # safe to push? prints the command
python $S requeue CP-...            # blocked or crashed (applying) -> pending again
python $S drop CP-... --reason "superseded by CP-..."
```

- **`--path P`** commits the whole working-tree file as it is *now* (or its deletion if it's gone). The script stores that content as a git blob at once, so later edits by anyone don't change what the plan commits.
- **`--content P=FILE`** commits FILE's exact bytes as P: a partial change, when P also holds someone else's edits. Build FILE from `git show HEAD:P` plus only your part, write it with LF line endings as bytes, and keep it in your scratchpad (the git-commit memory has recipes for snapshot JSON and line-based files).
- **`--message-file`**: title line (about 72 characters at most), a blank line, the body, the trailers. The script checks the title and that every planned `.py` file compiles.
- **`--push`** records what the caller said: `main`, `branch` (the current branch), or `ask` (the default: nobody said, so the user must be asked before pushing).
- One file can be in only one pending plan. If `new` says a path is taken, report it: the caller decides whether to apply or drop the other plan first.

## What apply guarantees

For each plan, `apply` commits exactly the planned blobs on top of the current HEAD, or blocks it with the reason:

- **Blocked** when a planned file changed in HEAD since planning (someone committed it), changed in the working tree since planning (someone kept editing it), has other staged changes, or when the branch or checkout differs. A blocked plan is stale: re-plan it from the current diff, then `drop` the old one. Use `requeue` only when the block was transient (a different branch checked out, a crashed apply).
- **Already in HEAD** when every planned file already has the planned content: it's marked done without a new commit.
- The commit is built in a private index and HEAD moves with `git update-ref HEAD <new> <old>`, so files other agents have staged never ride along and a commit someone made in between is never overwritten (it retries on the new HEAD). The shared index is then pointed at the committed blobs, so `git status` stays clean for those paths. Other agents' staged work stays staged.
- There are no git hooks in this repo; `apply` doesn't run any.

## Pushing

`apply` never pushes. Pushing is the agent's own `git push` command, so the user's permission prompt for `git push` still applies:

1. `python $S push-check --target main <every hash this apply made, oldest first>`. It fetches, checks that the push is a fast-forward, and refuses when `origin/main..<last hash>` holds a commit that isn't yours (another agent's unpushed commit would ride along).
2. If it says Safe, run the `git push origin <hash>:main` it prints, as a command of its own, then the confirm command it prints.
3. Otherwise report its output; never force-push, rebase or merge to make it fit.

## Where plans live

`<main checkout>/.claude/commit-plans/<state>/<id>/` with `plan.json` (files, blobs, push target, history), `message.txt`, and nothing else once done. Every worktree and agent sees the same plans. The folder is git-ignored; never commit it. Done and dropped plans can be deleted whenever they're no longer interesting.
