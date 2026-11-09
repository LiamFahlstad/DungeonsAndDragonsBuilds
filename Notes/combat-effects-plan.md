# Plan: one way to say what Features and Spells do in a fight

## How to use this document

This is a living plan. Whoever works on combat effects updates it in the same
change:

- tick the step in **Status**;
- when the code shows a better way than the plan, do the better thing and
  write down what changed and why in **Revisions**;
- add new questions to **Open questions** (with a suggestion), and move them
  to **Decisions** once answered;
- log bugs found along the way with the `discovered-issues` skill and list
  their ids in **Discovered issues**.

## Status (2026-11-09, late night)

| Phase | Step | State |
|---|---|---|
| 1 | 1.1 Scaling amounts on `CombatEffect` (`CombatHitPoints`; `upcast`, `cantrip`, `add_modifier` on `CombatDamage`) | **Done** |
| 1 | 1.2 Strict `to_dict()` / `from_dict(data, where)`, tolerant of old logs | **Done** |
| 1 | 1.3 `Spell.combat_effects()`; `DataSpell` reads its entry | **Done** |
| 1 | 1.4 Text reading returns a draft `CombatEffect` | **Dropped** (R4) |
| 1 | 1.5 One converter for described spells, features and monster abilities | **Done** (`_described_option`; R5) |
| 1 | 1.6 Migrate the spell JSON, delete `SpellMechanics` | **Done** |
| 2 | Q1 Golden picker rows as a test | **Done**: `tests/test_picker_rows.py`, one golden per party member, homebrew monster and all described spells, in `tests/snapshots/picker_rows/` |
| 2 | 2.1 Several conditions (`conditions` tuple) | **Done** (R12, R13). Damage plus Hit Points together: **dropped** (R9) |
| 2 | 2.2 Dialog applies every condition; one repeat save ends them all | **Done**. The second amount box: dropped (R9) |
| 2 | 2.3 `instances` and a Times box in the dialog | **Done** |
| 2 | 2.4 Spell variants (a row per effect) | **Done** (Q3 resolved as suggested; R15) |
| 2 | 2.5 A use that casts a spell takes the spell's effect | **Done** |
| 2 | 2.6 `Feature.adjust_combat_effect` hook | **Done** |
| 2 | 2.7 Conditional extra damage (`when`) | **Done**, as a generated note (R14) |
| 2 | Extensions list their own uses under their parent | **Done** (R10, new) |
| S | **Spells as classes** (new direction, 2026-11-09; see its section) | S.1 base class, factory and converter **done**; S.2 the 57 spells with combat effects converted **done**; S.2c card lines as dataclasses **done** (R20); S.3 new effects go into classes **done** (R22); S.5 drift check **done** (R23); S.4 not started |
| 3 | Lasting effects (3.1-3.6) | Not started |
| 4 | One `combat-effects` skill; feature agent; content rollout | Partly: the skill's rubric and script cover every new field; first content batch below |
| 5 | Sheet chips, monster score | Not started |

**Content described so far.** Spells: 57 (2024) + 1 (2014), all as classes;
Lightning Bolt (2026-11-09) was the first written through S.3's `add`. Added
2026-11-09: Burning Hands, Charm Person, Chill Touch, Command (5 options),
Divine Smite, Sacred Flame, Scorching Ray, Shield of Faith; upgraded from notes
to fields: Eldritch Blast and Magic Missile (`instances`), Ice Knife (two
steps), Tasha's Hideous Laughter (two conditions), Toll the Dead (a row for a
hurt target). Features of the Curse of the Lich party: Channel Divinity (Divine
Spark heal and harm, Turn Undead), Radiance of the Dawn, Warding Flare, Lay on
Hands, Paladin's Smite, Sneak Attack.

**Verified 2026-11-09 (after S.3):** full suite passes (9,917); every
picker-row change reviewed field by field against the previous golden.

## Decisions

Accepted as recommended when the user said "go ahead with plan" (2026-11-08):

1. **Spells stay JSON, features stay Python**, in one shared format.
2. **`CombatEffect` stays flat** (`roll=EffectRoll.SAVE, save_ability=...`).
3. **Several attacks from one use get a repeat count in the dialog** (built:
   the Times box).
4. **Modifiers are added automatically to rolls the simulator makes**, and
   shown as a reminder next to totals typed in from the table (Phase 3).
5. **Lasting effects are plain dicts on the combatant**, so undo and log
   replay keep working (Phase 3).

