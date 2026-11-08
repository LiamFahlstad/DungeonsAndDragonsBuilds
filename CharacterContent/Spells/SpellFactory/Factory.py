import json
from typing import Any, Optional

import Core.Definitions as Definitions
from .DataSpell import DataSpell
from .Spell import Spell


class SpellFactory:
    """Factory for every spell: a spell written as a class
    (CharacterContent/Spells/SpellClasses, see SpellFactory/ClassSpell.py)
    if it has one, otherwise its JSON record.

    The JSON sources are merged whole-record (never per-field) in priority
    order, highest priority first. For any given spell name, the entire record
    from the highest-priority source that has that name wins outright; lower
    priority sources only fill in spells missing from higher ones. A class
    wins over all of them.
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
                    source_data = json.load(f)
                # Try to load extended data for this source
                extended_path = path[:-5] + "_extended.json"
                try:
                    with open(extended_path, "r", encoding="utf-8") as f:
                        extended_data = json.load(f)
                except FileNotFoundError:
                    extended_data = {}
                # Merge extended fields into matching spells
                for name, extra_fields in extended_data.items():
                    if name in source_data:
                        source_data[name].update(extra_fields)
                # Improved descriptions (blocks, as JSON) belong to this
                # source's wording of the spell, so they ride on its record.
                for name, blocks in cls._load_improved(path).items():
                    if name in source_data:
                        source_data[name]["improved_description"] = blocks
                # So do the combat effects read from that wording.
                for name, entry in cls._load_combat_effects(path).items():
                    if name in source_data:
                        source_data[name]["combat_effects"] = entry
                merged.update(source_data)
            cls._cache = merged
        return cls._cache

    @staticmethod
    def improved_path(path: str) -> str:
        """spells_dnd2024.json -> spells_dnd2024_improved.json"""
        return path[:-5] + "_improved.json"

    @classmethod
    def _load_improved(cls, path: str) -> dict[str, Any]:
        try:
            with open(cls.improved_path(path), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @staticmethod
    def combat_effects_path(path: str) -> str:
        """spells_dnd2024.json -> spells_dnd2024_combat_effects.json"""
        return path[:-5] + "_combat_effects.json"

    @classmethod
    def _load_combat_effects(cls, path: str) -> dict[str, Any]:
        """What casting each spell does in a fight (Spell.combat_effects), for
        the spells the source's companion file has checked."""
        try:
            with open(cls.combat_effects_path(path), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @classmethod
    def create(
        cls,
        spell_name: str,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        additional_ruling: Optional[str] = None,
        grant_source: Optional[str] = None,
    ) -> Spell:
        """Create a Spell object from the name: its class, or its record."""
        spell_class = cls._spell_classes().get(spell_name)
        if spell_class is not None:
            return spell_class(spell_casting_ability, additional_ruling, grant_source)
        data = cls._load_json()
        if spell_name not in data:
            raise ValueError(
                f"Spell {spell_name!r} has no class and isn't in any of"
                f" {cls.json_paths}."
            )
        return DataSpell(
            spell_data=data[spell_name],
            spell_casting_ability=spell_casting_ability,
            additional_ruling=additional_ruling,
            grant_source=grant_source,
        )

    @classmethod
    def all_spells(cls) -> list[Spell]:
        """Every spell: its class if it has one, otherwise its record."""
        return [cls.create(name) for name in cls.spell_names()]

    @classmethod
    def spell_names(cls) -> list[str]:
        """Every spell's name: those of the JSON records, then those only a
        class has."""
        names = list(cls._load_json())
        known = set(names)
        return names + [name for name in cls._spell_classes() if name not in known]

    @staticmethod
    def _spell_classes() -> dict:
        """The spells written as classes, by name. Imported when first asked
        for: the classes import this package's ClassSpell."""
        from CharacterContent.Spells.SpellClasses import SPELL_CLASSES

        return SPELL_CLASSES


if __name__ == "__main__":
    # Example usage
    fireball = SpellFactory.create("Fireball")
    print(f"Description: {fireball.description}")
