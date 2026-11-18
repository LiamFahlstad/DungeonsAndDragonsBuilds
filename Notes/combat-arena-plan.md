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
the Use / Cast dialog moved on the map, Later's third, 2026-11-18. What's
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

## How it fits the code that's there

What the code already gives, found while writing this:

- **The window** ([window_mixin.py](../Combat/CombatUIQt/window_mixin.py),
  `_build_window`) is a row of three parts: the cards' scroll area
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
- Reminders (`arena_mixin.py`, Decision 23): a move after which someone is
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
  falling; Grapple isn't a row yet (Later 4).

Tests: `tests/test_arena_pushes.py`, `tests/test_combat_ui_arena_pushes.py`;
the picker rows' goldens (`tests/test_picker_rows.py`) have the Shove rows.

### Later (not scheduled)

In order of relevance (R15, the user, 2026-11-16: "add your suggestions
(in order of relevancy) to the plan"). Each is a step of its own when it's
picked up. The first three, cover, range and pushes, were steps 19 to 21.

3. *(Step 21.)* **Shove's push** and the other pushes, moved on Apply.
   What's left is content (DI-095).
4. **Grappling moves the Grappled creature** (Rules Glossary, Grappled): the
   grappler drags it, each foot costing 1 extra foot unless it's Tiny or two
   or more sizes smaller; the grapple ends when they're further apart than
   its range (Rules Glossary, Grappling).
5. **The path walked kept**, so an Opportunity Attack catches a walk that
   passes through a reach, or leaves and comes back (only the walk's ends
   are known now, step 13); Sentinel and Polearm Master's entering reach.
   With it: Undo of the walk takes its Opportunity Attack buttons back, and
   an enemy's other buttons go once it spends its Reaction (step 14's Not
   done).
6. **Areas that stay, acting** (Q12, Q13): a creature entering one, or
   starting its turn in it, prompts its effect (a turn-column button, as a
   trigger's) instead of a reminder; a **Move** button on the area panel for
   Moonbeam and Flaming Sphere; walls (Wall of Fire, Wall of Force), which
   aren't one of the six shapes.
7. **Other speeds** (Q7, the map painter plan's Q4): Fly, Swim, Climb or
   Burrow Speed chosen for a move, switching part-way (Rules Glossary,
   Speed: "subtract the distance already moved from the new speed"); a
   flying creature's altitude added into distances; falling when it's Prone
   or Incapacitated or its Fly Speed is 0, unless it hovers (Rules
   Glossary, Flying).
8. **Water is swimming, not Difficult Terrain** (Rules Glossary, Swimming):
   1 extra foot a foot, 2 extra in Difficult Terrain, none with a Swim Speed
   (which the combatants don't have a field for yet, with 7).
9. **Distance in triggers and auras** (DI-085; the conditions' "within 5
   feet" counts since step 16, through `settled_by_distance`): triggers
   that ask "within 5 feet" (Fire Shield) or 10 feet (Dark One's Blessing,
   combat-effects-plan Q63), Spirit Guardians' aura. Each still asks when
   either creature is off the map.
10. **Light and senses counted** (the map painter plan's Q5): Heavily
    Obscured as Blinded for sight there, Darkvision, Blindsight, Truesight,
    each from the viewer's senses; needs DI-068 (Invisible as a condition).
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
cover (step 19), range (step 20) and pushes (step 21), its first three
items.

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
23. **Entering an area or starting a turn in it is a reminder, not a
    prompt**: what it asks varies by spell (Spirit Guardians on entering or
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
  step 6), with Fly or Climb as the fallback: there is no swim field.*
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
  filled where the text misleads.
- **Q11. Should the Custom Effect open with no targets when the source is
  on the map?** *Blocks nothing.* Today it needs a target first
  (`test_dialog_needs_a_target`), so aiming an area starts with a
  right-click on anyone. *Suggestion:* leave it for the user to decide;
  opening without targets means an Apply with none, which the dialog
  would then refuse with "Select targets in area, or right-click a card".
  *Since step 11, a kept area opens it with no targets (Decision 21).*
- **Q12. Should entering an area, or starting a turn in it, open its
  effect?** *Blocks nothing.* Now it's a reminder (Decision 23).
  *Suggestion:* a prompt in the turn column, like a trigger's, opening the
  Custom Effect on the pick with that creature targeted, once a kept area
  records its pick and when its rules fire (a `CombatEffect` trigger).
- **Q13. Can a kept area be moved?** *Blocks nothing.* Moonbeam and
  Flaming Sphere move as an action. *Suggestion:* a **Move** button on
  the area panel (step 12) that aims it again in the bar and keeps its
  time.
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

## Discovered issues

Found while writing the plan:

- **DI-084** (fixed 2026-11-13, step 2): `speed_in_use` ignored the conditions' Speed 0. The
  rules conditions give it as a `Note`, not as `Speed(set_to=0)`, so a
  Grappled, Restrained, Paralyzed, Petrified or Unconscious creature keeps
  its full Speed on its card and in More Info
  (`speed_in_use({"conditions": ["Grappled"]}, 30)` is 30). The arena's reach
  reads it, so step 2 fixed it first.
- **DI-085** (open, a gap): the simulator doesn't know where anyone is, so
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

Already logged, and touched by this plan:

- **DI-068** (open): Invisible is a visibility state, so the Invisible
  condition's rules never reach the attack notes. The map draws hidden
  tokens from the visibility states, so it doesn't depend on this, but a map
  on the Player Screen (Later) must leave Invisible creatures out the same
  way the Player Screen does.
- **DI-034** (fixed): attack rolls count conditions, except those that need
  a position (Prone, Paralyzed's and Unconscious's Critical Hits), which
  stay notes. These are DI-085's first candidates.
