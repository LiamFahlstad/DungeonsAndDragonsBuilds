# Plan: a battle map view in the combat UI

Goal: a second view of the fight in the combat window, a grid that is the
arena, with a token for every combatant that the GM can move around. One click
switches between this **Arena** view and the usual **Cards** view, and the
turn column, the control panel, selection and undo work the same in both.

Distance is counted with **Manhattan distance** first (moves go up, down, left
and right; a diagonal step costs two squares). The design keeps the counting
rule separate from the grid, so hexagons, Euclidean distance and the
Player's Handbook's own 5-foot diagonals can be added later without changing
the view or the fight state.

Written 2026-11-13. All eight steps (the Qt-free map, its saving, the view,
the Cards/Arena switch, moving, distances in the UI and the docs) built the
same day. Step 9, the fixes after the user tried it, 2026-11-14. Step 10,
targets in an area from the Custom Effect dialog, the user's request the
same day. Step 11, areas that stay on the map with their concentration and
a colour picked for each, the user's request, 2026-11-15. Step 12,
selecting a kept area to read, recolour, target or end it, the same day.
Steps 13 to 18, the rules of moving and "within 5 feet" counted from the
map, 2026-11-15 and 16. Steps 19 and 20, cover and range counted from the
map, the first two of Later, 2026-11-16. Step 21, pushes and pulls from
the Use / Cast dialog moved on the map, Later's third, 2026-11-18. Step 22,
grapples on the map (the grappler drags, the grapple ends past its range),
Later's fourth, the same day. Step 23, the way a walk goes (Opportunity
Attacks along it, Reactive Strike, Undo of the buttons), Later's fifth, the
same day. Step 24, kept areas acting by a turn-column button and moved from
their panel, Later's sixth, the same day. Step 25, walls (the rest of that
sixth item) and DI-096, the same day. Step 26, other speeds, altitude,
falling and water swum, Later's seventh and eighth, the same day. Step 27,
distances in triggers (Later's ninth, closing DI-085), the same day. Step
28, light and senses (Later's tenth, with DI-068), the same day. What's
next is under Later.

## How to use this document

This is a living plan, like [combat-effects-plan.md](combat-effects-plan.md).

**The plan updates itself as the work teaches us** (the user, 2026-11-13).
It's the best guess before building, not a contract. When working on a step
turns up a better solution, or a realisation that changes the picture (an
interface that doesn't fit, a step that's needed earlier, a rule that reads
differently, an existing piece of code that already does part of it), do the
better thing and change the plan to match in the same change. Rewrite the
Design, add, split, reorder or drop steps, replace a decision, raise a new
question. Then record what changed and why as a Revision. Nobody follows the
plan against a better idea just because it was written down first; the only
thing that needs the user's word first is overruling one of the user's own
decisions.

Whoever works on the arena updates it **in the same change** as the code:

- **Status**: tick the step, with the date and the Revisions it made.
- **Decisions**: numbered, never renumbered. Each says who decided and when
  ("the user, 2026-11-13", or "in the plan, for the user to overrule"), and
  which question it settles. A decision that replaces an earlier one says so,
  and the earlier one gets "replaced by N" rather than being deleted.
- **Open questions**: numbered Q1, Q2, ..., never reused. Each says which step
  it blocks and gives a *Suggestion*, which is what gets built if nobody says
  otherwise. When it's answered, it moves to Decisions and leaves a one-line
  pointer behind ("Q2: Decision 10").
- **Revisions**: numbered R1, R2, ... Each better solution or realisation
  (see above) gets one: what the plan said, what's done instead, why, and the
  step it came from. The Design, Steps and Status are then brought up to
  date, so they always describe what is built or about to be, and the
  Revisions keep the history of how it got there.
- **Discovered issues**: bugs and gaps found along the way go into
  [discovered-issues.md](discovered-issues.md) through the `discovered-issues`
  skill's `issues.py` (never edited by hand), and their ids and state are
  listed here. Mark one fixed with `issues.py update` when a step fixes it.

**Keep the overhead low (the user, 2026-11-10).** Run only the arena's own
test files after a step (`./run_tests.sh -q tests/test_arena*.py
tests/test_combat_ui_arena*.py`), and the attack and dialog tests
(`tests/test_combat_ui_attack_roll.py tests/test_combat_ui_custom_effect.py
tests/test_effect_modifiers.py`) when a step changes how a roll is made. No step here changes a character sheet, so the
character-creation tests and snapshots don't need to run. No reviewer or
verification passes per step unless asked.

## Status

| Step | What | State |
|---|---|---|
| 1 | Geometry: cells, the square grid, the Manhattan rule, the rule registry (Qt-free) | Done 2026-11-13 (R1) |
| 2 | Arena state: map settings, positions, footprints by size, distances between creatures, reachable cells, placing tokens (Qt-free). Fix DI-084 first: the reach reads `speed_in_use` | Done 2026-11-13 (R2); DI-084 fixed |
| 3 | Saving: positions and map settings in the encounter log, undo | Done 2026-11-13 (R3) |
| 4 | The view: the grid and tokens drawn, click to select and target | Done 2026-11-13 (R4) |
| 5 | Switching views: the Cards/Arena toggle and its shortcut | Done 2026-11-13 (R5) |
| 6 | Moving: drag or click to move, reach shown, feet moved this turn | Done 2026-11-13 (R6) |
| 7 | Distances in the UI: hover and the target label in feet | Done 2026-11-13 (R7) |
| 8 | Docs: KEYBOARD_SHORTCUTS.md, HOWTO.md, Combat/CHEATSHEET.md | Done 2026-11-13 (R8) |
| 9 | After the user tried it: encounter allies on the party's side, click to pick up and click to move, the move's line with from, to and what's left, whose turn on gold, clicks and Ctrl+Z in both views | Done 2026-11-14 (R9); DI-092 fixed |
| 10 | Targets in an area: the Custom Effect's "Select targets in area", the area read from the pick's text and aimed on the map, whoever is in it targeted | Done 2026-11-14 (R10); Cones, Lines and range checked against Manhattan 2026-11-15 (R11) |
| 11 | Areas that stay: kept on the map by an active spell, ending with its time or its caster's concentration, an Emanation following its caster, reminders on entering and at a turn's start; a colour for each area | Done 2026-11-15 (R12) |
| 12 | Selecting a kept area: a click on it, the area panel with what it is and its rules text, its colour, Target who's in it, End spell | Done 2026-11-15 (R13) |
| 13 | Dash and Opportunity Attacks reminded of | Done 2026-11-15 |
| 14 | Opportunity Attacks made in the UI | Done 2026-11-15 |
| 15 | Moving by what a creature has: Halfling Nimbleness, Incorporeal Movement, Swarm, Difficult Terrain ignored (Freedom of Movement, Speedy, Fairy Trickster), climbing at no extra cost, standing up from Prone spent from its movement | Done 2026-11-16 (R14) |
| 16 | Counting "within 5 feet" from the map: Prone's Advantage/Disadvantage, Paralyzed's and Unconscious's Critical Hits | Done 2026-11-16 (R15, R16); DI-085 narrowed |
| 17 | Moves that aren't walks: Teleport and Pushed, no movement spent and no Opportunity Attack | Done 2026-11-16 (planned in R15) |
| 18 | Distances count only once the map is in use: a token moved this fight, or a painted map's starts (Decision 29) | Done 2026-11-16 |
| 19 | Cover from the map: walls, objects and creatures on the line give cover, counted into the AC and Dexterity saves, Total Cover warned about, areas stopped by it | Done 2026-11-16 (R17; Decision 30) |
| 20 | Reach and range: Long range's and close combat's Disadvantage counted, past a reach or range warned about | Done 2026-11-16 (R18; Decision 31) |
| 21 | Pushes: a pick's `CombatPush` (Thunderwave, a Shove, the Push mastery) moves who it lands on straight away from its source as a Push move | Done 2026-11-18 (R19; Decisions 32, 33); DI-095 logged |
| 22 | Grapples: the Grappled creature names its grappler, who drags it at 1 extra foot a foot; the grapple ends past its range or with the grappler Incapacitated; the Unarmed Strike's Grapple row | Done 2026-11-18 (R20; Decision 34) |
| 23 | The path walked: Opportunity Attacks anywhere along a walk, Polearm Master's Reactive Strike on entering a reach, Undo taking a walk's buttons back, a spent Reaction taking its attacker's other buttons away | Done 2026-11-18 (R21; Decision 35) |
| 24 | Areas that stay, acting: a turn-column button when a creature enters a kept area, the area is moved onto it, or a turn starts or ends in it, as its text says, opening Use / Cast on its effect at no cost; the area panel's Move (Moonbeam, Flaming Sphere) | Done 2026-11-18 (R22; Decisions 36, 37); DI-096 logged |
| 25 | Walls: a Wall shape aimed by its two ends (a ring by its middle); Wall of Force blocking movement and giving Total Cover while it lasts, through the map the rules read and never the painted one; Wall of Fire's damaging side picked by a third click and acting on who ends a turn by it; Flaming Sphere's area (DI-096) | Done 2026-11-18 (R23; Decisions 38 to 41); DI-096 fixed, DI-097 logged |
| 26 | Other speeds: the speed bar picking a creature's Speed, Fly, Swim, Climb or Burrow Speed for its moves (switching counts what it moved), each costing as it should over the ground, a flyer's altitude (spending movement, counted into distances), falling when it can't stay aloft, water swum; the Fly spell's Fly Speed | Done 2026-11-18 (R24; Decisions 42 to 46); DI-098 logged |
| 27 | Distances in triggers: a `when` asking how far the other creature is (Fire Shield's "within 5 feet", Hellish Rebuke's "within 60 feet") counted from the map, and Dark One's Blessing for a knockout someone else makes within 10 feet of its owner (combat-effects plan Q63) | Done 2026-11-18 (R25; Decisions 47, 48); DI-085 fixed |
| 28 | Light and senses: who sees whom from the map (painted Darkness, kept areas that are Darkness or Heavily Obscured, Invisible, Blinded; Darkvision, Blindsight, Truesight, See Invisibility, Faerie Fire), counted in attack rolls, the close-combat Disadvantage and triggers' "you can see it"; the Invisible visibility state as the condition | Done 2026-11-18 (R26; Decisions 49-53); DI-068 fixed |

## How it fits the code that's there

What the code already gives, found while writing this:

- **The window** ([window_mixin.py](../Combat/CombatUIQt/window_mixin.py),
  `_build_window`, whose `_build_frame` lays it out since the refactor
  plan's step 4) is a row of three parts: the cards' scroll area
  (`self._scroll_area`), the turn column, and the control panel. Only the
  first part changes between views; the other two stay as they are.
- **Selection** is the app's, not the cards': a left click calls
  `_select_character(char)` and a right click
  `_select_target_character(char, ctrl, shift)`. A token calls the same two,
  so Ctrl/Shift targeting and every button in the control panel work on the
  map with no changes.
- **Undo** ([undo.py](../Combat/CombatUIQt/undo.py)) copies every key of a
  combatant dict that doesn't start with `_`. A position kept on the
  combatant (`char["position"]`) is undone with everything else, as long as
  moving is an `@undoable` method.
- **Saving a fight in progress** (`LoggingMixin._write_log`) already keeps
  every public key of each monster and ally in `"combatants"`. Players keep
  only `PLAYER_FIGHT_KEYS` ([EncounterLogs.py](../Combat/EncounterLogs.py)),
  so `"position"` is added there.
- **Refreshing**: `_refresh_cards` and `_refresh_views` run after anything
  changes. The arena refreshes from the same places.
- **What the map reads, live**: `size_in_use(char)` and `speed_in_use(char,
  stored)` in [modifiers.py](../Combat/Effects/modifiers.py) (an Enlarged
  Ogre takes up Huge space, Haste doubles the reach shown), and
  `on_party_side(char)` in [triggers.py](../Combat/Effects/triggers.py) for
  the token's colour and starting edge. An encounter's own allies
  (`EncounterSpec.allies`) count since step 9 (DI-092). A walking speed is `speed_ground_ft` on a monster and
  `speed` on a player (as `_speeds_text` in `dialogs_mixin.py` reads them);
  a creature with neither shows no reach.
- **The conditions' Speed 0** (DI-084, fixed in step 2): Grappled,
  Restrained, Paralyzed, Petrified and Unconscious give `Speed(set_to=0)`
  beside their note, so `speed_in_use` is 0 and a Grappled goblin reaches
  nothing.

## Design

Two layers, kept apart: the rules of the grid, with no Qt, under a new
`Combat/Arena/` package, and the Qt view under `Combat/CombatUIQt/`. All the
counting is testable without a window, as with `Combat/Effects/`.

### Grid shape and distance rule are two different things

A battle map has two separate choices:

- **The grid shape**: how cells are laid out and drawn (squares, hexagons),
  which cells are next to each other, where a cell is on screen and which
  cell a mouse point falls in.
- **The distance rule**: how far apart two cells are on that shape.

Several rules share one shape. Squares can be counted as Manhattan (a
diagonal is two steps), Chebyshev (a diagonal is one step, the 2024 Player's
Handbook's default), 5-10-5 (every second diagonal costs double, the
optional variant) or Euclidean (straight-line distance, rounded). Hexagons
have one natural rule. So each `DistanceRule` names the `GridShape` it
works on, and the map settings pick a rule, which brings its shape.

```text
Combat/Arena/geometry.py                (Qt-free)
  Cell(col, row)                        frozen dataclass; hex cells use axial (q, r) in the same two fields
  Cell.of([col, row]) / cell.to_list() to and from a combatant's "position"
  GridShape (abstract)                  SquareGrid now, HexGrid later
    neighbours(cell) -> list[Cell]      the cells next to it, all of them (the edge is the arena's)
    center(cell, size_px) -> (x, y)     where to draw it
    polygon(cell, size_px) -> [(x, y)]  its outline
    cell_at(x, y, size_px) -> Cell      which cell a point falls in
    footprint(anchor, cells) -> [Cell]  the cells a creature N cells across covers
    in_bounds(cell, w, h), cells(w, h)  the map's edge, and every cell on it
    offset(cell, cols, rows)            a cell so far across and down (lining a token up on an edge)
    from_edge(w, h, left) -> [Cell]     from one edge inward, middle row first: where tokens start
    labels(cell) -> (col, row)          what the edges show: ("C", "7"); cell_name(cell) "C7" (R9)
  DistanceRule (abstract)
    key, label, shape                   "manhattan", "Manhattan (diagonals cost 2)", SquareGrid
    steps(a, b) -> float                cells apart; an int for grid rules
    feet(a, b, cell_ft) -> int          what the UI shows, rounded the rule's way
    neighbours(cell) -> list[Cell]      the cells a move steps to (the shape's by default; R1)
    step_cost(a, b) -> float            the cost of one move between neighbours
  ManhattanRule(DistanceRule)           |dc| + |dr|, 4 neighbours, every step costs 1
  RULES: dict[str, DistanceRule]        {"manhattan": ManhattanRule()}; a new rule is a class and one line here
  rule_named(key) -> DistanceRule
```

Everything else (distances between creatures, reach, the view's drawing and
clicks) goes through these two interfaces and never does arithmetic on
`col` and `row` itself (Decision 3). A step that has to
`if rule.key == "manhattan"` is a step that's in the wrong layer.

Movement is a path search over `neighbours` with `step_cost`, times what the
mover's state and the cell add (crawling while Prone, another creature's
space, later difficult terrain). That is a uniform-cost search, so it doesn't
need to change when a rule or a cost is added.

### The arena's state

```text
Combat/Arena/arena.py                   (Qt-free)
  ArenaSettings                         width, height (cells), cell_ft = 5, rule = "manhattan"
    to_dict() / from_dict(data)         the encounter log's "arena" key; tolerant of a log without one
    distance_rule, on_map(cell)         the rule it names (rule_named), and its edge
  position(char) -> Cell | None         its anchor; None when it isn't on the map
  size_cells(char)                      from size_in_use: Tiny/Small/Medium 1, Large 2, Huge 3, Gargantuan 4 cells across
  footprint(char, rule) -> [Cell]       footprint_at(char, anchor, rule) for a cell it isn't on yet
  occupied(chars, rule) -> {Cell: char}
  distance_ft(a, b, settings) -> int | None
                                        between two creatures: their nearest cells (Decision 8); None off the map
  walking_speed_ft(char) -> int | None  speed_in_use of speed_ground_ft or speed, else its highest
                                        Fly/Climb Speed (Q7); None when it has none
  can_pass_through(mover, other)        Q4: an ally, Incapacitated or at 0 HP (Q9), Tiny, two sizes apart
  is_difficult_for(mover, other)        Q4: a creature that isn't Tiny or an ally
  reachable(char, chars, settings, feet) -> {Cell: feet}
                                        where it can end a move of `feet`, and what each costs:
                                        a uniform-cost search with those two and crawling (Q8)
  fits_at(char, anchor, chars, settings), nearest_free(char, near, chars, settings)
  place_new(chars, settings)            starting cells for whoever isn't on the map yet (Q1)
  place_beside(char, owner, ...)        the first free cell next to another
  place_summons(new, chars, settings)   each new summon beside its owner, when the owner is on the map
```

A combatant's place is on the combatant, as plain JSON (Decision 4):

```python
char["position"] = [col, row]   # its footprint's top-left cell (the anchor); no key = not on the map
char["moved_ft"] = 15           # how far it has moved this turn; reset as its turn starts
```

Plain lists, not `Cell`, so undo's copy and the log's JSON need nothing new.
`Cell` is built from it where it's read.

The map settings are the fight's, not a combatant's: they're kept on the app
(`self.arena_settings`) and in the encounter log's top-level `"arena"` key.
Changing them isn't an undo step yet (Q6).

**Nothing about the map goes into the player log** (Decision 5). Positions
only matter inside one fight, so a move logs no `action` and nothing is
replayed from it on the next session. Continuing a fight in progress reads
positions back from the saved fight state.

### The view

```text
Combat/CombatUIQt/arena_view.py         ArenaView(QGraphicsView): draws, no rules
  the cells, from shape.polygon         a light grid; coordinates on the edges; the whole map
                                        fits the view until the GM zooms (R4)
  a token per placed combatant          a circle (a square covering its footprint when Large+)
                                        with its letters (token_label: "G2", "A1", "HD"),
                                        coloured by side (Q5), its name as a tooltip,
                                        its HP as a thin bar, a gold ring on whose turn it is
                                        and its cells tinted and edged gold, as its card (R9),
                                        the source and target outlines the cards use (white,
                                        red; both: white with a red ring inside),
                                        greyed at 0 HP (Q9), dashed while the players can't see it
  "Not on the map" strip                a button per combatant without a position: it becomes
                                        the source, and a cell clicked puts it there (R6)
  pick_up(row, held) / drop(cell)       a drag: the reach shaded with its costs, then on_move
                                        with the anchor that puts the held cell on `cell`
  pick(name, held) / move_picked(cell)  a click on a token picks it up (the same shading), the
                                        next click on an empty cell moves it; unpick() puts it
                                        down; a double-click counts as a click (R9)
  zoom with Ctrl+wheel, pan by dragging empty space
  token_rows(chars, settings, turn, source, targets) -> [TokenRow]
                                        the rows, from the combatant dicts (Decision 6)
Combat/CombatUIQt/arena_mixin.py        ArenaMixin: the glue
  _build_view_stack(cards)              the stack, and the view wired to _select_character /
                                        _select_target_character by name
  _build_view_toggle()                  the turn column's Arena / Cards button
  _toggle_view()                        Cards <-> Arena, during combat only (G)
  _show_view()                          the page the phase and the view last used call for
  _place_on_arena()                     place_new as combat starts or is continued
  _arena_reach(name)                    reachable with remaining_ft: what a picked-up token shades
  _arena_pick(name)                     the strip's button: the source, picked up
  _arena_cell(cell)                     an empty cell clicked with nobody picked up: a hint,
                                        no move (Decision 14)
  _move_combatant(char, cell)           @undoable: places one off the map, or walks one on it
                                        (move_cost, else straight_ft), adds to moved_ft, logs
                                        a GM-only line (which saves the fight), warns (Q2, Q8)
  move_line(char, start, to, ...)       that line: "Clover moves from A7 to C8 (15 ft.; 15 of
                                        30 ft. left this turn)." (Decision 13)
  _refresh_arena()                      called from _refresh_views (R4); puts a picked-up
                                        token down once it isn't the source (R9)
```

The view gets what it draws as a list of plain token rows (name, cells,
colour, HP fraction, flags), made by one function, like `player_view_rows`
for the Player Screen (Decision 6). The view never reads a combatant dict,
which keeps it simple to test and makes a map on the Player Screen (later) a
second reader of the same rows.

**Switching** (Decision 9). `self._scroll_area` becomes page 0 of a
`QStackedWidget` and the `ArenaView` page 1, in the same place in the row. A
button at the top of the turn column, "Arena" / "Cards", and the **G** key
switch between them. **G** is free: neither KEYBOARD_SHORTCUTS.md nor the
code binds it. The view picked is kept in the settings store (`view/arena`,
Decision 10), so the window opens on the one last used. The initiative
screen and the party view between encounters stay cards-only, and the
button hides with them.

**Moving** (Decision 12). Click a token, which makes it the source and
picks it up, then click an empty cell; or drag the token to a cell. A
picked-up token is put down again by a second click on it, Escape, another
source or the turn moving on. A click on an empty cell with nothing picked
up moves nobody (Decision 14). While a token is picked up or dragged, the
cells it can reach this turn (its walking speed in use, less `moved_ft`)
are shaded with what each costs.
Going past the reach is warned about, not refused (Q2). Ending on another
creature is refused (Q4). Each move is one undo step. A move counts the
cheapest walk there (`move_cost`); when no walk gets there (walled in by
enemies) it counts the straight distance and the log line says so, as the
GM moved it some other way. A creature with no Speed as a number (a plain
combatant like the Pirate) reaches only its own cell but can still be
moved. Someone without a place is put on the map from the strip: their
button picks them up, and a cell clicked puts them there; placing moves
nothing and logs nothing. A move's line names the cells it went from and
to, columns lettered and rows numbered as on the map's edges ("C7",
Decision 15), and what's left of the Speed (Decision 13).

**Distances.** With a source selected, hovering a cell or token shows the
distance from the source in feet next to the cursor, and the target label
reads "Target: Goblin (25 ft.)" while both are on the map. The Cards view
shows the same label, so a range can be checked without switching.

## Steps

### Step 1: geometry (`Combat/Arena/geometry.py`, new)

`Cell`, `GridShape` and `SquareGrid`, `DistanceRule` and `ManhattanRule`,
`RULES` and `rule_named`.

Tests (`tests/test_arena_geometry.py`, new): Manhattan's distances (a
straight line, a diagonal costs 2, symmetric, 0 to itself), feet at 5 ft.
cells, four neighbours (the map's edge is the arena's job, so `neighbours`
gives all four and step 2 filters), `cell_at` of `center` gives the cell
back, a 2-cell footprint is 4 cells. One test runs the same contract
(symmetry, zero to itself, neighbours one step away, `cell_at(center(c)) ==
c`) over every rule in `RULES`, so a new rule is tested by being registered.

