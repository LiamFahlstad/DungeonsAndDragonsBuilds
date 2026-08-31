from typing import Any, Optional

import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import FeatureTarget
from .Spell import Spell


class DataSpell(Spell):
    """Spell backed by a single source of truth: an entry in spells.json."""

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
    ):
        super().__init__(spell_casting_ability, additional_ruling)
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
    def range(self) -> str:
        return str(self._data["range"])

    @property
    def components(self) -> str:
        return str(self._data["components"])

    @property
    def duration(self) -> str:
        return str(self._data["duration"])

    @property
    def description(self) -> str:
        return str(self._data["description"])

    @property
    def source(self) -> str:
        return str(self._data["source"])

    @property
    def usage_tags(self) -> list[str]:
        value = self._data.get("usage_tags", [])
        if not isinstance(value, list):
            raise ValueError(
                f"Invalid usage_tags value for spell {self.name!r}: {value!r}"
            )
        return value

    @property
    def target(self) -> Optional[FeatureTarget]:
        value = self._data.get("target")
        if value is None:
            return None
        try:
            return FeatureTarget(value)
        except ValueError:
            raise ValueError(
                f"Invalid target value for spell {self.name!r}: {value!r}"
            )
