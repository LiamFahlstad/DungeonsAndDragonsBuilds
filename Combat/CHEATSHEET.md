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
| Time Loop — Square | `python RunCombatSimulator.py --scenario time_loop_square --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/time_loop_square.json` |
| Time Loop — Drunk Oxe | `python RunCombatSimulator.py --scenario time_loop_drunk_oxe --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/time_loop_drunk_oxe.json` |
| Grim's Castle — Bull | `python RunCombatSimulator.py --scenario grims_castle_bull --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/grims_castle_bull.json` |
| Curse of the Lich — Black Tongues Skirmish | `python RunCombatSimulator.py --scenario curse_of_the_lich_black_tongues_skirmish --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/curse_of_the_lich_black_tongues_skirmish.json` |
| Curse of the Lich — Yellow Capes Patrol | `python RunCombatSimulator.py --scenario curse_of_the_lich_yellow_capes_patrol --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/curse_of_the_lich_yellow_capes_patrol.json` |
| Curse of the Lich — Black Tongues Ritual | `python RunCombatSimulator.py --scenario curse_of_the_lich_black_tongues_ritual --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/curse_of_the_lich_black_tongues_ritual.json` |
| Curse of the Lich — Yellow Capes Last Stand | `python RunCombatSimulator.py --scenario curse_of_the_lich_yellow_capes_last_stand --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/curse_of_the_lich_yellow_capes_last_stand.json` |
| Curse of the Lich — Mouth That Walks | `python RunCombatSimulator.py --scenario curse_of_the_lich_mouth_that_walks --player-log Combat/PlayerLogs/main_party.json --log Combat/CombatLogs/curse_of_the_lich_mouth_that_walks.json` |

## Other flags

- `--log <path>` — resume a persistent encounter log (non-player combatants only). Each scenario above is wired to its own file under `Combat/CombatLogs/`; drop the flag to start monsters fresh instead of resuming.
- Omit `--player-log` entirely to run a one-off scenario without touching the persistent party (old behavior, defaults to `time_loop_square` if `--scenario` is also omitted).
