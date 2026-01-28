import json
from typing import Optional

import Definitions
from Spells.Definitions import DataSpell, Spell
from Spells.GeneratedSpells import SpellSet


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
    def create(
        cls,
        spell_name: str,
        spell_casting_ability: Optional[Definitions.Ability] = None,
    ) -> Spell:
        """Create a Spell object from the name."""

        if spell_name in SpellSet:
            spell_class = SpellSet[spell_name]
            return spell_class(spell_casting_ability)

        data = cls._load_json()
        if spell_name in data:
            return DataSpell(
                spell_data=data[spell_name], spell_casting_ability=spell_casting_ability
            )
        raise ValueError(f"Spell '{spell_name}' not found in JSON file.")

    @classmethod
    def all_spells(cls):
        """Return all Spell objects."""
        data = cls._load_json()
        return [DataSpell(info) for info in data.values()]

    @classmethod
    def spell_names(cls):
        """Return a list of spell names."""
        return list(cls._load_json().keys())


if __name__ == "__main__":
    # Example usage
    fireball = SpellFactory.create("Fireball")
    print(f"Description: {fireball.description}")
