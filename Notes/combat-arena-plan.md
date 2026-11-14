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
same day. What's next is under Later.

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
test files after a step (`./run_tests.sh -q tests/test_arena_geometry.py
tests/test_arena.py tests/test_combat_ui_arena.py`). No step here changes a character sheet, so the
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
  the token's colour. A walking speed is `speed_ground_ft` on a monster and
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
                                        its HP as a thin bar, a gold ring on whose turn it is,
                                        the source and target outlines the cards use (white,
                                        red; both: white with a red ring inside),
                                        greyed at 0 HP (Q9), dashed while the players can't see it
  "Not on the map" strip                a button per combatant without a position: it becomes
                                        the source, and a cell clicked puts it there (R6)
  pick_up(row, held) / drop(cell)       a drag: the reach shaded with its costs, then on_move
                                        with the anchor that puts the held cell on `cell`
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
  _arena_cell(cell)                     an empty cell clicked: the source goes there
  _move_combatant(char, cell)           @undoable: places one off the map, or walks one on it
                                        (move_cost, else straight_ft), adds to moved_ft, logs
                                        a GM-only line (which saves the fight), warns (Q2, Q8)
  _refresh_arena()                      called from _refresh_views (R4)
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

**Moving.** Drag a token to a cell, or with a source selected, click an
empty cell. While a token is picked up, the cells it can reach this turn
(its walking speed in use, less `moved_ft`) are shaded with what each costs.
Going past the reach is warned about, not refused (Q2). Ending on another
creature is refused (Q4). Each move is one undo step. A move counts the
cheapest walk there (`move_cost`); when no walk gets there (walled in by
enemies) it counts the straight distance and the log line says so, as the
GM moved it some other way. A creature with no Speed as a number (a plain
combatant like the Pirate) reaches only its own cell but can still be
moved. Someone without a place is put on the map from the strip, or with
a source selected by clicking a cell; placing moves nothing and logs
nothing.

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

### Later (not scheduled)

- **More distance rules**, each a `DistanceRule` and a line in `RULES`:
  Chebyshev and 5-10-5 on squares, Euclidean (rounded to the nearest 5 ft.),
  hexagons (a `HexGrid` shape with axial cells and its rule; footprints of
  Large+ creatures on hexes need their own decision). A combo box in the map
  settings picks one.
- **Map settings dialog**: size, cell feet, rule; per encounter in its
  `EncounterSpec` (a default map and starting positions, Q1).
- **Terrain**: walls and obstacles (cells nobody enters), difficult terrain
  (a step costs 1 extra foot, which `reachable`'s costs already allow).
- **Other speeds**: flying, climbing, swimming as a choice when moving (Q7).
- **Using distance in the rules**, which is where the map pays off (DI-085):
  the "within 5 feet" in Paralyzed's and Unconscious's automatic Critical
  Hits and Prone's Advantage, triggers that ask "within 5 feet" (Fire Shield)
  or 10 feet (Dark One's Blessing, combat-effects-plan Q63), a spell's range
  checked as it's cast, Spirit Guardians' aura, Opportunity Attacks prompted
  as a creature leaves reach. Each still asks when either creature is off the
  map.
- **Areas of effect**: a cone, sphere or line drawn from the source, and the
  creatures inside it made the targets.
- **The map on the Player Screen and the player link**, from the same token
  rows, hidden monsters left out the way `player_view_rows` leaves them out.
- **Height**: a flying creature's altitude, counted into distance.

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
  ("Goblin moves 15 ft."; placing a token logs nothing).*
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
  helping stays red. *Built so in step 4.*
- **Q6. Is changing the map's settings an undo step?** *Blocks nothing yet.*
  *Suggestion:* not until there's a map settings dialog (Q1, Later); it joins
  `UndoPoint` then.
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
  enemy's space, Rules Glossary, Crawling); the reminder too, in step 6.*
- **Q9. What happens to a token at 0 HP?** *Blocks step 4.* *Suggestion:*
  it stays where it fell, greyed. It doesn't block anyone (it's
  Incapacitated, Q4), and it leaves the map only when it leaves the fight. A
  player making death saves keeps their colour, greyed. *Not blocking is
  built in step 2 (`can_pass_through` counts 0 HP too, for a monster with
  no Unconscious badge); the greying too, in step 4.*

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
  rules); building the map alone doesn't close it.

Already logged, and touched by this plan:

- **DI-068** (open): Invisible is a visibility state, so the Invisible
  condition's rules never reach the attack notes. The map draws hidden
  tokens from the visibility states, so it doesn't depend on this, but a map
  on the Player Screen (Later) must leave Invisible creatures out the same
  way the Player Screen does.
- **DI-034** (fixed): attack rolls count conditions, except those that need
  a position (Prone, Paralyzed's and Unconscious's Critical Hits), which
  stay notes. These are DI-085's first candidates.
