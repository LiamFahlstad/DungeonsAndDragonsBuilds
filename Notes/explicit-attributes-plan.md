# Plan: explicit attributes instead of reading rules text with regexes

## How to use this document

A living plan, like [combat-effects-plan.md](combat-effects-plan.md) and
[combat-arena-plan.md](combat-arena-plan.md): tick **Status** in the same
change as the step, write better solutions into **Revisions**, move answered
**Open questions** to **Decisions**, and log bugs with the
`discovered-issues` skill. Keep the overhead low (the user, 2026-11-10): run
the few test files a step touches, chiefly `tests/test_picker_rows.py`.

## Goal

The user (2026-11-19): "in the combat ui I see a pattern that we use regex to
find certain keywords from texts. I would avoid that if possible instead I
would like to have that as explicit attributes instead."

**Principle.** A rule the simulator acts on is a field. Text is parsed at
most once, when the content is authored or generated (a scraper, the
monster generator, `combat_effects.py draft`), where a person or a golden
test reviews the result. The fight never parses text at runtime. A regex
that reads *what the GM types*, or formats a log line, is not rules text
and stays.

## Inventory (2026-11-19)

About 160 `re.` calls in `Combat/`. Sorted by what they read:

| Group | Where | Reads | Explicit home |
|---|---|---|---|
| A. A field already exists | `Arena/ranges.py` `action_range`, `Arena/arena.py` `reach_ft` | "reach 10 ft.", "range 80/320 ft." from a description that `MeleeAttack`, `RangedAttack` and `MeleeOrRangedAttack` *built* from `reach_ft` / `range_ft` / `long_range_ft` | those fields |
| | `Arena/areas.py` `spell_range_ft(spell.range)` (callers: `arena_mixin.py`, `effect_options.py`) | "150 feet", "Touch" | `SpellRules.range` is already `Range(RangeType.FOOT, 150)`; `Spell.range_spec` / `range_feet` |
| | `attack_rolls.py` `armor_without_shield` | a player's "18 (with Shield) and 16 (without Shield)" | the sheet knows both ACs: an `ac_without_shield` key on the player's combat dict |
| B. Text we wrote ourselves | `Effects/triggers.py` `settle_when` (`_WHEN_WITHIN`, `_WHEN_SEES`) | `CombatTrigger.when` = "you can see it within 60 feet" | `within_ft: int \| None`, `sees: bool` on `CombatTrigger` (precedent: its `others_within_ft`), `when` keeps only what's left for the GM |
| | `Effects/modifiers.py` `settled_by_distance` (`_WITHIN_FEET`, `_FARTHER_THAN_FEET`) | a modifier's `when` = "the attacker is within 5 feet of it" (`RulesConditions.py`) | `within_ft` / `farther_than_ft` on the modifier (`Model/Content/CombatModifiers.py`) |
| C. Spell/feature map data | `Arena/areas.py` `parse_area`, `point_range_ft`, `wall_ring_ft`, `damaging_side_ft` (about 20 regexes) | "20-foot-radius Sphere", "within 60 feet of you", walls, rings, panels | a `CombatArea` (below) |
| | `Arena/lasting.py` `area_timing`, `move_rule`, `wall_terrain` | "enters the area", "ends its turn there", "move the sphere up to 30 feet as a Bonus Action", "barrier", "provides Three-Quarters Cover" | fields on `CombatArea` |
| | `Arena/senses.py` `area_obscures` | "Heavily Obscured", "Darkvision can't see through" | `CombatArea.obscures` |
| | `Arena/cover.py` `_IGNORES_COVER` | Sacred Flame's "no benefit from Half Cover...", Sharpshooter | `CombatEffect.ignores_cover: bool`; a feature modifier for the feats |
| D. Monster stat blocks | `CombatUIQt/monster_actions.py` (about 24 regexes) | to-hit, save DC, damage dice, riders, "(Recharge 5-6)", "(2/Day)", "(Costs 2 Actions)", start-of-turn traits | fields on `MonsterAbility`, filled by `generate_monsters.py` |
| | `Arena/speeds.py` `_SPECIAL`, `_HOVER` | `speed_special_rules` = "swim 40 ft.", "hover" | `speed_swim_ft`, `speed_burrow_ft`, `hover` on `ExtendedCombatantData` |
| | `Arena/senses.py` `_SENSE`, `WildShape.py` `_PASSIVE_PERCEPTION` | `senses` = "Blindsight 30 ft. (blind beyond this radius), Darkvision 120 ft., Passive Perception 15" | `darkvision_ft`, `blindsight_ft`, `blind_beyond`, `truesight_ft`, `tremorsense_ft`, `passive_perception` |
| | `saves.py` `_SPELL_SAVE_DC`, `_SPELL_ATTACK` | "spell save DC 15", "+7 to hit with spell attacks" | `spell_save_dc`, `spell_attack_bonus` on `ExtendedCombatantData` |
| | `effect_options.py` `_CASTS`, `_SPELL_LIST`, `_FOLLOWING`, `_MAKES_ONE`, `_USES`, `_MOVES` | "casts Fear", "At will: ...; 2/Day each: ...", "makes one Rend attack" | `MonsterAbility.casts: tuple[MonsterCast, ...]` (spell, level, per day); `MonsterAbility.uses: str` (the other action's name) |
| E. The text-reading fallback | `effect_options.py` `EffectText` (about 40 regexes) | a spell's or feature's whole effect when it has no `combat_effects()` | `CombatEffect`. Already planned to shrink: combat-effects-plan R4, Phase 4.3. 571 of 662 spells still use it |
| F. **Stays** (not rules text) | `amounts.py`, `attack_rolls.py` `_NATURAL`, `conditions_mixin.py`, `trigger_prompt.py`, `saves.py` `_DICE` | what the GM types ("nat 20", "2d6 + 3", "12, 15") | - |
| | `EncounterLogs.py`, `public_log.py`, `player_view.py`, `arena_view.py`, `effect_options.py` `_without_slot_note` | our own log/display strings | - (could become fields later; low value) |
| | `EncounterConfig.py` `ID_PATTERN`, `CombatEffect.py` `DICE` | validation | - |
| | `Combat/Tools/*` (scrapers, generators) | scraped HTML/JSON | - This is *where* parsing belongs; group D moves parsing here |

## Status

| Phase | Step | State |
|---|---|---|
| 1 | Read the fields that already exist (group A) | 1.2 **done** with Phase 3 (R3); 1.1, 1.3 not started |
| 2 | Our own `when` strings become fields (group B) | Not started |
| 3 | `CombatArea` for spells and features (group C) | **Done** (2026-11-19, R1-R8). 3.5 done for described spells; Sharpshooter and Spell Sniper not (R6) |
| 4 | Monster stat-block fields at generation time (group D) | Not started |
| 5 | Retire `EffectText` (group E) | Not started; waits on the content rollout |
| G | A guard test that lists every remaining text regex | Not started |

## Phase 1: read the fields that already exist

Small and low-risk, with no data to migrate.

- **1.1** `action_range` / `reach_ft`: an ability that is a `MeleeAttack`,
  `RangedAttack` or `MeleeOrRangedAttack` (or a dict carrying `reach_ft` /
  `range_ft`) gives its fields. The text read stays only for a freeform
  ability until Phase 4.
- **1.2** Every `spell_range_ft(spell.range)` becomes `spell.range_feet`
  (`Range` handles Touch, Self and miles). Delete `_RANGE_FEET` and
  `_RANGE_MILES`.
- **1.3** The player's combat dict gets `ac_without_shield` from the sheet
  where the AC sentence is built. `armor_without_shield` reads the key, and
  old logs keep the text read in their upgrade path.

*Verify:* `tests/test_picker_rows.py`, the arena range and reach tests, and
the shield tests. No golden changes.

## Phase 2: our own `when` strings become fields

These strings are written in this repo and then parsed back. That is the
clearest case of the pattern the user means.

- **2.1** `CombatTrigger`: `within_ft: int | None` and `sees: bool`. Migrate
  Fire Shield, Storm's Thunder, Hellish Rebuke and Warding Flare (5
  `when="...within N feet"` today); `when` keeps only the leftover question
  for the GM. Delete `_WHEN_WITHIN` and `_WHEN_SEES`.
