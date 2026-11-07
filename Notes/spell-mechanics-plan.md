# Plan: curated spell mechanics for the Custom Effect picker

## Status (2026-11-07)

| Step | State |
|---|---|
| 1 Schema, `Mechanics.py` | **Done.** Final schema in the module docstring of [Mechanics.py](../CharacterContent/Spells/SpellFactory/Mechanics.py). It differs from the first draft below: `upcast` and `cantrip` sit on each damage entry, and `heal` has its own `upcast`. |
| 2 Loader, `DataSpell.mechanics`, `Spell.mechanics = None` | **Done.** |
| 3 Picker uses curated data, falls back to the text | **Done.** `EffectOption.is_curated`. The picker tooltip says "Filled in from checked spell data." or "Read from its rules text: check the form." |
| 4 Seed script + full review | **Tooling done, review partly done.** `spell_mechanics.py draft` (in the `spell-mechanics` skill) prints a draft per spell with a check against the improved description, for review. It does not write high-confidence entries on its own, unlike the first draft below: every entry is reviewed before `add`. 49 entries are checked: 16 for variety (Alarm, Bless, Chromatic Orb, Cure Wounds, Faerie Fire, Fireball, Guiding Bolt, Hold Person, Ice Knife, Ice Storm, Magic Missile, Ray of Sickness, Shatter, Sleep, Spiritual Weapon, Toll the Dead), and every spell of the Time Loop PR party plus Eldritch Blast and Resistance (`todo --campaign time_loop_pr` prints 0). Absorb Elements is 2014-only, so it is in `spells_dnd5e_mechanics.json`. Left: 545 spells (408 in the 2024 file, 137 that only the 2014 data has), see Phase 2. |
| 5 `applicable: false` | **Done as recommended.** Hidden under All spells, still listed in the caster's own spells. |
| 6 Tests | **Done.** [test_spell_mechanics.py](../tests/test_spell_mechanics.py). The text-reading tests in `test_combat_ui_effect_options.py` drop the curated data so they keep testing the fallback. The consistency report is `spell_mechanics.py compare`. |
| 7 Skill + agent | **Done.** The `spell-mechanics` skill (`.claude/skills/spell-mechanics/`: the rubric, and `spell_mechanics.py` with `check`, `todo`, `draft`, `add`, `compare`, `format`) and the `spell-mechanics` agent on sonnet (`.claude/agents/spells/`). |
| 8 Later phases | **Not started.** Now Phase 2 (end of this file), which orders the remaining work. |

## Goal

When the GM picks a spell in the combat UI's Custom Effect dialog, the form is
filled in by `spell_option()` in [effect_options.py](../Combat/CombatUIQt/effect_options.py),
which reads the spell's rules text with regexes (`read_effect_text()`). That
reading is careful but can't be sure, so the GM still has to check the text and
read the option's note.

Instead, the facts the form needs (saving throw or attack roll, which ability,
damage dice and types, half on a save, a condition and how long it lasts,
upcasting, cantrip scaling, and whether the spell has anything to apply at all)
will be stored in a new companion file:

```
CharacterContent/Spells/spells_dnd2024_mechanics.json
```

When a spell has an entry there, the picker uses it. When it doesn't, the
picker reads the text as it does now.

**Why `_mechanics`:** `_extended` already holds sheet metadata (`usage_tags`,
`target`) and `_improved` holds display blocks. This file holds the rules
mechanics: what a cast rolls and does. It isn't specific to the combat UI, so
the sheet or a future simulator can read it too, and `_combat` would be too
narrow a name. It follows the existing per-source convention (`<source>_<suffix>.json`,
keyed by spell name, never editing the scraped source JSON), so
`spells_dnd5e_mechanics.json` and `spells_aidedd_mechanics.json` can be added
later without new code.

## Current state (what the plan builds on)

