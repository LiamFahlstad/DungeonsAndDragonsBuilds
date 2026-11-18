# Plan: the Map Painter

Goal (the user, 2026-11-15): "create something called the 'map painter' as
part of the combat ui. There you can design the combat area, starting
positions of NPCs, heights, visibility, objects, etc".

The Map Painter is a dialog of the combat window where the GM paints an
encounter's battle map before the fight (or changes it during one): its
size, walls, Difficult Terrain and water, the ground's height, Dim Light and
Darkness, objects, and the cell each combatant starts on. The fight then
plays on it: the battle map of
[combat-arena-plan.md](combat-arena-plan.md) draws the paint and its rules
count it.

Written and built 2026-11-15 (steps 1-5). What's next is under Later and the
Open questions.

## How to use this document

This is a living plan, like [combat-arena-plan.md](combat-arena-plan.md)
and [combat-effects-plan.md](combat-effects-plan.md).

**The plan updates itself as the work teaches us** (the user, 2026-11-13).
It's the best guess before building, not a contract. When working on a step
turns up a better solution, or a realisation that changes the picture, do
the better thing and change the plan to match in the same change, and
record what changed and why as a Revision. Only overruling one of the
user's own decisions needs the user's word first.

Whoever works on the painter updates it **in the same change** as the code:

- **Status**: tick the step, with the date and the Revisions it made.
- **Decisions**: numbered, never renumbered. Each says who decided and when,
  and which question it settles. A decision that replaces an earlier one
  says so, and the earlier one gets "replaced by N".
- **Open questions**: numbered Q1, Q2, ..., never reused. Each says what it
  blocks and gives a *Suggestion*, which is what gets built if nobody says
  otherwise. When it's answered, it moves to Decisions and leaves a
  one-line pointer behind.
- **Revisions**: numbered R1, R2, ...: what the plan said, what's done
  instead, why, and the step it came from.
- **Discovered issues**: bugs and gaps go into
  [discovered-issues.md](discovered-issues.md) through the
  `discovered-issues` skill's `issues.py`, and their ids are listed here.

**Keep the overhead low (the user, 2026-11-10).** After a step run the
painter's and the arena's own tests (`./run_tests.sh -q
tests/test_arena_terrain.py tests/test_combat_ui_map_painter.py
tests/test_arena.py tests/test_combat_ui_arena.py`), and the rest of
`tests/test_combat_ui_*.py` when the window's layout changes. Nothing here
changes a character sheet.

## Status

| Step | What | State |
|---|---|---|
| 1 | Terrain (Qt-free, `Combat/Arena/terrain.py`): ground, height, light, objects per cell, as plain JSON; in `ArenaSettings` | Done 2026-11-15 |
| 2 | The rules (`Combat/Arena/arena.py`): walls and blocking objects nobody enters, Difficult Terrain, climbing, height in distances | Done 2026-11-15 (R1) |
| 3 | The map file (`Combat/Arena/maps.py`): `MapDesign`, `Maps/<encounter id>.json`, starting cells | Done 2026-11-15 |
| 4 | The painter (`Combat/CombatUIQt/map_painter.py`): the dialog, its tools, undo, the window's button and Ctrl+M, a fight starting on the map, saving mid-fight as an undo step | Done 2026-11-15 (R2) |
| 5 | The fight on a painted map: the terrain drawn, the hover, Obscured on the target label, hazard reminders; docs | Done 2026-11-15 (R3) |

## How it fits the code that's there

- **Every arena rule takes `ArenaSettings`** (`reachable`, `fits_at`,
  `distance_ft`, `place_new`, the areas), so the terrain is a field of it
  (Decision 4) and none of their signatures changed.
- **The fight's map is saved in its log** under `"arena"`
  (`LoggingMixin._write_log`, during combat only), and read back by
  `_load_log_from_path`. A log without one is a fight not started yet, which
  is where the painted map comes in (Decision 3).
- **Tokens are placed as the fight starts** (`ArenaMixin._place_on_arena`,
  from `_switch_to_combat`), which now puts whoever the map gives a starting
  cell there first.
- **Undo** (`undo.py`) copies the combatants; it now keeps the map's
  settings too, so painting mid-fight is one step (Decision 10).
- **The view** (`arena_view.py`) draws token rows over the grid; the
  terrain is drawn between them by one function, `draw_terrain`, that the
  painter's view uses too: the painter's view *is* an `ArenaView` whose
  mouse paints (`PainterView`).

## Design

