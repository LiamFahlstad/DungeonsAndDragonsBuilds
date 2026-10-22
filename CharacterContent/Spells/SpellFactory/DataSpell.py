from typing import Any, Optional

import Core.Definitions as Definitions
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, blocks_from_json
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
    def improved_description(self) -> Optional[list[Block]]:
        value = self._data.get("improved_description")
        if value is None:
            return None
        try:
            return blocks_from_json(value)
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError(
                f"Invalid improved description for spell {self.name!r}: {error}"
            ) from error

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
            ) from None
