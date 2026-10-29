# Discovered issues

Bugs, rules mismatches and gaps that agents (and people) found but did not fix in the task at
hand. Every agent may add to this file and mark entries fixed, **only through the script**:

```bash
python .claude/skills/discovered-issues/issues.py list --status open      # what's known
python .claude/skills/discovered-issues/issues.py add --title "..." --area <agent or area> \
    --where "<path:line>" --by <your name> --details "<what's wrong, a failing scenario, a fix>"
python .claude/skills/discovered-issues/issues.py update DI-007 --status fixed --commit <hash> --by <your name>
```

The script locks the file, so several agents can write at the same time. Don't edit entries
with Edit/Write. The `discovered-issues` skill has the rules for when to add, fix or close one.

## Open

### DI-002 · No instant death from massive damage
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_do_apply_damage`

A 20/20 creature with 10 temp HP takes 70: it ends at 0 HP and 'dying'. 2024 rule (Playing the Game > Instant Death): if damage reduces you to 0 HP and the remainder equals or exceeds your HP maximum, you die. Fix: compute the overflow before clamping HP to 0; if overflow >= max_hp, set death_saves_fail = 3.

**History**
- 2026-10-28 rules-checker: found

### DI-003 · Damage at 0 HP adds no failed death save and doesn't end Stable
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_do_apply_damage`

A dying creature at 0 HP takes 3 damage: failures stay 0. A stable creature that is hit stays stable. 2024 rule (Playing the Game > Damage at 0 Hit Points): 1 failed save, 2 on a Critical Hit, death if the damage >= HP maximum. The UI has no crit flag, so at least add 1 failure (and clear Stable) when pre_hp <= 0 and dmg > 0.

**History**
- 2026-10-28 rules-checker: found

### DI-005 · No buttons for a natural 20 or natural 1 on a death save
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/cards_mixin.py`

A 20 should restore 1 HP; a 1 counts as two failures. Today the GM clicks Fail twice or heals 1 by hand.

**History**
- 2026-10-28 rules-checker: found

### DI-007 · Bloodied is removed when a creature drops to 0 HP
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_apply_bloodied_condition`

should_be_bloodied = hp > 0 and hp <= max_hp / 2. Bloodied.md: 'A creature is Bloodied while it has half its Hit Points or fewer remaining' - 0 counts. Low impact (badge only). User deferred this on 2026-10-28.

**History**
- 2026-10-28 rules-checker: found

### DI-008 · Negative damage or heal input isn't rejected
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_do_apply_damage`, `Combat/CombatUIQt/damage_mixin.py:_apply_heal`

Typing -5 as damage adds 5 temp HP (temp_reduction = min(temp_hp, -5)); a negative heal deals damage. Reject values below 0 in both handlers.

**History**
- 2026-10-28 rules-checker: found

### DI-010 · UPDATE_SNAPSHOTS with -n auto can lose golden updates
- **Status:** open
- **Area:** test-bughunter
- **Where:** `tests/_snapshot_helpers.py`, `pytest.ini:7`

On 2026-10-28, 'UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -k "<5 builds>"' rewrote only 4 of the 5 builds' sheet_hashes.json entries; rerunning for the missing build alone fixed it. Likely several xdist workers read-modify-write the same golden file at once. Fix: lock the golden file during updates, or have the update path run with -p no:xdist / -n 0.

**History**
- 2026-10-28 main-session: found
- 2026-10-28 claude-main: Also seen in tests/snapshots/combat_ui_cards.json (via tests/_combat_ui.py check_golden): the races left truncated, invalid JSON, not just lost entries

### DI-013 · Boon effects that apply only while Bloodied are text only
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Features/CharacterFeats/EpicBoon.py:768`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:1121`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:598`

