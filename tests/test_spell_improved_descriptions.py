"""
Improved spell descriptions (CharacterContent/Spells/IMPROVED_DESCRIPTIONS.md):
the same rules as a spell's source text, as FeatureText blocks in a
spells_<source>_improved.json. Shown on the card instead of the source;
RunCharacterCreator.py --source-text prints the source instead.
"""

import io
import json

import pytest

from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Spells.SpellFactory.DataSpell import DataSpell
from CharacterContent.Spells.SpellFactory.Spell import UPCAST_OPTION_NAMES
from Model.Content.FeatureText import (
    Facts,
    Option,
    Paragraph,
    Table,
    blocks_from_json,
)
from Presentation.FeatureCards import improved_description_to_html
from Presentation.SpellCards import write_spell_to_file


def _improved_entries():
    """(source path, spell name, blocks JSON) for every improved file."""
    entries = []
    for path in SpellFactory.json_paths:
        try:
            with open(SpellFactory.improved_path(path), encoding="utf-8") as f:
                improved = json.load(f)
        except FileNotFoundError:
            continue
        entries += [(path, name, blocks) for name, blocks in improved.items()]
    return entries


ENTRIES = _improved_entries()
ENTRY_IDS = [f"{path.rsplit('/', 1)[-1]}:{name}" for path, name, _ in ENTRIES]


def _source(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _card(spell, source_text=False) -> str:
    out = io.StringIO()
    write_spell_to_file(spell, out, source_text=source_text)
    return out.getvalue()


@pytest.mark.parametrize("path,name,blocks", ENTRIES, ids=ENTRY_IDS)
class TestEveryImprovedDescription:
    def test_it_names_a_spell_in_its_own_source(self, path, name, blocks):
        # An entry keyed by a misspelled name, or written for a spell another
        # source holds, would be silently dropped by the factory.
        assert name in _source(path)

    def test_it_renders(self, path, name, blocks):
        assert improved_description_to_html(blocks_from_json(blocks))

    def test_it_keeps_the_upcasting_rules(self, path, name, blocks):
        # The source's upcasting and cantrip scaling paragraphs each become
        # an Option of the same name - the scroll card drops upcasting by it.
        description = _source(path)[name]["description"]
        option_names = {
            block.name
            for block in blocks_from_json(blocks)
            if isinstance(block, Option)
        }
        for heading in (*UPCAST_OPTION_NAMES, "Cantrip Upgrade"):
            if heading in description:
                assert heading in option_names, f"{name}: no {heading!r} Option"

    def test_its_flavor_is_quoted_from_the_source(self, path, name, blocks):
        # A Flavor row quotes the source text (or the aidedd text when the
        # source's is missing); it never paraphrases or adds flavor. Its
        # first letter may be capitalized and a period added, nothing more.
        source = _source(path)[name]["description"] or _source(
            "CharacterContent/Spells/spells_aidedd.json"
        ).get(name, {}).get("description", "")
        source = source.replace("�", "'").replace("’", "'").replace("‘", "'")
        for block in blocks:
            for label, value in block.get("facts", ()):
                if label != "Flavor":
                    continue
                assert block is blocks[0], f"{name}: Flavor isn't the card's first row"
                for sentence in value.rstrip(".").split(". "):
                    sentence = sentence.rstrip(".")
                    assert (
                        sentence in source
                        or sentence[0].lower() + sentence[1:] in source
                    ), f"{name}: Flavor isn't verbatim: {sentence!r}"

    def test_it_is_the_one_the_factory_loads(self, path, name, blocks):
        # A higher-priority source holding the same spell wins outright, so
        # this entry would never be shown.
        spell = SpellFactory.create(name)
        assert spell.improved_description == blocks_from_json(blocks)


class TestSpellCard:
    def test_it_shows_the_improved_layout(self):
        html = _card(SpellFactory.create("Fireball"))
        assert (
            "<span class='feature-option-name'>Using a Higher-Level Spell Slot</span>"
            in html
        )
        assert "<th class='feature-box-label'>Area</th>" in html
        assert "<th>Failed save</th>" in html

    def test_it_replaces_the_source_text(self):
        html = _card(SpellFactory.create("Fireball"))
        assert "makes a Dexterity saving throw, taking 8d6" not in html
        assert "spell-higher" not in html

    def test_its_flavor_is_kept_word_for_word(self):
        html = _card(SpellFactory.create("Fireball"))
        assert "<th class='feature-box-label'>Flavor</th>" in html
        assert "blossoms with a low roar into a fiery explosion" in html

    def test_source_text_flag_prints_the_source_instead(self):
        html = _card(SpellFactory.create("Fireball"), source_text=True)
        assert "low roar" in html
        assert "<div class='spell-higher'>" in html
        assert "feature-box" not in html

    def test_spells_without_one_keep_their_source_text(self):
        # Fireball's record with its improved description taken out, so the
        # test doesn't depend on which spells have one yet.
        fireball = SpellFactory.create("Fireball")
        assert isinstance(fireball, DataSpell)
        data = dict(fireball._data)
        del data["improved_description"]
        html = _card(DataSpell(data))
        assert "low roar" in html
        assert "feature-box" not in html


def test_a_scroll_leaves_out_the_upcasting_option():
    blocks = SpellFactory.create("Fireball").improved_description_at_fixed_level()
    assert blocks is not None
    names = [block.name for block in blocks if isinstance(block, Option)]
    assert "Using a Higher-Level Spell Slot" not in names
    assert any(isinstance(block, Facts) for block in blocks)


def test_a_bad_block_names_the_spell():
    data = {
        "name": "Broken",
        "level": 1,
        "school": "Evocation",
        "classes": [],
        "casting_time": "Action",
        "range": "Self",
        "components": "V",
        "duration": "Instantaneous",
        "description": "x",
        "source": "x",
        "improved_description": [{"prose": "x"}],
    }
    with pytest.raises(ValueError, match="Broken"):
        DataSpell(data).improved_description


class TestBlocksFromJson:
    def test_every_block_type(self):
        blocks = blocks_from_json(
            [
                {"paragraph": "Lead."},
                {"facts": [["Save", "Wisdom"]]},
                {"table": {"columns": ["A", "B"], "rows": [["1", "2"]]}},
                {"option": {"name": "Name", "blocks": [{"paragraph": "Inner."}]}},
            ]
        )
        assert blocks == [
            Paragraph("Lead."),
            Facts((("Save", "Wisdom"),)),
            Table(("A", "B"), (("1", "2"),)),
            Option("Name", (Paragraph("Inner."),)),
        ]

    @pytest.mark.parametrize(
        "bad",
        [
            {"paragraph": "x"},  # not a list
            [{"paragraph": "x", "facts": []}],  # two keys
            [{"statblock": "<div/>"}],  # no JSON form
            [{"facts": [["only a label"]]}],
            [{"table": {"columns": ["A", "B"], "rows": [["1"]]}}],
        ],
    )
    def test_malformed_blocks_are_rejected(self, bad):
        with pytest.raises(ValueError):
            blocks_from_json(bad)