```text
Combat/Arena/terrain.py                 (Qt-free)
  grounds   open, wall, difficult, water
  lights    bright, dim (Lightly Obscured), dark (Heavily Obscured)
  covers    none, half, three_quarters, total
  MapObject(name, blocks, difficult, cover, hazard)   to_dict / from_dict / describe
  OBJECT_PRESETS                        Table, Low wall, Barrel, Crate, Pillar, Tree, Boulder,
                                        Statue, Door, Rubble, Bushes, Campfire, Trap
  Spot(ground, height_ft, light, thing) one cell; PLAIN is open, level, bright, empty
  Terrain(cells: {Cell: Spot})          only cells that aren't plain
    at, put, change(cell, **fields)     paint
    blocks, difficult, height, hazard   what the rules ask
    describe(cell) -> [str]             what the hover says
    within(on_map), to_dict, from_dict  {"cells": [{"at": [c, r], "ground": "wall", ...}]}
Combat/Arena/arena.py
  ArenaSettings.terrain                 to_dict has "terrain" only when painted
  ArenaSettings.standable(cell)         on the map, no wall, no blocking object
  ArenaSettings.height_of(cells)        a footprint's ground: its highest cell
  ArenaSettings.copy()
  has_climb_speed(char)
Combat/Arena/geometry.py
  GridShape.between(a, b)               the block between two cells (Shift+drag)
  GridShape.edges(cell, px)             each side, with the cell beyond it (cliffs)
  DistanceRule.with_height(flat, rise)  Manhattan adds them (Decision 5)
Combat/Arena/maps.py                    (Qt-free)
  MapDesign(settings, starts: {name: Cell})    to_dict / from_dict / copy / cropped
  map_path(combat_log_dir, id)          <Campaign>/Maps/<id>.json
  read_map, write_map
  place_at_starts(chars, starts, settings)
Combat/CombatUIQt/arena_view.py
  draw_terrain(scene, settings)         walls, water, dotted Difficult Terrain, height tint
                                        and labels, pale cliff edges, objects, light last
Combat/CombatUIQt/map_painter.py
  PainterView(ArenaView)                strokes: start_stroke / stroke_to / end_stroke;
                                        Shift: a block; click_only on the Start tab
  MapPainterDialog                      encounter list, width / height, the tool tabs
                                        (Ground, Height, Light, Objects, Start), Clear
                                        terrain, Undo (Ctrl+Z), Save (Ctrl+S), Cancel
  MapPainterMixin                       _show_map_painter, _painter_load, _painter_roster,
                                        _save_painted_map, _use_painted_map (@undoable),
                                        _encounter_map
```

What the fight does with the paint:

| Painted | On the battle map |
|---|---|
| Wall, blocking object | Nobody is moved, placed or starts there; the reach goes around it |
| Difficult Terrain, furniture | A step onto it costs 1 extra foot per foot; not cumulative with a creature's space (Decision 7) |
| Water | Swum since the arena plan's step 26 (its Decision 45): 1 extra foot per foot, 2 in Difficult Terrain, none by a Swim Speed or flying |
| Height | A step between two heights climbs the difference (Decision 6); distances add the height difference (Decision 5) |
| Dim Light, Darkness | Shaded; the hover names it; the target label adds "Lightly Obscured" / "Heavily Obscured" (Decision 8) |
| Object | Drawn and named; its cover on the hover (Decision 9) |
| Hazard | "Tiger enters a hazard: Campfire at G3." on walking onto it; "... starts its turn in Campfire at G3." in the turn column |
| Starting cell | Where the combatant is put as the fight starts (Decision 11) |

## Decisions

From the user (2026-11-15, the request that started this plan):

1. **The Map Painter is part of the combat UI** and designs the combat area:
   the map, where NPCs start, heights, visibility and objects.

Taken in the plan (2026-11-15), for the user to overrule:

2. **A map belongs to an encounter, in its own file**:
   `Combat/Campaigns/<Campaign>/Maps/<encounter id>.json`, beside
   `CombatLogs/`. JSON, as it's painted rather than written, and not a field
   of `EncounterSpec`, so painting never edits `encounters.py`. An encounter
   without one plays on the empty 24 x 16 map as before.
3. **A fight takes the map when it starts and keeps its own copy** in its
   log's `"arena"` key. A fight continued later plays on the map it started
   on, whatever was painted since; a restarted one reads the file again.
4. **The terrain is part of `ArenaSettings`**, which every arena rule
   already takes, so no rule's signature changes and the log, undo and the
   view carry it with the map's size.
5. **Height counts into distance by the distance rule**
   (`DistanceRule.with_height`): Manhattan adds the height difference as one
   more direction, so a goblin on a 10-foot ledge next to you is 15 ft. away,
   and the count stays the rule's (the arena plan's Decision 3). A
   footprint stands on its highest cell.
