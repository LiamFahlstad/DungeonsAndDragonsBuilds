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
        if "hunter" in name:
            pass

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

    def get_name(self):
        return self._get_text(self.col1.find("h1"))

    def get_level_and_school(self):
        return self._get_text(self.col1.find("div", class_="ecole"))

    def get_casting_time(self):
        return self._clean_field(self.col1.find("div", class_="t"))

    def get_range(self):
        return self._clean_field(self.col1.find("div", class_="r"))

    def get_components(self):
        return self._clean_field(self.col1.find("div", class_="c"))

    def get_duration(self):
        return self._clean_field(self.col1.find("div", class_="d"))

    def get_description(self):
        return self._get_text(self.col1.find("div", class_="description"))

    def get_source(self):
        return self._get_text(self.col1.find("div", class_="source"))

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
        return {
            "name": self.get_name(),
            "level_and_school": self.get_level_and_school(),
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
