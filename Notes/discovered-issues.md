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

### DI-010 · UPDATE_SNAPSHOTS with -n auto can lose golden updates
- **Status:** open
- **Area:** test-bughunter
- **Where:** `tests/_snapshot_helpers.py`, `pytest.ini:7`

On 2026-10-28, 'UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -k "<5 builds>"' rewrote only 4 of the 5 builds' sheet_hashes.json entries; rerunning for the missing build alone fixed it. Likely several xdist workers read-modify-write the same golden file at once. Fix: lock the golden file during updates, or have the update path run with -p no:xdist / -n 0.

**History**
- 2026-10-28 main-session: found
- 2026-10-28 claude-main: Also seen in tests/snapshots/combat_ui_cards.json (via tests/_combat_ui.py check_golden): the races left truncated, invalid JSON, not just lost entries
- 2026-11-03 main-session: Hit again 2026-11-03: UPDATE_SNAPSHOTS=1 pytest on test_combat_ui_cards/more_info/combatant_snapshots lost writes (combatants.json got 31 of 166 lines). -n 0 works. conftest's xdist_group only takes effect with --dist loadgroup, which pytest.ini doesn't pass.
- 2026-11-09 main-session: Hit again 2026-11-09 (S.4): an update over every build left JSONDecodeErrors and 27 builds unwritten. Cause confirmed: pytest.ini's addopts has -n auto but no --dist loadgroup, so conftest's xdist_group does nothing. Workaround: UPDATE_SNAPSHOTS=1 ./run_tests.sh -q -n 0 ... Fix: add --dist loadgroup to addopts.

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

### DI-027 · Cards read ability scores of 10 or less as modifiers
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/cards_mixin.py:_add_ability_rows`

_add_ability_rows treats scores as modifiers unless one is over 10, so a Commoner shows +10 on every ability on its card. No stat block or campaign log holds modifiers. Saves in saves.py no longer do this. The cards golden has a modifier_scores case that pins the old reading.

**History**
- 2026-10-31 main-session: found

### DI-035 · Monster Spellcasting entries have lost their spell lists: the text stops at the colon
- **Status:** open
- **Area:** content-scraper
- **Where:** `Combat/monsters_raw.json`, `Combat/Tools/generate_monsters.py`

109 of the 115 Spellcasting entries across the monster classes end at 'casts one of the following spells ...:' with no spell names, for example Pixie, Giant Owl and Priest Acolyte. Combat/monsters_raw.json has the same cut text, so the loss is in the scrape, not in generate_monsters.py. Monsters also have no structured spell field. The combat UI therefore can't tell which spells a monster knows. Only hand-written entries such as PriestOfTheBlackTongues list them. Fix: rescrape the lists into monsters_raw.json, then regenerate.

**History**
- 2026-11-02 main-session: found
- 2026-11-07 main-session: The Custom Effect picker now offers the spells a monster's other abilities name ('casts Fear', 'uses Spellcasting to cast Mind Spike (level 3 version)') at the Spellcasting DC (effect_options.monster_action_options), but the Spellcasting row itself still has nothing to list until the scraped text has its spells again.

### DI-036 · Encounter difficulty treats 2024 XP budgets as floors, so it rates one tier too low
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/EncounterDifficulty.py:classify_difficulty`

classify_difficulty uses the 2014 '>= threshold' convention: 800 XP against four level 3s (Low 600, Moderate 900) is rated Low. In the 2024 DMG the XP Budget per Character is the most XP you may spend for that difficulty, so 800 XP exceeds the Low budget and is a Moderate encounter; anything above the High budget is beyond High. Fix: classify by the lowest tier whose budget the XP does not exceed (and flag XP over the High budget), then update the --difficulty output, tests and campaign difficulty notes. Workaround used in TimeLoopPR: encounters sit exactly on a budget number, which is the same tier under both readings.

**History**
- 2026-11-02 main-session: found

### DI-037 · Combat UI: features that spend a Wild Shape use don't take it from Wild Shape's count
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/features_mixin.py`, `CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py`

Uses are counted per feature name in char['feature_uses_used'], so Starry Form, Land's Aid, Wild Companion, Wildfire Spirit and similar features that cost 'a use of Wild Shape' count their own uses (if any) and leave Wild Shape's untouched. Scenario: a Stars Druid with 2 Wild Shape uses enables Starry Form twice, then can still Wild Shape twice (the card menu says '2 left'). Fix: let a feature declare that it spends another feature's uses, and have _count_feature_use charge that one.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-038 · Combat UI: a Wild Shape form's duration (hours = half Druid level) isn't tracked
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/WildShape.py`, `Combat/CombatUIQt/rest.py`

Wild Shape: 'You stay in that form for a number of hours equal to half your Druid level'. The combat UI keeps a form until the Druid leaves it, is Incapacitated, or takes a Long Rest (the player-log replay starts after it). Scenario: a Druid 2-3 (1 hour) ends a fight as a Brown Bear, takes a Short Rest (at least 1 hour) and starts the next encounter still a Brown Bear. Fix: count Short Rests (1 hour each) in the form's state, recorded with a logged event so the replay sees them, and end the form once they reach druid_level // 2 hours.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-039 · Combat UI: merged equipment's bonuses still apply in a Wild Shape form
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/WildShape.py`

Wild Shape: 'Equipment that merges with the form has no effect while you're in that form.' Combat/WildShape.py keeps everything a save or skill modifier adds beyond the ability score (character.get_saving_throw_modifier minus the ability modifier), which includes magic items, and the Druid's AC-independent item effects carry over too. Scenario: a Druid with a Cloak of Protection (+1 saves) in Brown Bear form still adds +1 to every save. Fix: separate item bonuses from proficiency and feature bonuses (the ledger's sourced values), and drop items unless the GM marks them as worn by the form.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-040 · Combat UI: a Druid's weapons are still offered while in a Wild Shape form
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/effect_options.py`, `Combat/WildShape.py`

