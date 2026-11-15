---
name: combat-ui-explore
description: Exploratory testing of the PyQt6 combat UI through the real CombatAppQt - a harness (explore.py) that opens an encounter on a temp log and party log, drives it the way a GM does (start the fight, select source and targets, Use / Cast a picker row through its real Apply button, conditions, turns, menus, dialogs, the Player Screen, the battle map) and records every Qt console message, Python warning, exception in a callback, modal dialog and status message with the step and Python stack behind it, and checks state invariants (HP, slots, conditions, turn order), that Undo puts the state and the logged events back, and that reopening the log rebuilds the same fight. A sweep command opens everything once. Use when trying out the combat UI for bugs, combinations that break it or Qt warnings in the terminal, when checking that a combat UI change works as intended end to end (not only in unit tests), and when the user reports an error or warning while using the combat simulator. The combat-ui-tester agent preloads it.
---

# Explore the combat UI

Unit tests in `tests/test_combat_ui_*.py` pin down single operations. This skill finds what they miss: **combinations** (cast, then undo, then next turn; damage on a concentrating Wild Shaped druid; a summon whose owner drops), **state that drifts** (Undo that leaves a line in the log, a reopened fight that forgets something), and **terminal noise** (Qt style sheet, font or geometry warnings).

## The harness: `explore.py`

```bash
python .claude/skills/combat-ui-explore/explore.py scenarios                      # campaigns and their scenario ids
python .claude/skills/combat-ui-explore/explore.py sweep --scenario ashelm_church  # ~2 min: everything once
python .claude/skills/combat-ui-explore/explore.py sweep --all --no-stacks        # first scenario of each campaign
python .claude/skills/combat-ui-explore/explore.py sweep --scenario ashelm_church --native   # real Windows platform
```

`sweep` exits 1 when it found a problem. For combinations, write a probe script in the **scratchpad directory** (never the repo) and run it from the repo root:

```python
import random, sys
sys.path.insert(0, ".claude/skills/combat-ui-explore")
from explore import Session

random.seed(7)                                   # dice are random.randint: seed or monkeypatch them
with Session("ashelm_church") as s:              # Session(..., native=True, answer="no")
    s.start()                                    # distinct initiatives; s.start(first=char) to pick who goes first
    obmar, ghoul = s.char("Obmar"), s.char("Accursed Group of 3")
    print(s.picks(obmar))                        # every Use / Cast row Obmar has (EffectOption names)
    s.use_cast("Fire Bolt", source=obmar, targets=[ghoul])       # picks the row, presses Apply
    s.use_cast("Grease", source=obmar, targets=[ghoul], fill=lambda dlg: ..., apply=False)
    s.run("add Prone", s.ui._add_condition_to, ghoul, "Prone")    # any UI method, exception recorded
    s.check("after Prone")                       # invariants, recorded as findings
    s.undo_roundtrip(s.ui._advance_turn)         # do it, Undo it: same state and same logged events?
    s.replay_matches()                           # reopen the log in a fresh window: same fight?
print(s.report())                                # every finding with its step (and stack)
```

- `s.ui` is the `CombatAppQt`; `s.window` its main window (shown, offscreen by default). Call its methods as the buttons do: `_start_combat`, `_advance_turn`, `_apply_damage`, `_apply_heal`, `_add_condition_to(char, name)`, `_remove_condition_from`, `_undo_last`, `_card_menu(char)`, `_show_custom_condition_dialog(pick)`, `_end_encounter`. Find others with `grep -n "def _" Combat/CombatUIQt/*.py`; `state.py` lists the attributes and stubs every mixin shares.
- **Modals never block.** `QDialog.exec` shows the dialog, paints it, runs `s.on_dialog(dlg)` if a probe set one (`use_cast` and `picks` do), then closes it. `QMenu.exec` pops each menu and submenu up. A `QMessageBox.question` gets `answer` ("yes" by default: "Out of spell slots, cast anyway?"); the others get Ok. Each is recorded as `[dialog]`.
- **What a finding is.** `report()` lists `[qt]`, `[warning]`, `[exception]`, `[invariant]`, `[undo]` and `[replay]` as problems, and `[dialog]` / `[status]` (what the GM was shown) as information. A status message can still be the bug: "Nothing applied" after a valid pick is one.
- `s.run(label, fn, ...)` records an exception instead of raising it: in the real app `CombatAppQt.run` installs `sys.excepthook` so a click's exception is printed and shown in the status line instead of ending the app. An exception inside `with Session(...)` that the probe itself raised is recorded too, and the block ends.

### Invariants `check()` tests

HP is an int in 0..max_hp; temp HP ≥ 0; no condition twice; death saves 0..3; spell and pact slots left ≥ 0; feature uses spent ≥ 0; no two combatants share a name; in combat, the turn index is in range, everyone in the order is in the fight, and the round is ≥ 1. These are the floor, not the oracle: what *should* have happened comes from the rules (below).

### Round-trip checks

