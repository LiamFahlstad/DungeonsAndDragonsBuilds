import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from WikiDotPageRenderer import render_content_lines

BASE_URL = "https://dnd5e.wikidot.com/"

# NOTE: https://dnd5e.wikidot.com/system:page-tags/tag/subclass does NOT work as
# a discovery mechanism on this site - unlike dnd2024.wikidot.com, dnd5e.wikidot.com
# has no "subclass" tag at all (confirmed: it's absent from the site's own tag
# cloud), and the tagged-pages-list div on that page is populated by an AJAX
# call (list/ListPagesModule) that returns empty for this/most tag+category
# combinations tried here. Do not rely on it.
#
# What *does* work: every class has a bare index page at /{class} (e.g.
# https://dnd5e.wikidot.com/paladin, NOT /paladin:main - that page doesn't
# exist) whose #page-content contains one or more <table class="wiki-content-table">
# listing every official subclass as a "/{class}:{slug}" link, followed by a
# "<th colspan=...>Archived Unearthed Arcana</th>" row and more links whose slugs
# end in "-ua". See discover_all_subclasses() below.
#
# NOTE: dnd5e.wikidot.com subclass slugs are the *short* archetype name, not
# "oath-of-..."/"circle-of-..." style like dnd2024 (e.g. paladin:vengeance, not
# paladin:oath-of-vengeance). Some pages also have "-ua" (Unearthed Arcana /
# unofficial playtest) siblings, e.g. paladin:redemption vs paladin:redemption-ua -
# those are unofficial and should be avoided.

# The 12 classes with subclass index pages, keyed by their dnd5e.wikidot.com
# class-page slug (all are single lowercase words, matching the wikidot
# page-ref category exactly).
CLASS_INDEX_PAGES = [
    "artificer", "barbarian", "bard", "cleric", "druid", "fighter",
    "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
]


def discover_all_subclasses() -> dict[str, list[tuple[str, str]]]:
    """Discover every official (non-UA) subclass per class by fetching each
    class's bare index page (https://dnd5e.wikidot.com/{class}) and scanning
    its subclass table(s) for "/{class}:{slug}" links.

    Multi-colon sub-page links (e.g. /fighter:battle-master:maneuvers) and
    any slug ending in "-ua" (Unearthed Arcana / unofficial playtest content)
    are excluded.

    Returns {class_name: [(display_name, slug), ...]}.
    """
    results: dict[str, list[tuple[str, str]]] = {}
    for class_name in CLASS_INDEX_PAGES:
        response = requests.get(f"{BASE_URL}{class_name}")
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find("div", id="page-content")
        if not content or response.status_code != 200:
            results[class_name] = []
            continue

        found: list[tuple[str, str]] = []
        seen_slugs: set[str] = set()
        for a in content.find_all("a", href=True):
            path = urlparse(a["href"]).path.lstrip("/")
            if ":" not in path:
                continue
            prefix, _, slug = path.partition(":")
            if prefix != class_name or ":" in slug or slug.endswith("-ua"):
                continue
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            found.append((a.get_text(strip=True), slug))
        results[class_name] = found
    return results


# -------------------
# Display-name -> discovered-slug resolution
# -------------------
# dnd5e.wikidot.com's subclass index tables list the *short* archetype name
# (e.g. "Ancients", "Archfey", "Land"), while a roster file is more likely to
# use the full official name ("Oath of the Ancients", "The Archfey", "Circle
# of the Land"). These helpers strip the common naming-convention prefixes/
# suffixes before matching against the discovered short names.

_STRIP_PREFIXES = [
    "path of the ", "path of ",
    "way of the ", "way of ",
    "oath of the ", "oath of ",
    "college of ",
    "circle of the ", "circle of ",
    "school of ",
    "the ",
]
_STRIP_SUFFIXES = [" domain"]


def _strip_naming_convention(name: str) -> str:
    lower = name.lower()
    for prefix in _STRIP_PREFIXES:
        if lower.startswith(prefix):
            name = name[len(prefix):]
            lower = name.lower()
            break
    for suffix in _STRIP_SUFFIXES:
        if lower.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name.strip()


