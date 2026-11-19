# Plan: what `CombatArea` can't say yet (DI-105)

## How to use this document

A living plan, like [explicit-attributes-plan.md](explicit-attributes-plan.md)
and [combat-arena-plan.md](combat-arena-plan.md). Tick **Status** in the
same change as the step. Write better solutions into **Revisions**, move
answered **Open questions** to **Decisions**, and log bugs with the
`discovered-issues` skill. Keep the overhead low (the user, 2026-11-10): run
the test files a step touches (`tests/test_arena_lasting.py`,
`tests/test_arena_areas.py`, `tests/test_arena_walls.py`,
`tests/test_picker_rows.py` and the matching `test_combat_ui_arena_*`),
not the whole suite.

## Goal

DI-105 lists seven things that spells' areas do but
`Model/Content/CombatArea.py` has no field for. They turned up while R9 of
the explicit-attributes plan wrote areas from the rules. Each one is now
either missing from the spell or written as something close to it but
wrong. This plan adds the fields, has the battle map (`Combat/Arena/`)
read them, and corrects the spells.

The principle stays the explicit-attributes plan's: a rule the simulator
acts on is a field, written once in the spell's class. The fight never
reads it out of rules text.

## What's there now (2026-11-19)

- `CombatArea` is flat and frozen. Only a Wall may have `ring_ft`,
  `side_ft`, `blocks`, `cover` or `difficult` (`_WALL_FIELDS`). Empty
  `acts` means `DEFAULT_TIMING` (enters, starts).
- `lasting.area_record` writes a kept area's `"terrain"` (a `MapObject`
  dict) only for a Wall (`wall_terrain`). `with_kept_walls` lays that
  terrain over the painted map for everyone alike. It uses
  `record_cells`, so terrain on an area that follows its caster would move
  with the caster.
- `arena._walk_search` charges 1 extra foot per foot for Difficult Terrain,
  not cumulative (`int(difficult)`). It knows allies (`_is_ally`), but
  terrain doesn't depend on who moves.
- An Emanation always comes from its caster (`record_cells` and
  `area_cells(area, caster, None, ...)`). A wall's damaging side is one
  side the GM picks, and it acts only when a turn ends there
  (`areas_beside`).
- Senses know painted light (bright, dim, dark) and three area kinds
  (Darkness, magical Darkness, Heavily Obscured).
- A record has one `"aim"`.

The spells involved, as they are now:

| Gap | Spell | Area now | What's wrong |
|---|---|---|---|
| 1 | Spike Growth | Sphere 20 | no Difficult Terrain |
| 1 | Dark Star | Sphere 40, magical Darkness | no Difficult Terrain |
| 1 | Grave Ground | Cube 10, enters/ends | no Difficult Terrain (enemies only), one square (gap 7) |
| 1 | Investiture of Ice | Emanation 10 | no Difficult Terrain (not for the caster) |
| 1 | Guardian of Nature | none | Great Tree: 15 ft around you is Difficult for enemies |
| 1 | Storm of Vengeance | Cylinder 300 | Difficult only from turn 5 |
| 2 | Detonate | Sphere 60 aimed at the target | a 60-foot Emanation from the target (not including it) |
| 2 | Conjure Animals | Sphere 10, movable 30 | "within 10 feet" of a Large pack |
| 2 | Guardian of Faith | Sphere 10 | "within 10 feet" of a Large guardian |
| 2 | Conjure Elemental | Sphere 5 | within 5 feet of the elemental spirit |
| 2 | Hail of Thorns, Lightning Arrow, Searing Orb, Jim's Glowing Coin, Holy Weapon | Sphere at the target (R9) | an Emanation from the target |
| 3 | Detect Magic, Detect Evil and Good, Detect Poison and Disease, Warp Sense, Hallow, ... | default timing | get enters/starts prompts they never act on |
| 4 | Wall of Thorns | Wall, enters/ends | 4 ft of movement per foot through it |
| 4 | Wall of Sand | Wall, Heavily Obscured | 3 ft of movement per foot through it |
| 5 | Prismatic Wall | Wall, acts on enters | the 20-foot zone on both sides (moves within, starts there: blinded) |
| 6 | Forcecage | Cube 20 | nothing crosses its faces; the box blocks spells too |
| 6 | Shadow of Moil | none | 10 ft around you a step darker |
| 7 | Fire Storm | one 10-ft Cube | up to ten, contiguous |
| 7 | Grave Ground | one 10-ft Cube | up to four, contiguous |