Wild Shape: 'Your ability to handle objects is determined by the form's limbs rather than your own.' effect_options() lists char['_weapons_objects'] under Attacks whatever the form, so the Custom Effect dialog offers a Brown Bear's Druid a Quarterstaff attack with the Druid's own bonuses. Fix: hide the Attacks category while current_form(char) is set (the form's attacks are already listed from char['actions']).

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-041 · Combat UI: species damage resistances carry into a Wild Shape form
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/WildShape.py`, `Combat/PlayerCombatant.py`

Wild Shape keeps only creature type, HP, Hit Dice, INT/WIS/CHA, class features, languages and feats; the rest of the game statistics are the Beast's. Combat/WildShape.py adds the form's damage resistances/immunities to the Druid's own, because the combatant dict (built from character.damage_resistances()) doesn't say where each came from. Scenario: a Tiefling (Infernal Legacy) Druid in Brown Bear form still resists Fire. Fix: have PlayerCombatant record each resistance's source, and keep only class-feature and feat ones in a form.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-042 · Combat UI: damage riders on a Wild Shape form's attacks aren't applied
- **Status:** open
- **Area:** combat-simulator
- **Where:** `CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py`, `CharacterContent/Features/SubClassFeatures/Druid/DruidMoonFeatures.py`, `Combat/CombatUIQt/turn_panel_mixin.py`

The form's attack buttons roll the stat block's damage only. Not applied: Lunar Radiance (Improved Circle Forms, Moon 6: a form's attacks can deal Radiant instead of their type), Primal Strike (Druid 7: once per turn +1d8 Cold/Fire/Lightning/Thunder on a hit with a Beast form's attack; 2d8 from 15) and Improved Lunar Radiance (Lunar Form, Moon 10: once per turn +2d10 Radiant). The GM must remember and add them by hand. Fix: let a feature declare a rider for form attacks (type swap or extra dice, once per turn) and offer it on the turn column's buttons while current_form(char) is set.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-043 · Combat UI: Evergreen Wild Shape and Wild Resurgence don't give back Wild Shape uses
- **Status:** open
- **Area:** combat-simulator
- **Where:** `CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py`, `Combat/CombatUIQt/wild_shape_mixin.py`, `Combat/CombatUIQt/turns_mixin.py`

Archdruid (Druid 20), Evergreen Wild Shape: 'Whenever you roll Initiative and have no uses of Wild Shape left, you regain one expended use of it.' Nothing does this when combat starts. Wild Resurgence (Druid 5): 'Once on each of your turns, if you have no uses of Wild Shape left, you can give yourself one use by expending a spell slot'. Enabling it counts its own use and spends no slot, and Wild Shape stays at 0 left, so _assume_wild_shape refuses. Fix: at _start_combat, regain one Wild Shape use for an Archdruid at 0; give Wild Resurgence a handler that spends a slot and logs REGAIN_FEATURE_CHARGE for Wild Shape. Related: DI-037.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-052 · 2024 spell usage_tags that don't match the spell text (heal on polymorph spells, control on Find Steed); Conjure X summon tags inconsistent
- **Status:** open
- **Area:** character-engine
- **Where:** `CharacterContent/Spells/spells_dnd2024_extended.json`

Several 2024 spells carry usage_tags their own text doesn't support, all looking like one bad batch: Find Steed ['control'], Simulacrum ['heal'], True Polymorph ['heal'], Polymorph ['heal'], Shapechange ['heal'], Animal Shapes ['heal'], Astral Projection ['heal'], Alter Self ['damage'], Conjure Celestial ['heal'] (it also deals damage). Separately, 2024 Conjure Animals is tagged summon (an area of spirits) while the same-shaped 2024 Conjure Celestial, Conjure Constructs, Conjure Elemental, Conjure Fey, Conjure Minor Elementals and Conjure Woodland Beings are not. Found during summon-framework S4.1, which only added summon tags; re-tag through the usage-tags skill.

**History**
- 2026-11-05 character-engine-dev: found

### DI-053 · Combat UI: a summon that vanishes on its own turn skips the next turn's start (and the new round when it was last)
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/summons_mixin.py:466`, `Combat/CombatUIQt/summons_mixin.py:395`

When the combatant removed by _vanish_at_zero_hp (S2.10) is the current turn, _remove_from_fight only moves current_turn_idx (at %= len). Nothing Next does runs: no round_number += 1 and no '--- Round N ---' line, no _tick_active_features / _tick_timed_conditions / _tick_active_spells, the next combatant's action_uses isn't reset, _start_monster_turn (recharge) and _on_turn_changed don't run. Scenario (code-reviewer probe): order Tiger, Dessie, Hanna, drake; the drake drops to 0 HP on its round-1 turn (Fire Shield, Armor of Agathys, a reaction, a hazard): the turn goes to Tiger but the round stays 1, so Tiger acts twice in round 1 and every round-based duration is a round off. Mid-order, the next combatant keeps action_uses {'Action': 1}. Dismiss and 'replaced' have the same older flaw, but those are GM-chosen. Fix: in _remove_from_fight, when the current turn group is only the removed combatant, call self._advance_turn() first (nested @undoable, one undo step). Extend test_a_summon_vanishing_on_its_own_turn_passes_the_turn_on (it only checks the name) with the wrap case: round_number == 2 and the next combatant's action_uses == {}.

**History**
- 2026-11-05 main-session: found

### DI-054 · Combat UI: conditions timed on a removed summon's turn never end
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/conditions_mixin.py:294`

turns_left condition entries whose 'of' is a combatant that leaves the fight (a summon that vanished at 0 HP, or one dismissed), e.g. 'until the end of the drake's next turn', never count down, because that turn never comes. time_left entries already fall back to ticking at the start of a round when ticks_on is gone. Older for Dismiss; S2.10 makes it automatic. Fix: in _remove_from_fight, expire (or tick) entries with of == the removed combatant.

**History**
- 2026-11-05 main-session: found

### DI-055 · Test gap: no test drives _apply_custom_effect on a summon that vanishes
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/conditions_mixin.py:387`, `tests/test_combat_ui_summons.py`

S2.10 added a `continue` in the custom-effect path so a target that vanished from the damage isn't given the effect's condition or recorded in the caster's active_spells 'applied'. The code is right (code-reviewer probe), but test_a_damage_effect_skips_its_condition_on_a_summon_that_vanished calls _deal_damage directly, with no condition, so removing the `continue` fails nothing. Fix: drive _apply_custom_effect(CustomEffect(condition='Prone', damage=[(5, 'Bludgeoning')], concentration=True)) on [drake at 1 HP, another target]; assert the drake is gone and the caster's active_spells[0]['applied'] doesn't name it.

**History**
- 2026-11-05 main-session: found

### DI-056 · Combat UI: an older log's summon resolves to the first spec when one source has two specs of the same creature type
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/Summons.py (source_for, _earlier_names)`

Since S2.11, summons carry summon_source + summon_spec, so new logs are fine. A summon from a log written before S2.1 has neither key, so source_for falls back to matching the stat block's creature type, and _earlier_names gives the legacy alias "<owner>'s Companion (<type>)" to every spec of that type. With two specs of one type on one source, both resolve to the first spec. No such old log exists today (the four TimeLoopPR logs were rewritten in S2.1, and each companion feature had one spec), so this only matters for logs kept outside the repo.

**History**
- 2026-11-05 main-session: found

### DI-057 · Summon plan: S4.5/S4.7 need Monster Manual stat blocks that CharacterContent can't import
- **Status:** open
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Summons/SpellSummons.py`, `tests/test_layering.py`, `Notes/summon-framework-plan.md (S4.5, S4.7, S3.7)`

tests/test_layering.py lets content import only core/helpers/records/model/content, and forbids lazy imports that hide a cycle. So the SPELL_SUMMONS entries for Find Familiar (CR 0 beasts), Animate Dead and Fungal Infestation (Skeleton/Zombie), Create Undead, Danse Macabre etc. can't build their stat blocks from Combat.Monsters. Decide before S4.5 where they come from: handed in by the build as Wild Shape's CreatureForm callables are, or the needed stat blocks moved into a lower layer. Also: an entry must not import a content module that imports SpellFactory (today only CharacterFeats/EpicBoon.py), or Spell.py's import of the registry becomes a cycle.

