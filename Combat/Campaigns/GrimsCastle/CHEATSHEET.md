# Grim's Castle — Cheat Sheet

Run from the repo root. Everything for this campaign lives in
`Combat/Campaigns/GrimsCastle/`:

- `encounters.py`: the encounters (format: [../ENCOUNTERS.md](../ENCOUNTERS.md)).
  Its party is empty, since there are no character sheets yet.
- `CombatLogs/<encounter id>.json`: one log per encounter, prepared from
  `encounters.py`.

The four placeholder players (Player 1–4) join each encounter as allies, so the
party appears in the combat window without `--player-log`. Because there are no
character sheets, `--difficulty` can't rate these fights.

After changing `encounters.py`, prepare the logs:

```
python -m Combat.Tools.prepare_encounters --campaign grims_castle
```

## Encounters

| Encounter | Command |
|---|---|
| The Bull | `python RunCombatSimulator.py --scenario grims_castle_bull` |

When its log holds a fight in progress, the window asks whether to continue it
or restart it with fresh monsters.
