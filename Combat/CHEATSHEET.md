# Combat Simulator Cheat Sheet

Run from the repo root. All commands below track the "Players" party continuously
in `Combat/PlayerLogs/main_party.json` — every run preloads HP/conditions/spell
slots from the last session and appends a new one (`encounter` if `--scenario`
is given, `adventure` if not).

Each scenario also has its own persistent encounter log under `Combat/CombatLogs/`
(non-player combatants only — HP, conditions, round number). Passing `--log`
resumes that scenario where it left off instead of starting monsters fresh; the
files start out empty (`{"round_number": 1, "combatants": []}`) and fill in as
you play.

PowerShell commands work as-is. In bash (Git Bash), swap `python` for `python`
too — the commands are identical either way.

## Adventure (default, out of combat)

```
python RunCombatSimulator.py --player-log Combat/PlayerLogs/main_party.json
```

## Encounters

| Scenario | Command |
|---|---|
| Ashelm Church | `python RunCombatSimulator.py --scenario ashelm_church --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/ashelm_church.json` |

## Other flags

- `--log <path>` — resume a persistent encounter log (non-player combatants only). Each scenario above is wired to its own file under `Combat/CombatLogs/`; drop the flag to start monsters fresh instead of resuming.
- Omit `--player-log` entirely to run a one-off scenario without touching the persistent party (old behavior, defaults to `time_loop_square` if `--scenario` is also omitted).