## Status

- [ ] Step 1: an area that never acts
- [ ] Step 2: terrain on any shape, and for whom
- [ ] Step 3: movement that costs more than Difficult Terrain
- [ ] Step 4: Emanations from someone else
- [ ] Step 5: a wall's zone on both sides, acting
- [ ] Step 6: Forcecage and Shadow of Moil
- [ ] Step 7: several copies of one shape
- [ ] Close DI-105 (`issues.py update DI-105 --status fixed`), with a line
  in the explicit-attributes plan's R9

The steps go from smallest to largest. Each one is its own commit. Every
step edits `CombatArea.py` and `lasting.py`, so they run **one after
another, never in parallel**. Agent: `combat-simulator` (opus) for each
step, spell classes included. Steps 1 and 3 are small enough for
`model: "sonnet"`.

## Step 1: an area that never acts (gap 3)

Detect Magic's Emanation, or Hallow's 60-foot area, stays on the map to be
seen, but nothing happens when a creature enters it. Right now its empty
`acts` reads as `DEFAULT_TIMING`, so the turn column offers prompts for it.

- `acts: tuple[AreaTiming, ...] | None = None`. **None** means "the rules
  don't say" (`DEFAULT_TIMING`, as today). **`()`** means it never acts.
  `timing` returns an empty frozenset for `()`.
- `to_dict` leaves out None and writes `[]` for `()`. `from_dict` reads
  `[]` as `()`. This is backward compatible: `to_dict` never wrote an
  empty `acts` before, so no kept record or log has `"acts": []`.
- `lasting.area_timing` and the prompt code already go through `timing`.
  Check that nothing else tests `not rules.acts`
  (`grep -rn "\.acts\b" Combat Model`).
- Spells: write `acts=()` on every lasting area that only marks where
  something is. Find them with a one-off scratch script: every spell whose
  area is kept, has no `acts`, and whose combat effects have no save,
  damage or condition. Review the list by hand. Expected: the three
  Detects, Warp Sense, Hallow, Mordenkainen's Private Sanctum, Temple of
  the Gods, Druid Grove. Antipathy/Sympathy does act.

*Verify:* a test that Detect Magic's kept area gives no prompt when a
creature enters it or starts its turn there, and that a record without
`acts` still gets the default. `test_picker_rows.py` goldens: only the
edited spells' `area` changes.

## Step 2: terrain on any shape, and for whom (gaps 1 and 6a's groundwork)

- Take `blocks`, `cover` and `difficult` out of `_WALL_FIELDS`, so any
  shape may have them. `ring_ft` and `side_ft` stay wall-only.
