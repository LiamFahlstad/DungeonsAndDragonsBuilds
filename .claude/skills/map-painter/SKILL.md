---
name: map-painter
description: The combat UI's Map Painter and painted battle maps - terrain (walls, Difficult Terrain, water, height, Dim Light/Darkness, objects with cover and hazards), starting cells, the Maps/<encounter id>.json files, and how the fight's rules read them (blocked cells, movement cost, climbing, height in distances, Obscured, hazard reminders). Has a script that indexes the painter's code (file:line, live from the code) and shows, lists and paints maps as compact ASCII instead of reading their JSON. Use before reading or changing any painter or terrain code, before opening a Maps/*.json file, when asked to make, check or change an encounter's map or where combatants start, and for bugs about terrain on the battle map.
---

# Map Painter

**Save tokens:** don't open a `Maps/*.json` file (a painted map is ~17 KB of JSON) or read the painter's files to find something. Use the script, then read only the lines it points to.

```bash
T=.claude/skills/map-painter/map_tool.py
python $T index [--grep word]        # painter code: file:line kind name - doc line (live, never stale)
python $T maps                       # every painted map: size, what's painted, starts
python $T show wrath_of_durmor       # one map as ASCII + legend, heights grid, starts
python $T paint wrath_of_durmor ground wall C7:F7 H9   # layers: ground|height|light|object
python $T start wrath_of_durmor "Goblin King" A8       # "-" removes the start
```

`paint`/`start` write the file as the painter does; take an encounter id or a path.

## Model (Qt-free, `Combat/Arena/`)

- `terrain.py`: `Spot(ground, height_ft, light, thing)` per cell; `Terrain.cells` keeps only non-plain cells. `MapObject(name, blocks, difficult, cover, hazard)`, `OBJECT_PRESETS`.
- `ArenaSettings.terrain` (arena.py): every arena rule already takes the settings. `to_dict()` has `"terrain"` only when painted, so old logs stay identical.
- `maps.py`: `MapDesign(settings, starts: {name: Cell})` in `<Campaign>/Maps/<id>.json`; `place_at_starts`; starts are keyed by the fight's combatant name ("Greypaw (Ally) (Greypaw (Young))").
- UI: `CombatUIQt/map_painter.py`. `PainterView` is an `ArenaView` whose mouse paints, `MapPainterDialog` has a tab per tool, and `MapPainterMixin` handles the window side. Drawing is `arena_view.draw_terrain`.

## Rules counted

Walls and blocking objects can't be entered. Difficult Terrain costs +1 ft./ft. and isn't cumulative with an enemy's space. A height step is a climb: +1 ft./ft., +2 in Difficult Terrain, +0 with a Climb Speed. Height adds into distances via `DistanceRule.with_height`. Obscured is shown, not rolled. Cover is shown, not counted. Hazards give reminders.

## Gotchas

- A fight copies the map when it starts (the log's `"arena"`). After that it keeps its own copy. Saving the open encounter's map mid-fight goes through `_use_painted_map`, as one undo step (`UndoPoint.arena`).
- No arithmetic on `col`/`row` outside `geometry.py`. Use `between`, `edges`, `offset`, `cell_name`.
- [Notes/map-painter-plan.md](../../../Notes/map-painter-plan.md) is a living plan. Update its Status, Decisions, Qs and Revisions in the same change. Open work is its Q1-Q8.
- Tests: `./run_tests.sh -q tests/test_arena_terrain.py tests/test_combat_ui_map_painter.py tests/test_arena.py tests/test_combat_ui_arena.py`.
