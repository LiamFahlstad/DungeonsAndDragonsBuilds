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


def test_track_runs_from_level_3_to_20():
    track = spellcasting_table("Fighter")
    assert track.level_label == "Fighter level"
    assert list(track.levels) == list(range(3, 21))
    series = dict(track.series)
    assert list(series) == [
        "Prepared spells",
        "1st slots",
        "2nd slots",
        "3rd slots",
        "4th slots",
    ]
    # Level 3, then level 4 (the first of the 4-6 run), then level 20.
    for column, expected in (
        (0, ("3", "2", "-", "-", "-")),
        (1, ("4", "3", "-", "-", "-")),
        (-1, ("13", "4", "3", "3", "1")),
    ):
        assert tuple(values[column] for values in series.values()) == expected


def test_track_merges_runs_of_the_same_value_into_one_cell():
    from Presentation.FeatureCards import improved_description_to_html

    html = improved_description_to_html([spellcasting_table("Fighter")])
    # 1st slots: 2 at level 3, 3 at levels 4-6, 4 from level 7 to 20.
    assert "<td>2</td><td colspan='3'>3</td><td colspan='14'>4</td>" in html
