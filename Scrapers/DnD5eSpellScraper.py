import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TextIO

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://dnd5e.wikidot.com/"

# Connector words the wiki's index page inconsistently title-cases mid-name
# (e.g. "Spray Of Cards" instead of "Spray of Cards"). Lowercase them
# whenever they're not the first word, to match standard spell-name casing.
_LOWERCASE_MIDWORDS = {"of", "and"}


def normalize_spell_name(name: str) -> str:
    words = name.split(" ")
    return " ".join(
        w.lower() if i > 0 and w.lower() in _LOWERCASE_MIDWORDS else w
        for i, w in enumerate(words)
    )


def fetch_all_spells() -> list[tuple[str, str]]:
    """Fetch all (name, slug) pairs from https://dnd5e.wikidot.com/spells.

    Unlike dnd2024.wikidot.com (whose /spell:all index page is a flat list
    of links), dnd5e.wikidot.com's /spells index renders a tabbed set of
    wiki-content-table's (one tab per spell level), each row's spell name
    being a link like <a href="/spell:acid-splash">Acid Splash</a>. We keep
    the href-derived slug alongside the display name because some entries
    (mostly Unearthed Arcana spells tagged "(UA)" in their display name)
    have slugs that don't cleanly correspond to a simple slugification of
    the name shown (e.g. "Guiding Hand (UA)" -> /spell:guiding-hand-ua but
    "Hand of Radiance (UA)" -> /spell:hand-of-radiance).
    """
    url = f"{BASE_URL}spells"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.find("div", id="page-content")
    if not content:
        raise ValueError("Could not find page content on /spells page.")

    slug_to_name: dict[str, str] = {}
    for link in content.find_all("a"):
        href = link.get("href", "")
        if not href.startswith("/spell:"):
            continue
        slug = href[len("/spell:") :]
        name = link.get_text(strip=True)
        if not name:
            continue
        # Unearthed Arcana spells are unofficial playtest content, tagged
        # "(UA)" in their display name on this wiki — exclude them.
        if "(UA)" in name:
            continue
        slug_to_name[slug] = normalize_spell_name(name)

    return sorted(
        ((name, slug) for slug, name in slug_to_name.items()), key=lambda t: t[0]
    )


class SpellNotFoundError(Exception):
    """Raised when the spell does not exist on dnd5e.wikidot.com."""

    pass


