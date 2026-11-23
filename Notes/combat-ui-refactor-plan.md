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
5. **No file you have to scroll through to find a part of it.** A file over
   about 1,000 lines that holds several separate jobs is split into one
   module per job (step 9).
6. **A folder says what's in it, and a name means one thing.** `Combat/`'s
   loose modules go into packages named for their job, two modules never
   share a name, and runtime code leaves `Tools/` (step 10).

Written 2026-11-21. Steps 0 to 2 built 2026-11-22. Step 9 (splitting large
files) and step 10 (folders and names) added 2026-11-23.

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
| 5 | The Qt-free fight core (`Combat/Fight/`), one mixin at a time | XL | 5.1 **done** 2026-11-23 (R17): seven Qt-free modules moved to `Combat/Fight/`; 5.5's guard test in place; 5.2 **done** (R18): `Fight` holds the fight's state; 5.3 started (R19, R20): damage's defenses and arithmetic in `Combat/Fight/damage.py`, health (death state, healing, Temporary Hit Points, Death Saving Throws) in `Combat/Fight/health.py`; the map's questions (distance, sight, cover, range, Critical Hits within 5 feet) are `Fight` methods (R21); an attack roll's check is `Combat/Fight/attacks.py` (R22); gaining and losing a condition is `Combat/Fight/conditions.py` (R23); the turn order is `Fight`'s (R24); casting's slots, recipients and timers are `Combat/Fight/spells.py` (R25); joining and leaving the turn order are `Fight`'s, summons' questions and carry-over `Combat/Fight/summons.py` (R26); Wild Shape's uses and badge `Combat/Fight/wild_shape.py` (R27); a short rest's regains and Hit Dice `Combat/Fight/rests.py` (R28); saving, loading and replaying the fight `Combat/Fight/log.py` (R29); 5.3's areas are each started; what's left of them (features, triggers, the cascades a condition sets off, `_log_event`) waits for 5.4's `Asker` and step 6; 5.4 started (R30): the `Asker` asks "out of resources, go ahead anyway?", and the checks are `Combat/Fight/resources.py`; the core logs through a `Logger` (Decision 4, R32), first spending an Action, a feature use or a slot; what the players know is `Combat/Fight/player_knowledge.py` (R33); **5.4 continues with conditions and their cascades (R33), then the Use / Cast apply path and triggers** |
| 6 | One refresh path after every GM operation | M | Not started |
| 7 | Mixins into composed views and one module per dialog; `CombatWindowState` gone | L | Not started |
| 8 | Docs, agents and skills point at the new layout | S | Not started |
| 9 | Large files split into one module per job, with a file-size ratchet | M | Not started. 9.0 (the ratchet) and 9a (Qt-free files) can start now; 9b (UI files) after step 7 |
| 10 | Folders and names: `Combat/`'s loose modules into packages, clashing names apart, runtime code out of `Tools/`, stray files gone, `CombatUIQt/` in subfolders | M | Not started. 10.0 (the rule), 10a (stray files), 10b (the loose modules) and 10c (clashing names) can start now; 10d (UI subfolders) rides along with steps 7 and 9b |

Steps 0-2 are cheap and safe and make the later ones easier, so do them
first. Steps 3 and 4 are independent of each other. Step 6 needs step 5's
results. Step 7 comes last of the restructuring steps. Steps 9's and 10's
parts fit in between (see each step), and step 8 runs after the last part
of both, so the docs are updated once.

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
| Files over 1,000 lines in `Combat/` (2026-11-23, after steps 3 and 5.1) | 10: `arena_mixin.py` 2,108; `Fight/effect_options.py` 2,072; `use_cast/dialog.py` 1,908; `conditions_mixin.py` 1,646; `dialogs_mixin.py` 1,380; `turn_panel_mixin.py` 1,191; `Effects/triggers.py` 1,143; `Effects/modifiers.py` 1,120; `arena_view.py` 1,005; `damage_mixin.py` 1,001. Another 6 are over 800 (`state.py` 967, `map_painter.py` 929, `Arena/arena.py` 833, `cards_mixin.py` 830, `window_mixin.py` 803), and `logging_mixin.py` (791) is just under |

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
  Definitions.py, CHEATSHEET.md   the only loose files left (step 10)
  Effects/, Arena/            unchanged: Qt-free rules pieces
  Encounters/                 setting a fight up: campaigns, encounter configs, difficulty (step 10)
  Logs/                       the encounter and player log files on disk (step 10)
  Data/                       monsters_raw.json, the Rules dialog's reference (step 10)
  Campaigns/, Monsters/, Tools/   content, generated stat blocks, hand-run scripts
  Fight/                      NEW, Qt-free: one fight's state and what the GM can do to it
    combatant.py              Combatant TypedDict, key docs (step 2)
    new_combatant.py          a Combatant from a character or stat block (step 10)
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
    cards/  turn_column/  arena/ (arena_view, map_painter)  player/ (view, server, page)
    dialogs/                  one module per dialog (statistics, player link, add combatant, rules, ...)
    widgets/                  widgets several dialogs share (tree filter, effect dialog widgets)
    styles.py                 all the QSS
