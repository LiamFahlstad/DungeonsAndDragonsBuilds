import dataclasses
import re
from typing import Any, Optional

import Core.Definitions as Definitions
from .Spell import Spell
from .SpellFields import CastingTime, Components

_RITUAL_NOTE = re.compile(r"\(\s*ritual\s*\)", re.IGNORECASE)


class DataSpell(Spell):
    """A spell as its scraped record (spells_<source>.json) says it: what
    SpellFactory gives for a spell without a class, and what the converter
    writes a class from and checks it against. A record holds only the
    rules, so a DataSpell has Spell's defaults for usage_tags, target, the
    improved description and combat effects: those are written in the
    spell's class."""

    _REQUIRED_FIELDS = (
        "name",
        "level",
        "school",
        "classes",
        "casting_time",
        "range",
        "components",
        "duration",
        "description",
        "source",
    )

    def __init__(
        self,
        spell_data: dict[str, Any],
        spell_casting_ability: Optional[Definitions.Ability] = None,
        additional_ruling: Optional[str] = None,
        grant_source: Optional[str] = None,
    ):
        super().__init__(spell_casting_ability, additional_ruling, grant_source)
        missing = [f for f in self._REQUIRED_FIELDS if f not in spell_data]
        if missing:
            raise ValueError(
                f"Spell data for {spell_data.get('name', '<unknown>')!r} is missing "
                f"required field(s): {', '.join(missing)}"
            )
        self._data = spell_data

    @property
    def name(self) -> str:
        return str(self._data["name"])

    @property
    def level(self) -> int:
        value = self._data["level"]
        if not isinstance(value, int):
            raise ValueError(f"Invalid level value for spell {self.name!r}: {value!r}")
        return value

    @property
    def school(self) -> str:
        return str(self._data["school"])

    @property
    def classes(self) -> list[str]:
        value = self._data["classes"]
        if not isinstance(value, list):
            raise ValueError(
                f"Invalid classes value for spell {self.name!r}: {value!r}"
            )
        return value

    @property
    def casting_time(self) -> str:
        return str(self._data["casting_time"])

    @property
    def casting_time_spec(self) -> CastingTime:
        """The casting time, a ritual also when the record says so where the
        casting time doesn't: the 2014 source's "ritual": true key, or a
        "(Ritual)" written into the school (Wristpocket)."""
        spec = super().casting_time_spec
        if spec.ritual or spec.trigger:
            return spec
        if self._data.get("ritual") is True or _RITUAL_NOTE.search(self.school):
            return dataclasses.replace(spec, ritual=True)
        return spec

    @property
    def range(self) -> str:
        return str(self._data["range"])

    @property
    def components(self) -> str:
        return str(self._data["components"])

    @property
    def components_spec(self) -> Components:
        # A record without components (null) has none, not the text "None".
        return Components.from_text(self._data["components"] or "")

    @property
    def duration(self) -> str:
        return str(self._data["duration"])

    @property
    def description(self) -> str:
        return str(self._data["description"])

    @property
    def source(self) -> str:
        return str(self._data["source"])
