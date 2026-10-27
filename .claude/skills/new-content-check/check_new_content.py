"""Check dnd2024.wikidot.com for 2024-rules classes, subclasses, species, feats, spells and tools
that are not in the baseline.

2024 content only. 2014 content (dnd5e.wikidot.com, SubClasses2014) is not covered yet; it will
get its own baseline_2014.json rather than sharing this one.

Usage (from the repo root):
    python .claude/skills/new-content-check/check_new_content.py            # report only
    python .claude/skills/new-content-check/check_new_content.py --todo     # also list tracked entries not in the repo yet
    python .claude/skills/new-content-check/check_new_content.py --update   # write the result into baseline_2024.json

The baseline (baseline_2024.json next to this file) is the index of everything the wiki listed the
last time someone ran --update, one entry per line, with its status in this repo:

    have     - implemented in code (the `code` path)
    scraped  - source text is in the repo (the `text` path) but there is no code yet
    todo     - tracked, but neither scraped nor implemented
    ignored  - excluded by the rules at the top of baseline_2024.json (`reason` says which)

UA (playtest) pages, all under ua:, are left out entirely: never in the baseline or the report.

Exit status: 0 when nothing tracked is new, removed or moved; 1 otherwise.
"""

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SKILL_DIR = Path(__file__).resolve().parent
REPO_ROOT = SKILL_DIR.parent.parent.parent
BASELINE = SKILL_DIR / "baseline_2024.json"
BASE_URL = "https://dnd2024.wikidot.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
SPELL_JSON = "CharacterContent/Spells/spells_dnd2024.json"
TOOL_FILE = "CharacterContent/ToolProficiencies/Proficiencies.py"

CATEGORIES = ("classes", "subclasses", "species", "feats", "spells", "tools")

# Words dropped from a subclass name before matching it to a SubClasses2024/<Class><Rest>.py file.
SUBCLASS_FILLER = {
    "of",
    "the",
    "oath",
    "college",
    "circle",
    "path",
    "domain",
    "sorcery",
    "patron",
    "warrior",
}


# ---------------------------------------------------------------- fetching


