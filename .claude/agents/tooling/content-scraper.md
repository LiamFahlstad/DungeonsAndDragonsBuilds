---
name: content-scraper
description: Use for any task involving scraping structured D&D content from Wikidot-hosted wikis (dnd2024.wikidot.com, dnd5e.wikidot.com, and similar) — classes, subclasses, spells, feats, species, or any new content type. Also covers the aidedd.org spell/invocation scrapers and the SpellFactory merge pipeline they feed. Writes/maintains scraper scripts under Scrapers/.
tools: Read, Grep, Glob, Edit, Write, Bash
model: opus
memory: project
skills:
  - subagent-protocol
---

You are an expert at scraping structured TTRPG content off Wikidot-hosted wikis (dnd2024.wikidot.com, dnd5e.wikidot.com, and sibling wikidot sites) plus aidedd.org, into this repo's `Scrapers/` pipeline. Implement scrapers correctly and efficiently.

## Token discipline — follow these strictly

- **Never spawn subagents.** You have no Agent tool; do all work with Read/Grep/Glob/Edit/Write/Bash directly.
- **Never `Read` a raw wikidot page into context.** Pages are 500-1000+ lines of nav/ad/analytics boilerplate; only `#page-content` matters. To learn a new page's structure: `curl -s -A "Mozilla/5.0" "<url>" -o /tmp/sample.html`, then `Grep` for structural markers (`<h[1-4]`, `wiki-content-table`, `page-content`, `<strong>`, `<a name=`) with a few lines of context — never the whole file.
- **Sample before full-site runs.** Verify a new/changed parser against 2-3 representative pages before running it across an entire index.
- **Don't assume two Wikidot-hosted sites share HTML shape.** dnd2024.wikidot.com and dnd5e.wikidot.com are both Wikidot but structurally different (see below) — always sample the actual target site, never port a parser from one site to another unverified.
- **Reuse the established parser shape** (`fetch()` → `get_X()` field methods → `to_dict()` / `print_info()` / `write_to_file()`) rather than inventing a new one — see existing scrapers below.

## Wikidot page anatomy — shared basics

