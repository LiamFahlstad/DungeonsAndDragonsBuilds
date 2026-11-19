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
| 1 | Read the fields that already exist (group A) | **Done** (2026-11-19): 1.2 with Phase 3 (R3), 1.1 and 1.3 (R10) |
| 2 | Our own `when` strings become fields (group B) | **Done** (2026-11-19, R11) |
| 3 | `CombatArea` for spells and features (group C) | **Done** (2026-11-19, R1-R8). 3.5 done for described spells; Sharpshooter and Spell Sniper not (R6) |
| 4 | Monster stat-block fields at generation time (group D) | **Done** (2026-11-19: R13, R14, R15, R16, Decisions 3 and 4) |
| 5 | Retire `EffectText` (group E) | Not started; waits on the content rollout |
| 6 | Text reads outside `Combat/` (group H) | **Done** (2026-11-19, R17) |
| G | A guard test that lists every remaining text regex | **Done** (2026-11-19, R12); widened in 6.4 |

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
  `combat-effects` skill's Triggers section
  .

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
  `casts: tuple[MonsterCast, ...]` and `uses: str` (as built: R14). The name keeps its
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

- **4.5** (added with R15) The last stat-block text the fight reads: a
  freeform ability's reach and range (`Arena/arena.py` and
  `Arena/ranges.py` `_REACH`, `_RANGE`; only a `MeleeAttack`'s,
  `RangedAttack`'s or `MeleeOrRangedAttack`'s are fields, R10) and
  `MonsterAction.attack_kind`, which reads whether the description starts
  "Melee" or "Ranged". *Suggestion:* `reach_ft`, `range_ft`,
  `long_range_ft` and `attack_kind` on `CombatEffect`, which a spell's
  attack could use too (the "later" `ranges._RANGED_SPELL` /
  `_MELEE_SPELL`), written the same way as 4.3's effects. *Done* (R16;
  `attack_kind` is a property, not a field).

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

## Phase 6: text reads outside `Combat/` (group H)

The inventory and guard test G looked only under `Combat/`. A survey of
the rest (2026-11-19, the user: "are regex and implicit information
extraction prominent anywhere else?") found two runtime reads of rules
text, one of our own display text, and the readers the survey of the first
one turned up:

| Where | Reads | Explicit home |
|---|---|---|
| `Model/Creatures/MonsterAbilities.py` `extract_dc_from_text`, `DcMonsterAbility.extract_dc`; `dialogs_mixin._ability_dc` | "DC 12" in a monster ability's description, for the More Info dialog's save-chance table (and a log's dict's) | the ability's `combat_effects` (Phase 4.3 wrote the DC there); a casting ability's stat block `spell_save_dc` |
| `Model/Content/Feature.py` `_DURATION_RE`, `FeatureActivation.duration_to_seconds` | a feature's `duration="1 Minute"` card text, for its badge's timer | a `FeatureDuration(amount, unit)` |
| `Model/Content/Feature.py` `_RANGE_SHAPE_RE` | a feature's `range="30-Foot Cone"`, split into range and shape for the card | `range=` and `range_shape=` written apart |
| `Model/Creatures/MonsterStatText.py` `read_spellcasting` (authoring) | "spell save DC 17" in actions and traits only | the same, in every section: a Vampire's Charm (a bonus action) gave its stat block no `spell_save_dc` |
| `Model/Creatures/MonsterAbilityText.py` `_CASTS` (authoring) | "casts Fear" but not "casts the Sleep spell" | the same, both wordings |

Everything else outside `Combat/` is display (`Html.py`'s damage-type
colours and tag stripping, `FeatureCards._LEVEL_LABEL`), validation (the
dice patterns in `CombatEffect.py` and `CombatModifiers.py`), or
authoring (`SpellFields.from_text`, `SpellClassConverter`, the `*Text.py`
readers, `Scrapers/`, `Combat/Tools/`).

- **6.1** The More Info dialog's probability table reads fields only: a
  structured attack's `attack_bonus` or save's `dc`, else the first effect
  that rolls an attack or a save with a number, else, for an ability that
  `casts`, the stat block's `spell_save_dc`. `extract_dc_from_text`,
  `DcMonsterAbility` (whose only job was `extract_dc`) and their regex go:
  a scripted rename makes every `DcMonsterAbility(` a `MonsterAbility(`
  (Decision 3: no regeneration), and the generator writes `MonsterAbility`.
  With it, `read_spellcasting` reads every action section and `_CASTS`
  reads "casts the Sleep spell", and the fields they add are inserted into
  the files.
- **6.2** `FeatureDuration(amount, unit, up_to=False, or_until="")` in
  `Model/Content/Feature.py`. Its `text` is the card's ("1 Minute", "Up to
  10 Minutes", "1 Minute or Until Incapacitated") and `seconds` the badge
  timer's. `FeatureActivation.duration` takes it or a plain string (no
  timer: "Until Start of Next Turn", "Proficiency Bonus Hours"). A one-off
  script rewrites every `duration="<number> <unit>..."`. `_DURATION_RE` goes.