### Step 2: arena state (`Combat/Arena/arena.py`, new)

First fix DI-084 (the conditions' Speed 0 as `Speed(set_to=0)` in
`Model/Content/RulesConditions.py`), which the reach depends on.

Then `ArenaSettings`, `footprint`, `occupied`, `distance_ft`,
`walking_speed_ft`, `reachable`, `place_new`, `place_beside`.

Tests (`tests/test_arena.py`, new), on plain combatant dicts: a Large
creature's distance counts from its nearest cell; an Enlarged Medium creature
takes 2x2 (reads `size_in_use`); `reachable` with 30 ft. is the Manhattan
diamond of 6 steps, cut by an enemy in the way, open through an ally, never
ending on anyone, and cut at the map's edge; a Grappled creature reaches
nothing; a Prone one half as far (Q8); `place_new` puts the sides apart
without overlaps; `from_dict({})` gives the defaults.

### Step 3: saving and undo

- `"position"` and `"moved_ft"` added to `PLAYER_FIGHT_KEYS`.
- The `"arena"` key written by `_write_log` and read back by
  `_load_log_from_path`.
- `moved_ft` dropped as a combatant's turn starts (no key is 0 ft.; where
  `action_uses` resets, in `turns_mixin._pass_turn`).
- A summon that comes out is placed beside its owner (`place_summons` in
  `summons_mixin._join_fight`) when its owner is on the map.

Tests (`tests/test_combat_ui_arena.py`): a fight saved with positions and
continued has them back, players' too, and its map; a log without a map gets
the default one; undo (an `UndoPoint`, until step 6's `_move_combatant`)
puts a token back with its `moved_ft`, or takes it off the map again;
`moved_ft` resets as its own turn starts, not another's.

### Step 4: the view (`arena_view.py`, `arena_mixin.py`, new)

The grid and tokens drawn, the token rows function, clicks wired to selection.
Look at it with the `run-apps` skill's offscreen screenshot (`combat --arena`,
added for this).

Tests (`tests/test_combat_ui_arena.py`): starting the fight puts everyone on
the map, the sides apart and nobody overlapping; token letters; token rows
carry the turn, the selection, 0 HP, hidden and Large footprints, and leave
out whoever isn't on the map; left and right clicks (with Ctrl) select and
target as the cards do and the rows show it; a click finds the token under
it.

### Step 5: switching views

The `QStackedWidget`, the toggle button, **G**, the settings store's
`view/arena` that remembers the view. The toggle hides outside combat.

Tests: G does nothing on the initiative screen, switches both ways in combat
and remembers it, the button says which view it goes to, and a fight opens
on the view last used.

### Step 6: moving

Drag and click-to-move through `_move_combatant`; the shaded reach; the
over-speed warning (Q2); the move's log line, if any (Q3); the "Not on the
map" strip.

Tests (`tests/test_combat_ui_arena.py`, `tests/test_arena.py`): a drag
shades the reach with its costs and moves the token, logs a GM-only line
with no action and leaves less reach for the next; a move is one undo step;
a click on an empty cell moves the source (and asks for one without);
ending on someone is refused with nothing to undo; past the Speed is warned
about and allowed; Prone crawls at half the reach with a reminder; the strip
lists whoever has no place and puts them on the map, which undo takes back;
a token put on someone goes to the nearest free cell; a Large token moves by
the cell it's held by; no Speed, no reach; the real mouse (press, move past
the drag distance, release) drags a token; `move_cost`, `straight_ft` and
`remaining_ft` on plain dicts.

### Step 7: distances in the UI

The hover distance and "(25 ft.)" in the target label.

Tests: the target label gives each target's distance from the source in
the Cards view too, and none for the source itself; it follows a move and
its undo; none without a source or with a target off the map; a hover over
an empty cell counts from the source's nearest cell, over a token the
creatures' nearest cells, over the source nothing; `distance_to_cell_ft`
on plain dicts.

### Step 8: docs

**G** and the arena's mouse controls in
[KEYBOARD_SHORTCUTS.md](../Combat/CombatUIQt/KEYBOARD_SHORTCUTS.md) (a row in
the table and an "On the battle map" section), the view in HOWTO.md (a
paragraph and the shortcut table). CHEATSHEET.md is left as it is (R8).

### Step 9: after the user tried it (2026-11-14)

The user's six points (R9): an encounter's allies on the party's side,
selecting and targeting in both views, whose turn it is highlighted as on
the cards, Ctrl+Z after a move, the move's line with where from and to and
what's left, and moving by a click on the token and a click on a cell.

Tests (`tests/test_combat_ui_arena.py`, `tests/test_arena_geometry.py`):
Wrath of Durmor's Greypaw and Harat are on the party's side and start on
the left, also from a log prepared before the mark; a click picks a token
up and a click on a cell moves it, a second click puts it down, another
source or Escape too, and a click with nothing picked up moves nobody;
Ctrl+Z through the window's shortcut takes back a move made by clicks;
real left, right, Ctrl+right and double clicks select and target on the
map, and real clicks on the cards, with the map showing the same; whose
turn it is has gold cells; the move's line; cell names.

### Step 10: targets in an area (2026-11-14)

The user: "to the custom effect in the combat ui add support for 'select
targets in area' button when you click in you go to the area view and you
can hover over cells to see which cells the spell/feature can hit. Those
targets are then automatically selected if they are within area."

- `Combat/Arena/areas.py` (new, Qt-free): `AreaOfEffect` (shape, size,
  a Line's width, from the source), `parse_area(text)` (the first area a
  rules text states: "20-foot-radius Sphere", "15-foot Cone",
  "100-foot-long, 5-foot-wide Line", "15-foot Cube originating from you",
  "15-foot Emanation", "20-foot square", "each creature within 5 feet of
  you / of that point"), `area_cells(area, source, aim, settings)` and
  `creatures_in(chars, cells, settings)`. How each shape sits on the
  grid: Decision 16.
- The dialog (`conditions_mixin.py`): a **Select targets in area** button
  (Alt+R), enabled in a fight with the source on the map. It closes the
  dialog, and the map is brought up with the area bar (Decision 17).
- The map (`arena_view.py`): `start_area` / `aim_area` / `stop_area`, the
  covered cells shaded orange and an orange ring on each token in them; a
  left click picks, a right click cancels, nothing is picked up or moved
  meanwhile.
- The window (`arena_mixin.py`): the area bar over the map (what it is and
  who's in it, shape, size, a Line's width, From the source, Cancel), the
  area read from the pick's rules text (`EffectOption.tooltip`) or the last
  one used, a click setting the targets and opening the dialog again on the
  same pick; Esc, G, a right click or Cancel going back with the targets
  as they were.

Tests (`tests/test_arena_areas.py`, `tests/test_combat_ui_arena_areas.py`):
the areas real spell and stat-block texts state, and none for a single
target; each shape's cells on squares (the Manhattan Sphere's diamond, the
Cone's 1-3-3, a Line from the source's edge, a Cube centred or against the
source's side, a Large source's Emanation), the map's edge; who is in an
area by any of their cells; the button bringing up the map with the Ice
Mephit's Frost Breath read as a 15-foot Cone, aiming naming who is in it, a
click (also a real one) targeting them and reopening the dialog on the
pick, nobody in it changing nothing, the four ways back, the bar's shape
and size changing the area, an Emanation shown unaimed, the button off with
the source off the map, the last area kept for a pick without one.

### Step 11: areas that stay, and their colour (2026-11-15)

The user: "Many spells/features that has area effects in the combat ui have
lasting effects. Your task is to add support for lasting effects and
concentration. Also make it possible to select color for the effect in the
area view."