| Piece | Where | Relevance |
|---|---|---|
| Source spell data | `spells_dnd2024.json` (456 spells), `spells_aidedd.json`, `spells_dnd5e.json` | Scraped; never hand-edited. |
| Companion loading | [Factory.py](../CharacterContent/Spells/SpellFactory/Factory.py) `_load_json()` merges `_extended` fields and `_improved` blocks into each source's records | The new file is merged the same way. |
| Spell object | [DataSpell.py](../CharacterContent/Spells/SpellFactory/DataSpell.py) (`usage_tags`, `target`, `improved_description` validate their data on access) | Gets a `mechanics` property. |
| Text reading | `read_effect_text()` -> `EffectText` in `effect_options.py` | The fallback. Also a good seed for the new file. |
| Form values | `EffectOption` in [saves.py](../Combat/CombatUIQt/saves.py) | The target of both paths. Unchanged. |
| Improved descriptions | `spells_dnd2024_improved.json` (390 spells) with facts such as `Save`, `Failed save`, `Attack`, `On a hit`, `Repeat save`, `Damage`, `Healing` | A second, independent signal to check the seed against. |
| Tests | [test_combat_ui_effect_options.py](../tests/test_combat_ui_effect_options.py) (47 tests, many on real spells such as Fireball, Hold Person, Toll the Dead) | Must keep testing the regex path once those spells get JSON entries (see step 6). |

## Step 1: Schema (first draft; see Status for what changed)

Each entry is keyed by spell name and holds only what the caster's sheet can't
supply. The DC, attack bonus and spellcasting modifier stay computed per
caster, as now. Example entries:

```json
{
  "Fireball": {
    "applicable": true,
    "roll": "save",
    "save": {"ability": "DEX", "half_on_success": true},
    "damage": [{"dice": "8d6", "type": "Fire"}],
    "upcast": {"damage": ["1d6"]}
  },
  "Hold Person": {
    "roll": "save",
    "save": {"ability": "WIS", "repeat": true},
    "condition": {"name": "Paralyzed"}
  },
  "Guiding Bolt": {
    "roll": "attack",
    "damage": [{"dice": "4d6", "type": "Radiant"}],
    "upcast": {"damage": ["1d6"]},
    "notes": ["The next attack roll against the target before the end of your next turn has Advantage."]
  },
  "Toll the Dead": {
    "roll": "save",
    "save": {"ability": "WIS"},
    "damage": [{"dice": "1d8", "type": "Necrotic"}],
    "cantrip": {"die": "d8", "steps": {"5": "2d8", "11": "3d8", "17": "4d8"}},
    "notes": ["1d12 instead of 1d8 if the target is missing any Hit Points."]
  },
  "Chromatic Orb": {
    "roll": "attack",
    "damage": [{"dice": "3d8", "type": null, "choices": ["Acid", "Cold", "Fire", "Lightning", "Poison", "Thunder"]}],
    "upcast": {"damage": ["1d8"]}
  },
  "Alarm": {"applicable": false}
}
```

Fields (all optional except where noted):

