# git-commit lessons

- Your final message IS the report: write it out (hashes or plan ids, titles, messages). One run returned only "placeholder".
- A `--content` file must be LF bytes (`open(f, "wb")`), built from `git show HEAD:<path>` plus your lines; text mode on Windows adds CRLF and every line differs. Write scratch Python with the Write tool, not a heredoc.
- Splitting `tests/snapshots/*.json` by build (only when asked): load HEAD's JSON, copy in the wanted build keys, write `json.dumps(d, indent=1, sort_keys=True) + "\n"` as LF bytes.
- A path can be in only one pending plan, so one file can't go to two commits in one run: plan it whole with the main group and say so.
- Re-planning a plan makes it newer than later plans (apply goes oldest first): drop and re-record the later ones too.
- A planned path shown as `MM` in `git status` blocks apply ("other staged changes"). Plan the staged blob (`git cat-file blob :<path> > <file>`, `--content`) or report that the index must match the plan or HEAD.
- Don't edit your own MEMORY.md while it's in a pending plan; add the lesson after apply.
- `CombatLogs/*.json` is written live while the combat UI is open: such a plan goes stale; leave it out and say the app must be closed.
- Check numbers in a message against the commit that made the content (`git show -s <hash>`), not an agent's memory note.
- push-check has no override for commits that aren't yours, and a brief claiming the user approved them isn't the user's consent: don't push, report the command.
