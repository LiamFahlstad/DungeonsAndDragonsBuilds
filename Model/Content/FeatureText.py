"""Improved descriptions: a feature's rules restructured for reading at a
glance - short paragraphs, label/value facts, tables and named options -
instead of the source's wall of prose.

An improved description is not a summary: it keeps every rule of the
source text, just laid out so the numbers and choices can be found without
rereading.
Guidelines:

- Lead with one or two sentences saying what the feature is for.
- Put the numbers a player looks up mid-session in Facts, written as
  formulas ("8 + Wisdom modifier + Proficiency Bonus"), never as today's
  values: the sheet is printed once and kept as the character levels up.
  dc_formula() writes a save DC this way.
- Give each choice the feature offers its own Option (Divine Spark, Turn
  Undead), opening with Action, Range and Target rows, then what it does.
- Use a Table when an option has parallel outcomes (heal or harm; a failed
  or a successful save).
- Don't repeat what the card already shows: use boxes and dice tracks have
  their own panel.
- A companion's or form's stat block goes in a StatBlock, the one block
  allowed to show today's numbers (next to their formulas, as a stat block
  does).

The source text stays in Feature.get_description(): it's what the
improved version is checked against, and RunCharacterCreator.py
--source-text prints it instead.

This module only holds the structure; Presentation/FeatureCards.py renders
it.
"""

from dataclasses import dataclass, field

from Core.Definitions import Ability


@dataclass(frozen=True)
class Paragraph:
    """A short paragraph of prose."""

    text: str


@dataclass(frozen=True)
class Facts:
    """Label/value rows, e.g. ("Save DC", "13 = 8 + Wisdom +3 + ...")."""

    rows: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Table:
    """A table with a header row."""

    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def __post_init__(self):
        for row in self.rows:
            if len(row) != len(self.columns):
                raise ValueError(
                    f"Table row {row} has {len(row)} cells but there are "
                    f"{len(self.columns)} columns"
                )


@dataclass(frozen=True)
class Option:
    """One named choice or sub-effect of a feature (e.g. Divine Spark): a
    box headed by its name, holding its own blocks - usually Facts that open
    with Action, Range and Target rows."""

    name: str
    blocks: tuple["Block", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StatBlock:
    """A creature's stat block (a companion, a Wild Shape form), already
    formatted as HTML by the creature formatters. Unlike the other blocks it
    shows the creature at the character's current level, beside the
    formulas, as the source text's stat blocks do."""

    html: str


Block = Paragraph | Facts | Table | Option | StatBlock


def dc_formula(ability: Ability) -> str:
    """A save DC as its formula: "8 + Wisdom modifier + Proficiency Bonus"."""
    return f"8 + {ability.value} modifier + Proficiency Bonus"
