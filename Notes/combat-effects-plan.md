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

## Status (2026-11-11, Phase 3 done, Phase 4's tooling (4.1, 4.2, 4.4) done, and 4.3's first party done: lasting effects are one list, the rules conditions are data, effects carry modifiers the simulator counts, hits deal the extra damage effects give, badges act as turns start and end, a concentration ends everything linked to it, and every spell and feature of the Curse of the Lich party is described; Phase 8 done: every roll can be made at the table)

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
| 3 | Lasting effects (3.1-3.6) | 3.1 **done** (R28-R34): `char["active_effects"]`, one plain dict per badge, in the new Qt-free `Combat/Effects/active_effects.py`; the seven old keys are read only by its `upgrade_old_keys`, where a log is read; an old fight log replays the same (`tests/test_active_effects.py`). 3.2 **done** (R27), ahead of 3.1: the rules conditions are data, and saves, attack rolls (all three paths), AC, damage Resistance and condition immunity read them. 3.3 **done** (R35-R40): a badge's `CombatCondition` says its `modifiers`, the record keeps them as JSON, and `modifiers_on` reads them beside the conditions and cover; Bless's 1d4 is rolled into the saves (a monster's Concentration save too, R40) and attack rolls the simulator makes, Shield of Faith's +2 counts in AC, cover's +2/+5 in Dexterity saves (DI-066); a typed total stays as typed, with the bonus as a reminder in the dialog. 3.4 **done** (R41-R47): `ExtraDamageFrom` (on the target, from its effect's caster) and `ExtraDamageOnHit` (on the attacker); Hunter's Mark's 1d6 Force on its caster's hits and Divine Favor's 1d4 Radiant on its caster's weapon hits are rolled into the hits the dialog and a monster's action buttons deal, doubled on a Critical Hit, each type resisted on its own; a typed damage total stays as typed, with the extra as a reminder in the dialog. 3.5 **done** (R48-R53): `AtTurnStart` / `AtTurnEnd` are modifiers on a badge that name a row of their spell; Heroism's Temporary Hit Points are given as its target's turn starts, and Spirit Guardians asks, as each enemy of its caster ends its turn, with a button that opens the Custom Effect dialog with its damage row picked. 3.6 **done** (R54-R56): ending a concentration also ends every record linked to it (`held_by_concentration`), a creature leaving the fight ends its concentration first, and a badge another running effect still holds is relinked to that effect's caster. Added after (Decision 17, R125, 2026-11-11): a picked spell that gives a rules condition gives a badge of its own name beside it ("Charmed" and "Friends"), with its card, and taking either off takes the other off; a picked feature too (R126: "Turn Undead" beside Frightened and Incapacitated, "Hill's Tumble" beside Prone), not a weapon or a monster's action |
| 4 | One `combat-effects` skill; feature agent; content rollout | 4.1 **done** (R57-R60): the `combat-effects` skill and `combat_effects.py` (renamed from spell-mechanics), with the principles, a Features section, `features`, `coverage` and `notes`, and features in `check`; `is_curated` is `is_described`. 4.2 **done**: the `feature-combat-effects` agent (opus); the spell agent is `spell-combat-effects`. 4.4 **done**: `coverage`. 4.3 (content): **Curse of the Lich done** (R61-R65, 2026-11-11): spells 44/44, features 23 described, 37 nothing to apply, none read from text; Time Loop PR was already done. Next: spells level by level and features class by class, which wait for the user's go (Decision 9) |
| 5 | Sheet chips, monster score | Not started |
| 6 | **Triggers** (new concept, 2026-11-11; see its section): a row or badge says *when* it's used (a hit, damage taken, dropping to 0, ...), and the simulator applies it itself (AUTO) or asks with a pop-up as it happens (ASK) | 6.1-6.3 **done** (R66-R73, 2026-11-11): `CombatTrigger` on a row (`CombatEffect.trigger`, `Model/Content/CombatTriggers.py`), `outcome_firings` with its gates and modes, and the hit hooks in all three hit paths: when Kivi hits a Large or smaller creature and deals it damage, one pop-up per Apply asks about Hill's Tumble; Apply gives Prone, spends a Giant Ancestry use and logs it, inside the hit's undo step. Only `HIT` and `MISS` fire; the other events are data. 6.4 **done** (R74-R77, 2026-11-11): a monster's hit that gives a condition in a sentence of its own ("If the target is a Large or smaller creature, it has the Prone condition", "..., and the target has the Poisoned condition until the end of its next turn", "the Grappled condition (escape DC 13)") is read as a rider row of its own ("Tree Club: Prone") with an AUTO `after=` trigger: the Hill Giant's Tree Club knocks a Large target Prone from its button and Enter and from the dialog, asks when the size isn't known, and does nothing to a Huge target or on a miss. 101 riders in the catalog. 6.5 **done** (R108-R114, 2026-11-11): as an attack roll hits, the creature hit is asked about its `HIT_BY` rows before the damage (Shield's +5 turns Clover's 20 against AC 18 into a miss and spends her Reaction and a slot; Kivi's Deflect Attacks takes its 1d10 + 8 off, `CombatEffect.damage_reduction`), and damage from a creature asks the one damaged about its `TAKES_DAMAGE` rows (Hellish Rebuke, newly described; Storm's Thunder); a Reaction used this round or an Incapacitated owner asks no more. Not built: a badge's `OnTrigger` (Armor of Agathys, Fire Shield; Q57). 6.6 **done** (R127-R131, 2026-11-12): as damage would drop a creature to 0 Hit Points, it's asked first about its `DROPS_TO_ZERO` rows (Ymira's Relentless Endurance: Apply leaves her at 1, not Unconscious, a use spent, in the hit's undo step; not when killed outright), `CombatEffect.drops_to`; a creature that reduces an enemy to 0 gets its `REDUCES_TO_ZERO` rows (Dark One's Blessing's 6 Temporary Hit Points, given at once; the trigger's new `enemy_only` gate); Relentless Rage described too; damage that leaves a creature Bloodied asks about its `BLOODIED` rows (Harvest Undead, R131). 6.7 **done** for the content the parties and examples have (R132-R139, 2026-11-12): as the fight starts, `ROLLS_INITIATIVE` rows are given or asked once (Kivi's Uncanny Metabolism gives back his Focus Points, `CombatEffect.regains`; Superior Inspiration, Perfect Focus, Evergreen Wild Shape, Ever-Ready Shot, Persistent Rage); a failed save the dialog rolls asks about `FAILS_SAVE` rows (Indomitable's reroll +Fighter level, `reroll_save`, with a box for the roll made at the table); `USES` and `CombatTrigger.aim` give spells their later steps (Ice Knife's explosion on its target and the creatures added; Green-Flame Blade's fire on the creature picked). Not built: Weapon Mastery (Q38, now its own step 6.9), `CASTS_SPELL` (no source in the parties), Diamond Soul (Q64). 6.8 **done** (R140-R142, 2026-11-12): the skill's Triggers section (event, mode, gates, `when`, and when to leave one untriggered), `combat_effects.py triggers` and the trigger counts in `coverage`, `Feature.untriggered`; both parties' features with a Trigger fact are triggered (Deflect Attacks, Uncanny Metabolism, Hill's Tumble) or say why not (8), and a test keeps it so. 6.9 **done** (R143-R148, 2026-11-12): each mastery property a wielder has is a row after its weapon's ("Longsword: Sap", `Model/Content/WeaponMasteryEffects.py`), fired only after the weapon picked in the dialog: Sap and Vex are AUTO badges that count for one attack roll (the new `once` and `by_caster` modifier fields; Guiding Bolt and Vicious Mockery written with them too), Slow a Speed -10 badge, Topple a DC 8 + modifier + PB Constitution save or Prone, Graze the modifier's damage on a miss, Push a reminder for a Large or smaller target, Cleave an attack roll on another creature once per turn; Nick a note on the weapon's row. Phase 6 is done but for Q57, Q63-Q65 |
| 7 | **Stat changes while an effect is on** (new, 2026-11-11; see its section): AC formulas and floors, Immunity and Vulnerability beside the built Resistance, Speed, size, Hit Point maximum, worked out from the stored stat plus the badges, and shown on the card with their sources | 7.1-7.2 **done** (R78-R83, 2026-11-11): `ArmorClassBase` (Mage Armor) and `ArmorClassMinimum` (Barkskin) beside `ArmorClass`, worked out by `armor_class(char, stored)`, which every attack path reads through `armor_bonus`; the same effect twice adds once; `DamageImmunity` and `Vulnerability` beside `Resistance` in `_damage_type_modifier`; Mage Armor, Barkskin, Stoneskin, Protection from Energy (a row per type) and Rage described (`tests/test_stat_changes.py`). 7.4 **done** (R84-R89, 2026-11-11): `HitPointMaximum(amount, upcast)`, rolled as the badge is given; `hit_point_maximum(char)` is the stored `max_hp` plus the badges, read by every cap, bar and Bloodied check; giving it raises current HP as Hit Points regained, ending it caps current HP (`Action.LOSE_HIT_POINTS`, replayed); Aid and Heroes' Feast described. 7.5 **done** (R90-R93, 2026-11-11): the card's and More Info's AC is the AC in use with what changes it ("AC: 17 (15; Shield of Faith +2)", cover too), a "Max HP 35 (30; Aid +5)" line, and the defenses the conditions and badges give with where from ("Resist: ...; Bludgeoning, Piercing, Slashing (Rage)", "Cond. Immune: Frightened (Heroism)"); the player view's full rows show the AC in use. 7.3 **done** (R94-R98, 2026-11-11): `Speed(bonus, multiplier, set_to)` and `Size(steps, becomes)`, worked out by `speed_in_use` and `size_in_use`; the trigger size gates read the size in use (an Enlarged Large Ogre is Huge to Hill's Tumble); the card shows "Speed: 80 ft. (40 ft.; Haste ×2)" and, when changed, "Size Huge (Large; Enlarge/Reduce +1)"; Haste (and its lethargy row), Longstrider, Enlarge/Reduce and Large Form described. 7.6 **done** (R106, R107, 2026-11-11): the rubric's Stat changes table, `combat_effects.py stats` (each note naming AC, a defense, Speed, the Hit Point maximum or size, marked counted or NOTE ONLY), and both parties' rows: Shield's `ArmorClass(5)`, Absorb Elements' `Resistance` (a row per type), Silence's Thunder `DamageImmunity`, Shield of Faith's restating note gone. **Phase 7 done** |
| 8 | **Rolled at the table** (new, 2026-11-11, Decision 15; see its section): whatever the simulator rolls, the GM can give it a number rolled at the table instead | **Done** (R115-R124, 2026-11-11). 8.1-8.3: a hit's extra damage (Hunter's Mark, Divine Favor) has a box per target in the Custom Effect dialog, added as typed, even to a typed damage total, Critical Hit or not; Deflect Attacks' and Stone's Endurance's reduction has a box in the trigger pop-up; the setting "Roll monsters' recharges and repeat saves" (`monsters_roll_turn_dice`) off turns those into turn reminders. 8.4-8.7 (Decision 16): a card's Set initiative... (a summon's roll, or anyone's); a box takes one roll per Times copy ("nat 1, nat 20"); a Hit Point maximum box for a pick whose badge rolls one (Heroes' Feast), and a player's dice Hit Points at a turn's start left to a turn-column button; `tests/test_roll_sites.py` fails on a new place that rolls until it's listed with its way to the table (`tests/test_table_rolls.py`) |

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

**6.9 (2026-11-12).** Weapon Mastery rows for every wielder with the
mastery (the parties: Edmund's Longsword Sap and Handaxe Vex, Thum's
Shortsword and Halfling's Trick Vex, Hanna's Longbow Slow and Shortsword
Vex, Obmar's Sulvesburg's Folly Push; Nick on Obmar's Dagger and Light
Hammer and Thum's Scimitar as a note). Guiding Bolt's and Vicious
Mockery's "next attack roll" notes are badges now (`once`).

**6.7 (2026-11-12).** As the fight starts (`ROLLS_INITIATIVE`,
`regains`): Uncanny Metabolism (its note gone), Perfect Focus, Superior
Inspiration, Archdruid (Evergreen Wild Shape, and Nature Magician as a
note), Ever-Ready Shot, Persistent Rage. On a failed save: Indomitable
(`reroll_save`). Later steps: Ice Knife's explosion (`USES`,
`ALSO_OTHERS`) and Green-Flame Blade's leaping fire (`HIT`, `ANOTHER`).

