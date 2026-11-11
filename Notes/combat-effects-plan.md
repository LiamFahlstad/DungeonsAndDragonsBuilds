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

**Keep the overhead low (the user, 2026-11-10).** Only the user works in this
codebase, so a step doesn't need the full multi-agent ceremony. Make the
change and move on; the full suite can run later.

- Don't run the whole suite after every step. Run only the few test files the
  step touches (e.g. `./run_tests.sh -q tests/test_extra_damage.py
  tests/test_active_effects.py`).
- Skip the character-creation tests: sheet snapshots
  (`test_build_snapshots`, `test_order_invariance`, `test_all_builds`), the
  builder, class, subclass, feat, species and spell-slot tests. A combat
  effects step doesn't change a character sheet; run them only if the step
  edits builder or sheet code.
- No parity runs against main, `verify-agent-work`, `code-reviewer` or
  `rules-checker` passes per step unless asked.

## Status (2026-11-11, Phase 3 done, Phase 4's tooling (4.1, 4.2, 4.4) done, and 4.3's first party done: lasting effects are one list, the rules conditions are data, effects carry modifiers the simulator counts, hits deal the extra damage effects give, badges act as turns start and end, a concentration ends everything linked to it, and every spell and feature of the Curse of the Lich party is described)

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
| 3 | Lasting effects (3.1-3.6) | 3.1 **done** (R28-R34): `char["active_effects"]`, one plain dict per badge, in the new Qt-free `Combat/Effects/active_effects.py`; the seven old keys are read only by its `upgrade_old_keys`, where a log is read; an old fight log replays the same (`tests/test_active_effects.py`). 3.2 **done** (R27), ahead of 3.1: the rules conditions are data, and saves, attack rolls (all three paths), AC, damage Resistance and condition immunity read them. 3.3 **done** (R35-R40): a badge's `CombatCondition` says its `modifiers`, the record keeps them as JSON, and `modifiers_on` reads them beside the conditions and cover; Bless's 1d4 is rolled into the saves (a monster's Concentration save too, R40) and attack rolls the simulator makes, Shield of Faith's +2 counts in AC, cover's +2/+5 in Dexterity saves (DI-066); a typed total stays as typed, with the bonus as a reminder in the dialog. 3.4 **done** (R41-R47): `ExtraDamageFrom` (on the target, from its effect's caster) and `ExtraDamageOnHit` (on the attacker); Hunter's Mark's 1d6 Force on its caster's hits and Divine Favor's 1d4 Radiant on its caster's weapon hits are rolled into the hits the dialog and a monster's action buttons deal, doubled on a Critical Hit, each type resisted on its own; a typed damage total stays as typed, with the extra as a reminder in the dialog. 3.5 **done** (R48-R53): `AtTurnStart` / `AtTurnEnd` are modifiers on a badge that name a row of their spell; Heroism's Temporary Hit Points are given as its target's turn starts, and Spirit Guardians asks, as each enemy of its caster ends its turn, with a button that opens the Custom Effect dialog with its damage row picked. 3.6 **done** (R54-R56): ending a concentration also ends every record linked to it (`held_by_concentration`), a creature leaving the fight ends its concentration first, and a badge another running effect still holds is relinked to that effect's caster |
| 4 | One `combat-effects` skill; feature agent; content rollout | 4.1 **done** (R57-R60): the `combat-effects` skill and `combat_effects.py` (renamed from spell-mechanics), with the principles, a Features section, `features`, `coverage` and `notes`, and features in `check`; `is_curated` is `is_described`. 4.2 **done**: the `feature-combat-effects` agent (opus); the spell agent is `spell-combat-effects`. 4.4 **done**: `coverage`. 4.3 (content): **Curse of the Lich done** (R61-R65, 2026-11-11): spells 44/44, features 23 described, 37 nothing to apply, none read from text; Time Loop PR was already done. Next: spells level by level and features class by class, which wait for the user's go (Decision 9) |
| 5 | Sheet chips, monster score | Not started |
| 6 | **Triggers** (new concept, 2026-11-11; see its section): a row or badge says *when* it's used (a hit, damage taken, dropping to 0, ...), and the simulator applies it itself (AUTO) or asks with a pop-up as it happens (ASK) | 6.1-6.3 **done** (R66-R73, 2026-11-11): `CombatTrigger` on a row (`CombatEffect.trigger`, `Model/Content/CombatTriggers.py`), `outcome_firings` with its gates and modes, and the hit hooks in all three hit paths: when Kivi hits a Large or smaller creature and deals it damage, one pop-up per Apply asks about Hill's Tumble; Apply gives Prone, spends a Giant Ancestry use and logs it, inside the hit's undo step. Only `HIT` and `MISS` fire; the other events are data. 6.4 **done** (R74-R77, 2026-11-11): a monster's hit that gives a condition in a sentence of its own ("If the target is a Large or smaller creature, it has the Prone condition", "..., and the target has the Poisoned condition until the end of its next turn", "the Grappled condition (escape DC 13)") is read as a rider row of its own ("Tree Club: Prone") with an AUTO `after=` trigger: the Hill Giant's Tree Club knocks a Large target Prone from its button and Enter and from the dialog, asks when the size isn't known, and does nothing to a Huge target or on a miss. 101 riders in the catalog. Next: 6.5 (being hit) |

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
Radiant on weapon attacks; newly described, R47); with triggers on their
badge (3.5, both newly described): Heroism (`ConditionImmunity` to
Frightened and `AtTurnStart` of its "Heroism: Temporary Hit Points" row)
and Spirit Guardians (`AtTurnEnd` of its "Spirit Guardians: damage" row,
for its caster's enemies, with a `when`), so 61 spells have combat effects.

**4.3, Curse of the Lich (2026-11-11).** The party's last 14 spells: Booming
Blade and Green-Flame Blade (an attack row as True Strike's, and a later
step each: the Thunder for moving, the leaping fire), Protection from Evil
and Good (a badge with `AttacksAgainst` Disadvantage and a `when`), See
Invisibility (a badge on the caster), Silence (Deafened, with a note), and
`[]` for Elementalism, Mage Hand, Prestidigitation, Ceremony, Comprehend
Languages, Detect Magic, Silent Image, Misty Step and Zone of Truth: 75
spells have combat effects. The party's 46 features left: Kivi's Monk
(Martial Arts' Bonus Unarmed Strike, Flurry of Blows, Patient Defense's
Dodge badge, Step of the Wind, Deflect Attacks and its redirect, Uncanny
Metabolism, Elemental Attunement and its Strength save), Giant Ancestry
(all six ancestries), Large Form (from level 5), Edmund's Divine Sense and
Abjure Foes (Channel Divinity), Sacred Weapon, Fiendish Legacy's and Fey
Touched's free castings, Obmar's Second Wind and Illuminated Cartography,
Thum's Steady Aim; the rest `[]` (senses, proficiencies, languages,
Spellcasting, riders on weapon rows, the owner's own resistances).

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

**Verified 2026-11-11 (6.4, R74-R77), low overhead:** every combat test
file (`tests/test_combat*.py`, the effects, triggers, picker rows, spell,
feature and monster combat-effects files: 2,237; not the full suite)
passes; `combat_effects.py check` OK; pyright 0 errors on the changed
source files and `tests/test_hit_triggers.py`. 25 new tests there (95 in
all), with expected values from the stat blocks' text: Tree Club and Trash
Lob as rows, the rider shapes (a turn's duration, the source's or the
target's; two conditions; an escape DC "from one of two claws"; "until the
grapple ends"; a MeleeAttack's "If the target is Medium or smaller"; "While
Grappled, ..." after it), a `when` and "Once per turn", five sentences that
say more and stay text, and in the window the button and Enter, the dialog,
Times 2, a Huge target, a miss, an unknown size, a typed hit, one undo, and
an escape DC on the badge. No picker golden changed: the party has no
monster rows, and the four homebrew monsters' hits are written as combat
effects (Mirelle's) or say more than a rider (Curse Body Broken's "if ...
doesn't have another creature grappled"). Five older tests that read a
hit's condition off its attack row now read it off the rider row (Bite's
Grappled, the Lich's Paralyzing Touch twice, the Tiger's Rend).

**Verified 2026-11-11 (6.1-6.3, R66-R73), low overhead:** 20 combat test
files pass (1,490: the new `tests/test_hit_triggers.py` with 70 tests,
`test_turn_triggers.py` unchanged and passing, extra damage, active
effects, picker rows, feature, spell and monster combat effects, the Custom
Effect dialog's files, fast play, settings, layering; not the full suite);
`combat_effects.py check` OK (75 of 594 spells); pyright 0 errors on
`Combat/CombatUIQt`, `Combat/Effects`, `Model/Content` and the changed tests
and script. One picker golden changed, Kivi's, in one row (Hill's Tumble):
its note went and a `trigger` key came, `{"event": "hit", "largest_target":
"Large", "needs_damage": true}`, nothing else. The tests take their values
from Hill's Tumble's text (a Large Ogre asks, a Huge Hill Giant, a miss, 0
damage after Immunity, no uses left, an already Prone Ogre give nothing, an
unknown size asks with the reason, 2 uses at Proficiency Bonus 2), and drive
each hit path once: an attack roll and damage typed together, the Attack
roll field's Enter then the Damage field's, a monster action button, and
the Custom Effect dialog's attack loop (Times 2 asks once). The pop-up was
looked at in a screenshot.

**Verified 2026-11-11 (4.3, Curse of the Lich, R61-R65), low overhead:**
every combat test file plus the spell, feature and monster combat-effects
tests pass (3,380; not the full suite); `combat_effects.py check` OK (75 of
594 spells); pyright 0 errors on every changed source file (the test file
keeps its DI-060 errors). Picker goldens: the six party members' and
`caster_described_spells`, every changed row read field by field against
the rules text (Kivi's strikes +6 / 1d6 + 4 like his Unarmed Strike row,
Deflect Attacks 1d10 + 8 (DEX 4 + Monk 4), its redirect DC 13; Sacred
Weapon +2 (Edmund's CHA); Clover's leaping fire 4 Fire; Second Wind 1d10 +
1); the rows that went are the `[]` features, which the picker hides.
Five tests picked Edmund's Channel Divinity row, now Divine Sense (a use of
it, still logged and counted as Channel Divinity); one needed an always-on
feature that isn't described, which Edmund no longer has, so it adds one.

**Verified 2026-11-10 (4.1/4.2, R57-R60), low overhead:** the spell,
feature and monster combat-effects tests, the picker goldens, the Custom
Effect dialog's tests and `test_claude_config.py` (the agent index) pass
(1,987); the picker goldens changed only by `is_curated` -> `is_described`;
`combat_effects.py check` OK (61 of 594 spells, party features of every
campaign); `./typecheck.sh` adds no errors (the three in
`test_feature_combat_effects.py` and `test_monster_combat_effects.py` are
on HEAD too, DI-060). `coverage`: Curse of the Lich spells 30/44, features
8 described, 6 nothing to apply, 40 read from text, 6 extensions without
effects; Time Loop PR spells 33/33, features none left.

**Verified 2026-11-10 (3.6, R54-R56), low overhead:** every combat test
file passes (`tests/test_combat*.py`, summons, party allies, picker rows,
wild shape and the effects files: 1,727 + 985 tests; not the full suite);
no picker golden changed; `./typecheck.sh` 0 errors on every changed file;
20 new tests (`tests/test_concentration_effects.py`), expected values from
the glossary's Concentration and Bless's text.

**Verified 2026-11-10 (3.5, R48-R53), low overhead:** every combat test
file passes (40 files, 3,407 tests; not the full suite); one picker golden
changed (`caster_described_spells`), by four new rows, each read: Heroism
and its Temp HP row, Spirit Guardians and its damage row (DC 15 WIS, 3d8
Radiant, half, upcast 1d8, `counts_uses` false); no party member's golden
changed (none has either spell). `./typecheck.sh` 0 errors on every changed
file; spell-mechanics `check` OK (61 of 594 spells with combat effects); 36
new tests (`tests/test_turn_triggers.py`).

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
11. **Work in the main checkout and push to main** (the user, 2026-11-10,
    after 3.4: "stop this worktree and non main push stuff. I want edits
    here and to push towards main"). No `isolation: "worktree"` for any
    step, no agent branches, no parity runs that rely on a worktree; every
    step is edited in the main checkout, committed there and pushed to
    origin main. (CLAUDE.md says the same for all work.)
12. **Q40-Q45 as suggested** (the user, 2026-11-11: "start on 6.1-6.3",
    taken as accepting them, as "continue with plan" did for Decisions 7
    and 8): a modal pop-up for hits, one per Apply with a checkbox per
    (target, trigger); a row with no uses left is left out and said in the
    status line; an unknown attack kind asks; the trigger is a field on the
    row (`CombatEffect.trigger`); a declined prompt logs a GM-only line.
    Built in 6.1-6.3 (R66-R73), with the setting as one checkbox (R71).

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
12. **A row says what, a trigger says when** (Phase 6). "Right after you
    hit ..." in a note is a trigger that wasn't written down. The simulator
    applies a triggered row itself only when the rules say it happens and
    it can check every gate. Otherwise it asks; it never decides for the
    GM.

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
    trigger=None,   # a CombatTrigger (Phase 6, Model/Content/CombatTriggers.py)
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
one), `WhenHit(effect)` (Phase 6 widens this to every event of a fight:
see "Triggers"). Position-dependent ones are prompts. The rules
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
| 3.5 | Triggers and prompts. | **Done** (R48-R53): Heroism gives its caster's spellcasting modifier in temp HP as each of its target's turns starts (not on others', not after the badge or Concentration ends, taken back by undoing Next); Spirit Guardians asks about each enemy of its caster as its turn ends, once, never about an ally, the caster or a dead creature, and rolls nothing itself; the prompt opens the dialog on its caster and that creature with the damage row picked, spending no slot (`tests/test_turn_triggers.py`) |
| 3.6 | Concentration ends every `ActiveEffect` it holds. | **Done** (R54-R56): dropping Bless removes its badge, record and 1d4 from every target by every path (Ctrl+C, a failed save, Incapacitated, death, a new concentration, ending it early, its minute running out, its caster leaving the fight); a badge two casters hold stays with the one still concentrating (`tests/test_concentration_effects.py`) |

### Phase 4: content and tooling

1. **Done** (R57-R60). Rename the `spell-mechanics` skill and agent to
   `combat-effects` (Q2), add the principles above and a feature rubric (what
   the first batch of features showed: an extension's row, `with_bonus`, a
   feature casting a spell), and give the script a features mode (`todo
   --campaign` for features too) and a `notes` report (principle 7).
2. **Done.** A `feature-combat-effects` agent (opus) that writes
   `combat_effects()` for a named class, subclass or party.
3. Content: the rest of the Curse of the Lich party (Kivi's Monk features,
   Obmar's, Edmund's Channel Divinity; their 2014-only spells), then Time Loop
   PR, then spells level by level and features class by class. The
   level-by-level spell pass waits for Decision 9: not before the engine
   support is in place and the user says go.
4. **Done** (`combat_effects.py coverage`). A coverage line per campaign.

### Phase 5: beyond the dialog (optional)

Sheet chips ("DEX save · half · 8d6 Fire") from the same data;
`monster_score.py` reads `combat_effects`.

## Triggers (Phase 6, new concept, 2026-11-11)

**Why** (the user, 2026-11-11: "when a hill giant hits someone I want a
pop-up to ask if they fall prone or not. This is better than me needing to
remember to click and load the feature"). A row the GM has to remember to
pick at the right moment gets forgotten. Today:

- Kivi's **Hill's Tumble** (Goliath, `GoliathFeatures.py`) is a picker row
  that gives Prone, with the note "Right after you hit a Large or smaller
  creature with an attack roll and deal damage to it." Nothing offers it
  when Kivi hits.
- The **Hill Giant's Tree Club** (`CR_5/monsters.py`, generated) says "If
  the target is a Large or smaller creature, it has the Prone condition."
  The turn column shows that as "Also: ..." under the button, and nothing
  applies it. Pressing Enter in the Damage field deals the damage only.

A **trigger** says *when* a row is used. When nothing is left to decide,
the simulator applies the row itself. Otherwise it asks, with a pop-up, at
the moment the thing happens. 3.5's `AtTurnStart` / `AtTurnEnd` are the
first triggers (R48-R50): a badge's modifier that names a row, fired as a
turn starts or ends. Phase 6 widens "when" from turn edges to the other
events of a fight, and lets a source's own row carry a trigger, not just a
badge.

### What a trigger is

1. **Event:** what happens in the fight (a hit, damage taken, a failed
   save, dropping to 0 HP, ...).
2. **Role:** the owner's part in the event. The owner did it ("you hit"),
   it was done to the owner ("a creature hits you"), or, for a badge, it
   happened to someone the badge's caster opposes (`WhoseTurn.ENEMY`'s
   idea, R51).
3. **Gates:** what must also be true. Some the simulator can check: the
   target's size (`char["size"]`), the attack kind when it's known (a
   weapon row in the dialog; R44's `weapon_attack`), a hit or a Critical
   Hit, damage dealt after Resistance and Immunity, once per turn, uses or
   a Reaction left, the target not already having the condition. Whatever
   else matters goes in a `when`, which only the GM judges (as everywhere
   else, principle 8).
4. **Response:** the row it uses. For a row's own trigger that's the row
   itself; for a badge, the row it names (R49). **Mode:** AUTO, ASK or
   REMIND (below).

### Trigger types, from the content

Survey (2026-11-11): 351 `("Trigger", ...)` facts in `CharacterContent`'s
feature and spell descriptions, and about 116 on-hit condition riders in
the generated monster stat blocks (Prone 33, Grappled 32, Poisoned 20,
Restrained 12, 19 others). 90 of those riders are gated on size ("If the
target is a Large or smaller creature").

| Event (role) | Examples | Can the simulator see it? | Default mode |
|---|---|---|---|
| **Turn starts / ends** (bearer, enemy) | Heroism, Spirit Guardians; "A Frightened creature starts its turn within 60 feet" | Yes (**built**, 3.5) | AUTO if it only gives Hit Points, else REMIND |
| **Hits** (owner attacks) | Hill's Tumble, Fire's Burn, Frost's Chill, Stunning Strike, Paladin's Smite, Battle Master maneuvers, Sneak Attack, Open Hand Technique, Weapon Mastery Topple/Vex/Sap (Q38); monster riders: Tree Club's Prone, a Wolf's Prone, "Grappled (escape DC 13)" | Yes, in all three hit paths | A monster rider: AUTO. "You can": ASK |
| **Misses** (owner attacks) | Graze mastery, "You miss with an attack roll" | Yes | ASK |
| **Is hit, before damage** (owner is the target) | Shield, Deflect Attacks, Uncanny Dodge, Stone's Endurance (Q39), a monster's Parry | Yes, but the answer changes the hit (AC, damage), so it must come before damage is dealt | ASK |
| **Takes damage, after** (owner is the target) | Hellish Rebuke, Storm's Thunder, Absorb Elements; badges: Armor of Agathys, Fire Shield (Q30) | Yes (`_damage_target`) | ASK (a melee gate isn't known on a typed hit) |
| **Hit Point thresholds** | Bloodied; drops to 0 (Relentless Endurance, Relentless Rage); reduces a creature to 0 (Dark One's Blessing, Great Weapon Master's extra attack) | Yes (`_damage_target` knows a knockout) | AUTO if it only gives Hit Points (Dark One's Blessing), else ASK |
| **D20 tests** | Fails a save (Indomitable, Diamond Soul); another creature's roll (Cutting Words, Silvery Barbs, Bardic Inspiration) | Only for rolls the simulator makes (`roll_save`, attack rolls); a roll typed in from the table, no | ASK |
| **Casts or uses** | Casts a spell of a school or with a slot (Arcane Ward, Disciple of Life); uses a feature (Flurry of Blows -> Open Hand Technique, Action Surge -> Tactical Master) | Yes (Cast Spell, the dialog's pick) | ASK (a choice between options) |
| **Initiative** | "You roll Initiative": Uncanny Metabolism, Fighting Spirit, Superior Inspiration | Yes, as a fight starts | AUTO for regaining uses, else ASK |
| **Movement and position** | Enters or ends its turn in an area, moves into reach (Sentinel, Opportunity Attacks), falls, an ally within 5 feet is attacked (Protection, Interception) | No (principle 8) | REMIND at most; otherwise left to the picker |

### Modes

- **AUTO:** the rules say it happens ("it has the Prone condition"), every
  gate is checked, and there's nothing to choose. The simulator applies
  it and logs it, as it gives Heroism's temp HP (R50).
- **ASK:** a pop-up when it happens, for example: "Kivi hits Ogre (Large).
  Use Hill's Tumble? Ogre has the Prone condition. 2 of 2 uses left."
  with [Apply] [Skip] [Edit...]. Edit opens the Custom Effect dialog with
  the row picked. A trigger asks when its source says "you can", when it
  costs something (a use, a Reaction, a slot), when it has a `when`, or
  when a gate can't be checked (a size or attack kind not known). A rider
  that would be AUTO asks instead when one of its gates is unknown.
- **REMIND:** a button in the turn column, as 3.5's Spirit Guardians. For
  things only the GM can see (where creatures are).

What a trigger applies goes through the same path as picking its row in
the Custom Effect dialog (spending, logging, conditions, badges, their
records). It happens inside the undo step of the hit that fired it, so one
undo takes back the hit and what it triggered. Declining a prompt changes
nothing (Q45). No new log format: the log reads as if the GM had picked
the row ("Kivi uses Hill's Tumble", "Ogre has the Prone condition").

### The model (sketch)

In `Model/Content/` (principle 4), next to `AtTurnStart` /
`AtTurnEnd`:

```python
class TriggerEvent(StrEnum):
    HIT = "hit"                    # the owner hits
    MISS = "miss"
    HIT_BY = "hit by"              # before damage
    TAKES_DAMAGE = "takes damage"  # after damage
    BLOODIED = "bloodied"
    DROPS_TO_ZERO = "drops to 0"
    REDUCES_TO_ZERO = "reduces to 0"
    FAILS_SAVE = "fails a save"
    ROLLS_INITIATIVE = "rolls initiative"
    CASTS_SPELL = "casts a spell"
    USES = "uses"                  # another row of the same source

@dataclass(frozen=True)
class CombatTrigger:
    event: TriggerEvent
    optional: bool = True                   # "you can": ASK; False: it happens
    after: str = ""                         # only after this row of the source ("Tree Club")
    attacks: AttackKind = AttackKind.ANY    # widened: MELEE, RANGED, UNARMED, SPELL
    largest_target: CreatureSize | None = None  # "a Large or smaller creature"
    needs_damage: bool = False              # "and deal damage to it"
    critical_only: bool = False
    once_per_turn: bool = False
    reaction: bool = False                  # spends the owner's Reaction (action_uses)
    when: str = ""                          # what the GM judges: always ASK
```

It goes in one of two places:

- **On a row:** `CombatEffect.trigger`, meaning "this row is used when
  ...". This is for what a creature always has: a feature, a monster's
  ability, a reaction spell it knows (Shield, Hellish Rebuke). The row
  stays in the picker for use by hand.
- **On a badge:** a modifier `OnTrigger(trigger, effect="<row name>")`
  next to `AtTurnStart` / `AtTurnEnd` (R48, R49). This is for lasting
  effects: Armor of Agathys, Fire Shield, moving Hunter's Mark (Q24).
  `AtTurnStart` / `AtTurnEnd` stay as they are (Q46).

The two examples:

```python
# Kivi's Hill's Tumble: the trigger replaces the "Right after you hit ..." note
CombatEffect(
    name="Hill's Tumble",
    conditions=(CombatCondition(Condition.PRONE),),
    trigger=CombatTrigger(
        TriggerEvent.HIT, needs_damage=True, largest_target=CreatureSize.LARGE
    ),
)
# The Hill Giant's Tree Club, read from its text (monsters.py is generated)
CombatEffect(name="Tree Club", roll=EffectRoll.ATTACK, attack_bonus=8, damage=(...,))
CombatEffect(
    name="Tree Club: Prone",
    spends_use=False,
    conditions=(CombatCondition(Condition.PRONE),),
    trigger=CombatTrigger(
        TriggerEvent.HIT, optional=False, after="Tree Club",
        largest_target=CreatureSize.LARGE,
    ),
)
```

A monster rider becomes its own row (`after=`), not a condition on the
attack row. The main window's Damage field never applies an attack row's
conditions, but a rider row works from every hit path. Ice Knife's
explosion and Green-Flame Blade's leaping fire, today later steps the GM
picks by hand, can get the same `after=` (as `USES`, or `HIT` for the
fire).

### The interpreter and the hooks

- `Combat/Effects/triggers.py` (Qt-free, beside `firings`): an
  `AttackOutcome(attacker, target, hit, critical, kind, row, damage_dealt)`
  and `outcome_firings(chars, outcome, rows_of)`. Each `Firing` gets a
  `mode` and a `why` ("Ogre's size isn't known"). `rows_of(char)` gives a
  combatant's rows that have a trigger, from `feature_options`,
  `spell_options` and its monster abilities. They are built once per
  combatant and rebuilt when its sheet or form changes (Wild Shape). The
  gates are checked here, not in the window.
- One hook per event in the window, called from every path that makes the
  event:
  - `_after_attack(outcome)`: the dialog's attack loop (after
    `_deal_damage`); the main window's `_do_apply_damage` when it checked
    an attack roll; a monster button's hit. `_roll_action` remembers the
    action it rolled, so Enter knows it was Tree Club (`after=`).
  - `_before_hit(outcome)` (6.5): before damage, for Shield and the
    like. The answer may turn the hit into a miss or take damage off it.
  - `_damage_target`: `TAKES_DAMAGE`, `BLOODIED`, `DROPS_TO_ZERO`,
    `REDUCES_TO_ZERO`.
  - `roll_save` (only saves the simulator rolls): `FAILS_SAVE`. Initiative:
    `ROLLS_INITIATIVE`. Cast Spell and the dialog's pick: `CASTS_SPELL`,
    `USES`.
- **Order on one hit:** the target's before-hit reactions, then the damage,
  then the attacker's AUTO riders, then one pop-up with the attacker's ASKs
  and the target's after-damage reactions.
- **One pop-up per Apply** (Times 3, Multiattack's two Tree Clubs), with a
  row per (target, trigger) and no repeats. A row is left out when the
  target already has every condition it gives, when it's once per turn
  and was used this turn, or when the target is dead.
- A setting, `ask_triggers` (pop-up / turn-column button / off), like
  `ask_concentration_saves`.

### Steps

| # | Step | Done when |
|---|---|---|
| 6.1 | **Done** (R66, R67). `TriggerEvent`, `CombatTrigger`, `CombatEffect.trigger`; `AttackKind` widened. Follow the checklist for adding a field. | Invalid combinations raise (e.g. `after` naming no row of the source, `largest_target` on an event with no target); `to_dict` / `from_dict` round-trip strictly; an old log still reads; `combat_effects.py check` refuses an `after` that names nothing |
| 6.2 | **Done** (R68). The interpreter: `AttackOutcome`, `outcome_firings`, `rows_of`, the gates and the mode. | Tests with expected values from the rules text: Hill's Tumble on a Large target asks, on a Huge one gives nothing, on a miss nothing, on 0 damage (Immunity) nothing, with no uses left nothing (Q42), on an already Prone target nothing, on a target of unknown size asks with the reason |
| 6.3 | **Done** (R69-R73). **First slice:** the hit hooks in the three paths, the pop-up and the setting; Kivi's Giant Ancestry (Hill's Tumble, Fire's Burn, Frost's Chill) gets triggers in place of the `on_hit` note (principle 7). | A rolled or typed hit by Kivi on an Ogre pops up Hill's Tumble once; Apply gives Prone, spends a use and logs it; one undo takes back the hit and the Prone; Times / Flurry of Blows ask once per Apply; the picker golden's only change is the note going |
| 6.4 | **Done** (R74-R77). Monster riders: the monster text reading turns "Hit: ... [If the target is a <size> or smaller creature,] it has the <condition> condition" (and "Grappled (escape DC N)") into a rider row with an AUTO trigger. A homebrew `MeleeAttack`'s `additional_ruling` reads the same way. | The Hill Giant's Tree Club knocks a Large target Prone from its button and Enter, and from the dialog; asks when the size isn't known; does nothing to a Huge target or on a miss; the picker goldens' new rider rows read against their stat blocks |
| 6.5 | Being hit: `HIT_BY` before damage (Shield, Deflect Attacks, Stone's Endurance), and `TAKES_DAMAGE` after (Hellish Rebuke, Storm's Thunder; badges via `OnTrigger`: Armor of Agathys). Spends the Reaction (`_add_action_use`). Takes over Q30 and Q39. | Shield asked as a hit lands turns it into a miss when +5 is enough, and spends the Reaction and a slot; Deflect Attacks takes its roll off the damage; a used Reaction asks no more this round |
| 6.6 | Hit Point thresholds: `BLOODIED`, `DROPS_TO_ZERO`, `REDUCES_TO_ZERO`. | Relentless Endurance (Orc) asks "drop to 1 HP instead?" as its owner drops to 0; Dark One's Blessing's temp HP are given at once; both inside the damage's undo step |
| 6.7 | The rest as content needs them: `FAILS_SAVE` (Indomitable), `ROLLS_INITIATIVE` (regaining uses), `CASTS_SPELL` / `USES` (chained rows), `after=` on spells' later steps (Ice Knife, Green-Flame Blade, Booming Blade). Position events stay manual. | Per source, with a test from its rules text |
| 6.8 | Tooling and content: the `combat-effects` skill's rubric gets a Triggers section (which mode, which gate, when a `when`); `combat_effects.py coverage` counts rows with triggers and lists features whose text has a `("Trigger", ...)` fact but whose rows don't; then the parties, through `feature-combat-effects`. | Curse of the Lich's party features with a Trigger fact all have a trigger or a stated reason not to |

6.1-6.4 are the engine Decision 9 waits for. 6.3 is the vertical slice to
build first. It's what the user asked for, and it touches every hit path
once.

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

- **R48. Triggers are modifiers** (3.5, 2026-11-10): `AtTurnStart` and
  `AtTurnEnd` are in `Model/Content/CombatModifiers.py`, in a badge's
  `CombatCondition.modifiers`, not a `triggers` key of their own. R28 kept
  room for a key; but the modifiers list already goes everywhere a trigger
  must (`to_dict`/`from_dict`, `give_modifiers`, `badge_modifiers`, Cast
  Spell, Enable Feature, the dialog's pick, the record's JSON), and ends
  with its badge (R35), so no log, undo point or expected record changed.
  Every reader of modifiers picks its own types by `isinstance`, so nothing
  that counts a roll sees a trigger. `WhoseTurn` says whose turns: the
  badge's bearer's (`BEARER`) or each creature not on the caster's side
  (`ENEMY`). As JSON: `{"type": "AtTurnEnd", "effect": "Spirit Guardians:
  damage", "whose": "enemy", "when": "it ends its turn in the Emanation"}`.
- **R49. A trigger names a row, not an effect inside it.** `effect` is the
  name of another of its source's combat effects, one with
  `spends_use=False` (Heroism's "Heroism: Temporary Hit Points", Spirit
  Guardians' "Spirit Guardians: damage"). A `CombatEffect` inside a
  condition inside a `CombatEffect` would need its own JSON and checks; a
  row is also what the GM uses by hand (a creature entering the
  Emanation), and it is worked out when used (principle 5):
  `effect_options.trigger_option(caster, source, name)` builds that row for
  the record's caster, from the record's `source` spell or feature. A test
  checks each trigger names a row of its spell that spends nothing.
- **R50. What the simulator does itself, and what it asks.** A trigger's
  row that only gives Hit Points (no save, no attack, no damage, an amount
  known) is given at once, logged as any other ("Edmund gains 2 temp HP
  from Edmund") and noted for the turn ("Heroism: 2 temp HP for Edmund").
  Anything else, and any trigger with a `when`, is a prompt (principle 8):
  a button under the turn's reminders ("Tiger: if it ends its turn in the
  Emanation, Edmund's Spirit Guardians: damage"). Clicking it makes the
  caster the source and the creature the target, and opens the Custom
  Effect dialog with the row picked (`_show_custom_condition_dialog(pick=)`);
  the prompt then goes, and the GM applies or cancels. End triggers come
  after the end-of-turn saves, start triggers after durations tick (an
  effect that ran out gives nothing), both inside `_advance_turn`'s undo
  point. Prompts last the turn, like its notes: an undo clears them.
- **R51. An enemy-turn trigger counts from its caster, once.** Spirit
  Guardians' spell `target` is ENEMY (sheet data, left as it is), so Cast
  Spell puts its badge on the enemies it's aimed at, while the dialog puts
  it on whoever is targeted (the caster, say). `WhoseTurn.ENEMY` asks about
  every creature not on the caster's side, wherever the badge is, and once
  per creature however many have it. Sides: the party is the players,
  party allies and players' summons (`triggers.on_party_side`); a caster
  not in the fight asks nothing.
- **R52. Q19 decided: repeat saves stay `repeat_save`.** They hold what one
  casting set (DC, mode, `also`, Legendary Resistance), PartyAllies,
  Summons and `ending_conditions` read them, and a monster rolls them
  itself; as an `AtTurnEnd` they would need all that in a trigger row and
  change every log for no new behaviour. Revisit if a second kind of
  turn-end save needs it.
- **R53. Hit Points of the modifier alone.** `CombatHitPoints(add_modifier=
  True)` with no dice is the spellcasting modifier alone (Heroism), filled
  in when the caster's is known, else a note to type it in. A spell's later
  step can only upcast by spending a slot in the dialog (DI-078, Q29), so
  Spirit Guardians' damage row says to type the higher dice in.

- **R54. The link is read, not only written** (3.6, 2026-11-10). The
  caster's active spell's `applied` already ended what it put on whom, so
  dropping Bless already took it off every target by every path; 3.6 makes
  the record's `concentration` link a second, sufficient source:
  `_end_concentration_spells` and `_start_concentration` end, after the
  active spells' `applied` rows, every record still linked to the caster
  (`held_by_concentration`, `_end_linked_effects`), not Unconscious at 0
  HP. `applied` stays: it also says which badges a cast put on (so a badge
  already there isn't taken off, `_held_by_effect`), and a non-concentration
  effect's `ends_with_conditions` reads it.
- **R55. A creature leaving the fight ends its concentration first.**
  `_remove_from_fight` (a summon dismissed, vanishing at 0 HP or replaced)
  took the caster and its active spells away but left what they held on
  their targets, linked to a creature no longer there (and a replacing
  summon can take the same name). It now calls `_end_concentration_spells`
  with the reason "X leaves the fight" when the creature is Concentrating
  or anything is linked to it, inside its callers' undo points.
- **R56. A badge two effects hold names the one still running.** Two
  casters' Bless on one target: the link named whichever cast last, so when
  that one dropped the badge rightly stayed (the other's `applied` holds
  it) but the link still named the caster who had stopped.
  `_end_spell_effects` and `_end_linked_effects` now relink such a badge to
  the holder's caster (`_holder_of`, `_relink`), or unlink it when the
  holder needs no Concentration (`unlink_concentration`).
- **R57. One skill, two agents** (4.1/4.2, 2026-11-10). The skill is
  `combat-effects` (`.claude/skills/combat-effects/`, script
  `combat_effects.py`), as Q2 said. The agents are `spell-combat-effects`
  (the old spell-mechanics agent, sonnet: a draft and `compare` check each
  spell) and `feature-combat-effects` (opus: a feature has no draft or text
  reading to compare with, and deciding rows, `[]` or a hook is judgment),
  rather than an agent called `combat-effects` beside a
  `feature-combat-effects`, which would read as if the first covered both.
- **R58. Features are listed party by party, not drafted.** `features
  --campaign X [--member Y]` walks each member's features and their
  extensions (`sheet.extensions_of`, as the picker does) and says what the
  picker makes of each: described, nothing to apply, read from its text, a
  passive one with no row, or an extension without effects (no row), with
  the class's file and line. There's no `draft`/`add` for features: a
  feature's effects are worked out from `character` in Python, which a
  regex reading can't draft. `check` now also builds every party feature's
  effects and hooks, and refuses a `spell=` that isn't a spell.
- **R59. `notes` groups by a note's first words.** Notes are written in
  each source's words, so exact matches would miss most repeats; the first
  four words, lowercased, numbers and dice as `#`, catch "One more target
  per slot level above 1" (Command's five rows, Heroism, Tasha's Hideous
  Laughter: Q34) and nothing else at three sources; `--words` and `--min`
  widen it. It reads every spell class and every party feature (each class
  once), not monster abilities yet.
- **R60. `is_described` everywhere.** `EffectOption.is_curated` and every
  reader, test and picker golden key; the goldens changed by that key
  alone (checked line by line).
- **R61. A feature's free casting is a row, as Paladin's Smite's** (4.3,
  2026-11-11). Fey Touched, Fiendish Legacy and Mapping Magic's
  Illuminated Cartography give one row per spell they let their owner cast
  without a slot (`spell=`, "Without a spell slot, once per Long Rest."),
  so the GM casts it from the picker without spending a slot. Magic
  Initiate (Time Loop PR) still says `[]`, from before; it should follow
  when its party is next looked at. A cantrip's free casting (Fiendish
  Legacy's Chill Touch) gets none. Mapping Magic has `FeatureUses`, so its
  row counts them; the others have none (Q36).
- **R62. A feature's own attack works out its bonus.** The picker fills a
  feature's attack with the spell attack bonus unless the effect sets
  `attack_bonus`, and `CharacterView` has no weapons. So Monk's Martial Arts,
  Flurry of Blows and Deflect Attacks' redirect use a module helper,
  `MonkFeatures.unarmed_strike(character)`: the Martial Arts die and the
  better of Strength and Dexterity (Dexterous Attacks), the same numbers as
  the build's Unarmed Strike row (+6, 1d6 + 4 for Kivi).
- **R63. A pool's rows are its uses.** Monk's Focus returns `[]`: its
  extensions are the ways to spend Focus Points, each with its own rows,
  spending the parent's uses (principle 11). Paladin's Channel Divinity gives
  Divine Sense a notes-only row (a sense, but it spends the pool Sacred
  Weapon draws on) and Abjure Foes one from Paladin level 9; Stonecunning,
  a sense with its own uses, stays `[]` as the rubric says.
- **R64. A badge on its owner, with a `when` for what the GM judges.**
  Dodge (Patient Defense), Steady Aim, Sacred Weapon, Elemental Attunement,
  Large Form and See Invisibility are badges the owner puts on itself
  ("pick yourself as the target"). What they do only some of the time is a
  `when`, so it's a reminder, not counted: Dodge's Disadvantage "if it can
  see the attacker" (as Invisible's, Q16), Sacred Weapon's +CHA "if the
  attack is made with the imbued weapon" (Edmund also throws a Handaxe),
  Steady Aim's Advantage on "its next attack roll this turn", Protection
  from Evil and Good's Disadvantage for the six creature types. Dodge's
  Advantage on Dexterity saves is counted. A duration with "or until ..."
  (Sacred Weapon's, Elemental Attunement's) doesn't read as seconds, so
  their badges set `duration_seconds=10 * 60`.
- **R65. Damage that is the modifier alone is dice "0".** Green-Flame
  Blade's leaping fire is "equal to your spellcasting ability modifier"
  until level 5, then 1d8 + it. `CombatDamage("0", FIRE, cantrip=..., add_modifier=True)`
  says that, and `_with_modifier` writes "0" plus a modifier as the
  modifier alone ("4 Fire", not "0 + 4 Fire"). A spell's weapon attack
  (Booming Blade, Green-Flame Blade) is written as True Strike's: an attack
  row whose note says to give the weapon's own bonus and damage, as the
  spell can't know the weapon.

- **R66. A trigger is its own module, and `after=` is checked per source**
  (6.1, 2026-11-11). `TriggerEvent` and `CombatTrigger` are in
  `Model/Content/CombatTriggers.py`, not `CombatModifiers.py`: a trigger is
  not a modifier of a badge, and `CombatModifiers` keeps `AtTurnStart` /
  `AtTurnEnd` as they were (Q46). `CombatTrigger.__post_init__` refuses
  what no row could mean: `largest_target` on an event with no other
  creature (`BLOODIED`), `needs_damage` other than on `HIT`, `critical_only`
  other than on `HIT` / `HIT_BY`, a non-`ANY` `attacks` on an event that's
  no attack, `after` other than on `HIT` / `MISS` / `USES`, a `USES` without
  `after`, text with spaces around it. An `after` naming no other row can't
  be seen from one row, so `trigger_problems(source, effects)` checks a
  source's rows together (a row's name, or the source's when it has none),
  and `combat_effects.py check` runs it on every spell and party feature.
  As JSON a trigger is its fields not at their default, enums as values
  (`{"event": "hit", "largest_target": "Large", "needs_damage": true}`);
  `from_dict` is strict, a missing key is no trigger, and a log that wrote
  every field (`asdict`) reads too. Every event in the sketch is in the
  enum; only `HIT` and `MISS` fire (MISS came free with the same hooks).
- **R67. `AttackKind` widened, extra damage not.** MELEE, RANGED, UNARMED
  and SPELL are for triggers; `ExtraDamageFrom` / `ExtraDamageOnHit` refuse
  them (`EXTRA_DAMAGE_ATTACKS`), so `hit_plan`'s ANY / WEAPON mean what they
  did and no extra damage is counted for a kind it can't read. A trigger's
  kind is matched by `triggers.kind_fits` (an Unarmed Strike is melee; a
  weapon attack may be melee or ranged, so that asks). The dialog's
  outcome kind is WEAPON from a weapon's row, UNARMED from an Unarmed
  Strike's (`weapon_attack` False), else unknown; the main window's and a
  monster button's are unknown (Q43).
- **R68. `rows_of` is the picker's, passed in** (6.2). `Combat/Effects`
  stays Qt-free, and `effect_options` can't be imported from it (its
  package imports the window), so `outcome_firings(outcomes, rows_of, *,
  is_dead, used_this_turn)` takes the rows as a function, and the window
  passes `effect_options.triggered_rows`: a combatant's own rows with a
  trigger (actions, traits, weapons, own spells, features and extensions,
  never "All spells"), each a `TriggerRow` with its conditions, a line of
  what it does, its uses (left, most) and whether it costs anything. Not
  cached: it takes 2 ms for Kivi, and it's always the combatant's form and
  uses now. `outcome_firings` takes no `chars`: the target's own reactions
  are 6.5. It returns the firings and the "no uses left" lines (Q42) for
  the status line. `EffectOption.trigger` carries the effect's trigger (the
  picker goldens show it only on rows that have one, as `badge_modifiers`).
- **R69. One prompt per Apply, from every hit path** (6.3).
  `_one_trigger_prompt()` collects the outcomes of what runs inside it
  (`_apply_custom_effect`, whose body moved to `_apply_effect_to_targets`,
  and `_apply_custom_effects`, so Times copies share one), and the outermost
  asks once. The main window knows a hit three ways: the Attack roll field
  checked by the same Enter; the Attack roll field's own Enter, remembered
  (`PendingAttack`) while its undo step is still the last one, so an undo
  or anything done in between forgets it; and a monster action button's
  roll, remembered while it's in the Damage field (an undo clears that).
  Damage typed with no attack roll isn't a hit (a spell's, a fall's).
  `_deal_damage` now returns the damage taken, which is the `needs_damage`
  gate. A miss in any path is an outcome too (`MISS`).
- **R70. Applying a firing is the dialog's path, without the dialog.**
  `_apply_row(owner, target, option)` builds the `CustomEffect` that
  `do_apply` would for the row picked and nothing edited
  (`_picked_effect`: damage rolled now, its DC or bonus else the dialog's
  last) and runs `_apply_custom_effect` with the owner as source and the
  target alone as target, inside the hit's undo step. The log reads as a
  pick: "Kivi Jätti uses Giant Ancestry", "Ogre gains Prone from Kivi
  Jätti". What the owner is out of (two targets and one use left) isn't
  asked with `_go_ahead_anyway` in the middle of a hit: that firing isn't
  used, and the status line says so.
- **R71. The setting is one checkbox: off is turn-column buttons** (Q40's
  own suggestion). `ask_triggers` on: the pop-up; off: a button per firing
  under the turn's prompts (`_hit_prompts`, for the rest of the turn),
  which opens the Custom Effect dialog with the row picked (3.5's button
  and `_use_turn_prompt`; both firings have a `pick`). Not the three
  states the brief named (pop-up / button / off): the Settings dialog has
  room for exactly one more checkbox in a 600-high window
  (`test_the_settings_dialog_fits_the_smallest_window`), and none beside
  the Concentration saves, so it's in the first column's section, renamed
  "Initiative and triggers". A true "off" needs a choice setting or a third
  column in `dialogs_mixin.py` (Q48). AUTO firings are applied whatever the
  setting, as they ask nothing.
- **R72. What the pop-up is.** `trigger_prompt.TriggerPrompt`: a checkbox
  per firing, all checked, with its question ("Kivi Jätti hits Ogre
  (Large): use Hill's Tumble? Prone. 2 of 2 uses left."; "Check: Ogre's
  size isn't known." when a gate couldn't be), and Apply, Skip, Edit.
  Edit opens the Custom Effect dialog for each checked one in turn, then
  gives back the GM's source and targets. The window calls it through
  `_ask_triggers`, which tests replace. A declined firing logs "Kivi Jätti
  didn't use Hill's Tumble on Ogre" with `public=False`, in the hit's undo
  step (Q45). Once-per-turn uses are kept by the window per turn
  (`_trigger_uses`), not in the combatant, so an undo doesn't give one
  back (no content uses it yet).
- **R73. Giant Ancestry's three hit benefits carry triggers.** Hill's
  Tumble `HIT, needs_damage, largest_target=LARGE`; Fire's Burn and Frost's
  Chill `HIT, needs_damage`, all optional (ASK, "you can", and they spend a
  use). Their "Right after you hit ..." notes went (principle 7); Frost's
  Chill keeps its Speed note. Stone's Endurance and Storm's Thunder wait
  for 6.5, Cloud's Jaunt has no trigger. A Times copy drops the pick, so
  its outcome names no row: an `after=` rider (6.4) will ask which row hit
  on the 2nd and later copies unless `CustomEffect` keeps the row's name.

- **R74. Riders are read from the text, strictly, in `monster_actions`**
  (6.4, Q47 as suggested). `hit_riders(rider)` reads each sentence of what
  a hit's text says after its damage, and takes one only when it's nothing
  but a condition: "and the target has the X [and Y] condition[s] [until
  the start/end of <whose> next turn]" joined to the damage; "[Once per
  turn, ]If <gates>, it/the target [also] has ..."; "The target has ...";
  each with an optional "(escape DC N)", "from <what holds it>" and ", and
  it has the Y condition until the grapple ends", and a following "While
  Grappled, the target has the Y condition." joins it. The gates are a size
  ("the target is a Large or smaller creature", "is Medium or smaller")
  and/or a `when` (what's left: "the elephant moved 20+ feet straight
  toward it immediately before the hit", "the target isn't an Undead").
  Anything more in the sentence (the allosaurus's extra Bite, the balor's
  pull, the pixie's choice, a 2014 "must succeed on a ... saving throw or
  have", extra damage from a charge) isn't a rider and stays in the text
  (Q49). `MonsterAction.riders` holds them (a frozen `HitRider`), and
  `MonsterAction.rider` loses their sentences, so the turn column's
  "Also:" line and the picker's note don't say them again. 101 riders in
  the catalog: Prone 35 (Large or smaller 21, Medium 7, Huge 7; 4 of them
  with a `when`), Grappled 37 (12 with Restrained, Stunned or Poisoned too),
  Poisoned 16, and 13 of Charmed, Frightened, Paralyzed, Stunned, Blinded,
  Deafened and Incapacitated.
  An ability with combat effects written on it is taken at its word, as
  before: it writes its own rider rows if it wants them.
- **R75. A rider is a row of its own, and the attack row loses its
  condition.** `_rider_options` makes "Tree Club: Prone" right after Tree
  Club: its conditions (the first with the turn duration), its note, and
  `CombatTrigger(HIT, optional=False, after=<the action's name>,
  largest_target=..., once_per_turn=..., when=...)`; its row reads "on a
  hit, Large or smaller" rather than repeating "Prone". It has no
  `monster_action`, so it spends nothing (the attack spent the recharge or
  legendary actions) and its firing has no cost, so it's AUTO when every
  gate was checked. Its sentence is taken out of the text the attack row's
  condition is read from: before, picking Tree Club in the dialog gave
  Prone to a target of any size, and the Damage field's Enter gave none.
  Now all three paths give it, through the trigger. A typed hit (the main
  window's Attack roll field) doesn't say which attack it was, so each of
  the attacker's riders asks "if it was Tree Club" (Q50).
- **R76. A grapple's escape DC is a note, not part of the condition's
  name.** "Grappled (escape DC 13)" would count as Grappled
  (`rules_condition` reads a longer name), but the card's quick menu and
  colours go by the exact name. The rider's note says "Escape DC 13, from
  one of two claws." and `_apply_row` puts a fired row's note on what it
  gives (the badge's tooltip), since no dialog is open to show it; this
  goes for every fired row (Frost's Chill's Speed note too).
- **R77. A Times copy keeps the row it was made with** (R73's open end).
  `CustomEffect.row` is set on the 2nd and later copies, which drop the
  pick, and the dialog's outcome names `pick.name` or else `row`: two Tree
  Clubs with Times 2 give Prone once and ask nothing.

## Open questions (with suggestions)

- **Q2** done in 4.1 (R57, R60).
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
- **Q19** decided in 3.5 (R52): repeat saves stay as they are.
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
  active spell's `applied` row) and spends the Bonus Action. *Not done in
  3.5:* its prompts come with turns, and this one comes with a creature
  dropping to 0; left for its own small step.
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
- **Q29. Remember the slot a spell was cast with** (DI-078). A later step
  (Spirit Guardians' damage, Ice Knife's explosion) starts at the spell's
  own dice, and picking a higher slot in the dialog spends one.
  *Suggestion:* keep the slot on the caster's active spell, and fill a
  `spends_use=False` row's dice at that level, with the slot box left at
  "No spell slot".
- **Q30. `WhenHit` triggers** (Armor of Agathys, Fire Shield: damage to an
  attacker that hits). Not built in 3.5: no described spell needs it yet.
  *Suggestion:* the same shape as `AtTurnEnd`, fired by `_deal_damage` from
  an attack, a prompt when it depends on reach ("within 5 feet").
- **Q31. Many enemies, many prompts.** Spirit Guardians asks about every
  enemy of its caster as its turn ends, as the simulator can't tell who is
  near. *Suggestion:* keep it until the GM finds it noisy; then a
  right-click "Not in Spirit Guardians" on a card that silences it for
  that creature until it's given again.

- **Q32. A hand-given badge a cast also gives** (DI-079): Cast Spell's
  Bless on a target that already has a "Bless" badge typed by hand gives
  that badge Bless's 1d4 and tooltip, but doesn't link it (the cast didn't
  put it on), so it outlives the concentration. *Suggestion:* treat it as
  the cast's (an `applied` row and a link) whenever the cast gives the
  badge modifiers; the hand badge almost always meant this spell.
- **Q33. A monster caster's concentration across encounters.** Loading the
  next encounter drops the monsters without ending what they concentrated
  on, so a player keeps a monster's badge linked to a caster that's gone.
  *Suggestion:* end those through `_end_linked_effects` where the monsters
  are dropped (`encounters_mixin`), once a monster gives a party member a
  concentration badge in play.
- **Q34. Extra targets per slot level** is the one note `notes` finds on
  three spells ("One more target per slot level above 1": Command, Heroism,
  Tasha's Hideous Laughter; Bless and Charm Person say it inside a longer note, which grouping by first words misses).
  *Suggestion:* a `targets: CombatTargets(count, upcast=1)` field, which
  the dialog shows next to the slot box ("Targets: 2 at level 2") and
  warns when more targets are picked; until then it stays a note.
- **Q35. "Pick yourself as the target" is a missing field** (4.3): seven
  features say it mid-sentence (Second Wind, Sacred Weapon, Steady Aim,
  Patient Defense, Elemental Attunement, Uncanny Metabolism, Large Form),
  and False Life and See Invisibility say "pick the caster", which `notes`
  misses as it groups by first words. Several rows also say "nothing
  happens to the targets" (Divine Sense, Step of the Wind, Deflect Attacks,
  Cloud's Jaunt, Tinker's Magic). *Suggestion:* the picker reads the
  source's own `target()` (`FeatureTarget.SELF`, already set on most of
  these) or a `targets_self` field on the effect, and the dialog picks the
  user as the only target; a row with nothing to apply needs no target at
  all. Then drop those sentences.
- **Q36. Free castings aren't counted** (R61). Paladin's Smite (Q8), Fey
  Touched and Fiendish Legacy have no `FeatureUses`, so their "once per Long
  Rest" rows can be used again and again. *Suggestion:* with Q8, a
  `FeatureUses(1, regain_all_on="long rest")` per spell (a sheet change:
  read the snapshot diff), or uses kept by the combat UI per free casting.
- **Q37. "Until the end of the current turn"** has no duration: Sentinel's
  Halt (Speed 0 for the rest of the turn, so Sentinel stays `[]`) and Steady
  Aim's Speed 0. `(TurnEdge.END, TurnOf.TARGET)` given on the target's own
  turn lasts to the end of its next one. *Suggestion:* a third `TurnOf`,
  `CURRENT`, ending as this turn ends.
- **Q38. Weapon Mastery properties** (Topple, Vex, Sap, Push, ...) ride on
  weapon rows, so Weapon Mastery is `[]` for the Fighter, Paladin and Rogue.
  *Suggestion:* a weapon row adds its mastery's effect when its owner has
  it (Topple: a Constitution save or Prone; Vex: Advantage on the next
  attack, a badge), in Phase 5 or when the GM asks.
- **Q39. Reductions to damage being taken** (Deflect Attacks' 1d10 + DEX +
  Monk level, Stone's Endurance's 1d12 + CON) are notes: the GM takes them
  off before applying the hit. *Suggestion:* with `WhenHit` (Q30), a
  reaction prompt as a hit lands on its owner that rolls the reduction and
  takes it off the damage.

Q30, Q38 and Q39 are now part of Phase 6: Q30 and Q39 in step 6.5, and
Q38's masteries as `HIT` / `MISS` triggers on weapon rows (6.7).

Q40-Q45 are **built as suggested** (Decision 12, 6.1-6.3, R66-R73); Q40's
setting is one checkbox, off meaning turn-column buttons (R71, Q48). Q47 is
**built as suggested** in 6.4: riders are read from the text at runtime
(R74).

- **Q40. Pop-up or turn-column button?** The user asked for a pop-up.
  3.5's prompts are buttons, which don't interrupt but are easy to miss.
  *Suggestion:* a modal pop-up for events that happen *during* a roll (a
  hit, damage, a save), since the answer belongs to that moment and to its
  undo step. Buttons stay for turn edges and position. `ask_triggers` can
  switch hit events to buttons for a GM who finds the pop-ups noisy.
- **Q41. How many pop-ups for several hits?** Times 3, Multiattack and
  Flurry of Blows make several hits in a row. *Suggestion:* one pop-up per
  Apply (or per monster button and its Enter), with a checkbox per (target,
  trigger) and no repeats. A trigger that can't fire twice (once per turn,
  or the target is already Prone) is listed once.
- **Q42. A trigger with no uses left.** Hide it, or show it greyed out?
  *Suggestion:* leave it out of the pop-up, and say in the status line
  "Hill's Tumble: no uses left". With every uses-bound trigger spent, there
  is no pop-up. The picker can still use it by hand, with
  `_go_ahead_anyway`.
- **Q43. An attack kind that isn't known.** A typed attack roll or a
  monster button doesn't say whether it was a melee weapon or an Unarmed
  Strike (Stunning Strike needs a Monk weapon or an Unarmed Strike).
  *Suggestion:* as `hit_plan` does: unknown never counts as AUTO. It
  asks, with "if it was a Monk weapon or an Unarmed Strike" in the
  pop-up. The dialog's weapon rows know the kind and pass it in.
- **Q44. Standing triggers: a field on the row, or a feature method?**
  *Suggestion:* `CombatEffect.trigger`. The row is already what a trigger
  applies (R49), already goes through `to_dict` and the picker, and a
  monster's ability gets it the same way. A separate
  `Feature.combat_triggers()` would need a second list and a second
  validator (design goal 2).
- **Q45. Log a declined prompt?** *Suggestion:* a GM-only line ("Kivi
  didn't use Hill's Tumble on Ogre"), so a replayed fight shows it was
  offered, but no state change and no undo point of its own.
- **Q46. Rewrite `AtTurnStart` / `AtTurnEnd` as `CombatTrigger` events?**
  *Suggestion:* no, as R52 kept repeat saves. They work, logs hold them, and
  rewriting them adds no behaviour. `TriggerEvent` leaves out turn edges
  until a row (not a badge) needs one ("A Frightened creature starts its
  turn within 60 feet", which is REMIND anyway).
- **Q47. Generated monsters' riders: read at runtime, or generated?**
  `monsters.py` can't be hand-edited, so Tree Club's rider can't be
  written as a `combat_effects` row there. *Suggestion:* read it from the
  text in `monster_actions.py` (6.4), which also covers fight logs saved
  before. Teach `generate_monsters.py` to emit structured rows only if the
  reading proves fragile.
- **Q48. A true "off" for what hits trigger?** `ask_triggers` is one
  checkbox (R71): on asks in a pop-up, off leaves turn-column buttons. The
  Settings dialog only has checkboxes, and no room for a second one in a
  600-high window. *Suggestion:* if buttons turn out noisy too, let
  `SettingInfo` offer choices (a combo box) in `dialogs_mixin.py`, and make
  `ask_triggers` "pop-up / buttons / off"; until then, off-as-buttons loses
  nothing (a button can be ignored).

- **Q49. Riders that say more than a condition.** About 15 charge riders
  ("If the target is a Large or smaller creature and the boar moved 20+
  feet straight toward it immediately before the hit, the target takes an
  extra 3 (1d6) Piercing damage and has the Prone condition") add damage,
  and a few move the target (the balor's pull) or give another attack (the
  allosaurus). They stay text, as they were. *Suggestion:* read the extra
  damage into the rider row too (an ASK row, as it has a `when`), once a
  fired row's damage is doubled on a Critical Hit like the hit's own
  (`AttackOutcome.critical` is there to pass on); the moves and attacks
  stay the GM's.
- **Q50. A typed hit asks about every rider of the attacker.** A Hill Giant
  hit typed into the main window asks "Tree Club: Prone? ... if it was Tree
  Club" and "Trash Lob: Poisoned? ... if it was Trash Lob", since nothing
  says which attack it was. *Suggestion:* keep it while the GM mostly uses
  the action buttons (which know). If it turns out noisy, put the
  attacker's riders in the pop-up as one choice ("Which attack hit? Tree
  Club / Trash Lob / neither").

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
- **DI-078** (open, found in 3.5): the dialog's slot box is both cost and
  upcast level, so a later step of a casting (`spends_use=False`) can only
  upcast by spending a slot; nothing remembers the slot a spell was cast
  with (Q29).
- **DI-079** (open, found in 3.6): a badge typed by hand and then given by
  Cast Spell gets the spell's modifiers without a concentration link, so
  Bless's 1d4 outlives the concentration on it (Q32).
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

Per step, run only the files listed here for that step, not the whole suite
and not the character-creation tests (see **Keep the overhead low** at the
top). The full suite runs later, when the user asks.

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
  `tests/test_active_effects.py`. 3.5: `tests/test_turn_triggers.py` (the
  JSON form and its strict errors; Heroism's and Spirit Guardians' badges
  and the rows they name; `firings` for a bearer's turn, an enemy's, an
  ally's, the caster's, a summon's, a badge on two enemies, a badge off, a
  caster gone; in the window Heroism's temp HP on its target's turns only,
  not stacking, from another's caster, undone, ended by hand and by
  Concentration; Spirit Guardians' prompts and buttons, nothing rolled by
  itself, a prompt opening the dialog picked and spending no slot, its
  Wisdom save, a creature gone or dead).
- **Phase 6:** `tests/test_hit_triggers.py` (new). The JSON form and its
  strict errors. `outcome_firings`' gates and modes, with expected values
  from the rules text (Hill's Tumble, Tree Club, Shield). In the window,
  each of the three hit paths fires once; Apply and Skip; one undo for
  the hit and what it triggered; one pop-up per Apply; `ask_triggers`
  off. Plus `test_turn_triggers.py`, to show 3.5's triggers didn't change,
  and the picker goldens' diff read before `UPDATE_SNAPSHOTS=1`.

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
