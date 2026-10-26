---
name: dnd-spell-improved-descriptions
description: Use to write, audit or fix improved descriptions for D&D spells — each spell's full rules restructured into the Flavor/Facts/Table/Option blocks that spell cards render (the spell-side counterpart of Feature.get_improved_description()). Writes JSON into the companion `spells_<source>_improved.json` beside the source the SpellFactory actually loads (spells_dnd2024.json or spells_dnd5e.json, under CharacterContent/Spells), keyed by spell name; never edits a source JSON. Give it a level/class/spell-name filter ("all level 5 spells", "Cleric spells of level 1-3", "audit the level 2 entries"). Not a summary — for 1-2 sentence versions use dnd-spell-summaries; for usage_tags use dnd-spell-usage-tags; for Feature classes use dnd-builds.
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
---

You restructure D&D 5e spell descriptions so a player can read them at a glance at the table — **without losing or changing a single rule**. The spec is `CharacterContent/Spells/IMPROVED_DESCRIPTIONS.md`; read it first. This file is how to apply it, and the mistakes earlier passes made so you don't repeat them.

Your three goals, in priority order:
1. **Nothing lost, nothing changed.** Every rule, number, qualifier and exception of the source survives, worded as precisely as the source words it.
2. **Readable at a glance.** Labeled rows for what's looked up mid-combat; options and tables for choices; short rows.
3. **Clear.** Plain structure, labels a player understands, no invented prose.

## 1. Pick the spells, and the file each entry goes in

Sources merge **whole-record**, priority `spells_dnd2024.json` > `spells_aidedd.json` > `spells_dnd5e.json`. An entry must go in the improved file of the source that *wins* for that spell, or it's silently never shown (and the tests fail). List the work with:

```bash
PYTHONPATH=. python - <<'EOF'
import json
from CharacterContent.Spells.SpellFactory import SpellFactory as F
srcs = {p: json.load(open(p, encoding="utf-8")) for p in F.json_paths}
LEVEL = 5  # or filter on classes / names
for name in sorted(F.spell_names()):
    s = F.create(name)
    if s.level != LEVEL: continue
    win = next(p for p in F.json_paths if name in srcs[p]).split("/")[-1]
    done = s._data.get("improved_description") is not None
    print(f"{win:22} {'done' if done else 'TODO':5} {'EMPTY' if not s.description.strip() else '':6} {name}")
EOF
```

In practice entries land in `spells_dnd2024_improved.json` (2024 wording) and `spells_dnd5e_improved.json` (2014 wording). Skip spells that already have an entry unless asked to redo them.

## 2. Read the source text — and check it's whole

Print each spell's `casting_time | range | duration | components | source` and full `description` (use `PYTHONIOENCODING=utf-8`; the data has `�`/curly-quote characters — read them as apostrophes). The scraped data has known defects; look for each:

- **Empty description** (seen: Glyph of Warding, Forbiddance in dnd2024): `spells_aidedd.json` usually has the same 2024 text — write the entry from that and say so. Never fill a 2024 spell from the 2014 text.
- **Truncated text** (seen: Sticks to Snakes starts mid-thought; Shield's casting time is cut off): write what's there; for missing opening rules add a row like `["Missing text", "The opening of this spell's text (...) isn't included in this spell's data"]`. A truncated *trigger* you know with certainty (Shield's Magic Missile) may be completed in a Trigger row.
- **A table the text refers to but doesn't include** ("consulting the table below", "Roll on the following table"): check aidedd first (it had Confusion's). Otherwise add it only if you know it exactly (done before: Chaos Bolt d8 types, Augury omens, Summon Lesser Demons d6) **and flag it in your report**; if not certain, add a row saying the table isn't included (Nathair's Mischief, Spellfire Storm).
- **Junk lines** ("Range: …", "Components: …", "Spell Lists: …" inside a description): ignore them.

## 3. Layout

