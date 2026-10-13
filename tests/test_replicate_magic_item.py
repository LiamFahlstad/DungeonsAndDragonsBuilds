"""Replicate Magic Item's plan catalogue and Plans Known / Magic Items
progressions are data the card renders from; check them against the source
text so they can't drift."""

import pathlib
import re

from CharacterContent.Features.ClassFeatures.Artificer import ArtificerFeatures
from CharacterContent.Features.ClassFeatures.Artificer.ArtificerFeatures import (
    MAGIC_ITEM_PLANS,
    ReplicateMagicItem,
    magic_items_allowed,
    plans_known,
)
from Presentation.FeatureCards import improved_description_to_html
from tests._snapshot_helpers import ALL_BUILDS

ARTIFICER_TEXT = (
    pathlib.Path(__file__).parent.parent
    / "SourceTexts"
    / "ClassTexts"
    / "artificer.txt"
)


def _artificer_table_columns() -> dict[int, tuple[int, int]]:
    """{Artificer level: (Plans Known, Magic Items)} from the class table."""
    columns = {}
    for line in ARTIFICER_TEXT.read_text(encoding="utf-8").splitlines():
        cells = line.split("\t")
        if len(cells) == 10 and cells[0].isdigit() and cells[1].isdigit():
            columns[int(cells[0])] = (int(cells[1]), int(cells[2]))
    return columns


def test_plans_known_and_magic_items_match_the_artificer_table():
    columns = _artificer_table_columns()
    assert sorted(columns) == list(range(2, 21))
    for level, (known, items) in columns.items():
        assert plans_known(level) == known, level
        assert magic_items_allowed(level) == items, level
    assert plans_known(1) == magic_items_allowed(1) == 0


def _source_plan_tables(source: str) -> dict[int, list[tuple[str, str]]]:
    tables: dict[int, list[tuple[str, str]]] = {}
    current = None
    for line in source.splitlines():
        header = re.fullmatch(r"Magic Item Plans \(Artificer Level (\d+)\+\)", line)
        if header:
            current = tables.setdefault(int(header.group(1)), [])
        elif (
            current is not None
            and "\t" in line
            and not line.startswith("Magic Item Plan\t")
        ):
            plan, attunement = line.split("\t")
            current.append((plan.strip(), attunement.strip()))
    return tables


def test_plan_catalogue_matches_the_source_tables():
    source = ReplicateMagicItem().get_description(None)  # type: ignore[arg-type]
    tables = _source_plan_tables(source)
    assert sorted(tables) == sorted(MAGIC_ITEM_PLANS)
    for level, rows in tables.items():
        catalogue = MAGIC_ITEM_PLANS[level]
        assert [a for _, a in catalogue] == [a for _, a in rows], level
        for (ours, _), (theirs, _) in zip(catalogue, rows):
            if ours.startswith("Any "):
                # "Any Common magic item that isn't ..." stands for the
                # source's "Common magic item that isn't ... (you can learn
                # this option multiple times ...)".
                assert theirs.lower().startswith(ours[len("Any ") :].lower()), theirs
            else:
                assert ours == theirs


def test_card_marks_attunement_and_has_a_fill_in_row_per_plan_at_level_20():
    character = next(
        c
        for c in (builder().build() for builder in ALL_BUILDS.values())
        if c.has_feature(ReplicateMagicItem)
    )
    feature = next(
        f
        for f in character.iter_features_with_extensions()
        if isinstance(f, ReplicateMagicItem)
    )
    html = improved_description_to_html(feature.get_improved_description(character))
    assert "Manifold Tool<sup>A</sup>" in html
    assert "Bag of Holding<sup>A</sup>" not in html
    assert html.count("&#9744;") == plans_known(20)
    tiles = dict(feature.get_resource_tiles(character))
    assert tiles["Plans Known"][0] == ("Lv 2-5", "4")
    assert tiles["Magic Items"][-1] == ("Lv 18-20", "6")
    assert ArtificerFeatures.ANY_ITEM_MARK in html