| Field | Type | Meaning / maps to |
|---|---|---|
| `applicable` | bool, default `true` | `false` = the spell has nothing for the Custom Effect form to apply to a target (Alarm, Find Steed, Teleport). See step 5 for what the picker does with it. |
| `roll` | `"save"` / `"attack"` / `"none"` | `EffectOption.roll`. `"none"`: it just happens (Magic Missile, Bless, Cure Wounds). |
| `save.ability` | `"STR"`...`"CHA"` | `EffectOption.ability` (the short names in `saves.ABILITIES`). |
| `save.half_on_success` | bool | `half_on_save`. |
| `save.repeat` | bool | `repeat_save` (the save is repeated at the end of each of the target's turns). |
| `attack.kind` | `"melee"` / `"ranged"` | Informational for now; the form has one attack roll. |
| `damage[]` | `{dice, type, add_modifier?, choices?}` | `rolls` (a `DamageRoll` each). `type: null` + `choices` = the caster chooses; the note says so. `add_modifier: true` adds the caster's spellcasting modifier (Spiritual Weapon). |
| `heal` | `{dice, add_modifier?}` | Not on the form yet; kept so the "badge" rule (no badge for healing) and a future heal field have it. |
| `condition` | `{name, alternatives?, until?}` | `condition`, the "can be X instead" note, and `until` (`["end", "target"]` = until the end of the target's next turn). `name` must be a `Core.Definitions.Condition` value. |
| `badge` | bool | Overrides the current rule that a spell with nothing else to show puts its own name on the target as a badge (Bless, Bane, Faerie Fire). |
| `upcast.damage[]` | one dice string per `damage[]` entry, `""` = that part doesn't grow | `EffectOption.upcast`. |
| `cantrip` | `{die, steps: {"5": ..., "11": ..., "17": ...}}` | Replaces `_with_cantrip_level()`'s text reading. |
| `notes[]` | strings | Curated GM notes, shown in place of the regex notes (`EffectText.notes`). Per-caster notes (unknown DC, no slot left) are still added. |
| `variants[]` | list of partial entries with a `name` | **Later phase (step 8).** Spells with two distinct effects (Ice Knife: an attack, then a DEX save explosion; Alter Self options) become one picker row per variant. |

Rules for the file:
- Keys sorted, one spell per key, the spell name exactly as in `spells_dnd2024.json`.
- Only facts stated in the 2024 rules text. Anything situational goes in `notes`.
- No DCs, bonuses or computed numbers. They depend on the caster.

## Step 2: Loading (CharacterContent, no Combat imports)

1. **`SpellFactory`**: add `mechanics_path(path)` and `_load_mechanics(path)`
   next to `improved_path` / `_load_improved`, and in `_load_json()` attach
   each entry as `source_data[name]["mechanics"] = entry` (only for names in
   that source, like the improved blocks, so a 2024 entry never rides on a
   2014 record).
2. **New module `CharacterContent/Spells/SpellFactory/Mechanics.py`**: frozen
   dataclasses `SpellMechanics`, `SaveSpec`, `DamageSpec`, `ConditionSpec`,
   `CantripSpec`, plus `parse_mechanics(name, dict) -> SpellMechanics` that
   validates as it parses (ability in the six short names, damage type a
   `Core.Definitions` damage type or `null` with `choices`, condition a
   `Condition` value, dice matching `\d+d\d+`, `len(upcast.damage) ==
   len(damage)`, unknown keys rejected) and raises `ValueError` naming the
   spell, the same pattern as `DataSpell.target` / `usage_tags`.
3. **`DataSpell.mechanics`**: a property returning `SpellMechanics | None`,
   parsed lazily and cached.
4. `Spell` (the base / hand-written spells) gets `mechanics = None` so every
   spell object answers the question.

## Step 3: Use it in the picker (`effect_options.py`)

1. Add `effect_text_from_mechanics(m: SpellMechanics) -> EffectText`, which
   converts the curated data into the same `EffectText` the regex path
   produces, so the rest of `spell_option()` (DC, bonus, modifier, slots,
   badge) stays one code path.
2. Give `EffectText` two optional fields the regex path leaves `None`:
   `upcast_dice: tuple[str, ...] | None` and
   `cantrip_steps: dict[int, str] | None`. In `spell_option()`, use them when
   set, and fall back to `_upcast_dice()` / `_with_cantrip_level()` (text
   parsing) when not.
3. In `spell_option()`:
   ```python
   mechanics = getattr(spell, "mechanics", None)
   text = (effect_text_from_mechanics(mechanics) if mechanics is not None
           else read_effect_text(spell.description))
   ```
   The `"Upcasting won't change the damage"` note only applies on the text
   path.
4. Add `EffectOption.from_curated_data: bool` (or a short prefix on the note)
   so the GM can tell a checked fill from a guessed one, for example a "✓" in
   the row or "Read from the rules text: check it." on the fallback. Small,
   but it's what removes the need to read the text.
5. `_feature_option()` is not touched. Features have no such file; that's a
   separate follow-up.

## Step 4: Seed the file (script, then review)

Writing ~456 entries by hand is the slow part, so generate a draft and review it:

1. **Seed script** `Scrapers/Spells/seed_spell_mechanics.py` (or under
   `CharacterContent/Spells/`): for every spell in `spells_dnd2024.json`, run
   `read_effect_text()` and write what it found in the new schema. Also read
   the spell's `_improved` facts (`Save`, `Failed save`, `Successful save`,
   `Attack`, `On a hit`, `Repeat save`, `Damage`) and compare them with the
   regex reading. Output:
   - `spells_dnd2024_mechanics.json`: only entries where both signals agree
     **and** the regex produced no notes (high confidence).
   - a review list in the scratchpad (not the repo): every other spell with the
     regex reading, the improved facts, the notes and the raw description.
   - `--dry-run` prints counts only; the script never overwrites an existing
     entry unless `--force <name>` is given, so reviewed entries stay as they are.
2. **Review in batches by spell level** (cantrips, 1, 2, ... 9), each batch
   checked against the 2024 description text. That is rubric-driven batch work
   that a validator checks, so per CLAUDE.md a **sonnet** agent fits (see step 7).
   Each batch adds the remaining spells, `applicable: false` included, so at
   the end every 2024 spell has an entry and "no entry" means "not reviewed yet".
3. Spot-check the high-confidence auto entries too, at least the ones that
   have damage, before calling the file done.

## Step 5: Decide what `applicable: false` does in the picker

The trade-off: under **All spells**, a non-applicable spell is noise, but a
caster's **own spells** still need to be pickable to spend the slot and action
and to track Concentration. Proposed:
- In `<Name>'s Spells`: keep listed, filling only the action, slot,
  Concentration and the spell-name badge (as now for "nothing to roll" spells).
- In `All spells`: hide it.
- Spells with no entry behave exactly as today.

(Agreed and implemented.)

## Step 6: Tests

1. **Data validation test** (`tests/test_spell_mechanics.py`): every key exists
   in `spells_dnd2024.json`; every entry parses with `parse_mechanics`; keys are
   sorted; `upcast.damage` lengths match; a spell with `roll: "save"` has
   `save.ability`; a cantrip with damage has `cantrip`; a non-cantrip has no
   `cantrip`.
2. **Loader test**: a 2024 entry attaches only to the 2024 record; a missing
   file loads as no mechanics.
3. **Picker tests** in `test_combat_ui_effect_options.py`:
   - The existing tests for the text reading check the regex path, not
     whatever the JSON says. Point them at `read_effect_text()` directly, or
     give `spell_option()` a way to ignore curated data (e.g. a fixture that
     monkeypatches `SpellFactory`'s mechanics to `{}`), so they keep guarding
     the fallback once Fireball and the others have entries.
   - New tests: a curated spell fills the form from JSON (Fireball, Hold
     Person, Guiding Bolt); curated damage still gets the caster's modifier;
     cantrip steps and upcasting from JSON; a choice-of-type spell carries the
     "give one" note; a curated note replaces the regex notes; an
     `applicable: false` spell behaves as decided in step 5; a spell without
     an entry still uses the text.
4. **Consistency check (report, not a failing test)**: a small script that
   lists spells where the curated entry and `read_effect_text()` disagree.
   Useful for reviewing entries and for finding regex bugs; log real regex
   bugs with `issues.py`.
5. Run `./run_tests.sh -q -x`. No character sheet snapshots should change
   (sheets don't read mechanics yet). If one does, read it with the
   `snapshot-diffs` skill.

## Step 7: Tooling for agents

1. **Skill `spell-mechanics`** (`.claude/skills/spell-mechanics/SKILL.md`):
   the schema from step 1, the rubric for each field (what counts as
   `half_on_success`, when a condition goes in `notes` instead of `condition`,
   when `applicable` is false), and a `validate.py` that runs `parse_mechanics`
   over the file and prints the curated-vs-regex differences for a given filter
   (`--level 3`, `--name Fireball`).
2. **Agent**: either extend `spell-improved-descriptions` (it already works
   per level on a spell companion file) or add a sibling
   `.claude/agents/spells/spell-mechanics.md` on **sonnet**, preloading
   `spell-mechanics` and `subagent-protocol`. Its scope is only
   `spells_dnd2024_mechanics.json`. A separate agent is cleaner: the rubric is
   different and the two files can then be worked on in parallel.
3. The hook rebuilds the `agent-index` skill after the edit; check that its
   test passes.
4. Mention the new file in `CharacterContent/Spells/IMPROVED_DESCRIPTIONS.md`
   (or a sibling `MECHANICS.md`) and in [agent-workflow.md](agent-workflow.md)
   where the spell companion files are listed.

## Step 8: Later phases (out of scope for the first pass)

- `variants[]`: one picker row per distinct effect (Ice Knife, Chromatic Orb's
  bounce, spells whose option lines currently give "only with one of its
  options" notes).
- A heal field on the Custom Effect form, fed from `heal`.
- `spells_dnd5e_mechanics.json` / `spells_aidedd_mechanics.json` for spells
  only in the 2014 or aidedd sources (the loader already handles them).
- The same idea for features (a `mechanics=` kwarg or a `get_mechanics()`
  method on `Feature`, read by `_feature_option()`).
- Character sheet cards showing "DEX save, half" / "8d6 Fire" chips from the
  same data.

## Order of work and done criteria

| # | Step | Done when |
|---|---|---|
| 1 | Schema + `Mechanics.py` + parse/validate | `parse_mechanics` unit-tested on the example entries above |
| 2 | Loader + `DataSpell.mechanics` | Loader tests pass; no snapshot changes |
| 3 | Picker uses curated data, falls back otherwise | New picker tests pass; existing tests still cover the regex path |
| 4 | Seed script + first high-confidence file | Validator clean; spot-check of damage spells done |
| 5 | `applicable: false` behaviour agreed and implemented | Test covers it |
| 6 | Skill + agent | Agent index test passes |
| 7 | Review batches, cantrips to level 9 | Every 2024 spell has an entry; validator clean; consistency report reviewed |

## Phase 2: what's left (added 2026-11-07, after the first pass was pushed)

The first pass is on main (495dc647, 293b70b3): the schema, loader, picker,
tests, the `spell-mechanics` skill and agent, and 49 checked spells, including
every spell of the Time Loop PR party. What's left, in the order to do it:

| Spells without an entry | 2024 file | 2014 file | Total |
|---|---|---|---|
| Cantrips | 21 | 15 | 36 |
| Level 1-3 | 171 | 62 | 233 |
| Level 4-6 | 142 | 43 | 185 |
| Level 7-9 | 74 | 17 | 91 |
| **All** | **408** | **137** | **545** |

(`python .claude/skills/spell-mechanics/spell_mechanics.py todo --level N` lists them.)

### Step 9: Commit the `todo --campaign` fix

`todo`, `draft` and `compare` treated a campaign whose party has no spells
(Grim's Castle has no party yet) as no filter, and listed all 545 spells. The
fix is in the working tree (`chosen_spells` in `spell_mechanics.py`) and needs a
commit.

### Step 10: Schema gaps the next spells run into

The Curse of the Lich party's 23 missing spells show four things an entry
can't say yet. Each would otherwise end up as a note. Close them before the
bulk review, or the agent writes hundreds of notes that a later pass has to
turn back into fields. Each one is a field in `Mechanics.py`, handling in
`effect_options.py`, the rubric in the skill, and tests.

| Gap | Spells | Proposed field | What the picker does with it |
|---|---|---|---|
| A badge that lasts until a turn edge | Chill Touch (no healing until the end of your next turn), Guiding Bolt, Vicious Mockery, Shield, Starry Wisp | `"badge_until": ["end", "source"]` | Sets `EffectOption.until` for the badge as it does for a condition, so the badge drops off on its own |
| Several attacks or darts | Scorching Ray (3 rays), Magic Missile (3 darts), Eldritch Blast (beams by character level) | `"instances": {"count": 3, "upcast": 1}` or `{"cantrip": {"5": 2, "11": 3, "17": 4}}` | Works out the count at the chosen slot or level, and shows "3 rays: one attack roll each" in the row and note. Damage stays per instance |
| Extra damage that only starts at a character level | Booming Blade, Green-Flame Blade, True Strike | Let a cantrip damage entry have `"dice": "0"` plus `cantrip` steps | No damage below level 5, then the step's dice. Today True Strike's 1d6 at level 5 is only a note |
| Extra damage against some targets | Divine Smite (+1d8 against a Fiend or Undead), Toll the Dead (d12s if the target is hurt) | `"conditional": [{"dice": "1d8", "type": "Radiant", "when": "the target is a Fiend or an Undead"}]` | Becomes a generated note that includes the upcast. Later, it could be a checkbox in the dialog |

**Decision for the user:** whether `instances` should only produce notes, or
whether the dialog should get a repeat count (roll the attack and damage N
times against the chosen targets). A repeat count is the bigger change, in
`conditions_mixin.py` and `saves.py`.

### Step 11: Variants (was in Step 8)

Command (Approach/Drop/Flee/Grovel/Halt), Elementalism, Thaumaturgy, Ice Knife's
explosion, Chromatic Orb's leap, Alter Self, Enlarge/Reduce, Bestow Curse and
Contagion each have options with different mechanics. Proposed:
`"variants": [{"name": "Grovel", ...partial entry...}]`, merged over the base
entry. The picker shows one row per variant ("Command: Grovel"), and the base
row stays for the slot and action. Do this before the bulk review gets to
those spells (Command is level 1).

### Step 12: Bulk review with the `spell-mechanics` agent

1. **Curse of the Lich party first** (23 spells, `--campaign curse_of_the_lich`),
   after Steps 10 and 11. These are the spells played most at the table.
2. **Then a level at a time**, cantrips first, 2024 file and 2014 file in
   separate runs. Batches of about 40-70 spells, so two or three levels per run
   from level 4 up. Give each run its filter (for example "level 2 spells,
   2024 file") and the instruction to use `todo` then `draft --out` then `add`.
3. **After each run**, in the main session:
   - run `verify-agent-work` with `--claimed` set to the two mechanics files;
   - run `spell_mechanics.py compare` for that level and look at every
     difference;
   - spot-check five entries against their text, including one with damage and
     one condition spell;
   - curate what the agent wrote to its memory.
   Sonnet is the right model per CLAUDE.md, because `check` and `compare` verify
   it. Don't hand it to haiku: choosing what goes in notes versus fields is
   exactly the kind of judgment haiku runs have gotten wrong here.
4. **Data defects the agent should report, not work around:** Shield's casting
   time is cut off ("targeted by the"). Spells whose text refers to a missing
   table should be reported too. Log both with the `discovered-issues` skill.

**Done when:** `todo` prints 0, `check` is OK, and the full suite passes.

### Step 13: Spells cast by monsters

Stat blocks name the spells they cast: the Lich, dragons ("uses Spellcasting to
cast Fear", "cast Melf's Acid Arrow (level 4 version)"), and homebrew casters
such as the Elf Druid of the Land (Entangle, Hold Person). Today a monster
only has "All spells", with its DC and bonus taken from its Spellcasting text.
Proposed:
- parse the spell names out of a monster's Spellcasting actions in
  `monster_actions.py`, matching them against `SpellFactory.spell_names()`;
- list them as "<Monster>'s Spells" in `effect_options()`, at the level stated
  ("level 4 version" as the slot level), filled from their entries;
- leave the stat-block action rows as they are, since the monster uses them up.

This is combat-simulator work, with a test for a generated monster and one for
a homebrew monster.

### Step 14: Keep entries in step with the text

A re-scrape can change a spell's description, and its entry would then
describe the old text without anyone noticing. Proposed: `add` stores a short
hash of the description in a sidecar file. Use
`spells_<source>_mechanics.lock.json` rather than the entry itself, which
stays clean. `check` reports every spell whose text changed since it was
checked, and a test runs `check`. Also add a line about checking mechanics to
the `new-content-check` skill's "after scraping" steps, so a newly scraped spell
shows up in `todo`.

### Step 15: More of the form

- **Healing and Temporary Hit Points:** a Heal box on the Custom Effect dialog,
  filled from `heal`, plus a new `temp_hp` field (False Life, Heroism,
  Armor of Agathys). The note tells the GM to apply it by hand until then.
- **Two conditions:** let `EffectOption.condition` hold a tuple
  (Tasha's Hideous Laughter: Prone and Incapacitated; Hypnotic Pattern;
  Power Word Stun), and have the dialog apply each.
- **Extra targets per slot level and duration upcasting** (Hold Person,
  Invisibility, Hunter's Mark) stay notes. The picker has no target count to
  fill.

### Step 16: Beyond the combat picker (was in Step 8)

- Spell cards on the character sheet: "DEX save · half" and "8d6 Fire" chips
  from `mechanics`. This changes snapshots, so the `snapshot-diffs` skill
  applies.
- Features: the same data for features with a save or an attack (Breath
  Weapon, Channel Divinity options, Stunning Strike), as a `mechanics=` kwarg
  read by `_feature_option()`. This is a separate plan. Features are code, not
  JSON, so the regex reading could be replaced per feature class.

### Phase 2 order and done criteria

| # | Step | Done when |
|---|---|---|
| 9 | Commit the `todo --campaign` fix | Pushed |
| 10 | `badge_until`, `instances`, level-gated dice, `conditional` (after the user decides on a repeat count) | Parser and picker tests for each field; skill rubric updated |
| 11 | `variants` | Command and Ice Knife give one picker row per variant; tests |
| 12 | Curse of the Lich party, then all levels with the agent | `todo` prints 0; `check` OK; each batch verified and spot-checked |
| 13 | Monsters' own spells in the picker | A Lich and a homebrew caster list their spells, filled from entries |
| 14 | Description hashes | `check` flags a changed description; new-content-check mentions mechanics |
| 15 | Heal/Temp HP box, two conditions | The dialog applies them; Cure Wounds and Tasha's fill them |
| 16 | Sheet chips, features | Separate plans |