Blocks: `{"facts": [[label, value], ...]}`, `{"table": {"columns": [...], "rows": [[...]]}}`, `{"option": {"name": ..., "blocks": [...]}}`, `{"paragraph": "..."}`. Options don't nest.

**Opening**
- **Flavor row first**, when the source has flavor (how the magic looks/sounds/feels or where it comes from: "A frigid beam of blue-white light streaks toward…", "Invoking Hadar…", "the single chime of a dolorous bell"). Quote it **verbatim** — whole sentence(s), or just the clause when the rest is rules ("the target's skin assumes a bark-like appearance"). Only capitalize the first letter and end with a period. A test checks every Flavor row is verbatim.
- **No Flavor → a plain lead** paragraph, or none if the rows say it all. Never put imagery in a lead that the source lacks ("Divine power fills your weapon attacks", "grow drowsy", "climb like a spider" were all invented and had to be removed).
- A rule that appears in the flavor sentence still gets its own row (Magic Missile: `["Darts", "Three"]`; Shillelagh: `["Weapon", "A Club or Quarterstaff you are holding"]`) — readers skim past flavor.

**Rows** — standard labels: Target / Targets, Area, Attack ("Ranged spell attack"), On a hit, Save, Failed save, Successful save, Repeat save, Trigger, Healing, Effect, Ends early, Escape, Appears, Disappears.
- Save rows name the ability only ("Wisdom", or "Dexterity, made by each creature in the area"); the DC is on the sheet's Spellcasting headline.
- **Save-or-nothing is explicit**: add `["Successful save", "No damage"]` / `"No effect"` when the source only says "must succeed or…".
- Half-damage saves: a two-column table `Failed save | Successful save` (helper `SAVES`). Keep the source's "Half as much damage **only**" when it says "only".
- Don't repeat the card's quick-stats (level, school, casting time, range, duration, components, Concentration, Ritual) — but do spell out a reaction's trigger and an area's shape.
- Keep labels short (~15 chars; the label column is narrow). Split any value over ~200 characters into two labeled rows.

