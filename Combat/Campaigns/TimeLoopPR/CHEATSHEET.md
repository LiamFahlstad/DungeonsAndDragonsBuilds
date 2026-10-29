# Time Loop PR (oneshot) — Cheat Sheet

Run from the repo root. Everything for this oneshot lives in
`Combat/Campaigns/TimeLoopPR/`:

- `encounters.json`: the party and every encounter (format:
  [../ENCOUNTERS.md](../ENCOUNTERS.md)).
- `CombatLogs/<encounter id>.json`: one log per encounter, prepared from
  `encounters.json`, with every detail of its fight.
- `PlayerLogs/main_party.json`: where the party has been. Their current state is
  replayed from the encounter logs since the last long rest.

Party: Dessie (Artificer), Hanna (Ranger), Maggie (Druid), Thomas (Bard), all
level 3. After changing `encounters.json`, prepare the logs:

```
python -m Combat.Tools.prepare_encounters --campaign time_loop_pr
```

Hanna's drake and Dessie's Reanimator companion have stat blocks on their
character sheets, but the simulator doesn't add companions as combatants yet.

## Between encounters

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json
```

The party as they are now, with **Load Encounter...** (Ctrl+O), **Short Rest...**
and **Long Rest**.

## Encounters

| Encounter | Command |
|---|---|
| Outside the Gates (low) | `python RunCombatSimulator.py --scenario time_loop_pr_outside_the_gates --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |
| The Drunk Oxe (low) | `python RunCombatSimulator.py --scenario time_loop_pr_drunk_oxe --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |
| The Square (about 2.3× the High budget) | `python RunCombatSimulator.py --scenario time_loop_pr_square --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |

When a log holds a fight in progress, the window asks whether to continue it or
restart it (undoing it for the party too). Against the four level 3 players
(`--difficulty`): Outside the Gates is 600 XP (Low starts at 600), The Drunk Oxe
800 XP (just under Moderate's 900), and The Square 3650 XP against a High budget
of 1600.

## Rests and stats

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report --campaign time_loop_pr
```

The stats report writes `player_statistics_report.html` into this folder. It
covers every session, including those before long rests.
