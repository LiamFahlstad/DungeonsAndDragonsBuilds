# Grim's Castle — Cheat Sheet

Run from the repo root. Everything for this campaign lives in
`Combat/Campaigns/GrimsCastle/`:

- `Players.py`: the tracked party (empty, since there are no character sheets yet)
- `Encounters.py`: the monsters for each fight, plus four placeholder players
- `Campaign.py`: the scenarios
- `CombatLogs/`: the encounter logs (created on the first run)

The four placeholder players (Player 1–4) join each scenario as allies, so the
party appears in the combat window without `--player-log`. Because there are no
character sheets, `--difficulty` can't rate these fights.

## Encounters

| Scenario | Command |
|---|---|
| The Bull | `python RunCombatSimulator.py --scenario grims_castle_bull` |

To make the fight persistent, create
`Combat/Campaigns/GrimsCastle/CombatLogs/grims_castle_bull.json` containing
`{"round_number": 1, "combatants": []}` and add
`--log Combat/Campaigns/GrimsCastle/CombatLogs/grims_castle_bull.json`.
`--log` needs the file to exist, and combat logs are gitignored, so a fresh
clone has none to copy from.