```

Step 10 has the file-by-file version of the parts it adds.

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
Runs after the last parts of steps 9 and 10, so the new module names and
folders are final. (Code that imports a moved module, a skill's script
included, is fixed in the move's own commit; step 8 is the prose.)

### Step 9: one module per job *(moves only)*

Steps 3 to 7 shorten functions and pull rules out of the window, but they
leave some files long: a mixin with five jobs, or a Qt-free module that
grew a section per kind of pick. A long file isn't wrong in itself. One
that mixes jobs is, because finding the part you want means scrolling, and
two people editing different jobs in it collide. This step splits those
files along the seams they already have.

**When a file gets split.** It's over the limit (Q6: 1,000 lines) *and*
it holds more than one job, meaning groups of functions that call each
other and barely touch the rest. One cohesive class that's long because
its job is long (`ArenaView`'s drawing, `UseCastDialog`, see R12) stays
whole and goes on the allowlist with its reason. Splitting a class across
files would need more mixins, which step 7 is removing.

**How a split is done** (each split is one commit, a pure move):

- **The old module keeps the entry points** most importers use, and
  imports the pieces from the new modules, so the new modules form a
  layer under it and there's no import cycle. Importers of a moved name
  are pointed at its new home in the same commit. No re-export shims (as
  in R17), since a shim hides which module owns a name.
- **Names don't change.** A private helper that now crosses a module
  keeps its `_`. Making it public is a later edit commit, if anyone wants
  it.
- **`git mv` the old file to the biggest piece** when the old name stops
  fitting, so `git log --follow` keeps the history of most of the code.
- **What follows file paths has to move with the code:**
  - `monkeypatch.setattr(module, "name", ...)` patches the name where it's
    *looked up*. A test that patched a helper in the old module and now
    patches nothing still passes and silently tests less. So grep the
    tests for every moved name and point each patch at the module that
    calls it.
  - `test_roll_sites`, `test_text_readers` (every `re.compile` by file),
    the structure test's `LONG_FUNCTIONS` (keyed by path), and the
    `map-painter` and `combat-effects` skills' scripts and indexes.
  - The other two plans' file references.
- **Checks:** the moved code is byte-identical apart from imports (compare
  each moved function's AST with the old one, as R14 did), pyright is
  clean, and the full suite passes.

**9.0. The ratchet first.** `tests/test_combat_ui_structure.py` gets a
file-size rule in the same style as the long-function one: no file under
`Combat/` (skipping `Monsters/` and `Tools/`, as R1 does) over the limit,
except an allowlist of today's long files with their length as a cap. A
listed file that drops under the limit must come off the list. Each entry
says either "split in 9a/9b" or why it stays whole.

**9a. The Qt-free files** (any time, but not while a step 5 slice is
moving code into or out of the same file; do the slice first, then split
what's left):

| File | Split into (a sketch; the code's own seams decide) |
|---|---|
| `Fight/effect_options.py` 2,072 | The target design's `Fight/picker/` package: `effect_text.py` (reading an effect from its text, upcasting, cantrip levels), `spell_options.py` (slots, casting cost, spell rows), `monster_options.py` (monster actions and spells), `weapon_options.py` (weapons, Shove, Masteries), `feature_options.py` (feature rows and uses), `described.py` (`_described_option` and the effect amounts), `trigger_rows.py` (trigger and badge rows, regained uses). `effect_options.py` keeps `effect_options`, the standard actions, the area and range rows. `amounts`, `attack_rolls`, `saves` and `monster_actions` join the package then, as section 2 sketched |
| `Effects/modifiers.py` 1,120 | `modifiers.py` keeps held conditions and `modifiers_on`; `roll_plans.py` (save and attack plans, distance and sight), `hits.py` (hit notes, extras and `hit_plan`), `armor_class.py`, `stats_in_use.py` (Hit Point maximum, Speed, size) and `defenses.py` (Resistance, Immunity, Vulnerability) |
| `Effects/triggers.py` 1,143 | `triggers.py` keeps the firing functions; `outcomes.py` (the nine `*Outcome` records), `trigger_rows.py` (`TriggerRow`, `TriggerMode`, `TriggerChoice`, `Firing`), `hit_firings.py` (`HitFiring`, `PendingAttack`, `still_hits`, `reduced_damage`) |
| `Arena/arena.py` 833 | Under the limit: leave it |

`Combat/Effects/` belongs to the effects plan as much as this one, so its
splits wait until no effects-plan step has those files open, and that plan's
file references are updated in the same commit.

**9b. The UI files** (after step 7). Steps 5 and 7 take most of the
mixins apart: their rules move to `Combat/Fight/` and their views become
classes. So don't split a mixin before then, or its code moves twice. What
can move earlier is the module-level code that sits *beside* a mixin and
never touches it:

- `dialogs_mixin.py`: the More Info panel's 700 lines of builders
  (`_InfoPanel`, `_add_*`, the chance tables) become `dialogs/more_info.py`
  now. They're the first module of step 7's `dialogs/` folder.
- `arena_mixin.py`: the move and area text helpers at its end (`move_line`,
  `forced_move_line`, `area_reading`, `hazards_under`, ...) become
  `arena/texts.py`.
- `use_cast/dialog.py`: its 240 lines of text and tooltip helpers
  (`_attack_text`, `_attack_tooltip`, `_save_text`, `_damage_preview`, ...)
  become `use_cast/texts.py`. The dialog class itself stays whole (R12).

After step 7, measure again and split whatever is still over the limit
with more than one job. The likely ones, from today's outlines:
`arena_mixin.py`'s view code (the speed bar, the area bar and targeting,
the area panel, and moving combatants are four separate jobs),
`conditions_mixin.py` (applying an effect vs. conditions, badges and
visibility), and `turn_panel_mixin.py`. `state.py` (967) is deleted by
step 7 and needs nothing.

**Done when:** the structure test's file allowlist holds only files kept
whole on purpose, each with its reason, and the full suite passes.

### Step 10: folders and names *(moves and renames only)*

Step 9 splits files that are too long. This step puts each file where a
reader would look for it and gives it a name that means one thing. What's
there today (2026-11-23):

- **15 modules loose in `Combat/`**, beside 7 packages. Apart from
  `Definitions.py` they do four jobs:
  - setting up a campaign's encounters: `Campaign.py`, `Scenario.py`,
    `Scenarios.py`, `EncounterConfig.py`, `EncounterDifficulty.py`,
    `PartyAllies.py`;
  - the log files on disk: `EncounterLogs.py`, `PlayerLog.py`, `LogFiles.py`;
  - making and changing a combatant: `PlayerCombatant.py`, `Summons.py`,
    `WildShape.py`;
  - odds and ends: `Rules.py` (the Rules dialog's reference text, with
    `rules.json`) and `Combatants.py` (ten old hand-made stat blocks: 40
    test files and two campaigns' encounters use them).
- **Names that mean two things.**
  - `Combat/Summons.py` and `Combat/Fight/summons.py`, and
    `Combat/WildShape.py` and `Combat/Fight/wild_shape.py`, are two modules
    each on the same subject.
  - `asker.py` and `resources.py` are in both `Fight/` and `CombatUIQt/`.
    That clash already broke `test_roll_sites`' keys once (R31).
  - `Scenario.py` and `Scenarios.py` differ by one letter (the second is
    the registry of campaigns).
  - `Combat/Rules.py` sounds like `Core/Rules.py` (the rules constants
    CLAUDE.md means), and `Combat/Combatants.py` has the name of
    `Model/Creatures/Combatants.py`.
  - `CombatUIQt/rest.py` and `CombatUIQt/rests_mixin.py` sit beside
    `Fight/rests.py`.
- **Runtime code in `Tools/`.** `Tools/monster_effect_text.py` reads a
  stat block's text into the CombatEffects the picker offers.
  `Fight/monster_actions.py` imports it at run time, and so do 8 test
  files. `Tools/` is for scripts run by hand.
- **Two cases in one folder.** `Arena/`, `Effects/` and `Fight/` name their
  modules in snake_case. The top level is PascalCase, and each campaign
  folder has both (`Campaign.py` and `Players.py` beside `encounters.py`).
- **Files nothing reads.**
  - `Combat/PlayerLogs/main_party.json`: one session from 2026-10-22, from
    before each campaign had its own `PlayerLogs/`. It's tracked only
    because `.gitignore` covers just the campaigns' folders.
  - `Combat/rules.txt`: the raw text `rules.json` was written from.
  - `Combat/FEATURE_GAPS.md`: an audit from 2026-08-22 that nothing links
    to.
  - `Tools/migrate_monster_*.py`: three one-time migrations, all run.
- **`CombatUIQt/` is flat:** 37 files. Section 2 sketched subfolders, and
  nothing uses them yet (step 4's `shortcuts.py` went in flat).

**The conventions** (Q8):

- Folders are PascalCase, like the rest of the repo. Modules inside a
  package are snake_case, like `Arena/`, `Effects/` and `Fight/`. A module
  is renamed for its case only when it moves anyway.
- No two modules under `Combat/` share a name, ignoring case and `_`
  (`Summons.py` and `summons.py` clash), apart from `__init__.py` and the
  files every campaign folder has by design (`campaign.py`,
  `encounters.py`).
- `Combat/` itself holds packages, `Definitions.py` (the combat enums: 53
  importers, the counterpart of `Core/Definitions.py`) and `CHEATSHEET.md`.
- Nothing outside `Tools/` imports `Combat.Tools`.
- **Class and function names don't change**, as in step 9 (`CombatScenario`
  stays `CombatScenario` in `scenario.py`). Only modules and folders do.

**The layout** (a sketch: check each module's importers before moving it):

| Now | Goes to | Why |
|---|---|---|
| `Campaign.py`, `Scenario.py`, `Scenarios.py`, `EncounterConfig.py`, `EncounterDifficulty.py`, `PartyAllies.py` | `Combat/Encounters/`: `campaign.py`, `scenario.py`, `campaigns.py` (the registry, was `Scenarios.py`), `config.py`, `difficulty.py`, `party_allies.py` | Setting up what a fight is. `Campaigns/` stays content only: the campaign folders and `ENCOUNTERS.md` |
| `Combatants.py` | `Combat/Encounters/basic_stat_blocks.py` | Not into `Monsters/`: importing anything there runs its generated `__init__.py`, which loads every monster, and 40 test files import these |
| `EncounterLogs.py`, `PlayerLog.py`, `LogFiles.py` | `Combat/Logs/`: `encounter_log.py`, `player_log.py`, `files.py` | The log files on disk. `Fight/log.py` (replaying a fight) and `Fight/public_log.py` (what players see) stay with the fight |
| `PlayerCombatant.py` | `Fight/new_combatant.py` | It makes a `Combatant`, beside `combatant.py`, which declares one |
| `Summons.py`, `WildShape.py` | merged into `Fight/summons.py` (about 680 lines) and `Fight/wild_shape.py` (about 320) | One module per subject (Q10) |
| `Rules.py`, `rules.json` | `Combat/Data/rules_reference.py` and `rules_reference.json` | No clash with `Core/Rules.py`; the loader stays next to the one file it reads |
| `monsters_raw.json` | `Combat/Data/monsters_raw.json` | Data beside data. `scrape_monsters.py` writes it and `generate_monsters.py` reads it |
| `Tools/monster_effect_text.py` | `Fight/monster_effect_text.py`, and into `Fight/picker/` with `monster_actions.py` when 9a makes that | Runtime code |
| `PlayerLogs/main_party.json`, `Tools/migrate_monster_*.py` | deleted (Q9 for the migrations) | Nothing reads them; git keeps their history |
| `rules.txt`, `FEATURE_GAPS.md` | `SourceTexts/` and `Notes/combat-feature-gaps.md` (Q12) | Where the repo keeps source texts and audits |
| each campaign's `Campaign.py`, `Players.py` | `campaign.py`, `players.py` | One case per folder. `ENCOUNTERS.md`'s "add a campaign" says so |
| `CombatUIQt/asker.py`, `CombatUIQt/resources.py` | `window_asker.py`, `resources_mixin.py` | Named for what's in them (`WindowAsker`, `ResourcesMixin`), and no clash with `Fight/` |
| `CombatUIQt/rest.py` | split in step 7: `short_rest_dialog` into `dialogs/short_rest.py`, the command line's `apply_long_rest` and `run_short_rest` into `rest_commands.py` | It's two things today, and neither is `rests_mixin.py` or `Fight/rests.py` |

**The UI's subfolders** (10d). Every file moves once. A mixin doesn't move,
because step 7 replaces it with a view class, and that class is made in its
folder. 9b's new modules (`dialogs/more_info.py`, `arena/texts.py`,
`use_cast/texts.py`) are made in theirs. Files no step touches move by
themselves, between slices:

| Folder | Now (any time) | When steps 7 and 9b make them |
|---|---|---|
| `player/` | `player_view.py`, `player_server.py`, `player_page.html` (move its `!` line in `.gitignore` with it) | |
| `arena/` | `arena_view.py`, `map_painter.py` | `arena_mixin.py`'s views, `texts.py` |
| `turn_column/` | `log_feed.py`, `trigger_prompt.py` | the turn panel, turns and timer views |
| `window/` | `shortcuts.py`, `window_asker.py` | the panels `window_mixin.py` builds |
| `widgets/` | `tree_filter.py`, `effect_dialog_widgets.py` | |
| `dialogs/` | | one module per dialog, `short_rest.py` |
| `cards/` | | the cards view |

Left at the top of `CombatUIQt/`: `app.py`, `styles.py`, `settings.py`,
`rest_commands.py`, `KEYBOARD_SHORTCUTS.md`, `undo.py` (step 6 decides
where it goes) and `state.py` (step 7 deletes it). Section 2 called the
turn column `turn_panel/`; it's `turn_column/` here because that's what
the GM sees and what the code's docstrings call it.

**How a move is done** (one commit per package or per row, a pure move):

- `git mv`, so `git log --follow` keeps the history. On Windows a rename
  that only changes case (`Campaign.py` to `campaign.py`) needs two
  `git mv`s through a temporary name, since the filesystem ignores case.
- Every importer is pointed at the new path in the same commit. No
  re-export shims (as in R17 and step 9). The importers are not only
  `Combat/`: tests, `Run*.py`, the campaigns' `encounters.py` and the
  skills' scripts (`.claude/skills/*/*.py`) import these modules too.
- **What follows file paths moves with them**, the same list as step 9:
  `monkeypatch.setattr(module, ...)` targets (none use a string path
  today), `test_roll_sites`, `test_text_readers`, the structure test's
  lists, and `tests/test_layering.py`'s layer map (a new package gets its
  layer, or inherits `"Combat"`). Also `pyrightconfig.json` and
  `typecheck.sh` (they name a `Tools/` file), `.gitignore`, and
  `.claude/settings.json` (its allowed `Combat/Tools/...` commands).
- The logs on disk don't store module paths (checked 2026-11-23), so old
  encounter and player logs still open.
- `Combat/Monsters/` is left alone. Its `__init__.py` and `CR_*/` are
  generated, and their place is in `generate_monsters.py`, the skills and
  CLAUDE.md.
- `Tools/`'s hand-run scripts stay where they are (`monster_score.py`'s
  path is in CLAUDE.md, four skills, the `monster-balancer` agent and the
  permissions).

**10.0. The rule first.** `tests/test_combat_ui_structure.py` gets three
checks, in the same ratchet style as the others: the files loose in
`Combat/` (an allowlist of today's, which may only shrink); module names
that clash (an allowlist of today's clashes, which may only shrink); and no
`Combat.Tools` import outside `Tools/` (an allowlist with
`monster_effect_text`'s importers).

**The order.**

- **10.0** and **10a** (the deletions and stray files) any time. They're
  tiny.
- **10b** (the loose modules, one package per commit) any time, but never
  during a step 5 slice or a step 9a split that edits the same modules.
  `Summons.py` and `WildShape.py` go after any slice still moving code out
  of their mixins.
- **10c** (the clashing names in `CombatUIQt/` and the campaign folders'
  case) any time.
- **10d** (the UI's subfolders): the "now" column any time between slices,
  the rest as steps 7 and 9b make each module.

**Done when:** `Combat/` holds only packages, `Definitions.py` and
`CHEATSHEET.md`; the three allowlists of 10.0 are empty; the full suite and
pyright pass; and `RunCombatSimulator.py` opens an encounter and a player
log from the command line, `Combat/Tools/prepare_encounters.py` checks a
campaign and `monster_score.py` scores a monster (they find their files by
path, which tests don't cover).

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
- **File splits (step 9) never run beside other work on the same file.**
  A split touches every importer of the moved names, so it goes in alone,
  between slices, with nobody else's uncommitted changes in those files
  (check `git status` first). The same goes for step 10's moves, which
  also touch `Combat/Campaigns/` content and the skills' scripts.

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
4. **The core logs through a `Logger`** (the user, 2026-11-23). Like the
   `Asker`, a Protocol in `Combat/Fight/logger.py` that the rules are given:
   the window's forwards each line to `_log_event`, and tests keep them in a
   `RecordingLogger`. Chosen over returning the lines in a result (the
   `StepResult` of section 2), which would split every operation that logs,
   asks and logs again around each question, and over doing step 6 first.
   Line order and Undo stay as they are (R32).

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
- **Q6. The file-size limit.** What length makes a file a candidate for
  step 9? *Suggestion:* 1,000 lines, as the ratchet's limit, with the
  "more than one job" test deciding whether a file over it is split or
  allowlisted. 800 would also catch `map_painter.py`, `cards_mixin.py`
  and `window_mixin.py`, which each do one job today.
- **Q7. Packages or flat siblings?** Should a split file become a package
  (`Fight/picker/`, `Effects/modifiers/`) or sibling modules beside it
  (`Effects/armor_class.py`)? *Suggestion:* a package where section 2
  already sketched one (`Fight/picker/`, `dialogs/`, `arena/`), flat
  siblings elsewhere. Turning `modifiers.py` into a package would change
  the import path of every one of its importers for no gain.
- **Q8. Step 10's conventions and package names.** PascalCase folders,
  snake_case modules inside them, and the new packages `Encounters/`,
  `Logs/` and `Data/`? *Suggestion:* yes, as step 10 lists them.
  `Encounters/` rather than putting the code in `Campaigns/`, so that
  folder stays content a GM edits.
- **Q9. The one-time migration scripts** (`Tools/migrate_monster_*.py`,
  476 lines, all run). *Suggestion:* delete them. git keeps them, and
  `generate_monsters.py` already writes the format they migrated to.
- **Q10. Merge or rename?** `Summons.py` into `Fight/summons.py` and
  `WildShape.py` into `Fight/wild_shape.py`, or keep two modules each with
  telling names? *Suggestion:* merge, since both results stay under the
  1,000 lines of Q6. If a merge would make an import cycle, keep two:
  `Fight/summon_options.py` and `Fight/wild_shape_forms.py`.
- **Q11. Rename `CombatUIQt/`** to something shorter, such as
  `Combat/Window/`? *Suggestion:* no. 36 test files, 17 agent and skill
  files and HOWTO.md name it, and the name is odd but not ambiguous.
- **Q12. `FEATURE_GAPS.md` and `rules.txt`.** *Suggestion:* move them as
  step 10's table says, unchanged. Whether `FEATURE_GAPS.md`'s open items
  go into `Notes/discovered-issues.md` is a separate triage, not part of a
  move.

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

- **R18 (step 5.2, 2026-11-23).** `Combat/Fight/fight.py`'s `Fight` (a
  dataclass) holds `characters`, `initiative_order`, `current_turn_idx`,
  `round_number`, `phase` and `arena_settings`. The window holds one,
  `CombatAppQt.fight`.
  - **Forwarding properties.** `CombatWindowState` turns the six names
    into properties that read and write the `Fight`, so the mixins, undo,
    the log code and the tests, about 2,800 references in all, didn't
    change.
  - **Not moved yet:**
    - The undo history, because `UndoPoint` is still in the UI (R17).
    - The turn column's prompts, which are what the window shows.
    - The logs, which come with the log code in 5.3's last area.
  - **The stub budget now counts stubs only** (a lone
    `raise NotImplementedError`), so the forwarding properties don't
    count. It stays 211.
  - **Tests:** `tests/test_fight.py` (new) checks a `Fight` without Qt and
    that the window's attributes are its. The full suite passes (12,064 +
    3) and pyright is clean.

- **R19 (step 5.3, damage's first slice, 2026-11-23).** The rules of
  damage on one combatant are now `Combat/Fight/damage.py`, as functions
  of combatant dicts:
  - `damage_type_modifier`: Immunity, Resistance and Vulnerability, with
    the outcome the log names.
  - `damage_after_defenses`: a save's half, then the defenses.
  - `take_damage`: Temporary Hit Points first, Hit Points no lower than a
    floor, the knockout, and both sides' statistics. It returns a
    `DamageTaken`.

  `DamageMixin` keeps what the window does with them: the log line and its
  value, Bloodied (which logs through the conditions code), the players'
  notes and the card.
  - **What remains a wrapper:** `_damage_type_modifier` stays as a
    one-line wrapper because tests call it. `_damage_after_defenses`
    is gone; its one caller calls the function.
  - **The way the rest of 5.3 goes**, worked out on this slice:
    1. Move the arithmetic and state changes into a function of combatants
       or of the `Fight`. Test it without Qt, with expected values from
       the rules.
    2. Keep logging, prompts and drawing in the mixin.
    3. Move the logging once the log code itself moves (5.3's last area).
  - **Tests:** `tests/test_fight_damage.py` (8 tests without Qt).
    `damage_mixin.py` is 101 lines shorter. The full suite passes (12,075).

- **R20 (step 5.3, damage's second slice, 2026-11-23).** A combatant's
  health is now `Combat/Fight/health.py`:
  - `death_state`, with the `ALIVE` / `DYING` / `STABLE` / `DEAD` it
    returns (the same strings as before);
  - `regain_hit_points` (no more than the maximum, and someone at 0 comes
    to, with their saves reset) and `give_temp_hp` (they don't stack);
  - `revive`;
  - `fail_death_save`, `succeed_death_save` and `damage_at_zero_hp` (one
    failure, two from a Critical Hit, death from damage at least the Hit
    Point maximum, and Stable ended).

  `DamageMixin`'s `_heal_target`, `_revive`, `_damage_at_zero_hp`, the two
  death-save buttons and `_give_temp_hp` call them, and keep their log
  lines, conditions and cards. `CardsMixin._char_death_state` is a
  one-line wrapper, because tests call it 26 times.
  - **Tests:** `tests/test_fight_health.py` (8 tests without Qt, expected
    values from the Rules Glossary). The mixins are 68 lines shorter. The
    full suite passes (12,083).

- **R21 (step 5.3, attack rolls' first slice, 2026-11-23).** The battle
  map's questions the rules ask are `Fight` methods:
  - `map_settings` (the painted map with kept walls);
  - `distance_ft`, `sees`, `map_cover` and `covered`;
  - `range_check`, `cover_warning` and `critical_against`.

  Each reads only the fight's state, and each answers "not known" before
  the map is in use (arena plan Decision 29). The window's
  `_attacker_distance_ft`, `_sees`, `_map_cover`, `_covered`,
  `_range_check`, `_cover_warning`, `_critical_against` and `_map_settings`
  are one-line wrappers. They have about 40 callers across the mixins and
  tests, which switch to `self.fight` as their own code moves.
  - **Tests:** 3 more in `tests/test_fight.py`: before the map is in use,
    distances once it is, and Paralyzed's Critical Hit within 5 feet. The
    full suite passes (12,086).

- **R22 (step 5.3, attack rolls' second slice, 2026-11-23).** An attack
  roll's check is `Combat/Fight/attacks.py`'s `check_attack(fight, target,
  roll, source, notes, ignores_cover)`. It returns an `AttackCheck`: the
  hit (None with no AC), the target as the roll read it, its AC and bonus,
  the Critical Hit, and the notes.
  - **`_resolve_attack_roll` keeps** noting the roll for the players
    (`note_attack_roll` needs `player_view`'s sight, and that module is
    Qt), the log line, using up one-roll badges, and its status text. It's
    9 lines shorter.
  - **Order:** the hit's notes and Critical Hit used to be worked out after
    the noting. They're worked out first now, which gives the same result:
    they read the target's conditions and distance, never what the noting
    writes.
  - **Tests:** `tests/test_fight_attacks.py` (5 tests without Qt:
    equals-AC hits, naturals, no AC, Paralyzed within 5 feet, a miss's
    notes). The full suite passes (12,091).
  - **What's left of the attack path in the window** is how a hit is dealt
    (`_deal_typed_damage`) and its triggers (`_before_hit`,
    `_after_attack`). They go with the triggers' prompts, which ask the GM
    something and so need step 5.4's `Asker`.

- **R23 (step 5.3, conditions' first slice, 2026-11-23).** What gaining or
  losing a condition does to the combatant itself is
  `Combat/Fight/conditions.py`:
  - `gain_condition`: the grappler named, the condition added once, and
    both sides' statistics (not for a badge beside its conditions). It
    returns whether it's new.
  - `lose_condition`: the condition, its lasting effect, a Dash's movement
    and the grappler removed. It returns a `LostCondition` with the Hit
    Point maximum before, and the linked badges to follow up on.
  - **What stays in the mixin, and why:** the cascades a condition sets
    off (Concentration broken, a Wild Shape form left, grapples ended,
    Dodge lost, Prone after Unconscious, linked badges) each log through
    another mixin. So they stay in `_add_condition_to` and
    `_remove_condition_from` until the log moves. Those two are 28 lines
    shorter.
  - **Tests:** `tests/test_fight_conditions.py` (6 tests without Qt). The
    full suite passes (12,097).
  - **Process note:** a commit run started before the previous one had
    reported found that one's commit unpushed and refused to push. Start
    the next commit run only after the last one has reported.

- **R24 (step 5.3, turns' first slice, 2026-11-23).** The turn order is
  `Fight`'s:
  - questions: `turn_span`, `current_turn_group`, `is_last_turn`,
    `is_first_turn`, `turn_is_dead` and `upcoming_turns(skip_dead)`;
  - moves: `pass_turn()` (True when it starts a round) and
    `step_back(skip_dead)` (True when it went back one).

  `initiative_units`, `unit_label` and the new `start_turn` (a turn's
  actions back, its movement on the map anew) are module functions of
  `fight.py`, and their importers (`player_view`, `turn_panel_mixin`, a
  test) moved with them.
  - **What `TurnsMixin` keeps:** its six queries are one-line wrappers.
    `_pass_turn` and `_step_turn_back` keep the round's log line, the
    round label, and what the turn passing sets off (durations, spells,
    saves, triggers, kept areas, monsters' turns).
  - **Tests:** 7 more in `tests/test_fight.py` (group turns, a new round,
    stepping back over dead turns, upcoming turns, a turn's start). The
    full suite passes (12,104).
- **R25 (step 5.3, casting's first slice, 2026-11-23).** Casting's rules
  are `Combat/Fight/spells.py`:
  - `spend_slot`: a Pact Magic slot when asked for, or when there's no
    spell slot of that level, plus the statistics. It returns a
    `SpentSlot`, or None when there's none to spend.
  - `count_spell_cast`.
  - `spell_recipients`: SELF lands on the caster, AREA on the targets even
    if there are none, anything else on the targets, and None when one is
    needed and none is picked.
  - `active_spell_record`, the timer kept on the caster.
  - `ticks_now` and `tick`: a spell counts down on the turn it was cast
    on, and by `SECONDS_PER_ROUND` rather than a bare 6.
  - **What `SpellsMixin` keeps:** the log lines, the badge, conditions and
    Concentration a cast gives, and the expiry loop. That loop ends a
    spell's effects as it goes, and that can change other combatants, so
    only the per-entry decisions moved. It's 17 lines shorter.
  - **Tests:** `tests/test_fight_spells.py` (7 tests without Qt). The full
    suite passes (12,111).

- **R26 (step 5.3, summons' first slice, 2026-11-23).** Joining and
  leaving the fight are `Fight` methods, and the questions a fight asks of
  its summons are `Combat/Fight/summons.py`:
  - **`Fight`:** `place_in_turn_order` (before the first turn that rolled
    lower; a roll not known isn't compared), `place_as_in_turn_order`,
    `follow_owners_in_turn_order`, `move_in_turn_order` (Set
    initiative...) and `remove`. Each keeps whoever's turn it is.
    `INITIATIVE_KEY` moved to `fight.py` with them, and its importers with
    it.
  - **`summons.py`:** `summon_owner`, `owner_summons`, `summon_source`,
    `same_summons`, `room_for`, `already_summoned_options`, and
    `carry_summons_over` (the summons an earlier encounter left out, back
    as they were). `Combat/Summons.py` stays where it is: it's the summons
    themselves, and the player log's replay and the tests use it too.
  - **What stays in the window:** the menus, the log lines, rolling a
    summon's initiative (a roll site, `test_roll_sites`), the initiative
    screen's rows, the selection, and ending what a leaving summon
    concentrates on (it logs). `_summon_owner`, `_owner_summons`,
    `_summon_source`, `_already_summoned_options` and `_carry_summons_over`
    are one-line wrappers, because tests and other mixins call them.
    `_same_summons`, `_room_for`, `_place_as_in_turn_order` and
    `_place_in_turn_order` are gone, and so is one stub (210).
  - **Order kept:** `_join_fight` still puts the followers in the turn
    order, then each summon with its own roll, then the followers among
    the characters, so the window's order is what it was.
  - **Tests:** `tests/test_fight_summons.py` (6 tests without Qt, on
    Dessie's and Hanna's sheets) and 8 more in `tests/test_fight.py`.
    `summons_mixin.py` 679 → 520 lines, `turns_mixin.py` 770 → 736. The
    full suite passes (12,125).

- **R27 (step 5.3, Wild Shape, 2026-11-23).** Wild Shape's rules were
  already Qt-free: `Combat/WildShape.py` holds the forms, taking one on,
  leaving it and what can be cast in it. So this slice is small:
  - `Combat/Fight/wild_shape.py`: `wild_shape_uses_left`, and
    `describe_form_badge` (the badge's statistics, in `WILD_SHAPE_COLOR`,
    which moved with it).
  - `Combat/Fight/conditions.py`: `incapacitates` (from
    `conditions_mixin.py`) and `incapacitated_by`, the condition that
    keeps one from the Bonus Action Wild Shape costs.
  - **What `WildShapeMixin` keeps:** the menu, and the order of what taking
    a form on does (a use, the Bonus Action, leaving the old form, the
    temporary Hit Points, the badge), because each of those logs.
    `_wild_shape_uses_left` is a one-line wrapper (a test calls it).
  - **Not merged:** `Combat/Effects/triggers.py` has its own copy of the
    incapacitating conditions. That file is the effects plan's, so it's
    left for step 9a's split of `triggers.py`.
  - **Tests:** `tests/test_fight_wild_shape.py` (4 tests without Qt).
    `wild_shape_mixin.py` 192 → 178 lines. The full suite passes (12,129).

- **R28 (step 5.3, rests, 2026-11-23).** A long rest has no rules to move:
  it's a line in the player log, and the party is replayed from after it
  onto rested sheets. A short rest's are `Combat/Fight/rests.py`:
  - `regain_feature_uses` (with `SHORT_REST_CADENCES`, which moved with
    it, and the features that get only some uses back) and
    `regain_pact_slots`. Each returns what came back, one entry per use or
    slot, and `rest.py` logs one event for each, as before.
  - `heal_with_hit_dice`: none for the dead, else `health.py`'s
    `regain_hit_points`, which now takes `counted=False`. A short rest is
    outside any fight, and it never counted in the statistics. The
    short-rest window had its own copy of that arithmetic; now there's one.
  - **What stays in the window:** `RestsMixin` (the buttons, the question,
    the player log entry) and `rest.py`'s window, its heal boxes and the
    log lines.
  - **Order:** a downed player's Death Saving Throws are reset before the
    heal's log line now, not after it. The line doesn't read them.
  - **Tests:** `tests/test_fight_rests.py` (6 tests without Qt). `rest.py`
    221 → 200 lines. The full suite passes (12,135).

- **R29 (step 5.3, the log's first slice, 2026-11-23).** What a log has to
  do with the fight is `Combat/Fight/log.py`:
  - `record_fight`: what an encounter log saves of a fight (the round, the
    turn order by name and whose turn it is, the map, the non-player
    combatants without their `"_"` keys, the players' fight state).
  - `take_combatants_from`: a log's combatants beside the players, older
    logs' keys upgraded, slots by level. `saved_map`,
    `saved_initiative_order` and `continue_fight` (a saved fight continued
    on the turn it stopped at). `slots_by_level` and `SLOT_POOLS` moved
    with them.
  - `replay_player_log` and `apply_replay_action`: the party's state
    replayed from the recorded actions. That needed one change: the
    replay's Bloodied went through `_apply_bloodied_condition` with no
    source, which never logs. That silent half is now `health.py`'s
    `resync_bloodied` (with `bloodied_change`), and
    `_apply_bloodied_condition` calls it when there's no source.
  - **What `LoggingMixin` keeps:** reading and writing the files, the
    party's journal entry, `_log_event` (it reads the views' timer, the
    undo point and the rest being taken), Undo, and the log windows.
    `_apply_replay_action` is a one-line wrapper (9 test uses).
    `_take_combatants_from` and its stub are gone (its two callers in
    `encounters_mixin.py` call the function), and so are
    `_saved_initiative_order` and `_replay_player_log`. 209 stubs.
  - **Why `_log_event` stays for now:** an event's line names whose turn
    it is and whether players may read it, which `Fight` could answer, but
    it also opens the undo point's list of lines and starts the views'
    timer. Moving it waits for step 6's refresh path, which takes the
    timer out, and for `undo.py`, which moves after step 6 too (R17).
  - **Tests:** `tests/test_fight_log.py` (9 tests without Qt).
    `logging_mixin.py` 791 → 518 lines. The full suite passes (12,144).

- **R30 (step 5.4, the Asker's first question, 2026-11-23).** The fight
  asks the GM through an `Asker` (`Combat/Fight/asker.py`), a Protocol with
  one question so far: `go_ahead_anyway(char, doing, missing)`, "out of
  resources, go ahead anyway?".
  - **`Combat/Fight/resources.py`:** the checks moved there unchanged from
    `Combat/CombatUIQt/resources.py` (`action_lack`, `feature_uses_left`,
    `feature_lack`, `spell_slot_lack`, `monster_action_lack`,
    `legendary_resistance_lack`), plus `go_ahead_anyway(asker, char,
    doing, lacks)`, which asks only when something is missing. Their
    importers (four mixins, three tests) moved with them.
  - **The window's Asker** is `Combat/CombatUIQt/asker.py`'s
    `WindowAsker`, held as `CombatAppQt.asker`. It asks with the same
    `QMessageBox.question` as before, and a No says why on the status
    line, so the tests' `answer_out_of_resources` still answers it.
    `ResourcesMixin` keeps `_action_lack` (no action economy between
    encounters) and `_go_ahead_anyway`, now a one-line call through the
    Asker.
  - **Tests** answer with `ScriptedAsker`, which takes its answers from a
    list and keeps each question asked. `tests/test_fight_resources.py`
    has 4 tests without Qt. The full suite passes (12,148).

- **R31 (step 5's review so far, 2026-11-23).** The `code-reviewer` checked
  R17-R30 (`git diff 1e01a850..36642fce`) and found no behaviour change in
  the moves. It checked the order arguments of R22, R26 and R28, and that
  no module under `Combat/Fight`, `Combat/Effects` or `Combat/Arena`
  imports Qt even indirectly. Its findings were all in tests, and are
  fixed:
  - `test_fight_log` asserted that Bloodied ends at 0 Hit Points, which is
    the open DI-007, not the rule ("half its Hit Points or fewer"). The
    test no longer asserts it, and says why.
  - `test_fight_attacks`' "a miss adds no notes of a hit" used a Prone
    target, which a hit gives no notes either, so it couldn't fail. It
    uses a Paralyzed one now.
  - `test_fight_conditions`' "the maximum before" lost Prone, which
    doesn't change the maximum. It loses an Aid badge (+5) now.
  - `test_roll_sites` keys files by their path in each scanned folder,
    and `resources.py` and `asker.py` are in two of them. A new test fails
    when a file with a roll site shares its path with another folder's.

  Two `combat-ui-explore` sweeps (`ashelm_church`, `time_loop_pr_square`)
  found nothing. A probe of summons, Set initiative, a drake vanishing,
  dismissing and Wild Shape, each with Undo and a reopen, found DI-113,
  which is older than step 5.

- **R32 (step 5.4, the Logger, 2026-11-23).** The rules left in the mixins
  (triggers, feature use, a condition's cascades) were each stuck on the
  same thing: they log as they go, and only the window could. So the core
  logs through a `Logger` now (Decision 4):
  - `Combat/Fight/logger.py`: the `Logger` Protocol (`log(text, *,
    note_turn, character, action, value, public)`, the arguments of
    `_log_event`) and `RecordingLogger`, which keeps each `LoggedLine`.
  - **The window's** is `Combat/CombatUIQt/logger.py`'s `WindowLogger`,
    held as `CombatAppQt.logger`. It calls `_log_event` itself, so each
    line gets whose turn it is, its Undo step and its public flag as
    before, in the same order.
  - **Its first users, spending a resource:** `use_action` and
    `count_feature_use` (`Combat/Fight/resources.py`) and `use_slot`
    (`Combat/Fight/spells.py`, `spend_slot` logged). `_add_action_use`
    keeps the phase check, the question, the Opportunity Attack buttons
    a spent Reaction takes away and the card; `_count_feature_use` is a
    one-line call; `_spend_slot` keeps its status line.
  - **Tests:** `tests/test_fight_spending.py` (3 tests without Qt, one of
    them replaying the line it logged). The full suite passes (12,152).
  - **Next:** a hit's triggers. What they apply goes through the Use / Cast
    apply path (`_apply_row`, `_apply_effect_to_targets`), so that path
    moves first, with the Logger and the Asker.

- **R33 (step 5.4, what the players know, 2026-11-23).** The Qt-free half
  of `Combat/CombatUIQt/player_view.py` is `Combat/Fight/player_knowledge.py`,
  moved unchanged (each definition's AST matches): who players can perceive
  (`_can_be_seen`, `_seen`, `HIDDEN_STATES`, ...), `may_read_log_line`, and
  what the log has shown them of a monster (`note_health`,
  `note_damage_defense`, `note_condition_immunity`, `known_max_hp_text`,
  `known_defense_texts`). `player_view.py` keeps the rows and the window;
  its rows read those through imports (`_seen`, `_HEALTH_WORDS`, ...: the
  private names keep their `_`, as in step 9). The importers (four mixins,
  `arena_view.py`, four tests) moved with them.
  - **Why now:** the rules R22 left in the window note what an attack roll
    or a change of Hit Points showed the players, and that was Qt-module
    code. The rows can't follow yet: they use the More Info dialog's stat
    block helpers (`dialogs_mixin.py`), which step 9b moves.
  - **What's next, and why it's one slice.** Gaining or losing a condition
    sets off ending Concentration (`_end_concentration_spells`, with the
    spells' badges on others), leaving a Wild Shape form, standing up,
    Bloodied, Hit Points held to a lower maximum and healing, and each of
    those gains or loses conditions in turn. They call each other, so they
    move together: `_add_condition_to`, `_remove_condition_from`,
    `_take_dash`, `_stand_up`, `_keep_hit_points_in_maximum`,
    `_apply_bloodied_condition`, `_heal_target`, `_leave_wild_shape`,
    `_end_concentration_spells` and its helpers, `_forget_effect_on`. They
    also redraw cards and set the status line as they go, so the core
    reports those in section 2's `StepResult` (who changed, what to say),
    passed down the cascade and drawn once by the window at the end.
  - **Tests:** the existing ones. The full suite passes (12,152).
  - **Only one question, on purpose.** The trigger pop-up
    (`_ask_triggers`) and the initiative tie-break join the Protocol when
    the code that asks them moves into `Combat/Fight/`, so nothing is in
    it that no Qt-free code calls. The other yes/no questions (End
    Encounter, Long Rest, the Map Painter's unsaved map) confirm a click
    on the window rather than ask in the middle of a rule, so they stay
    dialogs.

## Discovered issues

- DI-112: pyright error in `tests/test_roll_sites.py:135`, which was
  already there (found in step 3c).
- DI-113: a Wild Shape badge's source and caster aren't saved until the
  next logged event, so a fight reopened right after a Wild Shape has
  them as None. It's older than step 5 (the order of `_assume_wild_shape`
  is unchanged since 1e01a850). Found by a `combat-ui-explore` probe in
  step 5's review.

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
- Step 9's splits: each moved function's AST matches the old one, and no
  test's `monkeypatch` of a moved name now patches a module that no longer
  looks it up.
- Step 10's moves: the same, plus `git grep` for the old module path finds
  nothing outside `Notes/` and the prose step 8 updates, and the commands
  in step 10's "Done when" still run.
