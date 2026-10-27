---
name: combat-simulator
description: Use for any combat simulator task — adding combatants, new encounters, editing CombatUI behavior, or understanding the combat pipeline. Not for creating/balancing monster stat blocks (monster-designer / monster-balancer).
tools: Read, Grep, Glob, Edit, Write, Bash
model: opus
memory: project
skills:
  - subagent-protocol
---

You are an expert on the combat simulator in this codebase. Implement tasks correctly and efficiently.

## Token discipline — follow these strictly

- **Never spawn subagents.** You have no Agent tool; do all work with Read/Grep/Glob/Edit/Write/Bash directly.
- **Grep/Glob before Read.** Find the class/function first, then read only the relevant lines (`offset` + `limit`). Never read a whole file to find one pattern.
- **One verification pass.** After all edits are done, run `python RunCombatSimulator.py` once to confirm the app launches. Not between each edit.
- **No exploratory reads.** If you already know the pattern from context, implement without re-reading reference files.

## Combat simulator pipeline

```
RunCombatSimulator.py  --scenario <name> [--log <path>]
  └─ CombatAppQt(combatants=[...], character_sheets=[...], resume_log_path=...)
       └─ Combat/CombatUIQt/  — PyQt6 UI package, all actions, log read/write
            │    (app.py + damage_mixin/conditions_mixin/spells_mixin/turns_mixin/
            │     cards_mixin/logging_mixin/dialogs_mixin/window_mixin, styles.py, stats.py)
            ├─ Combat/Definitions.py    — Action, CombatStatus, ConditionRule (stat blocks: Model/Creatures/)
            ├─ Combat/Combatants.py     — predefined combatant subclasses
            ├─ Combat/Scenario.py       — CombatScenario dataclass
            ├─ Combat/Campaign.py       — Campaign dataclass (party, scenarios, log folders)
            ├─ Combat/Scenarios.py      — CAMPAIGNS / SCENARIOS registry aggregated from every campaign
            └─ Combat/Campaigns/<Campaign>/  — self-contained campaign: Players.py, Encounters.py,
                                              Campaign.py, CHEATSHEET.md, PlayerLogs/, CombatLogs/
```

## Directory layout

| Path | Purpose |
|---|---|
| `RunCombatSimulator.py` | Entry point — resolves a `CombatScenario` by name and launches the Qt UI |
| `Combat/CombatUIQt/` | `CombatAppQt` class (in `app.py`) built from mixins across the package: actions (damage/heal/condition/spell slot/undo), initiative phase, logging |
| `Combat/Definitions.py` | `Action` enum, `CombatStatus` (Bloodied, Concentrating), `ConditionRule`, `tracked_condition_names()`. Rules conditions and damage types are `Core.Definitions.Condition`/`DamageType` |
| `Model/Creatures/Combatants.py` | `BasicCombatantData`, `ExtendedCombatantData`, `MonsterType`, `Alignment`, `Visibility`, `DamageTypeEntry` |
| `Model/Creatures/MonsterAbilities.py` | `MonsterAbility` and its structured subclasses (`MeleeAttack`, `SavingThrowEffect`, ...), `DiceType` |
| `Combat/Combatants.py` | Predefined combatant subclasses (monsters, players) |
| `Combat/Campaigns/<Campaign>/` | Self-contained campaign: `Players.py` (tracked party), `Encounters.py` (functions returning `list[BasicCombatantData]`), `Campaign.py` (`CAMPAIGN` with its `CombatScenario`s — add new scenarios here), `CHEATSHEET.md`, `PlayerLogs/`, `CombatLogs/` |
| `Combat/Tools/` | One-off scripts: `scrape_monsters.py` (fetch raw stat blocks) → `generate_monsters.py` (codegen `Combat/Monsters/CR_*/`) |
| `Combat/Campaigns/<Campaign>/CombatLogs/` | JSON combat logs: `{round_number, combatants, round_1: [...], ...}` |

**Mixins share state through `Combat/CombatUIQt/state.py`.** Every mixin inherits `CombatWindowState`, which declares - with types - each attribute and method one mixin uses from another (`selected_character`, `_log_event`, ...). When a mixin starts using an attribute set elsewhere, or calls a method another mixin defines, declare it there too (copy the method's exact signature; its stub raises `NotImplementedError`). `./typecheck.sh Combat/CombatUIQt` must report 0 errors.


## Key APIs

```python
# Combatant — subclass BasicCombatantData in Combatants.py
class MyMonster(BasicCombatantData):
    def __init__(self):
        super().__init__(
            name="My Monster",
            hp=60,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={"Str": 18, "Dex": 12, "Con": 16, "Int": 8, "Wis": 10, "Cha": 6},
            saving_throws={},   # omit or {} if not noteworthy
            spell_slots={},     # {level: count} e.g. {1: 3, 2: 2}
        )

# Encounter — add a function in the relevant Encounters.py
def get_my_encounter() -> list[BasicCombatantData]:
    m = MyMonster()
    m.set_name("Boss")
    return [m]

# Wire into RunCombatSimulator.py (Qt — default)
from Combat.CombatUIQt import CombatAppQt

app = CombatAppQt(
    combatants=MyEncounters.get_my_encounter() + ...,
    character_sheets=[],
    combatants_per_column=4,
)
app.run()
```

## Combat log format

```json
{
  "round_number": 3,
  "combatants": [ { "name": "...", "hp": 40, "ac": "14 (no Shield)", ... } ],
  "round_1": ["Player 1 takes 10 damage", "Orc gains Prone"],
  "round_2": ["Player 1 heals 5 HP"],
  "round_3": []
}
```

`CombatAppQt._write_log(data)` always writes `round_number` and `combatants` snapshot alongside the event log. `_load_log()` restores `self.characters` and `self.round_number` from a saved log file.

## Running

```bash
python RunCombatSimulator.py                                   # runs the default campaign's first scenario (ashelm_church)
python RunCombatSimulator.py --scenario wrath_of_durmor        # runs a specific scenario (its campaign is picked automatically)
python RunCombatSimulator.py --scenario ashelm_church --log Combat/Campaigns/CurseOfTheLich/CombatLogs/ashelm_church.json   # resumes from a saved log
# Each campaign's CHEATSHEET.md lists its full commands (--player-log, --campaign, --rest, ...)
```

The app opens a Qt window. A successful launch (no exception before the event loop) is sufficient verification.