- **2.2** The modifier `when` in `RulesConditions.py` (Prone, Paralyzed,
  Unconscious): `within_ft` / `farther_than_ft` on the modifier. Delete
  `_WITHIN_FEET` and `_FARTHER_THAN_FEET`.
- **2.3** `combat_effects.py check` flags a `when` that still says "within
  N feet" or "you can see", so new content uses the fields. Update the
  `combat-effects` skill's Triggers section.

*Verify:* the trigger and modifier tests; the same pop-ups appear at the
same distances.

## Phase 3: `CombatArea` for spells and features

This answers combat-arena-plan **Q10** ("Should a `CombatEffect` say its
area?"), which suggested waiting until the reading went wrong often enough.
The user's request settles it: yes.

- **3.1** Move `AreaOfEffect` out of `Combat/Arena/areas.py` into
  `Model/Content/CombatArea.py` (`Model` must not import from `Combat`),
  as `CombatArea`: `shape`, `size_ft`, `width_ft`, `from_source`,
  `point_within_ft`, and the wall fields (`ring_ft`, `side_ft`, `panels`,
  `thick_ft`). Then add the lasting-area fields: `timing: frozenset`
  (ENTERS, MOVED_ONTO, STARTS, ENDS), `move_ft` / `move_action`,
  `terrain: MapObject | None` (blocks, cover, difficult) and `obscures`
  (DARKNESS, DEEP_DARKNESS, FOG). Strict `to_dict` / `from_dict`, like
  `CombatEffect`.
- **3.2** Where it lives (see Q1): `SpellRules.area` for the spell's area,
  and `CombatEffect.area` for a row whose area differs (Ice Knife's
  explosion) and for features and monster abilities.
- **3.3** Fill it with a one-off authoring script: run today's
  `parse_area`, `area_timing`, `move_rule`, `wall_terrain`, `area_obscures`
  and `point_range_ft` over every spell class, and write `area=` into each
  class whose reading finds one (215 spells today). Review a sample, plus
  every wall and every spell flagged in DI-096. Then move the parsers into
  `combat_effects.py draft` (a new `areas` subcommand), so a newly scraped
  spell still gets a drafted area to review.
- **3.4** The runtime reads only the fields: `arena_mixin.py`'s area, range,
  timing and move lookups, `lasting.py`, `senses.area_obscures` and
  `conditions_mixin.py`'s "is it an area" check. A kept area's record
  stores its `CombatArea` dict instead of the `about` text that it
  re-reads today. Old logs: `upgrade_old_keys` reads the text once, as it
  loads.
- **3.5** `ignores_cover` on `CombatEffect` (Sacred Flame), and the
  Sharpshooter and Spell Sniper feats as a modifier. Delete
  `_IGNORES_COVER`.

*Verify:* a one-time parity test written before the parsers move:
`spell.area == parse_area(text)` for every spell, run once and then deleted.
After that, the picker and arena goldens stay unchanged.

## Phase 4: monster stat-block fields, filled by the generator

The generated `monsters.py` files are never hand-edited, so the parse moves
into `Combat/Tools/generate_monsters.py`. It reads the scraped JSON once and
writes fields. Homebrew files get the same fields by hand, or through the
`monster-ability-converter` agent.

- **4.1** `ExtendedCombatantData`: `speed_swim_ft`, `speed_burrow_ft`,
  `hover`; `darkvision_ft`, `blindsight_ft`, `blind_beyond`,
  `truesight_ft`, `tremorsense_ft`, `passive_perception`; `spell_save_dc`
  and `spell_attack_bonus`. The `senses` and `speed_special_rules` strings
  stay for display only.
- **4.2** `MonsterAbility`: `recharge: int | None` (5 for "Recharge 5-6"),
  `per_day: int | None`, `legendary_cost: int = 1`, `at_turn_start: bool`,
  `casts: tuple[MonsterCast, ...]` and `uses: str`. The name keeps its
  "(Recharge 5-6)" for display, but the UI spends from the fields. This
  replaces the docstring rule "its recharge or uses per day stay in its
  name, which is what the combat UI spends".
- **4.3** Attack, save, damage and riders: the generator emits the
  structured subclasses (`MeleeAttack`, `SavingThrowEffect`, ...) where the
  sentence fits one. Otherwise it emits `combat_effects=(CombatEffect(...),)`,
  which `monster_actions.parse_action` already takes at its word. The
  regexes in `monster_actions.py` move into the generator.
- **4.4** Saved fights store abilities as plain dicts, so the new fields
  serialize. An old log's dict without them is upgraded once at load (the
  text read lives only there), or is re-read from the catalog by
  `combatant_type` (Q3).