- **6.3** The 28 features with `range="30-Foot Cone"` say
  `range="30 Feet", range_shape="Cone"`, which is what `__post_init__`
  made of it. `_RANGE_SHAPE_RE` goes.
- **6.4** Guard test G covers `Model/`, `Presentation/` and
  `CharacterContent/` as well as `Combat/`, with an "authoring" kind for
  readers that run only where content is written.

*Verify:* `tests/test_combat_ui_more_info.py` (its golden changes where a
table changes; each change explained), the monster text tests, the feature
card snapshots (no change from 6.2 or 6.3 unless a card's wording was
irregular), `tests/test_text_readers.py`.

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

- **Q4. How does Phase 4 write fields into the catalog?** Running
  `generate_monsters.py` today would undo every `monsters.py`'s later
  edits: a fresh run differs from the files by about 4,000 lines (1,751 in
  CR_0, 514 in CR_10, 389 in CR_17, 16-172 in the rest), the
  DcMonsterAbility wrappers in all 27 tiers and the structured subclasses
  in CR_0, CR_10 and CR_17. *Suggestion:* the generator learns to emit the
  new fields (so a future run keeps them), and a one-off script inserts
  the same keyword arguments into the existing files, as Phase 3 did for
  the spell classes, leaving every other line alone. The alternative,
  folding the later edits into the generator first, is a project of its
  own.

## Decisions

1. **Phase 3 first** (the user, 2026-11-19: "Fix 3 first").
2. **Q1: a spell's area is `SpellRules.area`**, a row's own or a feature's
   use's is `CombatEffect.area` (the suggestion, taken as the user didn't
   say otherwise).
3. **Q4: script insert** (the user, 2026-11-19). `generate_monsters.py`
   emits the new fields, and a one-off script adds the same keyword
   arguments to the existing `monsters.py` files, leaving every other line
   as it is. Nothing is regenerated.
