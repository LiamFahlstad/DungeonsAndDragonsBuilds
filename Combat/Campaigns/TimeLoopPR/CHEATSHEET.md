# Time Loop PR (oneshot) — Cheat Sheet

Run from the repo root. Everything for this oneshot lives in
`Combat/Campaigns/TimeLoopPR/`:

- `Players.py`: the tracked party
- `Encounters.py`: the monsters for each fight
- `Campaign.py`: the scenarios
- `PlayerLogs/main_party.json`: where the party has been
- `CombatLogs/`: what happened, one encounter log per scenario

Party: Dessie (Artificer), Hanna (Ranger), Maggie (Druid), Thomas (Bard), all level 3, tracked in
`PlayerLogs/main_party.json`. Each scenario has its own persistent encounter log,
`CombatLogs/<scenario>.json`, used automatically, with every detail of the
fight. The player log only lists where the party has been; their current state
is replayed from the encounter logs since the last long rest. When a log holds a
fight in progress, the window asks whether to continue it or restart it
(undoing it for the party too). **Load Encounter...** (Ctrl+O) in the window switches to another
scenario the same way.

Hanna's drake and Dessie's Reanimator companion have stat blocks on their
character sheets, but the simulator doesn't add companions as combatants yet.

## Adventure (out of combat)

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json
```

## Encounters

| Scenario | Command |
|---|---|
| Outside the Gates (low) | `python RunCombatSimulator.py --scenario time_loop_pr_outside_the_gates --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |
| The Drunk Oxe (low) | `python RunCombatSimulator.py --scenario time_loop_pr_drunk_oxe --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |
| The Square (about 2.3× the High budget) | `python RunCombatSimulator.py --scenario time_loop_pr_square --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |

Against the four level 3 players (`--difficulty`): Outside the Gates is 600 XP
(Low starts at 600), The Drunk Oxe 800 XP (just under Moderate's 900), and The
Square 3650 XP against a High budget of 1600.

## Rests and stats

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report --campaign time_loop_pr
```

The stats report writes `player_statistics_report.html` into this folder. It
covers every session, including those before long rests (and the older
`PlayerLogs/main_party_long_rest_*.json` archives).
