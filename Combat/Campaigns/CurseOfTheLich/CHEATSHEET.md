# Curse of the Lich — Cheat Sheet

Run from the repo root. The commands work the same in PowerShell and Git Bash.
Everything for this campaign lives in `Combat/Campaigns/CurseOfTheLich/`:

- `encounters.json`: the party and every encounter (monsters, allies, who takes
  part). The format is in [../ENCOUNTERS.md](../ENCOUNTERS.md).
- `CombatLogs/<encounter id>.json`: one log per encounter, prepared from
  `encounters.json`, with every detail of its fight.
- `PlayerLogs/main_party.json`: where the party has been (encounters, short and
  long rests). The party's current HP, conditions and slots are replayed from
  the encounter logs since the last long rest.

Both logs are committed, since the party's state comes from them.

## Adding or changing an encounter

1. Edit `encounters.json`.
2. Prepare its log (checks the whole config first, writes nothing if it's wrong):

```
python -m Combat.Tools.prepare_encounters --campaign curse_of_the_lich
```

A log whose fight hasn't started is updated to match the config; one in progress
or ended is left alone.

## Between encounters

```
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json
```

The window shows the party as they are now. **Load Encounter...** (Ctrl+O)
lists every encounter with how far its fight got ("Ready", "Round 4, 5 of 9
standing", "Ended in round 5", or "Not prepared"), with its description,
difficulty, players and monsters. **Short Rest...** and **Long Rest** rest the
party; they also work with an encounter loaded but not started, so the party
can rest before it. Nothing else is logged between encounters.

## Encounters

| Encounter | Players | Command |
|---|---|---|
| Ashelm Church (ended) | whole party | `python RunCombatSimulator.py --scenario ashelm_church --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Goblin Scouting Party (in progress, round 4) | Edmund, Clover, Kivi | `python RunCombatSimulator.py --scenario goblin_scouting_party --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Goblin Warband Ambush (moderate) | whole party | `python RunCombatSimulator.py --scenario goblin_warband_ambush --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Wrath of Durmor (high) | whole party | `python RunCombatSimulator.py --scenario wrath_of_durmor --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Black Tongues Skirmish | whole party | `python RunCombatSimulator.py --scenario black_tongues_skirmish --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Yellow Capes Patrol | whole party | `python RunCombatSimulator.py --scenario yellow_capes_patrol --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Black Tongues Ritual | whole party | `python RunCombatSimulator.py --scenario black_tongues_ritual --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| Yellow Capes' Last Stand | whole party | `python RunCombatSimulator.py --scenario yellow_capes_last_stand --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |
| The Mouth That Walks | whole party | `python RunCombatSimulator.py --scenario mouth_that_walks --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json` |

Or open the party between encounters and pick one with Load Encounter.

- Who takes part comes from `encounters.json` (`"players"`); change it there and
  re-prepare, before the fight starts.
- If an encounter's log holds a fight in progress, the window asks first:
  **Continue Encounter** picks it up where it stopped; **Restart Encounter**
  undoes it (fresh monsters from the config, its line leaves the player log,
  and the party is as they were before it; the old log is kept, not committed,
  as `CombatLogs/<id>_restarted_<timestamp>.json`).
- **End Encounter** marks the fight ended (`ended_at`, in its log and on its
  player-log line) and goes back to the party between encounters. Continuing
  it later reopens it.
- The goblin encounters bring a friendly NPC, **Greypaw (Ally)**. `--difficulty`
  subtracts allies' XP from the monsters' XP and rates the fight on that net
  value (the monsters-only rating is printed too), against the players taking
  part:

```
python RunCombatSimulator.py --scenario goblin_warband_ambush --difficulty
```

## Rests and stats

```
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --player-log Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report
```

A short rest records its heals and regained features on its own line in the
player log; a long rest is a line of its own. The stats report writes
`player_statistics_report.html` into this folder. It covers every session,
including those before long rests (and the older
`PlayerLogs/main_party_long_rest_*.json` archives).
