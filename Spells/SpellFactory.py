import json
from abc import ABC, abstractmethod
from typing import Any, Optional, TextIO

import Definitions
from Utils import StringUtils


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

    def __init__(
        self,
        spell_casting_ability: Optional[Definitions.Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        self.spell_casting_ability = spell_casting_ability
        self._additional_ruling = additional_ruling

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
        self, file: TextIO, show_preparation_checkbox: bool = False
    ):  # writes HTML
        # ── Detect special tags ──────────────────────────────────────────────
        is_concentration = self.duration.lower().startswith("concentration")
        is_ritual = "ritual" in self.casting_time.lower()

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
    """Factory that loads spells from spells.json, the single source of truth."""

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
        additional_ruling: Optional[str] = None,
    ) -> Spell:
        """Create a Spell object from the name."""
        data = cls._load_json()
        if spell_name not in data:
            raise ValueError(f"Spell {spell_name!r} not found in {cls.json_path}.")
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