**6.6 (2026-11-12).** With Hit Point triggers: Relentless Endurance
(Orc; `DROPS_TO_ZERO`, `drops_to=1`), Relentless Rage (Barbarian 11;
`drops_to` twice the level, its save a `when`) and Dark One's Blessing
(Fiend Warlock 3; `REDUCES_TO_ZERO`, `enemy_only`, Charisma modifier +
Warlock level Temporary Hit Points, at least 1) and Harvest Undead
(Necromancer 10; `BLOODIED`, healing the Wizard level, a Reaction).

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

**7.1-7.2 (2026-11-11).** With stat changes on their badge: Mage Armor
(`ArmorClassBase(13, DEX)`), Barkskin (`ArmorClassMinimum(17)`), Stoneskin
(`Resistance` to Bludgeoning, Piercing and Slashing), Protection from
Energy (a row per type: Acid, Cold, Fire, Lightning, Thunder) and the
Barbarian's Rage (Resistance, Strength Advantage, its damage as a note):
79 spells have combat effects (`combat_effects.py check`).

**7.4 (2026-11-11).** Aid (`HitPointMaximum("5", upcast="5")`, "up to
three creatures") and Heroes' Feast (24 hours: Resistance to Poison,
immunity to Frightened and Poisoned, `HitPointMaximum("2d10")`): 81
spells have combat effects.

**7.3 (2026-11-11).** Haste (`Speed(multiplier=2)`, `ArmorClass(2)`,
Advantage on Dexterity saves, its extra action as a note, and a "Haste:
lethargy" row), Enlarge/Reduce (a row each: Enlarge `Size(steps=1)` with
Strength Advantage, Reduce `Size(steps=-1)` with a Constitution save and
Strength Disadvantage; the 1d4 as a note), Longstrider (`Speed(bonus=10)`,
its Speed note gone) and Large Form (`Size(becomes=LARGE)`,
`Speed(bonus=10)`): 83 spells have combat effects.

**7.6 (2026-11-11).** The parties' rows with a stat in a note: Shield
(`ArmorClass(5)` on its caster until the start of its next turn; the
triggering attack and Magic Missile stay notes), Absorb Elements (a row per
type, `Resistance` on its caster until the start of its next turn; the
melee hit's 1d6 stays a note), Silence (a "Silence" badge with
`DamageImmunity` to Thunder beside Deafened) and Shield of Faith (its note
only said the +2 again, gone). Sleep's "immune to Exhaustion" and Patient
Defense's "Speed is 0" read a stat as a gate and stay notes. Spirit
Guardians' halved Speed (an area, in no party) stays a note.

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

**Verified 2026-11-12 (6.9, R143-R148), low overhead:** every combat test
file, the spell-class, skill-script and new `tests/test_weapon_mastery.py`
files pass (3,775; not the full suite); `combat_effects.py check` OK;
pyright 0 errors on every changed file. 17 new tests, with expected values
from the mastery text and Edmund's sheet (Strength +4, PB 2: Topple DC 14,
Graze 4 Slashing, Cleave +6 for 1d12): the rows as data, `once` and
`by_caster` round-tripped and refused where they mean nothing, and in the
window Sap given with no pop-up on a Longsword hit, counted as the Ogre's
Greatclub button rolls, used up and given back by one undo; no Sap on a
miss; Vex only for Thum's next roll; Slow -10 feet once for two hits; Push
asked for an Ogre, not a Hill Giant; Topple's Prone on a failed save;
Graze on a miss; Cleave on the other Ogre, once a turn. Eight picker
goldens changed, each line read: the mastery rows (Edmund, Thum, Hanna,
Obmar), the Nick note on three weapons, and Guiding Bolt's and Vicious
Mockery's notes become their once-badges (Clover, Gabriel, Obmar, Thomas,
the spells' golden). One sheet snapshot changed, read with `snapshot_diff`:
Thum's Halfling's Trick shows "Mastery: Vex ✓" (DI-080). One older test
(`test_a_mark_from_before_extra_damage_adds_nothing`) hung on an unanswered
pop-up until masteries followed only the weapon picked (R144).

**Verified 2026-11-12 (6.8, R140-R142), low overhead:** `combat_effects.py
triggers` exits 0 for both parties and `coverage` reads "Trigger facts 3
triggered, 4 left to the GM, 0 to do" (Curse of the Lich) and "0
triggered, 4 left to the GM, 0 to do" (Time Loop PR); `check` OK; the
feature, picker-row, hit and initiative trigger tests (211), the skill
script tests (27, with the new party trigger test) and the `.claude`
config tests (82, the agent index rebuilt for the skill's new description)
pass; pyright 0 errors on the changed tool, `Feature.py` and the test. No
golden changed: `untriggered` isn't shown in the picker.

**Verified 2026-11-12 (6.7, R132-R139), low overhead:** every combat test
file (as for 6.6, with the three new ones: 2,502) passes;
`combat_effects.py check` OK; pyright 0 errors on every changed file but
one older error in `tests/test_roll_sites.py:138` (the AST visitor's type,
not touched here). 40 new tests in `tests/test_initiative_triggers.py`,
`tests/test_spell_step_triggers.py` and `tests/test_failed_save_triggers.py`,
with expected values from Uncanny Metabolism's, Perfect Focus's, Superior
Inspiration's, Evergreen Wild Shape's, Ever-Ready Shot's, Persistent Rage's,
Indomitable's, Ice Knife's and Green-Flame Blade's text. Three picker
goldens changed, each line read: Kivi's Uncanny Metabolism gained its
`rolls initiative` trigger and lost "reset them by hand"; Green-Flame
Blade's leaping fire (Clover, the spells' golden) gained its `hit`,
`after`, `aim: another` trigger and lost "After a hit:"; Ice Knife's
explosion gained its `uses` trigger and the shard lost "pick Ice Knife:
explosion next". One older test (`test_kivis_rows_with_a_trigger`) counted
Kivi's triggered rows; it reads them by name now.

**Verified 2026-11-12 (6.6, R127-R131), low overhead:** every combat test
file (`tests/test_combat*.py`, the trigger, hit-by, picker-row, stat-change,
extra damage, active effect, concentration, modifier, table-roll, roll-site
and spell, feature and monster combat-effects files: 2,462 with the new
ones; not the full suite) passes; `combat_effects.py check` OK; pyright 0
errors on every changed source file and `tests/test_hit_point_triggers.py`.
30 new tests there, with expected values from Relentless Endurance's, Dark
One's Blessing's, Relentless Rage's and Harvest Undead's text and the
rules' Instant Death:
the model fields and gates, the questions and buttons, and in the window a
typed hit that would drop Ymira (Apply: 1 HP, no Unconscious, the use
spent, the damage line's `knockout` false; Skip: 0 HP and Unconscious; one
undo), a second drop with no use left, damage that leaves her standing,
temporary Hit Points and Resistance counted first, a hit of two types asked
once, the setting off (a button, and the late pick bringing her back to 1),
and Wrenna's knockout of the Ogre giving 6 Temporary Hit Points (and one
undo taking them back), a hit that doesn't, and none for an ally; and
Mordecai's Harvest Undead asked once as damage leaves him Bloodied
(healing 20, his Reaction spent), not again while he stays Bloodied, nor
as he drops to 0. No picker golden changed: no party member has these
features at its level.

