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
| `--scenario <id>` | Play an encounter from its campaign's `encounters.py` (its log is set up from the config when it's opened). Its campaign is picked automatically |
| `--campaign <name>` | `curse_of_the_lich` (default), `time_loop_pr` or `grims_castle`. Used when there's no `--scenario` |
| `--player-log [<path>]` | Track the party across sessions. The player log lists where the party has been (encounters, rests); their HP, conditions and slots (and their allies') are replayed from the encounter logs since the last long rest. Who takes part in an encounter comes from `encounters.py`. A log in a campaign's `PlayerLogs/` picks that campaign; with no path, the campaign's own party log (`PlayerLogs/<party id>.json`) |
| `--rest long\|short` | `long`: record a long rest in the player log (the party is fully rested from then on; statistics still count what came before). `short`: open the healing window. Needs `--player-log` |
| `--difficulty` | Print the D&D 2024 encounter difficulty against the players taking part (allies' XP subtracted) and exit |

With no flags it runs the default campaign's first encounter. With only `--player-log` it opens the party between encounters (nothing is logged there): pick an encounter with Load Encounter, or rest.

**Campaigns and encounters** are configured in one file per campaign: `Combat/Campaigns/<C>/encounters.py` holds a `CONFIG` listing its party (imported character builder classes) and every encounter (imported monster and ally stat-block classes, who of the party takes part, description, difficulty note). The format is in [Combat/Campaigns/ENCOUNTERS.md](Combat/Campaigns/ENCOUNTERS.md). An encounter's log is an empty `{}` until the encounter is opened in the window, which sets it up from the config. After changing the config, check it (this empties the logs of fights not started yet):

```bash
python -m Combat.Tools.prepare_encounters --all            # check every config, empty every log not started
python -m Combat.Tools.prepare_encounters --check          # check only
```

**Common recipes** (`PL=Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json`)

```bash
python RunCombatSimulator.py --scenario ashelm_church                          # no party tracking
python RunCombatSimulator.py --scenario wrath_of_durmor --player-log $PL
python RunCombatSimulator.py --scenario goblin_warband_ambush --difficulty
python RunCombatSimulator.py --player-log $PL                                  # the party between encounters
python RunCombatSimulator.py --player-log $PL --rest long
python RunCombatSimulator.py --player-log Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json   # picks time_loop_pr
python RunCombatSimulator.py --campaign time_loop_pr --player-log                                   # the same
```

Exact per-campaign commands: [CurseOfTheLich](Combat/Campaigns/CurseOfTheLich/CHEATSHEET.md), [TimeLoopPR](Combat/Campaigns/TimeLoopPR/CHEATSHEET.md), [GrimsCastle](Combat/Campaigns/GrimsCastle/CHEATSHEET.md).
To add a campaign, create `Combat/Campaigns/<Name>/` with an `encounters.py` and a one-line `Campaign.py` (copy another campaign's), and register its `CAMPAIGN` in `Combat/Scenarios.py`.

Every encounter keeps its fight in its `CombatLogs/<id>.json`. When that log holds a fight in progress, the window asks **Continue Encounter** (pick up where it stopped) or **Restart Encounter** (set up again from the config, fight undone for the party; the old log is kept as `<id>_restarted_<timestamp>.json`).

**In the window:** **Load Encounter...** (the campaign's encounters with their description, players, monsters and how far each fight got; start, continue or restart one) · **End Encounter** (mark the fight ended in both logs and go back to the party between encounters) · **Short Rest...** / **Long Rest** (between fights, or before starting a loaded encounter) · **Roll for Monsters** / **Roll for All** / **Start Combat** (initiative, with a dialog for ties; Enter moves between the fields and starts the fight) · **+ Add Combatant** · **Next Combatant / Next Round** · **Undo Last Action** · **Cast Spell** / **Enable Feature** on a card · damage with **Apply** (type it as `12 fi` or `7 pi + 3 fi`; counts resistances; **Ignore Resist** applies the amount typed; **½ Saved** halves it; a Concentration save appears on the card) · the turn column (who's up and next, reminders, a monster's actions to click, the encounter log always open below them) · **Player Screen** (the turn order for a second screen) · **Player Link** (the same view on players' phones, see below) · **Settings** · **Encounter Log** · **Player Log** · **Statistics** · **Rules** · a turn timer (Start / Pause / Reset).

**Player Link:** a read-only live view of the fight for anyone on the same Wi-Fi, with no app, account or new package. The button starts a small web server inside the combat window and shows a link like `http://192.168.0.143:8765` to give the players, with **Copy** and an address list. If a phone can't connect, try another address: a VPN or a virtual adapter can take the top spot. A Tailscale address comes last, for players joining from home. Closing the dialog leaves the link running, and the button then reads **Player Link (on)**; **Stop** ends it. Nothing listens on the network until the button is clicked.

The page shows what the Player Screen shows (`Combat/CombatUIQt/player_view.py` decides): the round, the turn order, everyone's HP as a bar colored like the GM's cards, each combatant's size, AC and speed, and no hidden monsters. Under that, **Encounter log** opens what's happened so far, newest first: the latest round turn by turn, with damage and healing in a column of their own, and each earlier round folded to its totals until it's tapped. It only covers the fight itself, and leaves out lines that name a monster the players couldn't perceive at the time, plus a monster's private conditions, running effects, concentration and cover. Fights logged before this feature don't show their earlier lines. The page updates within a second or two, says "Lost connection" if it stops getting updates, and nothing on it can change the fight. Anyone on the Wi-Fi can open the link while it's running, and they see only what's on this page. Phones need the same Wi-Fi as the PC, with mobile data off. Guest networks often keep devices apart; a phone hotspot gets round that. [Notes/player-web-view-plan.md](Notes/player-web-view-plan.md) has the design and troubleshooting.

**Informative or Limited:** the **Players see** list in the Player Link dialog, or **Limited player view** in Settings, picks how much both the Player Screen and the link show. Informative, the default, is everything above. Limited is for players who'd rather know less about the monsters. Player characters' rows don't change, since players can tell each other all of that anyway. A monster's row shows its name, visible conditions, speed, the damage it has taken this encounter, a word for its health, what those and attack rolls have shown of its maximum HP and AC and what the log has shown of its resistances and immunities, with no current HP, size or the AC itself. The encounter log stays on the link in both views. The word goes Healthy (above 75% of max HP), Injured (above 50%), Bloodied (half or fewer), Dying (a quarter or fewer), Defeated (0 HP). The bar moves in steps with the word, and a monster's row never carries its exact HP. Damage taken goes up with each hit, stays put when the monster heals, and Undo takes it back. Each roll typed in the GM's Attack roll field narrows the AC down, since players know what they rolled and whether it hit: a miss on 10 reads AC > 10, a hit on 17 reads AC ≤ 17, both read 10 < AC ≤ 17, and only the best of what's known is kept. When a miss and a hit meet it reads AC = 11. A natural 20 or 1 shows nothing, as the AC played no part, and neither does a hidden attacker's roll. The notes are about the AC without cover, so they stay true when a monster leaves it. The word and the damage taken narrow the maximum HP down the same way, since players can do that sum themselves: 12 lost and Bloodied reads Max HP 17–24, as 16 would be Dying and 25 Injured, 12 lost and Healthy reads Max HP ≥ 49, each new word tightens it, and healing in the log comes off the sum. When it's pinned down it reads Max HP = 30. A hit on a hidden monster adds nothing, and neither does anything after temporary HP soaks damage, since the sum no longer matches the HP really lost and the note would be false. Resistances and immunities show the moment the log gives them away: a hit the log calls (resisted) adds Resists Fire, one it calls (immune) adds Immune to Fire, and an effect that fails with "is immune to Frightened" adds Immune to Frightened. Each is listed once, whichever way the hit went on a save. Ignore Resist shows nothing, as the log then says plain damage, and neither does a line players can't read. Petrified's own Resistance to all damage and Immunity to Poisoned add nothing either, since they say nothing about the monster. The choice is kept between runs, and players can't change it.

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
| `Combat/Campaigns/<C>/PlayerLogs/` | `main_party.json`, where the party has been (plus older `*_long_rest_<timestamp>.json` archives). Local, git-ignored |
| `Combat/Campaigns/<C>/encounters.py` | The campaign's party and encounters ([format](Combat/Campaigns/ENCOUNTERS.md)) |
| `Combat/Campaigns/<C>/CombatLogs/` | One log per encounter (`{}` until it's opened), with every event of its fight. Local, git-ignored, like the `*_restarted_*` backups |
| `Combat/Campaigns/<C>/player_statistics_report.html` | The campaign's player statistics report (git-ignored, like all `*.html`) |
| `Builds/GeneratedBuilds/` | Build files from the Character Creator GUI |
| `Guides/` | Static player guides (`ChoosingYourSpecies.html`, `ChoosingYourSubclass.html`), open directly |
| `tests/snapshots/` | Golden build stats and sheet hashes |

---

## 10. Claude Code agents and skills

Ask Claude Code to use an agent by name. Skills are shared know-how that agents preload, and you can also invoke them yourself (`/balance-monster`, `/verify-agent-work`, ...).

- **What exists:** [.claude/skills/agent-index/SKILL.md](.claude/skills/agent-index/SKILL.md) lists every agent (by domain folder, with model, preloaded skills, what it's for, and which agents it points to) and every skill (who preloads it, its scripts). It's generated from their frontmatter, so it's always current; Claude also consults it as the `agent-index` skill.
- **How it works:** [Notes/agent-workflow.md](Notes/agent-workflow.md).
