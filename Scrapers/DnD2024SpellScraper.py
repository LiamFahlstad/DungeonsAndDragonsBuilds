import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TextIO

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://dnd2024.wikidot.com/"

# Connector words the wiki's index page inconsistently title-cases mid-name
# (e.g. "Cloud Of Daggers" instead of "Cloud of Daggers"). Lowercase them
# whenever they're not the first word, to match standard spell-name casing.
_LOWERCASE_MIDWORDS = {"of", "and", "with", "without"}


def normalize_spell_name(name: str) -> str:
    words = name.split(" ")
    return " ".join(
        w.lower() if i > 0 and w.lower() in _LOWERCASE_MIDWORDS else w
        for i, w in enumerate(words)
    )


def fetch_all_spell_names() -> list[str]:
    """Fetch all spell names from http://dnd2024.wikidot.com/spell:all."""
    url = f"{BASE_URL}spell:all"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    content = soup.find("div", id="page-content")
    if not content:
        raise ValueError("Could not find page content on spell:all page.")

    spell_names = []
    for link in content.find_all("a"):
        href = link.get("href", "")
        if not href.startswith("/spell:") or href in ("/spell:all",):
            continue
        name = link.get_text(strip=True)
        # Skip category index links like "Abjuration Spells", "Conjuration Spells", …
        if not name or name.endswith(" Spells"):
            continue
        spell_names.append(normalize_spell_name(name))

    return sorted(set(spell_names))


class SpellNotFoundError(Exception):
    """Raised when the spell does not exist on dnd5."""

    pass