**Verified 2026-11-11 (6.5, R108-R114), low overhead:** every combat test
file (`tests/test_combat*.py`, the trigger, picker-row, stat-change, extra
damage, active effect, concentration, modifier and spell, feature and
monster combat-effects files: 2,494 with the new ones; not the full suite)
passes; `combat_effects.py check` OK (85 of 594 spells); pyright 0 errors on
every changed source file and `tests/test_hit_by_triggers.py`. 36 new tests
there, with expected values from Shield's, Deflect Attacks', Stone's
Endurance's and Hellish Rebuke's text and the glossary's Reaction: the
model field, the gates (a miss, a used Reaction, Stunned, Shield already
on, the attacker's own rows), the questions, and in the window a typed hit,
an attack roll then its damage, a monster button and Enter, the dialog, a
second hit the same round, Skip, one undo, the setting off, Deflect Attacks
taking 9 and taking it all, and Hellish Rebuke after a hit and after damage
with no attack roll. Four picker goldens changed, each line read: Shield's
rows (Clover, Dessie, the spells' golden) gained `{"event": "hit by"}` and
a note for a Shield picked by hand; Kivi's Deflect Attacks gained its
trigger (with the B/P/S `when`) and `damage_reduction` "1d10 + 8" (DEX 4 +
Monk 4) and lost the note that said it; the spells' golden gained Hellish
Rebuke (DC 15 DEX, 2d10 Fire, half, upcast 1d10, a Reaction). One older test
read Kivi's only triggered row; he has two now.

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

13. **Thirty open questions as suggested** (the user, 2026-11-11: "resolve
    30 of the easier questions, choosing your suggestion"). Each says when
    it's built. **Built 2026-11-11** (R99-R105): Q7, Q8, Q13, Q23, Q27, Q34,
    Q35, Q37; the rest are answered by the decision alone or wait for what
    they name. The seven left open here were decided next (Decision 14).
    - **Q4.** A cast spell's notes all come along (Jolt to Life shows Spare
      the Dying's range). Revisit only if a row gets noisy.
    - **Q5.** Hook notes keep following the sheet's feature order. Add a
      shuffled-order test once a second hook on the same source exists.
    - **Q6.** Agonizing Blast, Empowered Evocation, Potent Cantrip and Potent
      Spellcasting become `adjust_combat_effect` hooks when a party has
      them, not before.
    - **Q7.** **Built** (R99). An `ends_conditions: tuple[str, ...]` field on `CombatEffect`,
      which the dialog applies as "take these off each target" (one
      `_remove_condition_from` per target). It gets a small step of its own
      and follows the field checklist. Lay on Hands' Poisoned, Lesser
      Restoration, Remove Curse and Calm Emotions then drop their notes.
    - **Q8.** **Built** (R100). Paladin's Smite gets `FeatureUses(1, regain_all_on="long
      rest")`, so the picker counts its free casting. This adds a use box to
      its sheet card: read the snapshot diff before regenerating. (Q36,
      Decision 14, does the same for the other free castings.)
    - **Q9.** Times still splits across targets by applying again. A
      per-target count comes only if the GM asks.
    - **Q10.** Repeated saves (Times with a saving throw) wait until a
      described effect uses one. Then it gets a test.
    - **Q13.** **Built** before this (da650afe): `is_command_line_tool`. The converter stays beside `SpellGenerator.py`, and
      `review-house-rules`' debug-print check learns that a module with a
      `__main__` block may print.
    - **Q18.** The badge shows no `source` or `caster`, since the log already
      says it. Revisit if the GM asks.
    - **Q21.** In Phase 4's tooling, the picker writes out a badge's
      modifiers as a generated note (like R14's `when`), the rubric gets a
      `modifiers` line, and Bless's hand-written sentence goes (one picker
      golden change per Bless row).
    - **Q22.** A badge typed by hand in the Custom Condition dialog gets no
      modifiers. Revisit if the GM asks.
    - **Q23.** **Built** (R101; DI-069 fixed). The encounter log's encoder uses `to_dict()` for a monster
      ability's `combat_effects` (DI-069). Fix it before the first monster
      ability gives a badge with modifiers.
    - **Q24.** Moving a mark (Hunter's Mark, Hex). When a target carrying a
      living caster's mark drops to 0 HP, a reminder says "Hanna can move
      Hunter's Mark (a Bonus Action)". A card's right-click "Move Hunter's
      Mark here" moves the record (caster, modifiers, concentration link and
      the active spell's `applied` row) and spends the Bonus Action. Its own
      small step, alongside 6.6's `DROPS_TO_ZERO`.
    - **Q25.** Hex is a variant row per ability (R15). Each "Hex" badge has
      `ExtraDamageFrom("1d6", NECROTIC)` and `D20Mode((ABILITY_CHECK,),
      DISADVANTAGE, (ability,))`; the second part is only a reminder until
      the simulator rolls ability checks. A Hex moved to a new target keeps
      its variant.
    - **Q26.** Rage's damage is `ExtraDamageOnHit` with `damage_type=None`
      (meaning the type of the hit's first part) and `AttackKind.STRENGTH`,
      which a weapon pick can tell from the weapon's ability. A Finesse
      weapon is the GM's call, through a `when`. Built with the Barbarian's
      features.
    - **Q27.** **Built** (R102). After an attack roll typed into the main window hits, the
      status line adds "+1d6 Force (Pirate's Hunter's Mark)", as the
      dialog's target rows do.
    - **Q28.** The extra damage's log line stays GM-only. If players ask,
      `public_log.py` reads it as part of the hit (kind "hit-extra").
    - **Q29.** The caster's active spell remembers the slot it was cast with
      (DI-078). A `spends_use=False` row fills its dice at that level, with
      the slot box left at "No spell slot".
    - **Q31.** Spirit Guardians keeps asking about every enemy of its
      caster. A right-click "Not in Spirit Guardians" comes only if the GM
      finds it noisy.
    - **Q32.** A cast that gives modifiers to a hand-typed badge of the same
      name takes that badge over: an `applied` row and a concentration link
      (DI-079).
    - **Q33.** Monsters dropped when the next encounter loads end their
      concentration through `_end_linked_effects` (in `encounters_mixin`).
      Built once a monster gives a party member a concentration badge in
      play.
    - **Q34.** **Built** (R103). A `targets: CombatTargets(count, upcast=1)` field (Command,
      Heroism, Tasha's Hideous Laughter, Bless, Charm Person). The dialog
      shows "Targets: 2 at level 2" next to the slot box and warns when more
      targets are picked. Until it's built, the count stays a note.
    - **Q35.** **Built** (R104). "Pick yourself as the target": the picker reads the source's
      own `target()` (`FeatureTarget.SELF`) or a `targets_self` field on the
      effect, and the dialog picks the user as the only target. A row with
      nothing to apply needs no target at all. The "pick yourself" and
      "nothing happens to the targets" sentences then go.
    - **Q37.** **Built** (R105). A third `TurnOf`, `CURRENT`, which ends when the current turn
      ends (Sentinel's Halt, Steady Aim's Speed 0).
    - **Q46.** `AtTurnStart` / `AtTurnEnd` stay as they are and are not
      rewritten as `CombatTrigger` events.
    - **Q48.** `ask_triggers` stays one checkbox. A "pop-up / buttons / off"
      combo box (`SettingInfo` choices) comes only if the buttons turn out
      noisy too.
    - **Q49.** A rider's extra damage is read into the rider row (an ASK
      row, since it has a `when`), once a fired row's damage is doubled on a
      Critical Hit (passing on `AttackOutcome.critical`). Moves and extra
      attacks stay the GM's.
    - **Q50.** A typed hit keeps asking about every rider of the attacker. A
      "Which attack hit?" choice in the pop-up comes only if it turns out
      noisy.
    - **Q53.** Hit Point maximum reductions from a monster's hit (a Wight's
      Life Drain): a Phase 6 rider row gives a badge with
      `HitPointMaximum(-amount)`, the amount being
      `AttackOutcome.damage_dealt`. The badge has no timer, and a Long Rest
      takes it off.
    - **Q55.** An `AtEnd(effect)` modifier beside `AtTurnStart` /
      `AtTurnEnd`. It is used as the record ends (by hand, timer or
      Concentration, R54), inside that step's undo, so Haste's badge gives
      its lethargy row itself.

14. **The last open questions as suggested** (the user, 2026-11-11: "fix
    them now", after Decision 13 left seven open). None is built yet. Q11
    needed no decision: S.4 did it as suggested (R24-R26).
    - **Q14.** A `Sourcebook` enum with one member per book. The scrapers
      map every scraped spelling onto it ("Forgotten Realms - Heroes of
      Faerun" and its accented twin, "Player's Handbook 2024" and "... (BR)"),
      and `SpellRules.source` becomes the enum. Done with a re-scrape, not
      in the converter.
    - **Q16.** Invisible's Advantage and Disadvantage count by default, with
      "unless it can see it" as the note the GM overrides with the mode
      buttons. Built together with DI-068, which makes the simulator see the
      Invisible condition at all.
    - **Q30.** `WhenHit` damage to an attacker (Armor of Agathys, Fire
      Shield) is a `TAKES_DAMAGE` trigger on a badge (`OnTrigger`), fired
      by `_deal_damage` from an attack, and a prompt when it depends on
      reach ("within 5 feet"). Step 6.5. *The rows' `TAKES_DAMAGE` is built
      (R112); the badge's `OnTrigger` isn't yet (Q57).*
    - **Q36.** *Not buildable as written; back in Open questions as Q56.*
      Every free casting gets its own use count, as Paladin's Smite
      does (Q8): `FeatureUses(1, regain_all_on="long rest")` per spell of
      Fey Touched and Fiendish Legacy. This changes their sheet cards, so
      read the snapshot diff before regenerating.
    - **Q38.** A weapon row adds its Weapon Mastery property's effect when
      its owner has that mastery, as `HIT` / `MISS` triggers on the row
      (Topple: a Constitution save or Prone; Vex: Advantage on the next
      attack, as a badge). Step 6.7, not Phase 5.
    - **Q39.** Reductions to damage being taken (Deflect Attacks' 1d10 + DEX
      + Monk level, Stone's Endurance's 1d12 + CON) become a reaction prompt
      (`HIT_BY`) as a hit lands on their owner. It rolls the reduction, takes
      it off the damage and spends the Reaction. Step 6.5. *Built (R110).*

15. **Every roll can be made at the table** (the user, 2026-11-11: "I want
    extra damage, just like Hunter's Mark to be 'rollable in real life' as
    well. In fact, Everything that requires some kind of roll cannot be
    purely left to the engine, but should always have the options to roll
    in real life."). Design principle 13 and Phase 8. Decision 4 still
    holds for what's left blank: a total typed at the table gets nothing
    rolled on top of it. A roll with a box of its own (a hit's extra damage)
    is a roll of its own, though, so a number typed in that box is added,
    even to a typed damage total (R117).
16. **Q58-Q61 as suggested** (the user, 2026-11-11: "continue", after 8.1-8.3,
    taken as accepting them, as Decision 12 took "start on 6.1-6.3"). Built
    in 8.4-8.7 (R120-R124): Set initiative... on a card; a roll per Times
    copy in each box; a box for a rolled Hit Point maximum and a button for
    a player's dice Hit Points at a turn's start; a guard test for new
    roll sites.
17. **A spell's badge beside the conditions it gives** (the user,
    2026-11-11: "Sometimes, for example like the 'Friends' spell, it applies
    charmed. However, I still want to read about 'Friends' as conditions.
    ... Of course, if one is deleted so is the other. ... It's more a visual
    aid than anything else."). A picked spell that gives a rules condition
    also gives a badge named after the spell, with its card; the two are
    linked, so taking either off takes the other off. *Built (R125).*
    Features too, as Q62 suggested (the user, 2026-11-11: "do as you see
    most fit"): a class, subclass, species or feat feature picked in the
    dialog, not a weapon or a monster's action. *Built (R126).*

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
13. **Every roll can be made at the table** (Decision 15, Phase 8). The
    simulator rolling is a shortcut, never the only way. Wherever it rolls,
    the GM can give it the number rolled at the table instead: a box by
    the roll in the form or pop-up it happens in (blank rolls it here), or,
    for a roll made with no form open (as a turn starts or ends), a setting
    that turns it into a turn reminder. A number typed in counts as typed:
    it isn't doubled on a Critical Hit, and no gate overrules it. A new
    place that rolls comes with its way to type the roll in, in the same
    change.

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
- **A spell's or feature's own badge** (Decision 17, R125-R126): a picked
  spell or feature that gives a rules condition also gives a badge of its
  name ("Charmed" and "Friends", "Prone" and "Hill's Tumble"), with its
  card, which stands for those conditions (the record's `linked`). Taking
  it off takes them off; taking the last of them off takes it off. A
  weapon's or a monster's action gives none.

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
| `Resistance(types)` / `Immunity` / `Vulnerability` | Rage, Absorb Elements, Protection from Energy (only `Resistance` was built in 3.3; the rest is Phase 7) |
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
| 6.5 | **Done** (R108-R114), but for the badges (`OnTrigger`: Armor of Agathys, Fire Shield; Q57). Being hit: `HIT_BY` before damage (Shield, Deflect Attacks, Stone's Endurance), and `TAKES_DAMAGE` after (Hellish Rebuke, Storm's Thunder). Spends the Reaction (`_add_action_use`). Takes over Q30 and Q39. | Shield asked as a hit lands turns it into a miss when +5 is enough, and spends the Reaction and a slot; Deflect Attacks takes its roll off the damage; a used Reaction asks no more this round |
| 6.6 | **Done** (R127-R131). Hit Point thresholds: `BLOODIED`, `DROPS_TO_ZERO`, `REDUCES_TO_ZERO`. | Relentless Endurance (Orc) asks "drop to 1 HP instead?" as its owner drops to 0; Dark One's Blessing's temp HP are given at once; both inside the damage's undo step |
| 6.7 | **Done** (R132-R139), but for `CASTS_SPELL` (no source needs it yet) and Booming Blade's move (position). The rest as content needs them: `FAILS_SAVE` (Indomitable), `ROLLS_INITIATIVE` (regaining uses), `USES` (chained rows), `after=` on spells' later steps (Ice Knife, Green-Flame Blade). Position events stay manual. | Per source, with a test from its rules text |
| 6.9 | **Done** (R143-R148). Weapon Mastery (Q38, moved out of 6.7): a weapon row adds its mastery's effect as `HIT` / `MISS` triggers when its owner has that mastery (Topple: a Constitution save or Prone; Vex: Advantage on the next attack, a badge; Sap, Slow, Graze, Cleave, Nick, Push). | Each property, from the glossary text, on a party member's weapon |
| 6.8 | **Done** (R140-R142). Tooling and content: the `combat-effects` skill's rubric gets a Triggers section (which mode, which gate, when a `when`); `combat_effects.py coverage` counts rows with triggers and lists features whose text has a `("Trigger", ...)` fact but whose rows don't; then the parties, through `feature-combat-effects`. | Curse of the Lich's party features with a Trigger fact all have a trigger or a stated reason not to |

6.1-6.4 are the engine Decision 9 waits for. 6.3 is the vertical slice to
build first. It's what the user asked for, and it touches every hit path
once.

## Stat changes while an effect is on (Phase 7, new, 2026-11-11)

**Why** (the user, 2026-11-11: "temporary modifications to a character, AC
increase, new resistances, etc. while a feature/spell is active"). Phase 3
built the first of these: `ArmorClass(bonus)` (Shield of Faith's +2, counted
in every attack roll) and `Resistance(types)` (counted in `_damage_target`).
The rest of what a running spell or feature changes on its bearer is still a
note the GM has to remember: Mage Armor's AC, Barkskin's floor of 17, Rage's
Resistances on its owner, Haste's Speed, Enlarge/Reduce's size, Aid's Hit
Point maximum, Protection from Energy's or Stoneskin's Resistance, a
Vulnerability or Immunity a spell gives. And the card still shows the stat
block's numbers (Q20).

### The rule: computed, never written over

A badge never edits `char["ac"]`, `char["speed"]`, `char["size"]` or the
damage lists. The simulator works out the stat it uses from the stored one
plus the modifiers on the creature (`modifiers_on(char)`), as `armor_bonus`
already does for AC. So ending a badge (by hand, timer, Concentration, R54),
undo and log replay need nothing new: the stat goes back because the
modifier is gone. The Hit Point maximum is worked out the same way
(`hit_point_maximum`, R84); only current HP is written, as the badge is
given and as it ends (7.4).

### Vocabulary (in `Model/Content/CombatModifiers.py`)

| Modifier | Examples | What the simulator does with it |
|---|---|---|
| `ArmorClass(bonus)` (**built**, 3.3) | Shield of Faith +2, Shield +5, Haste +2 | Added to the AC an attack is compared with |
| `ArmorClassBase(base, abilities)` (**built**, 7.1) | Mage Armor (13 + DEX, for a creature "who isn't wearing armor") | Replaces the stored AC when higher (R79); what the target must be when it's given is the GM's to check (R80) |
| `ArmorClassMinimum(value)` (**built**, 7.1) | Barkskin (2024: "can't be less than 17") | The AC used is at least `value`, after the bonuses |
| `Resistance(types)` (**built**, 3.2/3.3) | Rage (B/P/S on its owner), Stoneskin, Protection from Energy, Absorb Elements | Halves that type in `_damage_target` |
| `DamageImmunity(types)` / `Vulnerability(types)` (**built**, 7.2) | No 2024 spell gives Immunity for a while (Heroes' Feast is Resistance to Poison); for a monster's or a homebrew effect | Zeroes / doubles that type, in the same place as Resistance, in the glossary's order (Resistance, then Vulnerability) |
| `Speed(bonus=0, multiplier=1, set_to=None)` (**built**, 7.3; no `modes`, R94) | Haste ×2, Longstrider +10, Ray of Frost -10, Steady Aim / Halt 0 (Q37) | Shown only: the simulator moves nothing (principle 8). Grappled / Restrained keep their own rules speed of 0 |
| `Size(steps=0, becomes=None)` (**built**, 7.3; R95) | Enlarge/Reduce (one step), Large Form (Large) | The size the Phase 6 gates read (`largest_target`, R68); shown on the card |
| `HitPointMaximum(amount, upcast)` (**built**, 7.4) | Aid (+5, and +5 per slot level above 2), Heroes' Feast (2d10); a monster's "its Hit Point maximum is reduced" rider | Added to the stored `max_hp` while on (R84); current HP moves as it's given and ends (R86, R87) |
| `D20Mode` / `D20Bonus` (**built**) | Enlarge's and Rage's Advantage on Strength checks and saves, Haste's Advantage on DEX saves | As today |
| `ExtraDamageOnHit` (**built**, 3.4) | Enlarge's +1d4 weapon damage, Reduce's -1d4, Rage's damage (Q26) | As today, once `damage_type=None` (the hit's own type) exists |
| `Note(text)` | Haste's extra action, Rage's "can't cast spells", reach changes | Shown on the card, not counted |

**Stacking** follows the glossary's Combining Game Effects: the same
spell's or feature's effects don't add (two Shields of Faith give +2), and
different ones do. Of several `ArmorClassBase`s only the best counts (one
way to work out AC); `ArmorClassMinimum` is taken after every bonus.

**Where the badge comes from** doesn't change: a spell's or feature's row
gives it to its targets (the dialog's pick, Cast Spell), and a self buff
(Rage, Large Form, Patient Defense's Dodge, Sacred Weapon) goes on its
owner, which Q35's `targets_self` makes one click. Always-on traits (an
owner's own Resistances, Unarmored Defense) stay on the sheet and in the
stat block, not here.

### Showing it

The card and the player view show the stat in use with what changes it:
"AC 17 (15 +2 Shield of Faith)", "Speed 60 ft. (30 ×2 Haste)", "Large
(Medium, Enlarge)", "HP 25 / 35 (30 +5 Aid)", and a Resistances line that
says where each came from ("Bludgeoning, Piercing, Slashing: Rage"). This
takes over Q20; cover's +2/+5 shows the same way. The player view hides
what the GM hides today (R27's known-AC notes take the bonus off).

### Steps

| # | Step | Done when |
|---|---|---|
| 7.1 | **Done** (R78-R81). `armor_class(char, stored)`: `ArmorClassBase`, `ArmorClassMinimum` next to the built `ArmorClass`, with the stacking rule; every attack path reads it through `armor_bonus`. Mage Armor and Barkskin described. | Mage Armor on a creature with stat-block AC 12 and DEX +3 makes an attack need 16; Barkskin on AC 13 makes it 17, and with Shield of Faith still 17 (17 is the floor, not a bonus); two Shields of Faith give +2; ending each badge gives the old AC back; an old log replays the same |
| 7.2 | **Done** (R82, R83). `DamageImmunity` / `Vulnerability` beside `Resistance` in `_damage_type_modifier`, in the glossary's order. Rage's Resistances and Stoneskin / Protection from Energy described (Rage as a badge its owner puts on itself). | Rage halves a Slashing hit on its owner and not a Fire one; a Vulnerability doubles; Resistance and Vulnerability to the same type halve, then double (11 Slashing becomes 10); an Immunity from a badge takes it all; ending Rage ends it |
| 7.3 | **Done** (R94-R98). `Speed` and `Size`: shown on the card; `Size` read by the Phase 6 gates. Haste, Longstrider, Enlarge/Reduce, Large Form described. | An Enlarged Medium creature is Large to Hill's Tumble's gate (asks) and a Reduced Large one Medium; Haste shows "Speed 60 ft. (30 ×2 Haste)"; both go when the badge ends |
| 7.4 | **Done** (R84-R89). `HitPointMaximum`: giving it raises `max_hp` and current HP by the same amount (Aid: "a creature's Hit Point maximum and current Hit Points increase"); ending it lowers `max_hp` and caps current HP at it; the Bloodied check (`damage_mixin`) uses the new maximum. All inside the giving step's undo. (Built without writing `max_hp`: R84.) | Aid +5 on a creature at 20/30 gives 25/35; taking Aid off at 33/35 leaves 30/30, at 10/35 leaves 10/30; one undo takes back the cast and the HP; a log replays the same |
| 7.5 | **Done** (R90-R93). The card and player view show the stats in use with their sources (Q20 done). | Shield of Faith's card reads "AC 17 (15 +2 Shield of Faith)"; a Resistances line names Rage; the player view's AC notes unchanged |
| 7.6 | **Done** (R106, R107). Content and tooling: the `combat-effects` skill's rubric gets a "stat changes" section (which modifier, a note only when nothing counts it); `combat_effects.py notes` lists rows whose notes say "AC", "Resistance", "Speed", "Hit Point maximum", "size"; then the parties, through `spell-combat-effects` / `feature-combat-effects`. | Curse of the Lich's and Time Loop PR's rows with such a note use a modifier or say why not |

7.1 and 7.2 are the slice to build first: they change the rolls and the
damage the simulator works out. 7.3 and 7.5 only change what is shown,
apart from the size gate. Wild Shape and Polymorph, which swap the whole
stat block, stay as they are (a form change, after which `rows_of` is
rebuilt), not a pile of modifiers.

## Rolled at the table (Phase 8, new, 2026-11-11)

The user (Decision 15): extra damage like Hunter's Mark should be "rollable
in real life", and so should everything else that's rolled. Players roll
their own dice; the simulator rolling for them is a convenience. Design
principle 13 is the rule; this is where each roll stands.

### Every roll, and how it's made at the table

| Roll | Rolled by | At the table | State |
|---|---|---|---|
| Initiative as the fight starts | the setup rows' Roll buttons | each row's box | already |
| A summon's initiative mid-fight | `_roll_into_turn_order` | the card's Set initiative... (anyone's, in a fight) | **built** (8.4) |
| A monster's attack and damage, main window | its action button (`_roll_action`) | the Attack roll and Damage fields; the rolled damage lands in the Damage field, which can be changed before Enter | already |
| A hit's extra damage, main window | the action button adds it to the Damage field; a typed hit says "+1d6 Force (Pirate's Hunter's Mark)" (Q27) | change the Damage field, or type it with the damage ("7 sl + 4 fo") | already |
| Attack rolls, saves and damage in the Custom Effect dialog | `_apply_custom_effect` | a box per target, and the Damage field | already |
| A hit's extra damage in the dialog | `_with_hit_extras` | a box under its target's row, per thing that gives it | **built** (8.1) |
| What modifiers add to a roll (Bless's 1d4, cover's +2) | `roll_bonuses` | in the total typed; the target's row says what to add (Decision 4) | already |
| Times copies after the first (Scorching Ray's second and third rays) | `repeated()` | a roll per copy in each box ("17, 9, nat 20"); blank or missing ones roll | **built** (8.5) |
| A fired row's damage, save and conditions (Hellish Rebuke) | `_use_trigger` → `_apply_row` | the pop-up's Edit... opens the dialog with it picked | already |
| A fired row's damage reduction (Deflect Attacks, Stone's Endurance) | `_before_hit` | a box beside its checkbox in the pop-up | **built** (8.2) |
| Hit Points a badge gives as a turn starts (Heroism) | `_give_trigger_hit_points` | dice from a player's badge, or a monster's with `monsters_roll_turn_dice` off: a turn-column button opening the dialog; a number is given by itself | **built** (8.6) |
| A badge's Hit Point maximum with dice (Heroes' Feast's 2d10) | rolled as the badge is given (R85) | the dialog's Hit Point maximum box: one total, or one per target | **built** (8.6) |
| A monster's recharge | `_start_monster_turn` | `monsters_roll_turn_dice` off: a reminder, and ↺ makes the action ready | **built** (8.3) |
| A monster's repeat save | `_end_of_turn_saves` | `monsters_roll_turn_dice` off: a reminder, as a player's | **built** (8.3) |
| A monster's Concentration save | `_ask_concentration_saves` | `monsters_roll_concentration` off (the default): on its card | already |
| A player's repeat, Concentration and death saves | nothing | reminders and card buttons | already |
| A badge's turn-end damage (Spirit Guardians) | its turn-column button opens the dialog | the dialog's boxes | already |

The free d20 roller under the turn panel is a convenience, not a rules
roll, and stays as it is.

### Steps

| # | Step | Done when |
|---|---|---|
| 8.1 | **Done** (R115-R117). `CustomEffect.typed_extras` (by target, then by what gives it); `hit_plan(..., rolled)` and `HitPlan.at_table`; a box under each target's attack row for each extra a hit on it deals. | Hunter's Mark typed as 3 deals 5 + 3 with no d6 rolled and logs "+3 Force (rolled at the table)"; a typed 4 joins a typed damage total of 7; 0 leaves it out; on a Critical Hit it isn't doubled; a blank under a typed total is logged as not rolled; the box goes with an attack roll's hit only; with Times, the first copy takes it; the dialog fits 600 high with eight targets under Divine Favor |
| 8.2 | **Done** (R118). A box for a fired row's own roll in the trigger pop-up (`TriggerChoice.rolled`). | Deflect Attacks typed as 11 takes 11 off a 13 hit without rolling, logged "(1d10 + 8, rolled at the table)"; "7 + 8" reads as 15; blank rolls |
| 8.3 | **Done** (R119). The setting `monsters_roll_turn_dice` (on by default, the old behaviour). | Off: a spent recharge action stays spent with a reminder and no d6 rolled; a monster's repeat save is a reminder and its condition stays; the Settings dialog still fits 600 high |
| 8.4 | **Done** (R120). Set initiative... on a card (Q58). | The Tiger's 10 set to 20 puts it first and it's still the Pirate's turn; the current turn's own moves and keeps the turn; one undo puts it back; the card menu asks and sets it; nothing to set before the fight |
| 8.5 | **Done** (R121). A roll per Times copy in each box (Q59). | Times 2 with "nat 1, nat 20" misses, then lands a Critical Hit with the extra typed for it (", 5"); "nat 1" alone rolls the second; "17, 9" with Times 1 is refused |
| 8.6 | **Done** (R122, R123). A rolled Hit Point maximum box; a player's dice Hit Points at a turn's start as a button (Q60). | Heroes' Feast typed as 12 raises the maximum by 12 with nothing rolled; the box is hidden for a pick without one; Heroism with 1d4 on a player gives nothing by itself and leaves a turn-column button |
| 8.7 | **Done** (R124). `tests/test_roll_sites.py` (Q61). | Every call of a rolling function is listed with its way to the table; a new one, or a listed one gone, fails |

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

- **R78. `armor_bonus` stays the one thing the attack paths read** (7.1).
  The plan named an `effective_ac(char)` for every path to call. The four
  paths (the dialog's target rows and attack loop, the main window's
  Attack roll field, a monster's buttons) already add `armor_bonus(target)`
  to `first_number(target["ac"])`, so `armor_bonus` now returns *the AC in
  use minus the stored AC*: `armor_class_bonus(char, stored)`, which is
  `armor_class(char, stored) - stored`. No caller changed, and
  `note_attack_roll`, which takes that bonus off a roll, keeps the players'
  known-AC notes about the stored AC, so they stay true when Mage Armor or
  Barkskin ends (Barkskin on AC 13 adds 4: a 15 that misses shows "AC >
  11"). With no stored AC only what adds to one counts, as before.
- **R79. The stored AC is the base Mage Armor competes with** (Q51 as
  suggested). A player's `ac` is the sheet's total and a monster's its
  stat block's; `ArmorClassBase` counts only when its 13 + DEX beats it.
  DEX comes from `char["Ability Scores"]` (0 without one). A shield the
  sheet already counts is lost under Mage Armor; that's the GM's edge.
- **R80. No `when` on `ArmorClassBase`** (Q52 decided otherwise). "A
  willing creature who isn't wearing armor" and Rage's "aren't wearing
  Heavy armor" are what the target must be when the effect is given, not
  something that comes and goes: the GM checks them by giving the badge.
  A `when` would mean "never counted" (principle 8), which is wrong here.
  Mage Armor's row says so in a note, with "it ends if the target dons
  armor".
- **R81. The order of AC modifiers** (7.1): the best of the stored AC and
  each `ArmorClassBase`, then every `ArmorClass`, then at least each
  `ArmorClassMinimum`, then cover. Barkskin is a floor under the AC the
  creature's own effects give (Shield of Faith on 13 is 15, so 17; on 16
  it's 18), and cover adds to whatever that is (Barkskin with Half Cover
  is 19), since cover is about the attack, not the creature. Each
  (source, modifier) pair counts once: two records of Shield of Faith
  give +2 (Combining Game Effects). The dialog's notes say each: "Mage
  Armor: base AC 13 + DEX", "Barkskin: AC at least 17".
- **R82. Immunity and Vulnerability from a badge go where Resistance
  does** (7.2): `_damage_type_modifier` reads `immune_to_damage` and
  `vulnerable_to` beside the stat block's lists, as it read `resists`.
  The three share `_damage_modifier`; none listed means all damage, as
  Petrified's Resistance. The player view no longer learns a defense a
  badge gave: `note_damage_defense` skips a resisted or immune type the
  creature's modifiers cover (before, only Resistance to all damage was
  skipped, so a monster's Stoneskin would have shown as "Resists
  Slashing").
- **R83. Rage is a 10-minute badge its owner puts on itself** (7.2):
  Resistance to Bludgeoning, Piercing and Slashing, `D20Mode` Advantage on
  Strength checks and saves, and two `Note`s (its Rage Damage bonus for
  the Barbarian's level, Q26 still open; no Concentration or spells). It
  lasts "until the end of your next turn" unless extended, which the
  simulator can't see, so the row's note tells the GM to take it off.
  No party has a Barbarian, so no picker golden changed for it. The
  spells' golden (`caster_described_spells`) gained the 8 new rows, read
  against their text: same shape as Bless and Shield of Faith, Barkskin a
  Bonus Action (2024), Concentration on Stoneskin and Protection from
  Energy only.

- **R84. The Hit Point maximum is worked out, not written** (7.4). The
  plan said giving Aid "raises `max_hp`". But a player's `max_hp` is
  refilled from the sheet whenever a fight is loaded
  (`_take_combatants_from`, `_rebuild_players_from_log`) while its
  `active_effects` come back from the log, so a raised `max_hp` would be
  lost or, worse, taken off twice. `hit_point_maximum(char)` is the
  stored `max_hp` plus each rolled `HitPointMaximum` on its badges (once
  per effect, never below 0), and every reader uses it: the heal cap,
  Bloodied, the card's bar, the player view's bar and known-maximum
  notes, the rest dialog, the encounter and log summaries. The `<= 0`
  checks for a summon whose HP isn't set still read the stored value.
- **R85. Dice and upcast are rolled once, as the badge is given**
  (`rolled_modifiers`): Heroes' Feast's 2d10 per creature, Aid's 5 plus 5
  for each slot level above 2 (the cast's `slot_level`, or the dialog's
  slot box, against the pick's `spell_level`). The record keeps the
  number (`HitPointMaximum("10")`), so the maximum is the same on every
  read and after a reload; an unrolled one counts nothing. All three
  places that give a badge's modifiers (the dialog's pick, Cast Spell,
  Enable Feature) go through one `_give_badge_modifiers`.
- **R86. The rise in current HP is Hit Points regained** (`_heal_target`
  from the caster): it's capped by the new maximum, logged and replayed
  as a heal, counted in the stats, and brings a dying creature to ("Aid
  ... current Hit Points increase by 5"). A dead one gets nothing, as
  with any healing. A line before it says the new maximum ("Tiger's Hit
  Point maximum is 35 (30, Aid: +5)"). Aid given again on a creature that
  has it keeps one number, so nothing is added (Combining Game Effects).
- **R87. The drop as it ends is its own action**, `Action.LOSE_HIT_POINTS`
  (`{"hp_delta": -3, "reason": "Aid"}`), not damage: it isn't damage
  taken (no stats, no Concentration save) but the party's history must
  replay it, as it replays damage and heals. `_remove_condition_from`
  measures the maximum before the badge goes and, when it changed, caps
  current HP and rechecks Bloodied by the new maximum (17 of 35 is
  Bloodied, 17 of 30 isn't). A GM taking Bloodied off by hand is left
  alone: only a change in the maximum rechecks it. The public log shows
  the line as minor.
- **R88. Heroes' Feast gives Resistance to Poison, not Immunity** (2024).
  The vocabulary table and 7.2's "done when" had named it as the
  `DamageImmunity` example; no 2024 spell gives a damage Immunity for a
  while, so that modifier is for monsters' and homebrew effects. Heroes'
  Feast is a 24-hour badge with `Resistance` (Poison), `ConditionImmunity`
  (Frightened, Poisoned) and `HitPointMaximum("2d10")`.
- **R89. A test 7.2 broke, found in 7.4**: describing Rage gave its row
  the "Rage" badge, and `test_rage_and_danger_sense_have_no_save` asserted
  it gave none (it guarded against reading "Incapacitated" from Rage's
  text as a condition). The test now asks for the Rage badge. 7.2 had run
  only the modifier and picker tests, not the effect-options file: run
  `test_combat_ui_effect_options.py` too whenever a party's or a
  sheet's feature gets combat effects.

- **R90. One wording for a changed stat: "in use (stored; what changes
  it)"** (7.5). The plan's examples mixed shapes ("AC 17 (15 +2 Shield of
  Faith)", "Large (Medium, Enlarge)"); a base AC and a floor don't read as
  "+n", so every changed stat is the number in use, then in brackets the
  stored one and each change by name, in the order it counts: "AC: 19
  (13; Shield of Faith +2, Barkskin at least 17, Half Cover +2)", "Max HP
  35 (30; Aid +5)". A base is named only when it beats the stored AC, a
  floor only when it lifts it, so what's listed is what made the number.
  The words come from Qt-free functions (`armor_class_text`,
  `hit_point_maximum_text`, `defenses_from_modifiers` in
  `Combat/Effects/modifiers.py`; `armor_text`, `armor_in_use` in
  `attack_rolls.py`), shared by the card, More Info and the player view.
- **R91. Cover is in the card's AC now.** It was a badge beside the stat
  block's AC; the number shown is what an attack must meet, so it counts
  cover too (the card golden's one change: "AC: 20 (18; Half Cover +2)").
- **R92. A player's AC sentence stays when nothing changes it.** A sheet
  with a Shield writes "18 (with Shield) and 16 (without Shield)"; that
  shows as before, and with Shield of Faith it's "20 (18; Shield of Faith
  +2)", from the first number, as every attack path already used.
- **R93. Defenses given are listed after the stat block's, with where
  from**, on the card's own rows ("Resist: Fire; Bludgeoning, Piercing,
  Slashing (Rage)"), and condition immunities too ("Cond. Immune:
  Poisoned (Petrified)"), so the card says why a hit was halved. The
  player view's summon card and the Limited view's known defenses are
  unchanged: the first lists the summon's stat block, the second only
  what the log showed (R82). No log line for any of it (Q54 as
  suggested).

- **R94. `Speed` has no `modes`** (7.3). The Rules Glossary's Speed: "If
  an effect increases or decreases your Speed ..., any special speed you
  have increases or decreases by an equal amount", and halving halves
  them too, so a change to one speed alone doesn't happen. A spell that
  *gives* a special speed (Fly's Fly Speed of 60) is another thing, a
  modifier of its own when content needs it. Order: every bonus, then
  every multiplier ((30 + 10) × 2 = 80 for Longstrider and Haste), rounded
  down, never below 0; the lowest `set_to` wins over all of them (a Speed
  of 0 "can't increase"). Each (source, modifier) counts once, as AC. The
  multiplier is an int or a float (0.5 halves), and the JSON reader takes
  both for it. Grappled's and Restrained's Speed 0 stay their `Note`, as
  the vocabulary table said.
- **R95. `Size(steps, becomes)`, not `set_to`.** The JSON reader goes by
  field name, one type each, and `Speed.set_to` is a number;
  `becomes` is a `CreatureSize` ("your size becomes Large"). `becomes`
  counts first, then the steps, kept between Tiny and Gargantuan (Large
  Form and Enlarge make a Medium Goliath Huge). A creature whose own size
  isn't known stays unknown with steps alone, so a size gate still asks.
- **R96. What reads the size in use.** `triggers.py`'s `largest_target`
  gate and its question ("Kivi hits Giant (Large)" for a Reduced Huge
  giant), and the player view's row. Nothing else in the simulator
  compares sizes yet (a monster rider's gate is a trigger, R75).
- **R97. Shown in R90's wording.** The card's AC and speed line reads
  "Speed: 80 ft. (40 ft.; Haste ×2)", every speed of a monster changed
  alike ("80 ft., climb 80 ft. (40 ft., climb 40 ft.; Haste ×2)"). The
  card showed no size, so it gets a line only when something changes it:
  "Size Huge (Large; Enlarge/Reduce +1)", "Large (Medium; Large Form)",
  nothing when the creature's own size isn't known (the badge is on the
  card anyway). More Info's type line and a player's Size and Speed
  fields use the same words. The player view shows only the speed and
  size in use, as it does the AC.
- **R98. A spell's badge keeps the spell's name, and Haste ends in a row
  of its own.** `combat_effects.py check` wants a spell's badge named as
  the spell, so Enlarge/Reduce's two rows both give "Enlarge/Reduce" with
  their own modifiers (the card says "Enlarge/Reduce +1" or "-1"). Haste's
  "Haste: lethargy" (`spends_use=False`: no slot, no Concentration) gives
  Incapacitated and a "Haste" badge holding `Speed(set_to=0)`, both until
  the end of the target's next turn; the GM picks it as Haste ends (Q55).
  Enlarge's +1d4 and Reduce's -1d4 are notes: they're the weapon's own
  damage type, which `ExtraDamageOnHit` can't say yet (the vocabulary's
  `damage_type=None`). Kivi is level 3, so Large Form (level 5) changed no
  picker golden; the spells' golden gained Haste's, its lethargy's and
  Enlarge/Reduce's rows, and Longstrider's (Obmar's, Hanna's) lost the
  Speed sentence from its note. Read against the spell texts.

- **R99. `ends_conditions`** (Q7). `CombatEffect.ends_conditions`, names
  (a `Condition` is kept as its name), not also given by the same effect.
  The dialog takes each off the targets its conditions would land on (a
  failed save, a hit, every target with no roll), through
  `_remove_condition_from`, so it's logged, replayed and undone with the
  Apply. A row with only that to do can be applied (the form's "Add a
  saving throw ..." check counts it). Lay on Hands has a row "Lay on Hands:
  end Poisoned"; Lesser Restoration a row per condition it can end
  ("end one condition"). The row's summary says "ends Poisoned".
- **R100. Paladin's Smite counts its free casting** (Q8):
  `FeatureUses(max_uses=1, regain_all_on="long rest")`. Its sheet card got
  a use box on all 16 Paladin builds (32 pages, the "Uses / Regain all on a
  long rest." lines only, read with `snapshot_diff.py`); its picker row's
  `counts_uses` is true. Regenerating the sheet goldens needs `-n 0`: the
  parallel workers each rewrite `sheet_hashes.json` and lose updates.
- **R101. The log encoder writes a monster ability's combat effects with
  `to_dict`** (Q23, DI-069), at any depth (`_encode` in
  `Combat/EncounterLogs.py` replaces `asdict`), so a badge's modifiers keep
  their `type`. Other dataclasses encode as before.
- **R102. A typed hit says its extra damage** (Q27): the Attack roll field's
  status line adds "; +1d6 Force on a hit (Pirate's Hunter's Mark)" per hit
  target, ", its dice twice" on a Critical Hit. Nothing is rolled for it
  (Decision 4).
- **R103. `targets: CombatTargets(count, upcast)`** (Q34), on 13 rows of 10
  spells (Bless 3 +1, Aid 3, Command's five, Charm Person, Heroism,
  Longstrider, Tasha's Hideous Laughter, Hold Person, Invisibility: 1 +1).
  The dialog shows "Targets: 4 at level 2" under the slot box and, with too
  many targeted, "(5 targeted: 1 too many)"; it doesn't refuse. Their "one
  more target per slot level" sentences went.
- **R104. `targets_self` is a field, not the source's `target()`** (Q35).
  `target()` didn't fit: Sacred Weapon's is OBJECT, and Elemental Strikes'
  is SELF while its save is against others. The dialog applies a
  `targets_self` row to the source alone and leaves the GM's targets as
  they were; the row's note starts "It goes on its user, whoever is
  targeted." Set on Second Wind, Rage, Patient Defense, Uncanny
  Metabolism, Steady Aim, Large Form, Elemental Attunement, Sacred Weapon,
  False Life and See Invisibility, whose "pick yourself" sentences went.
  Not built: opening the dialog with no target for a row with nothing to
  apply (Divine Sense, Step of the Wind, ...); their notes stay.
- **R105. `TurnOf.CURRENT`** (Q37): `(TurnEdge.END, TurnOf.CURRENT)`, which
  `CombatCondition` refuses with START. `duration_entry` makes it the end of
  the turn being taken (its first combatant's), and outside combat it
  lasts until removed. The Custom Condition dialog offers "Until the end
  of this turn". Steady Aim's badge uses it with `Speed(set_to=0)` (it was
  until the start of the Rogue's next turn, with the Speed in a note), and
  Sentinel's Halt is described (a "Halt" badge with `Speed(set_to=0)`;
  Edmund's picker gained the row).

- **R106. `stats` is a command of its own, not a filter on `notes`** (7.6).
  `notes` groups notes that start alike, to find a missing field; this
  one lists every note (and a badge's `Note`) that names a stat, by stat,
  and says whether the row's badge already has a modifier for it
  ("counted") or not ("NOTE ONLY"). It goes by words, so a note that only
  reads a stat as a gate (Sleep's "immune to Exhaustion", Patient
  Defense's "Speed is 0") is listed too: NOTE ONLY is a row to read, not
  a failure. `--campaign` keeps to one party's spells and features.
- **R107. Silence gets a badge though it's an area** (7.6). Its row already
  puts Deafened on each creature the GM says is inside, so the "Silence"
  badge with Thunder `DamageImmunity` goes on the same creatures and
  comes off with Deafened (its note says so). Absorb Elements is a row
  per type, as Protection from Energy; its Resistance and Shield's +5 come
  after the triggering damage or attack, so their notes say what the GM
  takes back until Phase 6.5's `HIT_BY` / `TAKES_DAMAGE` asks as it lands.
  The picker goldens: Hanna's, Clover's, Gabriel's and Dessie's Shield and
  Absorb Elements rows, Edmund's Shield of Faith note, and the Silence
  rows; read against the spell texts.

- **R108. `HIT_BY` is asked by itself, before the damage, not with the
  Apply's other triggers** (6.5). The answer changes the hit, so
  `_before_hit(outcome)` asks at once, in a pop-up of its own, for each hit
  target in turn, and returns whether the attack still hits and what to
  take off its damage. The dialog's attack loop calls it after the roll is
  checked and before damage, extra damage and conditions; the main window's
  Damage field calls it per target before `_deal_damage`
  (`_deal_typed_damage`, split out of `_do_apply_damage`). What it applies
  goes through `_apply_row` as any firing does, so Shield is cast (a slot,
  "Clover casts Shield"), its badge goes on Clover (`targets_self`), and
  her Reaction is spent by the row's own action cost, all in the hit's undo
  step. With `ask_triggers` off it's a turn-column button ("Clover: Shield
  (hit by Ogre)") and the hit is dealt as it is.
- **R109. The hit is rechecked against the AC in use after the answer**
  (`still_hits`): a Critical Hit, an unknown total or no AC still hits. The
  roll's total travels in `AttackOutcome.total` and `PendingAttack.total`
  (the Attack roll field's, a typed roll's, a monster button's), and the AC
  it was checked against in `AttackOutcome.armor`, so the pop-up says "AC
  18 + 5 = 23: the 20 misses." (`TriggerRow.armor_bonus`, the
  `ArmorClass` bonuses on the row's badges). A hit that now misses logs
  "Ogre's attack roll now misses Clover" (no AC: the Limited view reads it),
  becomes a `MISS` outcome for the attacker's rows, and the status line says
  "then a miss". In the two-step path (Attack roll field's Enter, then the
  Damage field's) it's asked as the damage lands, not as the roll is
  checked: only then is the damage known, which Deflect Attacks needs.
- **R110. `CombatEffect.damage_reduction`, dice, with a `HIT_BY` trigger
  only** (Q39). Deflect Attacks' and Stone's Endurance's reductions are a
  number the window rolls as the hit lands, logs ("Kivi Jätti's Deflect
  Attacks takes 9 off the damage (1d10 + 8)") and takes off the hit's damage
  before Resistance (the glossary: Resistance comes after other
  modifiers), part by part (`reduced_damage`); all of it off deals nothing.
  Not a `CombatHitPoints`: it isn't Hit Points, and a feature works out its
  own bonus (principle 5). Picked by hand it does nothing, and its row says
  so. Deflect Attacks' "its damage includes Bludgeoning, Piercing or
  Slashing" is a `when` below Monk level 13, not checked from the damage
  types (a typed hit's types are known, a monster button's too, but the
  dialog's damage may be retyped; left to the GM for now).
- **R111. Stone's Endurance is `HIT_BY`, though its text is "when you take
  damage"**. A reduction must come before the damage, and only an attack
  roll's hit has a "before" the window knows. Damage from a failed save is
  picked by hand (its note says so). A `TAKES_DAMAGE`-before event for any
  damage would need every damage path to pause; not worth it for one row.
- **R112. `TAKES_DAMAGE` comes from `_deal_damage`**: damage taken (after
  Resistance, more than 0) from a creature other than the one damaged is a
  `DamageOutcome(source, target, taken)`, collected with the Apply's hit
  outcomes (`_one_trigger_prompt`, which `_do_apply_damage` now wraps
  around its whole dealing, so typed damage with no attack roll asks too).
  `outcome_firings` takes both kinds: for damage, the rows are the damaged
  creature's and the firing's target is the one that dealt it. What a
  firing deals (Hellish Rebuke's 2d10 Fire) triggers in its turn, so a
  reaction to a reaction asks after it; the Reaction gate ends the chain.
  The source is whoever the window says dealt it (the source, else the
  creature whose turn it is), as for the stats.
- **R113. The Reaction gate.** A row whose action is a Reaction
  (`TriggerRow.action`, the option's `action_cost`) or with `reaction=True`
  isn't offered while its owner has a Reaction logged this round
  (`action_uses`, reset as its turn starts) or has a condition that gives
  Incapacitated (`reaction_lack`). A reaction row is never AUTO. A firing's
  "already has every condition" check looks at its owner for a row that
  goes on its user (`TriggerRow.on_self`: Shield already on asks nothing).
- **R114. Questions and buttons name the event.** `HitFiring.question`
  reads "Ogre hits Clover: use Shield? ..." for `HIT_BY` and "Ogre deals
  Clover 7 damage: use Hellish Rebuke? 2d10 Fire. Check: if you can see it
  within 60 feet." for `TAKES_DAMAGE` (`HitFiring.outcome` keeps what it
  answers), and a turn-column button "Clover: Shield (hit by Ogre)". The
  pop-up's apply/edit/skip handling is one `_answer_firings`, shared by
  the hit's prompt and `_before_hit`.
- **R115. The extra damage's box is under its target's row, not a block of
  its own** (8.1). A block under the Damage field (a hint, then a row per
  target and extra) was built first, and made the dialog 729 high with
  eight targets under Divine Favor, which is on its caster, so every target
  has one. A row under the target's own, inside the attack rows' scroll
  area, costs no height. The target's line no longer repeats "+1d6 Force on
  a hit", since the row under it says it ("Hunter's Mark: +1d6 Force on a
  hit"); `test_the_dialog_reminds_of_the_marks_extra_damage` changed with
  it. The row's label wraps and its box is at least 110 wide, so two extras
  on one target don't squeeze the attack box.
- **R116. A typed extra counts whatever the gates say** (8.1). In
  `hit_plan(attacker, target, weapon_attack, rolled)`, a label typed in is
  added even where the simulator would only note it (a `when`, a
  weapon-only extra on an attack it can't tell) or leave it out (Divine
  Favor on a spell attack): typing it is the GM deciding (principle 8). It
  isn't doubled on a Critical Hit, since the box asks for the total, its
  dice already twice over. `HitPlan.at_table` names those labels, so
  `roll_extra_damage` adds them as typed and logs "+4 Force (rolled at the
  table)".
- **R117. A blank box under a typed damage total still adds nothing**
  (Decision 4), as before 8.1. The log now says so for the GM ("Pirate's
  Hunter's Mark: not rolled, as the damage total typed has it"), where
  before it said nothing. `typed_damage` no longer stops
  `_with_hit_extras` from running; it only drops the extras that weren't
  typed in. So a weapon's 7 and a mark's 4, both rolled at the table, make
  11.
- **R118. The pop-up's box is a `TriggerChoice` field** (8.2).
  `TriggerChoice.rolled` holds (firing, total) pairs and `rolled_for(firing)`
  reads one. `_answer_firings` returns each applied firing with what was
  typed for it, and `_before_hit` takes that off instead of rolling. Only a
  row with `damage_reduction` gets a box: the other rolls a fired row makes
  go through `_apply_row`, whose way to the table is Edit.... The box
  takes a total or a sum ("7 + 8"), through a validator, so it has nothing
  wrong to report.
- **R119. One setting for monsters' turn dice** (8.3):
  `monsters_roll_turn_dice`, on by default (the old behaviour), in the
  Damage section beside "Roll monsters' Concentration saves". The
  Initiative column had no room, and the dialog's 600-high limit took
  three hints made shorter (Concentration saves, the remembered damage
  type, Jump to Damage). Off, a recharge is a reminder ("Fire Breath
  (Recharge 5–6): roll its recharge (a d6 of 5 or more), ↺ if it comes
  back"), and ↺ (`_restore_ability`), which already existed, is how the
  roll made at the table is entered. A repeat save is the reminder a
  player gets, and the GM takes the condition off on a success.
- **R120. Set initiative... is for anyone with a turn of its own** (8.4).
  A summon's initiative is still rolled as it joins (and its summon line
  still says it); the card's right-click Set initiative... gives it the
  player's roll instead, or anyone's, which Q58 asked for as well. It
  isn't offered for a member of an initiative group, whose turn is the
  group's: moving one would split it. `_place_in_turn_order(char, value)`
  is the placing `_roll_into_turn_order` did, shared; the move keeps
  whoever's turn it is (char too, if it was char's), moves the card in the
  window as a summon's is placed, and is one undo step.
- **R121. A roll per Times copy, comma separated** (8.5). Each box (attack
  rolls, save totals, extra damage) reads "17, 9, nat 20" as one roll per
  copy, in order. A blank part (", 5") or a short list rolls the copies
  left; more parts than the Times is refused. The parsers return a list
  per key and `nth(lists, index)` picks a copy's; `repeated()` hands each
  copy its own, where before only the first had any. The Damage field
  still takes one amount: a total typed there is each copy's.
- **R122. One Hit Point maximum box, under the condition's notes** (8.6).
  It shows only for a pick whose badge has a `HitPointMaximum` with dice
  in its amount or upcast (Heroes' Feast's 2d10; Aid's 5 + 5 a level has
  none, so no box). It takes one total for every target or one per target
  in the order they're listed, the upcast in it.
  `_give_badge_modifiers(rolled_maximum=)` puts it in place of the dice
  before `rolled_modifiers`, so the record keeps it as R85's rolls are
  kept.
- **R123. A player's dice Hit Points at a turn's start are a button**
  (8.6). `_give_trigger_hit_points` still gives a number by itself
  (Heroism's 2). With dice, from a player's badge (its caster a player, or
  unknown) or a monster's with `monsters_roll_turn_dice` off, it gives
  nothing and leaves the turn-column button, whose dialog takes the total.
  No described content has such dice yet; the test gives Heroism 1d4.
- **R124. The guard test reads the code, not a list of lines** (8.7).
  `tests/test_roll_sites.py` walks Combat/CombatUIQt/ and Combat/Effects/
  with `ast`, finds every call of a rolling function (`randint`,
  `roll_dice`, `roll_save`, `roll_extra_damage`, ...) by the function it's
  in, and compares them with `ROLL_SITES`, each with its way to the table
  (or "helper", or "not a rules roll" for the free d20). A new place that
  rolls fails until it's listed, and an entry whose roll is gone fails
  until it's taken out, so the plan's table and the code can't drift.
- **R125. A spell's badge stands for the conditions it gave** (Decision 17).
  `_give_spell_badge` runs after a target's conditions are given in
  `_apply_effect_to_targets`: for a pick with a `spell_name` (a feature's
  use that casts a spell too) whose conditions include a rules condition
  and not the spell's own name (Bless's badge already is the spell), it
  gives the spell's badge with its card (`describe(..., SPELL)`), not
  counted in the fight's condition stats (`_add_condition_to(counted=
  False)`), and `link_badge` writes the conditions on its record as
  `linked` (`NotRequired`, so older records and logs read as linking
  nothing). `_remove_condition_from` does the rest both ways: a badge taken
  off takes off what it stood for, unless another badge stands for it too
  (Friends and Charm Person both on a Charmed target) or it's Unconscious
  at 0 HP; a condition taken off is struck from every badge's `linked`
  (`linked_badges_left_without`), and a badge left standing for nothing
  goes. So a failed repeat save, a timer, a concentration ending and a
  right-click all take both, in one undo step, each logged as it goes. Only
  conditions the spell newly gave are linked, as `applied` does for
  concentration: a Charmed given by hand before stays when the spell's
  badge goes, so it gets no badge. The condition's own badge keeps the
  spell's card as its tooltip, and its click still shows the rule.
  A log replayed into a new window restores both badges but not the link
  (the replay restores conditions, as with other records); the saved fight
  state keeps it. `tests/test_linked_badges.py`.
- **R126. A feature's badge too** (Decision 17, Q62). `_give_spell_badge`
  is `_give_pick_badge`: a pick of kind FEATURE that isn't casting a spell
  gives a badge of the row's name (`option.name`: "Turn Undead", "Hill's
  Tumble", an extension's own name rather than the parent whose uses it
  spends) with the feature's card (`_feature_condition_tooltip`,
  `FEATURE_BADGE_COLOR`), linked the same way. `_picked_feature` finds the
  feature object by the row's name, then by `feature_name`; the badge
  card lookup in `_describe_effect_condition` uses it too, so an
  extension's condition badge now shows the extension's card, not its
  parent's. A trigger's Apply goes through the same path, so Hill's
  Tumble's Prone from a hit logs one more line ("Ogre gains Hill's Tumble
  from Kivi Jätti"; `tests/test_hit_triggers.py` updated). A weapon's or a
  monster's action (Tree Club's Prone rider) gets none: its rider is plain
  in the log.
- **R127. `DROPS_TO_ZERO` is asked before the damage, not after** (6.6).
  "Drop to 1 Hit Point instead" means the creature never reaches 0: no
  Unconscious, Concentration kept (its save from the damage still asked),
  no knockout in the stats or on the player link. So `_deal_damage` first
  works out whether the whole hit (every damage type, after the save's
  half, Immunity, Resistance and Vulnerability, then Temporary Hit Points)
  would drop its target to 0 (`_drops_to_instead`, with the pure
  `_damage_after_defenses`), and asks then, in a pop-up of its own as
  `_before_hit` does; what it applies goes through `_apply_row` (the use is
  spent and logged), inside the hit's undo step. The damage is then dealt
  with a `floor` (`_damage_target(floor=)`): Hit Points don't go below it,
  so the damage lines log the real `hp_delta` and `knockout: false` and
  replay as they are, with no new log action. A line "Ymira drops to 1 Hit
  Point instead of 0" follows. Asked once per hit: its other damage types
  are held at the floor too. A floor higher than the creature's Hit Points
  (Relentless Rage's twice the Barbarian level) raises them, as its text
  says ("your Hit Points instead change to").
- **R128. `CombatEffect.drops_to`, a number, with a `DROPS_TO_ZERO`
  trigger only.** The feature works out its own number (principle 5):
  Relentless Endurance's 1, Relentless Rage's `2 * level`. Picked by hand
  (the setting off, so it was a turn-column button, or the GM noticed
  late) for an owner at 0 Hit Points that isn't dead, it brings them back
  up to that many through `_heal_target` (logged as regaining
  consciousness); its row's note says so. Relentless Rage's DC 10
  Constitution save, 5 higher per use since a rest, is its trigger's
  `when`: nothing counts the uses, so the GM rolls it.
- **R129. Killed outright is a gate, though the simulator doesn't kill
  outright** (DI-002). The damage past 0 is known before it's dealt, so a
  `drop_firings` row isn't offered when it's at least the Hit Point
  maximum in use, and the status line says why ("Relentless Endurance: not
  when killed outright (45 damage past 0, Hit Point maximum 45)"). The
  creature still drops to 0 and dying, as before; DI-002 stays open.
- **R130. `REDUCES_TO_ZERO` is a `KnockoutOutcome(source, target)` from
  `_deal_damage`, collected with the Apply's other outcomes** (after its
  `DamageOutcome`), its rows the source's. Its target is usually dead, so
  the dead-target gate doesn't apply to it. A new gate,
  `CombatTrigger.enemy_only` (for the events with another creature in
  them), checks the two are on different sides (`on_party_side`): Dark
  One's Blessing's "you reduce an enemy to 0". Its row is
  `optional=False`, `spends_use=False`, `targets_self` with its
  `temp_hp`, so it's AUTO: Wrenna's 6 Temporary Hit Points are given as the
  Apply ends, in its undo step. Its "someone else reduces an enemy within
  10 feet of you" is a note for now (Q63). The pop-up says what a row
  gives in words ("6 Temporary Hit Points", "Drops to 1 Hit Point
  instead"; `_trigger_row_what`).
- **R131. `BLOODIED` is a `BloodiedOutcome(target, source)` from
  `_deal_damage`**: damage that leaves its target Bloodied, when it wasn't
  before the hit, and not at 0 Hit Points ("become Bloodied but aren't
  reduced to 0 Hit Points from taking damage"), collected with the Apply's
  outcomes. Its rows are the target's own and fire on itself, so the
  "its own damage" check doesn't apply to it. Not from healing or a
  maximum that rises (Bloodied then goes, not comes), nor from a log being
  replayed. The one source here is the Necromancer's Harvest Undead
  (level 10: a Reaction, healing the Wizard level, `targets_self`; the
  Undead it drains is a `when` and a note, dealt by hand). The homebrew
  monsters' "While Bloodied" traits (Bloodied Frenzy) are a state, not a
  trigger: they'd be a badge modifier, not this.
- **R132. `ROLLS_INITIATIVE` is an `InitiativeOutcome(char)` per combatant,
  resolved once as `_start_combat` ends** (6.7), through the same
  `_resolve_attack_triggers` as a hit's: AUTO rows applied, the ASKs in one
  pop-up headed "Rolling Initiative can trigger:", or turn-column buttons
  with the setting off. Its rows fire on their owner (with Bloodied's and a
  failed save's, `_OWN`). A row that only heals or gives uses back isn't
  offered when it would give nothing (full Hit Points and no use spent),
  so a rested party is asked nothing and Uncanny Metabolism's once-a-day
  use isn't spent for nothing. Not from a fight continued from a log (no
  one rolls), nor a summon's own roll mid-fight (nothing here needs it).
- **R133. `CombatEffect.regains: tuple[CombatRegain, ...]`, on a
  `targets_self` row.** `CombatRegain(feature, up_to=None, count=None)`
  covers every "regain on Initiative" here: all (Uncanny Metabolism,
  Persistent Rage), until N are left (Superior Inspiration 2, Perfect
  Focus 4, Evergreen Wild Shape 1: "if you have no uses left, one"), at
  most N (Ever-Ready Shot 1). `regained_uses(char, regain)` counts what it
  would give now; the dialog gives each back with a
  `REGAIN_FEATURE_CHARGE` line, as a rest does, so the party's history
  replays it. Psionic Reserves isn't described: Psionic Power has no uses
  counted to give back.
- **R134. A use-free extension row says `spends_use=False`.** Ever-Ready
  Shot, Superior Inspiration and Persistent Rage are extensions of the
  feature they give uses back to, and an extension without uses spends its
  parent's: applied, Ever-Ready Shot spent an Arcane Shot and gave it
  back (found by its window test). The rubric says so now.
- **R135. `USES` is a `UsesOutcome(owner, target, row)` from the dialog's
  apply**, for every living target of a described pick, hit or miss,
  collected with the Apply's outcomes: a row whose `after` names the row
  picked fires against that target. `USES` joins the events with another
  creature in them (`largest_target`, `aim`).
- **R136. `CombatTrigger.aim` (`TriggerAim`: TARGET, ANOTHER,
  ALSO_OTHERS).** Green-Flame Blade's fire goes on a different creature,
  Ice Knife's explosion on its target and those near it: the simulator
  doesn't know who's near, so a row aimed past its target always asks,
  and the pop-up lists everyone else alive but its owner under its line
  (`HitFiring.others`, filled by `_answer_firings`): one to pick for
  ANOTHER (checking one unchecks the rest), any to add for ALSO_OTHERS.
  Apply applies the row to each (`_use_trigger(targets=)`); ANOTHER with
  none picked isn't used and the status line says so. A turn-column
  button for ANOTHER opens the dialog on the creatures right-clicked
  (not the one hit), or asks for one first.
- **R137. A spell's `after=` row follows only the casting picked**
  (`TriggerRow.spell`). A hit typed in has no row, and a monster's rider
  asks "if it was Tree Club" then (R74); a spell's later step would have
  asked about Green-Flame Blade on every hit Clover or Thum typed in. The
  casting is always picked in the dialog, which knows the row.
- **R138. `FAILS_SAVE` is asked from `_roll_effect_save`, before Legendary
  Resistance**, in a pop-up of its own (the answer decides the save), for a
  save the dialog rolled (a typed total was rolled at the table, so its
  reroll is too) that wasn't an automatic failure.
  `CombatEffect.reroll_save` is the bonus: the window rolls the save again
  (its modifiers count) and adds it, or takes the new total typed in the
  pop-up's box, logs "Sylvaine rerolls the save with Indomitable: 5 + 18 =
  23, makes it", and the save is what the new roll says. Saves rolled
  elsewhere (a monster's end-of-turn repeat save, a monster's
  Concentration save) don't ask: no monster here has such a row.
- **R139. What 6.7 leaves.** Booming Blade's "if the target willingly
  moves" stays a row picked by hand (position, principle 8). Weapon
  Mastery (Q38) is its own step, 6.9: eight properties, each a `HIT` or
  `MISS` row on the weapon. `CASTS_SPELL` has no source in the parties
  (Arcane Ward, Disciple of Life are for other builds). Diamond Soul's
  reroll spends a Focus Point, another feature's use (Q64).
- **R140. "A stated reason not to" is `Feature.untriggered`**, a class
  attribute beside the feature's code (6.8), not a list in the tool: the
  reason travels with the feature, and an agent writing its
  `combat_effects()` sees it. It isn't shown in the picker: the row's
  notes already say when to pick it by hand.
- **R141. `combat_effects.py triggers --campaign X`** lists the party's
  features (each class once, extensions too) whose improved description
  has a fact whose key starts with "Trigger" (an option's too: "Hill's
  Tumble: Trigger") and that have neither a row with a trigger nor
  `untriggered`, and exits 1 if any; `--all` shows the triggered and the
  reasoned ones as well. `coverage` adds the feature rows with a trigger
  and the Trigger facts triggered, left to the GM and to do.
  `tests/test_skill_scripts.py` runs `triggers` for both parties. Features
  that say "When you ..." only in their plain text, with no improved
  description, aren't seen: a feature agent writing one's facts then sees
  it.
- **R142. The parties' eight were all left to the GM**, each for a reason
  the rubric now lists: Sacred Weapon (the Attack action isn't an event),
  Combat Inspiration (twice: the die is spent by the creature with the
  badge, Q57), Warding Flare (before an attack is rolled; Q65), Slow Fall
  (falling), Jolt to Life (changes a casting of Spare the Dying), Luck (a
  natural 1, rerolled at the table) and Lethargy Resilience (the player's
  own end-of-turn save). The three with a trigger were already built
  (6.3, 6.5, 6.7). No `feature-combat-effects` run was needed for eight.
- **R143. A mastery is the weapon's, not a feature's** (6.9). The eight
  properties are written once, in `Model/Content/WeaponMasteryEffects.py`
  (`mastery_effects(weapon, character)`, Qt-free, the 2024 Player's
  Handbook text as `MASTERY_RULES`: the Rules Glossary has no entry), and
  the picker adds the row under each weapon its wielder has the mastery of
  (`AbstractWeapon.has_mastery`): "Longsword: Sap", kind WEAPON, `after=`
  the weapon, spending nothing, its tooltip the rules text (the badge's
  card). The Weapon Mastery class feature stays `[]`: it grants, the
  weapon does. Numbers come from the weapon and its wielder: Topple's DC 8
  + the attack's ability modifier (`AbstractWeapon.attack_ability_modifier`,
  new) + Proficiency Bonus, Graze's modifier (no row at 0 or less),
  Cleave's attack bonus and its die with the weapon's other damage bonuses
  but not the modifier.
- **R144. A mastery follows only the weapon picked** (as R137 for a
  spell's later step: `TriggerRow.spell` is `picked_only`, for SPELL and
  WEAPON rows). A hit typed in the main window doesn't say which weapon:
  asking "if it was Longsword" and "if it was Handaxe" on every hit Edmund
  types was the Green-Flame Blade problem again, and broke every older
  test that typed a hit for a party member with a mastery (a modal pop-up
  no test answers). Pick the weapon in the dialog (its roll can be typed
  in there) and the mastery comes.
- **R145. `once` and `by_caster`, two modifier fields, not a new
  modifier** (principle 5: "the next attack roll" was a note on Guiding
  Bolt and Vicious Mockery, and Sap and Vex made four). `D20Mode(once=True)`
  (attack rolls only) is "its next attack roll" (Sap, Vicious Mockery);
  `AttacksAgainst(once=True)` "the next attack roll against it" (Guiding
  Bolt), with `by_caster=True` "your next attack roll against that
  creature" (Vex): only the creature that gave it gets it (a `when`, "the
  attacker is Thum", with no attacker known). `used_up_by_attack(attacker,
  target)` names the badges a roll uses up, and the window ends them
  ("Ogre's Sap is used up", then the usual loss line) as each roll is made:
  in `_resolve_attack_roll` (the dialog's loop and the Attack roll field,
  rolled or typed) and a monster's button, inside that roll's undo step.
  One with a `when` isn't used up (it may not have counted). Guiding Bolt
  and Vicious Mockery have their badge now, their notes gone.
- **R146. Slow's "doesn't exceed 10 feet" is the one-badge-per-name rule**:
  a second Slow on the same creature renews the badge, so Speed stays -10.
  Vex from two wielders on one creature is one badge too, the last
  wielder's; the first's Advantage goes (Q66).
- **R147. Push and Cleave ask, Nick is a note.** Push moves nothing the
  simulator tracks: its row is a reminder (Large or smaller, `largest_target`),
  and applied it logs "Obmar uses Sulvesburg's Folly: Push on Ogre"
  (`_use_trigger` logs a row that applies nothing). Cleave is an attack
  roll aimed at ANOTHER creature (the GM picks it in the pop-up),
  once per turn; its own hit fires nothing more (no row comes after
  "Greataxe: Cleave"). Nick changes when the Light extra attack is made,
  which isn't an event: a note on the weapon's row.
- **R148. A magic weapon is a weapon of its kind** (DI-080): `has_mastery`
  compared exact types, so Thum's Halfling's Trick (a Shortsword) had no
  Vex; `isinstance` now. Thum's sheet shows "Mastery: Vex ✓" on it.

## Open questions (with suggestions)

Q4-Q10, Q13, Q18, Q21-Q29, Q31-Q35, Q37, Q46, Q48-Q50, Q53 and Q55 are
**decided as suggested** (Decision 13, 2026-11-11), and Q14, Q16, Q30,
Q36, Q38 and Q39 too (Decision 14), Q58-Q61 (Decision 16) and Q62 (Decision 17); all
moved there. Q11 was done as suggested in S.4 (R24-R26): every spell is
a class.

- **Q67. A badge given by one hit, counted in the next of the same
  Apply** (R145). What a hit triggers is applied as the Apply ends (Q41),
  so with Times 2 (Extra Attack) the second attack doesn't get the
  Advantage of the Vex the first hit gave. *Suggestion:* apply
  AUTO rows that give a badge right after their hit, inside the loop, and
  keep only the ASKs for the one pop-up at the end; or leave it, and say
  "Vex: on the next Apply" in the status line.
- **Q66. Two wielders' Vex on one creature** (R146). One badge per name
  keeps the last wielder's caster, so Edmund's Advantage goes when Thum
  vexes the same Ogre. *Suggestion:* leave it until it comes up at the
  table; else name the badge after the wielder ("Vex (Thum)"), as
  Hunter's Mark would need for two Rangers.
- **Q65. Before an attack is rolled** (R142). Warding Flare ("when a
  creature you can see within 30 feet of yourself makes an attack roll,
  you can take a Reaction to impose Disadvantage on the roll"), Cutting
  Words' sibling Silvery Barbs, and a monster's Parry-like answers come
  before the roll. *Suggestion:* an `ATTACKS` event asked by the dialog's
  attack loop and a monster button before they roll (a typed roll is
  rolled already), with the attacker's target known, whose answer sets
  the roll's mode; only for an owner whose Reaction is left, and only for
  attacks on its side (`on_party_side`), so it isn't asked on every roll.
- **Q64. A row that spends another feature's use** (R139). Diamond Soul
  ("When you fail a saving throw, you can expend 1 Focus Point to reroll
  it") and Uncanny Metabolism's opposite, many Monk and Battle Master rows,
  spend uses of a feature that isn't theirs. *Suggestion:*
  `CombatEffect.spends: CombatRegain`-like `CombatCost(feature, count=1)`,
  checked and spent by `_use_pick` as a feature's own uses are, and
  counted in `TriggerRow.uses` so a firing with none left is said, not
  asked.
- **Q63. Dark One's Blessing for someone else's knockout** (R130). "You
  also gain this benefit if someone else reduces an enemy within 10 feet
  of you to 0 Hit Points": the knockout is seen, the 10 feet aren't.
  *Suggestion:* a gate `by_anyone: bool` on a `REDUCES_TO_ZERO` trigger,
  whose rows then fire for every creature's knockout of one of the
  owner's enemies, the owner's own as AUTO and another's as ASK with a
  `when` ("it was within 10 feet of you"). Until then the note says to
  pick it by hand. The two homebrew monsters with "drops to 1 Hit Point
  instead" (CR 1's assassin, CR 2's Harat) are freeform abilities; they
  get a `drops_to` row when they're converted.
- **Q57. A badge that answers a hit (`OnTrigger`, 6.5's rest).** Armor of
  Agathys ("a creature hits you with a melee attack roll ... takes 5 Cold
  damage", 5 more per slot level above 1, and it ends with no Temporary Hit
  Points) and Fire Shield. *Suggestion:* `OnTrigger(trigger, effect)` beside
  `AtTurnStart`, naming a row of the spell ("Armor of Agathys: Cold
  damage", `spends_use=False`), fired with the `HIT` outcomes of the one
  hit (after the damage, so AUTO when the melee kind is known, else ASK
  "if it was a melee attack"); its upcast amount rolled as the badge is
  given and kept on the record, as `HitPointMaximum`'s is (R85), so the
  fired row deals what the cast's slot said. Ending it with the last
  Temporary Hit Point is the GM's (a note).

- **Q56. Counting a feature's free castings one by one** (Q36 again). Fey
  Touched (Misty Step and a level 1 spell) and Fiendish Legacy (a level 1
  and a level 2 spell) each give two castings, once per Long Rest each,
  but a feature has one `FeatureUses`, so Q36's "a `FeatureUses(1)` per
  spell" can't be written. `FeatureUses(2)` would let one spell be cast
  twice. *Suggestion:* count them in the combat UI, not on the sheet: a
  row with `spends_use=True` and a new `CombatEffect.uses_per_long_rest=1`
  counts under its own row name in `feature_uses_used` ("Misty Step (Fey
  Touched)"), so `feature_lack` refuses a second casting until a Long Rest.
  The sheet cards don't change.

- **Q2** done in 4.1 (R57, R60).
- **Q17** moved to Decisions (10, R39): no.
- **Q19** decided in 3.5 (R52): repeat saves stay as they are.
- **Q20** built in 7.5 (R90), as "17 (15; Shield of Faith +2)". **Should the card show an AC with what adds to it** (Shield of
  Faith's 17, not the stat block's 15)? 3.3 counts it in every attack roll
  and shows it in the dialog's target rows, but the card still shows the
  stat block's AC, as it does under cover. *Suggestion:* yes, "AC 17 (15
  +2)", with cover too, in Phase 5 with the sheet chips; the player view's
  known-AC notes already take the bonus off (R27). *Now step 7.5*, with
  Speed, size, Hit Point maximum and Resistances shown the same way.

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
- **Q47. Generated monsters' riders: read at runtime, or generated?**
  `monsters.py` can't be hand-edited, so Tree Club's rider can't be
  written as a `combat_effects` row there. *Suggestion:* read it from the
  text in `monster_actions.py` (6.4), which also covers fight logs saved
  before. Teach `generate_monsters.py` to emit structured rows only if the
  reading proves fragile.

- **Q51** built as suggested (R79). **Is the stored AC a base or a total?** A player's `char["ac"]`
  is the sheet's total (armor, shield, Unarmored Defense), and a monster's
  is its stat block's. `ArmorClassBase` (Mage Armor) needs the base it
  replaces. *Suggestion:* treat the stored AC as the base the creature has
  without effects, and let `ArmorClassBase` replace it only when higher
  (13 + DEX on a Wizard with 12 is 15; on a Fighter in plate, nothing).
  The shield bonus the sheet already counts is the edge case: say so in
  Mage Armor's `when`.
- **Q52** decided otherwise (R80): no `when`. **Gates on a stat change the simulator can't see** ("if it isn't
  wearing armor", Rage's "while you aren't wearing Heavy armor").
  *Suggestion:* the same as everywhere (principle 8): a `when` on the
  modifier, counted by default and shown in the card's tooltip, so the
  GM takes the badge off when it doesn't hold.
- **Q54** decided as suggested (R93). **Should a shown stat change go in the log?** *Suggestion:* no
  line of its own: the log already says the badge was given and ended.
  The card's "AC 17 (15 +2 Shield of Faith)" is the reminder.

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
- **DI-080** (fixed in 6.9, R148): `AbstractWeapon.has_mastery` compared
  exact types, so a magic weapon didn't count its kind's mastery.
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
- **Phase 7:** `tests/test_stat_changes.py` (new). The JSON form and its
  strict errors for each new modifier. Expected values from the rules text
  and the glossary's Combining Game Effects and Damage Resistance and
  Vulnerability: Mage Armor, Barkskin with and without Shield of Faith,
  two Shields of Faith, Rage, Enlarge's size in a Phase 6 gate; 7.4: Aid's
  maximum and current HP given (level 2 and 3) and taken back (above and
  below the new maximum), Bloodied by the maximum in use, one undo, Aid
  again, a dying creature coming to, Heroes' Feast's 2d10 rolled once, and
  the drop replayed. Also `test_combat_ui_effect_options.py` (R89).
  7.5: the AC, Hit Point maximum and defense texts, a player's AC
  sentence, and a card before and after its badges end; the card golden
  (`test_combat_ui_cards.py`) read before `UPDATE_SNAPSHOTS=1`. Each badge
  ending by hand, timer and Concentration; one undo; an old log replaying
  the same. Plus `test_effect_modifiers.py` and `test_extra_damage.py`,
  to show what Phase 3 built didn't change.
- **Phase 8:** `tests/test_table_rolls.py`. Each roll typed in is used as
  typed and nothing else is rolled (a stand-in `randint` fails on any die
  but the d20s expected); blank still rolls; the boxes show only where
  their roll happens; the Custom Effect and Settings dialogs still fit
  600 high (eight targets under Divine Favor; two extras on one target).
  Plus `test_extra_damage.py`, `test_hit_by_triggers.py`,
  `test_combat_ui_settings.py` and `test_combat_ui_fast_play.py`. 8.4-8.6
  in the same file (Set initiative and its undo, a roll per Times copy, a
  typed Hit Point maximum, dice Hit Points left to a button);
  `tests/test_roll_sites.py` keeps principle 13 for new code (8.7).

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
