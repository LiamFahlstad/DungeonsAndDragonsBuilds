import json
from typing import Any, Optional

import Core.Definitions as Definitions
from .DataSpell import DataSpell
from .Spell import Spell


class SpellFactory:
    """Factory that loads spells from multiple JSON sources and merges them.

    Sources are merged whole-record (never per-field) in priority order,
    highest priority first. For any given spell name, the entire record from
    the highest-priority source that has that name wins outright; lower
    priority sources only fill in spells missing from higher ones.
    """

    # Highest priority first; each subsequent path only fills gaps.
    json_paths = (
        "CharacterContent/Spells/spells_dnd2024.json",
        "CharacterContent/Spells/spells_aidedd.json",
        "CharacterContent/Spells/spells_dnd5e.json",
    )
    _cache = None

    @classmethod
    def _load_json(cls):
        if cls._cache is None:
            merged: dict[str, Any] = {}
            # Apply lowest priority first, then overwrite with higher
            # priority sources so higher-priority entries win outright.
            for path in reversed(cls.json_paths):
                with open(path, "r", encoding="utf-8") as f:
                    merged.update(json.load(f))
            cls._cache = merged
        return cls._cache

    @classmethod
    def create(
        cls,
        spell_name: str,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        additional_ruling: Optional[str] = None,
    ) -> Spell:
        """Create a Spell object from the name."""
        data = cls._load_json()
        if spell_name not in data:
            raise ValueError(
                f"Spell {spell_name!r} not found in any of {cls.json_paths}."
            )
        return DataSpell(
            spell_data=data[spell_name],
            spell_casting_ability=spell_casting_ability,
            additional_ruling=additional_ruling,
        )

    @classmethod
    def all_spells(cls):
        """Return all Spell objects."""
        return [DataSpell(info) for info in cls._load_json().values()]

    @classmethod
    def spell_names(cls):
        """Return a list of spell names."""
        return list(cls._load_json().keys())


if __name__ == "__main__":
    # Example usage
    fireball = SpellFactory.create("Fireball")
    print(f"Description: {fireball.description}")