- `undo_roundtrip(fn)`: the state (each combatant's public keys, the order, the round, the turn) and the log's **events** (`round_N` lists) must be what they were. The log's snapshot keys (`combatants`, `player_fight_state`, the order, the turn) are rewritten on every write, so they aren't compared. An operation that changed the fight but left no Undo step is a finding too.
- `replay_matches()`: builds a second `CombatAppQt` on the same log and party log, as the next launch would ("continue the fight"), and diffs its state. `position` is ignored by default. A key missing on one side and empty (`{}`, `[]`, 0, None) on the other is no difference.

## The oracles: decide what *should* happen

1. **The rules.** Find the glossary terms an outcome turns on with `python .claude/skills/rules-glossary/glossary_terms.py <file>` (or read `SourceTexts/RulesGlossary/<Section>/<Entry>.md` directly) and compare clause by clause: Concentration (DC 10 or half the damage, max 30; Incapacitated ends it), conditions and what they do to other creatures' rolls, Temporary Hit Points (don't stack, are lost first), healing caps at the Hit Point maximum, 0 HP (Unconscious, death saves, a hit at 0 is a failed save, a critical two), Resistance after a save's halving, Bloodied. Quote the clause in the finding.
2. **The content's own text.** A spell's or feature's `combat_effects()` (the `combat-effects` skill) and its description say what using it does. The picker fills the form from them; the outcome must match.
3. **The code's own contract.** Docstrings in `Combat/CombatUIQt/` state intended behaviour ("Undoing it puts that state back and deletes exactly those lines"). Disagreeing with one is a finding; a house rule documented there isn't.

## Combinations worth trying

The code joins features in these places, and that is where they break:

| Area | Try |
|---|---|
| Undo | every mutating step through `undo_roundtrip`; Undo across a round boundary; Undo of a cast that added conditions, Concentrating and a spent slot |
| Reopen | `replay_matches()` mid-turn, after an Undo, after a summon, after End Encounter (continuing an ended fight reopens it) |
| 0 HP | damage past 0 on a player (death saves) and a monster (dead); heal from 0; damage while dying; Revive; Unconscious + Prone together |
| Concentration | damage to a concentrating caster (the save, the DC), a second concentration spell, Incapacitated |
| Durations | conditions "until the end of the target's next turn" across Next Turn, Previous, Undo; repeat saves |
| Resources | casting with no slot left (answer "yes" and "no"), feature uses at 0, pact slots, legendary actions and resistances |
| Temp HP and defenses | temp HP then damage, resistance + vulnerability, immunity to a condition the effect gives |
| Summons, Wild Shape | summon, damage the summon to 0, the owner drops or leaves; Wild Shape HP running out; the card menus |
| Removing / adding | remove the combatant whose turn it is; Add Combatant mid-fight; two with the same name |
| Areas | the battle map's area targeting (`_start_area_targeting`), kept areas, moving into one |

Pick scenarios whose party has what you test (`explore.py scenarios`; a party's builds are in its campaign's `encounters.py`). Mix sources: players and monsters reach different code (`_is_player`).

## Gotchas

- **Never touch real campaign data.** The harness writes only to a temp folder (`CombatLogs/` and `PlayerLogs/party.json` under it). Don't pass a campaign's log paths, don't run `RunCombatSimulator.py`, and run `git status --short` after a session: it must show nothing new.
- **Players need the party log.** Without a party log (`Session(player_log=False)`), a reopened fight restarts the players from their sheets (HP, conditions), so `replay_matches()` would flag that. Keep the default.
- **Change state only through UI methods.** `replay_matches()` rebuilds the fight from what was logged, so a probe's own `char["hp"] = ...` shows up as a wrong (even negative) HP in the reopened fight. Damage with `ui.damage_input` + `_apply_damage`, or Use / Cast.
- **Exact dice:** `random.randint` rolls everything. `D20 = [15]; random.randint = lambda a, b: D20[0] if b == 20 else b` gives a fixed d20 and maximum damage dice; set `D20[0] = 2` to make saves fail.
- **The Damage field** takes several types as `30 slashing+10 fire` (`30 slashing 10 fire` is refused as not an amount).
- **A Use / Cast spends the Action only when the picked row has an action cost**, which a monster casting from the full spell list may not have. To test what a spent Action does, log it with `ui._add_action_use("Action", char, ask=False)`.
- `picks()` lists every spell for every creature, so any monster can cast Hold Person, Bless or Faerie Fire for a concentration test.
- **Use / Cast needs a target** (or an aimed area); without one it returns with "Nothing applied". `picks`/`use_cast` select one.
- **Offscreen vs native.** Offscreen (the default) has no window manager: the harness drops its "This plugin does not support ..." lines. Windows-only messages (setGeometry, DPI) appear only with `--native` / `native=True`, which flashes real windows on the user's screen: use it only when checking for those.
- **Qt prints some warnings once per process** (the first popup with a px font, for example). Probe one variant per process (`python probe.py variant`) when you bisect a warning.
- Don't combine this with `.claude/skills/run-apps/screenshot.py` in one process: its `qt_app()` patches `QDialog.exec` again and dialogs get skipped instead of shown.
- **Exit code 127 with nothing printed** at the very end of a probe that opened many windows is Qt dying in interpreter teardown, after your output: the report is still valid. `sweep` ends with `os._exit` for this reason; end a long probe with `sys.stdout.flush(); os._exit(0)` if it matters.
- A sweep picks thousands of rows (about 2 minutes per scenario); run long ones in the background.
