# HowTo: Cheat Sheet

Everything you can run in this repo. All commands are run from the **repo root**.
Generated `*.html` files are git-ignored.

```bash
pip install -r requirements.txt                 # core: attrs, PyQt6, pytest
pip install beautifulsoup4 requests tqdm        # only for scrapers
```

---

## 1. Character sheets: `RunCharacterCreator.py`

```bash
python RunCharacterCreator.py                       # every build registered in BuildSelector
python RunCharacterCreator.py --example             # every build in Builds/Examples/ instead
python RunCharacterCreator.py --feature-tags --probability-tables
```

| Flag | Effect |
|---|---|
| `--example` | Build all of `Builds/Examples/` (auto-discovered) instead of the registered builds |
| `--feature-tags` | Show tag chips (action/bonus/reaction, duration, range, save DC, Damage/Heal/…) next to features. The Passive tag is always shown |
| `--source-text` | Print the raw rules text instead of the improved descriptions |
| `--probability-tables` | Add tables of success chances for save DCs, spell attacks and weapon attacks |

**Output:** `Output/<class>_<subclass>_<name>/` (prefixed with `example_` for examples), plus `Output/_blank_template/`.

---

## 2. Create or edit a build

| Want to… | Do |
|---|---|
| Build a character in a GUI | `python RunCharacterCreatorUI.py` → **Preview code** / **Generate** writes `Builds/GeneratedBuilds/<Name>.py` |
| Tweak an existing build in the GUI | `python RunCharacterCreatorUI.py --load-build Builds/Characters/<File>.py` (or the **Load build…** button) |
| Write one by hand | Copy `Builds/Examples/_TEMPLATE.py` → `Builds/Characters/<Name>.py` and follow the TODOs |
| Include it in `RunCharacterCreator.py` | Import the module and add `"<Name>": <Module>.<Class>` to `BuildSelector.builds()` |
| Add an example build | Drop it in `Builds/Examples/`. `--example` picks it up automatically |

Notes: the GUI tabs are Basics / Level features / Equipment / Advanced. Multiclass builds aren't supported in the GUI yet.

---

## 3. Party & item sheets

```bash
python RunBuildGroups.py                 # joint features/spells/items/weapons pages for the party
python RunBuildGroups.py --level 4       # only features/spells gained at level 4
python RunBuildGroups.py --level 4-6     # inclusive level range
python RunItemSheets.py                  # every *_item_sheet() function in Builds/ItemSheets/
```

| Script | Output |
|---|---|
| `RunBuildGroups.py` | `Output/BuildGroups/Players (not Obmar)[_levelN]/`. The group is hardcoded to Curse of the Lich's party minus Obmar |
| `RunItemSheets.py` | `Output/ItemSheets/…`. To add a sheet, add a function ending in `_item_sheet` to a module in `Builds/ItemSheets/` |

---

## 4. Combat simulator: `RunCombatSimulator.py`