**History**
- 2026-11-05 main-session: found

### DI-058 · Pyright: 18 errors in tests/test_combat_ui_summons.py around lines 830-864
- **Status:** open
- **Area:** combat-simulator
- **Where:** `tests/test_combat_ui_summons.py:830`

./typecheck.sh tests/test_combat_ui_summons.py reports 18 errors, all in older code at lines ~805-870 (not in the S2.10-S2.12 hunks). Found by combat-simulator and code-reviewer on 2026-11-05; not looked into.

**History**
- 2026-11-05 main-session: found

### DI-059 · Tests: intermittent UnicodeDecodeError ('charmap' codec, byte 0x8d) in a background thread
- **Status:** open
- **Area:** test-bughunter
- **Where:** `tests/ (unknown test)`

One full ./run_tests.sh -q run on 2026-11-05 ended '9303 passed ... 1 warning' with a PytestUnhandledThreadExceptionWarning: a thread's codecs.charmap_decode raised UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d in position 39. Two later runs had no warning. Likely a subprocess whose output is read with the Windows default (cp1252) encoding instead of encoding='utf-8' (0x8d is undefined in cp1252). Which test wasn't captured; grep tests/ for subprocess.run/Popen with text=True and no encoding.

**History**
- 2026-11-05 main-session: found

### DI-060 · pyright errors in two combat-effects test files (test doubles not typed as CharacterView / Combatant)
- **Status:** open
- **Area:** test-bughunter
- **Where:** `tests/test_feature_combat_effects.py:204`, `tests/test_monster_combat_effects.py:349`

./typecheck.sh on these files reports: _ArtificerAt passed where Feature.combat_effects expects a CharacterView (a duck-typed stub), and a Combatant constructed without combatant_type/hp/ac/temp_hp/conditions. Both predate the combat-effects refactor (2026-11-08) and the tests pass. Fix: give the stubs the type the call expects (a Protocol, or cast in the test), or build a real object.

**History**
- 2026-11-08 main-session: found
- 2026-11-08 main-session: Also about 30 errors of the same kind (Optional Qt accessors, QTest.keyClick overloads) in tests/test_combat_ui_custom_effect.py and tests/test_combat_ui_player_server.py, outside the lines changed on 2026-11-09.

### DI-061 · Homebrew Mira, Princess of the Loop has 6 MonsterAbility entries; the house rule is at most 4
- **Status:** open
- **Area:** monster-balancer
- **Where:** `Combat/Monsters/CR_5/monsters_homebrew.py:MiraPrincessOfTheLoop`

check_monster.py 'Mira, Princess of the Loop': score 0.55 OK, implied CR 5.15 OK, but 'abilities 6/4 FAIL house rule is at most 4 (1 trait)'. Present since the monster was added (c1a7b8aa); not caused by the combat-effects refactor (2026-11-08), which only changed Rewind's temp_hp to CombatHitPoints('10'). Fix: merge or drop abilities to 4 and rebalance to 0.4-0.6, or record an explicit exception if the campaign needs all six.

**History**
- 2026-11-08 main-session: found

### DI-064 · Shield's casting time is cut off in the scraped spell JSON ('...or targeted by the')
- **Status:** open
- **Area:** content-scraper
- **Where:** `CharacterContent/Spells/spells_dnd2024.json`, `CharacterContent/Spells/spells_dnd5e.json`

Both dnd2024 and dnd5e records for Shield end their casting_time at 'targeted by the'; spells_aidedd.json has the full text '...targeted by the Magic Missile spell'. The wikidot scraper likely stops at a link inside the trigger. Fix in the scraper (not by hand-editing the scraped JSON), then re-scrape.

**History**
- 2026-11-08 main-session: found

### DI-067 · Combat UI: a creature whose Unconscious ends isn't left Prone
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:535, Combat/CombatUIQt/damage_mixin.py:567, Combat/CombatUIQt/rest.py:204`

Unconscious.md: 'When this condition ends, you remain Prone.' Unconscious now gives Prone through HasConditions (Combat/Effects/modifiers.py held_conditions), so removing Unconscious (healing from 0 HP, Revive, Short Rest healing) also removes the Prone it gave, and nothing adds a Prone of its own. The healed creature's attack rolls then lose Prone's Disadvantage, and attacks against it lose the Prone notes, until the GM adds Prone by hand. Fix: when Unconscious is removed, add Prone unless the creature already holds it (and it isn't immune), logged like any other condition.

**History**
- 2026-11-09 rules-checker: found

### DI-068 · Combat UI: Invisible is a visibility state, so the Invisible condition's rules never reach the attack notes
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/Effects/modifiers.py:44 held_conditions, Model/Creatures/Combatants.py:71 Visibility.INVISIBLE`

The GM marks a creature Invisible through the visibility combo (char['visibility_states']), and the spells add an 'Invisibility'/'Greater Invisibility' badge; held_conditions only reads char['conditions'] and matches 'Invisible' or 'Invisible ...'. So attack_plan never shows Invisible.md's 'Attack rolls against you have Disadvantage, and your attack rolls have Advantage. If a creature can somehow see you, you don't gain this benefit against that creature.' for the usual way a creature becomes Invisible. Fix: have held_conditions also read the Invisible visibility state (or the UI add the condition with it).

**History**
- 2026-11-09 rules-checker: found

### DI-069 · A monster ability's combat effects are written to the encounter log with dataclasses.asdict, which drops a badge modifier's type, so one with modifiers can't be read back
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/EncounterLogs.py:73 LogJSONEncoder.default`, `Combat/CombatUIQt/monster_actions.py:124`

Plan step 3.3 gave CombatCondition a modifiers tuple (Model/Content/CombatModifiers.py types). CombatEffect.to_dict writes each as {'type': 'D20Bonus', ...}; LogJSONEncoder asdict()s a MonsterAbility, so its combat_effects' modifiers lose 'type', and CombatEffect.from_dict (monster_actions.py:124) refuses them ('type None is not one of ...'). No monster ability gives a badge with modifiers yet, so nothing fails today. Fix: in LogJSONEncoder, write a MonsterAbility's combat_effects as [e.to_dict() for e in o.combat_effects] (from_dict reads both forms). Reproduce: CombatEffect.from_dict(dataclasses.asdict(Bless().combat_effects()[0])).

**History**
- 2026-11-09 combat-simulator: found

### DI-070 · SpellClassConverter's _IMPORTS has no modifier names (D20Bonus, D20Test, ArmorClass, ...), so spell_mechanics.py add can't write a badge with modifiers into a module that doesn't import them yet
- **Status:** open
- **Area:** spell-mechanics
- **Where:** `CharacterContent/Spells/SpellClassConverter.py:80 _IMPORTS`

Plan step 3.3: CombatCondition.modifiers holds Model.Content.CombatModifiers types. source_of() writes them (CombatCondition('Bless', modifiers=(D20Bonus(...),))), but module_with() only adds imports for names in _IMPORTS, so a module without 'from Model.Content.CombatModifiers import ...' gets no import and add's fresh-import check fails. Level1.py has the import by hand (Bless, Shield of Faith). Fix: add the CombatModifiers names (ArmorClass, AttacksAgainst, AutoFail, D20Bonus, D20Mode, D20Test, Resistance, RollMode, ...) to _IMPORTS, and a rubric line for modifiers in the spell-mechanics skill.

**History**
- 2026-11-09 combat-simulator: found

### DI-072 · Model/Content/CombatEffect.py's _is_rules_condition duplicates Combat/Effects/modifiers.py's rules_condition (a rules condition's name, or one under a longer name)
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Model/Content/CombatEffect.py:93 _is_rules_condition`, `Combat/Effects/modifiers.py:62 rules_condition`

