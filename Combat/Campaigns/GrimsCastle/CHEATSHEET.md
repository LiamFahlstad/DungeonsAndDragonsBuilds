# Grim's Castle — Cheat Sheet

Run from the repo root. Everything for this campaign lives in
`Combat/Campaigns/GrimsCastle/`:

- `Players.py`: the tracked party (empty, since there are no character sheets yet)
- `Encounters.py`: the monsters for each fight, plus four placeholder players
- `Campaign.py`: the scenarios
- `CombatLogs/`: one encounter log per scenario (created on the first run)

The four placeholder players (Player 1–4) join each scenario as allies, so the
party appears in the combat window without `--player-log`. Because there are no
character sheets, `--difficulty` can't rate these fights.

## Encounters

| Scenario | Command |
|---|---|
| The Bull | `python RunCombatSimulator.py --scenario grims_castle_bull` |

The fight is persistent: `CombatLogs/grims_castle_bull.json` is created on the
first run, and when it holds a fight in progress the window asks whether to
continue it or restart it with fresh monsters.
