# Time Loop PR (oneshot) — Cheat Sheet

Run from the repo root. Everything for this oneshot lives in
`Combat/Campaigns/TimeLoopPR/`:

- `Players.py`: the tracked party
- `Encounters.py`: the monsters for each fight
- `Campaign.py`: the scenarios
- `PlayerLogs/`: the party's log
- `CombatLogs/`: one encounter log per scenario

Party: Dessie (Artificer), Hanna (Ranger), Maggie (Druid), all level 3, tracked in
`PlayerLogs/main_party.json`. Each scenario has its own persistent encounter log
in `CombatLogs/`. `--log` resumes it, and dropping `--log` starts monsters fresh.

Hanna's drake and Dessie's Reanimator companion have no stat blocks in the
simulator yet, so they don't appear as combatants.

## Adventure (out of combat)

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json
```

## Encounters

| Scenario | Command |
|---|---|
| The Drunk Oxe (moderate) | `python RunCombatSimulator.py --scenario time_loop_pr_drunk_oxe --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --log Combat/Campaigns/TimeLoopPR/CombatLogs/time_loop_pr_drunk_oxe.json` |
| The Square (about 3× the High budget) | `python RunCombatSimulator.py --scenario time_loop_pr_square --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --log Combat/Campaigns/TimeLoopPR/CombatLogs/time_loop_pr_square.json` |

## Rests and stats

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report --campaign time_loop_pr
```

The stats report writes `player_statistics_report.html` into this folder.