def fetch_soup(page: str, retries: int = 3) -> BeautifulSoup:
    for attempt in range(retries):
        try:
            response = requests.get(BASE_URL + page, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
    raise RuntimeError(f"fetch_soup({page!r}) failed")


def page_ref(href: str) -> str:
    return href.lstrip("/").split("#")[0]


def is_ua(page: str) -> bool:
    """UA (playtest) pages all live under ua:; they are left out of the index entirely."""
    return page.startswith("ua:")


def tabbed_links(content, prefix: str, section_of=None) -> list[tuple[str, str, str]]:
    """(page, name, group) for every link in a Wikidot tab view; group is the tab label,
    prefixed with section_of(navset) when given (the feat page nests tabs under h1 sections).
    """
    found = []
    for navset in content.find_all("div", class_="yui-navset"):
        labels = [
            li.get_text(strip=True)
            for li in navset.find("ul", class_="yui-nav").find_all("li")
        ]
        panels = navset.find("div", class_="yui-content").find_all(
            "div", recursive=False
        )
        section = section_of(navset) if section_of else None
        for label, panel in zip(labels, panels):
            group = f"{section} / {label}" if section else label
            for a in panel.find_all("a", href=True):
                page = page_ref(a["href"])
                if a["href"].startswith(prefix) and not is_ua(page):
                    found.append((page, a.get_text(strip=True), group))
    return found


def merge(found: list[tuple[str, str, str]]) -> dict[str, dict]:
    """Key by page; a page listed under several tabs (Dhampir: Ravenloft and Exotic) keeps every group."""
    entries: dict[str, dict] = {}
    for page, name, group in found:
        entry = entries.setdefault(page, {"name": name, "page": page, "groups": []})
        if group not in entry["groups"]:
            entry["groups"].append(group)
    return entries


def scrape_classes() -> dict[str, dict]:
    content = fetch_soup("class:all").find("div", id="page-content")
    found = [link for link in tabbed_links(content, "/") if link[0].endswith(":main")]
    return merge(found)


def scrape_species() -> dict[str, dict]:
    content = fetch_soup("species:all").find("div", id="page-content")
    return merge(tabbed_links(content, "/species:"))


def scrape_feats() -> dict[str, dict]:
    content = fetch_soup("feat:all").find("div", id="page-content")
    section_of = lambda navset: navset.find_previous("h1").get_text(strip=True)
    return merge(tabbed_links(content, "/feat:", section_of))


def scrape_subclasses(known: dict[str, dict]) -> dict[str, dict]:
    """Every page tagged `subclass`. The tag page has no setting tabs, so the group is the
    page's own "Source:" line, fetched only for pages the baseline doesn't already know.
    """
    soup = fetch_soup("system:page-tags/tag/subclass")
    found = []
    for item in soup.find("div", id="tagged-pages-list").find_all(
        "div", class_="pages-list-item"
    ):
        a = item.find("a", href=True)
        page = page_ref(a["href"])
        if not is_ua(page):
            found.append((page, a.get_text(strip=True), ""))
    entries = merge(found)
    for page, entry in entries.items():
        entry["class"] = page.split(":")[0].capitalize()
    return add_sources(entries, known)


def scrape_spells(known: dict[str, dict]) -> dict[str, dict]:
    """The spell index is tabbed by level (Cantrip, 1st Level, ...), which says nothing about
    the setting, so the group is the page's "Source:" line, as for subclasses."""
    content = fetch_soup("spell:all").find("div", id="page-content")
    entries = merge(tabbed_links(content, "/spell:"))
    for entry in entries.values():
        entry["level"] = entry["groups"][0]
    return add_sources(entries, known)


def scrape_tools() -> dict[str, dict]:
    """Tools have no pages of their own: each is a row in one of the tables on equipment:tool
    (Artisan Tool, Other Tool, Gaming Set, Musical Instrument), keyed by a made-up anchor.
    """
    content = fetch_soup("equipment:tool").find("div", id="page-content")
    found = []
    for table in content.find_all("table", class_="wiki-content-table"):
        rows = table.find_all("tr")
        group = rows[0].find(["th", "td"]).get_text(strip=True)
        for row in rows[1:]:
            name = row.find("td").get_text(" ", strip=True)
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            found.append((f"equipment:tool#{slug}", name, group))
    return merge(found)


def add_sources(entries: dict[str, dict], known: dict[str, dict]) -> dict[str, dict]:
    """Group each entry by its page's "Source:" line, fetching only pages the baseline doesn't
    already have a source for (the first run fetches them all, later runs only new ones).
    """
    for page, entry in entries.items():
        if page in known and known[page].get("source"):
            entry["source"] = known[page]["source"]
    missing = [p for p, e in entries.items() if "source" not in e]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for page, source in zip(missing, pool.map(fetch_source, missing)):
            entries[page]["source"] = source
    for entry in entries.values():
        entry["groups"] = [entry["source"]]
    return entries


def fetch_source(page: str) -> str:
    content = fetch_soup(page).find("div", id="page-content")
    for p in content.find_all("p"):
        # First line only: some pages put the stat block in the same <p> after a <br/>.
        lines = p.get_text("\n", strip=True).split("\n")
        text = " ".join(lines[:2]) if lines[0] == "Source:" else lines[0]
        if text.startswith("Source:"):
            return text.removeprefix("Source:").strip()
    return "?"


# ---------------------------------------------------------------- local status


def camel(name: str) -> str:
    return "".join(
        w[:1].upper() + w[1:] for w in re.sub(r"[^A-Za-z0-9 ]", "", name).split()
    )


def significant(words: list[str]) -> str:
    """'Oath of the Noble Genies' -> 'noblegenies'; 'Genies' (from PaladinGenies.py) -> 'genies'."""
    return "".join(w.lower() for w in words if w.lower() not in SUBCLASS_FILLER)


def plain(name: str) -> str:
    """Spell and tool names compared loosely: case ("Commune With Nature"), curly
    apostrophes, and the legacy "Power Word: Stun" colon."""
    return name.lower().replace("’", "'").replace(": ", " ").strip()


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


class LocalIndex:
    """What this repo already has, by the naming rules each content type follows."""

    def __init__(self):
        self.subclass_files = sorted(
            (REPO_ROOT / "CharacterContent/Classes/SubClasses2024").glob("*.py")
        )
        feature_dir = REPO_ROOT / "CharacterContent/Features"
        self.feat_classes: dict[str, str] = {}
        for py in sorted(feature_dir.rglob("*.py")):
            for match in re.finditer(
                r"^class (\w+)\(", py.read_text(encoding="utf-8"), re.M
            ):
                # Lowercased: class names don't always keep the wiki's casing (EnclaveMAGIC).
                self.feat_classes.setdefault(match.group(1).lower(), rel(py))
        self.text_lines: dict[str, set[str]] = {}
        spells = json.loads((REPO_ROOT / SPELL_JSON).read_text(encoding="utf-8"))
        self.spells = {plain(name) for name in spells}
        tools = (REPO_ROOT / TOOL_FILE).read_text(encoding="utf-8")
        self.tools = {plain(n) for n in re.findall(r'^\s+name="([^"]+)"', tools, re.M)}

    def lines(self, path: str) -> set[str]:
        if path not in self.text_lines:
            file = REPO_ROOT / path
            text = file.read_text(encoding="utf-8") if file.exists() else ""
            self.text_lines[path] = {line.strip() for line in text.splitlines()}
        return self.text_lines[path]

    def find(self, category: str, entry: dict) -> tuple[str | None, str | None]:
        """(code path, text path), either None when absent."""
        name, slug = entry["name"], entry["page"].split(":")[-1]
        if category == "classes":
            code = REPO_ROOT / f"CharacterContent/Classes/BaseClasses/{name}Base.py"
            text = REPO_ROOT / f"SourceTexts/ClassTexts/{name.lower()}.txt"
            return rel(code) if code.exists() else None, (
                rel(text) if text.exists() else None
            )
        if category == "subclasses":
            text = (
                REPO_ROOT
                / f"SourceTexts/SubclassTexts2024/{slug.replace('-', '_')}.txt"
            )
            return self.subclass_code(entry), rel(text) if text.exists() else None
        if category == "species":
            code = REPO_ROOT / f"CharacterContent/Species/{camel(name)}.py"
            text = "CharacterContent/Species/species.txt"
            return rel(code) if code.exists() else None, (
                text if name in self.lines(text) else None
            )
        if category == "feats":
            texts = (
                "CharacterContent/Features/origin_feats.txt",
                "CharacterContent/Features/general_feats.txt",
            )
            text = next((t for t in texts if name in self.lines(t)), None)
            return self.feat_classes.get(camel(name).lower()), text
        if category == "spells":
            # Spells are data: a spell is usable once it is in the JSON SpellFactory loads.
            return (SPELL_JSON if plain(name) in self.spells else None), None
        if category == "tools":
            return (TOOL_FILE if plain(name) in self.tools else None), None
        raise ValueError(category)

    def subclass_code(self, entry: dict) -> str | None:
        cls = entry.get("class")
        if not cls:
            return None
        key = significant(entry["name"].replace("-", " ").split())
        for py in self.subclass_files:
            if py.stem.startswith(cls):
                rest = significant(re.findall(r"[A-Z][a-z]*", py.stem[len(cls) :]))
                if rest and (rest in key or key in rest):
                    return rel(py)
        return None


# ---------------------------------------------------------------- baseline


def ignore_reason(config: dict, entry: dict) -> str | None:
    # Ignored only when every group is: Dhampir is under both Ravenloft and Exotic, and is tracked.
    groups = entry["groups"]
    words = [next((w for w in config["ignore_groups"] if w in g), None) for g in groups]
    if groups and all(words):
        return words[0]
    return None


def classify(config: dict, local: LocalIndex, category: str, entry: dict) -> dict:
    out = {
        k: entry[k]
        for k in ("name", "page", "class", "level", "source", "groups")
        if entry.get(k) is not None
    }
    if "source" in out:  # groups is just [source] then
        out.pop("groups")
    reason = ignore_reason(config, entry)
    code, text = local.find(category, entry)
    if code:
        out["status"] = "have"
    elif text:
        out["status"] = "scraped"
    else:
        out["status"] = "ignored" if reason else "todo"
    if reason:
        out["reason"] = reason
    if code:
        out["code"] = code
    if text:
        out["text"] = text
    return out


def load_baseline() -> dict:
    if not BASELINE.exists():
        return {
            "config": {"ignore_groups": ["Lorwyn", "Exotic"]},
            **{c: [] for c in CATEGORIES},
        }
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def write_baseline(baseline: dict):
    """One entry per line, so the file reads as an index and diffs line by line."""
    parts = ["{", f' "config": {json.dumps(baseline["config"], ensure_ascii=False)},']
    for i, category in enumerate(CATEGORIES):
        entries = sorted(
            baseline[category], key=lambda e: (e.get("class", ""), e["name"], e["page"])
        )
        rows = ",\n".join(f"  {json.dumps(e, ensure_ascii=False)}" for e in entries)
        parts.append(
            f' "{category}": [\n{rows}\n ]' + ("," if i < len(CATEGORIES) - 1 else "")
        )
    parts.append("}")
    BASELINE.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- report


def describe(entry: dict) -> str:
    where = ", ".join(filter(None, (entry.get("level"), entry.get("source"))))
    where = where or ", ".join(entry.get("groups", []))
    status = entry["status"] + (f" ({entry['reason']})" if entry.get("reason") else "")
    return f"{entry['name']:<34} {entry['page']:<44} {where:<40} {status}"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="write the fresh index into baseline_2024.json",
    )
    parser.add_argument(
        "--todo", action="store_true", help="also list tracked entries with no code yet"
    )
    args = parser.parse_args()

    baseline = load_baseline()
    config = baseline["config"]
    local = LocalIndex()
    # .get: a category added to CATEGORIES later starts out empty (everything in it is NEW).
    old = {c: {e["page"]: e for e in baseline.get(c, [])} for c in CATEGORIES}

    scraped = {
        "classes": scrape_classes(),
        "subclasses": scrape_subclasses(old["subclasses"]),
        "species": scrape_species(),
        "feats": scrape_feats(),
        "spells": scrape_spells(old["spells"]),
        "tools": scrape_tools(),
    }
    fresh = {
        c: {p: classify(config, local, c, e) for p, e in scraped[c].items()}
        for c in CATEGORIES
    }

    print(f"2024 content on {BASE_URL} vs {rel(BASELINE)}")
    attention = False
    for category in CATEGORIES:
        before, now = old[category], fresh[category]
        new = [now[p] for p in now if p not in before]
        gone = [before[p] for p in before if p not in now]
        moved = [
            (before[p], now[p])
            for p in now
            if p in before
            and (before[p].get("groups"), before[p].get("source"))
            != (now[p].get("groups"), now[p].get("source"))
        ]
        changed = [
            (before[p], now[p])
            for p in now
            if p in before and before[p]["status"] != now[p]["status"]
        ]
        todo = [e for e in now.values() if e["status"] in ("todo", "scraped")]

        tracked_new = [e for e in new if e["status"] != "ignored"]
        attention |= bool(tracked_new or gone or moved)
        print(
            f"== {category}: {len(now)} on the wiki, {len(new)} new, {len(gone)} removed, {len(moved)} moved, "
            f"{sum(e['status'] == 'have' for e in now.values())} have, {len(todo)} todo/scraped"
        )
        for title, rows in (
            ("NEW (tracked)", tracked_new),
            ("NEW (ignored)", [e for e in new if e["status"] == "ignored"]),
            ("REMOVED from the wiki", gone),
        ):
            if rows:
                print(f"  {title}:")
                for e in rows:
                    print(f"    {describe(e)}")
        if moved:
            print("  MOVED (group or source changed):")
            for b, n in moved:
                print(
                    f"    {n['name']}: {b.get('source') or b.get('groups')} -> {n.get('source') or n.get('groups')}"
                )
        if changed:
            print("  LOCAL STATUS changed:")
            for b, n in changed:
                print(f"    {n['name']}: {b['status']} -> {n['status']}")
        if args.todo and todo:
            print("  TODO (tracked, no code yet):")
            for e in sorted(todo, key=lambda e: e["name"]):
                print(f"    {describe(e)}")

    if args.update:
        write_baseline(
            {"config": config, **{c: list(fresh[c].values()) for c in CATEGORIES}}
        )
        print(f"\nWrote {rel(BASELINE)}")
    elif attention:
        print(
            "\nTracked content changed on the wiki. Review it, then rerun with --update to accept it as the new baseline."
        )
    sys.exit(1 if attention and not args.update else 0)


if __name__ == "__main__":
    main()
