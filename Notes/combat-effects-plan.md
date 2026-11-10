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

## Status (2026-11-10, 3.1-3.4 done: lasting effects are one list, the rules conditions are data, effects carry modifiers the simulator counts, and hits deal the extra damage effects give)

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
| S | **Spells as classes** (new direction, 2026-11-09; see its section) | S.1 base class, factory and converter **done**; S.2 the 57 spells with combat effects converted **done**; S.2c card lines as dataclasses **done** (R20); S.3 new effects go into classes **done** (R22); S.5 drift check **done** (R23); S.4 **done** (R26): all 594 spells are classes, the agents' tools switched over (R24), Q15 and DI-065 done (R25), every companion file deleted and nothing reads them |
| 3 | Lasting effects (3.1-3.6) | 3.1 **done** (R28-R34): `char["active_effects"]`, one plain dict per badge, in the new Qt-free `Combat/Effects/active_effects.py`; the seven old keys are read only by its `upgrade_old_keys`, where a log is read; an old fight log replays the same (`tests/test_active_effects.py`). 3.2 **done** (R27), ahead of 3.1: the rules conditions are data, and saves, attack rolls (all three paths), AC, damage Resistance and condition immunity read them. 3.3 **done** (R35-R40): a badge's `CombatCondition` says its `modifiers`, the record keeps them as JSON, and `modifiers_on` reads them beside the conditions and cover; Bless's 1d4 is rolled into the saves (a monster's Concentration save too, R40) and attack rolls the simulator makes, Shield of Faith's +2 counts in AC, cover's +2/+5 in Dexterity saves (DI-066); a typed total stays as typed, with the bonus as a reminder in the dialog. 3.4 **done** (R41-R47): `ExtraDamageFrom` (on the target, from its effect's caster) and `ExtraDamageOnHit` (on the attacker); Hunter's Mark's 1d6 Force on its caster's hits and Divine Favor's 1d4 Radiant on its caster's weapon hits are rolled into the hits the dialog and a monster's action buttons deal, doubled on a Critical Hit, each type resisted on its own; a typed damage total stays as typed, with the extra as a reminder in the dialog. 3.5-3.6 not started |
| 4 | One `combat-effects` skill; feature agent; content rollout | Partly: the skill's rubric and script cover every new field; first content batch below |
| 5 | Sheet chips, monster score | Not started |

**Content described so far.** Spells: 57 (2024) + 1 (2014), all as classes
(every spell is a class since S.4; 58 have combat effects);
Lightning Bolt (2026-11-09) was the first written through S.3's `add`. Added
2026-11-09: Burning Hands, Charm Person, Chill Touch, Command (5 options),
Divine Smite, Sacred Flame, Scorching Ray, Shield of Faith; upgraded from notes
to fields: Eldritch Blast and Magic Missile (`instances`), Ice Knife (two
steps), Tasha's Hideous Laughter (two conditions), Toll the Dead (a row for a
hurt target). Features of the Curse of the Lich party: Channel Divinity (Divine
Spark heal and harm, Turn Undead), Radiance of the Dawn, Warding Flare, Lay on
Hands, Paladin's Smite, Sneak Attack. With modifiers on their badge (3.3):
Bless (`D20Bonus` 1d4 on attack rolls and saving throws) and Shield of Faith
(`ArmorClass(2)`); with extra damage on their badge (3.4): Hunter's Mark
(`ExtraDamageFrom` 1d6 Force) and Divine Favor (`ExtraDamageOnHit` 1d4
Radiant on weapon attacks; newly described, R47), so 59 spells have combat
effects; everything else waits for Phase 4.

**Verified 2026-11-09 (after S.3):** full suite passes (9,917); every
picker-row change reviewed field by field against the previous golden.