The engine has no way to express a resistance or immunity that holds only under a condition. So Boon of Desperate Resilience's resistances and Boon of the Furious Storm's immunity (both only while Bloodied), and Boon of the Night Spirit's resistance (only in dim light or darkness), are left out of the sheet's resistance/immunity lists and appear only in the feature text. Fix: a conditional-defense entry (e.g. 'Resistance to X while Bloodied') that the sheet shows with its condition, and that the combat simulator could apply when Bloodied.

**History**
- 2026-10-28 main-session: found

### DI-014 · tag_report.py misses usage_tags set as a class attribute
- **Status:** open
- **Area:** main-session
- **Where:** `.claude/skills/usage-tags/tag_report.py:36`

tag_report.py finds tags only as a literal usage_tags=[...] keyword in a call inside the class. A class that sets _USAGE_TAGS = [...] and passes it via a base class's __init__ shows as untagged, although the card renders the tags. Found while adding the Faerun Epic Boons (the agent worked around it by passing the literal in each subclass's super().__init__). Fix: also read a class-level _USAGE_TAGS list, or fall back to instantiating the feature and reading .usage_tags.

**History**
- 2026-10-28 main-session: found

### DI-016 · No way to add spells to a class's spell list, so Dragonmark 'Spells of the Mark' and Potent Dragonmark's extra slot are text only
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Features/CharacterFeats/OriginFeats.py:_DragonmarkFeat`, `CharacterContent/Features/CharacterFeats/GeneralFeats.py:PotentDragonmark`

Each house Dragonmark feat adds a Spells of the Mark table to the Spellcasting/Pact Magic spell list; the engine has no expanded-spell-list support (2014 Warlock patrons' Expanded Spell List is text only too), so the table is only on the feat card. Potent Dragonmark's 'Dragonmark Preparation' (Spells of the Mark always prepared) and its extra spell slot (half level rounded up, max 5, Short or Long Rest, only for Dragonmark spells) aren't modelled either: the slot is a use box plus a slot-level tile. Fix needs a Model-level hook: a feature declaring extra spells for a class list, and a feature-owned spell slot.

**History**
- 2026-10-28 character-engine-dev: found

### DI-017 · Feat prerequisites on other feats are not validated (Greater Dragonmarks, Potent Dragonmark, 'Can't have another Dragonmark feat')
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Features/CharacterFeats/GeneralFeats.py:_GreaterDragonmarkFeat`

Greater Mark of X requires the Mark of X feat, Potent Dragonmark requires any Dragonmark feat, and a Dragonmark feat forbids a second one. No feat checks another feat's presence (only character level is checked, in constructors), so a build can take a Greater mark without its base mark or two house marks. Could be a validate() rule: each feat declares required/excluded feat types, checked with has_feature after all grants.

**History**
- 2026-10-28 character-engine-dev: found
- 2026-10-28 character-engine-dev: Planar Pact feats (OriginFeats.FeyPact/InfernalPact/ShadowPact, 'Can't have another Planar Pact feat') and the six Greater Planar Pacts (GeneralFeats._GreaterPlanarPact subclasses, which need their base pact feat) have the same gap: not validated, stated on the card only.

### DI-018 · Senses can't express 'gain Darkvision N, or +M if you already have it' with N != M, nor Darkvision unimpeded by magical Darkness
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `Model/Ledger/Senses.py:39`, `CharacterContent/Features/CharacterFeats/OriginFeats.py:1809`, `CharacterContent/Features/CharacterFeats/OriginFeats.py:1759`

Shadow Pact: 'You gain Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 30 feet.' GrantOrExtendSense/add_sense_or_extension uses one amount for both cases, so ShadowPact records GrantSense(DARKVISION, 60): a character with 60 ft Darkvision shows 60 instead of 90 (the card states the +30). Suggested fix: an extension_feet argument, range = max(range_feet, best plain grant + extension_feet). Separately, Infernal Pact's Darkvision 'is unimpeded by magical Darkness' (like Devil's Sight); a sense has only a range, so the senses line shows a plain 'Darkvision 30 ft.' and only the card says it sees through magical Darkness.

**History**
- 2026-10-28 character-engine-dev: found

