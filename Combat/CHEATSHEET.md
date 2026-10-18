# Combat Simulator Cheat Sheet

Every campaign is self-contained in `Combat/Campaigns/<Campaign>/`, which has its
own cheat sheet with the exact commands to run it:

- [Curse of the Lich](Campaigns/CurseOfTheLich/CHEATSHEET.md) (`curse_of_the_lich`, the default campaign)
- [Time Loop PR (oneshot)](Campaigns/TimeLoopPR/CHEATSHEET.md) (`time_loop_pr`)
- [Grim's Castle](Campaigns/GrimsCastle/CHEATSHEET.md) (`grims_castle`, placeholder party)

## Campaign layout

```
Combat/Campaigns/<Campaign>/
├─ Players.py      get_players_group(): the party tracked by --player-log
├─ Encounters.py   functions returning each fight's monsters
├─ Campaign.py     CAMPAIGN = Campaign(name, folder, players, scenarios=[...])
├─ CHEATSHEET.md   commands for this campaign
├─ PlayerLogs/     main_party.json (+ timestamped long-rest backups)
└─ CombatLogs/     one persistent encounter log per scenario, plus timestamped
                   encounter_log_*.json from runs without --log
```

To add a campaign, create that folder and register its `CAMPAIGN` in
`Combat/Scenarios.py`. Scenario names must be unique across all campaigns.

## Flags

- `--scenario <name>`: run an encounter. Its campaign is picked automatically.
- `--campaign <name>`: choose the campaign when there's no `--scenario` (adventure sessions and rests). Defaults to `curse_of_the_lich`. The campaign decides which party `--player-log` loads and which `CombatLogs/` folder new encounter logs go to.
- `--player-log <path>`: track the campaign's party across sessions. Omit it to run a one-off scenario without touching the persistent party. With neither `--scenario` nor `--player-log`, the campaign's first scenario runs.
- `--log <path>`: resume a persistent encounter log (non-player combatants only). Drop it to start monsters fresh.
- `--absent <name> [<name> ...]`: leave players out of the tracked party for this session (case-insensitive partial name match, e.g. `--absent Gabriel`). Their player-log history is kept and picks up again the next time they join.
- `--rest long|short`: rest the tracked party (requires `--player-log`).
- `--difficulty`: print the encounter's D&D 2024 difficulty against the party and exit. Allies' XP is subtracted from the monsters' XP.
