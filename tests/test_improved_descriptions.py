"""
Improved descriptions (Model/Content/FeatureText.py): the same rules as a
feature's source text, laid out for reading at a glance. Shown instead of
the source on full sheets; RunCharacterCreator.py --source-text prints the
source instead.
"""

import pytest

from CharacterContent.Features.ClassFeatures.Cleric.ClericFeatures import (
    ChannelDivinity,
)
from Core.Definitions import Ability
from Model.Content.Feature import Feature
from Model.Content.FeatureText import (
    Facts,
    Option,
    Paragraph,
    StatBlock,
    Table,
    dc_formula,
)
from Presentation.FeatureCards import (
    improved_description_to_html,
    render_feature_description,
)
from tests._snapshot_helpers import ALL_BUILDS


def _cleric():
    name = next(n for n in ALL_BUILDS if "ClericLight" in n)
    character = ALL_BUILDS[name]().build()
    feature = next(f for f in character.features if isinstance(f, ChannelDivinity))
    return character, feature


def _html(feature, character, mode=None, source_text=False) -> str:
    html = render_feature_description(feature, character, mode, source_text)
    assert html is not None
    return html


class TestChannelDivinity:
    def test_full_sheet_shows_the_improved_layout(self):
        character, feature = _cleric()
        html = _html(feature, character)
        assert "<span class='feature-option-name'>Divine Spark</span>" in html
        assert "<span class='feature-option-name'>Turn Undead</span>" in html
        assert "<th class='feature-box-label'>Harm</th>" in html

    def test_it_replaces_the_source_text_on_the_sheet(self):
        # The sheet is printed, so nothing is collapsed or hidden: the
        # improved layout stands in for the source text.
        character, feature = _cleric()
        html = _html(feature, character)
        assert "directly from the Outer Planes" not in html
        assert "<details" not in html

    def test_source_text_flag_prints_the_source_instead(self):
        character, feature = _cleric()
        html = _html(feature, character, source_text=True)
        assert "directly from the Outer Planes" in html
        assert "feature-option-name" not in html

    def test_save_dc_is_written_as_its_formula(self):
        character, feature = _cleric()
        html = _html(feature, character)
        assert "8 + Wisdom modifier + Proficiency Bonus" in html

    def test_it_holds_formulas_not_todays_numbers(self):
        # The sheet is printed once and kept as the character levels up, so
        # two Clerics with different stats and levels get the same text.
        rendered = set()
        for name in [n for n in ALL_BUILDS if "Cleric" in n and "Y2024" in n][:2]:
            character = ALL_BUILDS[name]().build()
            feature = next(
                f for f in character.features if isinstance(f, ChannelDivinity)
            )
            improved = feature.get_improved_description(character)
            assert improved is not None
            rendered.add(improved_description_to_html(improved))
        assert len(rendered) == 1

    def test_condensed_sheets_fall_back_to_it(self):
        character, feature = _cleric()
        assert feature.get_concise_description(character) is None
        html = _html(feature, character, "concise")
        assert "feature-option-name" in html


def test_features_without_one_keep_their_source_text():
    character, _ = _cleric()
    plain = Feature(name="Plain")
    plain.get_description = lambda c: "Just the rules."  # type: ignore[method-assign]
    html = render_feature_description(plain, character)
    assert html == "<p>Just the rules.</p>\n"


class TestBlocks:
    def test_every_block_renders(self):
        html = improved_description_to_html(
            [
                Paragraph("Lead. Some text."),
                Facts((("Save DC", "13"),)),
                Table(("A", "B"), (("1", "2"),)),
                Option("Name", (Paragraph("Inner."),)),
            ]
        )
        assert "<strong>Lead.</strong>" in html
        assert "<th class='feature-box-label'>Save DC</th>" in html
        assert "<th>A</th>" in html and "<td>2</td>" in html
        assert "<p>Inner.</p>" in html

    def test_an_option_is_one_contained_box(self):
        html = improved_description_to_html(
            [Option("Name", (Facts((("Save", "Wisdom"),)),))]
        )
        assert html.count("<table class='feature-box'>") == 1
        header = html.index("feature-box-header")
        assert header < html.index("<th class='feature-box-label'>Save</th>")
        assert html.rstrip().endswith("</table>")

    def test_options_dont_nest(self):
        with pytest.raises(TypeError):
            improved_description_to_html([Option("Outer", (Option("Inner"),))])

    def test_a_table_row_must_fill_every_column(self):
        with pytest.raises(ValueError):
            Table(("A", "B"), (("only one",),))

    def test_dc_formula(self):
        assert dc_formula(Ability.WISDOM) == "8 + Wisdom modifier + Proficiency Bonus"


def test_every_improved_description_keeps_its_source_text():
    """The improved layout is shown instead of get_description(), which must
    still exist - it's the source the improved version is checked against."""
    for name, builder in ALL_BUILDS.items():
        character = builder().build()
        for feature in character.iter_features_with_extensions():
            if feature.get_improved_description(character) is not None:
                assert feature.get_description(
                    character
                ), f"{name}: {feature.name} has an improved description but no source text"


def _without_stat_blocks(blocks):
    """The blocks minus StatBlocks, which show today's numbers by design."""
    kept = []
    for block in blocks:
        if isinstance(block, StatBlock):
            continue
        if isinstance(block, Option):
            block = Option(block.name, tuple(_without_stat_blocks(block.blocks)))
        kept.append(block)
    return kept


def test_every_improved_description_is_formulas_not_todays_numbers():
    """The sheet is printed once and kept as the character levels up, so an
    improved description must not depend on the character's stats or level.
    Each granted feature is rendered against two very different reference
    characters; a choice stored on the feature itself (a Storm Herald's
    environment, a Genie's kind) may vary between builds, a number may not."""
    by_level = sorted(
        (builder().build() for builder in ALL_BUILDS.values()),
        key=lambda c: c.character_level,
    )
    low, high = by_level[0], by_level[-1]
    assert low.character_level < high.character_level

    checked: set[str] = set()
    varying: set[str] = set()
    for character in by_level:
        for feature in character.iter_features_with_extensions():
            if feature.get_improved_description(character) is None:
                continue
            checked.add(type(feature).__qualname__)
            renders = {
                improved_description_to_html(
                    _without_stat_blocks(feature.get_improved_description(ref) or [])
                )
                for ref in (low, high, character)
            }
            if len(renders) > 1:
                varying.add(type(feature).__qualname__)
    assert (
        not varying
    ), f"Improved descriptions that change with the character: {sorted(varying)}"
    assert len(checked) >= 10