### DI-019 · A feat can't grant a spell at a later character level than the one it is taken at
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Features/CharacterFeats/GeneralFeats.py:3788`, `CharacterContent/Features/CharacterFeats/GeneralFeats.py:3857`

Fey Sentinel ('When you reach character level 5, you also always have the Plant Growth spell prepared') and Fey Tormentor (Bestow Curse at character level 5) gate the extra spell on the constructor's character_level. A feat taken at character level 4 is built with character_level=4 (multiclass-builds skill), so a level 5+ build that took it at 4 never gets Plant Growth/Bestow Curse unless the build passes a later level. The feat's Grants scope is stamped with the feat's level and can't add a grant at a later level. Suggested fix: let Grants add a spell 'from character level N', or give grant_to the build's character level like SpeciesGrants.character_level.

**History**
- 2026-10-28 character-engine-dev: found
- 2026-10-28 main-session: code-reviewer: wider than Fey Sentinel/Tormentor. _DragonmarkFeat.free_cast_spells (OriginFeats.py:1734) gates the level-3 Spells of the Mark spell the same way (Detection, Finding, Healing, Hospitality, Scribing, Storm, Warding); passing a higher character_level stamps the grant at that level's page instead. Fix in Model/Grants.py (level-aware grant), then drop character_level from these feats.
- 2026-10-28 main-session: Feats now declare spells via granted_spells() (FeatureSpell). A level-aware grant could be a FeatureSpell field (e.g. from_character_level) resolved in Character._feature_spell_grants, once the character level at read time is available there.

### DI-020 · tests/test_format_changed.py fails where format_changed.sh is checked out with CRLF (core.autocrlf=true)
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `format_changed.sh:13`, `tests/test_format_changed.py:38`

In worktree agent-af14d0d23a4dd92e0 (core.autocrlf=true) format_changed.sh is LF in the index but CRLF on disk, and 3 tests fail: test_formats_a_given_file, test_skips_format_sh_exclusions, test_staged_refuses_partly_staged_file, with bash errors "line 13: $'\r': command not found" and "set: pipefail: invalid option name". Suggested fix: a .gitattributes entry '*.sh text eol=lf' so shell scripts always check out with LF.

**History**
- 2026-10-28 character-engine-dev: found

### DI-021 · Character Creator offers private _Base feat classes (e.g. _DragonmarkFeat, _GreaterPlanarPact) as pickable feats
- **Status:** open
- **Area:** character-creator-gui
- **Where:** `Builds/CharacterCreator/Registry.py:425`

concrete_subclasses doesn't skip names starting with '_', so _DragonmarkFeat, _GreaterDragonmarkFeat, _GreaterPlanarPact (and older _SchoolAdept, _AbilityScoreFeat, _SpellcastingOriginFeat) appear in feat pickers; constructing them raises AttributeError (_NAME/_ABILITIES). Fix: filter cls.__name__.startswith('_') in Registry.

**History**
- 2026-10-28 code-reviewer: found

### DI-022 · Dragonmark/Planar Pact feats: Shadow Weaver use box, duplicated base-class init, no tests
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Features/CharacterFeats/GeneralFeats.py:4764`, `CharacterContent/Features/CharacterFeats/GeneralFeats.py:4312`

(1) ShadowWeaver._USES (1/Long Rest) is for Create Shadow's free Darkness cast, already on the spell row, but the card's activation is Manipulate Shadow (no limit), so it reads as 'Manipulate Shadow once per Long Rest'; remove _USES like Fey Sentinel/Tormentor. (2) _GreaterPlanarPact.__init__ copies _AbilityScoreFeat.__init__'s validation and calls Feature.__init__ directly, while _GreaterDragonmarkFeat calls super and overwrites usage_tags/activation; give _AbilityScoreFeat.__init__ optional usage_tags/activation and have both call it. (3) No tests for any of the ~40 new feats (e.g. Mark of Passage speed 35, Infernal Bulwark AC 10+Dex+CON with dex14/con16 = 15, Aberrant Anatomy Perception expertise + Blindsight 15, Greater Aberrant Mark rejects non-CON, Fey Sentinel rejects level 3). (4) Optional: literal 8 / 10 instead of SPELL_SAVE_DC_BASE / UNARMORED_AC_BASE at GeneralFeats.py:3935,4507,4540,4688,4750. (5) Greater Aberrant Mark / Greater Mark of Healing change the base feat's recharge but the base card still shows the old one.