Found in review of plan step 3.3. CombatCondition refuses modifiers on a rules condition and needs the same name rule the simulator uses, but Model can't import Combat, so the rule is written twice. If one changes (e.g. how a longer name is matched), the two disagree. Fix: move rules_condition into Model/Content/RulesConditions.py (beside CONDITION_RULES) and have both import it; that touches RulesConditions.py, which was off-limits for 3.3.

**History**
- 2026-11-10 combat-simulator: found

### DI-073 · Combat UI: a non-concentration spell cast with Cast Spell keeps its badge after its duration runs out (Divine Favor, Mage Armor)
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/spells_mixin.py:580 (_apply_cast_spell: applied is filled only for concentration spells)`

Cast Spell starts a timer on the caster's active_spells for any spell with a duration, but its applied rows (what _end_spell_effects takes off) are only filled for concentration spells. So when a 1-minute Divine Favor expires the log says it expires, yet the Divine Favor badge (and since step 3.4 its ExtraDamageOnHit) stays on the caster until taken off by hand. Reproduced 2026-11-10: Pirate casts Divine Favor, 12 rounds pass, active_spells is empty and conditions still holds Divine Favor. The Custom Effect dialog's pick of the same spell gives the badge its own timer, which does end it. Fix idea: record applied rows for non-concentration spells too (without linking concentration), or give their badges a duration_entry as the dialog does.

**History**
- 2026-11-10 combat-simulator: found

### DI-074 · Re-adding a badge by hand overwrites its record's caster, so Hunter's Mark's extra damage follows whoever re-adds it
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/conditions_mixin.py:495`

_add_custom_condition calls note_origin(target, cond, caster=source_name), overwriting caster on an existing record; give_modifiers keeps the modifiers. Hanna marks the Tiger, then with the Pirate selected 'Hunter's Mark' is re-added from the combo: caster='Pirate', and the Pirate's hits get the 1d6. Same when a second caster marks the same target (one record per badge name). Fix: only set caster when the record has none.

**History**
- 2026-11-10 code-reviewer: found

### DI-075 · Monster action button's extra damage makes the extra's type the monster's remembered damage type
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/turn_panel_mixin.py:369`, `Combat/CombatUIQt/damage_mixin.py:244`

The button appends the extra last ('3 Piercing + 4 Force'); _do_apply_damage stores parts[-1][1] as source['_last_damage_type'], so the monster's next hit defaults to Force in both damage-type dropdowns. Only when the monster is itself the caster of an extra. Fix: remember parts[0][1], or have the button store the weapon's own type.

**History**
- 2026-11-10 code-reviewer: found

### DI-076 · A Divine Favor (Self) pick in the Custom Effect dialog puts its badge on the selected target, not the caster
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/conditions_mixin.py:839`

The dialog never redirects a Self spell's badge to the caster (R47 documents it). If the enemy is still selected, the enemy gets ExtraDamageOnHit. Fix: send a pick whose spell target is Self to the source, as Cast Spell does.

**History**
- 2026-11-10 code-reviewer: found

### DI-077 · Extra-damage test gaps: monster button on a Critical Hit; a weapon pick's damage edited to other dice
- **Status:** open
- **Area:** test-bughunter
- **Where:** `tests/test_extra_damage.py`

No test covers roll_extra_damage(plan, critical) from turn_panel_mixin.py:368 (passing False survives), nor the not _DICELESS.search(...) half of typed_damage at conditions_mixin.py:1753 (probe: Longsword edited to '1d8 + 6 Slashing' correctly still got +2 Radiant). Add one test each.

**History**
- 2026-11-10 code-reviewer: found

### DI-078 · Combat UI: a later step of a casting (spends_use=False) can upcast only by spending a slot
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/conditions_mixin.py (slot_combo, _apply_custom_effect)`

The Custom Effect dialog's slot box is both the cost and the upcast level. A row that is a later step of one casting (Ice Knife's explosion, Spirit Guardians: damage, Heroism's temp HP) spends no slot, so it starts at 'No spell slot' with the spell's own dice; choosing a higher slot to get the upcast dice also spends that slot. Nothing remembers the slot the spell was cast with. Suggestion: keep the cast's slot level on the caster's active spell (or the badge's record) and fill a later step's damage at that level without spending; Notes/combat-effects-plan.md Q29.

**History**
- 2026-11-10 main session (combat effects 3.5): found

### DI-079 · Cast Spell gives a hand-given badge its spell's modifiers, which then outlive the concentration
- **Status:** open
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/spells_mixin.py`

