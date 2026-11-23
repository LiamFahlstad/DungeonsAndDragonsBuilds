# Plan: clean up and restructure the combat UI

Goal: the combat UI (`Combat/CombatUIQt/`, about 24,700 lines in 40 files)
grew one feature at a time, mostly through
[combat-effects-plan.md](combat-effects-plan.md) and
[combat-arena-plan.md](combat-arena-plan.md). Nobody has gone back over it
as a whole yet. This plan does that, without changing what the GM sees or
what a fight does:

1. **Rules away from widgets.** What a fight *does* (damage, conditions,
   turns, casting, undo, the log) lives in a Qt-free core that can be tested
   without a window. The window only shows the fight and turns clicks into
   calls.
2. **No function you can't read in one sitting.** The 1,580-line Use / Cast
   dialog and the 680-line `_build_window` become classes with named parts.
3. **Types where there are dicts and strings now.** A combatant has a
   declared shape, the phase is an enum, and pyright catches a mistyped key.
4. **One way to do each thing:** one way to refresh the views after an
   operation, ask the GM a question, style a widget and build a button.

Written 2026-11-21. Steps 0 to 2 built 2026-11-22.

**What never changes during this plan:** the behaviour, the widget
`objectName`s (the tests, the golden widget dumps and the `combat-ui-explore`
harness find widgets by them), the encounter and player log formats (unless
Q1 says otherwise), and every test passing at the end of each step.

## How to use this document

This is a living plan, like the two combat plans. Whoever works on a step
updates it **in the same change** as the code:

- **Status**: tick the step, with the date and the Revisions it made.
- **Revisions**: when the code shows a better way than the plan, do the
  better thing and write down what changed and why (R1, R2, ...).
- **Open questions**: Q1, Q2, ..., never reused, each with a *Suggestion*,
  which is what gets built if nobody says otherwise. Answered ones move to
  **Decisions** (numbered, never renumbered, each saying who decided and
  when).
- **Discovered issues**: bugs found while moving code go into
  `Notes/discovered-issues.md` through the `discovered-issues` skill's
  script, and their ids go here. **A refactor step does not fix them**: it
  moves the bug along unchanged, so a test diff never mixes "moved" with
  "fixed". Fix them in a step of their own.