**History**
- 2026-10-28 code-reviewer: found

### DI-023 · Improved descriptions of new feats drop 'you can' on optional, use-limited benefits
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Features/CharacterFeats/EpicBoon.py:817`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:898`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:939`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:682`, `CharacterContent/Features/CharacterFeats/GeneralFeats.py:4644`, `CharacterContent/Features/CharacterFeats/GeneralFeats.py:3819`, `CharacterContent/Features/CharacterFeats/OriginFeats.py:2413`

wrong text (rules-checker, source = each feat's own get_description()). Several new improved descriptions turn an optional, use-limited benefit into one that always happens, so a player reading the card thinks the once-per-turn / once-per-rest use is spent automatically on the first qualifying roll. The branch already fixed this pattern for Grappler and Tavern Brawler ("use both" -> "can use both").
- EpicBoon.py:817 Boon of Exquisite Radiance, Powerful Radiance: card "use the highest number possible for each damage die"; source "you can instead use the highest number possible ... Once you use this benefit, you can't do so again until you finish a Long Rest."
- EpicBoon.py:898 Boon of Fortune's Favor: card "reroll it and use the new roll"; source "you can reroll it and must use the new roll. Once you use this benefit, you can't do so again until the start of your next turn."
- EpicBoon.py:939 Boon of Poison Mastery, Perfect Poisoner: card "use the highest number possible for each die"; source "you can instead use the highest number possible for each die" (once per turn).
- EpicBoon.py:682 Boon of Bloodshed, Power from Pain: card "deal extra damage ..."; source "you can deal extra damage to the target equal to your Proficiency Bonus" (once per turn).
- GeneralFeats.py:4644 Infernal Dragoon, Devil's Favor: card "When you make a D20 Test, add +2 to the roll. Once per Long Rest."; source "you can add a +2 bonus to the roll. Once you use this benefit, you can't do so again until you finish a Long Rest."
- GeneralFeats.py:3819 Greater Aberrant Mark, Mark of Inspiration: card "When you cast a cantrip, roll one or two unexpended Hit Point Dice, then expend them ... Proficiency Bonus times per Long Rest."; source "When you cast a cantrip, you can roll one or two of your unexpended Hit Point Dice" (each use spends HP dice and a use).
- OriginFeats.py:2413 Fey Pact, Honeyed Words: card "reroll it and use the new roll"; source "you can reroll the check, and you must use the new roll."
Fix: put the choice back in each row ("can use the highest number...", "can reroll it; must use the new roll", "can add +2", "can roll one or two..."). No mechanics change; text only.

**History**
- 2026-10-28 rules-checker: found

### DI-024 · Multiclass Monks who don't start as Monk get no Martial Arts die or Dexterity on Unarmed Strike (Kagen shows 1d4 -1 instead of 1d12 +5)
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Classes/BaseClasses/MonkBase.py:225`, `CharacterContent/Features/ClassFeatures/Monk/MonkFeatures.py:MartialArts`, `Builds/Characters/Y2024_Rogue_ShadowMonk_KagenVoidstep.py:92`

contradicts (wrong number on a sheet). Source: SourceTexts/ClassTexts/monk.txt:85 "Martial Arts Die. You can roll 1d6 in place of the normal damage of your Unarmed Strike or Monk weapons. This die changes as you gain Monk levels" and :87 "Dexterous Attacks. You can use your Dexterity modifier instead of your Strength modifier for the attack and damage rolls of your Unarmed Strikes and Monk weapons."
The Martial Arts die and Dexterity reach the Unarmed Strike only through MonkCustomStarterClassArgs.default_equipment (MonkBase.py:225-237); MonkFeatures.MartialArts has no apply() that touches weapons. So a character who doesn't start as Monk keeps the plain 1d1 + Str strike at any Monk level.
Probe: Builds/Characters/Y2024_Rogue_ShadowMonk_KagenVoidstep.py (Rogue 1 / Monk 19, Str -1, Dex +5, Tavern Brawler) shows Unarmed Strike "1d4 -1" (Tavern Brawler's 1d4 + Str now beats the 1d1). Per the rules it is 1d12 + 5 (Martial Arts d12 at Monk 17+, Dexterous Attacks). Without Tavern Brawler the same gap shows 1d1 -1. The new Tavern Brawler work makes it visible but didn't cause it.
Suggested fix (character-engine-dev): have MartialArts.apply() register a WeaponDamageDie for weapons with is_unarmed_strike (and Monk weapons) using the Martial Arts die for the character's Monk level, the same "used only where it beats the weapon's own die" mechanism Tavern Brawler uses (WeaponMinimumDamageDie, Improvements.py:370). It also needs Dexterity, or the better of Str/Dex, as the ability, since WeaponDamageDie holds a single ability. Then the starting-class default equipment no longer has to carry the die.

**History**
- 2026-10-28 rules-checker: found

## Fixed

### DI-001 · Temporary Hit Points stack instead of keeping one amount
- **Status:** fixed · 2026-10-28 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_apply_temp_hp`, `Combat/CombatUIQt/logging_mixin.py:338`

_apply_temp_hp adds new temp HP to the old (5 + 8 = 13); replay does the same. 2024 rule (Playing the Game > Temporary Hit Points, not in the local glossary): temp HP don't stack; the creature keeps either the old or the new amount. Fix: max(old, amount) or a keep/replace prompt, in both places.

**History**
- 2026-10-28 rules-checker: found
- 2026-10-28 main-session: marked fixed; Temp HP keep max(old, new) live and on replay; log line says which amount was kept (uncommitted)
- 2026-10-28 main-session: Committed in ff16d3a1

### DI-004 · Unconscious isn't applied at 0 HP
- **Status:** fixed · 2026-10-28 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_do_apply_damage`

Knockout drops Concentration but never adds the Unconscious condition, so its effects (attackers have Advantage, hits within 5 ft are crits, auto-fail Str/Dex saves) aren't shown. Fix: add Unconscious at knockout for creatures that make death saves; remove it when HP is regained.

**History**
- 2026-10-28 rules-checker: found
- 2026-10-28 main-session: marked fixed; Knockout adds Unconscious to creatures that make death saves; healing/short rest/revive remove it (uncommitted)
- 2026-10-28 main-session: Committed in ff16d3a1

### DI-006 · Healing brings a dead creature back to life
- **Status:** fixed · 2026-10-28 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_apply_heal`, `Combat/CombatUIQt/rest.py:172`

Any heal on a creature with 3 failed death saves gives it HP, resets the saves and logs 'is resurrected'; healing a dying/stable creature is also logged as 'resurrected'. Dead.md: 'A dead creature has no Hit Points and can't regain them unless it is first revived by magic such as the Raise Dead or Revivify spell.' User deferred this on 2026-10-28 (may be a deliberate GM shortcut); confirm with them before fixing.

**History**
- 2026-10-28 rules-checker: found
- 2026-10-28 main-session: marked fixed; User confirmed: heal/short rest skip dead creatures; new Revive button on a dead card sets 1 HP (Action.REVIVE, replayed); downed heal logs 'regains consciousness' (uncommitted)
- 2026-10-28 main-session: Committed in ff16d3a1

### DI-009 · Summons with hp=0 stat blocks show as dead in the combat simulator
- **Status:** fixed · 2026-10-28 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/Monsters/CR_0/monsters.py:DraconicSpirit`

Spell-summoned creatures (e.g. Draconic Spirit) have hp=0 in their generated stat block because the spell sets their HP. Since 03bcecb0 a monster at 0 HP without death_saves is dead, so they appear with the skull icon until the GM sets HP. Possible fix: prompt for HP when adding a 0-HP combatant, or treat max_hp == 0 as 'HP not set'. Don't hand-edit the generated monsters.py.

**History**
- 2026-10-28 main-session: found
- 2026-10-28 claude-main: marked in-progress; Main session working on it
- 2026-10-28 claude-main: marked fixed; Initiative screen now asks for HP for any combatant with max HP 0 (Start Combat stays disabled until it's a positive number) and _char_death_state treats max HP 0 as 'HP not set', not dead. Uncommitted in the working tree.
- 2026-10-28 claude-main: Committed in f6dbd2d2

### DI-011 · Spell improved descriptions orphaned by the 2024 spell additions
- **Status:** fixed · 2026-10-28 · ea8a58f5
- **Area:** spell-improved-descriptions
- **Where:** `CharacterContent/Spells/spells_dnd5e_improved.json`, `CharacterContent/Spells/spells_dnd2024_improved.json`

a19d9d7e added 2024 versions of Catnap, Enervation, Negative Energy Flood and Power Word Pain, so their 2014 improved descriptions no longer loaded and Astral Flood's flavor stopped matching its rescraped text. This broke 20 tests (spell descriptions, 5 build snapshots, 10 order-invariance).

**History**
- 2026-10-28 main-session: found
- 2026-10-28 main-session: marked fixed; 2024 improved descriptions written, orphaned 2014 entries removed, 5 builds' goldens regenerated
- 2026-10-28 git-commit: marked fixed in ea8a58f5

### DI-012 · Epic boons can't grant spells, so boon spells are text only
- **Status:** fixed · 2026-10-28 · uncommitted
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Classes/BaseClasses/BardBase.py:296`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:955`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:1275`, `CharacterContent/Features/CharacterFeats/EpicBoon.py:385`

Every class base adds the level-19 boon with data.add_feature(self.epic_boon) (ArtificerBase.py:264, BarbarianBase.py:204, BardBase.py:296, ... RogueBase.py:188), which has no spell path. So Boon of Revelry's Otto's Irresistible Dance, Boon of Siberys's chosen spell and Boon of Magic School Mastery's spells appear only in the description and are never added to the character's spell list or spell cards. Fix: give EpicBoon an optional grant_to(data) hook like GeneralFeat.grant_to (GeneralFeats.py:112) and have the class bases call it, then move the three boons' spells onto it.

**History**
- 2026-10-28 main-session: found
- 2026-10-28 main-session: marked in-progress; Starting: unified feature spell-grant hook in the engine
- 2026-10-28 main-session: marked fixed; Feature.granted_spells() (Model/Spells.py FeatureSpell) is now the one way a feature grants spells; Character.spell_grants grants them with the feature, stamped like it. Boon of Revelry, Siberys and Magic School Mastery declare their spells (listed as '<boon> (<class> Level 19)'); feats, class and subclass features moved off their own grant paths. Tests in tests/test_spell_grants.py.
- 2026-10-28 main-session: Committed in 5b7d6912

## Won't fix

### DI-015 · UPDATE_SNAPSHOTS=1 under xdist corrupts shared golden JSON files
- **Status:** wontfix
- **Area:** tests
- **Where:** `tests/_combat_ui.py:check_golden`

run_tests.sh runs pytest with xdist workers; with UPDATE_SNAPSHOTS=1 each worker does load/modify/save on the same golden file (e.g. tests/snapshots/combat_ui_cards.json), so the writes race and leave truncated/garbled JSON (seen while fixing DI-009). Workaround: add -n0. Possible fix: lock the file in save(), or have run_tests.sh force -n0 when UPDATE_SNAPSHOTS is set.

**History**
- 2026-10-28 claude-main: found
- 2026-10-28 claude-main: marked wontfix; Duplicate of DI-010
