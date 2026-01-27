import re

import requests
from bs4 import BeautifulSoup


class SpellNotFoundError(Exception):
    """Raised when the spell does not exist on AideDD."""

    pass


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

    def write_to_file(self, file):
        """Write all spell info in a readable format to a file."""
        data = self.to_dict()
        for key, value in data.items():
            file.write(f"{key.title().replace('_', ' ')}: {value}\n")


if __name__ == "__main__":
    spells = ["Mage Armor", "Fireball", "Cure Wounds", "Guidance"]

    for spell_name in spells:
        spell = SpellParser(spell_name)
        spell.fetch()
        spell.print_info()
        print("-" * 40)