class DnD5eSpellParser:
    def __init__(self, spell_name: str, slug: str | None = None):
        self.original_name = spell_name
        self.known_slug = slug
        self.soup = None
        self.col1 = None

    def _slugify1(self, name: str) -> str:
        """Convert a spell name into the URL-friendly format (no regex)."""
        name = name.lower().strip()

        name = name.replace("’", "'")
        name = name.replace("'", "")
        name = name.replace("/", "-")
        name = name.replace("é", "e")

        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
        cleaned = "".join(ch for ch in name if ch in allowed_chars)

        return cleaned.replace(" ", "-")

    def _slugify2(self, name: str) -> str:
        """Convert a spell name into the URL-friendly format (no regex)."""
        name = name.lower().strip()

        name = name.replace("’", "'")
        name = name.replace("'", "-")
        name = name.replace("/", "-")
        name = name.replace("é", "e")

        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
        cleaned = "".join(ch for ch in name if ch in allowed_chars)

        return cleaned.replace(" ", "-")

    def fetch(self):
        """Download the spell page HTML and prepare the soup object."""
        candidate_slugs = []
        if self.known_slug:
            candidate_slugs.append(self.known_slug)
        candidate_slugs.append(self._slugify1(self.original_name))
        candidate_slugs.append(self._slugify2(self.original_name))

        # De-duplicate while preserving priority order.
        seen = set()
        slugs = []
        for slug in candidate_slugs:
            if slug not in seen:
                seen.add(slug)
                slugs.append(slug)

        last_status = None
        for slug in slugs:
            self.url = f"{BASE_URL}spell:{slug}"
            response = requests.get(self.url)
            last_status = response.status_code
            if response.status_code == 200:
                candidate_soup = BeautifulSoup(response.text, "html.parser")
                candidate_content = candidate_soup.find("div", id="page-content")
                if candidate_content and candidate_content.find(
                    "p", id="404-message"
                ):
                    # Some CDN configs return HTTP 200 for wikidot's own
                    # soft-404 page instead of propagating the 404 status.
                    last_status = 404
                    continue
                self.soup = candidate_soup
                self.col1 = candidate_content
                break

        if self.soup is None or self.col1 is None:
            raise SpellNotFoundError(
                f"Spell '{self.original_name}' not found (HTTP {last_status})."
            )

        if self.col1.find("p", id="404-message"):
            raise SpellNotFoundError(
                f"Spell '{self.original_name}' ({self.url}) does not exist on dnd5e.wikidot.com."
            )

    # -------------------
    # Individual field getters
    # -------------------

    def format_text(self, text: str) -> str:
        return text.replace("´", "'").replace("’", "'").replace("“", '"').replace(
            "”", '"'
        )

    def get_name(self):
        return self.original_name

    def get_level_and_school(self) -> dict:
        em = self.col1.find("em")
        if not em:
            raise ValueError("Could not find level/school text")

        text = self.format_text(em.get_text(strip=True))

        ritual = False
        if text.endswith("(ritual)"):
            ritual = True
            text = text[: -len("(ritual)")].strip()

        if "cantrip" in text.lower():
            level = 0
            school = text.split(" ")[0]
        else:
            match = re.match(r"(\d+)\w{2}-level\s+(.+)", text, re.IGNORECASE)
            if not match:
                raise ValueError(f"Could not parse level/school from {text!r}")
            level = int(match.group(1))
            school = match.group(2)

        return {
            "level": level,
            "school": school.strip().title(),
            "ritual": ritual,
        }

    def get_casting_time(self):
        label = self.col1.find("strong", string="Casting Time:")
        if not label:
            return None

        return label.next_sibling.strip()

    def get_range(self):
        label = self.col1.find("strong", string="Range:")
        if not label:
            return None

        return label.next_sibling.strip()

    def get_components(self):
        label = self.col1.find("strong", string="Components:")
        if label:
            return label.next_sibling.strip()

        label = self.col1.find("strong", string="Component:")
        if label:
            return label.next_sibling.strip()

        return None

    def get_duration(self):
        label = self.col1.find("strong", string="Duration:")
        if not label:
            return None

        return label.next_sibling.strip()

    def get_classes(self):
        label = self.col1.find("strong", string="Spell Lists.")
        if not label:
            return []

        p = label.find_parent("p")
        if not p:
            return []

        return [a.get_text(strip=True) for a in p.find_all("a")]

    def get_description(self):
        # dnd5e.wikidot.com spell pages are a flat sequence of direct
        # children of #page-content: Source paragraph, an <em>-only
        # level/school paragraph, a metadata paragraph (Casting Time /
        # Range / Components / Duration separated by <br/>), one or more
        # description <p>/<ul> elements (including an optional
        # "At Higher Levels." paragraph), and finally a "Spell Lists."
        # paragraph of class links.
        elements = self.col1.find_all(["p", "ul"], recursive=False)

        started = False
        lines: list[str] = []
        for elem in elements:
            if elem.name == "p":
                if elem.find("strong", string="Casting Time:"):
                    started = True
                    continue
                if not started:
                    continue
                if elem.find("strong", string="Spell Lists."):
                    break
                text = elem.get_text(" ", strip=True)
                if text:
                    lines.append(text)
            else:  # <ul>
                if not started:
                    continue
                for li in elem.find_all("li", recursive=False):
                    li_text = li.get_text(" ", strip=True)
                    if li_text:
                        lines.append(li_text)

        return self.format_text("\n".join(lines)) if lines else None

    def get_source(self) -> str | None:
        p = self.col1.find("p")
        if not p or not p.contents:
            return None

        first_text = p.contents[0].strip()  # first child is usually the text
        if first_text.startswith("Source:"):
            return first_text[len("Source:") :].strip()
        return None

    # -------------------
    # Helpers
    # -------------------

    def _get_text(self, element):
        return element.get_text(" ", strip=True) if element else ""

    def to_dict(self):
        """Return all spell info as a dictionary."""
        level_school = (
            self.get_level_and_school()
        )  # returns dict with level, school, ritual

        return {
            "name": self.get_name(),
            **level_school,  # <-- Unpacks into "level", "school", "ritual"
            "classes": self.get_classes(),
            "casting_time": self.get_casting_time(),
            "range": self.get_range(),
            "components": self.get_components(),
            "duration": self.get_duration(),
            "description": self.get_description(),
            "source": self.get_source(),
        }

    def print_info(self):
        """Print all spell info in a readable format."""
        data = self.to_dict()
        for key, value in data.items():
            print(f"{key.title().replace('_', ' ')}: {value}")

    def write_to_file(self, file: TextIO):
        """Write all spell info in a readable format to a file."""
        data = self.to_dict()
        for key, value in data.items():
            file.write(f"{key.title().replace('_', ' ')}: {value}\n")


def fetch_spell(
    spell_name: str, slug: str | None = None, max_retries: int = 3
) -> tuple[str, dict]:
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            spell = DnD5eSpellParser(spell_name, slug=slug)
            spell.fetch()
            return spell_name, spell.to_dict()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise last_exc or RuntimeError(f"fetch_spell({spell_name!r}) failed")


if __name__ == "__main__":
    print("Fetching spell list from /spells …")
    spells = fetch_all_spells()
    print(f"Found {len(spells)} spells.")

    results: dict[str, dict] = {}
    failed: list[str] = []

    MAX_WORKERS = 4

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_spell, spell_name, slug): spell_name
            for spell_name, slug in spells
        }

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Fetching spells",
        ):
            spell_name = futures[future]
            try:
                name, data = future.result()
                results[name] = data
            except Exception as e:
                print(f"  FAILED {spell_name}: {e}")
                failed.append(spell_name)

    sorted_results = dict(sorted(results.items()))

    out_path = "Spells/spells_dnd5e.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=4, ensure_ascii=False)

    print(f"\nWrote {len(sorted_results)} spells -> {out_path}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