*Verify:* regenerate, then `tests/test_picker_rows.py` must not change for
any homebrew monster or catalog row. Also run `monster_score.py` over a CR
tier before and after: the same scores.

## Phase 5: retire `EffectText`

`EffectText` reads a whole undescribed spell or feature. It goes away only
when nothing needs it. That is the combat-effects plan's content rollout
(Phase 4.3), which waits for the user's go (its Decision 9). Until then:

- **5.1** Freeze it: no new regexes in `EffectText`. A missing reading is
  fixed by describing the content, not by a new pattern (guard test G).
- **5.2** When coverage reaches every spell and party feature, delete
  `EffectText`. An undescribed source then gets a plain manual row (the
  GM fills in the dialog), and the readers move into
  `combat_effects.py draft`.

## Guard test G

Modelled on `tests/test_roll_sites.py`: `tests/test_text_readers.py` lists
every `re.` call under `Combat/` (outside `Combat/Tools/`) with its group
(F: input / log / validation, or a phase it waits on). A new one fails until
someone lists it, so the pattern can't creep back. Each phase removes its
entries.

## Open questions

- **Q1. Where does a spell's area live?** *Suggestion:* `SpellRules.area`.
  The area is a fact of the spell (the card's "Area" line could render from
  it too), and 215 spells have one while only 91 have combat effects.
  `CombatEffect.area` holds a row's own area. The alternative is
  `CombatEffect` only, which would leave undescribed spells without areas
  until Phase 5.