- Add `difficult_for: AreaWho | None = None`, a new
  `AreaWho(StrEnum)` with `EVERYONE`, `NOT_CASTER` and `ENEMIES` (the
  caster's). It is only valid when `difficult=True`. None means everyone.
- `lasting.wall_terrain` becomes `area_terrain` and `area_record` writes
  `"terrain"` for any shape. `with_kept_walls` becomes `with_kept_terrain`
  (keep the old name as an alias until its callers are moved) and lays
  only the everyone terrain over the map, as now.
- Terrain for some creatures only can't go into the shared overlay. Add
  `kept_difficult_cells(mover, chars, settings) -> set[Cell]` to
  `lasting.py`: the cells of every kept area whose `difficult_for` counts
  the mover (not its caster, or the caster's enemy by the same `_is_ally`
  the arena already uses). `_walk_search` takes it as one more reason a
  cell is Difficult, under the same flying, burrowing and
  `ignores_difficult` rules as painted Difficult Terrain. The ground is
  what's Difficult in each of these spells, so a flier ignores it.
- A record kept before this step has a wall's `"terrain"` or none: no
  upgrade needed.
- Spells: Spike Growth, Dark Star (`difficult=True`); Grave Ground
  (`difficult_for=ENEMIES`); Investiture of Ice (`NOT_CASTER`); Guardian of
  Nature: its Great Tree row gets `CombatEffect.area`, a 15-foot Emanation
  with `difficult_for=ENEMIES`, and the spell keeps no area (Primal Beast
  has none). Storm of Vengeance stays without terrain (Q2).

*Verify:* walk tests in `tests/test_arena_lasting.py`. Moving through
Spike Growth costs double. Grave Ground costs double for an enemy and
normal for the caster's ally. Investiture of Ice's cells move with its
caster, and the caster walks them at normal cost. A flier crosses Spike
Growth at normal cost.

## Step 3: movement that costs more than Difficult Terrain (gap 4)

Wall of Thorns: "For every 1 foot a creature moves through the wall, it
must spend 4 feet of movement". Wall of Sand: 3 feet.

- `CombatArea.move_cost: int | None = None`: feet of movement each foot
  through its space costs (at least 2). `MapObject` gets the same field
  (default None, left out of `to_dict` when None), so it reaches the map
  through `"terrain"` like `difficult`.
- `_walk_search`: the step's terrain extra is `max(int(difficult),
  move_cost - 1)`, not the two added together (Q3). Crawling, dragging and
  swimming still add on top, as they do today. `ignores_difficult`
  doesn't waive it, because this cost isn't Difficult Terrain. Flying
  doesn't either, because the wall stands 10 to 20 feet tall.
- The Map Painter doesn't offer it. It's for spells only (an object's
  dialog could add it later).
- Spells: Wall of Thorns `move_cost=4`, Wall of Sand `move_cost=3`.

*Verify:* a 5-foot step into Wall of Thorns costs 20 feet, and 40 when
Prone. Painted Difficult Terrain under it doesn't raise that to 25. A
creature with `ignores_difficult` still pays 20.

## Step 4: Emanations from someone else (gap 2)

An Emanation "extends from a creature or an object in all directions"
(Rules Glossary, Emanation) and moves with it. That creature isn't always
the caster. "Within 10 feet of" a Large guardian is the same area,
measured from its 10-foot space.

- `CombatArea.around: AreaAnchor | None = None` (Emanation only).
  `AreaAnchor(StrEnum)` has:
  - `TARGET`: the creature the row targets (Detonate, Hail of Thorns,
    Lightning Arrow, Searing Orb, Jim's Glowing Coin, Holy Weapon). The
    area bar needs no aim and takes the one target picked, or asks for
    one. A kept area follows that creature: the record keeps
    `"around": <its name>` and `record_cells` measures from it, covering
    nothing while it's off the map, as for a caster.
  - `PLACED`: a space the caster puts something in (Conjure Animals' pack,
    Guardian of Faith, Conjure Elemental's spirit). The record keeps the
    anchor `"aim"` and `"follows": False`. Moving it (Conjure Animals'
    30 feet) moves the anchor and works its cells out again.
- `around_size: CreatureSize | None` for `PLACED`: the size of the space
  it's measured from (Large for the pack and the guardian). None means one
  cell. `area_cells` takes a stand-in footprint of that size at the
  anchor, using the same `footprint_at` creatures use, so a Large source's
  emanation is 30 feet across on squares, not 25.
- "Not including the target" (Detonate) follows the Emanation rule the
  caster already has: the origin creature is left out. Check
  `creatures_in` does that for `TARGET` too.
- R9's Spheres become Emanations: Hail of Thorns etc. (`around=TARGET`),
  Detonate (`around=TARGET`, 60), Conjure Animals (`around=PLACED`,
  `around_size=LARGE`, 10, `move_ft=30`), Guardian of Faith (same, no
  move), Conjure Elemental (`PLACED`, 5, with the elemental's size).

*Verify:* geometry tests in `tests/test_arena_areas.py` (a Large anchor's
10-foot Emanation covers the cells within 10 feet of its 2x2). A kept
`TARGET` area follows its target when the target moves. Conjure Animals
moved 30 feet gives a moved-onto prompt. Picker goldens: the listed spells'
`area` changes from Sphere to Emanation.

## Step 5: a wall's zone on both sides, acting (gap 5)

Prismatic Wall: "If another creature that can see the wall moves within 20
feet of it or starts its turn there, the creature must succeed on a
Constitution saving throw or have the Blinded condition".

- `CombatArea.both_sides: bool = False` (Wall only, needs `side_ft`): the
  zone is within `side_ft` of the wall on both sides (a globe's inside and
  outside), and no side is picked as it's put down. `areas.side_cells` gets
  a both-sides form (the union of the two, the wall's own cells left out).
  The record keeps `"side": "both"`.
- `CombatArea.side_acts: tuple[AreaTiming, ...] | None = None`: when the
  zone acts. None means `(ENDS,)`, Wall of Fire's, as `areas_beside` does
  today. `who_is_in` and `entered` also look at the side cells, so ENTERS
  and STARTS can fire there, and `AreaPrompt.beside` gets the text for
  each time ("moved within 20 ft. of it", "starts its turn by it").
- "You and creatures you designate" and "that can see the wall" stay with
  the GM, who skips the prompt (as for every area prompt now).
- Spell: Prismatic Wall `side_ft=20, both_sides=True,
  side_acts=(ENTERS, STARTS)`. Its own `acts` (ENTERS, passing through the
  layers) stays as it is.

*Verify:* `tests/test_arena_walls.py`. A creature that walks to within
20 feet on either side gets a prompt. Wall of Fire's one side still acts
only at turn end.

## Step 6: Forcecage and Shadow of Moil (gap 6)

**Forcecage.** The prison is the Cube's faces, not its cells. A creature
inside a 10-foot box stands in one of the box's cells and must still move
within it. So `blocks` on the cells (step 2) is wrong for it.

- `CombatArea.encloses: bool = False` (Cube only): nothing crosses its
  faces. `_walk_search` refuses a step from a cell inside an enclosing
  kept area to one outside it, and the other way round. It compares the
  set of enclosures each cell is in, so two cages side by side work too.
  `lasting.kept_enclosures(chars, settings)` gives the cell sets.
  Teleporting doesn't walk, so it isn't stopped (the spell's Charisma
  save is the GM's).
- With `cover=TOTAL`, `cover.cover_between` gives Total Cover when exactly
  one of the two creatures is inside (the box "blocking any spells cast
  into or out from the area"). Without it (the cage), it gives no cover.
- Spell: the spell's area is the cage (Cube 20, `encloses=True`). A second
  row, "Forcecage (box)", gets `CombatEffect.area` Cube 10
  `encloses=True, cover=TOTAL`. Pushing out creatures that are only
  partly inside stays the GM's (a push from the Use / Cast dialog).

**Shadow of Moil.** "The shadows turn dim light within 10 feet of you into
darkness, and bright light in the same area to dim light."

- `AreaSight.DIMS = "a step darker"`. `senses.obscured_cells` reads each
  covered cell's painted light one step down: dim becomes Darkness
  (`DARKNESS`, which Darkvision sees in), and bright becomes dim (Lightly
  Obscured, which the sight rules don't count today). A cell that's
  already Darkness stays as it is. When areas overlap, the darkest wins,
  as `_stronger` does now.
- Spell: Shadow of Moil, a 10-foot Emanation, `obscures=DIMS`,
  `acts=()`. Its "you become heavily obscured to others" is a badge on the
  caster, not the area (a combat-effects question, not this plan's).
- DI-099 (light that spells give) is the reverse, a step brighter. Name
  the sense code's helper `light_step(cell, steps)` so DI-099 can reuse it.

*Verify:* walk tests (inside a 10-foot box, a step out is refused, a step
within is allowed; the same from outside), cover tests (box: Total across
it, nothing between two creatures inside; cage: none), and senses tests
(Shadow of Moil on painted dim light is Darkness, seen by Darkvision).

## Step 7: several copies of one shape (gap 7)

Fire Storm: "up to ten 10-foot Cubes, which you arrange as you like. Each
Cube must be contiguous with at least one other Cube." Grave Ground: four
10-foot squares, the same.

- `CombatArea.count: int = 1`: up to this many copies, each aimed on its
  own. Not for a Wall or an unaimed area.
- Area bar (`arena_mixin.py`): with `count > 1`, each click adds a copy
  ("Cube 3 of 10"), Undo removes the last one, and **Done** (or the
  `count`th click) finishes. A copy that doesn't share a face with one
  already placed is refused with a status message (Q5).
- The record keeps `"aim"` (the first copy, so old readers still work),
  `"aims"` (all copies), and `"cells"`, the union. Targets in the area are
  the union, each creature once (Rules Glossary, Area of Effect: a
  creature is in the area or isn't). A kept area acts once per creature
  per time, as now.
- Moving a multi-copy area isn't needed (neither spell moves).
- Spells: Fire Storm (`count=10`), Grave Ground (`count=4`). Look for
  others with a scratch-script search of the spell texts for "up to
  (two|three|...|ten) N-foot".

*Verify:* `tests/test_combat_ui_arena_areas.py` (three Cubes aimed, a
creature in two of them listed once, a non-contiguous click refused, Undo
of the last copy), and a kept Grave Ground giving one prompt to a
creature entering two of its squares.

## Not in this plan

- **Storm of Vengeance's later rounds** (turn 5 onwards Difficult
  Terrain, and its other per-round effects). An area that changes by round
  is its own model (Q2).
- **Area prompts only for enemies** (Grave Ground's "Any enemy", Guardian
  of Faith's). Today the GM skips the prompt. `AreaWho` from step 2 could
  later become a `prompts_for` field.
- **Drafting the new fields from text** in `CombatAreaText.py`. These
  areas are rare and written by hand. The draft only has to stop
  producing the wrong reading for them (Detonate's Sphere, for example).

## Open questions

- **Q1. Never acts: `acts=()` or a flag?** *Suggestion:* `acts=None` as the
  "unsaid" default and `()` as "never" (step 1). This adds no field, and
  no stored record says `[]` today. The alternative, `inert: bool`, gives
  two fields that can disagree.
- **Q2. Storm of Vengeance's terrain from turn 5.** *Suggestion:* leave it
  out. The GM paints Difficult Terrain at turn 5 if it matters. A
  per-round area is a bigger model than one spell justifies.
- **Q3. Wall of Thorns on Difficult Terrain: 4 or 5 feet per foot?**
  *Suggestion:* 4, the larger of the two. Difficult Terrain isn't
  cumulative, and the spell says what each foot costs.
- **Q4. Guardian of Faith and Conjure Animals as summon tokens** (they
  occupy a space; `place_summons` exists) instead of `around=PLACED`?
  *Suggestion:* `PLACED` now. A token would also need HP, turns and the
  summon framework. If they become summons later, `around` can gain a
  `SUMMON` anchor.
- **Q5. Fire Storm's contiguity: enforce or allow anything?**
  *Suggestion:* enforce sharing a face, since the spell says so. The GM
  can still aim a second cast. "Contiguous" for squares on a grid means
  sharing an edge.

## Decisions

(None yet.)

## Revisions

(None yet.)

## Discovered issues

- DI-105: this plan.