**Verified 2026-11-09 (after S.4's levels 1-9, R25):** full suite passes
(10,612); picker goldens unchanged; drift check clean; `build_stats.json`
unchanged. Every sheet line that changed was read: 41 builds' spell cards
in the 2024 wording (R20: "1 action" -> "Action", "1 Hour" -> "1 hour",
"60ft" -> "60 feet", "Concentration up to 10 minutes" -> "up to 10
minutes", the badge still shown), Gate's and Yolande's Regal Presence's
components slips (DI-062), and Ceremony's Ritual tag on three builds
(DI-065); Armor of Agathys' "1 hour" in six More Info goldens.

**Verified 2026-11-09 (3.2, R27):** full suite passes; picker goldens and
sheet snapshots unchanged; pyright clean on the changed files; 175 new tests
(`test_combat_modifiers.py`, `test_combat_ui_condition_rolls.py`) with
expected values from the glossary's condition entries. The rules-checker
found every counted modifier right, sentence by sentence, and 7 gaps: 5 fixed
(see R27's last point), 2 logged (DI-067, DI-068).

**Verified 2026-11-09 (S.4 done, R26):** full suite passes (10,011; six fewer than before
R26's last step, the removed `blocks_from_json` tests); no snapshot changed;
spell-mechanics `check` and usage-tags `check` OK (594 of 594 spells
tagged, 58 with combat effects); the converter's parity check passed for
Gate Seal.

**Verified 2026-11-09 (3.1, R28-R34):** full suite passes but for the
three `test_format_changed.py` tests of DI-020 (10,028 passed); no snapshot
or golden changed; `./typecheck.sh Combat` 0 errors before and after. Parity
with the code before 3.1: one scripted fight (custom conditions with timers
and notes, a repeat save ending two conditions, Bless cast, a timer and a
note given again, five turns, an undo, a removal, then the log continued in
a fresh window for three turns) played by HEAD's code (a `git archive` copy)
and by the new code gave identical conditions, badge tooltips and colours,
card texts, log lines and turn reminders. **Re-verified on top of 3.2**
(rebased onto 8b7b78ff): full suite passes (10,206 passed, 4 skipped, 20
xfailed; the DI-020 tests pass once `format_changed.sh` is checked out with
LF, as in the main checkout); no snapshot or golden changed; `./typecheck.sh
Combat` 0 errors, as on main; 3.2's `test_combat_modifiers.py` and
`test_combat_ui_condition_rolls.py` pass. The same scripted fight played by
8b7b78ff's code and by the rebased code matched step for step, and the
rebased code continuing the old-key log 8b7b78ff wrote matched 8b7b78ff
continuing it.

**Verified 2026-11-10 (3.3, R35-R40, after review):** full suite passes
(10,279 passed, 4 skipped, 20 xfailed, with the worktree's shell scripts
checked out with LF, DI-020); no sheet snapshot changed; three picker
goldens changed, each only by a `badge_modifiers` entry on the Bless and
Shield of Faith rows (`caster_described_spells`, Gabriel's and Edmund's);
`./typecheck.sh Combat` 0 errors, as on main; spell-mechanics `check` OK;
71 new tests. One expected value changed on purpose: a Half Cover target's
Dexterity save row reads "DEX +5 (cover)" (DI-066). Review found a monster's
Concentration save rolled outside `roll_save` (DI-071, fixed: R40) and two
tests that didn't prove the record went; both fixed. Parity with main
(3ed1d427, a `git archive` copy): one scripted fight with neither Bless,
Shield of Faith nor cover (custom conditions with a timer, a turn edge and
notes, a save effect with damage and a repeat save ending two conditions,
rolled, typed and monster attack rolls with condition modes, Hold Person
cast, two Concentration saves the monster rolls itself, five turns, an undo,
a removal, direct saves with Exhaustion, then a copy of the log continued
in a fresh window for three turns) gave identical cards, badge tooltips and
colours, dialog target rows and tooltips, log lines, status and reminder
texts, and combatant state (the records' new empty `modifiers` left out).

**Verified 2026-11-10 (3.4, R41-R47):** full suite passes (10,340 passed, 4
skipped, 20 xfailed); no sheet snapshot changed; three picker goldens
changed, each line read: a `badge_modifiers` entry (`ExtraDamageFrom` 1d6
Force) on the Hunter's Mark rows (`caster_described_spells`, Hanna's spell
and her Favored Enemy use, which casts it), and Divine Favor now described
(Edmund's row: `condition` "Divine Favor", `is_curated` true, its
`badge_modifiers` and its note in place of "Its text states damage that
isn't filled in: check it."; a new row in `caster_described_spells`).
`./typecheck.sh Combat` 0 errors, as on main; spell-mechanics `check` OK
(59 of 594 spells with combat effects); 59 new tests
(`tests/test_extra_damage.py`, 57, and two in `tests/test_active_effects.py`),
expected values from Hunter's Mark's and Divine Favor's text and the
glossary's Critical Hit, Resistance, Weapon Attack and Unarmed Strike.
Parity with main (d0b8085d, a `git archive` copy), seeded dice: one
scripted fight with neither spell (Bless cast on two; rolled attacks, a
Times 3 with misses, a save effect, three monster Bite buttons with a
Critical Hit and a miss applied with Enter, a typed attack roll and damage
in the main window, Edmund's Longsword and Handaxe picked in the dialog, one
with Times 2 and one with a typed total, an undo, four turns, then a copy of
the log continued in a fresh window with an attack and three turns) gave
identical cards and tooltips, dialog target rows and tooltips, result
label and Damage field texts, log lines (and which are public), the player
link, and combatant state, byte for byte. The same fight with Hunter's Mark
on the Tiger and Divine Favor on Edmund logged "Pirate's Hunter's Mark: +1
Force (1d6)" before "Tiger takes 5 Slashing ..." and "Tiger takes 1 Force
damage from Pirate", "Edmund's Divine Favor: +4 Radiant (1d4)" on each
weapon hit (none on the typed total), filled the Bite button's Damage field
with "6 Piercing + 5 Force", and the player link's hit lines read "5
Slashing + 1 Force" and "6 Slashing + 4 Radiant".

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
8. **Q15 as suggested** ("continue with plan", 2026-11-09):
   `SpellRules.school_note`, and "Wizard (Dunamancy)" read as Wizard plus
   that note. Built in S.4 (R25).
9. **No hand-fixing every spell yet** (the user, 2026-11-09: no okay "to fix
   all spells by hand until the proper engine/framework/support is in
   place"). Writing or correcting the combat effects of all spells one by one
   waits until the engine, framework and tooling they need exist (Phase 3's
   lasting effects and Phase 4's tooling). Until then, hand edits stay limited
   to the spells a step or a campaign needs; a sweep over all spells needs the
   user's go-ahead first.
10. **Q17: not every badge gets a record** (decided while building 3.3,
    2026-11-09, against the suggestion, for the user to overrule; R39). A
    record lasts while it says something: a tooltip, colour, duration,
    repeat save, concentration link or modifiers.

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

- `SpellRules` is the record's fields plus `usage_tags`, `target` and a
  `school_note` (R25); what the
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
| S.4 | Convert the rest (Q11) and retire the companion files: once every spell of a source has a class, its `_extended`/`_improved`/`_combat_effects` files and `DataSpell`'s companion handling go | **Done** (R26). Before that, **all but one spell** (Q11 as suggested: level by level). Cantrips (2026-11-09): 33 more classes. Levels 1-9 (2026-11-09): 487 classes, each checked against its JSON by the converter; then Q15 and DI-065 (R25) converted the 15 Dunamancy spells. 593 of 594 spells are classes; drift check clean; picker goldens unchanged; sheet changes all R20 wording, DI-062 slips or Ceremony's Ritual tag (see Verified). The companion entries nobody read (a spell with a class, or a record another source wins over: 797, 411 in `spells_aidedd_extended.json` and 386 in `spells_dnd5e_extended.json`) were removed, and the five files left empty deleted: every 2024 and aidedd companion file, and `spells_dnd5e_combat_effects.json`. The tools that wrote JSON handle classes (R24). Gate Seal, whose record had no components, was fixed in the scraper (DI-062) and converted last; then the last two companion files and every reader and writer of them went (R26) |
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
| `ExtraDamageFrom(amount, damage_type, attacks, when)` | Hunter's Mark, Hex: on the target, "hits from the caster deal 1d6 more" (the record's `caster`, R42) |
| `ExtraDamageOnHit(amount, damage_type, attacks, when)` | Rage damage, Divine Favor: on the attacker |
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
| 3.1 | `ActiveEffect` and `char["active_effects"]`; old keys read through it. Undo, log replay, the player view keep working. | **Done** (R28-R34): one record per badge in `Combat/Effects/active_effects.py`; the old keys are converted where a log is read; combat UI tests pass and an old fight log replays the same (`tests/test_active_effects.py`) |
| 3.2 | Rules conditions as data; `roll_save`, attack resolution and AC read modifiers. | **Done** (R27): saves behave as before, from data; attack rolls now count conditions too (DI-034), the monster action buttons cover as well (DI-033); rules-checker run on the table |
| 3.3 | `D20Bonus`, `D20Mode`, `AttacksAgainst`, `ArmorClass`, `Resistance`. | **Done** (R35-R40): Bless adds 1d4 to a rolled save (a monster's Concentration save included) and attack roll, and the log says so; Shield of Faith raises the AC an attack is compared with; cover adds to Dexterity saves (DI-066); ending the badge ends its modifiers; an old log replays as before (`tests/test_effect_modifiers.py`, `tests/test_active_effects.py`) |
| 3.4 | `ExtraDamageFrom` / `ExtraDamageOnHit`. | **Done** (R41-R47): Hunter's Mark adds 1d6 Force on its caster's hits (not another's, not a miss or a save effect), Divine Favor 1d4 Radiant on its caster's weapon hits, doubled on a Critical Hit, resisted per type, on each hit of Times; the log says so; a typed damage total gets a reminder instead; ending the badge ends it; an old log replays as before (`tests/test_extra_damage.py`, `tests/test_active_effects.py`) |
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
   PR, then spells level by level and features class by class. The
   level-by-level spell pass waits for Decision 9: not before the engine
   support is in place and the user says go.
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

- **R24. Converting a level also means the tools stop sending that level to
  JSON** (S.4). `tag_report.py` (the usage-tags skill) read only the JSON
  files, so it called every class spell untagged and `set-spell` would have
  written a JSON entry that `test_spell_classes` rejects: wrong since S.2,
  unnoticed while only 58 spells were classes. It now reads `SPELL_CLASSES`
  (a class wins over its record, a class-only spell is listed), reports the
  `SpellRules` line, and `set-spell` refuses a class spell with that line.
  The `spell-improved-descriptions` agent's work list names the class to
  edit instead of failing on `_data`. The JSON paths stay for the spells
  not converted yet.

- **R25. A school's note is a field; a ritual the record says only
  elsewhere is the casting time's** (S.4, Q15, DI-065). `SpellRules.school_note`
  holds Wildemount's "Dunamancy" / "Dunamancy:Graviturgy" and `ClassSpell.school`
  shows it in brackets, so the card is unchanged. A class "Wizard
  (Dunamancy)" is the Wizard class, and its note is the school's when the school
  has none (Sapping Sting, whose card now says "Necromancy (Dunamancy)"). The
  converter's parity check compares the school, the classes without notes and
  the set of note parts, not the text. Q15 suggested reading the class note "as
  Wizard plus that note": a separate class note would only have repeated the
  school's in every record. Converting the 2014 records also showed DI-065 was
  about to be baked into classes: the converter dropped `"ritual": true`.
  `DataSpell.casting_time_spec` now reads that key and a "(Ritual)" written into
  the school (Wristpocket) as `ritual=True`, the converter writes that spec, and
  Ceremony and Skywrite, converted just before, got it by hand.

- **R26. A scraped record is only the rules; everything else is the
  class's** (S.4's end, 2026-11-09). Gate Seal's components were missing
  because dnd5e.wikidot.com writes that label as
  `<strong>Components</strong>:`, colon outside the tag, and
  `DnD5eSpellScraper` matched only `Components:`. It now matches all four
  stat-line labels with or without the colon. Only Gate Seal's record was
  re-scraped (a full re-scrape would have been drift for hundreds of
  classes to merge); only its components changed. With it converted, the
  plan's leftovers went: `spells_dnd5e_extended.json` / `_improved.json`;
  `SpellFactory`'s companion merging (`_load_json` reads the three sources
  only; `improved_path`, `combat_effects_path` and their loaders are gone);
  `DataSpell`'s `usage_tags`, `target`, `improved_description` and
  `combat_effects`, so a record falls back to `Spell`'s defaults; the
  converter's companion removal (`remove_entry`, `companion_paths`,
  `--keep-json`); `spell_mechanics.py`'s JSON half (`format`, JSON entries in
  `check`, JSON writes in `add`, which now refuses a spell that can't be a
  class); `tag_report.py set-spell`'s JSON writes (it says where to edit);
  and `FeatureText.blocks_from_json`, which only `DataSpell` used. Better
  than the plan: instead of a JSON path for "a spell that can't be a class",
  there is none. A spell scraped later is converted first, and the tools
  say so. Tests: `test_every_spell_the_sources_have_is_a_class` and
  `test_no_companion_file_is_left` (a companion file written now would be
  silently ignored) replace the companion-entry tests; the converter's
  parity test checks a record against its class's rules only. The agents,
  the skills, HOWTO and IMPROVED_DESCRIPTIONS.md say "every spell is a
  class".

- **R27. 3.2 before 3.1: the modifiers come from the conditions a combatant
  already has** (2026-11-09). 3.2 doesn't need `ActiveEffect`: the rules
  conditions live in `char["conditions"]` by name, so the interpreter
  (`Combat/Effects/modifiers.py`, `modifiers_on(char)`) reads them there,
  a longer custom name counting as before. 3.1 adds `active_effects` as a
  second source of the same `(source, modifier)` pairs, and nothing that
  reads them changes. (In the end 3.1 gave the records no `modifiers` key;
  3.3 adds it, see R28.) What the plan didn't foresee:
  - **The table is its own module**, `Model/Content/RulesConditions.py`
    (`CONDITION_RULES`, one entry per glossary sentence), beside the
    vocabulary in `Model/Content/CombatModifiers.py` (R1).
  - **More modifier types than the plan's list**, each one a sentence the
    conditions say: `AutoFail` (STR and DEX saves), `CriticalHitsAgainst`,
    `ConditionImmunity` (Petrified's Poisoned), `HasConditions` (Paralyzed
    is Incapacitated; Unconscious, Incapacitated and Prone), and `Note` for
    every sentence that changes no roll, AC or damage. `D20Mode`'s rolls
    are a `D20Test` (attack roll, saving throw, ability check, initiative).
  - **`when` on a modifier, as on `CombatDamage`** (R14): what depends on
    where creatures are or what they see (Prone, Invisible, Frightened,
    Grappled, the Critical Hit from within 5 feet) is never counted, only
    noted ("Tiger is Prone (not counted): Advantage if the attacker is
    within 5 feet of it, Disadvantage if ..."). Principle 8 says prompt; a
    note is the prompt until the dialog knows distances.
  - **Attack rolls changed, on purpose.** "Behave as before" held for saves
    (same rolls, same notes, one reworded: "Restrained: Disadvantage,
    cancelling Advantage"), but "attack resolution reads modifiers" meant
    attacks gain what they never had (DI-034): the Custom dialog's rolls
    and a monster's action buttons count the attacker's and the target's
    conditions per target, with the dialog's mode, cancelling as the rules
    say. The log line says why (", Tiger is Restrained: Advantage"; the
    player link's parser drops it).
  - **A typed total is used as it is** (Decision 4): only an automatic
    failure overrides it, and a hit still says to check for a Critical
    Hit. The reminder comes before the roll instead, in the dialog's
    target rows ("DEX +3, Disadvantage", "DEX fails", "AC 15, Advantage",
    the reasons in the tooltip).
  - **AC reads modifiers** through `attack_rolls.armor_bonus` (cover plus
    `ArmorClass`), used by the dialog, the Attack roll field and now the
    monster action buttons, which ignored cover (DI-033). No condition has
    one; Shield of Faith will (3.3). A note about AC takes the whole bonus
    off, so it stays true when the effect ends.
  - **The other hard-coded rules went too:** Petrified's Resistance and
    Poisoned immunity (damage, `is_immune_to`, the player view's "says
    nothing about it") and `INCAPACITATING_CONDITIONS` (now the conditions
    that give Incapacitated) come from the table.
  - **`D20Bonus` is in the vocabulary but not counted yet:** Exhaustion's
    is per level, which isn't tracked, so it is noted as before. Counting
    it is 3.3 (done: R37; Exhaustion's stays a note).
  - **The rules-checker's fixes:** an uncounted mode that would cancel the
    counted one says so (an Unconscious target from farther than 5 feet:
    "..., a straight roll then"); a monster's action counts its own
    conditions with no target or several; a condition another makes it
    immune to does nothing (Petrified's Poisoned, Immunity: "doesn't affect
    you in any way"); a longer name ("Stunned by Stunning Strike") breaks
    Concentration and blocks Wild Shape (`incapacitates`); Invisible's
    Concealed note has the equipment sentence.
- **R28. The record is a `TypedDict` of plain values, with every key
  always there** (3.1, 2026-11-09). `ActiveEffect` in
  `Combat/Effects/active_effects.py`: `name` (the badge), `source` (the
  spell, feature or action), `caster`, `concentration` (who concentrates on
  it), `duration` (a timer, `time_left`/`duration`/`ticks_on`, or a turn
  edge, `until`/`of`/`turns_left`/`text`: the old entries' keys, so nothing
  that read them changed meaning), `repeat_save` (`ability`, `dc`, `mode`,
  `use_legendary_resistance`, `also`), `tooltip`, `tooltip_from`, `color`.
  A `TypedDict` keeps Decision 5's plain dict (undo's copy, the log's JSON)
  while pyright checks the keys. **No `modifiers` or `triggers` key yet:**
  nothing would read them, every log, undo point and expected record in the
  tests would carry an empty list, and adding one later is two lines
  (`new_effect` and the converter), with readers taking `.get(..., ())` for
  records written before. 3.2 landed first and reads modifiers only from
  `char["conditions"]`, through `modifiers_on(char)` in
  `Combat/Effects/modifiers.py`; 3.3 adds `modifiers` to the record (Bless,
  Shield of Faith), and `modifiers_on` then reads it as a second source
  beside the conditions (done in 3.3, with the key always there: R35).
  Today's repeat save is the one trigger; 3.5 can
  turn it into `AtTurnEnd(save)` in the same converter (Q19).
- **R29. One record per badge, not per application.** A repeat save that
  ends several conditions (R13) lives on its first condition's record with
  `also`, as before. Each badge comes off on its own (right-click, a timer,
  a save), and every old key was per badge name; a record per application
  would need a badge-to-record lookup on every removal. 3.6 still gets "every
  effect a concentration holds" from the `concentration` link on each
  record. A record lasts while it holds a tooltip, colour, duration, repeat
  save or link (`says_something`), and goes with its badge
  (`_remove_condition_from`); a badge with none of them has no record (Q17,
  kept so in 3.3: Decision 10, R39; modifiers are one more thing it holds).
- **R30. One tooltip, with what wrote it.** The three tooltip maps were read
  spell, then feature, then custom note, and two colour maps spell then
  feature. One `tooltip` keeps `tooltip_from` (`TOOLTIP_FROM`), and
  `describe` never lets a lower kind replace a higher one (the notes
  `_add_custom_condition` writes after a picked spell's card no longer win by
  being written last); the same kind without a colour keeps the colour (a
  monster action's text over a feature badge). That gives exactly what the
  maps showed, as no map was ever emptied on its own.
- **R31. A duration given again puts its record last; a repeat save doesn't
  move it.** The card's Timed Conditions list keeps its order (the old list
  put a re-given timer last). The order of turn-end saves now follows the
  records too; it differs from before only on one combatant with two repeat
  saves when one's condition gets a new timer from the Custom Condition
  dialog (the two save lines are then logged in the other order).
- **R32. A player's whole effects are kept with a fight in progress.**
  `PLAYER_FIGHT_KEYS` was `custom_condition_descriptions`, `repeat_saves`,
  `timed_conditions` (DI-028's fix) and is now `active_effects`. So a
  player's spell and feature badges keep their tooltip and colour when the
  fight is continued; before, the card rebuilt them from the badge's name
  (the same text, without notes typed in the dialog, and a feature's Uses
  Left as they are now, not as when it was used). Loading a log replaces a
  player's effects as a whole, as it did their timers.
- **R33. The converter runs where logs are read, not on every access.**
  `upgrade_old_keys` turns the seven old keys (`OLD_KEYS`) into records in
  `_take_combatants_from` (each combatant, and each player's saved fight
  state) and in `ending_conditions` (Summons and PartyAllies read earlier
  logs' combatants directly, on a copy). It reads as leniently as the old
  readers (`test_party_allies` gave entries with only a name). Nothing else
  knows the old keys.
- **R34. What moved and was renamed.** `_timed_condition_entry` is
  `duration_entry` (names instead of dicts), the timer arithmetic is
  `tick`, `_drop_repeat_save` is `drop_repeat_save`; `_tick_timed_conditions`
  is `_tick_effect_durations` and `_repeat_saves` `_end_of_turn_saves`;
  `_roll_repeat_save` takes the record. `source`, `caster` and
  `concentration` are filled in by the Custom Effect dialog, Cast Spell,
  Enable Feature and Wild Shape, but nothing reads them yet (3.6 will read
  `concentration`). `active_spells` stays: it is the caster's list of what it
  holds (the duration bar, `applied`), not an effect on a target, and 3.6
  joins the two through the link.
- **R35. The record's `modifiers` is always there, like its other keys**
  (3.3, 2026-11-09). R28 suggested readers take `.get("modifiers", ())`
  for records written before. Instead `new_effect` gives `[]` and
  `upgrade_old_keys` gives a 3.1 record without the key `[]` (on a copy, so
  `ending_conditions` still leaves a log alone), keeping R28's "every key
  always there"; the readers use `.get` anyway, for a dict built elsewhere.
  A record with only modifiers says something (`says_something`), so a
  badge whose spell gives modifiers always has one. An effect's modifiers
  count only while its badge is in `char["conditions"]`, so a record left
  behind by a path that takes the badge off directly can't keep counting.
  Records come from the three places that give a badge: the Custom Effect
  dialog copies its pick's (`EffectOption.badge_modifiers`, by badge name,
  so a badge typed over in the dialog gets none), Cast Spell and Enable
  Feature read the spell's or feature's own `combat_effects()`
  (`badge_modifiers`). Giving none keeps what a record has: a badge given
  again by hand keeps its spell's. A Bless from a 3.1 log has no modifiers
  and adds nothing, as it didn't then.
- **R36. A modifier as JSON is its type's name and its non-default fields**
  (`{"type": "D20Bonus", "tests": ["attack roll", "saving throw"],
  "amount": "1d4"}`), enums as their values: `modifier_to_dict` /
  `modifier_from_dict` in `Model/Content/CombatModifiers.py`, strict as
  step 1.2 (an unknown type or key, a bool for a number, a missing field:
  `ValueError` naming where). `CombatCondition.modifiers` uses it in
  `to_dict` / `from_dict`, and older data without it reads as `()`. A
  condition refuses modifiers on a rules condition (also under a longer
  name: its modifiers are the table's) and `HasConditions` (a badge gives a
  condition through `conditions`, and `held_conditions` reads only those).
  `D20Bonus`'s amount is now checked as dice or a number (`BONUS_AMOUNT`).
  The picker goldens show `badge_modifiers` only on the rows that have
  them, so no other row changed.
- **R37. `modifiers_on`'s source is a `Condition` or a name**
  (`Source = Condition | str`): a rules condition, a cover ("Half Cover") or
  an effect's badge ("Bless"). Saves label it by its text ("Bless: +3
  (1d4)"), attacks by whose it is ("Pirate's Bless: +3 (1d4)", as
  "Pirate's Exhaustion"). The plan stays free of dice: `RollPlan.bonuses`
  lists (label, amount), and the code that makes the roll rolls them
  (`saves.roll_bonuses`, used by `roll_save`, `roll_planned_attack` and a
  monster's action buttons, "rolled 15 (8+5+2)"), always after the d20, so
  a fight without bonuses throws exactly the dice it did. A typed total
  gets none (Decision 4). Exhaustion's `per_level` bonus and a bonus with a
  `when` stay notes.
- **R38. Cover is a source of modifiers too** (DI-066). The glossary gives
  both halves in one sentence ("+2 bonus to AC and Dexterity saving
  throws"), so `COVER_RULES` in `Combat/Effects/modifiers.py` holds an
  `ArmorClass` and a `D20Bonus` per degree, the most protective counting.
  So `attack_rolls.armor_bonus` is `armor_class_bonus` (cover included)
  and `cover_bonus` reads cover's part, for the "(cover)" texts.
  The dialog's reminders: a number folded into the bonus, dice after it
  ("DEX +5 (cover)", "WIS +1 +1d4", "AC 17 (cover), +1d4 to hit"), each
  source in the tooltip ("Bless: +1d4", "Half Cover: +2", "Shield of
  Faith: +2 AC").
- **R39. Q17 decided: no record for every badge** (Decision 10). The
  suggestion was yes once effects carry modifiers. But a rules condition's
  modifiers come from its name, so a record adds nothing to a plain Prone;
  `char["conditions"]` is written directly in about ten places (Bloodied,
  log replay, Summons, PartyAllies, Concentrating) that would all have to
  make and drop records; and every log and undo point would grow, which a
  parity check against the code before would see. A record still lasts
  while it says something, and modifiers are one more thing it can say;
  the card already reads every badge through `find_effect`, taking None as
  nothing to show.
- **R40. A monster's Concentration save is a save like any other** (3.3,
  after review; DI-071). With "monsters roll concentration" on,
  `_roll_concentration` threw `randint(1, 20)` plus the CON save itself, so
  a Blessed monster got no 1d4 and an Exhausted one no note. It now calls
  `roll_save(char, "CON", dc, "Neutral", one_die_if_straight=True)` and the
  keeps/loses line carries its note ("Tiger keeps concentration (DC 10,
  rolled 11, Bless: +3 (1d4))"). `one_die_if_straight` keeps the one d20 a
  straight Concentration roll always threw (`roll_save` otherwise throws
  two, keeping the first), so a fight without bonuses rolls the same dice.
  The other d20s the window rolls are not saves or attacks: initiative (the
  turn order's Roll buttons, a summon's `_roll_into_turn_order`) and the
  d20 Roll button with no roller; initiative modifiers (Incapacitated,
  Invisible) aren't in 3.3's scope.
- **R41. The two extra-damage modifiers have the same fields** (3.4,
  2026-11-10): `amount` (dice or a number, never signed or 0:
  `EXTRA_DAMAGE_AMOUNT`), `damage_type` (a `DamageType`), `attacks` (an
  `AttackKind`: `ANY`, "attack roll", the default, or `WEAPON`, "weapon
  attack") and `when`. The plan's `ExtraDamageFrom(source, ...)` has no
  `source`: whose hits count is the record's `caster` (R42), so the
  modifier stays what the spell says and the record says who cast it. As
  JSON (R36) `damage_type` and `attacks` are enum values
  (`{"type": "ExtraDamageOnHit", "amount": "1d4", "damage_type": "Radiant",
  "attacks": "weapon attack"}`). The names stay apart from a weapon's
  `Model/Content/ExtraDamage.ExtraDamage`, which is untouched. Rage's
  damage needs more than these fields (Q26), so it isn't in the vocabulary
  yet.
- **R42. A mark's caster is matched by name.** `caster` is a combatant's
  name, as `concentration` is: Cast Spell and Enable Feature write their
  source's, the dialog its source's (the card selected, or the one whose
  turn it is), Wild Shape the druid's. Names are what the window already
  finds combatants by (`_find_character_by_name`, the concentration links),
  and a fight's are unique (a second summon of a name is numbered). The
  dialog noted the caster only on a record that existed before the pick's
  modifiers made one (`_add_custom_condition` runs first); it now notes
  source and caster again after `give_modifiers`, with the same values, so
  a badge with only modifiers knows its caster too. `hit_extras` takes the
  attacker's `ExtraDamageOnHit` and the target's `ExtraDamageFrom` whose
  record's caster is the attacker, only while each badge is on (R35).
- **R43. Where the extra dice are rolled.** The dialog rolls an effect's
  damage when Apply is pressed, before any d20; that stays. A hit's extra
  is rolled per target and per Times copy in `_apply_custom_effect`, right
  after its attack roll and Bless's d4 (`hit_plan`, `roll_extra_damage`),
  so a fight without extras throws the same dice (the parity run, and
  `test_a_fight_without_extra_damage_rolls_the_same_dice`). A Critical Hit
  rolls the extra's dice twice ("Roll all of the attack's damage dice
  twice"), a number once. The extra joins the hit's part of its type, or is
  a part of its own (`with_extra_damage`), and `_deal_damage` takes each
  type in turn, so Resistance, Immunity and Vulnerability apply per type
  and once to an instance, and the Concentration DC is the hit's whole
  damage. A monster's action button rolls the extra after its own dice into
  the Damage field ("3 Piercing + 4 Force"), with the line in the result
  label, as Bless's notes there (that path logs the damage when Enter
  applies it); a target's `ExtraDamageFrom` only with one target. The main
  window's Attack roll and Damage fields take totals typed at the table,
  so they add nothing (Decision 4; Q27). Every other `roll_dice` /
  `randint` in the window was checked: initiative, a recharge's d6 and the
  d20 Roll button roll no damage.
- **R44. A typed damage total.** A Damage box with no dice that isn't the
  pick's own text was rolled at the table (`CustomEffect.typed_damage`):
  the extra isn't added to it, as a typed attack roll gets no Bless. A
  pick's own flat damage (an Unarmed Strike's "5 Bludgeoning") is the
  simulator's and gets it. The reminder is in the dialog's attack target
  rows, whatever was typed: "AC 15, +1d6 Force on a hit", "+1d4 Radiant on
  a weapon hit", each source in the tooltip ("Pirate's Hunter's Mark: +1d6
  Force on a hit") with "Rolled and added to a hit's damage, not to a
  total typed in".
- **R45. A weapon attack is known only from a weapon pick.**
  `EffectOption.weapon_attack` is True on a weapon's row and False on an
  Unarmed Strike's ("instead of using a weapon"; `is_unarmed_strike`), and
  None elsewhere: a spell can grant a weapon attack (True Strike), a 2024
  monster's "Melee Attack Roll" doesn't say, and a typed effect has no
  pick. `CustomEffect.weapon_attack` carries it, kept on the Times box's
  copies (which drop the pick). `WEAPON` extra damage adds nothing to an
  attack that isn't one, and is noted, not counted, when that isn't known
  ("Pirate's Divine Favor (not counted): +1d4 Radiant on a weapon hit");
  one with a `when` too.
- **R46. The extra's log line is the GM's.** "Pirate's Hunter's Mark: +4
  Force (1d6)" ("(2d6, critical hit)" on a crit) comes after the hit's line
  and before its damage lines, with `public=False`: the player link joins
  a hit's damage lines to its line, and any other public line between them
  would stop that. The players read "Hits Tiger (20) 5 Slashing + 4
  Force". The damage lines themselves are unchanged ("Tiger takes 4 Force
  damage from Pirate"), so replay and stats need nothing new.
- **R47. Divine Favor gained its combat effects** (Decision 9: one of the
  two spells 3.4 names). It had none, so its row was read from the text
  ("Its text states damage that isn't filled in: check it."). Its badge
  goes on the caster (Cast Spell already puts a Self spell's there; in the
  dialog the GM targets the caster's card), with one note saying so, as the
  rubric asks when the caster gets what the dialog gives its targets.
  Hunter's Mark's two notes stay as they were (Q21). Hanna's Favored Enemy
  row, a use that casts Hunter's Mark (2.5), carries the badge's modifier
  too. Divine Favor lasts a minute without Concentration: from the dialog
  its badge has a timer that ends it, but from Cast Spell it outlives its
  duration (DI-073).

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
  `ActiveEffect` is what it removes. *Not done in 3.1:* it is a field on
  `Model/Content/CombatEffect.py`, outside 3.1's scope. With 3.1 the dialog's
  half is one call per target (`_remove_condition_from`, which drops the
  record); suggest it as its own small step before 3.3.
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
- **Q16. Should Invisible count by default?** The glossary gives its
  Advantage/Disadvantage "unless a creature can somehow see you", so the
  usual case applies, but 3.2 gives both a `when` and only notes them
  (principle 8). *Suggestion:* count them, with "unless it can see it" as
  the note the GM can override with the mode buttons; decide together with
  DI-068, which makes the simulator see Invisible at all.
- **Q17** moved to Decisions (10, R39): no.
- **Q18. Show `source` and `caster` on the badge** ("from Edmund's Bless")?
  *Suggestion:* not until the GM asks; the log says it already.
- **Q19. Repeat saves as triggers.** *Suggestion:* in 3.5, `repeat_save`
  becomes an `AtTurnEnd` trigger in a `triggers` list, the converter reading
  `repeat_save` as it reads the old keys now.
- **Q20. Should the card show an AC with what adds to it** (Shield of
  Faith's 17, not the stat block's 15)? 3.3 counts it in every attack roll
  and shows it in the dialog's target rows, but the card still shows the
  stat block's AC, as it does under cover. *Suggestion:* yes, "AC 17 (15
  +2)", with cover too, in Phase 5 with the sheet chips; the player view's
  known-AC notes already take the bonus off (R27).
- **Q21. Bless's note now says what the badge counts.** "Each target adds
  1d4 to its attack rolls and saving throws" was the GM's reminder; now the
  simulator adds it, and the spell-mechanics rubric says not to restate what
  the form shows. *Suggestion:* in Phase 4, have the picker say a badge's
  modifiers itself (a generated note, as R14's `when`), give the rubric a
  `modifiers` line, then drop the hand-written sentence. Both notes were
  kept as they are in 3.3, so no row's text changed.
- **Q22. A badge typed by hand gets no modifiers.** Only the dialog's pick,
  Cast Spell and Enable Feature know a badge's source; typing "Bless" in the
  Custom Condition dialog gives a badge that adds nothing. *Suggestion:*
  leave it: the picker row is how a spell's badge is given, and a hand-typed
  name may mean something else. Revisit if the GM asks.
- **Q23. Monster abilities' badges and the encounter log** (DI-069): the
  log `asdict`s a monster ability, which drops a modifier's type. No monster
  ability gives a badge with modifiers yet. *Suggestion:* fix the encoder
  (`to_dict()` for `combat_effects`) before the first monster gets one, in
  Phase 4.
- **Q24. Moving the mark when its target drops to 0 HP** (Hunter's Mark,
  Hex: "you can take a Bonus Action to move the mark to a new creature").
  *Suggestion:* in 3.5 (prompts): when a target with a living caster's
  mark drops to 0, the turn reminder says "Hanna can move Hunter's Mark (a
  Bonus Action)", and a card's right-click "Move Hunter's Mark here" moves
  the record (caster, modifiers, concentration link and the caster's
  active spell's `applied` row) and spends the Bonus Action.
- **Q25. Hex's chosen ability** ("Disadvantage on ability checks made with
  the chosen ability"). *Suggestion:* Hex as a variant row per ability
  (R15), each badge "Hex" with `ExtraDamageFrom("1d6", NECROTIC)` and a
  `D20Mode((ABILITY_CHECK,), DISADVANTAGE, (ability,))`; the simulator
  rolls no ability checks, so that part is a reminder until it does. A
  Hex given again on a new target keeps the ability (the same variant).
- **Q26. Rage's damage** is a bonus to the weapon's own damage (no type of
  its own), and only "when you make an attack using Strength". *Suggestion:*
  with the Barbarian's features in Phase 4: `damage_type=None` meaning the
  hit's first part's type, and `AttackKind.STRENGTH`, which a weapon pick
  can tell (its ability, Finesse aside: then the GM's choice, a `when`).
- **Q27. The main window's Attack roll and Damage fields** take totals rolled
  at the table, so a mark adds nothing there and nothing says it should.
  *Suggestion:* after a typed attack roll hits, the status line adds "+1d6
  Force (Pirate's Hunter's Mark)", as the dialog's target rows do.
- **Q28. Should the extra's log line be public?** It's GM-only so the player
  link keeps joining a hit's damage to its line (R46), and the hit line
  already shows the Force. *Suggestion:* leave it; if players ask where the
  Force came from, let `public_log.py` read the line as part of the hit
  (kind "hit-extra") instead.

## Discovered issues

- **DI-060** (open): pre-existing pyright errors in the combat-effects tests;
  the Qt dialog test files (`test_combat_ui_custom_effect.py`,
  `test_combat_ui_player_server.py`) have about 30 more of the same kind
  (Optional Qt accessors, `QTest.keyClick` overloads). All tests pass.
- **DI-061** (open): homebrew Mira, Princess of the Loop has 6 abilities; the
  house rule is at most 4.
- **DI-062** (fixed): five spell records had malformed components ('V,S',
  'M(a diamond ...)', a stray 'Component: ', none at all). Since R20 the
  converter reads the first four. Gate Seal's (none) was a scraper bug,
  fixed and re-scraped (R26). The other four are typos on the wiki itself,
  copied faithfully; their classes have the right components.
- **DI-063** (fixed, R25): 15 Dunamancy spells had a school or class with a
  note; they are classes with a `school_note`.
- **DI-064** (open): Shield's casting time is cut off in the 2024 and 2014
  records ("...or targeted by the"); aidedd has the whole trigger.
- **DI-065** (fixed, R25): the 2014 records' `"ritual": true` was ignored, so
  2014-only ritual spells didn't show as rituals; Ceremony now does.
- **DI-033** (fixed, 3.2): a monster's action buttons ignored the target's
  cover; `_target_armor` adds `armor_bonus` (cover and modifiers).
- **DI-034** (fixed, 3.2): attack rolls didn't count conditions.
- **DI-067** (open, rules-checker, 3.2): Unconscious ends without leaving
  Prone ("When this condition ends, you remain Prone"); since Prone is now
  given through `HasConditions`, it goes with it.
- **DI-068** (open, rules-checker, 3.2): Invisible as a visibility state or
  spell badge isn't read by `held_conditions`, so its notes never show.
- **DI-066** (fixed, 3.3, R38): saving throws ignored cover's +2/+5 to
  Dexterity saves; cover is a source of a `D20Bonus` (and its `ArmorClass`).
- **DI-069** (open, found in 3.3): the encounter log writes a monster
  ability's combat effects with `dataclasses.asdict`, which drops a badge
  modifier's `type`, so `CombatEffect.from_dict` would refuse one. No
  monster ability has one yet (Q23). `Combat/EncounterLogs.py` was outside
  3.3's scope.
- **DI-071** (fixed, 3.3 review, R40): a monster's own Concentration save
  was rolled outside `roll_save`, so Bless's 1d4 and Exhaustion's note
  were missing from it.
- **DI-072** (open, 3.3 review): `CombatEffect.py`'s `_is_rules_condition`
  repeats `modifiers.rules_condition`'s name rule, as Model can't import
  Combat; the fix moves it into `RulesConditions.py`, off-limits for 3.3.
- **DI-073** (open, found in 3.4): a spell without Concentration cast with
  Cast Spell keeps its badge after its duration runs out (its active spell's
  `applied` is filled only for concentration spells), so Divine Favor's
  extra damage outlasts its minute unless the badge is taken off by hand.
  The dialog's pick gives the badge a timer, which ends it.
- **DI-070** (open, found in 3.3): `SpellClassConverter`'s `_IMPORTS` has no
  modifier names, so `spell_mechanics.py add` can't write a badge with
  modifiers into a module that doesn't import them; Bless and Shield of
  Faith were written by hand (Level1.py imports them). Phase 4 tooling.
- **DI-010** (open, hit again twice in S.4): `UPDATE_SNAPSHOTS=1` over many
  builds loses writes (JSONDecodeErrors, 27 builds unwritten), because
  `pytest.ini` runs `-n auto` without `--dist loadgroup`, so conftest's
  `xdist_group` does nothing. Until that's fixed, update with
  `UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -n 0 ...`.
- **DI-020** (open, hit again in 3.1): `tests/test_format_changed.py`'s three
  tests fail in a checkout with CRLF shell scripts (`core.autocrlf=true`);
  unrelated to the combat code.
- Found and fixed: `test_an_entry_rides_only_on_its_own_sources_record` found
  no subject once every spell in both sources was a class; it hides the
  classes now (S.4). `tag_report.py` ignored class spells (R24); the text-reading tests dropped a spell's data by its old
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
  the `rules-checker` agent reviews the condition table. 3.1:
  `tests/test_active_effects.py` (the helpers; the old keys converted; an
  old-format log and the same log in the new format continued and played
  two turns, compared with each other and with what the old code showed).
  3.3: `tests/test_effect_modifiers.py` (the JSON form; a condition's
  modifiers; Bless, Shield of Faith and cover from their rules text, in the
  plans, the rolls, the log, the dialog's reminders; the badge ending by
  hand, timer and Concentration) and a 3.1 log replaying as a new one in
  `tests/test_active_effects.py`. 3.4: `tests/test_extra_damage.py` (the
  JSON form and its strict errors; `hit_plan` for the caster, another
  attacker, a weapon attack, one that isn't and one not known, a `when`;
  in the window a hit, a miss, a save effect, a Critical Hit, Resistance to
  Force, Times, a typed total, the monster buttons, the log lines and the
  player link, the dialog's reminders and its weapon picks; the badge
  ending by hand, timer and Concentration; the same dice without extras)
  and a 3.1 and a 3.3 log's Hunter's Mark adding nothing in
  `tests/test_active_effects.py`.

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