4. **4.3: CombatEffect, not flat fields** (the user, 2026-11-19, over
   attack/save/damage fields on `MonsterAbility`). Each rolling ability gets
   `combat_effects=(CombatEffect(...), ...)`: its attack or save with its
   damage and the condition it gives, plus one HIT-triggered effect per
   condition its hit gives in a sentence of its own (the rider rows the
   picker already builds). One model for monsters, spells and features, so
   the picker's text-reading row path can go. Picker goldens may change
   where a described row says things differently from a text-read one;
   each change gets explained.

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
- **R9. The gaps, written from the rules (2026-11-19).** 22 more spells got
  `SpellRules.area`: the three Detects and Warp Sense (30-foot Emanation),
  Conjure Celestial, Conjure Animals, Conjure Elemental, Guardian of Faith,
  Spirit Shroud, Roar of Ursoc, Cordon of Arrows, Freezing Trap,
  Antipathy/Sympathy, Dark Star, Hallow, Grave Ground, Fire Storm, Forcecage,
  Tidal Wave (a 30-by-10 Wall, aimed by its ends), Mordenkainen's Private
  Sanctum, Temple of the Gods, Storm of Vengeance. 25 existing ones were
  corrected: false finds removed (Booming Blade's and Green-Flame Blade's
  2014 "Self (5-foot radius)" range; Ice Knife's area is now its explosion
  row's 5-foot Sphere), Emanations around a target made Spheres aimed at it
  (Hail of Thorns, Lightning Arrow, Searing Orb, Jim's Glowing Coin, Holy
  Weapon, Detonate), the area a lasting spell actually keeps (Investiture of
  Flame's and of Ice's aura, Pyrotechnics' smoke, Druid Grove's 90-foot
  Cube without its fog), `acts` and move fields an instant area had picked
  up removed (Fear, Illusory Dragon, Mold Earth, Wall of Water's misread
  ranged-attack line), and walls given their terrain, sight and timing
  (Wall of Stone and Wall of Ice block and give Total Cover; Prismatic Wall
  is 1 inch thick, a 30-foot globe, Total Cover, acts on entering; Wall of
  Sand, Thorns and Light are Heavily Obscured; Blade Barrier and Wall of
  Thorns act on entering and ending a turn; Tsunami moves 50 feet onto
  creatures). Four features got `area`: Turn Undead (30-foot Emanation),
  Divine Sense (60-foot Emanation), Elemental Burst (20-foot Sphere within
  120 feet) and Cinnamon Dragon breath (30-foot Cone). Left without one:
  Control Weather, Commune with Nature, Mirage Arcane (miles), Forbiddance
  (40,000 square feet of any shape), Find Traps and Hindsight (what's in
  range or sight), Shadow of Moil (dims light a step), Guardian of Nature
  (Difficult Terrain only), Bones of the Earth (2½-foot pillars), Detect
  Thoughts (its 30 feet is where it targets). Lightning Lure keeps its false
  area until its test moves (DI-104); what the model can't say is DI-105.

Remaining text regexes under `Combat/` after Phase 3: group B (Phase 2),
group D (Phase 4, including `_monster_area` and `ranges.py`'s
"ranged spell attack"), group E (`EffectText`, Phase 5), and group F.

- **R10. Phase 1.1 and 1.3 (2026-11-19).**
  - *1.1.* `MonsterAbilities.stated_reach_and_range(ability)` reads a
    MeleeAttack's, RangedAttack's or MeleeOrRangedAttack's `reach_ft`,
    `range_ft` and `long_range_ft`. It works on the ability or on its log
    dict, which `EncounterLogs._encode` writes with every field.
    `MonsterAction.stated_range` keeps them. `ranges.monster_action_range`
    is what the turn column and `pick_attack_range` call now, and
    `arena.reach_ft` reads the field too. `action_range` and `_REACH` stay
    only for a freeform `MonsterAbility`, whose text is all there is
    (Phase 4 gives those fields). A feature's tooltip still goes through
    `action_range` in `pick_attack_range`'s last line.
  - *1.3.* The text read was deleted, not kept for old logs: a log never
    holds a player's `"ac"` (`PLAYER_FIGHT_KEYS` doesn't list it; players
    are rebuilt from their build each time), so no old log has the
    sentence. `PlayerCombatant` writes `ac_without_shield`
    (`AC_WITHOUT_SHIELD_KEY`, None without a Shield), and Wild Shape sets
    it to None while in a form (the "kept" record puts it back).
    `"ac"` is now only shown.
  - *Goldens:* the plan said "no golden changes", but
    `tests/snapshots/combatants.json` gains the new key for every build
    (a number for the 52 with a Shield). Nothing else changed.
