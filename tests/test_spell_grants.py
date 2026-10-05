"""Spells are order-free grants (Notes/model-refactor-plan.md, Step 9).

Every spell is a SpellGrant stamped by the builder's Grants scope with its
grant level and who grants it; replacements are declared and resolved when
the spells are read. Nothing depends on the order of the calls.
"""

import itertools

import pytest

from Core.Definitions import Ability
from Model.Character import Character
from Model.Grants import Grants

INT = Ability.INTELLIGENCE
WIS = Ability.WISDOM


def _names(character: Character) -> list[str]:
    return [spell.name for spell in character.spells]


class TestGrantsScope:
    def test_stamps_level_and_grant(self):
        character = Character(spell_casting_ability=INT)
        Grants(character, 5, "Wizard").add_spell("Fireball")
        (spell,) = character.spells
        assert (spell.grant_level, spell.granted_by) == (5, "Wizard")

    def test_granted_by_can_be_overridden(self):
        # An origin feat granted through a species lists its spells under
        # the feat.
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Human").add_spell(
            "Bless", WIS, granted_by="Magic Initiate"
        )
        assert character.spells[0].granted_by == "Magic Initiate"

    def test_keeps_the_free_text_source_label(self):
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Wizard").add_spell("Shield", source="Chosen spell")
        assert character.spells[0].source == "Chosen spell"


class TestDuplicates:
    def test_the_same_spell_from_two_grants_is_listed_for_each(self):
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Wizard").add_cantrip("Prestidigitation")
        Grants(character, 1, "Rock Gnome").add_cantrip("Prestidigitation")
        assert sorted(s.granted_by for s in character.spells) == [
            "Rock Gnome",
            "Wizard",
        ]

    def test_the_same_spell_twice_from_one_grant_fails(self):
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Wizard").add_spell("Shield")
        Grants(character, 3, "Wizard").add_spell("Shield")
        with pytest.raises(ValueError, match="already added"):
            character.spells


class TestReplacements:
    def test_a_replacement_keeps_level_grant_and_label(self):
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Wizard").add_spell("Sleep", source="Chosen spell")
        character.replace_spell("Sleep", "Shield")
        (spell,) = character.spells
        assert (spell.name, spell.grant_level, spell.granted_by, spell.source) == (
            "Shield",
            1,
            "Wizard",
            "Chosen spell",
        )

    def test_a_replacement_may_be_declared_before_its_target(self):
        character = Character(spell_casting_ability=INT)
        character.replace_spell("Sleep", "Shield")
        Grants(character, 1, "Wizard").add_spell("Sleep")
        assert _names(character) == ["Shield"]

    def test_replacing_a_spell_nobody_grants_fails(self):
        character = Character(spell_casting_ability=INT)
        character.replace_spell("Sleep", "Shield")
        with pytest.raises(ValueError, match="not found to replace"):
            character.spells

    def test_a_chain_fails(self):
        # Sleep -> Shield -> Mage Armor would depend on which resolves first.
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Wizard").add_spell("Sleep")
        character.replace_spell("Sleep", "Shield")
        character.replace_spell("Shield", "Mage Armor")
        with pytest.raises(ValueError, match="chain"):
            character.spells

    def test_replacing_into_a_spell_already_known_fails(self):
        # The six builds this step fixed: swapping Sleep for a spell learned
        # at a later level listed that spell twice.
        character = Character(spell_casting_ability=INT)
        Grants(character, 1, "Bard").add_spell("Sleep")
        Grants(character, 4, "Bard").add_spell("Enhance Ability")
        character.replace_spell("Sleep", "Enhance Ability")
        with pytest.raises(ValueError, match="already added"):
            character.spells


def test_grant_order_never_changes_the_spells():
    calls = [
        lambda c: Grants(c, 1, "Wizard").add_spell("Sleep", source="Chosen spell"),
        lambda c: Grants(c, 3, "Wizard").add_spell("Misty Step"),
        lambda c: Grants(c, 1, "Rock Gnome").add_cantrip("Mending"),
        lambda c: c.replace_spell("Sleep", "Shield"),
    ]
    results = set()
    for ordered in itertools.permutations(calls):
        character = Character(spell_casting_ability=INT)
        for call in ordered:
            call(character)
        results.add(tuple(character.spells))
    assert len(results) == 1
