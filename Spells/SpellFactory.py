import json
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, TextIO

import Definitions
from Utils import StringUtils


class School(Enum):
    """The eight schools of magic."""

    ABJURATION = "Abjuration"
    CONJURATION = "Conjuration"
    DIVINATION = "Divination"
    ENCHANTMENT = "Enchantment"
    EVOCATION = "Evocation"
    ILLUSION = "Illusion"
    NECROMANCY = "Necromancy"
    TRANSMUTATION = "Transmutation"


class CastingTimeType(Enum):
    """The broad category of a spell's casting time, ignoring reaction triggers, ritual
    alternatives, and other qualifying detail (e.g. "Reaction, which you take in response
    to taking damage" is just REACTION)."""

    ACTION = "Action"
    BONUS_ACTION = "Bonus Action"
    REACTION = "Reaction"
    MINUTE = "Minute"
    HOUR = "Hour"


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
        return {
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

    def write_to_file(
        self,
        file: TextIO,
        show_preparation_checkbox: bool = False,
        show_classes: bool = False,
    ):  # writes HTML
        # ── Detect special tags ──────────────────────────────────────────────
        is_concentration = self.is_concentration
        is_ritual = self.is_ritual

        # ── Process description ──────────────────────────────────────────────
        description = self.description.strip()

        # Split off the higher-level note, if present
        higher_level_marker = "Using a Higher-Level Spell Slot."
        higher_level_html = ""
        if higher_level_marker in description:
            main_desc, higher_rest = description.split(higher_level_marker, 1)
            main_desc = StringUtils.boxes_to_html(main_desc.strip())
            main_desc = StringUtils.bolden_text_html(main_desc).replace("\n", "<br>")
            higher_rest = StringUtils.boxes_to_html(higher_rest.strip())
            higher_rest = StringUtils.bolden_text_html(higher_rest).replace(
                "\n", "<br>"
            )
            higher_level_html = f"<strong>{higher_level_marker}</strong> {higher_rest}"
        else:
            main_desc = StringUtils.boxes_to_html(description)
            main_desc = StringUtils.bolden_text_html(main_desc).replace("\n", "<br>")

        # ── Level label ──────────────────────────────────────────────────────
        level_label = "Cantrip" if self.level == 0 else f"Level {self.level}"

        # ── Build tag chips ──────────────────────────────────────────────────
        tags_html = ""
        if is_concentration:
            tags_html += "<span class='stag stag-concentration'>Concentration</span> "
        if is_ritual:
            tags_html += "<span class='stag stag-ritual'>Ritual</span> "

        # ── Quick-stats cells ────────────────────────────────────────────────
        # Left ~35%: level, school, components
        school_color = Spell.get_school_color(self.school)
        left_cell = (
            f"<span class='slabel'>{level_label}</span>"
            f"<span class='ssep'>·</span>"
            f"<span class='slabel'>School</span> <span style='color: {school_color}; print-color-adjust: exact; -webkit-print-color-adjust: exact;'>{self.school}</span>"
            f"<span class='ssep'>·</span>"
            f"<span class='slabel'>Components</span> {self.components}"
        )
        # Right ~65%: casting time, range, duration
        duration_display = self.duration
        if is_concentration:
            # Strip the "Concentration, " prefix for display; the tag already shows it
            duration_display = (
                self.duration[len("Concentration, ") :]
                if self.duration.lower().startswith("concentration, ")
                else self.duration
            )
        right_cell = (
            f"<span class='slabel'>Cast</span> {self.casting_time}"
            f"<span class='ssep'>·</span>"
            f"<span class='slabel'>Range</span> {self.range}"
            f"<span class='ssep'>·</span>"
            f"<span class='slabel'>Duration</span> {duration_display}"
        )

        # ── Classes row (optional) ─────────────────────────────────────────────
        classes_html = ""
        if show_classes and self.classes:
            class_chips = " ".join(
                f"<span class='sclass-chip'>{cls}</span>" for cls in self.classes
            )
            classes_html = (
                f"<span class='slabel'>Classes</span> {class_chips}"
            )

        # ── Spell name with optional checkbox ─────────────────────────────────
        spell_name_display = self.name
        if (
            show_preparation_checkbox and self.level > 0
        ):  # Don't show checkbox for cantrips
            spell_name_display = (
                f"<span class='spell-prep-checkbox'></span> {self.name}"
            )

        # ── Write card ───────────────────────────────────────────────────────
        file.write("<table class='spell-card'>\n")

        # Name header row (full width)
        file.write(
            f"<tr><th class='spell-name' colspan='2'>{spell_name_display}"
            f"{(' ' + tags_html.strip()) if tags_html else ''}"
            f"</th></tr>\n"
        )

        # Quick-stats row
        file.write(
            f"<tr class='spell-quickstats'>"
            f"<td class='sqs-left'>{left_cell}</td>"
            f"<td class='sqs-right'>{right_cell}</td>"
            f"</tr>\n"
        )

        # Classes row (if requested)
        if classes_html:
            file.write(
                f"<tr class='spell-classes-row'>"
                f"<td colspan='2'>{classes_html}</td>"
                f"</tr>\n"
            )

        # Description row
        file.write(
            f"<tr class='spell-desc-row'>"
            f"<td class='sdesc-text' colspan='2'>{main_desc}</td>"
            f"</tr>\n"
        )

        # Higher-level row (if present)
        if higher_level_html:
            file.write(
                f"<tr class='spell-higher-row'>"
                f"<td class='sdesc-text' colspan='2'>{higher_level_html}</td>"
                f"</tr>\n"
            )

        # Additional ruling row (if present) - e.g. a Channel Divinity option
        # that lets this specific character cast the spell without a slot.
        if self._additional_ruling:
            ruling_html = StringUtils.bolden_text_html(
                StringUtils.boxes_to_html(self._additional_ruling.strip())
            ).replace("\n", "<br>")
            file.write(
                f"<tr class='spell-higher-row'>"
                f"<td class='sdesc-text' colspan='2'><strong>Ruling.</strong> {ruling_html}</td>"
                f"</tr>\n"
            )

        file.write("</table>\n")

    def __repr__(self):
        return f"<Spell {self.name!r}, level {self.level}>"


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


class SpellFactory:
    """Factory that loads spells from multiple JSON sources and merges them.

    Sources are merged whole-record (never per-field) in priority order,
    highest priority first. For any given spell name, the entire record from
    the highest-priority source that has that name wins outright; lower
    priority sources only fill in spells missing from higher ones.
    """

    # Highest priority first; each subsequent path only fills gaps.
    json_paths = (
        "Spells/spells_dnd2024.json",
        "Spells/spells_aidedd.json",
        "Spells/spells_dnd5e.json",
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