A target with a Bless badge typed by hand (Custom Condition) that is then Blessed with Cast Spell isn't in the active spell's applied (the cast didn't put the badge on), so it isn't linked to the caster's concentration; but give_modifiers still gives it Bless's 1d4 and describe the spell's tooltip. When the caster's concentration ends the badge stays and keeps adding 1d4 forever. Fix: either count the badge as the spell's (applied + link) when the cast gives it modifiers, or give modifiers only to badges the cast put on. Plan Q32.

**History**
- 2026-11-10 claude (combat effects 3.6): found

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

### DI-008 · Negative damage or heal input isn't rejected
- **Status:** fixed · 2026-11-03 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:_do_apply_damage`, `Combat/CombatUIQt/damage_mixin.py:_apply_heal`

Typing -5 as damage adds 5 temp HP (temp_reduction = min(temp_hp, -5)); a negative heal deals damage. Reject values below 0 in both handlers.

**History**
- 2026-10-28 rules-checker: found
- 2026-11-03 main-session: marked in-progress
- 2026-11-03 main-session: marked fixed; Already fixed by 4ad8f4ab: parse_damage/parse_amount reject a leading '-' and totals below 0, so Damage, Heal and Temp HP refuse them with a 'Nothing applied' status. Added test_negative_amount_is_refused (tests/test_combat_damage_rules.py) covering all three handlers.

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

### DI-020 · tests/test_format_changed.py fails where format_changed.sh is checked out with CRLF (core.autocrlf=true)
- **Status:** fixed · 2026-11-10 · uncommitted
- **Area:** character-engine-dev
- **Where:** `format_changed.sh:13`, `tests/test_format_changed.py:38`

In worktree agent-af14d0d23a4dd92e0 (core.autocrlf=true) format_changed.sh is LF in the index but CRLF on disk, and 3 tests fail: test_formats_a_given_file, test_skips_format_sh_exclusions, test_staged_refuses_partly_staged_file, with bash errors "line 13: $'\r': command not found" and "set: pipefail: invalid option name". Suggested fix: a .gitattributes entry '*.sh text eol=lf' so shell scripts always check out with LF.

**History**
- 2026-10-28 character-engine-dev: found
- 2026-11-09 combat-simulator: Hit again 2026-11-09 in a worktree (combat effects 3.1): the same 3 tests fail, everything else passes.
- 2026-11-09 main-session: 2026-11-09: reproduces per checkout, not per branch. In .claude/worktrees/agent-a4cd6d9a2cf96ff85 git ls-files --eol showed format_changed.sh as i/lf w/crlf (autocrlf checkout) and the 3 tests failed; the main checkout has w/lf and they pass. Git Bash grep/od hide the CRs, so check with git ls-files --eol or Python read_bytes. rm + git -c core.autocrlf=false checkout -- format_changed.sh fixes a checkout without a content change.
- 2026-11-09 main-session: marked in-progress; Adding .gitattributes '*.sh text eol=lf' in the main checkout.
- 2026-11-10 main-session: marked fixed; .gitattributes '*.sh text eol=lf' committed with the combat effects 3.3 merge; git ls-files --eol shows attr/text eol=lf on all four .sh files

### DI-025 · Warlock pact magic slots aren't tracked in the combat UI
- **Status:** fixed · 2026-11-03 · cbf7e0ae
- **Area:** combat-simulator
- **Where:** `Combat/PlayerCombatant.py:124`

combatant_from_character loads character.spell_slots only; character.pact_magic_slots never reaches the combatant dict, so a Warlock's card shows no slots, the 1-9 keys do nothing, and the Cast Spell dialog's slot picker says 'No slots tracked' and spends none. Fixing it needs pact slots kept apart from spell slots (a multiclass has both, a Short Rest restores only pact slots) plus their card row, rests and player-log replay. No Warlock in the Curse of the Lich party right now.

**History**
- 2026-10-31 main-session: found
- 2026-11-03 main-session: marked in-progress
- 2026-11-03 main-session: marked fixed; Players carry pact_slots apart from spell_slots, with their own add/remove_pact_slot log actions. Shown on the card, More Info and party view; spent by the 1-9 keys (once spell slots of that level run out), Cast Spell and Custom Effect (PactSlot choices); restored by Short Rest; replayed from the player log. Tests: tests/test_combat_ui_pact_slots.py.
- 2026-11-03 git-commit: marked fixed in cbf7e0ae

### DI-026 · Breaking concentration by casting another spell replays as an extra cast
- **Status:** fixed · 2026-10-31 · 97b31819
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/spells_mixin.py:_apply_cast_spell`

The 'ends (concentration broken by casting X)' log line carries action=CAST_SPELL with no value. _apply_replay_action counts every CAST_SPELL as a cast, so replaying the player log gives one spells_cast too many and a None key in spells_cast_by_name. Found by code-reviewer; existing bug, not fixed here.

**History**
- 2026-10-31 main-session: found
- 2026-10-31 main-session: marked fixed; New casts no longer tag the ended spell as a cast, and replay skips the valueless entries in older logs.
- 2026-10-31 main-session: marked fixed in 97b31819

### DI-028 · Player timers and condition notes do not survive replaying the player log
- **Status:** fixed · 2026-10-31 · 5247bcd7
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/logging_mixin.py:_rebuild_players_from_log`

timed_conditions, custom_condition_descriptions and repeat_saves on a player are not restored, so after a restart the condition stays with no timer or note. Predates the Custom Effect dialog, which makes timed conditions on players more common.

**History**
- 2026-10-31 main-session: found
- 2026-10-31 main-session: marked fixed; A fight in progress now keeps each player's active spells, timers, notes, repeat saves and owed Concentration saves in its log (PLAYER_FIGHT_KEYS), restored when the fight is continued.
- 2026-10-31 git-commit: marked fixed in 5247bcd7

### DI-029 · End Encounter leaves the Player Screen on the last round
- **Status:** fixed · 2026-10-31 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/encounters_mixin.py:223`

_leave_encounter switches to the party view without calling _refresh_views or starting _views_timer, so an open Player Screen keeps showing the finished fight's round and rows (monsters included) until something else refreshes it. Reproduced offscreen: after _leave_encounter the window was last told 'Round 1' with 3 rows, while a manual refresh gives 'Waiting for the fight to start' with 0. Start combat, HP changes, next and previous turn, undo across a round and back to initiative all refresh correctly. Fix: call self._refresh_views() at the end of _leave_encounter. Part of Notes/player-web-view-plan.md.

**History**
- 2026-10-31 main-session: found
- 2026-10-31 main-session: marked in-progress; Being fixed as step 1 of Notes/player-web-view-plan.md
- 2026-10-31 combat-simulator: marked fixed; _leave_encounter now calls _refresh_views. The same gap existed in Load Encounter: _open_encounter_log now refreshes too, so a fresh encounter no longer leaves the last fight on the Player Screen or the link. Tests in tests/test_combat_ui_player_server.py.

### DI-030 · *.html in .gitignore hides Combat/CombatUIQt/player_page.html from git
- **Status:** fixed · 2026-10-31 · uncommitted
- **Area:** combat-simulator
- **Where:** `.gitignore:210`, `Combat/CombatUIQt/player_page.html`

The player link's page is a source file, but the repo-wide *.html rule ignores it: git status doesn't list it and a commit won't include it, so on a fresh checkout every start of the player link fails with 'The link couldn't start ... No such file or directory'. Reproduce: git check-ignore -v Combat/CombatUIQt/player_page.html. Fix: add the line !Combat/CombatUIQt/player_page.html after *.html in .gitignore. .gitignore was outside the player web view task's scope.

**History**
- 2026-10-31 combat-simulator: found
- 2026-10-31 main-session: marked fixed; Added !Combat/CombatUIQt/player_page.html after *.html in .gitignore; not committed yet

### DI-031 · Player Link can't offer a Tailscale address, though the plan recommends Tailscale for remote players
- **Status:** fixed · 2026-11-01 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/player_server.py:31`, `Combat/CombatUIQt/dialogs_mixin.py:875`, `Notes/player-web-view-plan.md:166`

rank_addresses keeps only 192.168/16, 10/8 and 172.16/12, but Tailscale uses 100.64.0.0/10, and the address combo isn't editable, so the dialog can't serve on a tailnet IP. The plan's 'Only the address in the link would differ' is therefore wrong. Fix: allow 100.64.0.0/10 in _PRIVATE_NETWORKS (ranked last), or correct the plan. Found by reading the code, not by running Tailscale.

**History**
- 2026-11-01 main-session: found
- 2026-11-01 main-session: marked in-progress
- 2026-11-01 main-session: marked fixed; rank_addresses now keeps 100.64.0.0/10, ranked last, with tests. Not tried with a real Tailscale connection.

### DI-033 · Monster action rolls ignore the target's Half or Three-Quarters Cover
- **Status:** fixed · 2026-11-09 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/turn_panel_mixin.py:299`

_attack_hits compares the total with the target's bare AC, though Half Cover (+2) and Three-Quarters Cover (+5) are tracked in the target's visibility_states and SourceTexts/RulesGlossary/Combat/Attacks/Cover.md adds them to AC. Example: a monster action rolling 14 against an AC 13 target with Half Cover (effective AC 15) shows HIT and fills the Damage field; by the rules it misses. The 'vs AC' text at line 260 shows the bare AC too. Fix: one helper for a target's effective AC (first_number plus the cover bonus, the highest grade only), used here and by any other attack check.

**History**
- 2026-11-01 code-reviewer: found
- 2026-11-09 main-session: marked fixed; Plan step 3.2: _roll_action checks the one target's AC with attack_rolls.armor_bonus (cover plus modifiers), and 'vs AC' shows that AC.

### DI-034 · Attack rolls don't count conditions: Advantage/Disadvantage from Restrained, Paralyzed, Blinded, Poisoned etc., and Paralyzed/Unconscious critical hits
- **Status:** fixed · 2026-11-09 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/saves.py:roll_attack`, `Combat/CombatUIQt/turn_panel_mixin.py:_roll_d20_for_attack`

Saving throws in the Custom Effect dialog count conditions per target (saves.py _with_conditions), but none of the three attack paths do: roll_attack (Custom Effect), the monster action buttons, and the Attack roll field. In the Custom Effect dialog one Advantage setting covers every target, so a +5 attack on a Paralyzed Tiger and a healthy Bandit can't be rolled correctly in one go. Attack rolls against Blinded, Paralyzed, Petrified, Restrained, Stunned or Unconscious creatures have Advantage; a Blinded, Poisoned, Prone or Restrained attacker has Disadvantage. Prone targets and the automatic critical hits on Paralyzed/Unconscious depend on being within 5 feet, which the UI doesn't know, so those need flagging for the GM rather than applying. Documented as not counted in KEYBOARD_SHORTCUTS.md.

**History**
- 2026-11-02 main-session: found
- 2026-11-09 main-session: marked in-progress; Plan step 3.2: conditions as data (Combat/Effects)
- 2026-11-09 main-session: marked fixed; Plan step 3.2 (R27): the Custom dialog's rolls and a monster's action buttons count the attacker's and target's conditions from Model/Content/RulesConditions.py; position/sight-dependent ones (Prone, Paralyzed/Unconscious crits, Invisible, Frightened, Grappled) are noted, not counted; a typed roll stays as typed.

### DI-044 · Short Rest gave back every spent use of a feature that regains only one
- **Status:** fixed
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/rest.py`

_restore_feature_uses restored every spent use of each short-or-long-rest feature, ignoring FeatureUses.regain_x_on. Wild Shape, Rage, Channel Divinity (Cleric, Paladin), Second Wind, Psionic Energy and Soul Knife's energy all say to regain one use on a Short Rest. Fixed: a Short Rest now regains at most regain_x_on's count; tested in tests/test_combat_ui_wild_shape.py.

**History**
- 2026-11-04 main session (Claude Opus 5.5): found

### DI-045 · Combat UI: player companions roll their own initiative instead of acting on their owner's turn
- **Status:** fixed · 2026-11-04 · 8044cc59
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/turns_mixin.py:432`, `Combat/PlayerCombatant.py`

Companions from Feature.companion() (Dessie's Reanimated Companion, Hanna's Drake Companion in Time Loop PR) get their own row on the initiative screen. Roll for Monsters and Roll for All roll them a fresh d20 like any monster (they aren't _is_player), so the drake can end up acting before Hanna or rounds away from her. Rules: the drake 'shares your initiative count, but it takes its turn immediately after yours'; the Reanimated Companion 'acts during your turn'. Today the GM has to type the owner's number by hand, and with equal initiative a stable sort puts the companion after every tied player, not right after its owner. Fix: companions_of() records the owner (e.g. char['companion_of'] = 'Hanna'); the initiative screen gives companions no row of their own, and _start_combat puts each one directly after its owner in initiative_order (or makes it part of its owner's turn).

**History**
- 2026-11-04 main-session: found
- 2026-11-04 main-session: marked in-progress
- 2026-11-04 main-session: marked fixed
- 2026-11-04 main-session: marked fixed in 8044cc59

### DI-046 · Combat UI: a player's companion comes back fresh in every encounter (HP, death, summon use not carried over)
- **Status:** fixed · 2026-11-04 · 8044cc59
- **Area:** combat-simulator
- **Where:** `Combat/EncounterLogs.py:92`, `CharacterContent/Features/SubClassFeatures/Artificer/ArtificerReanimatorFeatures.py:241`, `CharacterContent/Features/SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py:170`

prepared_log puts each companion in at full HP, hidden, in every encounter's log, and nothing links one encounter's companion to the next. Example: Hanna's drake drops to 5/20 HP in The Drunk Oxe, and The Square starts it at 20/20; a drake killed in one fight is back in the next one, although Drake Companion says it remains 'until it is reduced to 0 hit points' and can be summoned again only once per long rest (or with a spell slot). The Reanimated Companion lasts until a long rest, and if Dessie dies it drops to 0 HP and dies, triggering Death Burst, which isn't automated either. Neither feature has FeatureUses, so revealing (summoning) one spends nothing. Add Combatant only makes a free-text name/HP/AC combatant, so a fight started before a companion was in its log can't get the real stat block. Suggested fix: replay companion HP/death from the player log like player state, spend a summon use (or a slot) when the GM reveals it, and let Add Combatant offer the party's companions.

**History**
- 2026-11-04 main-session: found
- 2026-11-04 main-session: marked in-progress
- 2026-11-04 main-session: marked fixed
- 2026-11-04 main-session: Fixed per feature (Feature.companion_rules): a Reanimated Companion can't be re-made while out and ends at a long rest; a drake is replaced by a new summon and stays out past a long rest until 0 HP. Summon spends the use, else the lowest slot (no slot-level choice for the GM).
- 2026-11-04 main-session: marked fixed in 8044cc59

### DI-047 · Combat UI: Drake Companion's Draconic Essence type is fixed by the build, not chosen per summon
- **Status:** fixed · 2026-11-04 · 8044cc59
- **Area:** combat-simulator
- **Where:** `CharacterContent/Features/SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py:228`

Drake Companion: 'Whenever you summon the drake, choose a damage type listed in its Draconic Essence trait' (Acid, Cold, Fire, Lightning or Poison). The companion card in the combat log is built once from the build's damage_type (Hanna: Fire), so its damage immunity and Infused Strikes always say Fire. If Hanna picks Cold against a fire monster, the drake still resists Fire and is hit by Cold for full damage, and damage applied through the UI is wrong. Fix: let the GM pick the essence when revealing the drake (rebuild immunity and Infused Strikes text), or at least note on the card that the type can change.

**History**
- 2026-11-04 main-session: found
- 2026-11-04 main-session: marked in-progress
- 2026-11-04 main-session: marked fixed
- 2026-11-04 main-session: marked fixed in 8044cc59

### DI-048 · run-apps screenshot.py combat prepares logs without the party, so players and companions never show
- **Status:** fixed · 2026-11-04 · e6fab83b
- **Area:** main-session
- **Where:** `.claude/skills/run-apps/screenshot.py:102`

The combat screenshot prepares the encounter log with players=[] and passes character_sheets=[] to CombatAppQt, so a screenshot of e.g. time_loop_pr_mira shows only Mira and the Warrior: no party, and none of the companions prepared_log adds from the party's sheets. Checking the companion change needed a scratch script instead. Fix: build the scenario's campaign party (campaign.players()), resolve_players for the encounter, and pass sheets= to prepare_log and the sheets to CombatAppQt.

**History**
- 2026-11-04 main-session: found
- 2026-11-04 main-session: marked in-progress
- 2026-11-04 main-session: marked fixed
- 2026-11-04 main-session: marked fixed in e6fab83b

### DI-049 · Player Screen overflows a 1080p TV in a large encounter (no scroll, rows squash)
- **Status:** fixed · 2026-11-05 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/player_view.py`

PlayerViewWindow lays its rows in a plain QVBoxLayout with no scroll area. time_loop_pr_square (4 players, 2 summons, 3 monster groups of 2) needs about 1130 px of rows at 1920x1080 before any summon card, so the window either grows past the screen or squashes word-wrapped labels (a summon card was cut off mid-line when the window was held at 1400 px). Fix idea: scale fonts down, or a two-column layout, when the rows don't fit the screen's height.

**History**
- 2026-11-05 combat-simulator: found
- 2026-11-05 combat-simulator: Seen with screenshot.py combat --scenario time_loop_pr_square --summon 'Drake Companion' --player-screen --size 1920x1080: the window grows to 1206 px tall and the drake's stat block loses its wrapped last line ('damage.'); at 1600x1300 it shows whole.
- 2026-11-05 main-session: marked fixed; PlayerViewWindow shrinks its style sheet's sizes (to 0.5 at most) until every row fits the window's height, and its layout no longer grows the window past the screen; refits on resize. Tests in test_combat_ui_player_server.py. Not committed yet.

### DI-050 · Combat UI: summon menu entry reads "Summon Summon Wildfire Spirit"
- **Status:** fixed · 2026-11-05 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/summons_mixin.py (_add_spec_summon_actions)`

The card menu labels a summon's entry f"Summon {feature.name} (...)". The feature Summon Wildfire Spirit (Wildfire Druid) now has a SummonSpec named "Wildfire Spirit", so the entry reads "Summon Summon Wildfire Spirit (...)". Animating Performance reads "Summon Animating Performance" though it summons a Dancing Item. Label it from spec.name instead ("Summon Wildfire Spirit", "Summon Dancing Item"). Not fixed now: summons_mixin.py is being changed for S2.5-S2.9 of Notes/summon-framework-plan.md.

**History**
- 2026-11-05 main-session: found
- 2026-11-05 combat-simulator: marked in-progress; S2.11: menu labels by spec
- 2026-11-05 combat-simulator: marked fixed; S2.11: _summon_label(spec) labels entries 'Summon <spec.name>' (Summon Wildfire Spirit, Summon Dancing Item); uncommitted

### DI-051 · An Invisible player's summon attacking records nothing for the Limited player view
- **Status:** fixed · 2026-11-05 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:175`

damage_mixin only notes what players learn from an attack roll (known AC etc.) when _can_be_seen(source). Since S2.9 a player's summon is shown like a player even while Invisible, so the players see its roll, but an Invisible summon's attack notes nothing. Fix: use player_view's player-aware check (_is_known / _seen) for the source there.

**History**
- 2026-11-05 combat-simulator: found
- 2026-11-05 combat-simulator: marked in-progress
- 2026-11-05 combat-simulator: marked fixed; _resolve_attack_roll uses player_view._seen(source, _player_names(...)); test test_an_invisible_players_summons_attack_roll_shows_the_targets_ac; uncommitted

### DI-062 · Five spell records have malformed components text, so SpellClassConverter leaves them as JSON
- **Status:** fixed · 2026-11-09 · cfc58eaa
- **Area:** content-scraper
- **Where:** `CharacterContent/Spells/spells_dnd2024.json`, `CharacterContent/Spells/spells_dnd5e.json`

SpellRules stores components as Component flags plus a material (Notes/combat-effects-plan.md, Spells as classes), so a record's components must read 'V, S, M (...)'. These don't: Ashardalon's Stride 'V,S'; Gate 'V, S, M(a diamond worth 5,000+ GP)'; Imprisonment 'V, S, M(a statuette of the target worth 5,000+ GP)'; Yolande's Regal Presence 'Component: V, S, M (a miniature tiara)'; Gate Seal None. They're scrape errors: fix them in the scraper (never by hand in the source JSON), re-scrape, and the converter takes them.

**History**
- 2026-11-08 main-session: found
- 2026-11-08 main-session: SpellFields (R20) reads 'V,S', 'M(...)' and a stray 'Component: ', so the converter now converts all but Gate Seal (no components). The records themselves still want the scraper fix.
- 2026-11-09 main-session: 2026-11-09: Gate Seal (no components) is now the only spell left as JSON, so it alone keeps DataSpell's companion handling and spells_dnd5e_extended/_improved.json alive (combat-effects plan S.4).
- 2026-11-09 main-session: Gate Seal fixed at the source: dnd5e.wikidot.com writes its label as '<strong>Components</strong>:' (colon outside the tag), which DnD5eSpellScraper's exact 'Components:' match missed. The scraper now matches a label with or without the colon (all four stat lines); Gate Seal's record was re-scraped alone (only components changed: 'V, S, M (a broken portal key, which the spell consumes)') and converted, so every spell is a class. Still open: the other four records' slips (2024 and 2014 sources), which SpellFields already reads; they want a scraper fix and re-scrape.
- 2026-11-09 main-session: marked fixed in cfc58eaa; Closed. Gate Seal was the only scraper bug (fixed in cfc58eaa). The other four are typos on the wiki pages themselves, checked 2026-11-09: dnd2024.wikidot.com has 'V, S, M(a diamond ...)' (Gate), 'V, S, M(a statuette ...)' (Imprisonment) and 'Component: V, S, M (a miniature tiara)' (Yolande's Regal Presence) inside the Components line; dnd5e.wikidot.com has 'V,S' (Ashardalon's Stride). The records copy the source faithfully, SpellFields reads all four (R20), and each spell is a class with the right Components, so no card is wrong. Normalizing them in the scraper would only change the records' stamps (drift) for no gain.

### DI-063 · Wildemount Dunamancy spells have a school or class with a note, which SpellRules' enums can't hold
- **Status:** fixed · 2026-11-09 · uncommitted
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Spells/SpellFactory/ClassSpell.py`

15 spells (Dark Star, Fortune's Favor, Gift of Alacrity, Gravity Fissure, Gravity Sinkhole, Immovable Object, Magnify Gravity, Pulse Wave, Ravenous Void, Reality Break, Sapping Sting, Temporal Shunt, Tether Essence, Time Ravage, Wristpocket) have a school like 'Evocation (Dunamancy:Graviturgy)' or a class 'Wizard (Dunamancy)'. SpellRules.school is a School and classes are CharacterClass, so SpellClassConverter leaves them as JSON. Fix: a SpellRules note field (e.g. school_note='Dunamancy: Graviturgy', and the Dunamancy classes as a note too), shown on the card as the JSON shows it now.

**History**
- 2026-11-08 main-session: found
- 2026-11-09 main-session: marked fixed; SpellRules.school_note (Q15): the converter reads the note off the school, and 'Wizard (Dunamancy)' as Wizard with that note (the school's when it has none: Sapping Sting). The card shows the school as before. All 15 are classes now.

### DI-065 · 2014 spell records' "ritual": true is ignored, so 2014-only ritual spells don't show as rituals
- **Status:** fixed · 2026-11-09 · uncommitted
- **Area:** character-engine-dev
- **Where:** `CharacterContent/Spells/SpellFactory/DataSpell.py`, `CharacterContent/Spells/SpellClassConverter.py`

33 records in spells_dnd5e.json have "ritual": true but a casting time without 'or Ritual' (the 2014 card puts it after the name). Spell.is_ritual reads only the casting time (CastingTime.ritual), so a 2014-only ritual spell (one no 2024/aidedd record overrides) loses the Ritual tag on cards and in the combat UI; the converter's _IGNORED_KEYS drops the key with the comment that the casting time says it too, which is wrong for these. Fix: DataSpell.casting_time_spec sets ritual=True when the record's key does, and the converter keeps it (CastingTime(..., ritual=True)); expect snapshot changes for builds with such spells.

**History**
- 2026-11-08 main-session: found
- 2026-11-09 main-session: marked fixed; DataSpell.casting_time_spec is a ritual when the record's ritual key or a '(Ritual)' in its school says so, and the converter writes that. Ceremony and Skywrite (2014-only, converted before the fix) got ritual=True by hand; Wristpocket's school '(Ritual)' became its casting time. Three builds' sheets gained Ceremony's Ritual tag.

### DI-066 · Saving throws ignore cover's +2/+5 to Dexterity saves
- **Status:** fixed · 2026-11-09 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/saves.py:roll_save`

Cover.md: Half Cover gives +2 to AC and Dexterity saving throws, Three-Quarters Cover +5. attack_rolls.cover_bonus counts it in AC only; roll_save adds save_modifier alone, so a Fireball against a monster behind Half Cover rolls its DEX save 2 low, and the dialog's 'DEX +3' row doesn't show it. Fix: add cover_bonus to rolled DEX saves (and show it in _save_text); natural fit for plan step 3.3's D20Bonus, with cover as a modifier source.

**History**
- 2026-11-09 main-session: found
- 2026-11-09 combat-simulator: marked in-progress; Plan step 3.3: cover as a source of modifiers (ArmorClass and a D20Bonus on Dexterity saves)
- 2026-11-09 combat-simulator: marked fixed; Plan step 3.3 (R38), uncommitted in worktree agent-a30cb9221e9d3c056: COVER_RULES in Combat/Effects/modifiers.py gives each cover an ArmorClass and a D20Bonus on Dexterity saves (most protective only); roll_save adds it ('Half Cover: +2'), the dialog's row reads 'DEX +5 (cover)'.

### DI-071 · A monster's Concentration save rolled by the simulator ignores its modifiers (Bless's 1d4, Exhaustion's note)
- **Status:** fixed · 2026-11-10 · uncommitted
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/damage_mixin.py:431`

_roll_concentration (monsters_roll_concentration on) rolls random.randint(1, 20) + _con_save_mod(char) directly, bypassing save_plan/roll_save. Concentration is a Constitution saving throw, so Bless ("the target adds 1d4 to the attack roll or save") applies, and Exhaustion's -2/level note should show. Probe on the 3.3 worktree: a blessed Pirate concentrating on Bless, d20 10, CON +1, logged 'keeps concentration (DC 10, rolled 11)' with no 1d4. Fix: roll it with roll_save(char, 'CON', dc, 'Neutral') and log its note (Bless: +n (1d4)); the card's concentration check for a player could show the save_reminder too.

**History**
- 2026-11-10 code-reviewer: found
- 2026-11-10 combat-simulator: marked in-progress; Concentration roll through roll_save
- 2026-11-10 combat-simulator: marked fixed; Plan step 3.3, R40 (uncommitted, worktree agent-a30cb9221e9d3c056): _roll_concentration calls roll_save(char, 'CON', dc, 'Neutral', one_die_if_straight=True), so its modifiers count (Bless's 1d4 rolled after the d20, a mode, notes) and _settle_concentration adds the note to the keeps/loses line; a straight roll still throws one d20, so fights without bonuses roll the same dice.

## Won't fix

### DI-015 · UPDATE_SNAPSHOTS=1 under xdist corrupts shared golden JSON files
- **Status:** wontfix
- **Area:** tests
- **Where:** `tests/_combat_ui.py:check_golden`

run_tests.sh runs pytest with xdist workers; with UPDATE_SNAPSHOTS=1 each worker does load/modify/save on the same golden file (e.g. tests/snapshots/combat_ui_cards.json), so the writes race and leave truncated/garbled JSON (seen while fixing DI-009). Workaround: add -n0. Possible fix: lock the file in save(), or have run_tests.sh force -n0 when UPDATE_SNAPSHOTS is set.

**History**
- 2026-10-28 claude-main: found
- 2026-10-28 claude-main: marked wontfix; Duplicate of DI-010

### DI-032 · Player link server doesn't check the Host header (DNS rebinding)
- **Status:** wontfix
- **Area:** combat-simulator
- **Where:** `Combat/CombatUIQt/player_server.py:93`

A malicious website opened by someone on the same Wi-Fi could rebind its domain to the PC's address and read /state from their browser while the link runs. It would get only what the page already shows, and the server takes no input, so this adds nothing beyond the plan's accepted 'no login' decision. A Host check would also reject hostnames such as a Tailscale MagicDNS name. Revisit if /state ever carries anything private or the server starts accepting input.

**History**
- 2026-11-01 main-session: found
