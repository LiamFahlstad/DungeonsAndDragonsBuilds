"""
Improved spell descriptions (CharacterContent/Spells/IMPROVED_DESCRIPTIONS.md):
the same rules as a spell's source text, as FeatureText blocks, in a spell's
class (CharacterContent/Spells/SpellClasses) or in a
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
# Every spell with an improved description, in a JSON file or in its class.
IMPROVED = sorted(
    (s for s in SpellFactory.all_spells() if s.improved_description is not None),
    key=lambda spell: spell.name,
)


def _source(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _card(spell, source_text=False) -> str:
    out = io.StringIO()
    write_spell_to_file(spell, out, source_text=source_text)
    return out.getvalue()


@pytest.mark.parametrize("path,name,blocks", ENTRIES, ids=ENTRY_IDS)
class TestEveryImprovedDescriptionEntry:
    def test_it_names_a_spell_in_its_own_source(self, path, name, blocks):
        # An entry keyed by a misspelled name, or written for a spell another
        # source holds, would be silently dropped by the factory.
        assert name in _source(path)

    def test_it_is_the_one_the_factory_loads(self, path, name, blocks):
        # A higher-priority source holding the same spell wins outright, so
        # this entry would never be shown; so does the spell's class.
        spell = SpellFactory.create(name)
        assert spell.improved_description == blocks_from_json(blocks)


@pytest.mark.parametrize("spell", IMPROVED, ids=[s.name for s in IMPROVED])
class TestEveryImprovedDescription:
    def test_it_renders(self, spell):
        assert improved_description_to_html(spell.improved_description)

    def test_it_keeps_the_upcasting_rules(self, spell):
        # The source's upcasting and cantrip scaling paragraphs each become
        # an Option of the same name - the scroll card drops upcasting by it.
        option_names = {
            block.name
            for block in spell.improved_description
            if isinstance(block, Option)
        }
        for heading in (*UPCAST_OPTION_NAMES, "Cantrip Upgrade"):
            if heading in spell.description:
                assert heading in option_names, f"{spell.name}: no {heading!r} Option"

    def test_its_flavor_is_quoted_from_the_source(self, spell):
        # A Flavor row quotes the source text (or the aidedd text when the
        # source's is missing); it never paraphrases or adds flavor. Its
        # first letter may be capitalized and a period added, nothing more.
        source = spell.description or _source(
            "CharacterContent/Spells/spells_aidedd.json"
        ).get(spell.name, {}).get("description", "")
        source = source.replace("�", "'").replace("’", "'").replace("‘", "'")
        blocks = spell.improved_description
        for block in blocks:
            if not isinstance(block, Facts):
                continue
            for label, value in block.rows:
                if label != "Flavor":
                    continue
                assert block is blocks[0], f"{spell.name}: Flavor isn't first"
                for sentence in value.rstrip(".").split(". "):
                    sentence = sentence.rstrip(".")
                    assert (
                        sentence in source
                        or sentence[0].lower() + sentence[1:] in source
                    ), f"{spell.name}: Flavor isn't verbatim: {sentence!r}"


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
        # Fireball's JSON record without an improved description, so the
        # test doesn't depend on which spells have one yet.
        data = dict(SpellFactory._load_json()["Fireball"])
        data.pop("improved_description", None)
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