**Structure**
- A choice with several rules of its own → one Option per choice (Alter Self's forms, Control Water's effects, Guardian of Nature's forms).
- Many one-line choices → one Table, a row each, with a `Lasts` column when durations differ (Prestidigitation, Command, Mordenkainen's Private Sanctum).
- Three or more failed-save effects → a `Failed Save` Option with one row per effect (Wardaway, Tasha's Mind Whip).
- Several end conditions → a `The Spell Ends If` Option (Compelled Duel, Warding Bond).
- Duration/bonus/damage changing by slot → a Table inside the upcast Option (Bestow Curse, Hex, Magic Weapon, Shadow Blade).
- **Upcasting** last, in an Option named **exactly** as the source's heading: `Using a Higher-Level Spell Slot` (2024) or `At Higher Levels` (2014) — also when the heading has a colon or no period. The tests require it, and scrolls drop that Option by name.
- **Cantrip scaling**: Option `Cantrip Upgrade` (2014 text: `At Higher Levels`) holding a `Character level` table with rows 1, 5, 11, 17.
- A paragraph starting with a short phrase + "." or ":" gets that phrase auto-bolded; write leads as plain sentences.

**Summons** (Summon Beast/Fey/Undead/Aberration/Construct/Elemental, Find Steed, Giant Insect…): Facts `Appears`, the choice (Environment/Mood/Form/Element…), `Stat block: X (below)`, `Disappears`; an Option `Combat` (Allegiance, Initiative, Commands); an Option named after the creature with its stat block as rows (Type, AC, Hit Points, Speed, Abilities, Resistances/Immunities, Senses, Languages, then each trait/action — qualifiers like "Slaad only." first); and the upcast Option `Stat block: Use the spell slot's level for the spell's level in the stat block`.
- Take stat blocks from `Combat/Monsters/CR_0/monsters.py` (`grep -n 'combatant_type="<Name>"'`). That scrape **lost the per-level AC/HP formulas** (`hp=0`, odd `hp_formula`) and sometimes garbles `speed_special_rules` — rebuild AC/HP from the rules only if you're certain, and **list those lines in your report** for the user to verify.
- No stat block in the repo → `["Stat block", "<Name> (not included in this spell's data)"]`. Never write a whole stat block from memory.

## 4. Wording is rules

Earlier passes made all of these mistakes; each had to be fixed later.

- **Optional stays optional.** "You *can* take a Magic action to move it" → keep "you can". A bare `Move: Magic action: move it` reads as mandatory. This was the single most common error (Hex, Hunter's Mark, Heat Metal, Spiritual Weapon, Moonbeam, Enemies Abound, Animate Dead…). Likewise "it *can* deal 2d8 damage", "*can* repeat the save", "you *can* issue a general command", "you *must* cast this spell again".
- **Keep limiting words**: only, until, unless, instead, immediately, automatically, willingly, up to, at least, no larger than, of your choice, that you can see, other than, the first time, once per turn, either way.
- **Keep defined terms and referents.** "Can't be possessed or gain the Charmed condition" ≠ "Immune to" (Immunity is a rule term). "within 30 feet of the target" ≠ "of the last one". "Extra damage *from* the attack" ≠ "*to* the attack". "a spectral *force*" stays "force".
- **Don't reword source text for presentation** — not to avoid a damage-type word being colored ("fire", "force" are colored on cards wherever they appear; that's fine), not to "tidy" an example. Only your own lead sentence is yours to phrase.
- **No other edition's text** — no 2014 flavor on a 2024 spell (a lead once borrowed Fear's 2014 line). No rules the source lacks.
- **2014 entries keep 2014 terms**: "1 action", "bonus action", "weapon attack roll", "opportunity attacks", "slot level above 1st", "your spell DC" if the source says so. Capitalize defined terms for consistency (Prone, Restrained, Disadvantage, damage types) — that changes nothing.
- Fix only obvious scrape typos (stray " .", "spells ends"); everything else stays as written.

## 5. Write the entries

Write a script in your scratchpad and run it from the repo root. Use these helpers — they merge into the improved file and keep its compact, diff-friendly layout (sorted keys, one row per line):

```python
import json, os
def P(t): return {"paragraph": t}
def F(*rows): return {"facts": [list(r) for r in rows]}
def T(cols, *rows): return {"table": {"columns": list(cols), "rows": [list(r) for r in rows]}}
def O(name, *blocks): return {"option": {"name": name, "blocks": list(blocks)}}
def SAVES(failed, succeeded="Half as much damage"):
    return T(("Failed save", "Successful save"), (failed, succeeded))

def _fmt(block, ind):
    pad = " " * ind; ((k, v),) = block.items(); d = lambda x: json.dumps(x, ensure_ascii=False)
    if k == "paragraph": return pad + d(block)
    if k == "facts": return pad + '{"facts": [\n' + ",\n".join(pad + "  " + d(r) for r in v) + "\n" + pad + "]}"
    if k == "table": return (pad + '{"table": {"columns": ' + d(v["columns"]) + ', "rows": [\n'
                             + ",\n".join(pad + "  " + d(r) for r in v["rows"]) + "\n" + pad + "]}}")
    return (pad + '{"option": {"name": ' + d(v["name"]) + ', "blocks": [\n'
            + ",\n".join(_fmt(b, ind + 2) for b in v["blocks"]) + "\n" + pad + "]}}")

def merge(path, new, replace=()):
    data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    clash = (set(new) & set(data)) - set(replace)
    assert not clash, f"already written: {clash}"
    data.update(new)
    text = "{\n" + ",\n".join(f"  {json.dumps(n, ensure_ascii=False)}: [\n"
                               + ",\n".join(_fmt(b, 4) for b in data[n]) + "\n  ]" for n in sorted(data)) + "\n}\n"
    assert json.loads(text) == data
    open(path, "w", encoding="utf-8").write(text)
```

For edits to existing entries, load the JSON, change the specific rows (assert the old text first, so a stale edit fails loudly), and `merge(path, changed, replace=set(changed))`. Never hand-edit large spans of the JSON, and never run repo-wide scripted edits that could touch `.claude/worktrees/`.

## 6. Verify — every time, before reporting

1. `python -m pytest tests/test_spell_improved_descriptions.py -q` — entries are in the right file, render, keep upcast/Cantrip Upgrade Options, Flavor rows are verbatim and first.
2. **Coverage check**: for each new entry, every die expression (`\d*d\d+`), every number followed by a unit (feet, pounds, hours, minutes, miles, words, percent…) and every rules term in the source (conditions, damage types, abilities, skills, creature types, area shapes, action types, "willingly", "automatically", "Concentration", "Long Rest", …) must appear in the entry (case-insensitive). Investigate every miss.
3. **Qualifier audit**: count, in the source (upcast paragraph excluded) and in the entry (upcast Option excluded), these patterns: `can't|cannot`, `doesn't|don't`, `isn't|aren't`, `only`, `unless`, `instead`, `willing(ly)`, `can see`, `your choice|you choose`, `up to`, `at least`, `no (more|larger) than`, `automatically`, `immediately`, `other than`, `first time`, `start of`, `end of`, `until`, `can <verb>` (not "can see/be"), `either`, `once`. Where the entry has fewer, print the source sentences and judge each: fine only if the rule clearly survives in another shape (a "Ends early" row for "until", "not pushed" for "isn't pushed").
4. **Reverse check**: no die or number in an entry that the source lacks (allowed: stat-block lines from the repo, tables you flagged, the trigger range from the casting-time field).
5. **Lead-in check**: `Presentation.Html.bold_lead_in(text)` must return None for every paragraph.
5b. **Flavor-only rules check** (the level 5 pass missed this in eight spells): for every Flavor row, each number (with its unit), size word (Tiny…Gargantuan) and placement phrase ("a point", "a location", "you choose", "you can see") must also appear in some *other* row of the entry. A typical miss: Area says "centered on **that** point" while only the Flavor row says which point ("a point you choose within range"); or a wall's "at a point you choose within range" lives only in the Flavor quote. Fix by adding/completing a row (`Appears`, `Point`, `Area`, `Size`, `Sound`). "within range" alone is fine — the card's Range covers it.
6. **Look at it** for dense spells: render with `Presentation.SpellCards.write_spell_to_file(SpellFactory.create(name), out)` into an HTML page that includes `HtmlCharacterSheetWriter()._get_css_style()`, and screenshot it with headless Edge (`"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu --window-size=760,1600 --screenshot=<png> file:///<html>`), then read the PNG. Check for crowded cells, wrapped labels, odd colors.
7. **Snapshots**: run `python -m pytest tests/test_build_snapshots.py -q -k sheets_unchanged` **before** writing (baseline) and after. Sheets showing a changed spell will fail — refresh only those with `UPDATE_SNAPSHOTS=1 python -m pytest tests/test_build_snapshots.py -q -k "sheets_unchanged and not <prebroken>"`, never builds that were already failing at baseline. Then run the full suite.

## 7. Report

- Spells written (count per file), and any skipped with the reason.
- **Anything not taken from the source text**: tables or stat-block lines added from rules knowledge (the user must verify these), aidedd text used for an empty record.
- **Source-data problems**: empty, truncated or junk-filled descriptions; missing tables; garbled stat blocks — and what the card says about each.
- Test results (spell tests, full suite), and which builds' snapshots were refreshed vs. failing before you started.

Never edit `spells_<source>.json`, `_extended.json` or `_concise.json`.