- **R11. Phase 2 (2026-11-19).**
  - *2.1:* `CombatTrigger` has `within_ft` and `sees`, for events with
    another creature only. `CombatTrigger.asks` says what's left to the GM
    (`asked_text`: "you can see it within 60 feet of you"). Fire Shield's
    distance was on a badge's `WhenHit`, not a trigger, so `WhenHit` got
    `within_ft` too. `triggers._asked` reads the fields. `settle_when`,
    `_WHEN_WITHIN` and `_WHEN_SEES` are deleted. The map's sight now
    settles `sees` even when the distance isn't known; before, it was only
    checked once the distance was settled. Moved to fields: Storm's Thunder
    (Goliath), Warding Flare, Hellish Rebuke, Fire Shield ×2, and the
    Molten Body trait of the CR 6 homebrew manifestation ("the attacker is
    within 5 feet of the manifestation", which the old regex never
    matched). The asked text now always ends "of you" (Goliath's was "it
    is within 60 feet").
  - *Found on the way:* `CombatEffect.from_dict` dropped a trigger's
    `others_within_ft` (Dark One's Blessing), so it was lost on a round
    trip. It's read now, with the new fields. A round-trip test is in
    `tests/test_arena_trigger_distances.py`.
  - *2.2:* `AttacksAgainst` and `CriticalHitsAgainst` have `within_ft` /
    `farther_than_ft` (Prone, Paralyzed, Unconscious in
    `RulesConditions.py`). `modifiers.settled_by_distance(modifier, feet)`
    reads them. When the map gives no distance, `_distance_asked` turns them
    into the same `when` text as before (`attacker_distance_text`), so
    the notes read as they did. `_WITHIN_FEET` and `_FARTHER_THAN_FEET` are
    deleted.
  - *2.3:* `trigger_problems` (run by `combat_effects.py check`) flags a
    trigger's or a `WhenHit`'s `when` that says "within N feet" or "you
    can see it". The `combat-effects` skill's Triggers section says to use
    the fields instead. Picker goldens changed only in those four rows'
    trigger dicts.

- **R12. Guard test G (2026-11-19).** `tests/test_text_readers.py` lists
  every `re.` call under `Combat/` (outside `Combat/Tools/`) by the module
  constant or function it's in: 95 entries, each "input", "log",
  "validation", "phase 4", "phase 5" or "later: <what it reads>". Five
  read rules text no phase covers yet ("later"): `ranges._RANGED_SPELL` and
  `_MELEE_SPELL` (a spell's attack kind; Spiritual Weapon and Flame Blade
  mean it isn't a function of the range), `effect_options._NOT_ALWAYS` (a
  weapon's extra damage note), `monster_actions.first_number` (a player's
  AC is still read from the sheet's sentence by `attack_rolls` and
  `damage_mixin`, so R10's "`ac` is now only shown" isn't quite true) and
  `WildShape._MATERIAL_COST` (a spell's costly Material component).
  `Model/Content/CombatAreaText.py` is outside `Combat/` and authoring-time,
  so it isn't listed.

- **R13. Phase 4.1 (2026-11-19).**
  - *Fields:* ExtendedCombatantData has `speed_swim_ft`,
    `speed_burrow_ft`, `hover`, `darkvision_ft`, `blindsight_ft`,
    `blind_beyond`, `truesight_ft`, `tremorsense_ft`, `passive_perception`,
    `spell_save_dc` and `spell_attack_bonus` (None / False by default).
    `combatant_from_stat_block` puts them on the combat dict, and Wild
    Shape takes a form's (its `passive_perception` is the Druid's).
  - *Readers:* `Model/Creatures/MonsterStatText.py` (`read_stat_block`)
    holds the regexes that were in `speeds.py`, `senses.py` and `saves.py`.
    It's used by `generate_monsters.py`, which now writes the fields after
    the `speed_special_rules` and `senses` lines (only the ones the text
    gives), by a one-off scratch script that wrote the same lines into the
    existing files (Decision 3: 718 insertions in 27 `monsters.py`, 12
    `monsters_homebrew.py` and 7 summon builders in CharacterContent), and
    by `upgrade_stat_block_keys`, which reads an old log's monster once as
    it loads (Q3's suggestion, taken). `speeds.py`, `senses.py` and
    `saves.known_save_dc` / `known_spell_attack_bonus` read only fields;
    the DC - 8 fallback for a stat block that gives only a DC stays.
  - *Parity:* all 554 catalog and homebrew stat blocks have fields equal
    to their text's reading (kept as
    `tests/test_monster_stat_text.py::test_every_stat_blocks_fields_say_what_its_text_says`,
    which also stops a new homebrew monster from having the text without
    the fields), and a fresh generator run differs from the files by
    exactly as many lines as before. Picker goldens unchanged. Tests that
    built monster dicts from text (arena senses and speeds, the custom
    effect DCs, the two CASTER fixtures) now set the fields.
  - *Changed on purpose:* four CR_0 spirits whose speeds are per form
    ("Fly 60 ft. (Air only)") lost the Fly Speed the old regex read out of
    the speed text, since a Fly Speed has its own field (DI-106).
  - `WildShape._PASSIVE_PERCEPTION` stays, now as display: it rewrites the
    shown senses to match the field.

- **R14. Phase 4.2 (2026-11-19).**
  - *Fields* (`Model/Creatures/MonsterAbilities.py`, keyword-only on
    `MonsterAbility`): `recharge`, `per_day`, `legendary_cost` (1),
    `at_turn_start`, `casts` (`MonsterCast(spell, level, per_day)`),
    `uses_ability` and `moves_first`. Three differ from the plan:
    `at_turn_start` is the sentence the turn column reminds of, not a bool
    (a bool would have meant finding the sentence in the text again);
    `uses` is `uses_ability`, as `LegendaryResistance` already has a
    `uses: int`; and `moves_first` is new ("moves up to half its Speed,
    and it makes one Rend attack": the row's note says to move it first).
    `ability_field(ability, name)` reads one from an ability or its log
    dict.
  - *Readers:* `Model/Creatures/MonsterAbilityText.py` (`read_ability`)
    holds the regexes that were in `monster_actions.py` (`_RECHARGE`,
    `_PER_DAY`, `_LEGENDARY_COST`, `_START_OF_TURN`) and `effect_options.py`
    (`_CASTS`, `_LIST_ITEM`, `_AT_LEVEL`, `_FOLLOWING`, `_SPELL_LIST`,
    `_MAKES_ONE`, `_USES`, `_MOVES`). `monster_actions.read_ability_fields`
    gives it what only a whole stat block knows (the names another ability
    can use, whether this one rolls of its own). It's used by
    `generate_monsters.py` (`format_ability_list` writes the keywords), a
    one-off scratch script that wrote them into the existing files
    (Decision 3: 37 files, 544 fields: 148 recharge, 118 per day, 4
    legendary costs, 18 turn starts, 101 casts, 128 uses, 27 moves first),
    and `upgrade_ability_keys` as a log loads. Two summons got `per_day`
    by hand (the Steel Defender's Repair, the Vestige's Divine Power).
  - *Logs:* `EncounterLogs._encode` leaves the fields out at their
    defaults, as it does `combat_effects`, so a log reads as before. An
    ability dict with none of them is read once as it loads (Q3); for a new
    log's that gives the defaults again, since
    `tests/test_monster_ability_text.py::test_every_abilitys_fields_say_what_its_text_says`
    holds every catalog and homebrew ability's fields to its text.
  - *Parity:* every picker row, parsed action and turn-start reminder of
    all 554 stat blocks was dumped before and after, and again after a
    round trip through an old-style log: the same, apart from three notes.
    Priest of the Black Tongues' Hold Person and Silence say "(2/Day)",
    not "(2/Day each)". The Mummy Lord's Multiattack ("makes one Rotting
    Fist or Channel Negative Energy attack, and it uses Dreadful Glare")
    says "It uses Dreadful Glare", not "It makes one Dreadful Glare
    attack": the verb now comes from whether the used ability is an
    attack, not from any "makes one" in the text. Picker goldens
    unchanged. A fresh generator run writes the same fields as the files.
  - *Found:* DI-107, abilities that recharge after a rest have no
    `per_day`, as before.
  - The name still says "(Recharge 5-6)", which `effect_options._NAME_ALONE`
    takes off for a row's name (now listed as "log").
  - *Correction (found in 4.3):* `upgrade_ability_keys` was never called as
    a log loads, so an old log's abilities lost their recharge, uses and
    casts. `logging_mixin` calls it now, after `upgrade_stat_block_keys`.

- **R15. Phase 4.3 (2026-11-19, Decision 4).**
  - *Model:* nothing new. Each action-section ability (actions, bonus
    actions, reactions, legendary actions) with something to apply has
    `combat_effects`: its own effect (attack or save, damage with a damage
    type or `choices`, the condition its outcome gives and until when,
    Hit Points, area, repeat save, and an "Also: ..." note with what's
    left), then a HIT-triggered `spends_use=False` effect per condition its
    hit gives in a sentence of its own (what `_rider_options` built), and
    one for a save its hit forces. That last one is new: "Hit: ... If the
    target is a creature that isn't an Undead or elf, it is subjected to the
    following effect. Constitution Saving Throw: DC 10. Failure: ...
    Paralyzed" was one note ("apply it apart"); now it's a row with its DC,
    condition and duration, its `when` the gate, and its own area. A "Hit
    or Miss:" save (the Dao's Earth Burst) is a USES row instead, as Ice
    Knife's explosion is. Not read: an ability that `casts` or has
    `uses_ability` (those rows come first, as before) or already has
    effects.
  - *Readers:* `Combat/Tools/monster_effect_text.py` (`read_effects`,
    `read_ability_effects`, and `read_ability_fields`, moved from
    `monster_actions`) holds `_ATTACK`, `_SAVE`, `_CONDITIONAL`, the rider
    regexes and `_damage_rolls` from `monster_actions.py`, and `_HIT_ENDS` /
    `_monster_action_condition` from `effect_options.py`. It still borrows
    `_inflicted_condition`, `_read_gain` and `_REPEATS_THE_SAVE` from
    EffectText (Phase 5), and `DAMAGE`, `JOINED`, `tidy_dice` stay in
    `monster_actions` for EffectText (relisted as "phase 5"; `DIE` as
    "input"). It's in `Combat/Tools/` rather than `Model/` (where 4.1's and
    4.2's are) because of those borrowings. `python -m
    Combat.Tools.monster_effect_text "Name" "text"` drafts a hand-written
    ability's effects. `generate_monsters.py` writes them (its header now
    imports what they use), a one-off scratch script inserted them into the
    files (999 abilities, 1,119 effects: 936 in 27 `monsters.py`, 63 in 10
    `monsters_homebrew.py`), and `upgrade_ability_keys` reads an old log's
    once. `SpellClassConverter._IMPORTS` gained `CombatTrigger`,
    `TriggerEvent` and `CreatureSize`, which any written trigger needs.
  - *Runtime:* `parse_action` reads only effects and fields (the first
    effect, or for an attack the save after it); `MonsterAction.rider` /
    `riders` became `notes` (the first effect's, shown by the turn column as
    it hits). `effect_options` lost the text row path (`_monster_action_condition`,
    `_monster_action_notes`, `_rider_options`, `_monster_area`): an
    ability without effects is a plain row (Multiattack). A HIT- or
    USES-triggered row says when ("on a hit, Large or smaller") and, as
    before, spends nothing, isn't greyed out by its attack's spent recharge,
    and has no `monster_action`.
  - *Summons* (hand-written, their numbers follow the owner through
    `MonsterAbilities.dice_plus`): Steel Defender's Rend and Repair, the
    Wildfire Spirit's Flame Seed and Fiery Teleportation (both missed by
    any reader: 2014 "Ranged Weapon Attack" and an old-style save), Vestige's
    Strike, Beast's Strike (the Land beast's charge is a HIT row with its
    `when`, not an unconditional Prone), Dreadful Swipe, the drake's Bite.
  - *By hand in homebrew:* the Cantor of the Black Choir's Speak Noc'tra is
    now a DC 11 Wisdom save (old-style prose: before, a save row with no
    ability and "half on save"), and the Manifestation of Durmor's Eruption
    got its 20-foot Emanation (the text reading gave it before).
  - *Parity:* every picker row and turn-column reading of all 554 stat
    blocks dumped before and after. The same, apart from: 1,195 rows now
    `is_described` (from data, not text); 594 summaries in the described
    rows' style ("+4  1d6 + 2 Piercing + 1d4 Thunder", "DC 12 STR", the
    condition named); 37 notes (reordered, "Its damage is of a type to
    choose (Necrotic, Radiant)" for "It chooses a damage type", a listed
    choice like the kobold's five types now taken as listed); the 20 new
    forced-save rows; 3 "uses Breath Weapon" rows that now carry the
    breath's Cone; the Dao's attack no longer claiming its burst's area; the
    Cantor. Picker goldens: 7 lines in the 4 homebrew monsters' files
    (`is_described`, two summaries). A fresh generator run writes as many
    effects per tier as the files have.
  - *Tests:* `tests/test_monster_effect_text.py` (the reader; every
    generated ability's effects equal its text's reading; no catalog,
    homebrew or summon ability with a roll in its text lacks effects; logs;
    the generator). Tests that built monsters from bare text now give them
    effects through `tests/_combat_ui.described()`, as the generator would.
    `tests/test_spell_combat_effects.py`'s CASTER got the 4.1 fields it had
    missed (`test_fireball` and `test_guiding_bolt` failed on HEAD since R13).
  - *Left:* 4.5 (a freeform ability's reach and range, an attack's kind).

- **R16. Phase 4.5 (2026-11-19).**
  - *Model:* `CombatEffect.reach_ft`, `range_ft`, `long_range_ft`, for an
    `attack` only (positive feet; `long_range_ft` with a shorter
    `range_ft`). `attack_kind` is a property, not the suggested field: only
    a reach is MELEE, only a range RANGED, both (or neither) None
    (`attack_kind_of`). A field would repeat what the two already say, and
    could disagree with them. A melee spell attack's reach measured from
    something other than its caster (Spiritual Weapon) is still a "later"
    question, not a question of kind.
  - *Readers:* `monster_effect_text.read_reach_and_range` holds the regexes
    that were in `arena.py` (`_REACH`) and `ranges.py` (`_REACH`, `_RANGE`).
    It reads only the part before "Hit:" (the old ones searched the whole
    text, though no stat block had a reach or range after its "Hit:") and
    takes "feet" as well as "ft." (the Eagle's and Giant Rat's "reach 5
    feet", which the old ones missed). `read_effects` writes the fields on an
    attack's own effect, so `generate_monsters.py` emits them. A one-off
    scratch script inserted them into the files (Decision 3: 650 effects,
    781 lines in 27 `monsters.py` and 8 `monsters_homebrew.py`; only the
    keyword lines, nothing else). In homebrew it skipped structured attacks,
    whose own `reach_ft` / `range_ft` already say it. Seven summons got them
    by hand. `upgrade_ability_keys` reads an old log's attack effect once
    when it states neither (a log from after 4.3) and its ability is not a
    structured attack.
  - *Runtime:* `MonsterAbilities.stated_reach_and_range` gives the first
    attack effect's fields, else a structured attack's own
    (`own_reach_and_range`). `MonsterAction.attack_kind` comes from them,
    not from how the description starts. `ranges.action_range` is
    deleted: `monster_action_range` reads only `stated_range`;
    `arena.reach_ft` reads only fields; `EffectOption.reach_and_range`
    (from a described row's effect) is what `pick_attack_range` takes for
    a row before its monster action. Its last line, `action_range` on the
    tooltip, is gone too: no party feature's row got a range from it.
  - *Parity:* every stat block's (561, each also round-tripped through a
    log) and both parties' reach, opportunity-attack row, actions' kind and
    range, and picker rows' attack range, before and after: 107
    differences, the same for each stat block and its logged copy, of
    three kinds. (1) Gains: 77 rows made from another ability's attack
    (Multiattack, Pounce, Tail Swipe, Rampage, Riposte, Arcane Prowl, ...)
    now carry that attack's reach. Before, they had no `monster_action` and
    their tooltip didn't say it, so the map never checked their reach. The
    Eagle's and Giant Rat's "5 feet" are read (their action and row). The
    Mouth That Walks' Chain-Wracked Lash, whose text starts with flavour,
    is now a melee attack. (2) The Dancing Item (College of Creation's
    summon) had no effects: its 2014-style "Melee Weapon Attack" was missed
    in 4.3, so it never rolled. It has them now (its action, row and
    opportunity-attack row). (3) Losses: 21 abilities with no attack effect
    lost a range nothing used (it only feeds attacks). One of them matters:
    the catalog's 2024 spell summons, whose "Bonus equals your spell
    attack modifier" attacks have no effects, so Giant Insect's reach is
    5 ft., not 10 (DI-108). Picker goldens unchanged (they don't record
    ranges).
  - *Tests:* `tests/test_arena_ranges.py` (the reader, the fields, a
    freeform attack's effect, a log dict, the text alone giving nothing),
    `tests/test_monster_effect_text.py` (an old log's attack is upgraded
    once; `test_every_attack_says_how_far_it_goes` holds every catalog,
    homebrew and summon attack's reach and range to its text). Tests that
    gave a monster its reach in text only now give the effect's field.
    Guard test G lost its three "phase 4" entries.

Remaining text regexes under `Combat/` after Phase 4: group E (`EffectText`,
Phase 5), the five "later" ones (R12), and group F.

- **R17. Phase 6 (2026-11-19).**
  - *6.1, the More Info dialog.* `dialogs_mixin._ability_roll(ab, char)`
    gives the table's ("hit", bonus) or ("save", DC) from fields only: a
    structured attack's `attack_bonus` or save's `dc`, the first effect
    that rolls an attack or a save with a number, or for an ability with
    `casts` the stat block's `spell_save_dc` (so `_add_monster_ability`
    now takes the combatant). `extract_dc_from_text`, `_DC_PATTERN` and
    `DcMonsterAbility` are deleted. A one-off script made its 484 uses
    `MonsterAbility` (37 files, their imports, and the header paragraph
    that listed the wrapped classes); the generator never wrote it, so a
    fresh run is now closer to the files. `SavingThrowEffect` derives from
    `MonsterAbility`. The `monster-stat-blocks` skill says to give a
    free-text save its effect instead.
  - *Found and fixed with it:* `read_spellcasting` read only actions and
    traits, so six stat blocks whose casting is a bonus or legendary action
    (Kenku, Stone Golem, Adult and Ancient White Dragon, Vampire, Drider)
    had no `spell_save_dc`, and their cast rows no DC. It reads every
    section now (actions and traits first, so no DC already read changed;
    `read_stat_block` takes the block). `_CASTS` missed "casts the Sleep
    spell": seven abilities (Dust Mephit's Sleep, Vine Blight's Entangle,
    Stone Golem's Slow, Cultist Fanatic's Spiritual Weapon, Ghost's
    Etherealness, Cloaker's Mirror Image, Cloud Giant's Misty Step) now
    `casts`, so they're cast rows. 13 lines inserted (Decision 3); a fresh
    generator run writes the same `spell_save_dc`, `casts` and no wrapper.
  - *Table survey* (every ability of the 554 catalog and homebrew stat
    blocks, before and after): 464 freeform attacks gain a hit table
    (before, only a structured attack had one); 82 abilities gain a save
    table (a save effect on a plain `MonsterAbility`, or a cast with its
    stat block's DC, such as Counterspell); 62 attacks whose table was
    their rider's save DC (Banishing Claw, the Ghoul's Claw) now show their
    attack. Lost, for want of a field: 108 catalog casting entries with no
    `casts`, nearly all "Spellcasting" whose scraped spell list stops at
    the colon (DI-035), and the hags' Coven Magic traits; 33 traits (Death
    Burst; DI-110), some of whose DCs were checks, not saves (Kenku's
    Mimicry); and 22 homebrew abilities in older save prose that never got
    their save effect (DI-109), some of whose DCs were escape DCs (the
    Accursed's Grab). Goldens:
    `combat_ui_more_info.json` (Arcanaloth live and from a log, Shadow
    Demon, Swarm of Bats, Sphinx of Valor, as above).
  - *6.2, durations.* `FeatureDuration(amount, unit, up_to, or_until)` and
    `TimeUnit` in `Model/Content/Feature.py`; `FeatureActivation.duration`
    is one or plain text, `duration_text` the card's tag and
    `duration_to_seconds()` its `seconds` or None. A one-off AST-guided
    script rewrote 107 durations in 90 files; 42 wordings stay text
    ("Until Start of Next Turn", "Proficiency Bonus Hours", "1 Hour (8
    Hours if Enhanced)", "For 10 Minutes"). Changed on purpose: the 33
    "N or Until ..." durations now get a badge timer of their whole length
    (before, only a bare "1 Minute" did; Kivi's Elemental Attunement is the
    picker golden's one change: `duration_seconds` 600), and two cards read
    "or" and "Up to" for "Or" and "Up To".
  - *6.3, shapes.* 28 `range="30-Foot Emanation"` became `range="30 Feet",
    range_shape="Emanation"`; Dragonborn's "15-Foot Cone or 30-Foot Line"
    was never split and stays.
  - *6.4, guard test G* covers Combat/ (outside Tools), Model/,
    Presentation/, CharacterContent/, Core/, Utils/ and Builds/. New kind:
    AUTHORING, whole modules that read text only where content is written
    (CombatAreaText, MonsterStatText, MonsterAbilityText, SpellFields,
    DataSpell, SpellClassConverter, SpellGenerator), with a test that each
    is there and still reads text. New entries: the card display regexes
    ("log"), CombatEffect's and CombatModifiers' dice and the check's
    `_FIELD_IN_WHEN` ("validation"). The "phase 4" kind is gone.
  - *Also fixed (DI-111):* two tests failing on HEAD since R14.
    `test_imports_point_down`: `MonsterAbilityText.py` (Model) imported
    CharacterContent for its spell list; `spell_name_in_list` moved to
    `Combat/Tools/monster_effect_text.py`, and `read_ability` takes
    `spell_named` as required. `test_with_the_setting_off_a_recharge_is_a_reminder`:
    its ability dict had no `recharge` field.
  - *Full suite:* 1 failure left, DI-103 (open, from before this plan).

Remaining text reads at runtime after Phase 6: group E (`EffectText`, Phase
5), the five "later" ones (R12), and group F, all listed by guard test G.

## Discovered issues

- DI-103: `test_the_target_label_says_when_a_target_is_obscured` fails on
  HEAD (dbf889cd), before this plan's changes.
- DI-104: a test asserts Lightning Lure's false area (R9).
- DI-106: a summoned spirit's form-only speeds (R13).
- DI-107: abilities that recharge after a rest aren't spent (R14).
- DI-105: what `CombatArea` can't say yet, found writing R9's areas. Its
  plan: [combat-area-gaps-plan.md](combat-area-gaps-plan.md).
- DI-108: the catalog's 2024 spell-summon stat blocks have no combat
  effects, so their attacks don't roll and their reach isn't known (R16).
- DI-109: homebrew abilities in older save prose have no save effects (R17).
- DI-110: traits that roll a save (Death Burst) have no effects (R17).
- DI-111 (fixed): two tests failing since R14 (R17).
- DI-035 (older): catalog Spellcasting entries lost their spell lists, so
  they have no `casts` and, since 6.1, no DC table (R17).
