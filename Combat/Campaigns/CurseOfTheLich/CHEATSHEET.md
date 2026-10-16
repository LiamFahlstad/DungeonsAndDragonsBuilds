# Curse of the Lich — Cheat Sheet

Run from the repo root. Everything for this campaign lives in
`Combat/Campaigns/CurseOfTheLich/`:

- `Players.py`: the tracked party
- `Encounters.py`: the monsters for each fight
- `Campaign.py`: the scenarios
- `PlayerLogs/`: the party's log
- `CombatLogs/`: one encounter log per scenario

All commands below track the "Players" party continuously in
`PlayerLogs/main_party.json`. Every run preloads HP/conditions/spell slots from
the last session and appends a new one (`encounter` if `--scenario` is given,
`adventure` if not).

Each scenario also has its own persistent encounter log in `CombatLogs/`
(non-player combatants only: HP, conditions, round number). Passing `--log`
resumes that scenario where it left off instead of starting monsters fresh. The
files start out empty (`{"round_number": 1, "combatants": []}`, a copy of
`CombatLogs/empty.json`) and fill in as you play.

The commands work the same in PowerShell and Git Bash.

## Adventure (out of combat)

```
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json
```

`curse_of_the_lich` is the default campaign, so no `--campaign` is needed.

## Encounters

| Scenario | Command |
|---|---|
| Ashelm Church | `python RunCombatSimulator.py --scenario ashelm_church --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --log Combat/Campaigns/CurseOfTheLich/CombatLogs/ashelm_church.json` |
| Goblin Scouting Party (easier) | `python RunCombatSimulator.py --scenario goblin_scouting_party --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --log Combat/Campaigns/CurseOfTheLich/CombatLogs/goblin_scouting_party.json --absent Gabriel Obmar Thum` |
| Goblin Warband Ambush (bigger) | `python RunCombatSimulator.py --scenario goblin_warband_ambush --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --log Combat/Campaigns/CurseOfTheLich/CombatLogs/goblin_warband_ambush.json --absent Gabriel Obmar Thum` |
| Wrath of Durmor (difficult) | `python RunCombatSimulator.py --scenario wrath_of_durmor --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --log Combat/Campaigns/CurseOfTheLich/CombatLogs/wrath_of_durmor.json --absent Gabriel Obmar Thum` |

- The goblin and Durmor encounters are balanced for three players (Edmund, Clover, Kivi), with Gabriel, Obmar and Thum absent.
- They also bring a friendly NPC, **Greypaw (Ally)**, shown alongside the monsters. `--difficulty` subtracts allies' XP from the monsters' XP and rates the fight on that net value (the monsters-only rating is printed too).

## Rests and stats

```
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report
```

The stats report writes `player_statistics_report.html` into this folder.
