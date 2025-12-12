import json


class Spell:
    """Spell object that wraps JSON spell data."""

    def __init__(self, spell_data: dict):
        self._data = spell_data

    # ---------- Property Accessors ---------- #
    @property
    def name(self):
        return self._data.get("name")

    @property
    def level(self):
        return self._data.get("level")

    @property
    def school(self):
        return self._data.get("school")

    @property
    def classes(self):
        return self._data.get("classes", [])

    @property
    def casting_time(self):
        return self._data.get("casting_time")

    @property
    def range(self):
        return self._data.get("range")

    @property
    def components(self):
        return self._data.get("components")

    @property
    def duration(self):
        return self._data.get("duration")

    @property
    def description(self):
        text = self._data.get("description")

        def replace_last(text, old, new):
            parts = text.rsplit(old, 1)  # split from the right, max 1 split
            return new.join(parts)

        def inject_newline(text):
            go = True
            while go:
                try:
                    index = text.index(" . ")
                    text = replace_last(text[:index], ". ", ".\n") + text[index:]
                    text = text.replace(" . ", ":\n")
                    pass
                except ValueError:
                    go = False
            return text

        return inject_newline(text)

    @property
    def source(self):
        return self._data.get("source")

    def to_dict(self):
        """Return a full dict copy of spell data."""
        return self._data.copy()

    def __repr__(self):
        return f"<Spell {self.name!r}, level {self.level}>"

    def write_to_file(self, file):
        """Write all spell info in a readable format to a file."""

        file.write(f"Name: {self.name}\n")
        file.write(f"Level: {self.level}\n")
        file.write(f"School: {self.school}\n")
        file.write(f"Classes: {', '.join(self.classes)}\n")
        file.write(f"Casting Time: {self.casting_time}\n")
        file.write(f"Range: {self.range}\n")
        file.write(f"Components: {self.components}\n")
        file.write(f"Duration: {self.duration}\n")
        file.write(f"Description:\n{self.description}\n")
        file.write(f"Source: {self.source}\n")


class SpellFactory:
    """Factory that loads a spell JSON file and creates Spell objects."""

    json_path = "Spells/spells.json"
    _cache = None

    @classmethod
    def _load_json(cls):
        if cls._cache is None:
            with open(cls.json_path, "r", encoding="utf-8") as f:
                cls._cache = json.load(f)
        return cls._cache

    @classmethod
    def create(cls, spell_name: str) -> Spell:
        """Create a Spell object from the name."""
        data = cls._load_json()

        if spell_name not in data:
            raise ValueError(f"Spell '{spell_name}' not found in JSON file.")

        return Spell(data[spell_name])

    @classmethod
    def all_spells(cls):
        """Return all Spell objects."""
        data = cls._load_json()
        return [Spell(info) for info in data.values()]

    @classmethod
    def spell_names(cls):
        """Return a list of spell names."""
        return list(cls._load_json().keys())


if __name__ == "__main__":
    # Example usage
    fireball = SpellFactory.create("Fireball")
    print(f"Description: {fireball.description}")