class DnD2024SpellParser:
    def __init__(self, spell_name: str):
        self.original_name = spell_name
        self.soup = None
        self.col1 = None

    def _slugify1(self, name: str) -> str:
        """Convert a spell name into the URL-friendly format used by AideDD (no regex)."""
        # Lowercase and strip whitespace
        name = name.lower().strip()

        # Replace curly apostrophes and normalize common punctuation
        name = name.replace("’", "'")
        name = name.replace("'", "")
        name = name.replace("/", "-")
        name = name.replace("é", "e")

        # Remove any non-alphanumeric characters except spaces and hyphens
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
        cleaned = "".join(ch for ch in name if ch in allowed_chars)

        # Replace spaces with hyphens
        return cleaned.replace(" ", "-")

    def _slugify2(self, name: str) -> str:
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
        slugygifies = [self._slugify1, self._slugify2]
        last_status = None
        for slugify in slugygifies:
            spell_name_slug = slugify(self.original_name)
            self.url = f"{BASE_URL}spell:{spell_name_slug}"
            response = requests.get(self.url)
            last_status = response.status_code
            if response.status_code >= 500:
                # Server hiccup, not a wrong slug: let fetch_spell retry.
                raise requests.exceptions.HTTPError(
                    f"HTTP {response.status_code} for {self.url}", response=response
                )
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.text, "html.parser")
                break

        if self.soup is None:
            raise SpellNotFoundError(
                f"Spell '{self.original_name}' not found (HTTP {last_status})."
            )

        self.col1 = self.soup.find("div", id="page-content")
        if not self.col1:
            raise ValueError(
                "Could not find main spell content. Check if the spell name is correct."
            )

        warning = self.col1.find("p", class_="warning")
        if warning:
            raise SpellNotFoundError(
                f"Spell '{self.original_name}' ({self.url}) does not exist on AideDD."
            )

    def format_text(self, text: str) -> str:
        return text.replace("´", "'")

    def get_name(self):
        return self.original_name

    # "Level 3 Evocation (Sorcerer, Wizard)" or "Evocation Cantrip (Sorcerer, Wizard)"
    _LEVEL_LINE = re.compile(r"^(Level\s+\d+\s+\w+|\w+\s+Cantrip)\s*\([^)]*\)")

    def _find_level_line(self) -> str | None:
        # Usually the first <em>, but some pages (e.g. Festering Blast) have it
        # as bare text at the start of a <p>, possibly followed by the
        # Casting Time block in the same <p>, so keep only the matched line.
        em = self.col1.find("em")
        candidates = ([em] if em else []) + self.col1.find_all("p")
        for elem in candidates:
            m = self._LEVEL_LINE.match(elem.get_text(" ", strip=True))
            if m:
                return m.group(0)
        return em.text.strip() if em else None

    def get_level_and_school(self) -> dict:
        level_line = self._find_level_line()
        if not level_line:
            raise ValueError("Could not find level/school text")

        text = self.format_text(level_line)

        def get_level():
            if "Level" not in text:
                return 0  # Cantrip
            return int(re.search(r"Level\s+(\d+)", text).group(1))

        def get_school():
            if "Level" not in text:
                return text.split(" ")[0]
            return text.split(" ")[2]

        def get_base_classes():
            local_text = text[:-1]  # Remove trailing parenthesis
            local_text = local_text.split("(")[-1]
            return [c.strip() for c in local_text.split(",")]

        return {
            "level": get_level(),
            "school": get_school(),
            "classes": get_base_classes(),
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

    def get_description(self):
        # Skip anything inside a table: stat blocks (e.g. Battle Familiar's)
        # can sit mid-description and contain <em>-bearing paragraphs that
        # would otherwise stop the backwards walk below.
        elements = [
            e for e in self.col1.find_all(["p", "ul"]) if e.find_parent("table") is None
        ]

        if not elements:
            return None

        # Work backwards, collecting description elements until we hit metadata.
        first_em = self.col1.find("em")
        if first_em is not None and not self._LEVEL_LINE.match(
            first_em.get_text(" ", strip=True)
        ):
            first_em = None
        desc_elements = []
        for elem in reversed(elements):
            if elem.name == "p":
                text = elem.get_text(" ", strip=True)
                if (
                    text.startswith("Casting Time:")
                    or text.startswith("Source:")
                    or text.startswith("Level ")
                    or self._LEVEL_LINE.match(text)
                ):
                    break
                # The level/school line is the page's first <em>. Other <em>s
                # are italics inside the description (e.g. a stat block name).
                if first_em is not None and elem.find("em") is first_em:
                    break
            desc_elements.append(elem)

        desc_elements = list(reversed(desc_elements))

        lines = []
        for elem in desc_elements:
            if elem.name == "ul":
                for li in elem.find_all("li", recursive=False):
                    li_text = li.get_text(" ", strip=True)
                    if li_text:
                        lines.append(li_text)
            else:
                text = elem.get_text(" ", strip=True)
                if text:
                    lines.append(text)

        return self.format_text("\n".join(lines))

    def get_source(self) -> str | None:
        p = self.col1.find("p")
        if not p or not p.contents:
            return None

        first_text = p.contents[0].strip()  # first child is usually the text
        if first_text.startswith("Source:"):
            return first_text[len("Source:") :].strip()
        return None

    def _get_text(self, element):
        return element.get_text(" ", strip=True) if element else ""

    def to_dict(self):
        """Return all spell info as a dictionary."""
        level_school = self.get_level_and_school()

        return {
            "name": self.get_name(),
            **level_school,
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
            spell = DnD2024SpellParser(spell_name)
            spell.fetch()
            return spell_name, spell.to_dict()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,  # only raised for 5xx, see fetch()
        ) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2**attempt)
    raise last_exc or RuntimeError(f"fetch_spell({spell_name!r}) failed")


if __name__ == "__main__":
    print("Fetching spell list from spell:all …")
    spells = fetch_all_spell_names()
    print(f"Found {len(spells)} spells.")

    results: dict[str, dict] = {}
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
            except Exception as e:
                print(f"  FAILED {spell_name}: {e}")
                failed.append(spell_name)

    sorted_results = dict(sorted(results.items()))

    out_path = "CharacterContent/Spells/spells_dnd2024.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=4, ensure_ascii=False)

    print(f"\nWrote {len(sorted_results)} spells -> {out_path}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