- **Q2. Order?** *Suggestion:* 1 → 2 → G → 3 → 4. Phases 1 and 2 are a day's
  work each and remove the self-parsing cases. Phase 3 touches 215 spell
  classes, and Phase 4 regenerates every catalog file. Run 3 and 4 one after
  the other, not in parallel, since both edit `arena_mixin.py` and
  `effect_options.py`.
- **Q3. Old logs in Phase 4.** *Suggestion:* upgrade the dicts at load with
  the old parse (the same pattern as `upgrade_old_keys`), so a logged
  fight replays even if the catalog changed since.

## Decisions

1. **Phase 3 first** (the user, 2026-11-19: "Fix 3 first").
2. **Q1: a spell's area is `SpellRules.area`**, a row's own or a feature's
   use's is `CombatEffect.area` (the suggestion, taken as the user didn't
   say otherwise).

## Revisions

- **R1. The model.** `Model/Content/CombatArea.py`: `CombatArea` (flat:
  shape, size, width, from source, point, `acts`, move, `obscures`, and a
  Wall's ring, side and terrain, checked to be a Wall's only) with
  `CombatAreaShape`, `AreaTiming`, `AreaCover`, `AreaSight`. The shape enum
  is named `CombatAreaShape`, not `AreaShape`, because spell modules import
  SpellFactory's `AreaShape` (a 2014 range's "Self (15-foot cone)", card
  text). `Combat/Arena/areas.py` imports it as `AreaShape`, so the map's
  code reads as before. `AreaOfEffect` stays the map's aimed geometry (it
  has the bar's `ring`); `area_of(rules)` gives one.
- **R2. The readers moved, they weren't deleted.** Every regex from
  `areas.py`, `lasting.py` and `senses.py` (area, point, ring, side,
  timing, move, wall terrain, sight) is in `Model/Content/CombatAreaText.py`
  (`read_combat_area`), used where content is written: the converter drafts
  a new spell's `area=` with it, and a one-off run wrote it into the 212
  spell classes whose text states one. Nothing in `Combat/Arena` reads
  rules text now.
- **R3. Phase 1.2 came along.** `spell_range_ft(spell)` (effect_options.py)
  reads `Range` (Touch as 5 feet); the text range regexes are gone.
- **R4. A kept record keeps its pick's CombatArea as "rules"**; "about" is
  only shown on the area panel. A record logged before has none:
  `record_rules` takes the CombatArea of the spell it was picked as (its
  "pick", or its active spell's name), so old fights keep acting as they
  did for spells; a feature's or a monster's old area falls back to the
  default timing.
- **R5. Parity.** A survey of every picker row (all 662 spells, both
  parties, the homebrew monsters: 1,085 rows) gave the same area, point or
  range, ring, side, timing, move, sight and wall terrain before and after
  for every spell. Three rows changed, on purpose: Radiance of the Dawn
  doesn't hide its space (the text reading took "magical Darkness ... is
  dispelled" for Darkness); Jolt to Life is a 10-foot Sphere on the
  creature revived (the reading made it an Emanation around the
  Artificer); Illuminated Cartography's Faerie Fire gets Faerie Fire's Cube
  (it had none). Picks that aren't areas (Shield, Message, Hide) no longer
  carry the wall, sight and move readings their text gave.
- **R6. 3.5, cover.** `CombatEffect.ignores_cover` (Sacred Flame's note
  became the field) and `EffectOption.ignores_cover`. The two spells still
  without combat effects that say it (Spellfire Flare, Soul Reap) are read
  by `EffectText` (the Phase 5 fallback), as the rest of their effect is.
  Sharpshooter and Spell Sniper didn't work before (their text is a feat's,
  not a pick's) and still don't: a modifier for them is still to do.
- **R7. Monster abilities keep their text reading for now.**
  `effect_options._monster_area` reads a stat block ability's description
  with `read_combat_area` (a CombatEffect written on it can say `area`
  instead), until Phase 4 gives stat blocks fields. Undescribed features
  get no area (none of the parties' has one); the GM picks the shape in
  the bar, as for a typed effect.
- **R8. Goldens.** `tests/test_picker_rows.py` now records a row's `area`
  and `ignores_cover` (only where set), so a change to a spell's area shows
  up in its diff.

Remaining text regexes under `Combat/` after Phase 3: group B (Phase 2),
group D (Phase 4, including `_monster_area` and `ranges.py`'s
"ranged spell attack"), group E (`EffectText`, Phase 5), and group F.

## Discovered issues

- DI-103: `test_the_target_label_says_when_a_target_is_obscured` fails on
  HEAD (dbf889cd), before this plan's changes.
