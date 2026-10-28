# Curse of the Lich — Cheat Sheet

Run from the repo root. Everything for this campaign lives in
`Combat/Campaigns/CurseOfTheLich/`:

- `Players.py`: the tracked party
- `Encounters.py`: the monsters for each fight
- `Campaign.py`: the scenarios
- `PlayerLogs/main_party.json`: where the party has been
- `CombatLogs/`: what happened, one encounter log per scenario (plus one per
  adventure or short rest)

## The two logs

- **Encounter logs** (`CombatLogs/<scenario>.json`) hold every detail of a
  fight: each event, the monsters' HP and conditions, and the round.
  `--scenario` uses its log automatically and creates it if it's missing.
- **The player log** (`PlayerLogs/main_party.json`) only lists where the party
  has been, one line per encounter, adventure, short rest or long rest, each
  pointing to its encounter log.

Every run with `--player-log` rebuilds the party's current HP, conditions and
spell slots by replaying the players' events from the logs listed since the
last long rest. Both logs are committed, since the party's state comes from
them.

If a scenario's log holds a fight in progress, the window asks first:

- **Continue Encounter** picks the fight up where it stopped.
- **Restart Encounter** undoes the fight: the monsters come back fresh, its
  line leaves the player log, and the party is as they were before it. The old
  log is kept (not committed) as `CombatLogs/<scenario>_restarted_<timestamp>.json`.

## Switching encounters in the window

**Load Encounter...** (Ctrl+O) lists this campaign's scenarios with how far each
fight got ("Round 4, 5 of 9 standing, last played ..." or "Not started"). Pick
one and choose **Continue Encounter** or **Start / Restart Encounter**. The
party stays as it is, absent players included, so you can open an adventure
session and load each fight as the party reaches it, without restarting the
program. The fight you leave is already saved in its log.

**End Encounter** closes the current fight: it's marked as ended (with
`ended_at`) in its encounter log and on its line in the player log, the
monsters leave the window, and the party carries on as they are in an
adventure session. Load Encounter shows it as "Ended in round N"; continuing it
reopens the fight.

**Short Rest...** and **Long Rest** rest the party between fights: in an
adventure session, or with an encounter loaded but not started yet (so the
party can rest before it). A long rest restores them fully on the spot; a
short rest opens the healing window and logs its heals to a
`CombatLogs/short_rest_<timestamp>.json` of its own. Both get their line in
the player log, in the order they happened. The `--rest` flags below do the
same without opening the main window.

The commands work the same in PowerShell and Git Bash.

## Adventure (out of combat)

```
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json
```

`curse_of_the_lich` is the default campaign, so no `--campaign` is needed.

## Encounters

| Scenario | Command |
|---|---|
| Ashelm Church | `python RunCombatSimulator.py --scenario ashelm_church --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Goblin Scouting Party (played) | `python RunCombatSimulator.py --scenario goblin_scouting_party --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --absent Gabriel Obmar Thum` |
| Goblin Warband Ambush (moderate) | `python RunCombatSimulator.py --scenario goblin_warband_ambush --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Wrath of Durmor (high) | `python RunCombatSimulator.py --scenario wrath_of_durmor --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |

- The Goblin Scouting Party was balanced for three level 3 players (Edmund, Clover, Kivi), with Gabriel, Obmar and Thum absent. It has been played: its log holds the fight as it stopped in round 4, so the command above offers to continue it there.
- The Goblin Warband Ambush and Wrath of Durmor are balanced for the full party of six level 4 players: Moderate (2500 XP, 2300 net of Greypaw) and High (3200 XP, 3000 net of Greypaw).
- They also bring a friendly NPC, **Greypaw (Ally)**, shown alongside the monsters. `--difficulty` subtracts allies' XP from the monsters' XP and rates the fight on that net value (the monsters-only rating is printed too).

## Rests and stats

```
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report
```

The stats report writes `player_statistics_report.html` into this folder. It
covers every session, including those before long rests (and the older
`PlayerLogs/main_party_long_rest_*.json` archives).
