"""The one-third casters' Spellcasting cards print a prepared-spells and
spell-slot table built from data; check it against each subclass's source
table."""

import pathlib

import pytest

from CharacterContent.Features.SubClassFeatures.ThirdCasterSpellcasting import (
    prepared_spells,
    spell_slots,
    spellcasting_table,
)

SOURCES = pathlib.Path(__file__).parent.parent / "SourceTexts" / "SubclassTexts2024"


def _source_rows(name: str) -> dict[int, tuple[int, ...]]:
    """{class level: (prepared spells, 1st, 2nd, 3rd, 4th)} from the
    subclass's Spellcasting table."""
    rows = {}
    for line in (SOURCES / f"{name}.txt").read_text(encoding="utf-8").splitlines():
        cells = line.split("\t")
        if len(cells) == 6 and cells[0].isdigit():
            rows[int(cells[0])] = tuple(0 if c == "-" else int(c) for c in cells[1:])
    return rows


@pytest.mark.parametrize(
    "name", ["eldritch_knight", "arcane_trickster", "warrior_of_the_mystic_arts"]
)
def test_prepared_spells_and_slots_match_the_source_table(name):
    rows = _source_rows(name)
    assert sorted(rows) == list(range(3, 21))
    for level, (prepared, *slots) in rows.items():
        assert prepared_spells(level) == prepared, level
        assert spell_slots(level) == tuple(slots), level


def test_table_merges_levels_with_the_same_numbers():
    table = spellcasting_table("Fighter")
    assert table.columns[0] == "Fighter level"
    assert table.rows[0] == ("3", "3", "2", "-", "-", "-")
    assert ("4-6", "4", "3", "-", "-", "-") in table.rows
    assert table.rows[-1] == ("20", "13", "4", "3", "3", "1")
