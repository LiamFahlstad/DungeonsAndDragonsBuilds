# Combat Simulator Cheat Sheet

Every campaign is self-contained in `Combat/Campaigns/<Campaign>/`, which has its
own cheat sheet with the exact commands to run it:

- [Curse of the Lich](Campaigns/CurseOfTheLich/CHEATSHEET.md) (`curse_of_the_lich`, the default campaign)
- [Time Loop PR (oneshot)](Campaigns/TimeLoopPR/CHEATSHEET.md) (`time_loop_pr`)
- [Grim's Castle](Campaigns/GrimsCastle/CHEATSHEET.md) (`grims_castle`, placeholder party)

## Campaign layout

```
Combat/Campaigns/<Campaign>/
├─ encounters.py    CONFIG: the party and every encounter (format: Campaigns/ENCOUNTERS.md)
├─ Campaign.py      CAMPAIGN = Campaign.from_config(CONFIG, <this folder>)
├─ CHEATSHEET.md    commands for this campaign
├─ PlayerLogs/      main_party.json: where the party has been (encounters, rests)
└─ CombatLogs/      <encounter id>.json: one prepared log per encounter
```

To add a campaign, create that folder with an `encounters.py` and a
one-line `Campaign.py`, and register its `CAMPAIGN` in `Combat/Scenarios.py`.
Encounter ids must be unique across all campaigns. After changing an
`encounters.py`, prepare its logs:

```
python -m Combat.Tools.prepare_encounters --campaign <name>   # or --all, or --check
```

## Flags

- `--scenario <id>`: play an encounter from its campaign's `encounters.py` (its log must be prepared). Its campaign is picked automatically, and the players taking part come from the config.
- `--campaign <name>`: choose the campaign when there's no `--scenario` (the party between encounters, and rests). Defaults to `curse_of_the_lich`.
- `--player-log <path>`: track the campaign's party across sessions. Omit it to play an encounter without touching the persistent party. With `--player-log` but no `--scenario`, the window opens on the party between encounters; with neither, the campaign's first encounter runs.
- `--rest long|short`: rest the tracked party (requires `--player-log`).
- `--difficulty`: print the encounter's D&D 2024 difficulty against the players taking part and exit. Allies' XP is subtracted from the monsters' XP.
