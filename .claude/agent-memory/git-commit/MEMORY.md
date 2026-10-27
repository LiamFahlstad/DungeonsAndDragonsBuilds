# git-commit lessons

- 2026-10-27: Your final message IS the report: write it out in full (hash, branch, title, full message, files, Black result, co-author, left uncommitted). One run committed correctly but returned only "placeholder", so the caller had to reconstruct everything from git.
- 2026-10-27: To stage single hunks, filter `git diff` output with a scratch Python script that writes bytes (`sys.stdout.buffer.write`), and set each kept hunk's `+start` to its `-start`. Text-mode stdout on Windows adds CRLF, and then `git apply --cached` fails with "while searching for" errors.
