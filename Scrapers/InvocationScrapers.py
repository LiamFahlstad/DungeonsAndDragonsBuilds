from typing import TextIO

import requests
from bs4 import BeautifulSoup


class InvocationNotFoundError(Exception):
    """Raised when the invocation does not exist on AideDD."""

    pass


class InvocationParser:
    BASE_URL = "https://www.aidedd.org/invocation/"

    def __init__(self, invocation_name: str):
        self.original_name = invocation_name
        self.invocation_name = self._slugify(invocation_name)
        self.url = f"{self.BASE_URL}{self.invocation_name}"
        self.soup = None
        self.col1 = None

    def _slugify(self, name: str) -> str:
        """Convert a invocation name into the URL-friendly format used by AideDD (no regex)."""
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
        """Download the invocation page HTML and prepare the soup object."""
        response = requests.get(self.url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, "html.parser")
        self.col1 = self.soup.find("div", class_="col1")
        if not self.col1:
            raise ValueError(
                "Could not find main invocation content. Check if the invocation name is correct."
            )

        warning = self.col1.find("p", class_="warning")
        if warning:
            raise InvocationNotFoundError(
                f"Invocation '{self.original_name}' ({self.url}) does not exist on AideDD."
            )

    # -------------------

    # -------------------
    # Individual field getters
    # -------------------

    def get_name(self):
        return self._get_text(self.col1.find("h1"))

    def get_description(self):
        return self._get_text(self.col1.find("div", class_="description"))

    def get_prerequisite(self):
        return (
            self._get_text(self.col1.find("div", class_="prerequis"))
            .split("Prerequisite: ")[-1]
            .strip()
        )

    def get_level(self) -> int:
        prerequisite = self.get_prerequisite()
        if "Level" not in prerequisite:
            return 0
        return int(prerequisite.split("Level ")[-1].strip().split("+")[0])

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
        """Return all invocation info as a dictionary."""
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "prerequisite": self.get_prerequisite(),
            "level": self.get_level(),
            "source": self.get_source(),
        }

    def print_info(self):
        """Print all invocation info in a readable format."""
        data = self.to_dict()
        for key, value in data.items():
            print(f"{key.title().replace('_', ' ')}: {value}")

    def write_to_file(self, file: TextIO):
        """Write all invocation info in a readable format to a file."""
        data = self.to_dict()
        for key, value in data.items():
            file.write(f"{key.title().replace('_', ' ')}: {value}\n")


if __name__ == "__main__":
    invocations = [
        "Agonizing Blast",
        "Armor of Shadows",
        "Ascendant Step",
        "Devil's Sight",
        "Devouring Blade",
        "Eldritch Mind",
        "Eldritch Smite",
        "Eldritch Spear",
        "Fiendish Vigor",
        "Gaze of Two Minds",
        "Gift of the Depths",
        "Gift of the Protectors",
        "Investment of the Chain Master",
        "Lessons of the First Ones",
        "Lifedrinker",
        "Mask of the Many Faces",
        "Master of Myriad Forms",
        "Misty Visions",
        "One with Shadows",
        "Otherworldly Leap",
        "Pact of the Blade",
        "Pact of the Chain",
        "Pact of the Tome",
        "Repelling Blast",
        "Thirsting Blade",
        "Visions of Distant Realms",
        "Whispers of the Grave",
        "Witch Sight",
    ]

    master_dict = {}
    for invocation_name in invocations:
        invocation = InvocationParser(invocation_name)
        invocation.fetch()
        invocation_dict = invocation.to_dict()
        master_dict[invocation_name] = invocation_dict

    dict_per_level = {}
    for invocation_name, invocation_data in master_dict.items():
        level = invocation_data["level"]
        if level not in dict_per_level:
            dict_per_level[level] = {}
        dict_per_level[level][invocation_name] = invocation_data

    with open("Invocations/Definitions.py", "w", encoding="utf-8") as f:
        for level in sorted(dict_per_level.keys()):
            f.write(f"class InvocationsLevel{level}(str, Enum):\n")
            for invocation_name, invocation_data in dict_per_level[level].items():
                a = (
                    invocation_name.replace(" ", "_")
                    .replace("'", "")
                    .replace("-", "_")
                    .upper()
                )
                f.write(f"    {a} : {invocation_name}\n")
