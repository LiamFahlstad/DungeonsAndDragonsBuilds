import re
from abc import ABC, abstractmethod
from typing import Optional, TextIO

import Core.Definitions as Definitions
from .Enums import CastingTimeType, School
from .Writer import write_spell_to_file


class Spell(ABC):
    """Abstract base spell interface."""

    # School of magic color mapping
    SCHOOL_COLORS = {
        "Abjuration": "#4a90d9",
        "Conjuration": "#d4af37",
        "Divination": "#a0a0a0",
        "Enchantment": "#d44fa0",
        "Evocation": "#d94a4a",
        "Illusion": "#8b4ad9",
        "Necromancy": "#4a8b4a",
        "Transmutation": "#c87941",
    }

    # Matches ranges like "150 feet", "1,000 feet", "60ft", "90 ft", "120 feet."
    _RANGE_FEET_PATTERN = re.compile(
        r"^([\d,]+)\s*(?:feet|foot|ft)\.?$", re.IGNORECASE
    )
    # Matches ranges like "1 mile", "500 miles"
    _RANGE_MILE_PATTERN = re.compile(r"^([\d,]+)\s*miles?$", re.IGNORECASE)

    _SECONDS_PER_DURATION_UNIT = {
        "round": 6,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }
    _DURATION_INSTANTANEOUS_PATTERN = re.compile(
        r"^instant(?:aneous|anous)\b", re.IGNORECASE
    )
    _DURATION_CONCENTRATION_PREFIX = re.compile(r"^concentration,?\s*", re.IGNORECASE)
    _DURATION_UP_TO_PREFIX = re.compile(r"^up to\s*", re.IGNORECASE)
    _DURATION_VALUE_PATTERN = re.compile(
        r"^(\d+)\s*(round|minute|hour|day)s?$", re.IGNORECASE
    )

    def __init__(
        self,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        self.spell_casting_ability = spell_casting_ability
        self._additional_ruling = additional_ruling

    @property
    def additional_ruling(self) -> Optional[str]:
        """Character-specific ruling text attached when this spell was granted (e.g. a
        Channel Divinity option that lets it be cast without a slot), or None."""
        return self._additional_ruling

    # ---------- Required properties ---------- #

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def level(self) -> int:
        pass

    @property
    @abstractmethod
    def school(self) -> str:
        pass

    @property
    @abstractmethod
    def classes(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def casting_time(self) -> str:
        pass

    @property
    @abstractmethod
    def range(self) -> str:
        pass

    @property
    @abstractmethod
    def components(self) -> str:
        pass

    @property
    @abstractmethod
    def duration(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def source(self) -> str:
        pass

    @property
    def usage_tags(self) -> list[str]:
        """Zero or more of "heal"/"buff"/"control"/"damage"/"utility" flagging what the
        spell's effect functionally does, for a quick-scan chip on the card. Defaults to
        empty (no chips) for any Spell subclass that doesn't provide its own data for this."""
        return []

    # ---------- Interpreted properties (derived from the raw strings above) ---------- #

    @property
    def range_feet(self) -> Optional[int]:
        """The range in feet, or None if it isn't a plain distance (e.g. Self, Touch, Sight, Special, Unlimited)."""
        text = self.range.strip()
        match = self._RANGE_MILE_PATTERN.match(text)
        if match:
            return int(match.group(1).replace(",", "")) * 5280
        match = self._RANGE_FEET_PATTERN.match(text)
        if match:
            return int(match.group(1).replace(",", ""))
        return None

    @property
    def school_enum(self) -> School:
        """The school of magic as a School enum, ignoring any parenthetical suffix (e.g. "(Dunamancy)")."""
        base_name = self.school.split(" (", 1)[0].strip()
        try:
            return School(base_name)
        except ValueError:
            raise ValueError(
                f"Unknown school of magic for spell {self.name!r}: {self.school!r}"
            )

    def _has_component_letter(self, letter: str) -> bool:
        prefix = self.components.split("(", 1)[0]
        tokens = {token.strip() for token in prefix.split(",")}
        return letter in tokens

    @property
    def has_verbal(self) -> bool:
        return self._has_component_letter("V")

    @property
    def has_somatic(self) -> bool:
        return self._has_component_letter("S")

    @property
    def has_material(self) -> bool:
        return self._has_component_letter("M")

    @property
    def material_description(self) -> Optional[str]:
        """The text inside the M(...) component, or None if there is no material component."""
        if not self.has_material:
            return None
        start = self.components.find("(")
        end = self.components.rfind(")")
        if start == -1 or end == -1 or end <= start:
            return None
        return self.components[start + 1 : end].strip()

    @property
    def is_ritual(self) -> bool:
        return "ritual" in self.casting_time.lower()

    @property
    def casting_time_type(self) -> CastingTimeType:
        """The broad category of the casting time (see CastingTimeType). When multiple
        options are given (e.g. "1 action or 8 hours"), the first one is used."""
        text = self.casting_time.split(" or ", 1)[0].strip().lower()
        if "reaction" in text:
            return CastingTimeType.REACTION
        if "bonus action" in text:
            return CastingTimeType.BONUS_ACTION
        if "action" in text:
            return CastingTimeType.ACTION
        if "minute" in text:
            return CastingTimeType.MINUTE
        if "hour" in text:
            return CastingTimeType.HOUR
        raise ValueError(
            f"Unrecognized casting time for spell {self.name!r}: {self.casting_time!r}"
        )

    @property
    def is_concentration(self) -> bool:
        return self.duration.lower().startswith("concentration")

    @property
    def duration_seconds(self) -> Optional[int]:
        """The duration in seconds (Instantaneous is 0), or None if it isn't a fixed length
        (e.g. Special, Until dispelled). Rounds are 6 seconds. When multiple durations are
        given (e.g. "Instantaneous or 1 hour"), the first one is used."""
        text = self.duration.strip()
        if self._DURATION_INSTANTANEOUS_PATTERN.match(text):
            return 0
        lowered = text.lower()
        if lowered == "special" or lowered.startswith("until dispelled"):
            return None
        text = self._DURATION_CONCENTRATION_PREFIX.sub("", text)
        text = self._DURATION_UP_TO_PREFIX.sub("", text)
        text = text.split(" or ", 1)[0].strip()
        match = self._DURATION_VALUE_PATTERN.match(text)
        if not match:
            return None
        value, unit = match.groups()
        return int(value) * self._SECONDS_PER_DURATION_UNIT[unit.lower()]

    # ---------- Shared behavior ---------- #

    @staticmethod
    def get_school_color(school: str) -> str:
        """Return the color hex code for a school of magic, or a default gray if unknown."""
        return Spell.SCHOOL_COLORS.get(school, "#999999")

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "level": self.level,
            "school": self.school,
            "classes": self.classes,
            "casting_time": self.casting_time,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "description": self.description,
            "source": self.source,
        }
        if self.usage_tags:
            result["usage_tags"] = self.usage_tags
        return result

    def write_to_file(
        self,
        file: TextIO,
        show_preparation_checkbox: bool = False,
        show_classes: bool = False,
    ):
        write_spell_to_file(
            self,
            file,
            show_preparation_checkbox=show_preparation_checkbox,
            show_classes=show_classes,
        )

    def __repr__(self):
        return f"<Spell {self.name!r}, level {self.level}>"
