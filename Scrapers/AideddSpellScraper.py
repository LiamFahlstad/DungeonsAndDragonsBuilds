import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TextIO

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class SpellNotFoundError(Exception):
    """Raised when the spell does not exist on AideDD."""

    pass


# Connector words other sources may inconsistently capitalize mid-name
# (e.g. "Commune With Nature" vs "Commune with Nature"). Lowercase them
# whenever they're not the first word, matching the wikidot scrapers, so
# the same spell from different sources merges under one name instead of
# producing near-duplicate entries.
_LOWERCASE_MIDWORDS = {"of", "and", "with", "without"}


def normalize_spell_name(name: str) -> str:
    name = name.replace(": ", " ")
    words = name.split(" ")
    return " ".join(
        w.lower() if i > 0 and w.lower() in _LOWERCASE_MIDWORDS else w
        for i, w in enumerate(words)
    )


class SpellParser:
    BASE_URL = "https://www.aidedd.org/spell/"

    def __init__(self, spell_name: str):
        self.original_name = spell_name
        self.spell_name = self._slugify(spell_name)
        self.url = f"{self.BASE_URL}{self.spell_name}"
        self.soup = None
        self.col1 = None

    def _slugify(self, name: str) -> str:
        """Convert a spell name into the URL-friendly format used by AideDD (no regex)."""
        # Lowercase and strip whitespace
        name = name.lower().strip()

        # Replace curly apostrophes and normalize common punctuation
        name = name.replace("’", "'")
        name = name.replace("'", "-")
        name = name.replace("/", "-")
        name = name.replace("é", "e")

        # Remove any non-alphanumeric characters except spaces and hyphens
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
        cleaned = "".join(ch for ch in name if ch in allowed_chars)

        # Replace spaces with hyphens
        return cleaned.replace(" ", "-")

    def fetch(self):
        """Download the spell page HTML and prepare the soup object."""
        response = requests.get(self.url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, "html.parser")
        self.col1 = self.soup.find("div", class_="col1")
        if not self.col1:
            raise ValueError(
                "Could not find main spell content. Check if the spell name is correct."
            )

        warning = self.col1.find("p", class_="warning")
        if warning:
            raise SpellNotFoundError(
                f"Spell '{self.original_name}' ({self.url}) does not exist on AideDD."
            )

    # -------------------

    # -------------------
    # Individual field getters
    # -------------------

    def format_text(self, text: str) -> str:
        return text.replace("´", "'")

    def get_name(self):
        text = self._get_text(self.col1.find("h1"))
        return self.format_text(text)

    def get_level_and_school(self) -> dict:
        text = self._get_text(self.col1.find("div", class_="ecole"))
        text = self.format_text(text)
        pattern = r"^Level\s+(\d+)\s+([A-Za-z ]+)\s+\(([^)]+)\)"
        match = re.match(pattern, text)
        if not match:
            raise ValueError(f"Could not parse level and school from text: '{text}'")

        level = int(match.group(1))
        school = match.group(2).strip()
        classes = [c.strip() for c in match.group(3).split(",")]

        return {"level": level, "school": school, "classes": classes}

    def get_casting_time(self):
        text = self._clean_field(self.col1.find("div", class_="t"))
        return self.format_text(text)

    def get_range(self):
        text = self._clean_field(self.col1.find("div", class_="r"))
        return self.format_text(text)

    def get_components(self):
        text = self._clean_field(self.col1.find("div", class_="c"))
        return self.format_text(text)

    def get_duration(self):
        text = self._clean_field(self.col1.find("div", class_="d"))
        return self.format_text(text)

    def get_description(self):
        text = self._get_text(self.col1.find("div", class_="description"))
        return self.format_text(text)

    def get_source(self):
        text = self._get_text(self.col1.find("div", class_="source"))
        return self.format_text(text)

    # -------------------
    # Helpers
    # -------------------

    def _get_text(self, element):
        return element.get_text(" ", strip=True) if element else ""

    def _clean_field(self, div):
        """Remove the bold label part (e.g. 'Casting Time:') and return just the value."""
        text = self._get_text(div)
        return text.split(":", 1)[-1].strip() if ":" in text else text

    def to_dict(self):
        """Return all spell info as a dictionary."""
        level_school = (
            self.get_level_and_school()
        )  # returns dict with level, school, classes

        return {
            "name": self.get_name(),
            **level_school,  # <-- Unpacks into "level", "school", "classes"
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


def fetch_spell(spell_name: str, max_retries: int = 3) -> tuple[str, dict]:
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            spell = SpellParser(spell_name)
            spell.fetch()
            data = spell.to_dict()
            # Key by the name AideDD itself uses, not the input candidate -
            # different candidate spellings (e.g. "Power Word: Heal" from
            # dnd5e vs "Power Word Heal" from dnd2024) can resolve to the
            # same AideDD page, and we don't want two entries for one spell.
            name = normalize_spell_name(data["name"])
            data["name"] = name
            return name, data
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise last_exc or RuntimeError(f"fetch_spell({spell_name!r}) failed")


def _candidate_names() -> list[str]:
    """Union of spell names known from the dnd2024 and dnd5e wikidot scrapers.

    aidedd.org has no browsable spell index, so we reuse the names already
    discovered by the other two sources as our candidate list.
    """
    names: set[str] = set()
    for path in ("Spells/spells_dnd2024.json", "Spells/spells_dnd5e.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                names.update(normalize_spell_name(n) for n in json.load(f).keys())
        except FileNotFoundError:
            print(f"  (skipping missing {path})")
    return sorted(names)


if __name__ == "__main__":
    print("Building candidate spell list from dnd2024/dnd5e JSON files …")
    spells = _candidate_names()
    print(f"Found {len(spells)} candidate spell names.")

    results: dict[str, dict] = {}
    not_found: list[str] = []
    failed: list[str] = []

    MAX_WORKERS = 4

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(fetch_spell, spell_name): spell_name
            for spell_name in spells
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
            except SpellNotFoundError:
                not_found.append(spell_name)
            except Exception as e:
                print(f"  FAILED {spell_name}: {e}")
                failed.append(spell_name)

    sorted_results = dict(sorted(results.items()))

    out_path = "Spells/spells_aidedd.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=4, ensure_ascii=False)

    print(f"\nWrote {len(sorted_results)} spells -> {out_path}")
    print(f"Not found on AideDD ({len(not_found)}): {', '.join(not_found)}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