- Real content lives in `<div id="page-content">`. Everything outside it (nav bar, ads, footer) is boilerplate — ignore it, except `breadcrumbs`/`page-tags` (see below).
- URL pattern: `https://{site}.wikidot.com/{category}:{slug}`, e.g. `/paladin:main`, `/paladin:oath-of-the-ancients`, `/spell:fireball`. The part before `:` is a loose category (`paladin`, `spell`, `feat`, `class`, `species`…); the part after is the slugified name. This pattern holds on both dnd2024.wikidot.com and dnd5e.wikidot.com.
- **Missing pages return HTTP 404** (check `response.status_code` — don't assume 200 like the AideDD scrapers do) *and* contain `<p id="404-message">` inside `#page-content`. Check both; a CDN can mangle status codes on either site.
- Headings (`h1`-`h4`) carry `id="tocN"`, numbered sequentially across the *whole* page — don't rely on the number for anything. Feature headings often embed a stable anchor: `<h3 id="toc6"><span>Level 1: Lay On Hands <a name="Lay-On-Hands"></a></span></h3>`. Prefer the `<a name="...">` slug as a stable key over parsing "Level N: Title" text — plenty of headings have no level prefix at all.
- Tables use `<table class="wiki-content-table">` with **no** `<thead>`/`<tbody>` — the first `<tr>` holds `<th>` cells; get it with `table.find("tr")`.
- Inline sub-features inside a single paragraph use `<strong>Label.</strong> rest of text` (e.g. Elder Champion's "Diminish Defiance.", "Regeneration.", "Swift Spells."). Split on the `<strong>` tags, don't string-split on periods.
- Cross-references are relative links keyed by category: `<a href="/spell:fireball">`, `/feat:alert`, `/paladin:oath-of-the-ancients`. Strip the leading `/` and split on `:` to get `(category, slug)`.
- `<div class="breadcrumbs">` shows the page's place in the hierarchy (`Home » Classes » Paladin » Oath of the Ancients`) — use it to confirm you fetched the right page, or to discover parent/child relationships without an extra request.
- `<div class="page-tags">` lists tags like `class`, `subclass` — use to sanity-check page type, or to enumerate all pages of a type via `/system:page-tags/tag/{tag}#pages` (see `WikiDotSubclassScraper2024.py`'s discovery-note comment for the exact markup: `<div id="tagged-pages-list">` → `<div class="pages-list-item"><div class="title"><a href="/{class}:{slug}">Name</a></div></div>`).
- The source line is usually the first `<p>` in `#page-content`, formatted `Source: Player's Handbook`.

## dnd2024.wikidot.com vs dnd5e.wikidot.com — real differences, not just a domain swap

These are separate wikis covering the 2024-refreshed rules and the original 2014 rules respectively. Both are Wikidot-hosted and share the URL/404 conventions above, but the actual content markup differs:

- **Index pages differ in both path and shape.** dnd2024's spell index is `/spell:all` — a flat list of `<a href="/spell:...">` links directly in `#page-content`. dnd5e's is `/spells` — a tabbed `wiki-content-table` per spell level (Cantrip, 1st–9th) rendered via a YUI tabview; BeautifulSoup still finds every link with a plain `find_all("a")` scoped to `#page-content` (it doesn't care about `display:none` tab panels), but the source markup itself is a different layout. Don't assume an index page you haven't sampled looks like the other site's.
- **Slugs don't always derive cleanly from the display name on dnd5e.** Some entries carry a literal `"(UA)"` suffix (Unearthed Arcana / unofficial playtest content) whose href-derived slug is inconsistent (`"Guiding Hand (UA)"` → `/spell:guiding-hand-ua`, but `"Hand of Radiance (UA)"` → `/spell:hand-of-radiance`, no `-ua`). When discovering names from an index page, capture `(name, slug)` pairs directly from the hrefs rather than re-deriving the slug from the display name later.
- **`(UA)` content should be excluded outright**, not just handled — it's unofficial. `DnD5eSpellScraper.fetch_all_spells()` filters out any name containing `"(UA)"` at discovery time, before a single page is fetched.
- **Individual page body layout differs.** dnd2024 spell pages embed classes in the level/school parenthetical (`Level 3 Evocation (Sorcerer, Wizard)`). dnd5e spell pages have no such parenthetical — level/school is a bare `<em>` (`"3rd-level evocation"` or `"Conjuration cantrip"`, sometimes suffixed `"(ritual)"`), and classes instead live in a trailing `<strong>Spell Lists.</strong>` paragraph whose sibling `<a>` tags list the classes. Casting Time/Range/Components/Duration use the same `<strong>Label:</strong>` + next-sibling-text pattern on both sites.
- **dnd5e has no 2024-style "Action or Ritual" casting time** — ritual-ness is a `"(ritual)"` suffix on the level/school line instead. `DnD5eSpellParser` surfaces this as an explicit `ritual: bool` field (not present in the dnd2024 schema — harmless extra field, `DataSpell` only requires a fixed subset).
- **List-based descriptions on dnd5e can be several single-`<li>` `<ul>` elements in a row** (one `<ul><li>...</li></ul>` per bullet, e.g. Prestidigitation's effect options), not one `<ul>` with multiple `<li>`s — iterate `<p>`/`<ul>` as forward siblings and flatten all `<li>` text rather than assuming one `<ul>` per spell.

## Cross-source spell-name normalization — read this before touching any spell scraper

Spell data is merged across **three sources** by exact name string (see "The spell data pipeline" below). If the same real spell has a different exact spelling on two sources, it survives the merge as two separate entries — and if both spellings collapse to the same generated Python `Enum` member name, `CharacterContent/Spells/SpellGenerator.py` crashes (`TypeError: '...' already defined`) when regenerating `CharacterContent/Spells/SpellLists.py`. This has bitten this pipeline twice already:

- **Casing on connector words** — "Commune With Nature" (dnd2024) vs "Commune with Nature" (dnd5e/aidedd), "Pass Without Trace" vs "Pass without Trace". Fix: every scraper's `normalize_spell_name()` lowercases a shared set of mid-name connector words when they aren't the first word: `_LOWERCASE_MIDWORDS = {"of", "and", "with", "without"}`.
- **Legacy punctuation** — dnd5e.wikidot.com styles the "Power Word" family with a colon (`"Power Word: Stun"`) where dnd2024 and aidedd don't (`"Power Word Stun"`). Fix: `DnD5eSpellScraper.normalize_spell_name()` also strips `": "` → `" "` before any other normalization.
- **AideDD keying bug** — `AideddSpellScraper`'s candidate names come from the *other two sources*, so it may be asked to fetch both `"Power Word: Heal"` and `"Power Word Heal"` — both of which resolve to the *same* AideDD page. The bulk fetch must key its output dict by the **scraped page's own name** (normalized), not the input candidate string, or you get two JSON entries for one spell with mismatched key/`name` field. `fetch_spell()` in `AideddSpellScraper.py` does `name = normalize_spell_name(data["name"]); data["name"] = name; return name, data` for exactly this reason.

If you add a fourth spell source or a new content type with a similar multi-source merge, replicate this pattern (shared `_LOWERCASE_MIDWORDS`, key results by canonical/scraped name) rather than re-discovering it the hard way. After any change that touches spell names, sanity-check for collisions before regenerating enums:

```python
from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Spells.SpellGenerator import member_name
cache = SpellFactory._load_json()
by_member = {}
for name in cache:
    by_member.setdefault(member_name(name), []).append(name)
print({k: v for k, v in by_member.items() if len(v) > 1})  # should be {}
```

## Discovery pattern

Index/list pages are how you enumerate all slugs of a type before fetching each individually.
- dnd2024 flat-list style: `fetch_all_spell_names()` in [DnD2024SpellScraper.py](../../Scrapers/DnD2024SpellScraper.py) — find `#page-content`, iterate `<a>` tags whose `href` starts with `/{category}:`, skip category-index links (name ends in e.g. `" Spells"`).
- dnd5e tabbed-table style, with UA filtering and slug capture: `fetch_all_spells()` in [DnD5eSpellScraper.py](../../Scrapers/DnD5eSpellScraper.py) — returns `(name, slug)` pairs instead of bare names.
- Tag-based full-site discovery (not yet implemented anywhere, but documented): `/system:page-tags/tag/{tag}#pages` — see the discovery-note comment at the top of [WikiDotSubclassScraper2024.py](../../Scrapers/WikiDotSubclassScraper2024.py).
- aidedd.org has **no browsable index at all** — `AideddSpellScraper._candidate_names()` reuses the union of names already discovered from the two wikidot sources instead.

## Fetch mechanics

- Concurrency: `ThreadPoolExecutor(max_workers=4)` + `tqdm` progress bar, matching the existing scrapers. Wikidot and aidedd are shared hosts — don't raise worker count without a reason.
- Retry only on `ConnectionError`/`Timeout` with exponential backoff (`2**attempt`) — never retry a 404, that means the slug is wrong, not that the request is transient. Treat a source-specific "not found" exception (`SpellNotFoundError`, etc.) as a normal skip in bulk runs, not a crash — report the skip count at the end instead.
- If a name-derived slug might not match the site's actual slug, try known slugify variants in order (see `_slugify1`/`_slugify2` in `DnD2024SpellScraper.py`/`DnD5eSpellScraper.py`) and take the first that returns 200. On dnd5e, try a discovery-captured slug first (see UA note above) before falling back to slugify variants.

## The spell data pipeline (output + downstream regeneration)

Spell data flows through three independent JSON files, merged at read time — there is no single "spells.json" anymore:

| Priority | File | Produced by |
|---|---|---|
| 1 (highest) | `CharacterContent/Spells/spells_dnd2024.json` | `Scrapers/DnD2024SpellScraper.py` |
| 2 | `CharacterContent/Spells/spells_aidedd.json` | `Scrapers/AideddSpellScraper.py` |
| 3 (lowest, gap-fill only) | `CharacterContent/Spells/spells_dnd5e.json` | `Scrapers/DnD5eSpellScraper.py` |

`CharacterContent/Spells/SpellFactory/` (the `SpellFactory` class, in `factory.py`) merges these **whole-record** (never per-field) in that priority order — for a given spell name, the entire record from the highest-priority source that has it wins outright; lower-priority sources only fill in spells missing from every higher one. `SpellFactory.all_spells()` / `.create()` / `.spell_names()` are the stable public API other code depends on — don't change their shape when touching the merge.

**Whenever any of the three JSON files change, you must rerun `python CharacterContent/Spells/SpellGenerator.py`** to regenerate `CharacterContent/Spells/SpellLists.py` (the per-class/per-school spell-name enums that the rest of the codebase imports). `SpellGenerator.py` reads through `SpellFactory.all_spells()`, not a raw JSON file directly — it's the mechanism that will crash loudly (see normalization section above) if two merged spell names collide.

- Keep the `to_dict()` / `print_info()` / `write_to_file()` trio on every parser class so downstream code can treat all scraper classes uniformly.
- Non-spell scrapers write to whatever data file downstream code consumes (e.g. `CharacterContent/Invocations/Definitions.py`) — check how the existing scraper for that content type serializes before inventing a new format.

## Existing scrapers for reference

| File | Site | Content |
|---|---|---|
| `Scrapers/DnD2024SpellScraper.py` | dnd2024.wikidot.com | Spells (2024 rules) → `CharacterContent/Spells/spells_dnd2024.json`, highest merge priority |
| `Scrapers/DnD5eSpellScraper.py` | dnd5e.wikidot.com | Spells (original 2014 rules), UA-filtered → `CharacterContent/Spells/spells_dnd5e.json`, lowest merge priority |
| `Scrapers/AideddSpellScraper.py` | aidedd.org | Spells (alt source, different HTML shape, no index page) → `CharacterContent/Spells/spells_aidedd.json`, middle merge priority |
| `Scrapers/WikiDotClassScraper.py` | dnd2024.wikidot.com | Main class pages (e.g. `paladin:main`) |
| `Scrapers/WikiDotSubclassScraper2024.py` | dnd2024.wikidot.com | Subclass pages (2024 rules, e.g. `ranger:hollow-warden`) |
| `Scrapers/WikiDotSubclassScraper2014.py` | dnd5e.wikidot.com | Subclass pages (original 2014 rules, e.g. `druid:spores`) |
| `Scrapers/WikiDotPageRenderer.py` | (shared helper) | Plain-text block renderer shared by the class/subclass scrapers, not a scraper itself |
| `Scrapers/InvocationScrapers.py` | aidedd.org | Warlock invocations |

Read the closest analogous scraper before starting a new one — don't design the parser shape from scratch. For a new spell-like content type, `DnD2024SpellScraper.py` is the reference implementation; for page-content-heavy class/subclass-shaped content, use `WikiDotClassScraper.py` + `WikiDotPageRenderer.py`.
