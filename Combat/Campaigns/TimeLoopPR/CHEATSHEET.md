# Time Loop PR (oneshot) — Cheat Sheet

Run from the repo root. Everything for this oneshot lives in
`Combat/Campaigns/TimeLoopPR/`:

- `encounters.py`: the party and every encounter (format:
  [../ENCOUNTERS.md](../ENCOUNTERS.md)).
- `CombatLogs/<encounter id>.json`: one log per encounter, prepared from
  `encounters.py`, with every detail of its fight.
- `PlayerLogs/main_party.json`: where the party has been. Their current state is
  replayed from the encounter logs since the last long rest.

Party: Dessie (Artificer), Hanna (Ranger), Maggie (Druid), Thomas (Bard), all
level 3. After changing `encounters.py`, prepare the logs:

```
python -m Combat.Tools.prepare_encounters --campaign time_loop_pr
```

Dessie's Reanimated Companion and Hanna's Drake Companion join a fight when
they're summoned, as "Dessie's Reanimated Companion" and "Hanna's Drake
Companion". They roll no initiative: each takes its turn right after its
owner's. To summon one, select Dessie or Hanna and use **Enable Feature**, or
right-click the owner's card (or the summon's) and pick **Summon ...**; for
the drake, pick its Draconic Essence there. That spends the feature's use (then
a spell slot) and brings it out at full HP. **Dismiss** in the summon's menu
sends it away. One that's out stays out into the next encounter until a long
rest, and if its owner dies it drops to 0 HP. One summoned before the fight:
**Add Combatant**, "Already summoned…". The logs played before this hold
"Dessie's Companion" and "Hanna's Companion", hidden; they still load. See
"Players' summons" in [../ENCOUNTERS.md](../ENCOUNTERS.md).

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
| The Square (high; moderate without Mirelle) | `python RunCombatSimulator.py --scenario time_loop_pr_square --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |
| Mira (final fight; 1.5x high) | `python RunCombatSimulator.py --scenario time_loop_pr_mira --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json` |

When a log holds a fight in progress, the window asks whether to continue it or
restart it (undoing it for the party too). Against the four level 3 players
(`--difficulty`): Outside the Gates and The Drunk Oxe are 600 XP each (the Low
budget), and The Square is 1600 XP (the High budget): its guards alone are
900 XP (Moderate), three pairs that each share one turn (two Gilded Sentinels,
Animated Armor; two Watch Officers, Spy; two Guard Dogs, Wolf), and Mirelle,
the Gilded Knight (homebrew CR 3, in
`Combat/Monsters/CR_3/monsters_homebrew.py`) adds 700. Mira is 2500 XP, about
1.5x the High budget: Mira, Princess of the Loop (homebrew CR 5, in
`Combat/Monsters/CR_5/monsters_homebrew.py`) is 1800, and her Warrior
(Mirelle's stat block) 700.

## Rests and stats

```
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest short
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json --rest long
python -m Combat.Tools.create_player_statistics_report --campaign time_loop_pr
```

The stats report writes `player_statistics_report.html` into this folder. It
covers every session, including those before long rests.