def resolve_subclass_page_ref(
    class_name: str, display_name: str, discovered: list[tuple[str, str]]
) -> str | None:
    """Match a requested (class, display_name) against a discover_all_subclasses()
    entry, returning a 'class:slug' page_ref, or None if no match is found."""
    by_name = {name.lower(): slug for name, slug in discovered}

    candidates = [display_name]
    paren_match = re.match(r"^(.*?)\s*\((.*)\)\s*$", display_name)
    if paren_match:
        candidates = [paren_match.group(1).strip(), paren_match.group(2).strip()]

    for candidate in candidates:
        if candidate.lower() in by_name:
            return f"{class_name}:{by_name[candidate.lower()]}"

        stripped = _strip_naming_convention(candidate)
        if stripped.lower() in by_name:
            return f"{class_name}:{by_name[stripped.lower()]}"

        stripped_lower = stripped.lower()
        for name, slug in discovered:
            name_lower = name.lower()
            if stripped_lower in name_lower or name_lower in stripped_lower:
                return f"{class_name}:{slug}"

    return None


class SubclassNotFoundError(Exception):
    """Raised when the subclass page does not exist on dnd5e.wikidot.com."""

    pass


class SubclassParser:
    def __init__(self, page_ref: str):
        """page_ref is e.g. 'druid:spores' (class:slug)."""
        self.page_ref = page_ref
        self.url = f"{BASE_URL}{page_ref}"
        self.soup = None
        self.content = None

    def fetch(self):
        """Download the subclass page HTML and prepare the soup object."""
        response = requests.get(self.url)

        self.soup = BeautifulSoup(response.text, "html.parser")
        self.content = self.soup.find("div", id="page-content")

        if not self.content:
            raise ValueError(
                f"Could not find main page content for '{self.page_ref}' ({self.url})."
            )

        not_found = self.content.find("p", id="404-message")
        if response.status_code != 200 or not_found:
            raise SubclassNotFoundError(
                f"Subclass '{self.page_ref}' ({self.url}) does not exist "
                f"(HTTP {response.status_code})."
            )

    # -------------------
    # Rendering
    # -------------------

    def get_lines(self) -> list[str]:
        """Render the page content into the exact plain-text line list."""
        return render_content_lines(self.content)

    def get_text(self) -> str:
        return "\n".join(self.get_lines())

    # -------------------
    # to_dict / print_info / write_to_file trio
    # -------------------

    def to_dict(self) -> dict:
        return {
            "page_ref": self.page_ref,
            "url": self.url,
            "text": self.get_text(),
        }

    def print_info(self):
        data = self.to_dict()
        print(data["text"])

    def write_to_file(self, file):
        """Write the rendered subclass text to an already-open file handle."""
        file.write(self.get_text())
        file.write("\n")

    def write_to_path(self, path: Path):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            self.write_to_file(f)


def slug_to_filename(page_ref: str) -> str:
    """'druid:spores' -> 'spores.txt'."""
    slug = page_ref.split(":", 1)[-1]
    return slug.replace("-", "_") + ".txt"


def fetch_subclass(page_ref: str, max_retries: int = 3) -> tuple[str, SubclassParser]:
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            parser = SubclassParser(page_ref)
            parser.fetch()
            return page_ref, parser
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise last_exc or RuntimeError(f"fetch_subclass({page_ref!r}) failed")


DEFAULT_PAGES = [
    "druid:spores",
    "wizard:evocation",
    "ranger:hunter",
]

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "SourceTexts" / "SubclassTexts2014"


if __name__ == "__main__":
    pages = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_PAGES

    results: dict[str, SubclassParser] = {}
    failed: list[str] = []

    MAX_WORKERS = 4

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_subclass, page): page for page in pages}

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching subclasses",
        ):
            page_ref = futures[future]
            try:
                _, parser = future.result()
                results[page_ref] = parser
            except Exception as e:
                print(f"  FAILED {page_ref}: {e}")
                failed.append(page_ref)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for page_ref, parser in results.items():
        out_path = OUTPUT_DIR / slug_to_filename(page_ref)
        parser.write_to_path(out_path)
        print(f"Wrote {page_ref} -> {out_path}")

    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