- **The other two plans** describe where code lives ("The dialog
  (`conditions_mixin.py`)", "How it fits the code that's there"). A step
  that moves that code updates their file references in the same change.

**Keep the overhead low (the user, 2026-11-10).** Run the combat UI tests
and the few others a step touches, not the character-sheet tests. Steps 3,
5 and 7 are large enough to also warrant a `code-reviewer` pass and a
`combat-ui-explore` sweep before they're called done.

## Status

| Step | What | Size | State |
|---|---|---|---|
| 0 | Safety net: a structure test that ratchets the numbers below down, fix the one pyright error | S | **Done** 2026-11-22 (R1, R2): `tests/test_combat_ui_structure.py`; pyright clean on `Combat/`; the UI tests take about 77 s (1,498 tests, xdist) |
| 1 | Hygiene: enums for phase and action types, styles into QSS, dead code out | S-M | **Done** 2026-11-22: 1.1, 1.2, 1.6 (R3, R5); 1.3 (R6, R7): inline styles 98 → 23; 1.4 moved to 5.4, 1.5 dropped (R4) |
| 2 | A typed combatant (`Combatant` TypedDict) | M | **Done** 2026-11-22, revised (R8): the schema and a key test; annotating signatures moved to step 5 |
| 3 | The Use / Cast dialog as a class, its form-to-effects logic Qt-free | L | 3a **done** 2026-11-22 (R9): `use_cast/form.py`, dialog 1,580 → 1,440 lines; 3b **done** 2026-11-22 (R10): `_UseCastDialog`, `run()` 616 lines + 44 methods; 3c's move **done** (R11): `use_cast/dialog.py`, `conditions_mixin.py` 3,500 → 1,674 lines; 3c's split **done**, revised (R12): `run()` is 14 lines calling 10 builder methods, the longest 126; 3d **done** (R13): `do_apply` 146 → 50 lines over Qt-free `read_amount`, `check_applicable` and `build_effect`; reviewed (R14): no behaviour change; **step 3 done** |
| 4 | The window built from panels, shortcuts as a table | M | **Done** 2026-11-23 (R15, R16): `_build_window` 680 → 13 lines over 12 builders (the longest 111); the shortcuts a table (`shortcuts.py`) checked against KEYBOARD_SHORTCUTS.md |
| 5 | The Qt-free fight core (`Combat/Fight/`), one mixin at a time | XL | 5.1 **done** 2026-11-23 (R17): seven Qt-free modules moved to `Combat/Fight/`; 5.5's guard test in place; **5.2 (`Fight` holds the state) next** |
| 6 | One refresh path after every GM operation | M | Not started |
| 7 | Mixins into composed views and one module per dialog; `CombatWindowState` gone | L | Not started |
| 8 | Docs, agents and skills point at the new layout | S | Not started |

Steps 0-2 are cheap and safe and make the later ones easier, so do them
first. Steps 3 and 4 are independent of each other. Step 6 needs step 5's
results. Step 7 comes last.

## 1. Findings (2026-11-21)

Measured with an AST walk over `Combat/CombatUIQt/`. Step 0 turns these
numbers into a test.

### 1a. Size

| What | Now |
|---|---|
| Lines in `Combat/CombatUIQt/` | 24,740 in 40 files |
| Largest files | `conditions_mixin.py` 3,585; `arena_mixin.py` 2,114; `effect_options.py` 2,071; `dialogs_mixin.py` 1,393; `turn_panel_mixin.py` 1,190; `damage_mixin.py` 1,185 |
| Functions over 100 lines | 14 (over 50 lines: 64, of 1,225) |
| Longest functions | `_show_custom_condition_dialog` **1,580** lines with 53 nested functions; `_build_window` 680; `_apply_effect_to_targets` 236; `_show_statistics` 177; `_described_option` 161; `do_apply` (nested in the dialog) 137; `_show_player_link_dialog` 134; `_apply_replay_action` 133 |
| Mixins making up `CombatAppQt` | 19 |
| Method stubs in `state.py` (`CombatWindowState`) | 206 |

### 1b. Design

1. **Rules and widgets are mixed in the same methods.** For example,
   `DamageMixin._deal_typed_damage` works out criticals, asks `_before_hit`,
   deals damage and fires `_after_attack` triggers, and in between it
   clears `self.damage_input`, rebuilds cards and sets the status line.
   `damage_mixin.py` imports no Qt but is still part of the window. So
   every rules test needs a full `CombatAppQt` with its window built (61
   test files call `make_ui`), and a second front end (the player link, the
   map on the Player Screen, arena Later item 11) can't reuse the rules.
2. **Rules inside rendering.** `_refresh_views` starts by landing fliers
   who can't stay aloft (`_land_fallers`), so a view refresh changes the
   fight. `UndoPoint.restore` writes to `damage_input` and
   `attack_roll_input`.
3. **The mixin web.** 19 mixins call each other freely. `state.py` declares
   206 stubs so pyright can check those calls. That works, but every new
   method has to be added in two places, and nothing marks which mixin owns
   which state. The one pyright error right now is a missing stub
   (`_give_effect_conditions`, `damage_mixin.py:582`, from work in
   progress).
4. **Refreshing is manual.** There are 35 `_rebuild_card` calls, 27
   `_refresh_views` calls and 39 `_refresh_*` / `_update_*` / `_rebuild_*`
   functions. Every operation has to remember what to redraw, and tests
   call `_refresh_views` by hand 112 times. `@undoable` already wraps every
   GM operation (52 of them), which makes it the natural single place to
   save, redraw and publish afterwards.
5. **A combatant is an untyped dict**, with about 45 keys read directly
   (`name` 191 times, `stats` 63, `hp` 43, ...) and 236 `.get("...")`
   reads. A `"_"` prefix means the key is fixed for the fight and isn't
   undone. Some registries are keyed by `id(char)`, and many checks rely on
   identity (`any(t is c for c in ...)`). Undo's in-place refill is what
   keeps that identity working.
6. **Stringly-typed state.** `phase` is set to or compared with
   `"COMBAT"`, `"PARTY"` and `"INITIATIVE"` in 54 places. Action types are string literals
   next to `ACTION_ECONOMY_TYPES`.
7. **Styling is spread out.** There are about 100 `setStyleSheet(...)`
   calls outside `styles.py` (`cards_mixin.py` 25, `dialogs_mixin.py` 22,
   `turns_mixin.py` 11, ...).
8. **Old-log compatibility shims** sit in the replay code ("Older logs
   stored the condition name as a plain string", `upgrade_old_keys`). Each
   one is small, but they add up and nothing records which log version
   needs them.

### 1c. What's already good (keep it)

- `Combat/Effects/` and `Combat/Arena/` (6,400 lines) are Qt-free and
  imported by the UI, never the other way round. They're the model for
  step 5.
- 14 UI modules import no Qt at all (`amounts`, `attack_rolls`,
  `effect_options`, `saves`, `monster_actions`, `stats`, `public_log`,
  `undo`, `player_server`, ...). Some of them are really core code that
  sits in the wrong folder.
- The UI is well tested: about 20,000 lines of `test_combat_ui_*` tests,
  golden widget dumps (`tests/snapshots/combat_ui_*.json`), the picker-row
  goldens, and the `combat-ui-explore` harness. That safety net is what
  makes this plan affordable.
- Undo as a captured snapshot plus the log lines it wrote is simple and
  correct. Keep the design and only move it.
- pyright is clean apart from the one missing stub.

### 1d. The constraint: tests reach into the app

Tests use 215 different private members of the app, 2,833 times in all
(`_advance_turn` 175, `_show_custom_condition_dialog` 165,
`_select_character` 161, `_apply_custom_effect` 137, ...), and
`monkeypatch` 1,129 times. Rewriting those tests is out of scope. The
plan is built so they keep passing (Decision 2).

## 2. Target design

A sketch: the plan updates itself as the steps teach us.

```
Combat/
  Effects/, Arena/            unchanged: Qt-free rules pieces
  Fight/                      NEW, Qt-free: one fight's state and what the GM can do to it
    combatant.py              Combatant TypedDict, key docs (step 2)
    fight.py                  Fight: combatants, initiative order, turn, round,
                              phase (enum), arena settings, pending prompts
    undo.py                   UndoPoint / gm_operation (moved from CombatUIQt)
    log.py                    encounter log write / read / replay (from logging_mixin)
    damage.py conditions.py turns.py casting.py summons.py
    wild_shape.py rests.py    the operations (from the *_mixin files)
    picker/                   effect_options, saves, amounts, attack_rolls,
                              monster_actions (moved, Qt-free already)
    asker.py                  the Asker protocol: how the core asks the GM something
  CombatUIQt/                 Qt only
    app.py                    CombatAppQt: owns a Fight and the views; GM
                              operations stay as thin methods (Decision 2)
    window/                   control_panel.py, turn_column.py, menus.py, shortcuts.py
    use_cast/                 dialog.py + one widget per section, form.py
    cards/  turn_panel/  arena/ (arena_view, map_painter)  player/ (view, server, public log)
    dialogs/                  one module per dialog (statistics, player link, add combatant, rules, ...)
    styles.py                 all the QSS
```

**The core's API.** An operation takes the fight and plain arguments, and
returns what happened:

```python
@dataclass
class StepResult:
    changed: list[Combatant]          # whose cards to redraw
    status: str = ""                  # the status line
    prompts: list[Firing | AreaPrompt] = field(default_factory=list)  # turn-column buttons
```

When the core needs an answer in the middle of an operation (an ASK
trigger, "out of resources, use it anyway?", a tie-break), it asks through
an `Asker` it was given. The window implements that with dialogs, and core
tests use a scripted one instead of monkeypatching `QMessageBox`.

**One seam after every operation.** `@undoable` becomes `@gm_operation`.
After the outermost operation it records the undo point (as today), saves
the fight state, redraws whatever the results changed and publishes to the
Player Screen and player link. Operations stop calling `_rebuild_card` and
`_refresh_views` themselves.

**Layering.** `tests/test_layering.py` gets a `"Combat.CombatUIQt"` layer
above `"combat"`. Nothing in `Combat.Fight`, `Combat.Effects` or
`Combat.Arena` may import PyQt6 or `Combat.CombatUIQt`.

## 3. Steps

Each step is one or more commits, each behaviour-preserving and green. A
step that moves code moves it unchanged first, in its own commit, and
improves it in a later commit, so each diff is either a move or an edit,
never both.

### Step 0: safety net *(tests only)*

- `tests/test_combat_ui_structure.py`, in the same ratchet style as
  `test_layering.py`: an allowlist of today's functions over 150 lines in
  `Combat/` with their current length, which may only shrink (a listed
  function that's already short enough fails too, so the list can't go
  stale); the number of `CombatWindowState` stubs, which may only fall;
  `setStyleSheet` calls outside `styles.py`, which may only fall.
- Fix the missing `_give_effect_conditions` stub once the work in progress
  in `damage_mixin.py` is committed. It isn't ours to fix while someone
  else is editing that file.
- Time the combat UI tests once (`./run_tests.sh -q tests/test_combat_ui_*`)
  and write the number here, so later steps can tell if they slowed them
  down.

**Done when:** the structure test passes on HEAD and fails when a long
function grows.

### Step 1: hygiene *(mechanical, small commits)*

1. `Phase` as a `str` enum (`PARTY`, `INITIATIVE`, `COMBAT`) in
   `Combat/Definitions.py`. Its values stay the same strings, so the logs
   don't change.
2. The action economy types as an enum next to it, used for
   `ACTION_ECONOMY_TYPES` and the literals.
3. Inline `setStyleSheet` calls become `objectName`s or dynamic properties
   styled in `styles.py`. The golden widget dumps must stay byte-identical,
   apart from the style text they record, if they record it.
4. *(Moved to step 5.4, R4.)* One helper for the GM's questions.
5. *(Dropped, R4.)* A button factory.
6. **Done** (R5). Dead code: stubs in `state.py` that no mixin implements,
   methods nothing calls.

**Done when:** the UI tests and widget dumps pass, and the Step 0 counters
are lower.

### Step 2: a typed combatant *(types only, no runtime change)* — done, revised (R8)

- **Built:** `Combat/Fight/combatant.py`. `Combatant` is a TypedDict with
  all 110 keys, each typed and commented, including the `"_"` keys and
  what the prefix means for undo and saving. The 13 keys both builders
  always set are `Required`. The 110 are the union of a static scan and a
  runtime probe of every combatant the 1,589 UI tests build.
- **Built:** `tests/test_combatant_keys.py` checks four things against it:
  both builders' output (all 154 builds and all 513 catalog monsters, with
  the required keys present), `PLAYER_FIGHT_KEYS`, the key constants, and
  every literal key the combat code uses on a combatant (852 sites, found
  by the names it's given). A mistyped key (`char["hp_max"]`) fails the
  test (checked by planting one).
- **Moved to step 5:** replacing `dict` with `Combatant` in signatures.
  Each module switches as it moves into `Combat/Fight/`.

Whether it becomes an attrs class later is Q2.

### Step 3: the Use / Cast dialog *(the biggest single win)*

`_show_custom_condition_dialog` (`conditions_mixin.py:1870`, 1,580 lines,
53 nested functions sharing state through closures) is where the effects
plan and the arena plan both keep adding things. In sub-steps:

- **3a. Pull out what's already Qt-free.** `rolls_in`, `typed_totals`,
  `typed_attacks`, `typed_extras`, `typed_maximum`, `nth`, `repeated` and
  the module-level helpers (`_picked_effect`, `hit_rider`,
  `_option_duration`, ...) move into `use_cast/form.py` unchanged, with
  their inputs as arguments instead of closed-over widgets.
- **3b. Closure to class.** `UseCastDialog(QDialog)` in `use_cast/dialog.py`:
  closed-over variables become attributes, nested functions become
  methods. A mechanical move, with each `nonlocal` and closed-over name
  checked. `_show_custom_condition_dialog(pick, cost, kept_area)` stays as
  the entry point and builds and runs it (165 test uses).
- **3c. A class per section:** the targets row, the pick list and search,
  the roll section (save / attack), the amount section (damage / healing,
  Times, typed rolls), push, duration and condition, the preview. Each owns
  its widgets and tells the dialog when it changed. The dialog holds a
  `UseCastForm` dataclass (the pick, targets, typed values) that the
  sections read and write.
- **3d. Apply as a function.** `do_apply`'s logic becomes
  `build_effects(form, fight) -> list[CustomEffect]` in `form.py`, tested
  without Qt. The dialog's Apply only collects the form, calls it and
  hands the result to `_apply_custom_effects`.
- Then `_apply_effect_to_targets` (236 lines) is split into its phases
  (cost, rolls, damage, conditions, triggers, summary).

**Done when:** no function in `use_cast/` is over 80 lines, every
`objectName` is unchanged, `test_combat_ui_custom_effect.py`,
`test_combat_ui_effect_steps.py`, `test_picker_rows.py` and the rest of the
UI tests pass, and a `combat-ui-explore` sweep reports nothing new. Update
the effects plan's "The dialog" section.

### Step 4: the window from panels

`_build_window` (680 lines) becomes `window/control_panel.py`,
`window/turn_column.py`, `window/menus.py` and `window/shortcuts.py`, each
a function or a small `QWidget` subclass that returns its widgets.
Shortcuts become a table (key, action, when it's active), and a test checks
the table against `Combat/CombatUIQt/KEYBOARD_SHORTCUTS.md` so the doc
can't drift.
`_show_statistics` (177 lines) and `_show_player_link_dialog` (134) get
the same treatment in step 7.

**Done when:** the widget dumps are byte-identical. Update the arena plan's
"How it fits the code that's there".

### Step 5: the Qt-free fight core *(the design change)*

Strangler-style, one area per commit, the tests green after each:

1. **Move what's already Qt-free.** `undo.py`, `amounts.py`,
   `attack_rolls.py`, `effect_options.py`, `saves.py`, `monster_actions.py`,
   `stats.py` and `public_log.py` go into `Combat/Fight/` (the picker files
   into `Combat/Fight/picker/`). Leave re-export shims in their old places
   for one step if that's easier, then delete them.
2. **`Fight` holds the state** that `CombatAppQt.__init__` holds today
   (combatants, order, turn, round, phase, arena settings, history,
   pending prompts). The app keeps properties with the old names that
   forward to `self.fight`, so tests and mixins keep working.
3. **The operations, one mixin at a time**, in this order: damage
   (already Qt-import-free), conditions (`_add_condition_to`,
   `_remove_condition_from`, badges, durations), turns (`_advance_turn`,
   `_start_combat`, end-of-turn saves), casting and features
   (`_apply_cast_spell`, `_apply_feature`, `_apply_effect_to_targets` after
   step 3), summons, wild shape, rests, and last the log
   (`_write_log`, `_load_log_from_path`, `_replay_player_log`). Each mixin
   method becomes `result = damage.deal(self.fight, ...)` plus showing the
   result. The rules code moves and the widget lines stay behind.
4. **The Asker** replaces direct `QMessageBox` and trigger pop-up calls
   from rules code.
5. **Layering test** (section 2) added as soon as `Combat/Fight/` exists,
   with no allowlist.
6. **`Combatant` in signatures** (from step 2, R8). As a module moves into
   `Combat/Fight/`, its combatant parameters, returns and attributes say
   `Combatant` instead of `dict`, and so do the callers it touches. A
   TypedDict isn't assignable to or from a plain `dict`, so the change
   has to follow the call chain. That's why it rides along with the move,
   where every call site is touched anyway.
   - **Optional keys:** read `char["x"]` on an optional key only where the
     key is sure to be there (`"x" in char`, or the code that set it),
     else use `char.get("x")`.
   - **Key constants:** `Final`, so pyright reads them as their literal key.

New rules tests are written against `Combat/Fight/` without a
`QApplication`. Old tests move only when they're touched anyway (Q4).

**Done when:** no PyQt6 import under `Combat/Fight/`, the mixins hold only
widget code, and all UI tests pass unchanged. This is the step that lets
arena Later item 11 (the map on the Player Screen and player link) and
[player-web-view-plan.md](player-web-view-plan.md) read the fight without
the Qt window.

### Step 6: one refresh path

- `@undoable` becomes `@gm_operation`: after the outermost operation it
  saves the fight state, redraws the cards in the results' `changed` (or
  all of them, if that's simpler and fast enough), refreshes the turn
  column and the arena, and publishes to the player view and server.
- `_land_fallers` moves out of `_refresh_views` into the operations that
  can make a flier fall (moving, a condition, a speed change).
- `UndoPoint.restore` stops writing widgets. The window puts the Damage
  and Attack roll fields back from the restored state in its own redraw.
- Remove the manual `_rebuild_card` / `_refresh_views` calls the seam now
  covers. Tests that call `_refresh_views` by hand still work, since it's
  still there and is now just redundant.

**Done when:** an operation's code contains no redraw calls, and the
`_rebuild_card` count is near zero outside the seam.

### Step 7: composed views, one module per dialog

- With the rules gone (step 5), the remaining mixins are view code. Cards,
  the turn panel, the initiative widget, the arena and the map painter
  become classes the window owns (`self.cards = CardsView(...)`). Each one
  reads the `Fight` and calls back into the app's GM operations.
- `dialogs_mixin.py` (1,393 lines) and `encounters_mixin.py` split into
  `dialogs/<name>.py`, one per dialog.
- `CombatWindowState`'s stubs drop to zero and the class is deleted. The
  app's private method names that tests use stay as one-line delegates
  (Decision 2), listed in one block in `app.py`.

**Done when:** `state.py` is gone, and `CombatAppQt` is under about 500
lines, mostly delegates and wiring.

### Step 8: docs, agents and skills

Update `Combat/CHEATSHEET.md`, `HOWTO.md`, the `combat-simulator` and
`combat-ui-tester` agent prompts, the `combat-ui-explore` and `map-painter`
skills (their code indexes point at file:line), the agent index, and both
combat plans' file references. Then record the final numbers in Findings.

## 4. Coordination with the other plans

- **Where they stand.** The effects plan is down to content (Phase 4.3,
  spells and features: content files, not the UI), Phase 5 (sheet chips:
  `Presentation/`) and open questions Q63 and Q66. The arena plan's steps
  1-28 are done, and what's left is Later items 11-14. So feature work
  has paused at a good moment for this plan.
- **No two changes to the same file at once.** A refactor step and a
  feature step never edit the same file in parallel. Before a step starts,
  say in its Status row which files it moves. Content work (effects plan
  4.3) can continue throughout, since it doesn't touch `Combat/CombatUIQt/`.
- **Order against the arena's Later items.** Do items 11 (map on the Player
  Screen and player link) and 13 (doors, jumps) after step 5, since they
  read the fight from outside the window. Items 12 (areas count height)
  and 14 (distance rules) are in `Combat/Arena/` and can go any time.
- **New dialog features** (anything the effects plan adds to Use / Cast)
  wait for step 3 to finish, or go in before it starts. Never during it.

## Decisions

1. **Behaviour-preserving only.** No step changes what the GM sees or what
   a fight does. Bugs found are logged and fixed separately. (In the plan,
   for the user to overrule.)
2. **The app's operation methods are the test surface.** The 215 private
   names tests use stay on `CombatAppQt` (as delegates once their code has
   moved), so the 2,833 test uses keep working. They're cleaned up only if
   Q4 says so. (In the plan, for the user to overrule.)
3. **`objectName`s are a contract.** The tests, the widget dumps and the
   explore harness find widgets by them, so a refactor never renames one.
   (In the plan.) An objectName that nothing finds a widget by, used only
   as a style class, may change (R7).

## Open questions

- **Q1. Old logs.** Should every old encounter and player log keep replaying
  forever, or can a log version and a one-off migration script upgrade
  existing logs so the compatibility shims can go? Blocks nothing; it
  decides how much of step 5's log code can be simplified. *Suggestion:* a
  `"version"` field and `Combat/Tools/migrate_logs.py`, run once over
  `Combat/PlayerLogs/` and the campaigns' encounter logs, then delete the
  shims. The player logs are long-lived campaign data, so back them up
  first.
- **Q2. TypedDict or a class?** A `Combatant` attrs class would give
  methods and real attributes, but touches every `char["..."]` in the repo
  and undo's dict copying. *Suggestion:* TypedDict only (step 2). Revisit
  after step 5, when most access goes through the core.
- **Q3. How far to go with mixins?** *Suggestion:* step 7 as written:
  compose the views, which have clear boundaries. If a leftover mixin is
  small and only glue, keeping it is fine.
- **Q4. Moving old tests.** *Suggestion:* don't migrate in bulk. New rules
  tests go against `Combat/Fight/`, and an old UI test moves only when it's
  edited for another reason.
- **Q5. Who does the work?** *Suggestion:* the `combat-simulator` agent
  (opus) per step, one step at a time (no parallel agents on these files),
  and a `code-reviewer` pass after steps 3, 5 and 7. Steps 0-2 are small
  enough to do in the main session.

## Revisions

- **R1 (step 0, 2026-11-22).** The long-function rule skips `Combat/Tools/`
  (hand-run report scripts, outside this plan) as well as
  `Combat/Monsters/`. Its budgets are caps, not exact numbers: a function
  that shrinks doesn't fail the test, so feature work isn't blocked by
  every line it removes. A function that drops under 150 lines must come
  off the list. The stub budget is 207, not 206: fixing the pyright error
  added the missing stub. The test caught its first growth the same day
  (a two-line comment in the Use / Cast dialog), which moved to a
  docstring.
- **R2 (step 0).** The pyright error was more than a missing stub.
  `PendingAttack.rider` (`Combat/Effects/triggers.py`) is typed `object`
  because `CustomEffect` lives in the UI's `saves.py`, which
  `Combat/Effects` may not import. `damage_mixin.py` narrows it with
  `isinstance` for now. Step 5.1 moves `saves.py` down, and then the field
  can name its type.
- **R3 (step 1.2).** The action types were defined in four places (the
  app's `ACTION_ECONOMY_TYPES`, `effect_options.FEATURE_ACTION_COSTS`,
  `triggers.REACTION`, `lasting.ACTION` / `BONUS_ACTION`). They're now one
  `ActionCost` StrEnum in `Combat/Definitions.py`, beside `Phase`. Both
  enums keep the old strings as values, so logs, `action_uses` keys and
  tests comparing with `"COMBAT"` are unchanged. **Lesson for later steps:
  Qt's `findData` matches item data by type**, so an enum member and its
  string don't find each other. Give Qt `str(member)` as item data (the
  Use / Cast dialog's `actionCost` box does).
- **R4 (step 1).** 1.4, one helper for the GM's questions, is folded into
  step 5.4. There are only four yes/no questions, and step 5's `Asker`
  replaces them anyway. 1.5, a button factory, is dropped. Of the 88
  `QPushButton(...)`s, 34 take no setup at all and no sequence repeats
  more than 12 times, so a factory would be cleverness for nothing.
- **R5 (step 1.6).** A scan found no dead mixin methods and no stub without
  an implementation. The only unused UI-side code was `Summons.spec_for`,
  which `source_for` had replaced, and it's deleted.
  `Combat/Combatants.py`'s unused `SaberToothedTiger` is encounter
  content, not UI code, and stays.
- **R6 (step 1.3, before starting it).** The golden widget dumps record
  each widget's `styleSheet()` and dynamic properties, so moving inline
  styles into QSS changes `tests/snapshots/combat_ui_cards.json` and
  `combat_ui_more_info.json`. 1.3 is therefore a reviewed output change:
  regenerate them, read the diff (style text replaced by a property, and
  nothing else), and compare a `run-apps` screenshot of the window from
  before and after.
- **R7 (step 1.3, done).** What was built, and what it taught:
  - **ObjectNames as style classes, not a new `role` property.**
    `styles.py` already styles by objectName (`#secondary`, `#divider`,
    `#sectionHeader`), so the 75 static inline styles became objectNames
    (`muted`, `caption`, `goldHeading`, `panelTitle`, `cardResource`, ...)
    with their rules in one block at the end of the QSS. Being last, they
    win any specificity tie. The 23 left inline are computed per state (HP
    bar and badge colours, the damage type's colour, a rolled initiative,
    the player link button) or are a menu's own QSS, which guards it
    against a card's inline style cascading into it.
  - **Decision 3 gets a narrow exception:** three card labels were named
    `secondary` and overrode most of it inline. They're now `cardTempHp`
    and `caption`. Nothing looks them up (no test, no explore harness), so
    an objectName used *only* as a style class may change. One that a test
    or the harness finds a widget by still may not.
  - **The 12 dialogs no longer set the whole QSS on themselves.** The app
    sets it once (`run()`, and `rest.py`'s own entry point). The tests'
    `QApplication` (`tests/_combat_ui.py`) now sets it too, as `run()`
    does. Without that, the Settings dialog laid out in Qt's default font
    and failed `test_the_settings_dialog_fits_the_smallest_window` (620px
    > 600).
  - **The golden dumps changed in exactly two ways:** each inline `style`
    became its `object_name`, and `fixed_height` now appears where the
    app's QSS gives one (HP bars 16px, dividers). Before, a test window had
    no stylesheet, and a dialog only got its own copy lazily, after the
    dump was taken.
  - **Verified pixel-identical** in the real app's styling. The main
    window (initiative, a fight with a summon, the party view) and 25
    dialogs (More Info for all 13 combatants, Add Combatant, Settings,
    Player Link, Statistics, Rules, a rule popup, Load Encounter,
    Encounter Log, Map Painter, Short Rest, the tie-break, the party view)
    were screenshotted before and after and diffed pixel by pixel. The
    only difference was a log timestamp in Load Encounter.

- **R8 (step 2, 2026-11-22).** Annotating every signature with `Combatant`
  at once was tried and measured, then reverted. A sweep switched 703
  annotations (combatant-like parameters, `list[dict]`s, the window's
  attributes), and pyright then reported 922 errors:
  - **443** were reads of optional keys (`char["x"]`). Nearly all were
    keys both builders always set, now `Required`.
  - **About 400** were plain `dict` values flowing in from places the
    sweep couldn't see: dataclass fields like `PendingAttack.attacker`,
    helpers with parameters named `a`/`b`, and locals inferred from
    untyped sources. Each needs its source found by hand, over several
    rounds.
  - **Only 3** were undefined keys, and all three were the sweep's own
    false positives (dicts that aren't combatants).

  So the full switch would have been a diff of a thousand-plus lines that
  found no bug, while step 5 touches each of those signatures anyway. Step
  2 became the schema plus a test that does the type checker's key check
  (any literal key used on a combatant must be declared). The switch to
  `Combatant` in signatures is step 5's item 6. Two smaller lessons:
  - **Partial adoption doesn't work:** a TypedDict isn't assignable to or
    from `dict`, so returning `Combatant` from the builders alone breaks
    every caller.
  - **The runtime probe found three keys the static scan missed**
    (`known_resistances`, `known_immunities`, `shield_off`), so a schema
    should come from both.

- **R9 (step 3a, 2026-11-22).** The readers of rolls typed at the table
  (`typed_totals`, `typed_attacks`, `typed_extras`, `typed_maximum`,
  `rolls_in`), `nth` and the Times copies (`repeated`) are now
  `Combat/CombatUIQt/use_cast/form.py`, Qt-free and unit tested
  (`tests/test_use_cast_form.py`).
  - **Errors as exceptions:** in the dialog, each reader wrote its problem
    into the error label and returned None. Now it raises `FormError`
    with the same text, and the dialog's one-line wrappers show it
    through `read_or_say(read, say)`. Same text, same None.
  - **Plain arguments:** the readers take the boxes' text, not the boxes,
    and `repeated` takes the Damage text, type and amount kind it used to
    read from the widgets.
  - **What's left for 3b:** `do_apply` still builds the effect in the
    closure. Its reading moves out in 3d, once 3b has made the closure a
    class.
  - **How to do 3b safely:** the closure has no `nonlocal` (its shared
    state is dicts and lists), so turning it into a class is a rename.
    Every name a nested function reads from the outer function becomes
    `self.<name>`, and the app's `self` becomes `self.app`. Python's
    `symtable` lists each nested scope's free variables exactly, so the
    rename can be a scripted codemod. A text replace would also hit inner
    parameters that shadow outer names.

- **R10 (step 3b, 2026-11-22).** The closure is now the class
  `_UseCastDialog`, still in `conditions_mixin.py`. Moving it to
  `use_cast/dialog.py` with its imports is 3c's first commit, so that
  commit is a pure move.
  - **Done by a codemod** (a symtable-driven rename, as R9 planned). Of the
    function's 190 locals, 121 became attributes: each one a nested
    function or lambda reads, plus the 45 nested functions themselves,
    which became methods. The other 69 (widgets only the dialog's setup
    uses) stay locals of `run()`. 802 references were renamed, and the
    app's `self` became `self.app`.
  - **`_show_custom_condition_dialog`** keeps its signature and docstring
    and runs `_UseCastDialog(self).run(pick, cost, kept_area)`. Its 165
    test uses work unchanged.
  - **Comprehensions stay as they are:** a name read only by a
    comprehension in the dialog's setup stays a local, because a
    comprehension runs at once and a closure doesn't. The one `:=` (in a
    generator expression) relies on that.
  - **Result:** pyright clean with no hand fixes. 1,829 combat UI tests
    pass. The `combat-ui-explore` sweep over every campaign reports 0
    problems.
  - **Two test lists followed the new names:** `test_roll_sites`
    (`show_typed_type` is a method now) and the structure test (`run()`
    616 lines, `do_apply` 146).

- **R11 (step 3c's move, 2026-11-22).** The class is now `UseCastDialog`
  in `Combat/CombatUIQt/use_cast/dialog.py`. 41 module-level helpers and
  constants moved with it: everything it uses, found by following each
  helper's own uses. `conditions_mixin.py` imports back the three it
  still needs (`_SUMMARY_COLOR`, `_ignores_cover`, `_where_from`). It never
  imports the other way, so there is no cycle.
  - **App type and stubs:** the class types its app as `CombatWindowState`,
    not `ConditionsMixin`, which keeps the module free of the mixin. So the
    4 `ConditionsMixin` methods it calls got stubs (`_apply_custom_effect`,
    `_apply_custom_effects`, `_custom_condition_suggestions`,
    `_effect_picker`), and the stub budget went 207 → 211. Step 7 deletes
    the stubs with the class.
  - **Scans that missed subfolders:** `test_roll_sites` and the
    structure test's inline-style count only scanned the top of
    `CombatUIQt/`, so they would have missed `use_cast/`. Both now scan
    subfolders, and a file there is keyed by its path (`use_cast/dialog.py`).
  - **One test moved its import:** `test_combat_ui_arena_ranges` imports
    `_attack_text` from the dialog module now.
  - **Checks:** 2,009 tests pass and the sweep reports 0 problems.
  - **Logged, not fixed:** typing the touched test files showed a pyright
    error in `test_roll_sites.py` that was already there (DI-112).

- **R12 (step 3c's split, 2026-11-22).** `run()` (616 lines) is now 14
  lines that set the three parameters and call one builder per section:
  `_prepare`, `_build_targets`, `_build_picker`, `_build_roll_section`
  (126 lines), `_build_amount_section`, `_build_condition_section`,
  `_build_cost_section` (97), `_build_footer`, `_connect` and `_start`.
  - **Methods, not a class per section.** The plan said a class per
    section. But the form's readers cut across every section (`do_apply`
    reads all of them, and `show_preview` most), so section classes would
    have been held together by cross-references. Builder methods on the
    one dialog give the same readable shape without that.
  - **Same codemod approach** (symtable). A local of `run()` became an
    attribute only if a section reads it before assigning it, meaning it
    needs another section's value. That was 6 widgets (`outer`, `body`,
    `roll_col`, `effect_col`, `name_edit`, `cancel_btn`), plus the three
    parameters. The other 61 stay local to their section.
  - **One hand fix:** `name_edit`'s not-None assert now narrows a local
    before the attribute is set. An assert in one method doesn't narrow
    the attribute in another.
  - **Checks:** 1,851 tests pass. The sweep over every campaign reports 0
    problems. `run()` is off the long-function list.

- **R13 (step 3d, 2026-11-22).** Apply is now three Qt-free steps in
  `use_cast/form.py`, over a `FormValues` record of plain values that
  `UseCastDialog._read_form()` (48 lines) reads from the boxes:
  1. `read_amount` reads the Damage box.
  2. `check_applicable` checks there's a target and something to do.
  3. `build_effect` builds the `CustomEffect`.

  `do_apply` (146 → 50 lines) runs them, the typed-roll readers between
  steps 2 and 3, and then applies the effect. Errors are shown through
  `read_or_say`, as in 3a.
  - **Dice are rolled once, in the same order.** Reading the Damage box
    rolls its dice, so `read_amount` runs once and its `Amount` is passed
    on, never read again. `build_effect` rolls a hit's critical damage
    after it, as `do_apply` did.
  - **`check_applicable` returns True** rather than None. `read_or_say`
    returns None for an error, so a check that returned nothing couldn't
    be told apart from one that failed.
  - **Tests:** `tests/test_use_cast_form.py` has 8 new tests that build
    effects without Qt: targets, something to do, a spell pick, condition
    names, a typed total, an attack's critical damage and Shield boxes,
    and Temporary Hit Points. The dialog's 1,860 UI tests pass unchanged
    and the sweep is clean.

- **R14 (step 3's review, 2026-11-22).** The `code-reviewer` checked steps
  3a to 3d against 08c8fbaa and found **no behaviour change**.
  - **How it checked:** it compared ASTs after undoing the renames, and
    used symtable to look for renames that went wrong or were missed.
  - **One stale test:** 3a moved the dialog's regexes, but
    `tests/test_text_readers.py` still listed them under
    `conditions_mixin.py`, and it had failed since 2ab7c0c2 because the
    per-step test lists didn't include it. Fixed with the 3d commit: the
    entries point at `use_cast/form.py`. The full suite passes (12,060).
  - **Verification** now ends each step with a full-suite run.
  - **Step 3 is done.**

- **R15 (step 4's split, 2026-11-23).** `_build_window` (680 lines) is
  now 13 lines that call 12 builder methods on the window mixin:
  `_build_frame`, `_build_selection_labels`, `_build_turn_tracker`,
  `_build_damage_controls`, `_build_healing_controls`, `_build_d20_roll`,
  `_build_more_controls` (111 lines, the longest), `_build_action_buttons`,
  `_build_turn_buttons`, `_build_view_buttons`, `_finish_window` and
  `_build_shortcuts`.
  - **Arguments, not attributes.** Unlike 3c, the builders here are
    methods of the app itself, so `self.` attributes would have put
    temporaries like `left_col` on the app. A section takes what earlier
    ones made as typed parameters and returns what later ones need. Only 5
    locals crossed sections (`root_layout`, `panel`, `panel_layout`,
    `columns_layout`, `left_col`).
  - **Done by a script with a guard:** it refused to run if a nested
    function read a local that a later section sets.
  - **Not new modules yet.** The plan said `window/control_panel.py` and
    so on. The builders stay on the mixin for now, so the window doesn't
    have to be passed around. Step 7, which turns the mixins into
    composed views, is where they move.
  - **Checks:** the main window's screenshots are pixel-identical, and the
    full suite passes.
- **R16 (step 4's shortcuts, 2026-11-23).** The shortcuts are a table,
  `SHORTCUTS` in `Combat/CombatUIQt/shortcuts.py` (Qt-free): one row per
  action with its keys, the app method it calls, the method's arguments
  and whether it's combo-sensitive. `_build_shortcuts` is 31 lines that
  make them.
  - **`ACTION_ECONOMY_SHORTCUTS` folded into the table.** It was only
    used to build the A/B/R shortcuts, so it's gone from `app.py` and
    `state.py`.
  - **Attributes:** the 23 one-per-shortcut attributes nothing read are
    gone. The five that the window or tests read stay as typed attributes
    (`_next_turn_shortcuts`, `_previous_turn_shortcuts`,
    `_spell_slot_shortcuts`, `_more_info_shortcut`,
    `_map_painter_shortcut`), and so does `_combo_sensitive_shortcuts`.
  - **Same behaviour:** the shortcuts are made in the same order, and
    each key gives the same key sequence as before (checked: "Esc" ==
    Key_Escape, and so on). N and the Right arrow, and the like, now share
    a row, as they share a line in the doc.
  - **`tests/test_shortcuts_doc.py`** checks the table against
    KEYBOARD_SHORTCUTS.md both ways. Every action has a documented key,
    and every documented key exists. It catches either kind of mistake
    (checked by adding an undocumented shortcut, and by dropping Ctrl+M).

- **R17 (step 5.1, 2026-11-23).** Seven modules moved from
  `Combat/CombatUIQt/` to `Combat/Fight/` with `git mv`, unchanged:
  `amounts`, `attack_rolls`, `monster_actions`, `saves`, `effect_options`,
  `stats` and `public_log`. None of them imported Qt or anything in the
  UI, as a dependency walk showed. A script pointed everything at their
  new place: 88 files, including the UI's relative imports, tests, the
  two tools, the combat-effects skill's script, the code-lookup agent's
  prompt and the notes. Then one hand fix: a multi-name import whose other
  names stay in the UI.
  - **Not moved:**
    - `undo.py` still writes the Damage and Attack roll fields as it
      restores, so it moves after step 6 has taken that out.
    - `player_server.py`, `styles.py` and `shortcuts.py` are the window's.
  - **No shims.** Every importer was updated in the same change.
    `Notes/discovered-issues.md` keeps the old paths in its entries, since
    only its script edits it.
  - **Tests that follow file paths:** `test_roll_sites` scans
    `Combat/Fight/` too (its keys didn't change: they're paths within the
    scanned folder), and `test_text_readers` follows the new paths.
  - **5.5's guard is in** (`tests/test_combat_ui_structure.py`): nothing
    in `Combat/Fight`, `Combat/Effects` or `Combat/Arena` imports PyQt6 or
    `Combat.CombatUIQt`. There's no allowlist, because nothing breaks it.
  - **Checks:** the full suite passes (12,064) and pyright is clean.

## Discovered issues

- DI-112: pyright error in `tests/test_roll_sites.py:135`, which was
  already there (found in step 3c).

## Verification (every step)

- `./run_tests.sh -q tests/test_combat_ui_* tests/test_picker_rows.py
  tests/test_layering.py tests/test_combat_ui_structure.py` plus the core
  tests of the area the step moved (`test_active_effects.py`,
  `test_arena_*`, `test_*_triggers.py`, ...).
- At the end of each step (not each commit), the full suite runs once:
  `./run_tests.sh -q`. The list above missed `tests/test_text_readers.py`,
  which tracks every regex by file. Moving a `re.compile` constant breaks
  it, and it was broken from 3a until step 3's review (R14).
- `./typecheck.sh Combat` is clean.
- Widget dumps (`tests/snapshots/combat_ui_*.json`) unchanged. If one
  changes, read the diff and say why before regenerating.
- Steps 3, 5 and 7: a `combat-ui-explore` sweep reports nothing new, and the
  window is opened once with the `run-apps` skill's screenshot.
- `./format.sh` only on the files the step changed (it reformats the whole
  repo otherwise).
