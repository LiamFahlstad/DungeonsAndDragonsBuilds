import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TextIO

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class SpellNotFoundError(Exception):
    """Raised when the spell does not exist on dnd5."""

    pass


class SpellParser:
    BASE_URL = "https://dnd2024.wikidot.com/"

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
        for slugify in slugygifies:
            spell_name_slug = slugify(self.original_name)
            self.url = f"{self.BASE_URL}spell:{spell_name_slug}"
            response = requests.get(self.url)
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.text, "html.parser")
                break

            # response.raise_for_status()
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

    # -------------------
    # Individual field getters
    # -------------------

    def format_text(self, text: str) -> str:
        return text.replace("´", "'")

    def get_name(self):
        return self.original_name

    def get_level_and_school(self) -> dict:
        em = self.col1.find("em")
        if not em:
            raise ValueError("Could not find level/school text")

        text = self.format_text(em.text.strip())

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
        paragraphs = self.col1.find_all("p")

        # description is the last paragraph
        if not paragraphs:
            return None

        texts = []
        for p in reversed(paragraphs):
            text = p.get_text(" ", strip=True)
            if text.startswith("Casting Time:") or text.startswith("Level "):
                break
            texts.append(text)
        text = " ".join(reversed(texts))
        if "Faerun" in text:
            pass

        return self.format_text(text)

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


def fetch_spell(spell_name: str):
    spell = SpellParser(spell_name)
    spell.fetch()
    return spell_name, spell.to_dict()


if __name__ == "__main__":
    with open("Scrapers/spells_list_eberron.txt", encoding="utf-8") as f:
        spells = [line.strip() for line in f if line.strip()]

    results: dict[str, dict] = {}

    # Adjust depending on site rate limits
    MAX_WORKERS = 7

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
                print(f"Failed to fetch {spell_name}: {e}")

    # Sort alphabetically by spell name
    sorted_results = dict(sorted(results.items()))

    with open("Scrapers/spells_data_eberron.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=4, ensure_ascii=False)