6. **A step between two heights is a climb** (Rules Glossary, Climbing):
   each foot of the difference costs 1 extra foot, 2 extra in Difficult
   Terrain, none with a Climb Speed. Going down counts the same, as
   climbing down; jumping down is the GM's (Q8), as moves past the reach
   are warned about, not refused.
7. **Difficult Terrain isn't cumulative** (Rules Glossary, Difficult
   Terrain): painted Difficult Terrain under an enemy's space costs 1 extra
   foot per foot, not 2. Crawling still adds to it.
8. **"Visibility" is the light, as the rules have it**: Dim Light is
   Lightly Obscured and Darkness Heavily Obscured (Rules Glossary). It's
   shown (shading, the hover, the target label: Heavily Obscured only when
   every cell of the target is dark), not rolled into attacks yet (Q5).
   What the players can see of the map is Q1.
9. **Objects are per cell, with what the rules need**: whether they block
   movement, are Difficult Terrain (furniture), the cover they give, and
   whether they're a hazard. A row of the same object is named once. Cover
   is shown on the hover, and counted between two creatures since the arena
   plan's step 19 (its Decision 30; Q2).
10. **Saving the map of the encounter that's open changes its fight**: on
    the initiative screen it's the map the fight starts on; in combat it's
    one undo step (`UndoPoint` keeps the map's settings, the arena plan's
    Q6), with a GM-only line, and anyone now off the map or on a wall moves
    to the nearest free cell (off the map when there's none).
11. **Starting cells are by combatant name**, as the log names them
    ("Goblin Warrior 3"). A start someone else is on when the fight starts
    goes to the nearest free cell; whoever has none starts as before.
12. **The painter is a dialog with a tab per tool**: the tab shown is what
    a left-drag paints and a right-drag clears; Shift+drag fills a block;
    the Start tab places by clicks. It has its own Ctrl+Z, and asks before
    unsaved changes are lost (Cancel, Esc, another encounter).

## Open questions

- **Q1. Should "visibility" also be what the players see?** *Blocks
  nothing.* A fog of war: cells the players haven't seen hidden on the
  Player Screen's map. *Suggestion:* once the map is on the Player Screen
  (the arena plan's Later), a "Hidden from players" light layer the GM
  reveals.
- Q2 (cover): the arena plan's Decision 30, built in its step 19. Blocking
  sight is still the arena plan's Later (light and senses).
- **Q3. Should areas of effect count height?** *Blocks nothing.* Areas are
  flat now, so on uneven ground a creature the hover calls 20 ft. away can
  be in a 15-foot Sphere (the arena plan's Decision 18). *Suggestion:* yes,
  count each cell's height into the area's reach.
- **Q4. Flying creatures' altitude.** *Blocks nothing.* *Suggestion:* a
  token's own "flying at" height, added to the ground's in distances.
- **Q5. Should Obscured change attack rolls?** *Blocks nothing.* Heavily
  Obscured is Blinded while trying to see there. *Suggestion:* with DI-068
  (Invisible as a condition), give the attack notes "target Heavily
  Obscured: Disadvantage" from the map.
- **Q6. Doors that open in a fight.** *Blocks nothing.* *Suggestion:* a
  click on an object in the fight's map selects it, as a kept area is, with
  Open/Close for a door (blocks or not).
- **Q7. One map for several encounters.** *Blocks nothing.* *Suggestion:* a
  "Copy from..." in the painter, so each encounter still has its own file.
- **Q8. Jumping down rather than climbing.** *Blocks nothing.* Climbing
  down costs as climbing up. *Suggestion:* leave it to the GM (the move is
  warned about past the reach, not refused); falling damage stays the
  Custom Effect's.

## Revisions

- **R1** (step 2). *Plan:* the rules ask the terrain directly. *Done:* the
  geometry got `GridShape.between` and `edges` and `DistanceRule.with_height`,
  so the painter's blocks, the cliffs and height in distances do no
  arithmetic on cell coordinates (the arena plan's Decision 3), and
  `reachable` caches what entering each anchor costs.
- **R2** (step 4). *Found:* the view's "nothing changed" check compared
  `settings.to_dict().items()`, which hashes its values, so a map with
  terrain (lists in it) would raise. *Done:* it compares `to_dict()`
  itself. `to_dict` has `"terrain"` only when something is painted, so a log
  without paint is as before.
- **R3** (step 5). *Plan:* a gold edge where the ground drops. *Done:* a
  pale stone one: gold is whose turn it is, and the two read alike on the
  fight's map.

## Discovered issues

None found while building.

Already logged, and touched by this plan:

- **DI-068** (open): Invisible is a visibility state, not a condition; Q5
  would build on it.
- **DI-085** (open): rules with a distance in their `when` aren't counted.
  The painted map's heights now count into every distance those rules will
  read.
