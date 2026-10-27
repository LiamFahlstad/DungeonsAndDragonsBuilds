# git-commit lessons

- 2026-10-27: Your final message IS the report: write it out in full (hash, branch, title, full message, files, Black result, co-author, left uncommitted). One run committed correctly but returned only "placeholder", so the caller had to reconstruct everything from git.
- 2026-10-27: To stage single hunks, filter `git diff` output with a scratch Python script that writes bytes (`sys.stdout.buffer.write`), and set each kept hunk's `+start` to its `-start`. Text-mode stdout on Windows adds CRLF, and then `git apply --cached` fails with "while searching for" errors.
- 2026-10-27: To split `tests/snapshots/*.json` by build, load HEAD's JSON, copy in only the wanted build keys from the working file, write `json.dumps(d, indent=1, sort_keys=True) + "\n"` as LF bytes (reproduces HEAD exactly), then `git hash-object -w --no-filters` + `git update-index --cacheinfo 100644,<hash>,<path>`. Easier and safer than hunk filtering.
- 2026-10-27: When the index already holds another group's staged changes, commit that group first; there is no clean way to commit a partial-file stage alongside unrelated staged work.