- `Combat/Arena/lasting.py` (new, Qt-free): an area that stays is an
  `"area"` record on an active spell of its caster's (Decision 20):
  `area_record` (shape, size, where it was aimed, the cells it covers, or
  `follows` for an area around the caster, its colour), `record_cells`
  (the cells now: around the caster where it is, else the cells it was put
  on), `lasting_areas` (every one, as `LastingArea` rows the view draws),
  `areas_at`, `areas_holding`, and `who_is_in` / `entered` (who is in an
  area after a move that wasn't before).
- The area bar: a **colour** list (eight colours and Other..., the last one
  picked remembered for the next area; Decision 24) and **Keep on the map**,
  ticked for a pick that lasts (`area_lasts`: a spell that isn't
  Instantaneous, or anything needing Concentration). With it ticked, a
  click with nobody in the area still goes on (Decision 21). The bar's text
  is on a line of its own over its controls (R12).
- The dialog opened again (`conditions_mixin.py`): **Keep the ... on the
  map**, from the bar; it opens with no targets when the area is kept and
  nobody is in it, and Apply then spends the costs, starts the
  concentration and puts the area down, with no rolls. `CustomEffect.area`
  carries the record. With **Source concentrates on it** the area goes on
  the concentration's active spell (`_hold_concentration`), which then
  doesn't end with its conditions; without, on an active spell of its own
  with no concentration and nothing applied (`_hold_area`), lasting the
  spell's time, else the dialog's, else an hour. Only the first of a
  Times repeat keeps it.
- The map (`arena_view.py`): each kept area drawn over the grid in its
  colour, its name in its top-left cell, its edge dashed while its caster
  concentrates; the aiming shading and ring in the bar's colour.
- Reminders (`arena_mixin.py`, Decision 23, replaced by Decision 36 in
  step 24, where they became buttons): a move after which someone is
  in an area they weren't (walked in, or an Emanation moved onto them) says
  "Goblin enters Clover's Spirit Guardians." in the status line; a turn
  starting in one puts "Goblin starts its turn in Clover's Moonbeam." in
  the turn column's reminders (`_turn_start_notes`). Both are GM-only log
  lines. The hover names the areas on a cell ("25 ft. · Moonbeam").

Tests (`tests/test_arena_lasting.py`, `tests/test_combat_ui_arena_lasting.py`):
an aimed area keeps its cells as its caster walks off, an Emanation follows
and leaves its caster out, nothing drawn with the caster off the map, who is
in one by any cell, who entered; which picks are kept by default; Moonbeam
put on empty ground lasting while the mephit concentrates, gone with Ctrl+C
and back with undo; a new concentration ending it; Grease lasting its
minute without concentration; an empty area refused without Keep, applied
without the area when Keep is unticked in the dialog, and no targets with
nothing to keep refused; the bar's colour on the aim and the area, Other...
and cancelling it; Spirit Guardians following its caster and naming who it
reaches; the reminders on walking in and at the turn's start; the hover.

### Step 12: selecting a kept area (2026-11-15)

The user: "Once a spell is cast with a lasting area, I want it to be
clickable / selectable as well. It doesn't count as a "source" of course
but I want to make it clickable so I can cancel the spell, change color,
read what it does, etc."

- `lasting.py`: each record gets a `key` (`area_record`; `area_key` falls
  back to the caster's and the spell's names for one kept without), and
  the `pick` and `about` (its rules text) it was aimed for; `find_area`
  finds the caster and active spell by key; `LastingArea` carries its
  `key` and whether it's `selected`; `time_left_text` ("8 rounds left").
- The view: a click on an empty cell with nothing picked up goes to
  `on_area(key)` when a kept area covers it, the next one on that cell
  when the one selected is there too (`click_cell`), else to `on_cell` as
  before. The area selected is edged brighter.
- The window: `_selected_area` (a key; Decision 25), and the area panel
  over the map: its title (whose, its shape and where, Concentration, time
  left), a colour list (`_set_area_color`, one undo step), Target who's in
  it, End spell (`_remove_active_spell`, as the card's ✕), Close, and
  its rules text (its record's, else the spell named so). A click on an
  empty cell outside it, Close or Esc deselects it; an area that ends
  takes its selection with it.

Tests (`tests/test_arena_lasting.py`, `tests/test_combat_ui_arena_lasting.py`):
keys, finding by key or by names, time left; a real click selecting
Moonbeam with the panel's title and rules text and the source unchanged;
the three ways to deselect; overlapping areas taking turns; the colour
changed and undone a step at a time; Target who's in it with nobody and
with the Pirate; End spell ending concentration, undone; the panel going
when concentration ends.

### Step 13: Dash and Opportunity Attacks (2026-11-15)

The user: "in the combat ui I want to add actions like "dodge", "dash",
"disengage", etc." The standard actions are Use / Cast rows
(Model/Content/StandardActions.py, combat-effects-plan R168); two of them
are about moving, so the map counts them.

- `arena.py`: `DASHES_KEY` ("dashes", how many Dash actions this turn),
  `movement_ft` (the walking speed in use times one plus that), which
  `remaining_ft` and so the reach shaded now use; `reach_ft` (5 ft., a
  stat block's longest "reach N ft.", 10 ft. with a Reach weapon); and
  `opportunity_attackers`: enemies up, not Incapacitated, with their
  Reaction, whose reach the walk's start was in and its end isn't. Only
  the ends are known, so running past an enemy isn't caught (the path the
  cheapest-walk search finds may not be the one taken).
- The window: giving the Dash badge counts a Dash (`_take_dash`, a GM-only
  line), ending it clears them, and a turn starting clears them too; the
  move line and the warning count them ("15 of 60 ft. left this turn
  (Dash)"). A walk on the mover's own turn out of an enemy's reach
  reminds of the Opportunity Attack (status and a GM-only line), or says
  "Disengaged" with the Disengage badge, or notes Flyby. A player's
  `dashes` is kept with a fight in progress (`PLAYER_FIGHT_KEYS`).

Tests: `tests/test_combat_ui_standard_actions.py` (the Dash on the map,
two Dashes, the reminder, Disengage, a used Reaction, a 10-foot reach, a
Dash ending with its badge, Undo), and a continued fight keeping a
player's Dash (`tests/test_combat_ui_reopen_state.py`).

### Step 14: Opportunity Attacks made in the UI (2026-11-15)

The user: "add support for opportunity attack in the combat ui". Step 13
only reminded of them; now each can be made.

- A walk that reminds of Opportunity Attacks (not Disengaged; with Flyby
  the GM judges whether it flew) puts a turn-column button per enemy that
  can react: "Tiger: Opportunity Attack on Kivi (Reaction)"
  (`OpportunityAttack` in Combat/Effects/triggers.py, kept with the hit
  prompts in `_hit_prompts`, so it goes as the next turn starts). One per
  attacker and mover, however often it walks out.
- The button opens Use / Cast with the enemy as the source, the mover as
  the target and one melee attack picked (`opportunity_attack_row`: a
  player's first melee weapon, else its Unarmed Strike; a monster's first
  melee attack among its Actions, one that's melee or ranged if none; else
  nothing, for the GM to pick). The dialog's new `cost` holds the action
  combo on Reaction whatever row is picked, so Apply spends the Reaction,
  not the Action.
- Not done: the button isn't taken back by Undo of the walk (like the hit
  prompts), and an enemy's other buttons stay after it spends its Reaction
  on one (the dialog then says the Reaction is used).

Tests: `tests/test_combat_ui_opportunity_attacks.py`.

### Step 15: moving by what a creature has (2026-11-16)

The user: "make sure rules about moving through cells occupied by
enemies/allies are enforced, plus support for "Halfling Nimbleness" for
example, i.e. features related to moving. Check the rules before
implementing". The Player's Handbook's Moving Around Other Creatures (Q4)
and the Rules Glossary's Difficult Terrain were already counted in
`reachable` and refused on a drop (steps 2 and 6); what was missing was
everything that changes them.

- `Movement` (Model/Content/CombatModifiers.py), one modifier with a field
  per rule: `past_larger` (Halfling Nimbleness), `through_creatures` and
  `through_objects` (Incorporeal Movement: walls and blocking objects are
  Difficult Terrain to it, and a move can end inside one),
  `shares_space` (Swarm: it ends in anyone's space and anyone in its),
  `ignores_difficult` with `after` "Dash" or "Disengage" (Freedom of
  Movement; Speedy, Fairy Trickster's Faerie Trod Trotter), `climbs` (a
  Climb Speed equal to its Speed) and `stands_up_ft` (Hop Up's 5).
- Where it comes from (`movement_rules` in arena.py): a badge's modifiers
  (Freedom of Movement and Spider Climb now have one), an always-on
  feature's new `Feature.movement()` (Halfling Nimbleness, Athlete, Speedy,
  Fairy Trickster, Order's Resilience, Dhampir Spider Climb, Second-Story
  Work, both Tipsy Sways) and a stat block's trait by name
  (`TRAIT_MOVEMENT`: Incorporeal Movement, Swarm).
- `reachable` and `can_pass_through` count them; `can_end_at` replaces
  `fits_at` for where a move ends (`fits_at` stays for placing tokens). A
  move ending inside a wall reminds of Incorporeal Movement's 1d10 Force.
- Standing up (Q8): Prone taken off a creature on its own turn, on the
  map, spends `stand_up_ft` (half its Speed rounded down, or a feature's
  less) as moved, a GM-only line (Decision 27).

Tests: `tests/test_arena_movement.py`, `tests/test_combat_ui_arena_movement.py`.

### Step 16: "within 5 feet" counted from the map (2026-11-16)

The user asked what the arena still misses against the rules (R15); this
is the first of DI-085's rules to count. Prone (Rules Glossary): "An attack
roll against you has Advantage if the attacker is within 5 feet of you.
Otherwise, that attack roll has Disadvantage." Paralyzed and Unconscious:
a hit is a Critical Hit if the attacker is within 5 feet. Today these are
`when` notes ("not counted", `hit_notes` and `_uncounted` in
Combat/Effects/modifiers.py).

- When the attacker and the target are both on the map, `distance_ft`
  settles the `when`: the modifier counts (or doesn't), and the note says
  which ("Tiger is Prone, attacker 5 ft. away: Advantage", "Tiger is
  Paralyzed, attacker 35 ft. away: not a Critical Hit").
- When either is off the map, or there's no attacker, it stays a note, as
  now.

*Built (R16):* the window passes the distance in (`_attacker_distance_ft`,
damage_mixin.py) and Combat/Effects stays Qt-free: `attack_plan(...,
distance_ft=)`, `hit_notes(target, distance_ft)` and `makes_critical_hit`
(modifiers.py). `settled_by_distance` reads a `when` that asks only how far
the attacker is ("the attacker is within N feet of it", "... farther than N
feet") and says whether it holds; any other `when` stays the GM's. All three
attack paths count it: the Custom Effect / Use / Cast dialog (its rows and
its roll), a monster's action button (one target) and the Attack roll field
(the log's "(critical hit)", and a Critical Hit's two death save failures at
0 HP). A counted Critical Hit doubles the dice as a natural 20 does.

Tests: `tests/test_combat_ui_arena_within_5_feet.py`, and the distance cases
in `tests/test_combat_modifiers.py`.

### Step 17: Teleport and Pushed moves (2026-11-16)

Rules Glossary, Teleportation: it "doesn't expend movement unless a rule
tells you otherwise, and teleportation never provokes Opportunity Attacks".
A push (Shove, Thunderwave, Repelling Blast) isn't the creature's own
movement either, so it provokes nothing and spends none (Player's Handbook,
Opportunity Attacks). Today every move on the mover's own turn that could
be walked counts as a walk (`_move_combatant`): its feet and an Opportunity
Attack button.

- A move is a Walk (as now), a Teleport or a Push. A Teleport or a Push
  spends no movement, reminds of no Opportunity Attack and puts up no
  button; it still can't end on a wall or in someone's space (Teleportation:
  "the nearest unoccupied space of your choice"), and still reminds of
  areas and hazards entered.
- The move's GM-only line says which ("Kivi teleports from A7 to D7
  (15 ft.)", "Goblin is pushed from ... ").

*Built:* the keys held as a token is dropped pick the move (`MoveKind` and
`move_kind` in arena_view.py): **Shift** a teleport, **Alt** a push, Shift
winning when both are held; nothing else is a walk. They're read from the
release (a drag's, or the click on the cell for a token picked up), so they
don't clash with Shift and Ctrl on a right click (targeting) or Ctrl+wheel
(zoom), and a left press's modifiers still do nothing. `drop`,
`move_picked` and `on_move` carry the kind; `_move_combatant(char, cell,
kind)` (arena_mixin.py) is still one undo step. A teleport or a push:
the straight distance (`straight_ft`), `moved_ft` untouched, no Speed
warning, no Opportunity Attack line or button, no Prone crawl note; its
line, shown in the status too, is "Kivi teleports from A7 to D7 (15 ft.;
no movement spent)." / "Goblin is pushed from C4 to C5 (5 ft.; no movement
spent)."; areas and hazards entered and Incorporeal Movement's in-a-wall
note as for a walk. One that can't end there (`can_end_at`) is refused, as
a walk is; for a teleport the status says it "appears in the nearest
unoccupied space of your choice" instead, for the GM to drop it on (the
choice is the creature's, so the window doesn't pick one). A walk with no
way there still counts the straight distance as moved (its line unchanged):
it may be a creature squeezing through what the map doesn't know, and a
teleport is now one key away. The reach shaded while a token is held is
still the walk's.

Tests: `tests/test_combat_ui_arena_forced_moves.py` (a walk still provoking
and spending, a teleport and a push spending nothing and provoking nothing,
no Speed warning, one undo step each, refused on someone and on a wall, a
hazard reminded of, the keys, and real Shift-drag and Alt-click).

### Step 18: distances count once the map is in use (2026-11-16)

Decision 29. `ArenaSettings.in_use` (kept in the log's "arena" and in
undo, as "in_use" only when True, so older logs read the same; never in a
map file, `MapDesign.to_dict`) is set by any move or placement on the map
(`_move_combatant`, a walk, a teleport or a push) and by a painted map's
starting cells placing someone (`_place_on_arena`). Saving a map mid-fight
keeps it (`_use_painted_map`). `_attacker_distance_ft` gives None until it's
set, so the rules step 16 counts stay notes on a fight played on the cards.

Tests: `tests/test_combat_ui_arena_within_5_feet.py` (before use, a move
puts it in use and Undo takes it back, painted starts, the log and map
file), `tests/test_combat_ui_map_painter.py` (a fight on a painted map is
in use, and keeps that when continued).

### Step 19: cover from the map (2026-11-16)

Later's first item, the map painter plan's Q2. Rules Glossary, Cover: Half
Cover "+2 bonus to AC and Dexterity saving throws", Three-Quarters Cover +5,
Total Cover "can't be targeted directly", and only the most protective
degree counts. The Player's Handbook's examples: a low wall, large
furniture, a tree trunk, "or a creature, whether that creature is an enemy
or a friend".

*Built (R17):* how it sits on the grid is Decision 30.
`GridShape.crossed(a, b)` (geometry.py) gives the cells a straight line
between two cells' middles crosses, a corner's two cells as one step;
Combat/Arena/cover.py counts cover along it (`line_cover`,
`cover_between`, `cover_from`) as a `CoverReading` ("Half Cover from
Barrel at C4"), and `with_cover` gives the target as a roll reads it: a
copy with the map's cover among its visibility states, so `cover()` and
everything that reads the AC or a save (`armor_bonus`, `armor_in_use`,
`save_plan`) count it unchanged, and the roll's notes on the AC stay on
the real target. The window's `_map_cover` and `_covered` (damage_mixin.py)
give nothing before the map is in use (Decision 29), and every path uses
them: the Use / Cast dialog's AC and save rows, its rolled attacks and
saves (a save from an aimed area's point of origin,
`CustomEffect.cover_origin` from `lasting.record_origin`), a monster's
button, the Attack roll field, and the AC a Shield or Deflect Attacks is
checked against after a hit. The target label names it, and a roll against
Total Cover says "can't be targeted directly" in the status (warned about,
as Decision 19's range is). A pick whose text takes cover away ("no benefit
from Half Cover or Three-Quarters Cover": Sacred Flame) counts only the
map's Total Cover. `area_cells` leaves out what its point of origin
(`point_of_origin`) has no unblocked line to (`reaches`), so a Fireball
doesn't reach round a wall; only the terrain blocks an area.

- Not done: the attacker's own features that ignore cover (Sharpshooter,
  Spell Sniper) aren't read (Q15); height isn't counted, so a creature on
  a ledge is behind a low wall as one on the ground is; the hover doesn't
  show cover, only the target label.

Tests: `tests/test_arena_cover.py`, `tests/test_combat_ui_arena_cover.py`.

### Step 20: reach and range (2026-11-16)

Later's second item. The Player's Handbook: a ranged attack has
Disadvantage past its normal range and can't reach past its long one;
"Ranged Attacks in Close Combat", Disadvantage "if you are within 5 feet of
an enemy who can see you and who doesn't have the Incapacitated condition";
Rules Glossary, Reach: 5 feet, 10 with the Reach property.

*Built (R18):* Combat/Arena/ranges.py: an `AttackRange` (a melee reach, a
ranged normal and long range, or both for a thrown weapon) read from a stat
block's text (`action_range`: "reach 10 ft.", "range 80/320 ft."), a
player's weapon (`weapon_range`, with the Weapons table's ranges as
`WEAPON_RANGES_FT` in Core/Weapons.py, by the weapon's class, so a magic
Longbow has its range) or a spell attack (`spell_attack_range`: a "ranged
spell attack" reaches the spell's range, a "melee spell attack" 5 feet);
`pick_attack_range` (effect_options.py) finds it for a dialog pick.
`check_attack_range` gives a `RangeCheck`: its Disadvantages, counted as
`attack_plan`'s new `extra` sources ("Long range, 90 ft. of 80/320 ft.:
Disadvantage", "Ranged attack within 5 ft. of Goblin"), notes for an enemy
that may not see the attacker (Blinded, or the attacker Invisible), and
warnings past the reach or the long range (Decision 31). The window's
`_range_check` counts it once the map is in use, in the dialog's attack
rows ("AC 15, Disadvantage", "AC 15; past the 5 ft. reach") and rolls, and
a monster's button; a spell aimed at a creature from past its range says
so on the save row (`spell_range_warning`; an area's point is still the
bar's to check, step 10). The dialog's rows are now drawn again once a
pick is made, so they count the pick's range.

- Not done: the Attack roll field doesn't know which attack was rolled, so
  it counts no range; Crossbow Expert's and Sharpshooter's exceptions
  aren't read (Q15); a weapon of the repo's own with Range and no table
  entry has no range known.

Tests: `tests/test_arena_ranges.py`, `tests/test_combat_ui_arena_ranges.py`.

### Step 21: pushes from the Use / Cast dialog (2026-11-18)

Later's third item. Rules Glossary, Unarmed Strike: a Shove's target fails
"or you either push it 5 feet away or cause it to have the Prone
condition"; Thunderwave: "pushed 10 feet away from you"; the Push mastery
(Player's Handbook): "push the creature up to 10 feet straight away from
yourself if it is Large or smaller". Step 17 made a push a move of its own
(Alt as a token is dropped); now a pick that pushes does it on Apply.

*Built (R19):* `CombatPush(feet, up_to, toward, largest)` and
`CombatEffect.push` (Model/Content/CombatEffect.py, kept by `to_dict` /
`from_dict`), carried by `EffectOption.push` and `CustomEffect.push`; a
row's summary says it ("DC 14 STR  pushed 5 ft."). Combat/Arena/pushes.py
works out where each target ends (`push_destination`, Decision 32), which
to move first (`push_order`: a push's farthest, a pull's nearest) and
whether it's too big (`too_big`). `_apply_effect_to_targets`
(conditions_mixin.py) gathers who the push lands on (as its conditions do:
who fails the save, is hit, or everyone with no roll), and the window's
`_push_targets` (arena_mixin.py) moves them through `_relocate`, the move
`_move_combatant` makes, now without its status line so one Apply can
move several and say it once. Each is a Push move: no movement spent, no
Opportunity Attack, areas and hazards entered reminded of, one undo step
with the Apply's damage. What stops one short is a GM-only line ("Tiger
stops after 5 of 10 ft.: a wall or an object."), as is one too big
("Tiger isn't moved by Push: only Large or smaller is."). The dialog
shows **Who it lands on is pushed 10 ft. away from Edmund**, ticked, for a
pick with a push once the map is in use with the source on it (Decision
33); unticked, nobody moves. A row a trigger prompt applies (the Push
mastery after a hit) pushes as it applies.

Content: Thunderwave (`CombatPush(10)`, its note shortened), the Push
mastery (`CombatPush(10, up_to=True, largest=Large)`, its "move it at the
table" note gone; its row only moves, so the dialog takes that as
something to apply), and the Unarmed Strike's Shove as two rows under
every player's Unarmed Strike, "Unarmed Strike: Shove (push)" and "...
(Prone)" (Model/Content/UnarmedStrikeEffects.py: a Strength save, DC 8 +
the Unarmed Strike's ability modifier + Proficiency Bonus, so a Monk's
Martial Arts Dexterity counts). The combat-effects skill's rubric has
`push`.

- Not done: the other pushes and pulls in content are still text (DI-095,
  for the spell-combat-effects and feature-combat-effects agents); a
  monster can't Shove from its picker (stat blocks don't list it); the
  Shove's "it chooses" Strength or Dexterity is the GM's to switch; "up
  to" pushes the whole way (Decision 33); a push off a ledge doesn't count
  falling; Grapple isn't a row yet (Later 4; step 22 added it).

Tests: `tests/test_arena_pushes.py`, `tests/test_combat_ui_arena_pushes.py`;
the picker rows' goldens (`tests/test_picker_rows.py`) have the Shove rows.

### Step 22: grapples on the map (2026-11-18)

Later's fourth item. Rules Glossary, Grappled: "Movable. The grappler can
drag or carry you when it moves, but every foot of movement costs it 1
extra foot unless you are Tiny or two or more sizes smaller than it."
Grappling: "The condition also ends if the grappler has the Incapacitated
condition or if the distance between the Grappled target and the grappler
exceeds the grapple's range. In addition, the grappler can release the
target at any time (no action required)."

*Built (R20):* who grapples whom is on the grappled creature,
`char["grappled_by"] = "Edmund"` (`GRAPPLER_KEY` in arena.py, in
`PLAYER_FIGHT_KEYS` for a player), set by `_add_condition_to` whenever
Grappled is given with a source (a monster's grapple rider, the dialog, the
new row) and dropped when Grappled comes off. arena.py reads it
(`grappler_of`, `grappled_by`, `drag_costs_extra`, `drags_at_a_cost`,
`grapple_range_ft`), and `reachable` adds the drag's extra foot a foot to
every step, as it adds crawling's, so the shaded reach and the walk's cost
count it. Combat/Arena/grapples.py: `dragged_to`, where the held creature
goes (Decision 34, with geometry's new `GridShape.shifted`), and
`stretched`, the grapples a move has pulled apart. In the window, a walk
(`_relocate`) drags each creature its walker holds as a new `MoveKind.DRAG`
("Tiger is dragged from G6 to E6 (10 ft.; no movement spent).", no
movement of its own, no Opportunity Attack), before the walk is measured
for Opportunity Attacks so the dragged one doesn't get one on its
grappler, and the status says "Edmund drags Tiger: each foot of the walk
costs 1 extra foot." After any move or push, `_end_stretched_grapples`
ends each grapple past its range ("Edmund's grapple on Tiger ends: 25 ft.
apart, past its 5 ft. range."): a teleporting grappler, a pushed creature,
a creature the GM moves away. A grappler given an incapacitating
condition lets go of everyone it holds. Taking Grappled off by hand is the
grappler releasing it. The Unarmed Strike has a third row, "Unarmed
Strike: Grapple" (Model/Content/UnarmedStrikeEffects.py: the Shove's DC,
Grappled, the escape DC in its note).

- Not done: the Grappled creature's "Disadvantage on attack rolls against
  any target other than the grappler" is still a note, though the
  grappler is known now (it's the attacker's own modifier, which no
  `when` settles yet); only the grappler's reach is a grapple's range
  (Decision 34); a grappler can't choose to walk away without dragging
  except by releasing first; "one grapple per hand" isn't counted; a
  dragged creature carried up a climb costs nothing more.

Tests: `tests/test_arena_grapples.py`, `tests/test_combat_ui_arena_grapples.py`;
the picker rows' goldens have the Grapple row.

### Step 23: the path walked (2026-11-18)

Later's fifth item. Rules Glossary, Opportunity Attacks: "when a creature
that you can see leaves your reach". Polearm Master (Player's Handbook,
2024), Reactive Strike: "While you're holding a Quarterstaff, a Spear, or a
weapon that has the Heavy and Reach properties, you can take a Reaction to
make one melee attack against a creature that enters the reach you have
with that weapon." The 2024 Sentinel has no entering-reach rule (its
Guardian answers Disengage and hits, its Halt is a row already), so it
isn't here. Step 13 knew only a walk's two ends; step 14 left Undo of a
walk's buttons, and an attacker's other buttons once its Reaction is
spent, as Not done.

*Built (R21):* `walk_path` (arena.py) gives the cells of the cheapest walk
to the cell clicked, from the search `reachable` makes (now
`_walk_search`, which keeps each cell's parent). `opportunity_attackers`
takes that `path` and finds whoever had the walker in reach at one cell and
not at the next; `reactive_strikers` whoever has Polearm Master
(`_feature_objects`) and a polearm (`_polearm_reach_ft`: a Quarterstaff or
a Spear by class, so a magic Spear counts and a Javelin, of Spear's
family, doesn't, or a Heavy Reach weapon; 10 ft. with Reach) and had the
walker outside that reach at one cell and inside at the next. The window's
`_relocate` works out the path before the walk and
`_opportunity_attack_reminders` uses it: an Opportunity Attack button as
before, now also for a walk past someone, and a Reactive Strike button
("Edmund: Reactive Strike on Tiger (Reaction)", `OpportunityAttack.name`,
Disengaged or not), with a GM-only line ("Tiger enters Edmund's reach:
Reactive Strike (Polearm Master), a Reaction."). A creature its walker
drags gets neither. `UndoPoint` keeps the turn column's hit prompts, so
Ctrl+Z takes back the buttons a walk or a hit set off, and `_undo_last`
redraws them. Spending a Reaction (`_add_action_use`) takes away its
spender's other Opportunity Attack and Reactive Strike buttons.

- Not done: the path is the cheapest one, not the one the GM has in mind
  (a walk round the other side of a pillar is the GM's to judge, as the
  status names who it passed); Reactive Strike counts walks only, not a
  push or a teleport into the reach; a monster's polearm and its "holding"
  aren't read (stat blocks don't name feats); the buttons still don't
  check that the attacker can see the walker.

Tests: `tests/test_arena_paths.py`, `tests/test_combat_ui_arena_paths.py`;
`tests/test_combat_ui_standard_actions.py`'s walk round a corner now
provokes (Decision 35).

### Step 24: areas that stay, acting (2026-11-18)

Later's sixth item (Q12, Q13), the user's request: "A creature entering a
kept area, or starting its turn in one, gets a turn-column button (like
the Opportunity Attack prompts) that opens Use / Cast on the area's pick
with that creature targeted, instead of today's reminder line", and "a
Move button on the area panel for Moonbeam and Flaming Sphere: aim it
again in the area bar, keeping its time and concentration". Walls left
for later.

The spells' own wording (Player's Handbook 2024, as their classes have
it), read first: Moonbeam, "A creature also makes this save when the
spell's area moves into its space and when it enters the spell's area or
ends its turn there. A creature makes this save only once per turn", and
"you can take a Magic action on later turns to move the Cylinder up to
60 feet"; Spirit Guardians, "whenever the Emanation enters a creature's
space and whenever a creature enters the Emanation or ends its turn
there"; Flaming Sphere, "Any creature that ends its turn within 5 feet of
the sphere makes a Dexterity saving throw", "As a Bonus Action, you can
move the sphere up to 30 feet", "If you move the sphere into a creature's
space, that creature makes the save"; Web, "The first time a creature
enters the webs on a turn or starts its turn there". Most 2024 areas act
as a turn *ends*, not as one starts, so the moment comes from the text
(R22, Decision 36). The Rules Glossary's area entries (Emanation,
Cylinder, Sphere) say nothing of when an area acts.

*Built (R22):* `lasting.py`: `area_timing(text)`, when a kept area acts
(ENTERS, MOVED_ONTO, STARTS, ENDS, read from its rules text; one that says
none, ENTERS and STARTS, as the reminders were); `move_rule(text)`, how
far it moves and what that costs (`MoveRule`: Moonbeam's 60 ft. and an
Action, Flaming Sphere's 30 ft. and a Bonus Action); and `AreaPrompt`,
the turn-column button ("Clover's Moonbeam on Goblin (entered it)", "...
(ended its turn in it)"). The window (`arena_mixin.py`): a walk into an
area gives the walker ENTERS, and an Emanation brought onto someone by its
caster's move gives them MOVED_ONTO (`_area_entered`, kept with the hit
prompts, so Undo of the walk takes it back and the next turn clears it);
`_remind_lasting_areas` gives STARTS to whoever's turn starts in one and
ENDS to whoever's just ended in one (shown in the next turn's column, as
a turn-end trigger's button is), each with a GM-only log line ("Goblin
ends its turn in Clover's Moonbeam."). One button per area and creature
at a time. Pressed (`_use_area_prompt`), it opens Use / Cast with the
caster as the source, the creature targeted and the area's row picked
(`area_effect_row`: a row of the pick's that spends nothing, "Spirit
Guardians: damage", else the pick itself), through the dialog's new
`kept_area`: no slot, action or concentration (the cost widgets off, "...
acting again: its cast is spent already, so this costs nothing, at level
4."), damage at the slot it was cast with (the record's new
`slot_level`), cover from where the area was aimed, and what it gives held
by the area's concentration (`CustomEffect.from_area`,
`_hold_with_area`: Web's Restrained ends with it). A badge's turn trigger
of the same name as a kept area of its caster's (Spirit Guardians' "if it
ends its turn in the Emanation") gives way to the area once the map is in
use and the creature is on it (`_kept_area_answers`), so the button comes
only for whoever is in it. Hazards stay turn-column reminders.

The area panel's **Move** (not for an area around its caster): the area
bar aims it again from where it is (`_move_selected_area`; its shape
fixed, Keep and the colour hidden, "Moves 35 ft., up to 60 ft.", "past
its 60 ft.!" past it), a click puts it there (`_move_area`, one undo
step: its key, time, concentration and colour kept, "Clover's Moonbeam
moves from K6 to O9 (35 ft.)." GM-only), spending what its text says
from its caster, asked first when that's used already. Whoever it's
moved onto gets its MOVED_ONTO button. Esc, a right click or G leaves it
where it was, with no dialog.

- Not done: "only once per turn" is one button at a time per area and
  creature, not counted across the turn (a creature that entered and used
  its button gets another as its turn ends there); Spirit Guardians'
  creatures designated "to be unaffected" aren't known, so allies in it
  get a button too; Flaming Sphere's "stops moving for the turn" and its
  "over barriers up to 5 feet tall" are the GM's; its area is read as 20
  feet (DI-096, fixed in step 25); walls (Later 6, step 25).

Tests: `tests/test_arena_lasting.py` (the timing and move readers on the
spells' wording, the button's text), `tests/test_combat_ui_arena_area_prompts.py`
(Moonbeam's button costing nothing, Undo taking it back, its turn-end and
not turn-start, Web's turn start and its Restrained held by concentration,
an area that ended, an upcast one, Spirit Guardians through its area with
its damage row, an Emanation teleported onto someone, Move with its
Action, past its reach and cancelled, Flaming Sphere's Bonus Action, no
Move around a caster); `tests/test_combat_ui_arena_lasting.py`'s
reminders test now has Moonbeam's turn start as a log line only.

### Step 25: walls (2026-11-18)

The rest of Later's sixth item, the user's request: "A kept area can be a
wall: Wall of Fire (a straight wall up to 60 feet long, or a ring up to 20
feet across), Wall of Force, Blade Barrier, Wall of Thorns. A wall isn't
one of the six shapes, so it needs a shape of its own in
Combat/Arena/areas.py, aimed in the area bar by two clicks (its two ends,
or a ring's middle)", "A wall the text calls a barrier (Wall of Force)
blocks movement and gives Total Cover while it lasts, the same as a painted
wall: the terrain the rules read should count it, and it goes when the
spell ends or Undo takes it back. Don't write it into the painted map's
file", Wall of Fire's damaging side picked by the GM as it's put down, and
DI-096.

Read first: Rules Glossary, Area of Effect: an area "typically has one of
six shapes" and a point of origin, and a location is left out when "all
straight lines extending from the point of origin" to it are blocked by
Total Cover; Cover: Total Cover "can't be targeted directly". The spells
(Player's Handbook 2024, their classes): Wall of Fire, "up to 60 feet
long, 20 feet high, and 1 foot thick, or a ringed wall up to 20 feet in
diameter", "One side of the wall, selected by you when you cast this
spell, deals 5d8 Fire damage to each creature that ends its turn within 10
feet of that side or inside the wall. A creature takes the same damage
when it enters the wall for the first time on a turn or ends its turn
there"; Wall of Force, "a hemispherical dome or a globe with a radius of
up to 10 feet, or ... a flat surface made up of ten 10-foot-by-10-foot
panels", "as a horizontal or vertical barrier", "Nothing can physically
pass through the wall"; Blade Barrier, "a straight wall up to 100 feet
long ... and 5 feet thick, or a ringed wall up to 60 feet in diameter",
"The wall provides Three-Quarters Cover, and its space is Difficult
Terrain"; Wall of Thorns, "up to 60 feet long ... and 5 feet thick or a
circle that has a 20-foot diameter", "For every 1 foot a creature moves
through the wall, it must spend 4 feet of movement".

*Built (R23):* areas.py: `AreaShape.WALL` and `AreaOfEffect.ring`; a Wall
is read from "wall ... up to N feet long" (with its "N feet thick") and
Wall of Force's "ten 10-foot-by-10-foot panels" (`parse_area`), its ring
from "a ringed wall up to N feet in diameter", "a circle that has an
N-foot diameter" or a globe's radius (`wall_ring_ft`), and a damaging
side's reach from "One side of the wall ... within N feet of that side"
(`damaging_side_ft`). Its cells (`wall_cells`, Decision 38), where a wall
cut short by its length really ends (`wall_end`), which side of it a cell
is on (`side_of`; `side_name` "east", "inside") and the cells within
reach of a side (`side_cells`). `area_cells(..., end)` takes a Wall's
second end, and leaves a Wall uncut by Total Cover (it has no point of
origin). lasting.py: a wall's record keeps its "end", "ring", the "side"
picked and its "side_cells"; `wall_terrain` reads what it is as terrain
(Decision 39) into its "terrain", and `with_kept_walls` lays each kept
wall's terrain over the painted terrain as a copy; `LastingArea.side`,
`areas_beside` and `AreaPrompt.beside` ("... (ended its turn by its
damaging side)"); `record_origin` of a wall is its own cells, so nothing
covers who's in it.

The window (`arena_mixin.py`): `_map_settings`, the map as the rules read
it (with_kept_walls), is what every rule reads: the reach shaded and a
walk's cost and path, where a move may end, pushes, drags and a grapple's
range, Opportunity Attacks and Reactive Strike, the cover of attacks and
saves and the range check (`damage_mixin.py`), an area aimed or kept
(a Fireball doesn't spread past Wall of Force, an Emanation stops at it),
who's in a kept area, new tokens and summons placed. What's written
(`in_use`, the log's "arena", the Map Painter) stays `arena_settings`, so
the wall is never saved into the painted map, and it goes with its active
spell: the spell ending, Ctrl+C, the ✕, Undo. The area bar has **Ring**
for a Wall (its size becoming the ring its text offers, Wall of Fire's
20 feet across, and back), and the clicks go: one end ("click one end."),
the other ("click its other end (20 ft. long)."), or a ring's middle; then,
for Wall of Fire, the side ("click the side that deals damage (the east
side): within 10 ft. of it.", the side's cells shaded with the wall; a
click on the wall's line is refused). The dialog opens again as for any
kept area ("Keep the 60-foot-long Wall, its east side dealing damage, on
the map"). The map draws a wall's damaging side fainter, the hover names
it ("Wall of Fire's damaging side"), and the area panel says where it runs
("from G1 to G12"), what it is ("blocks movement, Total Cover") and which
side deals damage, with no Move (Decision 41). A turn ending by the side
gets the wall's button and a GM-only line ("Pirate ends its turn by
Clover's Wall of Fire's damaging side."); entering the wall or ending a
turn in it is step 24's.

DI-096: `parse_area` skips a radius after "Light in a" or "Light for", and
reads "within N feet of the sphere" as an N-foot Sphere, so Flaming Sphere
is its cell and the four beside it.

- Not done: Wall of Force's dome or globe is a ring on the grid and its
  panels one straight wall (ten panels in any contiguous shape, or a
  horizontal one, aren't drawn); a wall that appears through a creature's
  space doesn't push it out (Wall of Force: "pushed to one side"; the GM
  moves it, step 17's Alt); Wall of Fire's side opens the cast's own
  row, with the Dexterity save its appearing has and the side's damage
  doesn't, for the GM to switch off; the other walls' terrain (Wall of Stone, Wall of
  Ice, Wall of Thorns' 4 feet a foot, opaque walls blocking sight) isn't
  read (DI-097); a wall is one cell thick whatever its text says (Tsunami's
  50 feet); its height isn't counted (a flier going over it is the GM's,
  as flying is Later 7); "only once per turn" is as step 24 left it.

Tests: `tests/test_arena_walls.py` (each wall's reading, its ring and
side, Flaming Sphere's and a light's readings, a wall's cells and length,
a diagonal one shutting a corner in, a ring, a painted wall not cutting
one, sides and their names, the damaging side's reach, who ends a turn by
it, a wall's cover origin, each wall's terrain, Wall of Force blocking,
covering and stopping a Fireball without changing the map, what's painted
under a wall staying), `tests/test_combat_ui_arena_walls.py` (the two
clicks and the bar's text, Wall of Force's reach, cover, target label and
a walk that can't get round, the saved fight with no wall in its terrain,
Ctrl+C and Undo, Wall of Fire's third click with a click on its line
refused, the side kept, the panel's text and no Move, the turn-end button
by the side and entering the wall, a ring by its middle holding the Pirate
in).

### Step 26: other speeds, and water swum (2026-11-18)

Later's seventh and eighth items (Q7, the map painter plan's Q4), taken
together: water's cost depends on the speed used. Rules Glossary, Speed:
"If you have more than one speed, choose which one to use when you move;
you can switch between the speeds during your move. Whenever you switch,
subtract the distance already moved from the new speed", and every special
speed changes as the Speed does; Flying: "you fall if you have the
Incapacitated or Prone condition or your Fly Speed is reduced to 0. You can
stay aloft in those circumstances if you can hover"; Falling: "1d6
Bludgeoning damage at the end of the fall for every 10 feet it fell, to a
maximum of 20d6", Prone "unless it avoids taking any damage from the
fall"; Swimming: "each foot of movement costs 1 extra foot (2 extra feet in
Difficult Terrain). You ignore this extra cost if you have a Swim Speed and
use it to swim"; Climb Speed, Burrow Speed ("through sand, earth, mud, or
ice", not "solid rock"); Dash: "The increase equals your Speed". Fly: "the
target gains a Fly Speed of 60 feet and can hover. When the spell ends, the
target falls if it is still aloft".

*Built (R24):* Combat/Arena/speeds.py (new, Qt-free): `stored_speeds` and
`speeds` (in use, through `speed_in_use`), from a stat block's Speed, Fly
and Climb fields, its speed text ("swim 40 ft.", "burrow 20 ft.; swim 30
ft.") and any Movement (`movements`, moved here from arena.py, which still
exports it); `hovers` ("hover" in the speed text, or a Movement's);
`mode_of`, the speed it moves by (`char["moving_by"]`, none for its Speed,
a creature that only flies by its Fly Speed); `altitude_ft`
(`char["altitude_ft"]`, while it's set to fly); `fall_reason` and
`falling_dice`. Movement (Model/Content/CombatModifiers.py) gained
`fly_ft`, `flies` (equal to its Speed), `swim_ft`, `swims` and `hovers`,
and the Fly spell its badge: `Movement(fly_ft=60, hovers=True)`, one
target and one more a slot level, its falling in a note. arena.py:
`movement_ft` is the speed moved by plus its Speed a Dash, so
`remaining_ft` counts what it moved against the new speed (the
glossary's fly 10, walk 10, fly 20); `ArenaSettings.elevation` (the
ground's height and its altitude) in `distance_ft` and
`distance_to_cell_ft`, so the hover, reach, range and Opportunity
Attacks count how high it is; `_walk_search` by its speed (Decision 43),
water swum (Decision 45). terrain.py: water isn't `difficult` any more
but `water`, "Water (swimming)".

The window: the **speed bar** over the map (`_build_speed_bar`), for a
source on the map with more than one speed, or one aloft: "Giant Eagle
moves by: [Walk 10 ft. | Fly 80 ft.]" and, flying, **Altitude** ("30 ft.
up"). Picking a speed (`_set_move_mode`, one undo step, a GM-only line
"Giant Eagle moves by its Fly Speed now (80 ft.; 80 ft. left this
turn).") is refused while it's aloft ("bring it down to 0 ft. to land
first"); an altitude (`_set_altitude`, one undo step) spends its movement
("Giant Eagle flies up 30 ft. (to 30 ft. up; 50 ft. left this turn).",
warned past it). A walk's line has the speed's verb and name ("flies from
C6 to M6 (50 ft.; 30 of 80 ft. left this turn)", "moved 90 ft., Fly Speed
80 ft."). The token shows "↑30 ft." over it. `_land_fallers`, run as
`_refresh_views` starts, lands whoever can't stay aloft: its altitude
gone, back to its Speed, with the status and a GM-only line ("Giant Eagle
falls 30 ft. (Prone): 3d6 Bludgeoning damage, and it lands Prone unless it
takes none (Falling)."), so what made it fall and the fall are one undo
step (Decision 46). A player keeps `moving_by` and `altitude_ft` in the
log (`PLAYER_FIGHT_KEYS`).

- Not done: a walk is by one speed (to fly part of the way and walk the
  rest, switch between two walks); flying up or down isn't a walk, so
  rising out of a reach reminds of no Opportunity Attack; walls and
  objects block a flyer whatever their height (the map knows none), and
  height isn't counted in areas or cover (Later 12); a fall's damage and
  Prone are the GM's to apply, and falling into water isn't halved; the
  other features and spells that give a Fly or Swim Speed are text (DI-098,
  "twice your Speed" needs a field); swimming has no depth (a creature
  under water is as one on it); a Climb Speed climbs free whichever speed
  is used, as before, and climbing a wall isn't possible; rough water's
  Athletics check is the GM's.

Tests: `tests/test_arena_speeds.py` (speeds from fields, speed text and
Movements, hover, "equal to its Speed", Grappled making each 0, the speed
moved by, the glossary's switching example, a Dash, flying's, swimming's
and burrowing's costs, water swum with an enemy in it, staying in the
water, altitude in a distance, each reason to fall and hovering, Fly
gone, the dice), `tests/test_combat_ui_arena_speeds.py` (the bar's
speeds and none for one speed, a flight's reach, line and Undo, flying up
spending movement and counting into the distance and the token, landing
before walking, a Prone eagle falling once, the Fly spell's Fly Speed and
hover, its end dropping Rowan and Undo putting it back).

### Step 27: distances in triggers (2026-11-18)

Later's ninth item (DI-085; combat-effects plan Q63). Step 16 counted the
conditions' "within 5 feet", steps 20 and 23 reach, range and Opportunity
Attacks, step 24 Spirit Guardians' Emanation through its kept area; what
was left was the triggers. Read first, every `when` in content that names
a distance: Fire Shield's `WhenHit(when="it's within 5 feet of you")`
("Whenever a creature within 5 feet of you hits you with a melee attack
roll"), Hellish Rebuke's "you can see it within 60 feet", Warding Flare's
"you can see it within 30 feet of you", Storm's Thunder's "it is within 60
feet"; and Dark One's Blessing's "You also gain this benefit if someone
else reduces an enemy within 10 feet of you to 0 Hit Points". The one other
(a homebrew monster's "within 5 feet of the manifestation") is a distance
to something that isn't on the map. No turn trigger (AtTurnStart,
AtTurnEnd) has one.

*Built (R25):* Combat/Effects/triggers.py: `settle_when(when, feet)` reads
a `when` ending in "within N feet (of you)" (Decision 47): farther, it
doesn't fire; within, what's before the distance is all that's asked
("you can see it", said with the distance: "if you can see it (25 ft.
away)"), and nothing when that's all it said. Every firing path takes a
`distance_of(owner, other)` (`outcome_firings`, `hit_by_firings`,
`attack_roll_firings`, `badge_hit_firings`), which the window gives as
`_attacker_distance_ft` (None before the map is in use, Decision 29, or
with either off it: asked as before). `CombatTrigger.others_within_ft`
(REDUCES_TO_ZERO only): `outcome_firings` given the fight's creatures
(`others`) also fires such a row of each of them for a knockout another
creature makes of one of their enemies (Decision 48). Dark One's Blessing
has `others_within_ft=10`, its "pick it then" note gone. The combat-effects
skill says how to write a distance in a `when`.

- Not done: a turn trigger's `when` isn't read for a distance (none has
  one); "you can see it" is still the GM's (Later 10, light and senses);
  a distance to something that isn't a creature (the manifestation, a
  point) stays a question.

Tests: `tests/test_arena_trigger_distances.py` (settle_when's readings,
Fire Shield from 5 ft. by itself, from 10 not at all, off the map asked;
Hellish Rebuke's "can see" with the distance, past 60 feet, off the map;
Dark One's Blessing for another's knockout within 10, past it, off the
map, and the Warlock's own at any distance; the gate's checks),
`tests/test_combat_ui_arena_trigger_distances.py` (the Ogre's Greatclub
from beside Edmund burning it without a question, and from 10 ft. not);
`tests/test_hit_point_triggers.py`'s Dark One's Blessing trigger.

### Step 28: light and senses (2026-11-18)

Later's tenth item (the map painter plan's Q5), with DI-068. Read first,
the Rules Glossary's Vision and Senses: Darkness is Heavily Obscured, and
"You have the Blinded condition while trying to see something in a
Heavily Obscured space"; Darkvision sees in Darkness within its range "as
if it were Dim Light"; Blindsight sees within its range "anything that
isn't behind Total Cover", Blinded, in Darkness or Invisible; Truesight
sees "in normal and magical Darkness" and Invisible creatures; Invisible:
"If a creature can somehow see you, you don't gain this benefit against
that creature"; Tremorsense "doesn't count as a form of sight". And the
spells' own words: Darkness ("magical Darkness ... Darkvision can't see
through it"), Fog Cloud, Stinking Cloud, Sleet Storm, Cloudkill ("Heavily
Obscured"), Hunger of Hadar ("a 20-foot-radius Sphere of Darkness"), the
Darkvision spell ("Darkvision with a range of 150 feet"), See Invisibility,
Faerie Fire ("can't benefit from the Invisible condition, and attack rolls
against it have Advantage if the attacker can see it"). The Invisibility
spell already gave the condition; DI-068 was the GM's visibility list.

*Built (R26):* `Combat/Effects/sight.py`'s `Seen` (can: True, False or
None; why; obscured) and `Sight` (each of an attack's two). The Qt-free
`Combat/Arena/senses.py`: `sees(viewer, other, chars, settings)` by the
rules above (Decisions 50, 53), `sense_ranges` (a stat block's senses
text, a sheet's Senses, badges' `Vision`), `area_obscures` (a kept area's
text: DEEP_DARKNESS, DARKNESS, FOG), `obscured_cells`.
Model/Content/CombatModifiers.py: `Vision(darkvision_ft, blindsight_ft,
truesight_ft, sees_invisible, outlined)`, given by the Darkvision spell's
new effect, See Invisibility's badge and Faerie Fire's (with its
`AttacksAgainst(Advantage, when="the attacker can see it")`, which was a
note). Combat/Effects/modifiers.py: `held_conditions` reads the Invisible
visibility state as the condition (DI-068); `attack_plan(..., sight=)`
settles the `when`s that ask who sees whom and counts Heavily Obscured as
Blinded's (Decision 51). Combat/Arena/ranges.py: `RangeCheck.sight`
(`attack_sight`), so every attack row and roll that reads the map's range
gets it; an enemy within 5 feet that doesn't see a ranged attacker imposes
nothing and says why. Combat/Effects/triggers.py: `sees_of`, beside
`distance_of`, settles "you can see it" (Decision 52). The window:
`_sees` and `_sees_of` (DamageMixin, None before the map is in use), the
target label's "Pirate can't see it: Darkness at B1" or "sees it by
Darkvision 60 ft.".

- Not done: light that spells and carried sources give over painted
  Darkness (DI-099); Devil's Sight (DI-100); a spell that needs its target
  seen isn't warned about (Invisible's "Concealed", DI-101); the GM's
  Heavily Obscured and Darkness visibility states (DI-102); Lightly
  Obscured (Perception only) and whether eyes see past Total Cover stay
  the GM's (Decision 50).

Tests: `tests/test_arena_senses.py` (reading a kept area's text and the
senses; who sees whom off the map, in the light, in painted Darkness with
and without Darkvision in range, partly lit, from the dark, in the Darkness
spell, in a fog, Blinded with and without Blindsight and past Total Cover,
blind beyond its radius, the Invisible state as the condition, Truesight,
Blindsight and See Invisibility, Faerie Fire; Invisible's whens settled
both ways, the dark's Blinded Advantage and Disadvantage, both cancelling,
Blinded not counted twice, Faerie Fire's Advantage, Dodge; the close-combat
rule; Hellish Rebuke's "you can see it"),
`tests/test_combat_ui_arena_senses.py` (the Pirate's claws on the Tiger in
the light, in Darkness, Invisible, and before the map is in use);
`tests/test_arena_ranges.py`'s Blinded enemy close by, now settled.

### Later (not scheduled)

In order of relevance (R15, the user, 2026-11-16: "add your suggestions
(in order of relevancy) to the plan"). Each is a step of its own when it's
picked up. The first six, cover, range, pushes, grapples, the path
walked and areas acting, were steps 19 to 24, and the sixth's walls step
25; the seventh and eighth, speeds and water, step 26; the ninth,
distances in triggers, step 27; the tenth, light and senses, step 28.

3. *(Step 21.)* **Shove's push** and the other pushes, moved on Apply.
   What's left is content (DI-095).
4. *(Step 22.)* **Grappling moves the Grappled creature**, and the grapple
   ends past its range.
5. *(Step 23.)* **The path walked kept**: Opportunity Attacks along it,
   Polearm Master's Reactive Strike, Undo of the buttons, a spent Reaction
   taking the rest.
6. *(Steps 24 and 25.)* **Areas that stay, acting** (Q12, Q13): a
   turn-column button when one acts, the area panel's **Move**; and
   **walls**, a shape of their own aimed by two clicks, Wall of Force
   blocking movement and giving Total Cover while it lasts, Wall of Fire's
   damaging side. What's left is the other walls' terrain (DI-097).
7. *(Step 26.)* **Other speeds** (Q7, the map painter plan's Q4): the
   speed chosen, switching, altitude, falling. What's left is content
   (DI-098) and a walk by two speeds at once.
8. *(Step 26.)* **Water is swimming, not Difficult Terrain** (Rules
   Glossary, Swimming).
9. *(Step 27.)* **Distance in triggers and auras** (DI-085): Fire
   Shield's "within 5 feet", Hellish Rebuke's 60, Dark One's Blessing's 10
   for another's knockout (combat-effects-plan Q63); Spirit Guardians'
   aura is its kept area since step 24. Each still asks when either
   creature is off the map.
10. *(Step 28.)* **Light and senses counted** (the map painter plan's
    Q5): Heavily Obscured as Blinded for sight there, Darkvision,
    Blindsight, Truesight, each from the viewer's senses; DI-068 fixed.
    What's left is light that spells give (DI-099), Devil's Sight
    (DI-100), targets that must be seen (DI-101) and the GM's obscured
    visibility states (DI-102).
11. **The map on the Player Screen and the player link**, from the same
    token rows, hidden monsters left out the way `player_view_rows` leaves
    them out; kept areas on it (hidden with a hidden caster); later a fog
    of war (the map painter plan's Q1).
12. **Areas count height** (the map painter plan's Q3): each cell's height
    into an area's reach, as distances already count it (Decision 18).
13. **Doors and jumps** (the map painter plan's Q6 and Q8): a door opened or
    closed in a fight; a Long or High Jump (Rules Glossary, Jumping) over a
    gap or down a drop instead of climbing; falling damage stays the Custom
    Effect's.
14. **More distance rules**, each a `DistanceRule` and a line in `RULES`:
    Chebyshev and 5-10-5 on squares, Euclidean (rounded to the nearest 5
    ft.), hexagons (a `HexGrid` shape with axial cells and its rule;
    footprints of Large+ creatures on hexes need their own decision). A
    combo box in the map settings picks one, with the cell's feet.

Built from this list already: the map settings dialog and terrain, as the
Map Painter ([map-painter-plan.md](map-painter-plan.md), 2026-11-15); the
conditions' "within 5 feet" (step 16); moves that aren't walks (step 17);
cover (step 19), range (step 20), pushes (step 21), grapples (step 22),
the path walked (step 23), areas acting (step 24), walls (step 25),
other speeds and water (step 26), distances in triggers (step 27) and
light and senses (step 28), its first ten items.

## Decisions

From the user (2026-11-13, the request that started this plan):

1. **Manhattan first, the others later.** The design must make hexagon,
   Euclidean and other rules possible without changing the view or the
   state.
2. **Both views, one switch.** The Arena view replaces only the cards' area;
   selection, the control panel, the turn column and undo are shared.

Taken in the plan (2026-11-13), for the user to overrule:

3. **Grid shape and distance rule are separate interfaces**, `GridShape` and
   `DistanceRule`, with rules registered in `RULES`. Nothing outside
   `geometry.py` does arithmetic on cell coordinates. This is what makes
   Decision 1 hold.
4. **A position lives on the combatant as plain JSON** (`"position"`,
   `"moved_ft"`), so undo and the saved fight state carry it with no new
   code, as every other per-fight value does.
5. **The map stays out of the player log.** Positions end with the fight,
   so moves replay nothing and the party's journal doesn't grow with them.
6. **The view draws token rows, not combatant dicts**, made by one function,
   so the drawing has no rules in it and a Player Screen map can reuse them.
7. **The arena's rules are Qt-free, in `Combat/Arena/`**, tested without a
   window.
8. **Distance between two creatures is between their nearest cells**, so a
   Large creature is 5 ft. from anything next to any of its four cells, as
   on a printed map.
9. **The toggle exists only during combat, on G and a turn-column button**,
   and the view picked is remembered in the settings. (Where it's kept:
   replaced by 10.)

Taken while building (2026-11-13), for the user to overrule:

10. **The view last used is window state, not a setting** (R5): it's kept in
    the settings store under `view/arena`, and the Settings dialog doesn't
    list it. G and the button are how it's changed. Replaces the "in the
    settings" of Decision 9.

From the user (2026-11-14, after trying it):

11. **An encounter's allies start on the party's side**, as Greypaw and
    Harat do in Wrath of Durmor: blue, on the left (R9, DI-092).
12. **Click a combatant, then a cell, to move it**, besides dragging. Replaces
    "with a source selected, click an empty cell" of step 6's Moving.
13. **A move's log line says who moved from where to where, and how much
    movement is left**: "Clover moves from A7 to C8 (15 ft.; 15 of 30 ft.
    left this turn)." Replaces Q3's "Goblin moves 15 ft.".

Taken while building (2026-11-14), for the user to overrule:

14. **A click on an empty cell with nothing picked up moves nobody**, not
    even the source: with "Source follows the turn" on, the source is
    whoever's turn it is, and a stray click would move them. It says
    "Click a combatant, then the cell it moves to." instead.
15. **Cells are named by column letters and row numbers** ("C7", past Z
    "AA1"), as the user's example ("from A1 to B2") reads, and the map's
    top edge is lettered to match. The names come from the grid shape
    (`labels`, `cell_name`), so a hex grid names its own (Decision 3).
16. *Replaced by 18.* **How an area sits on the grid** (in the plan, for
    the user to overrule; step 10). A cell is in an area when the area covers its
    middle, and a creature is in it when any of its cells is. A Sphere or
    Cylinder is centred on the cell aimed at and its radius is counted by
    the map's distance rule, so with Manhattan it is a diamond: a creature
    the hover calls "20 ft." away is inside a 20-foot radius, and the map
    never disagrees with itself. Its point of origin is included (Rules
    Glossary, Sphere), so it can catch the source. An Emanation reaches its
    distance from the source's nearest cell and leaves the source out
    (Emanation: "isn't included unless its creator decides otherwise"); a
    Sphere or Cylinder "centered on you" or "Self (10-foot radius)" is one.
    A Cone and a Line are aimed in any direction, from the middle of the
    source's space, their length counted from its edge: a Cone is as wide
    at each point as it is far from that middle (Cone: "width ... equal to
    that point's distance from the point of origin"), which makes a
    15-foot Cone 1, 3 and 3 cells wide straight ahead; a Line is as wide as
    it says, 5 ft. by default. A Cube is centred on the cell aimed at, or,
    from the source (Thunderwave's "originating from you"), sits against
    the side of the source's space nearest the cell aimed at. Directions
    use the shape's cell centres (`GridShape.center`), never a cell's
    coordinates (Decision 3), so a hex grid gets Cones and Lines for free;
    a Cube against the source's side walks the shape's `offset` and
    `footprint`.
17. **Select targets in area closes the dialog and opens it again** (in the
    plan, for the user to overrule; step 10). The dialog is modal and its
    target rows are built for the targets it opened with, so it can't stay
    open while the map is clicked. It reopens on the same pick (its
    `pick` argument, as a trigger's prompt uses), so the form is filled in
    from the pick again: anything typed in it by hand is lost. The area's
    creatures replace the targets; Ctrl+right-click on the map or the cards
    adjusts them afterwards. The view the GM had comes back, and G during
    aiming cancels rather than switching. The area is read from the pick's
    rules text and shown in the bar to correct, not from `CombatEffect`
    (Q10).
18. **Every area agrees with the map's distance count** (in the plan, for
    the user to overrule; replaces 16, after the user asked for every shape
    and range to be checked against Manhattan, 2026-11-15; R11). Nothing in
    a Sphere, Cylinder, Emanation, Cone or Line is further from where it
    starts than its size, as the hover counts it, so a creature the hover
    calls "20 ft." away is never in a 15-foot Cone. A cell is in an area
    when the area covers its middle, and a creature when any of its cells
    is. A Sphere or Cylinder is centred on the cell aimed at, its radius by
    the rule (a diamond with Manhattan: 41 cells for 20 feet, where a
    circle would be about 50); its point of origin is in it, so it can catch
    the source. An Emanation reaches its distance from the source's nearest
    cell and leaves the source out; a Sphere around the source ("Self
    (10-foot radius)") is one. A Cone and a Line are aimed in any direction
    from the middle of the source's space and reach their length by the
    rule from its nearest cell. A Line covers the cells its path crosses,
    as many wide as it says, with the band open on one side, so a 5-foot
    Line is one unbroken row of cells, each a step further than the last,
    at any angle (a 30-foot Line is 6 cells, also diagonally); a 10-foot one
    is two rows, the second on one side. A Cone is as wide at each point as
    it is far from the middle of the source, and also covers its 5-foot
    spine, closed on both sides, so aimed exactly diagonally it is even and
    never empty: a 15-foot Cone is 5 cells, straight or diagonal (4.5 is
    its true area), a 5-foot one aimed diagonally the two cells beside the
    source towards it. With Manhattan, wide shapes lose their corners, as
    the diamond does: a 60-foot Cone is 44 to 56 cells, where its true area
    is 72. A Cube is the exception, as its size is a side, not a reach: 3
    by 3 cells for 15 feet, centred on the cell aimed at (an even one has
    the cell aimed at as its top-left middle cell), or against the
    source's side nearest the cell aimed at, so a corner of Thunderwave's
    Cube is 20 or 25 ft. away on the hover. Directions use the shape's cell
    centres (`GridShape.center`), never a cell's coordinates (Decision 3).
19. **A point aimed past the range is warned about, not refused** (in the
    plan, for the user to overrule; 2026-11-15), as a move past the Speed
    is (Q2): the GM may know better (a Spell Sniper, a reading gone wrong).
    The bar says "Aimed 45 ft. away, range 150 ft." or "Aimed 160 ft.
    away: past its 150 ft. range!", and a click there says so under
    Source/Target. The range is the text's "a point within 60 feet" when
    it has one, else the spell's own range ("150 feet", "1 mile", Touch as
    5 ft.); an area that starts at the source has none to check. A range
    of Self doesn't make the area start at the source (Investiture of
    Wind's Cube is "centered on a point you can see within 60 feet"), but
    a 2014 range of "Self (15-foot cone)" is read as the area itself.

Taken while building step 11 (2026-11-15), for the user to overrule:

20. **An area that stays is held by an active spell** (`"area"` on the
    caster's `active_spells` entry), not kept on the app. Everything that
    ends an active spell ends the area: its time, concentration lost by any
    path (a failed save, Incapacitated, a new concentration, Ctrl+C), the
    card's ✕. Undo and the saved fight state carry it with no new code
    (Decision 4). One kept without concentration gets an active spell of
    its own that holds nothing else, so its end takes only the area away:
    Grease's Prone stays on whoever fell.
21. **A kept area can be put down with nobody in it**, and the dialog then
    opens with no targets (Moonbeam on empty ground, Spirit Guardians with
    nobody near). Apply spends its costs and starts its concentration but
    rolls nothing. Only for an area to keep: Q11 stays open for the rest.
22. **An Emanation (or a Sphere around the source) follows its caster; any
    other kept area stays on the cells it covered when put down**, a Cone
    or Line too, so it doesn't swing round as its caster walks.
23. *(Replaced by 36.)* **Entering an area or starting a turn in it is a
    reminder, not a prompt**: what it asks varies by spell (Spirit Guardians on entering or
    ending a turn, Moonbeam and Web on entering or starting one), so the GM
    reads the line and uses the Custom Effect. "Enters" counts someone an
    Emanation moved onto too.
24. **The colour is picked per area in the bar**, from eight or any other,
    and the next area starts with the last one; it isn't chosen by damage
    type. It's kept on the area's record.

Taken while building step 12 (2026-11-15), for the user to overrule:

25. **A kept area is selected apart from the source and targets**: clicking
    it changes neither (the user: "it doesn't count as a source"), Esc
    deselects it before it clears the selection, and the panel acts on it
    alone. It's selected by a click on an empty cell of it, so a token
    standing in it is still clicked as a token.

Taken with the Map Painter (2026-11-15), for the user to overrule:

26. **Changing the map during a fight is an undo step**: `UndoPoint` keeps
    the map's settings and terrain, so saving the Map Painter mid-fight is
    one Ctrl+Z ([map-painter-plan.md](map-painter-plan.md), Decision 10).
    Answers Q6.

Taken in step 15 (2026-11-16), for the user to overrule:

27. **Taking Prone off a creature on its own turn is it standing up**, and
    spends its movement (half its Speed, Hop Up's 5 ft.); on anyone else's
    turn, or off the map, it's a correction or a feature and spends
    nothing. Too little movement left, or a Speed of 0, is warned about,
    not refused (as Q2). Undo gives the movement back with the badge.
28. **An incorporeal creature can end a move inside a wall or an object**
    (its rules hurt it only "if it ends its turn" there), but not on
    another creature; only a Swarm shares a space. A move's Difficult
    Terrain stays not cumulative, so an enemy standing in rubble is still
    one extra foot per foot.
29. **Distances count only once the map is in use** (the user, 2026-11-16,
    after step 16). Every fight places its tokens as it starts, the party
    along one edge and the rest along the other, so a fight played on the
    cards alone would have the map's made-up distances decide Prone's
    Advantage or Disadvantage and the Critical Hits. The map is in use once
    a token has been moved in this fight, or when the encounter's painted
    map gives starting cells; until then, what asks for a distance stays a
    note for the GM, as before step 16. Step 18.

Taken in steps 19 and 20 (2026-11-16), for the user to overrule:

30. **How cover sits on the grid** (answers the map painter plan's Q2).
    Cover is counted along the straight line between the middles of a cell
    of the attacker's (or of an area's point of origin) and a cell of the
    target's, over every such pair, and the least-covered line counts: the
    attacker takes its best line, as at a table (a Large creature shoots
    past a pillar from its other side). What the line crosses gives cover,
    the two creatures' own cells left out (a goblin on a table isn't behind
    it): a wall Total Cover, an object its own, another creature Half Cover
    whatever its side or size (the Player's Handbook's "a creature, whether
    that creature is an enemy or a friend"), one at 0 HP none. A line
    exactly through a corner, squeezed between two cells, is covered as the
    less protective of them, so peeking past one wall's corner is open and
    a gap between two walls' corners is Total Cover. The target's own Cover
    state counts too, the most protective of the two. Total Cover adds
    nothing to the AC: it's warned about, not refused (as Decision 19). An
    area is stopped only by Total Cover from the terrain, never by a
    creature. Height isn't counted.
31. **Range counts what's sure and warns about the rest.** A ranged attack
    past its normal range, or within 5 feet of an enemy that isn't
    Incapacitated or down, has Disadvantage in the roll; one past its long
    range, or a melee attack past its reach, is warned about, not refused
    (as Decision 19). A thrown weapon is melee within its reach and thrown
    past it. "Can see you" is counted as yes unless the enemy is Blinded or
    the attacker Invisible, which are left as notes, as the Dodge action's
    are. The warnings go on the dialog's target rows and in the log, not on
    the target label, which doesn't know which attack is made (R18).

Taken in step 21 (2026-11-18), for the user to overrule:

32. **How a push sits on the grid.** Each 5 feet of a push is one step to a
    neighbouring cell one step farther from the pusher by the map's rule
    (one nearer for a pull), and of those the one nearest the straight
    line from the pusher's middle through the target's middle as it
    started: along a row it stays on the row, diagonally it's a staircase.
    It stops short of anything the target couldn't end a move on
    (`can_end_at`): the map's edge, a wall or a blocking object, anyone
    else's space, an ally's too; an incorporeal creature goes into a wall,
    a Swarm into a space. A pull stops next to its puller. Difficult
    Terrain costs a push nothing. Two creatures sharing a space (a Swarm)
    have no "away", so neither moves. Height isn't counted.
33. **A push moves the tokens on Apply, once the map is in use.** It isn't
    a prompt to answer afterwards: the dialog's Push box, ticked, is the
    choice, and Ctrl+Z takes the push back with the damage. Before the map
    is in use (Decision 29) nothing moves and the box isn't shown. "Up to"
    pushes the whole way, as the common choice; for less, the GM Alt-drags
    the token back (a push, step 17), which spends nothing. A target too
    big for it ("Large or smaller") stays, with a GM-only line.

Taken in step 22 (2026-11-18), for the user to overrule:

34. **How a grapple moves and holds on the grid.** A grappler that walks
    drags everyone it holds who's on the map ("can drag": the GM who wants
    it to walk off alone takes Grappled off first, the grappler's release).
    The held creature moves as far and the same way as its grappler, so it
    keeps its place beside it; where that won't take it (a wall, someone,
    the edge) it goes to the nearest cell to there that does and is within
    the grapple's range, and where none does it stays, and the range ends
    the grapple. Several held creatures cost no more than one: each foot
    costs 1 extra foot. A grapple's range is the grappler's reach
    (`reach_ft`: 5 ft., a stat block's longest "reach N ft.", 10 ft. with
    a Reach weapon), as the attack that grappled was made within it; it's
    measured after a move, a push or a teleport, never mid-walk, and the
    grapple ends with a GM-only line when it's exceeded. Only a grapple
    whose source was known names a grappler: Grappled given by hand with
    no source drags nobody and never ends by distance.

Taken in step 23 (2026-11-18), for the user to overrule:

35. **A walk goes the cheapest way, cell by cell, and its reach is the
    map's distance at each cell.** The GM clicks where a walk ends; the way
    there is the cheapest walk (`walk_path`), and an Opportunity Attack is
    owed wherever the walker was in a reach at one cell and out of it at
    the next, once per attacker. With the Manhattan rule a diagonal cell is
    10 ft. off, so stepping round a creature's corner leaves a 5-foot reach
    and comes back: it provokes, as the hover's 10 ft. there says. That's
    the price of Manhattan (the Player's Handbook's own diagonals, Later
    14, would make it 5 ft.). Reactive Strike is owed where the walker
    was outside the polearm's reach at one cell and inside at the next,
    Disengage or not, for walks only.

From the user (2026-11-18, the request for step 24), and taken in it for
the user to overrule where marked:

36. **A kept area acts by a turn-column button, when its own text says.**
    Answers Q12, replaces 23. The user asked for a button on entering a
    kept area or starting a turn in one, opening Use / Cast on the area's
    pick with that creature targeted, instead of the reminder. *Taken in
    the plan, for the user to overrule:* the moments are the area's rules
    text's (`area_timing`): entering it, the area moved onto the creature,
    a turn starting there, a turn ending there (shown in the next turn's
    column). The 2024 spells mostly act as a turn ends (Moonbeam, Spirit
    Guardians, Cloud of Daggers, Flaming Sphere), so a button as Moonbeam's
    turn starts would offer a save the rules don't give; a text that names
    no moment (a stat block's, one typed in) acts on entering and at the
    turn's start, as asked. An area that acts on who enters it acts on who
    it's moved onto too. The button costs nothing (the cast was spent),
    deals the damage of the slot it was cast with, and a condition it
    gives is held by the area's concentration. A badge's turn trigger of
    the same name gives way to the area while the creature is on the map
    in use. The GM decides "once per turn" and who is unaffected; a
    button is offered once per area and creature at a time.
37. **Move re-aims a kept area in the area bar.** Answers Q13. The user
    asked for it on the area panel for Moonbeam and Flaming Sphere,
    keeping its time and concentration. *Taken in the plan:* it's shown
    for every aimed kept area (not one around its caster, which moves
    with it), as the GM may also correct where one was put; it spends
    what its text says moving costs (Moonbeam's Magic action, Flaming
    Sphere's Bonus Action), nothing when the text says none, and asks
    first when that's used already (as the dialog's costs do). Past its
    "up to" is warned about, not refused (as Decision 19), measured from
    where it was aimed to where it's aimed now. Its shape stays as it is.

From the user (2026-11-18, the request for step 25), and taken in it for
the user to overrule where marked:

38. **How a wall sits on the grid.** The user asked for a shape of its
    own, aimed by two clicks: its two ends, or a ring's middle. *Taken in
    the plan:* a straight wall is the cells a straight line between its
    two ends' middles crosses, both ends in it and a corner's two cells
    both (so nothing walks through it diagonally), as far from its first
    end as its length lets by the map's rule, as an area's size is
    (Decision 18): a 60-foot wall is 12 cells along a row, and a click
    past that stops it there. A ring is put by one click on its middle and
    is the edge of a Sphere half its size across: each cell that far from
    the middle with a neighbour beyond it, closed all round. Either is one
    cell thick (every wall here is 1 to 5 feet). A wall has no point of
    origin (Rules Glossary, Area of Effect), so nothing it crosses cuts it,
    and nothing covers who's in it from it.
39. **A kept wall is terrain the rules read, never painted.** The user
    asked that a wall its text calls a barrier (Wall of Force) block
    movement and give Total Cover while it lasts, as a painted wall does,
    counted by the terrain the rules read, gone when the spell ends or
    Undo takes it back, and not written into the painted map's file.
    *Taken in the plan:* the wall's record keeps what it is as an object
    (a `MapObject`), and the window reads every rule through the painted
    terrain with each kept wall's object laid over its cells (Decision 3
    still holds: no rule reads cells another way); what's written
    (`in_use`, the log, the painter) is the painted map. Wall of Force's
    "barrier" and "Nothing can physically pass through" make it block and
    be Total Cover; Blade Barrier's own "provides Three-Quarters Cover, and
    its space is Difficult Terrain" is read the same way. A painted wall
    under a kept one stays a wall, and a blocking object stays under a wall
    that doesn't block. A creature the wall appears on isn't moved (the GM
    pushes it out).
40. **Wall of Fire's side is picked by a third click.** The user asked for
    the GM to pick a side as it's put down, and for step 24's buttons to
    cover "ends its turn within 10 feet of that side or inside the wall"
    and "enters the wall". *Taken in the plan:* after its two ends (or a
    ring's middle) the bar asks for a click on one side, shading what that
    side reaches and naming it by the map's compass ("the east side",
    "inside"), as a click on the map is where the GM sees the sides; a
    click on the wall's line is refused. The cells within its reach of
    that side are kept with it. Ending a turn in the wall or by the side
    gets its button (ENDS); entering it is the wall's cells only (ENTERS),
    as "enters the wall" says. Only a wall whose text has "One side of the
    wall ... within N feet of that side" asks.
41. **A wall has no Move.** *Taken in the plan:* none of the walls' texts
    moves one, so the area panel's Move (Decision 37) isn't shown for a
    wall; a wall put in the wrong place is undone or ended and cast again.

Taken in step 26 (2026-11-18), for the user to overrule:

42. **The speed bar picks the speed, and it stays picked.** Answers what
    Q7 left for Later. The speed a creature moves by is kept on it until
    the GM picks another (a dragon that took off stays flying), not asked
    per move; what it moved this turn counts against the new one, as the
    glossary says, and a Dash adds its Speed whichever speed it uses. It
    can't stop flying while aloft: it's brought down to 0 ft. first, which
    spends movement as flying down does. A walk is by one speed, start to
    end.
43. **What each speed costs on the grid.** Flying: the ground's Difficult
    Terrain (painted, furniture), water and heights cost nothing, as
    they're the ground's; another creature's space is still Difficult
    Terrain and still can't be passed unless Q4 lets it; walls and
    blocking objects still block, as the map knows no heights for them.
    Burrowing: under creatures (it ends on nobody) and Difficult Terrain,
    no climbing, walls and blocking objects still block ("can't burrow
    through solid rock"). Swimming: into water only, at no extra cost.
    Climbing: as walking, its Climb Speed the limit (a Climb Speed climbs
    free whichever speed is used, as since step 15). Prone crawling counts
    for all but flying (a Prone flyer falls, or hovers).
44. **Altitude is how high a flyer is over the ground under it.** It's
    kept only while it's set to fly, set in the speed bar, and each foot
    up or down costs a foot of movement. It counts into every distance as
    the ground's height does (the map painter plan's Decision 5), so the
    hover, a reach, a range and an Opportunity Attack measure it; areas and
    cover don't yet (Later 12).
45. **Water is swum, not Difficult Terrain.** Replaces the map painter
    plan's water as Difficult Terrain (its Decision 7's table). A step into
    painted water costs 1 extra foot a foot, 2 with Difficult Terrain there
    too (an enemy's space, furniture), none swimming by a Swim Speed or
    flying over it. Walking, it's the same 10 feet a cell as before.
46. **A fall is landed at once; its damage is the GM's.** Whoever can't
    stay aloft (Prone, Incapacitated, its Fly Speed 0, or no Fly Speed
    left, as when Fly ends, and it can't hover) falls whenever the views
    are brought up to date, so in the same undo step as what dropped it:
    its altitude goes and it moves by its Speed again. The status and a
    GM-only line give the dice ("3d6 Bludgeoning damage, and it lands Prone
    unless it takes none"); the GM applies them, as a fall into water, a
    Feather Fall or a Reaction can change what happens.

Taken in step 27 (2026-11-18), for the user to overrule:

47. **A trigger's distance is counted, what else it asks isn't.** A `when`
    ending in "within N feet" is between the row's owner and the other
    creature of its event (the attacker, the one that dealt the damage,
    the one dropped). Once the map is in use with both on it: farther, the
    row doesn't fire and nothing is said (as a melee-only row for a ranged
    hit); within, the distance is dropped from the question, and a row
    with nothing else to ask is AUTO when its gates allow (Fire Shield).
    The rest stays the GM's ("you can see it", with the distance said).
    Off the map, the whole `when` is asked, as before.
48. **Dark One's Blessing answers others' knockouts near its owner.**
    Answers combat-effects Q63, as its suggestion said (`by_anyone`, named
    `others_within_ft` for the distance it needs). Its rows fire for every
    other creature's knockout of one of its owner's enemies: within its
    feet as the owner's own does (AUTO), farther not at all, and asked "if
    it was within 10 feet of you" off the map. A dead owner gets none.

Taken in step 28 (2026-11-18), for the user to overrule:

49. **Sight counts once the map is in use, from where everyone is.**
    Answers the map painter plan's Q5, as its suggestion said. With both
    creatures on the map and the map in use (Decision 29), who sees whom
    is the map's; off it, everything that asks is noted as before, even
    an Invisible target (a badge such as Faerie Fire may take its benefit
    away, which only the GM knows then).
50. **Only the space of what's looked at hides it.** As the glossary
    words it ("trying to see something in a Heavily Obscured space"): a
    creature every cell of which is dark (or in a fog) isn't seen, one
    partly out of it is, and a creature in the dark still sees out. A fog
    or Darkness between two lit creatures doesn't hide them. Eyes aren't
    stopped by Total Cover here (an attack there is warned about already,
    and a Wall of Force is see-through); Blindsight is, as its text says.
    Dim Light (Lightly Obscured) changes nothing counted.
51. **What being unseen counts in an attack roll.** Invisible's
    Advantage and Disadvantage count when the other doesn't see it, and
    say so when it does ("Ghost is Invisible: no Advantage, the target
    sees it (Truesight 60 ft.)"). An attacker that can't see its target
    for where the target is has Blinded's Disadvantage ("Pirate can't see
    Tiger (Darkness at B1)"), and attacks against a target that can't see
    the attacker for where that is have Blinded's Advantage; not again for
    one Blinded already. A Blinded creature's own rules still count when
    its Blindsight sees (the condition's "Attacks Affected" has no
    exception). Dodge's Disadvantage counts only against an attacker its
    bearer sees, and a ranged attack's close-combat Disadvantage only from
    an enemy that sees the attacker (it replaces the note).
52. **A trigger's "you can see it" is the map's.** What's left of a
    `when` after its distance (Hellish Rebuke's, Warding Flare's): seen,
    it isn't asked; unseen, the row isn't offered; not known, asked.
53. **Senses and what hides, from the text.** A viewer's senses are its
    stat block's ("Blindsight 10 ft. (blind beyond this radius)" sees
    nothing farther), a player's sheet's and its badges' `Vision`. A kept
    area's text says what its space is: magical Darkness Darkvision "can't
    see through" (only Truesight and Blindsight see in it), other
    Darkness (Darkvision too), "Heavily Obscured" (only Blindsight).
    Painted Darkness is the ordinary kind. *Since Decision 54, a kept
    area's rules (its CombatArea's `obscures`) say what its space is, not
    its text.*
54. **An area is fields, not text** (the user, 2026-11-19, answering Q10;
    Notes/explicit-attributes-plan.md, Phase 3). A spell's area is
    `SpellRules.area` and a feature's use's is `CombatEffect.area`, a
    `CombatArea` (Model/Content/CombatArea.py): its shape and size, how far
    its point may be, when a kept area acts, how it's moved, what it hides
    and a wall's ring, damaging side and terrain. The bar starts from it and
    a kept record keeps it as "rules"; nothing reads the rules text while a
    fight runs. A monster ability's area is still read from its description
    until stat blocks get fields (that plan's Phase 4).

## Open questions

Each has a *Suggestion*: what gets built if nobody says otherwise.

- **Q1. How big is the map, and where do tokens start?** *Blocks step 2.*
  *Suggestion:* 24 x 16 cells of 5 ft. for every fight to begin with, the
  party's side along the left edge and everyone else along the right as
  combat starts, moved by hand from there. Per-encounter maps and starting
  positions in `EncounterSpec` come later. *Built so in step 2
  (`ArenaSettings`'s defaults, `place_new`); step 4 calls `place_new` as
  combat starts or is continued.*
- **Q2. Is speed enforced?** *Blocks step 6.* *Suggestion:* no. Show the
  reach and warn in the status line when a move goes past it ("Goblin moved
  40 ft., Speed 30 ft."), but allow it: Dash, being shoved, teleporting and
  Misty Step all move a creature further than its speed, and the GM knows
  which happened. *Built so in step 6.*
- **Q3. Are moves logged?** *Blocks step 6.* *Suggestion:* a GM-only line
  with no action ("Goblin moves 15 ft."), so the log tells the fight's story
  but nothing replays from it and the player link never shows it. The other
  choice is no line at all, if that's too chatty. *Built so in step 6
  ("Goblin moves 15 ft."; placing a token logs nothing). The line's text:
  Decision 13.*
- **Q4. Whose space can a creature move through?** *Blocks step 2.* The
  2024 Player's Handbook (Playing the Game, "Moving Around Other Creatures";
  not in the local Rules Glossary): you can move through the space of an
  ally, an Incapacitated creature, a Tiny creature, or a creature two sizes
  larger or smaller than you; another creature's space is Difficult Terrain
  unless it's Tiny or your ally; you can't willingly end a move in another
  creature's space. *Suggestion:* count all of it in `reachable` from the
  start (it's a few lines once `step_cost` exists), and refuse a drop onto a
  creature. A token dragged from the "Not on the map" strip onto another goes
  to the nearest free cell. *Built so in step 2 (`can_pass_through`,
  `is_difficult_for`, `nearest_free`); refusing the drop too, in step 6,
  where the strip places by a click rather than a drag (R6).*
- **Q5. Which colours?** *Blocks step 4.* *Suggestion:* the party's side
  (players, party allies, players' summons: `on_party_side`) blue, everyone
  else red, whoever's turn it is with a gold ring. A monster charmed into
  helping stays red. *Built so in step 4. The encounter's own allies are
  blue too since step 9 (Decision 11), and whose turn it is stands on gold
  cells as well (R9).*
- Q6: Decision 26.
- **Q7. Which speed is the reach?** *Blocks step 6.* *Suggestion:* the
  walking speed in use. A creature with only a Fly or Swim Speed uses its
  highest one. Picking a speed for a move, and switching speeds part-way
  (Rules Glossary, Speed: "subtract the distance already moved from the new
  speed"), is Later. *Built so (`walking_speed_ft`, step 2; the reach,
  step 6), with Fly or Climb as the fallback: there is no swim field.
  Since step 26 the speed moved by is chosen in the speed bar (Decision
  42), swim and burrow read from the stat block's speed text.*
- **Q8. Does Prone change the reach?** *Blocks step 2.* Rules Glossary,
  Crawling: "each foot of movement costs 1 extra foot". *Suggestion:* yes, a
  Prone creature's steps cost double, so its reach is halved, with a status
  line reminder that standing up costs half its Speed. Standing up isn't
  done by the map; the GM removes Prone as now. *The halved reach is built
  in step 2 (crawling and Difficult Terrain add up: 3 ft. a foot through an
  enemy's space, Rules Glossary, Crawling); the reminder too, in step 6.
  Since step 15, removing Prone on its own turn spends the cost
  (Decision 27), and the reminder says how much.*
- **Q9. What happens to a token at 0 HP?** *Blocks step 4.* *Suggestion:*
  it stays where it fell, greyed. It doesn't block anyone (it's
  Incapacitated, Q4), and it leaves the map only when it leaves the fight. A
  player making death saves keeps their colour, greyed. *Not blocking is
  built in step 2 (`can_pass_through` counts 0 HP too, for a monster with
  no Unconscious badge); the greying too, in step 4.*

- **Q10. Should a `CombatEffect` say its area?** *Blocks nothing.* The
  area is read from the rules text (`parse_area`), which covers 215 of the
  662 spells and the stat blocks' "each creature in a 15-foot Cone"; the
  bar shows what was read, to change. *Suggestion:* not until a reading
  turns out wrong often enough; then an `area` field on `CombatEffect`,
  filled where the text misleads. *Answered (Decision 54, 2026-11-19): yes,
  `SpellRules.area` and `CombatEffect.area`, for every spell with one.*
- **Q11. Should the Custom Effect open with no targets when the source is
  on the map?** *Blocks nothing.* Today it needs a target first
  (`test_dialog_needs_a_target`), so aiming an area starts with a
  right-click on anyone. *Suggestion:* leave it for the user to decide;
  opening without targets means an Apply with none, which the dialog
  would then refuse with "Select targets in area, or right-click a card".
  *Since step 11, a kept area opens it with no targets (Decision 21).*
- Q12: Decision 36.
- Q13: Decision 37.
- **Q14. Which moving features still have no `Movement`?** *Blocks
  nothing.* The incorporeal forms are used features with no combat effect
  yet (Ghost Walk, Umbral Form, Superior Dread's Ghostly Flight, Frozen
  Haunt, Cloak of Shadows' Partially Incorporeal, Undead Steed's Ghostly
  Stride), and Aspect of the Wilds doesn't keep which aspect was chosen
  (Panther's climbing). *Suggestion:* give each form a badge with
  `Movement(through_creatures=True, through_objects=True)` when the
  feature-combat-effects work reaches it; Panther waits for the choice
  to be kept on the build.
- **Q15. Which features change cover or range?** *Blocks nothing.* Only a
  pick's own text is read ("no benefit from Half Cover or Three-Quarters
  Cover": Sacred Flame). Sharpshooter (ranged weapon attacks ignore Half
  and Three-Quarters Cover, no Disadvantage at long range), Spell Sniper
  (spell attacks ignore it, longer range) and Crossbow Expert (no
  Disadvantage within 5 feet with a Crossbow) are the attacker's.
  *Suggestion:* a `Feature.attack_rules()` like `Feature.movement()`
  (step 15), read by `check_attack_range` and `_covered`.

## Revisions

- **R1** (step 1). *Plan:* neighbours come from the `GridShape`. *Done:*
  `DistanceRule.neighbours`, which gives the shape's by default, and
  `reachable` steps by the rule's. *Why:* Chebyshev and 5-10-5 count
  diagonals as a step on the same squares Manhattan uses, so which cells a
  move steps to belongs to the rule; the shape's `neighbours` stays the
  cells that touch. The shape also gained `in_bounds`, `cells`, `offset` and
  `from_edge`, so the arena keeps Decision 3 (no arithmetic on `col` and
  `row` outside geometry.py) while it cuts at the edge and lines tokens up.
- **R2** (step 2). *Plan:* `distance_ft(a, b, rule, cell_ft)`, and DI-084's
  note replaced by `Speed(set_to=0)`. *Done:* `distance_ft(a, b, settings)`,
  as everything else in arena.py takes the settings, and `None` when either
  is off the map; the note stays beside the modifier (RulesConditions is
  the rules sentence by sentence). Added `can_pass_through`,
  `is_difficult_for`, `fits_at`, `nearest_free` and `place_summons`, which
  the plan's functions needed, and `walking_speed_ft` takes Q7's highest
  other speed now rather than in step 6, since it's one line. A creature at
  0 HP blocks nobody even without a badge (Q9), as a monster at 0 HP has
  none.
- **R3** (step 3). *Plan:* `moved_ft` set to 0 as a turn starts, and undoing
  a move tested. *Done:* `moved_ft` is dropped (no key = 0 ft., like a
  position), and undo is tested through `UndoPoint` because the move itself
  (`_move_combatant`) is step 6. `"arena"` is written only during combat,
  next to the turn order, so a prepared log stays as prepared. Summons are
  placed in `_join_fight` through the Qt-free `place_summons`; it does
  nothing until tokens are placed, which `place_new` will do when the view
  comes (step 4).
- **R4** (step 4). *Plan:* `_build_arena_page()`, and the map refreshed from
  `_refresh_cards`. *Done:* `_build_view_stack` and `_build_view_toggle`
  (the window builds the stack and the turn column the button), and
  `_refresh_arena` runs from `_refresh_views`, which every change reaches
  (the cards' refresh starts its timer) and which comes after the turn
  order is settled. `place_new` runs in `_switch_to_combat`, so a fight
  starting or continued puts whoever isn't on the map yet on it; someone
  added mid-fight stays off it until step 6's "Not on the map" strip. The
  map fits the view until the GM zooms, as 24 cells don't fit the cards'
  area at 40 px. Token letters skip a "Group of 3"'s count and read a
  "(1) ..." prefix, as the Ashelm encounters name their groups. A token
  that is both source and target is white with a red ring inside, the
  view's version of the cards' split border.
- **R5** (step 5). *Plan:* the view picked kept in the settings
  (`CombatSettings`). *Done:* kept in the same settings store, under
  `view/arena`, but not a `CombatSettings` field (Decision 10). *Why:* every
  setting is in the Settings dialog (a test holds it to that), and one more
  row made the dialog taller than the smallest window
  (`test_the_settings_dialog_fits_the_smallest_window`); and which view is
  up is window state, switched with G, like a panel left open.
- **R6** (step 6). *Plan:* tokens dragged from the "Not on the map" strip.
  *Done:* a strip button makes that combatant the source, and a click on a
  cell puts it there, the same path as click-to-move. *Why:* dragging from
  a widget into the map needs Qt drag-and-drop, and the click is one path
  for both. Also: a move with no walk there (walled in by enemies) counts
  the straight distance and says so in its line, rather than being refused,
  as Q2's reasoning (the GM knows how it got there) covers it; a Large
  token is moved by the cell it's held by, not its top-left; the reach
  shaded is of the anchor cell, so a Large creature's shading is its
  top-left cell's.
- **R7** (step 7). *Plan:* the hover distance and the label. *Done:* as
  planned, plus: the target label is brought up to date from
  `_refresh_views`, so it follows a move, a new source and undo in both
  views without each of them calling it; a hover over a token counts
  between the two creatures' nearest cells, over an empty cell from the
  source's nearest cell (`distance_to_cell_ft`), and over the source says
  nothing. The hover label follows the cursor without redrawing the map,
  which is redrawn only when its text changes.
- **R8** (step 8). *Plan:* the view in CHEATSHEET.md too. *Done:* not
  there. *Why:* Combat/CHEATSHEET.md is about campaign folders and
  command-line flags, and the map has neither; the window's controls are
  in KEYBOARD_SHORTCUTS.md and HOWTO.md, which link to each other.

- **R9** (step 9, the user's six points after trying it, 2026-11-14).
  1. *Plan:* the party's side is `on_party_side`. *Found:* an encounter's own
     allies (`EncounterSpec.allies`) had no mark in the log, so they started
     on the right in red (DI-092, which also made enemy-only triggers count
     them as enemies). *Done:* `prepared_log` marks them `encounter_ally`
     (`PartyAllies.ENCOUNTER_ALLY_KEY`), `on_party_side` reads it, and a log
     prepared before the mark has them marked by name from its encounter's
     config as it's loaded.
  2. and 4. *Asked:* selecting and targeting in both views, and Ctrl+Z after
     a move. *Found:* both worked with real clicks and keys, offscreen and
     on Windows, for monsters and players and in a campaign's encounter;
     but a quick second click on a token was a double-click, which the view
     sent only to the scene, so it was lost (a Ctrl+right-click toggled
     twice did nothing the second time). *Done:* a double-click counts as a
     press, as on the cards; real-mouse and real-key tests cover both views.
  3. *Plan:* a gold ring on whose turn it is. *Done:* its cells tinted and
     edged gold too, the active card's border and tint, as the ring alone
     was easy to miss.
  5. *Plan:* "Goblin moves 15 ft.". *Done:* from where to where and what's
     left (Decision 13), with cells named "C7" (Decision 15); the map's top
     edge is lettered to match.
  6. *Plan:* drag, or click a cell to move the source. *Done:* a click picks
     a token up and a click on a cell moves it (Decision 12); a click with
     nothing picked up moves nobody (Decision 14). The strip's buttons pick
     up too, so placing goes the same way.

- **R10** (step 10, the user's request, 2026-11-14). *Plan (Later):* "a
  cone, sphere or line drawn from the source, and the creatures inside it
  made the targets". *Done:* all six shapes of the Rules Glossary, aimed
  from the Custom Effect dialog rather than from the map on its own, as
  the dialog is where the GM has the spell or action picked and its text
  to read the area from (Decisions 16 and 17). Two questions left (Q10,
  Q11). Escape on the window cancels aiming before it clears the
  selection, so the targets the dialog had are still there to go back to.
- **R11** (step 10, the user asked to check every shape and range against
  the Manhattan grid, 2026-11-15). *Built:* Cones and Lines measured their
  length in straight lines, so a 15-foot Cone took in creatures the hover
  called 20 ft. away (and was 7 cells, against a true area of 4.5), a
  diagonal 100-foot Line reached 140 ft. by the hover, a diagonal 5-foot
  Line had cells touching only at their corners (4 cells for 30 feet), and
  a 10-foot-wide Line was 3 rows. *Done:* Decision 18: their reach is the
  rule's, a Line is the cells its path crosses (one unbroken row each 5
  feet of width), and a Cone keeps its spine. Also a range check (Decision
  19), and three readings the check turned up: "5-foot-wide, 60-foot-long
  Line" (Sunbeam), "A Line of strong wind 60 feet long and 10 feet wide"
  (Gust of Wind), and a 2014 range of "Self (15-foot radius)" (Lightning
  Lure, Earth Tremor), read from the spell's range, which the dialog now
  passes with its text.

- **R12** (step 11, the user's request, 2026-11-15). *Plan (Later):* "an
  area that stays on the map ... and a creature entering it prompting its
  effect". *Done:* the area stays, held by an active spell (Decisions 20 to
  22), with a reminder rather than a prompt (Decision 23, Q12), and a colour
  per area (Decision 24). *Found:* the new bar controls squeezed the bar's
  text into a column a word wide that pushed the map down, so the text has
  its own line now; and every log line clears the status line, so a turn's
  reminder goes in the turn column's reminders instead.

- **R13** (step 12, the user's request, 2026-11-15). *Plan:* nothing yet
  (Q13 suggested a button on the active spell's row). *Done:* the area is
  selected on the map itself, with a panel of its own (Decision 25), as
  that's where it's seen. A record needed a key, as two kept areas can
  have the same caster and name (two Greases), and its rules text, as a
  monster's action isn't a spell to look up. The panel's title has its own
  line, for the reason the area bar's has (R12).

- **R14** (step 15, the user's request, 2026-11-16). *Plan:* Q4's rules
  only, and standing up left to the GM (Q8). *Done:* a `Movement` modifier
  and `Feature.movement()` for whatever changes them (Decisions 27 and
  28). *Why:* one model for badges, always-on features and stat-block
  traits keeps the search in one place; a feature only adds a line.
  *Found:* `fits_at` was both "a token fits" and "a move can end", which a
  Swarm or a ghost in a wall splits, so a move now asks `can_end_at`.

- **R15** (after step 15, the user asked what the arena misses against the
  rules, 2026-11-16). *Plan (Later):* "using distance in the rules" as one
  item, terrain and speeds after it. *Done:* a review against the Rules
  Glossary found movement well covered and the rolls hardly using the map.
  The "within 5 feet" rules became step 16. Moves on the mover's own turn all
  counting as walks, so a Misty Step provoked Opportunity Attacks, became
  step 17. The rest of Later was ordered by value: cover, range, swimming,
  grapple dragging, the path walked, light and senses, Shove's push.

- **R16** (step 16, 2026-11-16). *Plan:* the Custom Effect's roll and hit
  notes settled by the distance. *Done:* the same input reaches every attack
  path (the dialog, a monster's button, the Attack roll field), and a counted
  Critical Hit counts everywhere a natural 20 does (doubled dice, the log's
  "(critical hit)", the two death save failures, what a hit triggers). The
  `when` is recognised by its text (`settled_by_distance`'s two patterns),
  not a new field on the modifier, so RulesConditions.py and the modifiers'
  saved form are unchanged, and any content saying "the attacker is within N
  feet of it" counts too. A CriticalHitsAgainst without a `when` (none in
  content yet) now counts as well, rather than being only a note. *Why:*
  one Critical Hit per path would have the Attack roll field and the dialog
  disagree on the same hit; Unconscious players at 0 HP are where it matters
  most. *Found:* tokens are placed as a fight starts, so every test that
  expected the old note now has to take the target off the map.

- **R17** (step 19, 2026-11-16). *Plan (Later):* "the line between the two
  creatures' nearest cells", walls and objects only, "shown on the target
  label and then counted". *Done:* every pair of cells, the least-covered
  line counting, and creatures in the way giving Half Cover (Decision 30),
  counted at once in every attack path and the dialog's saves. *Why:* the
  nearest cells alone gave a Large creature Total Cover from a wall that
  hides only half of it, and the Player's Handbook names a creature as
  cover, which is what a fight's lines cross most. The map's cover is a
  copy of the target with a Cover state added (`with_cover`), so the AC,
  the saves and their notes count it through the code that counts a Cover
  state set by hand, with no new path. *Found:* the dialog's target rows
  were drawn before a pick was stored, so they never saw the pick; they're
  drawn again once it is (needed by step 20 too).
- **R18** (step 20, 2026-11-16). *Plan (Later):* "warned about on the
  target label". *Done:* on the dialog's target rows, in the roll's log
  line and on a monster's button, with what's sure (Long range, close
  combat) counted as Disadvantage rather than warned about (Decision 31).
  *Why:* the label belongs to the selection, not to an attack: the same
  target can be in reach of a sword and in long range of a bow. *Found:*
  weapons kept no range numbers, only the Range property, so the Weapons
  table's are in Core/Weapons.py now.
- **R19** (step 21, 2026-11-18). *Plan (Later):* "as a Push move offered
  from the Custom Effect after a failed save". *Done:* a `push` field on
  `CombatEffect`, so the push belongs to the effect like its damage, moved
  on Apply with a box to untick in the dialog (Decisions 32 and 33),
  rather than a prompt after it. *Why:* a prompt per target after a
  Thunderwave would be a click per creature for what is nearly always
  done, and the map already knows which way "away" is. A Shove had no row
  at all, so the Unarmed Strike has two. *Found:* `_move_combatant` showed
  its own status line, so it's split into `_relocate`, which returns what
  to say; and the picker rows' golden for described spells hadn't been
  regenerated since step 15 gave Freedom of Movement and Spider Climb
  their `Movement` badges, so those two rows are new in it too.
- **R20** (step 22, 2026-11-18). *Plan (Later):* "the grappler drags it,
  each foot costing 1 extra foot ...; the grapple ends when they're
  further apart than its range". *Done:* as planned, plus who grapples
  whom kept on the grappled creature (nothing knew it: the condition's
  record keeps a "caster" only while it has a tooltip, and is pruned
  without one), the grapple ending with an Incapacitated grappler, and
  the Unarmed Strike's Grapple row, which step 21 left out. *Found:* the
  dragged creature was measured for an Opportunity Attack on its own
  grappler, since the walk was checked before the drag; the drag comes
  first now.
- **R21** (step 23, 2026-11-18). *Plan (Later):* "Sentinel and Polearm
  Master's entering reach". *Done:* Polearm Master's Reactive Strike
  only, as the 2024 Sentinel has no entering-reach rule. Undo now keeps
  every hit prompt, not only the walk's, so undoing a hit takes its
  trigger buttons (Hill's Tumble) back too, which step 14's Not done
  asked for the Opportunity Attacks. *Found:* a walk round a creature's
  corner, which `tests/test_combat_ui_standard_actions.py` had as "stays
  in reach" from its two ends, leaves a 5-foot reach on the Manhattan
  grid on the way (Decision 35); that test file's Tiger is the plain
  one-cell `Combat.Combatants.Tiger`, not the Large stat block.
- **R22** (step 24, the user's request, 2026-11-18). *Plan (Later, Q12):*
  "a creature entering one, or starting its turn in it, prompts its
  effect", "once a kept area records its pick and when its rules fire (a
  `CombatEffect` trigger)". *Done:* the moments are read from the area's
  own rules text, which every kept record has already (its `about`, else
  its spell's), and include ending a turn there and the area moved onto
  someone (Decision 36); no `CombatEffect` field was needed. *Why:* the
  2024 wording puts most areas' damage at the end of a turn (Moonbeam's
  "ends its turn there"), so a turn-start button would offer the wrong
  save, and one moment per area would have to be written by hand for
  every spell. *Found:* Use / Cast on Moonbeam's own row spends a slot,
  the Action and a new concentration, which would end the very Moonbeam
  acting, so the dialog has a no-cost mode (`kept_area`); the slot the
  area was cast with wasn't kept, so its damage at that slot is on the
  record now; Spirit Guardians' badge already asked "if it ends its turn
  in the Emanation" of every enemy, which the area now answers itself;
  Flaming Sphere's area is read from its light (DI-096).
- **R23** (step 25, the user's request, 2026-11-18). *Plan (Later 6):* "a
  Line of cells drawn freely ..., one side of it dealing damage, and its
  cover", "aimed by two clicks, and terrain the kept area adds while it
  lasts". *Done:* as planned, with the terrain the wall adds as a layer
  over the painted terrain that every rule reads (`_map_settings`,
  Decision 39) rather than cells added to `arena_settings.terrain`, and
  the damaging side picked by a third click (Decision 40). *Why:* terrain
  added to the map would have been saved with it (the painter, the log's
  "arena") and would need taking off by hand when the spell ends; laid
  over from the active spell, it ends, undoes and saves with the spell, as
  every kept area does. Blade Barrier's Three-Quarters Cover and Difficult
  Terrain came along, as the same reading. *Found:* skipping light radii
  (DI-096) changed other spells' readings for the better: Light, Continual
  Flame and Produce Flame read no area now, Holy Weapon, Combustion and
  Investiture of Flame the one their text states after the light; and the
  wall reading also finds Wall of Stone, Wall of Ice, Prismatic Wall, Wind
  Wall and four more, whose terrain isn't read (DI-097).

- **R24** (step 26, 2026-11-18). *Plan (Later 7 and 8):* two items,
  "Fly, Swim, Climb or Burrow Speed chosen for a move" and water swum,
  with "the combatants don't have a field for" a Swim Speed. *Done:* one
  step, as water's cost depends on the speed used; the speeds are read
  from what stat blocks already say (their Fly and Climb fields and their
  speed text: "swim 40 ft.", "burrow 20 ft.", "hover") and from a
  Movement, so no new stat-block field was needed (Decisions 42 to 46).
  *Found:* a Movement could only change how a creature moves, not give it
  a speed, so it gained `fly_ft`, `flies`, `swim_ft`, `swims` and
  `hovers`; Fly had no combat effects at all, and every other grant is
  text (DI-098); `movements` moved to speeds.py so arena.py can import
  the speeds without a loop; and a flyer whose Fly Speed is gone (Fly
  ended) would have gone back to its Speed and landed without falling,
  so its altitude is read from what it was set to, not from the speeds it
  has now.

- **R25** (step 27, 2026-11-18). *Plan (Later 9):* "triggers that ask
  'within 5 feet' (Fire Shield) or 10 feet (Dark One's Blessing ...),
  Spirit Guardians' aura". *Done:* the triggers, read from their own
  `when` text by one pattern (Decision 47), rather than a distance field
  on each trigger, as every distance in content is written the same way
  and the skill now says to write it so; Dark One's Blessing's other
  half as a new gate (Decision 48). Spirit Guardians' aura needed nothing
  more: its kept area (step 24) is it. *Found:* only four `when`s in all
  the content name a distance, and none is on a turn trigger, so DI-085
  closes with this step.

- **R26** (step 28, 2026-11-18). *Plan (Later 10):* "Heavily Obscured
  as Blinded for sight there, Darkvision, Blindsight, Truesight, each from
  the viewer's senses; needs DI-068". *Done:* that, and kept areas that
  hide (the Darkness spell, Fog Cloud) read from their text, See
  Invisibility and Faerie Fire as a new `Vision` modifier, the triggers'
  "you can see it" and the close-combat rule's "an enemy who can see you".
  The sight rides on the map's `RangeCheck` (its word on an attack), so
  the attack rows and rolls that already read it needed no new argument.
  *Found:* DI-068 was smaller than logged: the Invisibility spell already
  gave the condition; only the GM's visibility list didn't.
- **R27** (steps 26 and 28, 2026-11-19; explicit-attributes-plan Phase
  4.1). The speeds and senses R24 and R26 read from a stat block's text
  are fields now: `speed_swim_ft`, `speed_burrow_ft`, `hover`,
  `darkvision_ft`, `blindsight_ft`, `blind_beyond`, `truesight_ft`,
  `tremorsense_ft` on ExtendedCombatantData. `speeds.py` and `senses.py`
  read only those; the `speed_special_rules` and `senses` strings are only
  shown. *Found:* DI-106, a summoned spirit's form-only speeds.

## Discovered issues

Found while writing the plan:

- **DI-084** (fixed 2026-11-13, step 2): `speed_in_use` ignored the conditions' Speed 0. The
  rules conditions give it as a `Note`, not as `Speed(set_to=0)`, so a
  Grappled, Restrained, Paralyzed, Petrified or Unconscious creature keeps
  its full Speed on its card and in More Info
  (`speed_in_use({"conditions": ["Grappled"]}, 30)` is 30). The arena's reach
  reads it, so step 2 fixed it first.
- **DI-085** (fixed 2026-11-18, step 27; a gap): the simulator doesn't know where anyone is, so
  every rule with a distance in its `when` is noted, never counted. The arena
  is what lets those rules be counted later (Later: using distance in the
  rules); building the map alone doesn't close it. Step 16 counts the
  conditions' "within 5 feet" (Prone, Paralyzed, Unconscious); the rest
  are still notes.

Found in step 9:

- **DI-092** (fixed 2026-11-14, step 9): an encounter's own allies counted as
  enemies (`on_party_side` False), on the map and for enemy-only triggers.

Found in step 21:

- **DI-095** (open, content): pushes and pulls written only in text (Thorn
  Whip, Thunderous Smite, Pushing Attack, Open Hand Technique, Repelling
  Blast and more); each needs a `CombatPush` on its effect.

Found in step 24:

- **DI-096** (fixed 2026-11-18, step 25, the area reading): Flaming
  Sphere's area is read as a 20-foot Sphere, from its "Bright Light in a
  20-foot radius", not the 5-foot sphere whose damage reaches 5 feet; the
  GM sets 5 ft. in the bar meanwhile.

Found in step 25:

- **DI-097** (open, a gap): kept walls other than Wall of Force and Blade
  Barrier (and Wall of Water's Difficult Terrain) aren't terrain: Wall of
  Stone and Wall of Ice can be walked through and give no cover, Wall of
  Thorns' 4 feet a foot and the opaque walls' blocked sight aren't
  counted.

Found in step 26:

- **DI-098** (open, content): Fly and Swim Speeds from features and spells
  other than Fly (Aasimar and Dragonborn wings, Circle of the Stars and of
  the Sea, Zealot and Vengeance Paladin flight, the Swim Speeds of the
  Elements Monk and the Ranger, feats, Gaseous Form, Alter Self) are text;
  each needs a Movement (fly_ft, flies, swim_ft, swims, hovers).
- **DI-099** (open, step 28): light that spells and carried sources give
  (Light, Daylight, Flaming Sphere, Moonbeam, a torch) doesn't light
  painted Darkness; the GM repaints it.
- **DI-100** (open, step 28): Devil's Sight isn't a sense sight reads, so a
  Warlock with it in the Darkness spell doesn't see.
- **DI-101** (open, step 28): a spell that needs its target seen ("a
  creature you can see") isn't warned about against one the caster
  doesn't see (Invisible's Concealed).
- **DI-102** (open, step 28): the GM's Heavily Obscured and Darkness
  visibility states aren't read by sight.

Already logged, and touched by this plan:

- **DI-068** (fixed 2026-11-18, step 28): Invisible is a visibility state, so the Invisible
  condition's rules never reach the attack notes. The map draws hidden
  tokens from the visibility states, so it doesn't depend on this, but a map
  on the Player Screen (Later) must leave Invisible creatures out the same
  way the Player Screen does.
- **DI-034** (fixed): attack rolls count conditions, except those that need
  a position (Prone, Paralyzed's and Unconscious's Critical Hits), which
  stay notes. These are DI-085's first candidates.