| Flag | Effect |
|---|---|
| `--scenario <name>` | Run an encounter. Its campaign is picked automatically |
| `--campaign <name>` | `curse_of_the_lich` (default), `time_loop_pr` or `grims_castle`. Used when there's no `--scenario` |
| `--player-log <path>` | Track the party across sessions. The player log lists where the party has been (encounters, adventures, rests); their HP, conditions and slots are replayed from those encounter logs since the last long rest |
| `--log <path>` | Use this encounter log instead of the scenario's own `CombatLogs/<scenario>.json` (the default) |
| `--absent NAME …` | Leave players out this session (case-insensitive partial match). Needs `--player-log` |
| `--rest long\|short` | `long`: record a long rest in the player log (the party is fully rested from then on; statistics still count what came before). `short`: open the healing window. Needs `--player-log` |
| `--difficulty` | Print the D&D 2024 encounter difficulty (allies' XP subtracted) and exit |

With no flags it runs the default campaign's first scenario. With only `--player-log` it runs an out-of-combat "adventure" session.

**Scenarios**

| Campaign | Scenarios |
|---|---|
| `curse_of_the_lich` | `ashelm_church`, `goblin_scouting_party`, `goblin_warband_ambush`, `wrath_of_durmor` |
| `time_loop_pr` | `time_loop_pr_outside_the_gates`, `time_loop_pr_drunk_oxe`, `time_loop_pr_square` |
| `grims_castle` | `grims_castle_bull` (four placeholder players join as allies, no character sheets) |

**Common recipes** (`PL=Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json`)

```bash
python RunCombatSimulator.py --scenario ashelm_church                          # no party tracking
python RunCombatSimulator.py --scenario wrath_of_durmor --player-log $PL --absent Gabriel Obmar Thum
python RunCombatSimulator.py --scenario goblin_warband_ambush --player-log $PL --difficulty
python RunCombatSimulator.py --player-log $PL                                  # adventure session
python RunCombatSimulator.py --player-log $PL --rest long
python RunCombatSimulator.py --campaign time_loop_pr --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json
```

Exact per-campaign commands: [CurseOfTheLich](Combat/Campaigns/CurseOfTheLich/CHEATSHEET.md), [TimeLoopPR](Combat/Campaigns/TimeLoopPR/CHEATSHEET.md), [GrimsCastle](Combat/Campaigns/GrimsCastle/CHEATSHEET.md).
To add a campaign, create `Combat/Campaigns/<Name>/` (`Players.py`, `Encounters.py`, `Campaign.py`) and register its `CAMPAIGN` in `Combat/Scenarios.py`.

Every scenario keeps its fight in `CombatLogs/<scenario>.json`, created on first use. When that log holds a fight in progress, the window asks **Continue Encounter** (pick up where it stopped) or **Restart Encounter** (fresh monsters; the old log is kept as `<scenario>_restarted_<timestamp>.json`).

**In the window:** **Load Encounter...** (switch to another of the campaign's scenarios, showing how far each fight got, and continue or restart it; the party stays) · **End Encounter** (mark the fight ended in both logs; the party carries on in an adventure session) · **Short Rest...** / **Long Rest** (between fights, or before starting a loaded encounter) · **Roll for All** / **Start Combat** (initiative, with a dialog for ties) · **+ Add Combatant** · **Next Combatant / Next Round** · **Undo Last Action** · **Cast Spell** / **Enable Feature** on a card · damage with **Apply (Check Resist)** (concentration checks pop up automatically) · **Encounter Log** · **Player Log** · **Statistics** · **Rules** · a turn timer (Start / Pause / Reset).

**In-app keyboard shortcuts** (full list: [KEYBOARD_SHORTCUTS.md](Combat/CombatUIQt/KEYBOARD_SHORTCUTS.md))

| Key | Action | Key | Action |
|---|---|---|---|
| `Enter` | Next turn | `Space` | Select active combatant |
| `N`/`P` or `→`/`←` | Next/prev source | `Shift+N`/`Shift+P` or `↓`/`↑` | Next/prev target |
| `D` / `H` / `T` | Focus Damage / Heal / Temp HP | `A` / `B` / `R` | Log Action / Bonus / Reaction |
| `1`–`9` | Cast spell slot of that level | `C` / `Ctrl+C` | Add / remove Concentrating |
| `Ctrl+Shift+C` | Clear target conditions | `Ctrl+N` | Add combatant |
| `Ctrl+Z` | Undo | `Esc` | Clear selection |
| `Ctrl+O` | Load encounter | | |

**Statistics**

Every action logged in the window feeds the battle statistics, in five categories: **Damage** (dealt and taken, in total and per damage type), **Healing** (healing and temp HP, given and received), **Conditions** (given and received, per condition), **Spells** (slots used per level, casts per spell) and **Outcomes** (knockouts, times downed, deaths).

- **In the window:** the **Statistics** button has an *Encounter* tab per category (this fight, every combatant) and a *Players* tab per category (the tracked party's lifetime totals; needs `--player-log`).
- **As a report:** one standalone HTML page per campaign with the party's lifetime totals, bar charts and the full breakdown tables. Pick the campaign with `--campaign` (default `curse_of_the_lich`).

```bash
python -m Combat.Tools.create_player_statistics_report                         # Curse of the Lich
python -m Combat.Tools.create_player_statistics_report --campaign time_loop_pr
python -m Combat.Tools.create_player_statistics_report --log <log.json> --output report.html
```

The report goes to `Combat/Campaigns/<C>/player_statistics_report.html`. Lifetime totals, in both the window and the report, cover every session: every encounter log the player log lists, plus the sessions older long rests archived to `main_party_long_rest_*.json`. A campaign without a player log yet (Grim's Castle) has nothing to report.

---

## 5. Monster tools (`Combat/Tools/`)

| Command | What it does |
|---|---|
| `python Combat/Tools/monster_score.py "Name" ["Name" …] [-v]` | Power score relative to the monster's own CR (0.5 = average). `-v` prints the breakdown per stat. Homebrew target is 0.4–0.6 |
| `python Combat/Tools/monster_cr_compare.py "Name" … [-v]` | Implied CR plus the delta from the assigned CR, so monsters at different CRs can be compared. `-v` prints the score at every CR |
| `python -m Combat.Tools.generate_monster_cr_distributions` | → `Combat/Tools/monster_cr_distributions.html` (stat distributions per CR plus a power leaderboard) |
| `python -m Combat.Tools.generate_monster_cr_compare` | → `Combat/Tools/monster_cr_compare.html` (sortable implied-CR table of official monsters) |
| `python Combat/Tools/scrape_monsters.py` | Scrape aidedd.org → `Combat/monsters_raw.json` (needs the scraper deps) |
| `python -m Combat.Tools.generate_monsters` | Regenerate `Combat/Monsters/CR_*/monsters.py` from the raw JSON. ⚠ Overwrites unmarked generated files |
| `python -m Combat.Tools.migrate_monster_enums` / `…_speed_type` / `…_creature_type` | One-time source migrations. They skip files already migrated |

Hand-made monsters go in `Combat/Monsters/CR_<x>/monsters_homebrew.py`.

---

## 6. Content generators & scrapers

**Spells pipeline:** scrape → merge → regenerate enums/compendium

| Command | Output |
|---|---|
| `python Scrapers/DnD2024SpellScraper.py` | `CharacterContent/Spells/spells_dnd2024.json` |
| `python Scrapers/DnD5eSpellScraper.py` | `CharacterContent/Spells/spells_dnd5e.json` |
| `python Scrapers/AideddSpellScraper.py` | `CharacterContent/Spells/spells_aidedd.json` (for names already in the two files above) |
| `python -m CharacterContent.Spells.SpellGenerator` | Regenerates `CharacterContent/Spells/SpellLists.py`. **Run after any spell JSON change** |
| `python Presentation/SpellCompendium.py` | `CharacterContent/Spells/AllSpells.html` (every spell, grouped by level) |

**Source texts & handouts**

| Command | Output |
|---|---|
| `python Scrapers/WikiDotSubclassScraper2024.py [class:slug …]` | `SourceTexts/SubclassTexts2024/` (e.g. `paladin:oath-of-the-ancients`). Without arguments it uses the built-in list |
| `python Scrapers/WikiDotSubclassScraper2014.py [class:slug …]` | `SourceTexts/SubclassTexts2014/` (e.g. `druid:spores`) |
| `python Scrapers/FetchSubclassRoster2014.py` | Fetches every subclass listed in `Scrapers/subclasses2014.txt` into `SourceTexts/SubclassTexts2014/` |
| `python Scrapers/WikiDotClassScraper.py [class:main …]` | `SourceTexts/ClassTexts/` |
| `python Scrapers/InvocationScrapers.py` | Regenerates `CharacterContent/Invocations/Definitions.py` |
| `python Scrapers/GenerateClassHandouts.py` | `Output/ClassHandouts/index.html` + one page per 2024 class |
| `cd CharacterContent && python Features/FeatureGeneration/GenerateFeatures.py` | Turns `Input.txt` ("Level N: Name" + text) into Feature class stubs in `Output.py` |

---

## 7. Small demos (hardcoded inputs, edit the `__main__` block)

| Command | Prints / writes |
|---|---|
| `python -m Combat.EncounterDifficulty` | Sample 2024 difficulty calculation plus sanity checks |
| `python -m Utils.DamageCalculator` | `damage_report.txt`: hit and damage odds for one attack profile |
| `python -m CharacterContent.Spells.SpellFactory.Factory` | One spell's merged description ("Fireball") |
| `python -m CharacterContent.Invocations.InvocationFactory` | One invocation's description |

---

## 8. Dev: tests, formatting, type checking (Git Bash / WSL)

```bash
./run_tests.sh                         # all tests (args are passed to pytest)
./run_tests.sh -k builder -x -q        # filter, stop at first failure, quiet
./run_tests.sh tests/test_feats.py     # one file
./run_tests.sh -m slow                 # opt-in full order-invariance matrix
UPDATE_SNAPSHOTS=1 ./run_tests.sh tests/test_build_snapshots.py   # accept new golden snapshots (add -k <build> to limit)
SNAPSHOT_DUMP_DIR=/some/dir ./run_tests.sh tests/test_build_snapshots.py   # also dump rendered pages (for diff -r)
./format.sh            # Black, in place      |  ./format.sh --check   # report only
./format_changed.sh    # Black on changed .py files only (FILE... for specific files, --check to report)
./format_changed.sh --staged   # format the staged .py files and re-stage them (what the git-commit agent runs)
./typecheck.sh         # pyright, whole repo  |  ./typecheck.sh Model  # one folder
```

---

## 9. Where things land

| Path | Contents |
|---|---|
| `Output/<build>/` | Character sheets (`character.html`, features/, spells, items) |
| `Output/BuildGroups/`, `Output/ItemSheets/`, `Output/ClassHandouts/` | Party, item and handout pages |
| `Combat/Campaigns/<C>/PlayerLogs/` | `main_party.json`, where the party has been (plus older `*_long_rest_<timestamp>.json` archives) |
| `Combat/Campaigns/<C>/CombatLogs/` | Encounter logs with every event: one per scenario, plus `adventure_*.json` / `short_rest_*.json` (committed; only `*_restarted_*` backups are git-ignored) |
| `Combat/Campaigns/<C>/player_statistics_report.html` | The campaign's player statistics report (git-ignored, like all `*.html`) |
| `Builds/GeneratedBuilds/` | Build files from the Character Creator GUI |
| `Guides/` | Static player guides (`ChoosingYourSpecies.html`, `ChoosingYourSubclass.html`), open directly |
| `tests/snapshots/` | Golden build stats and sheet hashes |

---

## 10. Claude Code agents and skills

Ask Claude Code to use an agent by name. Skills are shared know-how that agents preload, and you can also invoke them yourself (`/balance-monster`, `/verify-agent-work`, ...).

- **What exists:** [.claude/skills/agent-index/SKILL.md](.claude/skills/agent-index/SKILL.md) lists every agent (by domain folder, with model, preloaded skills, what it's for, and which agents it points to) and every skill (who preloads it, its scripts). It's generated from their frontmatter, so it's always current; Claude also consults it as the `agent-index` skill.
- **How it works:** [Notes/agent-workflow.md](Notes/agent-workflow.md).