"Continue and do as you recommend" (2026-11-09) accepted Q1 and Q3 as
suggested.

6. **Spells become classes, like Features, with the JSON as the fallback when
   a spell has no class** (the user, 2026-11-09: "spells in JSON format have
   reached their limit"). This replaces Decision 1 for spells: a spell's
   rules, improved description and combat effects are Python in its class;
   the scraped JSON stays as the source of record for spells not converted
   yet. See "Spells as classes".
7. **Q12 as suggested** ("continue with plan", 2026-11-09): a converted
   class carries a hash of the record it came from, and a test lists every
   class whose record changed since, for a person to merge by hand. Built
   in S.5 (R23).

## Goal

The Custom Effect dialog is what the GM uses for almost everything in a fight.
Whatever is picked in it (a spell, a feature, a monster's ability, a weapon)
should be filled in **by one model, through one code path**, so that:

1. a spell and a feature that do the same kind of thing are written the same
   way and fill the form the same way;
2. adding a new kind of mechanic means changing one model, one validator and
   one adapter, not three of each;
3. the same descriptions can later drive **mechanical effects**: Bless adding
   1d4 to the saves the simulator rolls, Shield raising AC until the caster's
   next turn, Rage halving damage, Hunter's Mark adding 1d6 to hits.

## Design principles

1. **One vocabulary.** `CombatEffect` and its parts describe what a use does.
   Spells, features, monster abilities (and later weapons) all produce it.
2. **Python first, one format.** Features and spells with a class write it in
   Python; a spell not converted yet can still have a JSON entry, exactly
   what `to_dict()` writes and `from_dict()` reads, and fight logs store the
   same fields. One validator checks all of them. (Was "features in Python,
   spells in JSON" until Decision 6.)
3. **The model describes the rules, not the form.** The adapter that fills the
   dialog decides what fits and turns the rest into notes.
4. **Content never imports Combat.** The vocabulary lives in `Model/Content/`.
5. **Caster numbers are worked out when used** (DC, attack bonus, spellcasting
   modifier, slot and character level). A feature may work out its own.
6. **`None`, `[]` and a list mean the same everywhere.** Not described yet /
   nothing to apply / one picker row per item.
7. **Notes are the escape hatch, and a repeated note is a missing field.**
8. **The simulator never guesses positions or table decisions:** it prompts
   with a pre-filled form.
9. **Order doesn't matter** for `adjust_combat_effect` hooks: they only add.
10. **Nothing lands on a target unless the effect says so.** No implicit
    badges.
11. **An extension's uses are its parent's** (R10): an extension that describes
    combat effects adds rows under its parent and spends the parent's uses
    unless it has its own; one that only changes the parent uses the hook.

## The design as built

### The model (`Model/Content/CombatEffect.py`)

```python
CombatDamage(dice, damage_type, choices=(), upcast="", cantrip=(), add_modifier=False, when="")
CombatHitPoints(dice="", upcast="", add_modifier=False)   # dice "": the user types it
CombatCondition(name, until=None, duration_seconds=None)  # a rules condition or a badge
                                    # until=(TurnEdge.END, TurnOf.TARGET): "until the end of its next turn"
CombatInstances(count, upcast=0, cantrip=(), noun="")     # Scorching Ray: 3, +1 per slot, "ray"
CombatEffect(
    name="", roll=EffectRoll.NONE, save_ability=None, dc=None, half_on_success=False,
    repeat_save=False, attack_bonus=None,
    damage=(), healing=None, temp_hp=None, conditions=(), instances=None,
    action_type=None, concentration=False, spends_use=True, spell=None, notes=(),
)
with_bonus("1d8", 4) == "1d8 + 4"
```

- `from_dict` still reads logs from before: hit points as plain dice text,
  cantrip steps as pairs, and one `"condition"` (read as `conditions`).
- `spends_use=False` on a spell's effect: a later step of one casting (Ice
  Knife's explosion), which spends no slot, action or cast.

### A spell's entry

```json
"Scorching Ray": [
  {"roll": "attack", "damage": [{"dice": "2d6", "damage_type": "Fire"}],
   "instances": {"count": 3, "upcast": 1, "noun": "ray"}}
],
"Command": [
  {"name": "Command: Grovel", "roll": "save", "save_ability": "Wisdom",
   "conditions": [{"name": "Prone"}]},
  ...
],
"Divine Smite": [
  {"damage": [{"dice": "2d8", "damage_type": "Radiant", "upcast": "1d8"},
              {"dice": "1d8", "damage_type": "Radiant", "when": "the target is a Fiend or an Undead"}]}
],
"Alarm": []
```

### The picker (`Combat/CombatUIQt/effect_options.py`)

- `spell_options(spell, char)`: `None` → the text reading; `[]` → a row that
  only spends the cast; else one row per effect. Every spell row carries
  `spell_name`; `counts_uses` says whether it spends a cast. `spell_option` is
  the first row.
- `feature_options(char, feature)`: its own rows (or the text reading), then
  `_extension_options`: each described extension's rows, spending the parent's
  uses unless the extension has its own.
- `_described_feature_option`: a use with `spell=` takes that spell's effect
  (`_casting`); defaults come from the effect, then the feature (or its
  parent), then the spell. Then the hooks (`_adjusted`).
- `_described_option` fills the `EffectOption`. Several conditions are joined
  with `CONDITION_JOINER` (" + ") into its `condition`; `instances` and
  `instances_upcast` give the Times count (`instances_at(slot)`); damage with a
  `when` becomes a note ("If the target is a Fiend or an Undead: 1d8 Radiant
  more (1d8 more per slot level above 1). Add it for those targets.").
- A monster's spells: a row per way to cast each (`_monster_spell_options`).

### The dialog (`Combat/CombatUIQt/conditions_mixin.py`)

- **Condition box:** "Frightened + Incapacitated" gives both; each is matched
  to a rules condition by name. One repeat-save entry per effect holds the
  first condition and `"also"` the rest; a successful save ends them all
  (`PartyAllies.py` and `Summons.py` read `also` too).
- **Times box** (Damage section): filled from the pick, and from the slot as
  it changes; Apply repeats the effect that many times against each target,
  each with its own attack roll, save and damage roll, named "Scorching Ray
  (2 of 3)" in the log. Only the first costs anything; it's one undo step
  (`_apply_custom_effects`).
- **Spending a spell row** uses `spell_name`, not the row's name.

## Spells as classes (new direction, 2026-11-09)

**Why.** The JSON was enough for what a form shows, but the next steps need
what data can't say well: an effect that depends on the caster (a choice
made at casting, a subclass feature), shared helpers (dice at a slot), the
Phase 3 modifiers and triggers, summons, and one place to read a spell
whole. Features already do all this as classes. Spells should work the same
way, so a spell and a feature read alike and use the same tools.

**What it looks like.** `CharacterContent/Spells/SpellFactory/ClassSpell.py`:

```python
class Fireball(ClassSpell):
    rules = SpellRules(
        name="Fireball", level=3, school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(verbal=True, somatic=True,
                              material="a ball of bat guano and sulfur"),
        duration=Duration(DurationType.INSTANTANEOUS), source="Player's Handbook",
        description=("...\n" "Using a Higher-Level Spell Slot. ..."),
        usage_tags=("damage",), target=FeatureTarget.AREA,
    )

    @property
    def improved_description(self) -> list[Block]:
        return [Facts(...), Table(...), Option("Using a Higher-Level Spell Slot", (...))]

    def combat_effects(self, character=None) -> list[CombatEffect]:
        return [CombatEffect(roll=EffectRoll.SAVE, save_ability=Ability.DEXTERITY, ...)]
```

- `SpellRules` is the record's fields plus `usage_tags` and `target`; what the
  spell does is methods, as on a Feature. Per-grant data (casting ability,
  ruling, grant source) stays the constructor's, as for every Spell.
- **What has a fixed set of values is an enum** (R19): `school` a `School`,
  `classes` `CharacterClass`es, `usage_tags` the shared `UsageTag` literal
  (as on Feature), `target` a `FeatureTarget`, and in combat effects a rules
  condition is `CombatCondition(Condition.PRONE)` (a badge keeps its text
  name), `roll` an `EffectRoll` and `until` a `(TurnEdge, TurnOf)` pair (R21). `ClassSpell` turns them back into the card's text, so the `Spell`
  interface is unchanged. `source` stays the source's words (Q14).
- **The card's four top lines are dataclasses** (R20,
  `SpellFactory/SpellFields.py`): `CastingTime`, `Range`, `Components`,
  `Duration`. Each has `from_text()`, which reads every wording in the
  sources, and `text`, which writes the 2024 card's. A `DataSpell` parses its
  record's text into them (`casting_time_spec`, `range_spec`, ...), so
  `casting_time_type`, `range_feet`, `duration_seconds`, `is_concentration`,
  `is_ritual` and `has_verbal`... come from one parser for both kinds of
  spell. A JSON spell's card keeps the record's wording.
- One module per level in `CharacterContent/Spells/SpellClasses/`
  (`Cantrips.py`, `Level1.py`, ...), each ending in `SPELLS = [...]`;
  `SpellClasses/__init__.py` builds `SPELL_CLASSES` by name and refuses two
  classes for one spell.
- `SpellFactory.create(name)` gives the class if there is one, else the
  `DataSpell` of the JSON record; `all_spells()` and `spell_names()` include
  spells only a class has (homebrew needs no JSON at all).
- **One source per spell.** Converting takes the spell's entries out of its
  source's companion files (`_extended`, `_improved`, `_combat_effects`);
  `tests/test_spell_classes.py` fails if one is left, and
  `spell_mechanics.py check`/`add` point at the class. The scraped
  `spells_<source>.json` record stays: it's the fallback, what scrapers
  write, and what a re-scrape is compared against.

**The converter** (`python -m CharacterContent.Spells.SpellClassConverter`,
`--name`, `--described`, `--level N`, `--all`, `--dry-run`, `--keep-json`)
writes each class from the record and its companions, as readable code
(keywords for `SpellRules`, the description one source paragraph per line,
blocks and effects as constructor calls), formats it with Black, then
imports it and compares it with the JSON spell: every rules field, tags,
target, improved description, combat effects, and the derived duration,
Concentration, ritual and range. Only when every class matches does it
remove the companion entries; otherwise it takes the classes back out. It
never touches a spell that has a class (hand edits are safe) and keeps a
module's own imports and classes when adding to it.

| # | Step | State / done when |
|---|---|---|
| S.1 | `ClassSpell` + `SpellRules`, the factory preferring classes, the converter, `tests/test_spell_classes.py`; the skills, agents, HOWTO and IMPROVED_DESCRIPTIONS.md say where a class spell is edited | **Done** |
| S.2 | Convert the spells with combat effects (57: the ones where the JSON hit its limits) | **Done**: picker goldens and sheet snapshots unchanged; the converter's check passed for all 57 |
| S.2b | The converter writes enums where the values are a fixed set (R19), and leaves a spell it can't express as JSON with the reason (`CannotConvert`) | **Done**: the 57 regenerated with enums; 574 of the 594 spells can be converted, the 20 others are DI-062 and DI-063 |
| S.2c | Casting time, range, components and duration as `SpellFields` dataclasses (R20); the converter compares them by meaning; the 57 regenerated | **Done**: every record of the three sources reads and writes back (`tests/test_spell_fields.py`); old and new derived values agree on all 1,391 records but one fix (Yolande's Regal Presence now has V); one card changed (Absorb Elements "1 reaction, ..." -> "Reaction, ...") |
| S.2d | Combat effects' `roll` and `until` as enums (`EffectRoll`, `TurnEdge`, `TurnOf`; R21), written by the converter and used by every Python effect (spell classes, features, homebrew monsters, tests) | **Done**: picker goldens and sheet snapshots unchanged |
| S.3 | Write new combat effects in classes, not JSON: convert a spell, then edit its `combat_effects()`. Teach `spell_mechanics.py draft` to print a class's method instead of a JSON entry, and give the `spell-mechanics` agent classes in scope | **Done** (R22): `draft --out` writes a Python `EFFECTS` module; `add` converts the spell with those effects (`SpellClassConverter.convert(..., effects)`) or sets the method on its class (`set_combat_effects`), both checked and rolled back on a problem; JSON only for the spells that can't be classes; `check` covers class spells; skill, agent and tests updated. Lightning Bolt added through it (one new picker row, read) |
| S.4 | Convert the rest (Q11) and retire the companion files: once every spell of a source has a class, its `_extended`/`_improved`/`_combat_effects` files and `DataSpell`'s companion handling go | Not started |
| S.5 | Drift check: a re-scrape that changes a converted spell's record must be noticed (Q12) | **Done** (R23): every class carries `converted_from = RecordStamp(file, sha1)`, written by the converter and backfilled on the 58 classes (all 58 agreed with their records by meaning first); `test_no_class_has_drifted_from_its_record` fails on a changed record; `SpellClassConverter --drift` shows what to merge, `--accept <spell>` re-stamps; HOWTO and the `content-scraper` agent say to run it after a re-scrape |

## Lasting effects (Phase 3, design unchanged)

A `CombatCondition` on a target becomes an `ActiveEffect` on that combatant:
one record with its name, source, the caster, duration, concentration link,
how it ends, and its modifiers and triggers. It replaces the scattered
`timed_conditions`, `repeat_saves`, `*_condition_descriptions` and colour maps
with one list, `char["active_effects"]`, of plain dicts (Decision 5).

| Modifier | Examples |
|---|---|
| `D20Bonus(rolls, amount, ability=None)` | Bless (+1d4 attack and saves), Bane (-1d4), Guidance |
| `D20Mode(rolls, mode, ability=None)` | Restrained (Disadvantage on DEX saves and attacks), Dodge |
| `AttacksAgainst(mode)` | Faerie Fire, Restrained, Blinded, Dodge |
| `ArmorClass(bonus)` | Shield (+5), Shield of Faith (+2), Haste (+2) |
| `Resistance(types)` / `Immunity` / `Vulnerability` | Rage, Absorb Elements, Protection from Energy |
| `ExtraDamageFrom(source, amount, type)` | Hunter's Mark, Hex: on the target, "hits from the caster deal 1d6 more" |
| `ExtraDamageOnHit(amount, type)` | Rage damage, Divine Favor: on the attacker |
| `NoHealing` | Chill Touch (now a badge with a note) |
| `Note(text)` | anything not modelled, shown on the card |

Triggers: `AtTurnStart(effect)`, `AtTurnEnd(effect)` (today's repeat save is
one), `WhenHit(effect)`. Position-dependent ones are prompts. The rules
conditions become data in the same vocabulary. Modifiers count in the rolls
the simulator makes; for typed totals they're reminders (Decision 4). Start
with a vertical slice: Restrained, Bless, Shield of Faith, Rage, Hunter's
Mark, Heroism. The modifier types go in a sibling module,
`Model/Content/CombatModifiers.py` (R1); the interpreter in a new Qt-free
`Combat/Effects/` (R5).

| # | Step | Done when |
|---|---|---|
| 3.1 | `ActiveEffect` and `char["active_effects"]`; old keys read through it. Undo, log replay, the player view keep working. | Combat UI tests pass; an old fight log still replays |
| 3.2 | Rules conditions as data; `roll_save`, attack resolution and AC read modifiers. | Restrained, Prone, Blinded, Paralyzed behave as before, from data; rules-checker run on the table |
| 3.3 | `D20Bonus`, `D20Mode`, `AttacksAgainst`, `ArmorClass`, `Resistance`. | Bless adds 1d4 to a rolled save; Shield of Faith raises AC |
| 3.4 | `ExtraDamageFrom` / `ExtraDamageOnHit`. | Hunter's Mark adds 1d6 Force on its caster's hits |
| 3.5 | Triggers and prompts. | Heroism gives temp HP at turn start; Spirit Guardians prompts |
| 3.6 | Concentration ends every `ActiveEffect` it holds. | Dropping Bless removes it from every target |

### Phase 4: content and tooling

1. Rename the `spell-mechanics` skill and agent to `combat-effects` (Q2), add
   the principles above and a feature rubric (what the first batch of features
   showed: an extension's row, `with_bonus`, a feature casting a spell), and
   give the script a features mode (`todo --campaign` for features too) and a
   `notes` report (principle 7).
2. A `feature-combat-effects` agent (opus) that writes `combat_effects()` for a
   named class, subclass or party.
3. Content: the rest of the Curse of the Lich party (Kivi's Monk features,
   Obmar's, Edmund's Channel Divinity; their 2014-only spells), then Time Loop
   PR, then spells level by level and features class by class.
4. A coverage line per campaign.

### Phase 5: beyond the dialog (optional)

Sheet chips ("DEX save · half · 8d6 Fire") from the same data;
`monster_score.py` reads `combat_effects`.

## Revisions (better solutions found while building)

- **R1. `CombatEffect` stays in `Model/Content/CombatEffect.py`**, not a new
  `Model/Content/Combat/` package with a shim.
- **R2. No `Amount` wrapper:** scaling fields on `CombatDamage`, and
  `CombatHitPoints` for healing and temp HP.
- **R3. Badges are explicit** (principle 10); a row doesn't repeat a badge
  named like itself in its summary.
- **R4. The text reading stays its own path** (`EffectText`), the shrinking
  legacy fallback.
- **R5. No `sources.py` / `resolve.py` yet:** `_described_option` with the
  source's defaults is the resolve step.
- **R6. A use that casts a spell takes the feature's action first** (Wild
  Companion).
- **R7. `spell=` keeps its name** (no rename to `casts=`).
- **R8. `[]` entries carry no notes** (Fog Cloud's was dropped).
- **R9. No second amount box, and still one of damage / healing / temp HP per
  effect.** Looking for real cases: damage and healing *to the same targets*
  from independent dice almost never happens. What happens is damage to the
  targets plus Hit Points *to the caster* worked out from it (Vampiric Touch's
  half the damage, Life Transference). That needs "to the caster, from the
  damage dealt", a Phase 3 trigger, not a second box. The one-amount rule
  stays in the model, which is true to the rules for every effect described.
- **R10. Extensions list their own uses under their parent.** Radiance of the
  Dawn is granted as an extension of Channel Divinity, and extensions never
  reached the picker. The alternatives were Channel Divinity checking for its
  subclass (the backward reach the hook removed) or a hook that adds rows.
  Treating an extension's `combat_effects()` as more uses of its parent fits
  the existing `extends=` model, and the hook stays for "changes the parent"
  (Combat Inspiration).
- **R11. Golden picker rows: one file per test, keyed by category and name.**
  The tests run in parallel, so one shared golden file was corrupted by
  concurrent rewrites; index-based keys made every insertion look like a
  rewrite of every later row.
- **R12. Several conditions in the dialog are one text, joined by " + ".**
  The plan left the UI open. A list widget would be more code and more clicks;
  the text is visible, editable and matches how the GM already types custom
  conditions. `CustomEffect.conditions` splits it.
- **R13. One repeat save per effect, not per condition.** Tasha's ends on one
  successful save; two entries would have rolled two saves. The entry keeps
  `condition` (the first) for older readers and adds `also`.
- **R14. A replacement isn't a `when`.** Toll the Dead's d12s *replace* its
  d8s for a hurt target, so it's a second row ("Toll the Dead (hurt target)"),
  not conditional extra damage. `when` is only for damage added on top.
- **R15. Spell rows count their cast through `counts_uses`, like features.**
  It was only meaningful for features; now every spell row sets it, and a
  later step of one casting (`spends_use=False`) clears it.
- **R16. A spell class holds its rules in one `SpellRules` record, not ten
  overridden properties.** Features take their metadata as constructor
  keywords, but a spell's constructor already belongs to its grant (casting
  ability, ruling). A class-level record keeps the two apart, reads like the
  JSON it came from, and lets the converter write it in one call.
- **R17. Spell classes live in one module per level, not one file per spell.**
  900 files would bury the folder, and features are grouped by class too.
  The converter appends to a module safely (it parses it, keeps hand-written
  classes and imports, and rebuilds only the import block and `SPELLS`).
- **R18. Rules tests follow the spell, not the file.** The improved-description
  and combat-effects rules tests were parametrized over the JSON entries, so
  converting 57 spells silently dropped ~460 test cases. They now run over
  every spell that has one, class or JSON; only the tests about the files
  themselves stay on JSON entries.
- **R19. Enums where the values are a fixed set, text where they aren't.**
  School, classes, components, usage tags and rules conditions are closed
  sets that code filters and checks on, so a typo should fail when the class
  is imported, not show up as a missing chip. Casting time, range and
  duration are not: the sources word them differently ("Action" / "1
  action"), attach triggers and notes ("Reaction, which you take when..."),
  and `casting_time_type`, `range_feet` and `duration_seconds` already read
  what code needs from them; a structured form would have to reproduce every
  wording to keep the cards unchanged. Source names are a closed set in
  principle but the data has duplicate spellings (Q14). The converter
  refuses a record that doesn't fit rather than normalizing it: changing a
  card's text is a decision for a person, and the parity check would have to
  allow it. *Casting time, range, components and duration: superseded by
  R20.*
- **R20. The card's top lines are dataclasses after all, written in the 2024
  wording.** R19 overrated the variety: a ~30-line grammar per line reads
  every record of all three sources (two exceptions in a first try, both
  covered now: Plant Growth's labelled alternatives become `note`s, and
  Shield's cut-off trigger, DI-064, is still a trigger). One parser replaces
  `Spell`'s regexes and the converter's components regex, a class can't hold
  a malformed line, and code gets what the text only implied (a trigger, an
  area, alternatives, "until dispelled"). The card text is built from the
  fields, not stored beside them, so a class can't say two things; the
  price is that a class writes the 2024 wording ("1 action" -> "Action",
  "60ft" -> "60 feet"), which suits the 2024 engine. A JSON spell keeps its
  record's wording. The converter now compares these lines by meaning, and
  converts the components slips of DI-062 (only a record with no components
  stays JSON). Material cost and consumption are not fields yet: nothing
  reads them; `Components.material` is the place to parse them from.
- **R21. A combat effect's `roll` and `until` are enums too** (2026-11-09):
  `EffectRoll` (SAVE, ATTACK, NONE) and `until=(TurnEdge, TurnOf)`, in
  `Model/Content/CombatEffect.py`. They are `StrEnum`s, so the JSON, old logs
  and every `== "save"` / `("end", "target")` comparison are unchanged; text
  is still accepted and kept as the member. Left as they were, on purpose:
  dice stay text ("2d8", "1d4 + 1": not a closed set, and already checked by
  a pattern when built), as do `when`, `noun`, `notes` and `spell`.
  `damage_type`, `save_ability`, `action_type` and condition names already
  were enums.
- **R22. Describing a spell is one scripted step that writes its class**
  (S.3, 2026-11-09). The plan said "convert, then edit `combat_effects()`";
  done by hand that is two steps, the second an unchecked edit in a
  2,000-line module. Instead the draft is a Python module
  (`EFFECTS = {"Fireball": [CombatEffect(...)]}`, with enums and the checks
  as comments), so the reviewer already works in the class's own language,
  and `add` does the rest: the rubric checks, then the converter writes the
  class with those effects (or replaces / adds the method on a class that
  exists, by its AST span, then refreshes the module's imports), Black, a
  fresh import and a parity check, and every file put back on a problem.
  So describing a spell also converts it, moving its improved description
  and tags into the class: Q11's "as they're described" happens on its own.
  A draft the model refuses (a damage type to choose, no choices yet) stays
  a dict so `add` refuses it. The spells that can't be classes (DI-062,
  DI-063) still get JSON entries from `add`, so the JSON reader stays until
  Q15 is decided.
- **R23. The stamp names its source file, and drift comes with a report**
  (S.5). Q12 suggested `rules_from = "sha1:..."`. The stamp is a small
  dataclass instead, `RecordStamp("spells_dnd2024.json", "<16 hex>")`, of
  the record as the scraped file has it (no companions, keys sorted): a new
  2024 record winning over the 2014 one a class came from is drift too, and
  the hash alone couldn't say which file to look in. A hash says only *that*
  something changed, so `--drift` also compares the class's rules with the
  new record by meaning (the converter's own `differences`, companions
  left out) and prints what to merge; a re-scrape that only reformats
  still shows up, as "the rules still agree", and `--accept` clears it.
  A class without a record (homebrew) has no stamp and is never drift; one
  with a record and no stamp is.

## Open questions (with suggestions)

- **Q2. When to rename `spell-mechanics` → `combat-effects` (skill, agent,
  script) and `EffectOption.is_curated` → `is_described`?** *Suggestion:* in
  Phase 4, together with the feature agent.
- **Q4. Should a cast spell's notes all come along?** (Jolt to Life shows
  Spare the Dying's range.) *Suggestion:* keep it; revisit if a row gets noisy.
- **Q5. Hook notes follow the sheet's feature order.** *Suggestion:* add a
  shuffled-order test when a second hook on the same source exists.
- **Q6. Agonizing Blast, Empowered Evocation, Potent Cantrip, Potent
  Spellcasting** are natural hook users. *Suggestion:* write each when a party
  has it.
- **Q7. "Ends a condition" is now the most repeated note** (Lay on Hands'
  Poisoned, and spells like Lesser Restoration, Remove Curse, Calm Emotions).
  *Suggestion:* an `ends_conditions: tuple[str, ...]` field, applied by the
  dialog as "take these off each target". Do it with Phase 3.1, since
  `ActiveEffect` is what it removes.
- **Q8. Paladin's Smite is once per Long Rest but has no `FeatureUses`,** so
  the picker can't count its free casting. *Suggestion:* give it
  `FeatureUses(1, regain_all_on="long rest")`; that adds a use box to its sheet
  card, so read the snapshot diff before regenerating.
- **Q9. Times splits across targets by applying again** (three rays: two at
  one target, one at another means two Applies). *Suggestion:* good enough at
  the table; a per-target count is only worth it if the GM asks.
- **Q10. Repeated *saves* (Times with a saving throw)** are possible but no
  described effect uses them yet. *Suggestion:* leave it until one does, then
  test it.
- **Q11. Convert all spells now, or as they're described?** All at once
  (`--all`: about 900 classes over both editions) gives one source right
  away and lets S.4 delete the companion files and `DataSpell`'s merging; but
  the `spell-improved-descriptions` agent's JSON workflow then has to move to
  classes in the same step, and the diff is large. *Suggestion:* first S.3
  (new combat effects go into classes), then convert level by level with the
  agents' workflow switched over, cantrips first; delete the companion files
  in S.4 once nothing is left in them.
- **Q13. Where should the converter live?** It's a command-line tool in
  content code (beside `SpellGenerator.py`), so `review-house-rules` flags
  its `print` calls as debug output. *Suggestion:* keep it there (it
  belongs with the spells and the generator) and teach the check that a
  module with a `__main__` block may print.
- **Q14. Sourcebooks as an enum?** `source` has 25 values, several of them
  the same book spelled two ways ("Forgotten Realms - Heroes of Faerun" /
  "Forgotten Realms: Heroes of Faer�n", "Player's Handbook 2024" / "...
  (BR)"). *Suggestion:* a `Sourcebook` enum with one member per book and the
  scraped spellings mapped onto it in the scrapers, then `SpellRules.source`
  becomes the enum. Do it with a re-scrape, not in the converter.
- **Q15. A note on a school or class** (Wildemount's Dunamancy, DI-063).
  *Suggestion:* `SpellRules.school_note: str = ""`, written by the converter
  from "(Dunamancy:Graviturgy)", shown on the card after the school, and the
  "Wizard (Dunamancy)" class read as Wizard plus that note.

## Discovered issues

- **DI-060** (open): pre-existing pyright errors in the combat-effects tests;
  the Qt dialog test files (`test_combat_ui_custom_effect.py`,
  `test_combat_ui_player_server.py`) have about 30 more of the same kind
  (Optional Qt accessors, `QTest.keyClick` overloads). All tests pass.
- **DI-061** (open): homebrew Mira, Princess of the Loop has 6 abilities; the
  house rule is at most 4.
- **DI-062** (open): five spell records have malformed components ('V,S',
  'M(a diamond ...)', a stray 'Component: ', none at all). Since R20 the
  converter reads all but the one with none; the records still want a
  scraper fix.
- **DI-063** (open): 15 Dunamancy spells have a school or class with a note
  (Q15), so the converter leaves them as JSON.
- **DI-064** (open): Shield's casting time is cut off in the 2024 and 2014
  records ("...or targeted by the"); aidedd has the whole trigger.
- **DI-065** (open): the 2014 records' `"ritual": true` is ignored, so 2014-only
  ritual spells don't show as rituals (their casting time doesn't say so).
- Found and fixed: the text-reading tests dropped a spell's data by its old
  key name; the single golden file broke under parallel test runs (R11);
  `draft`'s cross-check with the improved description kept only the last
  "Damage" row (the "+1d6 per slot level" one), so nearly every levelled
  spell's draft said "Improved description DIFFERS" (S.3).

## Testing strategy

- **Model:** invalid combinations raise; `to_dict`/`from_dict` round-trips; old
  logs still read (`test_monster_combat_effects.py`,
  `test_spell_combat_effects.py`).
- **Data:** every spell entry reads and is exactly what `to_dict()` writes;
  conditions are rules conditions or the spell's own badge; cantrip steps only
  on cantrips (`spell_mechanics.py check` too).
- **Picker:** expected values from the rules text, per spell and feature
  (`test_spell_combat_effects.py`, `test_feature_combat_effects.py`).
- **Dialog:** several conditions and one repeat save, Times with one cost and
  one undo, variant rows spending the right thing, an extension spending its
  parent's uses (`test_combat_ui_effect_steps.py`).
- **Golden picker rows:** `test_picker_rows.py`. Read the diff before
  `UPDATE_SNAPSHOTS=1`.
- **Phase 3:** rules tests take expected values from the Rules Glossary, and
  the `rules-checker` agent reviews the condition table.

## Checklist: adding a field to the model

1. The field on the dataclass, with `__post_init__` checks.
2. `to_dict` / `from_dict` (strict, and tolerant of older logs if it replaces
   something).
3. The picker: what `_described_option` / `_effect_amounts` do with it, or the
   note it makes.
4. The dialog, if it changes what Apply does.
5. The rubric in the skill, with an example.
6. Tests: validation, round-trip, one real source using it, and the golden
   rows diff read.
7. If notes said this before: update those sources.
8. Update this plan's Status and, if the design moved, Revisions.
