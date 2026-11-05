"""Spell.summons: a spell's summon specs come from the registry in
CharacterContent/Summons/SpellSummons.py, looked up by the spell's name
(Notes/summon-framework-plan.md, S4.2)."""

from functools import cache

import pytest

from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Summons.SpellSummons import SPELL_SUMMONS
from Core.Definitions import Ability
from Model.Content.Summons import SummonContext, SummonSpec
from Model.View import CharacterView
from tests._snapshot_helpers import build

# Any build will do: Spell.summons hands the character to nothing yet.
WILDFIRE_BUILD = "Y2014DruidWildfireEmberAshgroveCharacterBuilder"


@cache
def _sheet():
    return build(WILDFIRE_BUILD)


def _never_built(character: CharacterView, ctx: SummonContext):
    raise AssertionError("the stat block isn't built in these tests")


def test_a_spell_without_an_entry_summons_nothing():
    assert "Fireball" not in SPELL_SUMMONS
    assert SpellFactory.create("Fireball", Ability.INTELLIGENCE).summons(_sheet()) == []


def test_a_registered_spell_returns_its_factorys_spec(monkeypatch):
    spec = SummonSpec(name="Bestial Spirit", build=_never_built)
    abilities: list[Ability | None] = []

    def factory(ability: Ability | None) -> SummonSpec:
        abilities.append(ability)
        return spec

    # monkeypatch.setitem removes the entry again when the test ends.
    monkeypatch.setitem(SPELL_SUMMONS, "Summon Beast", factory)

    spell = SpellFactory.create("Summon Beast", Ability.WISDOM)
    assert spell.summons(_sheet()) == [spec]
    # The factory gets the ability this copy of the spell is cast with.
    assert abilities == [Ability.WISDOM]


@pytest.mark.parametrize("spell_name", sorted(SPELL_SUMMONS))
def test_every_entry_is_a_summon_tagged_spell(spell_name):
    # A typo in a registry key would silently summon nothing.
    assert spell_name in SpellFactory.spell_names()
    assert "summon" in SpellFactory.create(spell_name).usage_tags
