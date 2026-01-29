import json
from typing import TextIO


class Invocation:
    """Invocation object that wraps JSON invocation data."""

    def __init__(
        self,
        invocation_data: dict,
    ):
        self._data = invocation_data

    # ---------- Property Accessors ---------- #
    @property
    def name(self):
        return self._data.get("name")

    @property
    def level(self):
        return self._data.get("level")

    @property
    def prerequisite(self):
        return self._data.get("prerequisite")

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
        """Return a full dict copy of invocation data."""
        return self._data.copy()

    def __repr__(self):
        return f"<Invocation {self.name!r}, level {self.level}>"

    def write_to_file(self, file: TextIO):
        """Write all invocation info in a readable format to a file."""

        file.write(f"Name: {self.name}\n")
        file.write(f"Level: {self.level}\n")
        file.write(f"Description:\n{self.description}\n")
        file.write(f"Source: {self.source}\n")


class InvocationFactory:
    """Factory that loads a invocation JSON file and creates Invocation objects."""

    json_path = "Invocations/invocations.json"
    _cache = None

    @classmethod
    def _load_json(cls):
        if cls._cache is None:
            with open(cls.json_path, "r", encoding="utf-8") as f:
                cls._cache = json.load(f)
        return cls._cache

    @classmethod
    def create(
        cls,
        invocation_name: str,
    ) -> Invocation:
        """Create a Invocation object from the name."""
        data = cls._load_json()

        if invocation_name not in data:
            raise ValueError(f"Invocation '{invocation_name}' not found in JSON file.")

        return Invocation(
            invocation_data=data[invocation_name],
        )

    @classmethod
    def all_invocations(cls):
        """Return all Invocation objects."""
        data = cls._load_json()
        return [Invocation(info) for info in data.values()]

    @classmethod
    def invocation_names(cls):
        """Return a list of invocation names."""
        return list(cls._load_json().keys())


if __name__ == "__main__":
    # Example usage
    fireball = InvocationFactory.create("Armor of Shadows")
    print(f"Description: {fireball.description}")
