---
name: new-content-check
description: Check for new 2024-rules content (2024 edition only, from dnd2024.wikidot.com; 2014 content is not covered yet) - classes, subclasses, species, feats, spells and tools - against a baseline index of everything the wiki listed last time, with each entry's status in this repo (have / scraped / todo / ignored) and the code, data or source-text file it maps to. A script fetches the wiki's index pages and reports what is new, removed or moved, and what changed status locally. Use whenever someone asks "is there new content?", "what's new on the wiki?", "are there new spells?", "what haven't we implemented yet?", before or after a scraping run, after implementing a subclass/species/feat or scraping spells (to mark it done), and when deciding what to scrape or build next, even if they don't say "baseline".
---

# New content check (2024 content)

**This covers 2024-rules content only**: [dnd2024.wikidot.com](https://dnd2024.wikidot.com/), `SubClasses2024`, `SubclassTexts2024`. The 2014 content (dnd5e.wikidot.com, `SubClasses2014`, `SubclassTexts2014`) is not checked yet. When it's added, it gets its own `baseline_2014.json` beside `baseline_2024.json` rather than sharing one, because the two wikis have different index pages and markup (see the `content-scraper` agent). Until then, don't read a missing 2014 subclass as "not on the wiki".

What the repo tracks for 2024, and where the wiki lists it:

| Category | Wiki index | Group comes from | Local code / source text |
|---|---|---|---|
| classes | `class:all` | tab (`General`) | `CharacterContent/Classes/BaseClasses/<Class>Base.py` / `SourceTexts/ClassTexts/<class>.txt` |
| subclasses | `system:page-tags/tag/subclass` (every page tagged *subclass*; `Scrapers/WikiDotSubclassScraper2024.py` scrapes them one by one) | the page's own `Source:` line | `CharacterContent/Classes/SubClasses2024/<Class><Name>.py` / `SourceTexts/SubclassTexts2024/<slug>.txt` |
| species | `species:all` | tab (Common, Eberron, Lorwyn, Ravenloft, Exotic) | `CharacterContent/Species/<Name>.py` / a line in `CharacterContent/Species/species.txt` |
| feats | `feat:all` | section and tab (`General Feats / Faerun`, `Dragonmark Feats / Dragonmarks`) | a `class <Name>(` under `CharacterContent/Features/` / a line in `origin_feats.txt` or `general_feats.txt` |
| spells | `spell:all` (tabbed by level, stored as `level`) | the page's own `Source:` line | the name is a key in `CharacterContent/Spells/spells_dnd2024.json` (spells are data, so that is `have`) |
| tools | `equipment:tool` (no page per tool: one row each in the Artisan Tool, Other Tool, Gaming Set and Musical Instrument tables, keyed `equipment:tool#<slug>`) | the table | a `name="..."` in `CharacterContent/ToolProficiencies/Proficiencies.py` |

Spell and tool names match ignoring case, curly apostrophes and the `Power Word: Stun` colon. A 2024 spell missing from `spells_dnd2024.json` is `todo` even when `SpellFactory` falls back to its 2014 text from `spells_dnd5e.json` (Catnap, Enervation, Power Word Pain, ...). New spells come from `Scrapers/DnD2024SpellScraper.py` (`content-scraper` knows the pipeline, including regenerating `SpellLists.py`).

**UA is left out entirely.** Every playtest page lives under `ua:` (`ua:class-psion`, `ua:subclass-fighter-hell-knight`), and the script drops those links before anything else, so UA never appears in the baseline or the report. When a UA subclass is printed it gets a normal page (`bard:college-of-spirits`), which shows up as NEW.

**Ignored** content: `ignore_groups` at the top of `baseline_2024.json` (now Lorwyn and Exotic). An entry is ignored only when *every* group it is listed under is ignored: Dhampir is under both Ravenloft and Exotic, so it is tracked. Lorwyn and Exotic subclasses would show up by their `Source:` line, so the source has to contain the word; the same goes for spells. A few Exotic origin feats are implemented anyway; they read `"status": "have", "reason": "Exotic"`.

## The baseline is the index

[baseline_2024.json](baseline_2024.json) holds one line per wiki entry, sorted by category and name:

```json
{"name": "Sorrow Knight", "page": "fighter:sorrow-knight", "class": "Fighter", "source": "D&D Beyond Drops - October 2026", "status": "todo"}
```

| status | meaning |
|---|---|
| `have` | implemented: `code` points at the file |
| `scraped` | source text is in the repo (`text`) but there is no code yet |
| `todo` | tracked, neither scraped nor implemented |
| `ignored` | excluded by a config rule; `reason` says which |

To answer "what do we have?" or "what's missing?", grep it rather than running anything: `grep '"todo"' .claude/skills/new-content-check/baseline_2024.json`. The status is worked out by naming rules (the table above), so after a rename that breaks a rule, an implemented entry falls back to `todo`. Fix the rule in `LocalIndex` rather than hand-editing the status, because `--update` recomputes it.

## Run the check (needs network, about 5 s)

The `Source:` lines of subclasses and spells are stored in the baseline, so a run only fetches pages for entries it hasn't seen. A run against an empty baseline, or after adding a category, fetches every page once (about a minute for the spells).

```bash
python .claude/skills/new-content-check/check_new_content.py            # diff the wiki against the baseline
python .claude/skills/new-content-check/check_new_content.py --todo     # also list every tracked entry with no code
python .claude/skills/new-content-check/check_new_content.py --update   # accept: rewrite baseline_2024.json
```

Per category it prints counts, then:

- **NEW (tracked)**: on the wiki, not in the baseline, not ignored. This is new content. For a new subclass or spell the script fetches its page once to read the `Source:` line.
- **NEW (ignored)**: new, but in Lorwyn or Exotic. Mention it; there's nothing to do.
- **REMOVED from the wiki**: in the baseline, gone from the index. Usually a renamed page (look for a NEW entry with a similar name) or one moved to another section.
- **MOVED**: the tab or `Source:` line changed, e.g. an Exotic feat moved to Common. That can turn an ignored entry into a tracked one.
- **LOCAL STATUS changed**: the repo changed since the baseline, e.g. `todo -> have` after someone implemented it.

Exit status is 1 when anything tracked is new, removed or moved, else 0.

## After a run

1. **Report** what's new (name, page, source/group) to the user. Don't scrape or implement anything unless asked.
2. **Scraping**: subclass text via `python Scrapers/WikiDotSubclassScraper2024.py <class:slug>` (writes `SourceTexts/SubclassTexts2024/`). New spells via the spell pipeline (`content-scraper`). A new kind of index or page is `content-scraper` work too.
3. **Implementing**: a new subclass goes to `subclass-implementer`, which takes the scraped text; species and feats go to `character-engine-dev`; a new tool to `equipment-inventory`. Apply the CLAUDE.md rules: a 2014 subclass with a 2024 reprint is not added, and so on.
4. **Accept** with `--update` once the user has seen the report, so the next run only shows what is newer. Commit `baseline_2024.json` with the work that changed it.

Changing what's ignored (say, start tracking Lorwyn): edit `config` in `baseline_2024.json`, then run `--update`. The statuses are recomputed for every entry.
