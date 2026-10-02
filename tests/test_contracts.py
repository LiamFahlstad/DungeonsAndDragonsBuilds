"""Model/Contracts.py: StatView is everything a formula may read
(Notes/model-refactor-plan.md, Step 3).

- Character really satisfies it: every member is called, not just looked up
  (typing's runtime_checkable only checks that the names exist).
- Effects - what apply() gets - has none of it, so a formula can never read
  a stat in the middle of evaluation.
- It exposes answers, never a part.
"""

import inspect
import typing

import pytest

from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from Core.Definitions import Ability, CharacterClass, Skill
from Model.Contracts import StatView
from Model.Effects import Effects
from Model.Recorder import Recorder

MEMBERS = sorted(
    name
    for name, value in vars(StatView).items()
    if not name.startswith("_") and (callable(value) or isinstance(value, property))
)

SAMPLE_ARGUMENTS = {
    Ability: Ability.WISDOM,
    Skill: Skill.ARCANA,
    CharacterClass: CharacterClass.PALADIN,
}


def _return_annotation(name: str):
    member = vars(StatView)[name]
    function = member.fget if isinstance(member, property) else member
    return typing.get_type_hints(function).get("return")


@pytest.fixture(scope="module")
def character():
    return SpellSlotTestPaladin5CharacterBuilder().build().validate()


def test_stat_view_has_members():
    assert "get_proficiency_bonus" in MEMBERS and "character_level" in MEMBERS


@pytest.mark.parametrize("name", MEMBERS)
def test_character_satisfies_stat_view(character, name):
    member = vars(StatView)[name]
    if isinstance(member, property):
        value = getattr(character, name)
    else:
        parameters = list(inspect.signature(member).parameters.values())[1:]
        arguments = [SAMPLE_ARGUMENTS[p.annotation] for p in parameters]
        value = getattr(character, name)(*arguments)
    expected = _return_annotation(name)
    if isinstance(expected, type):
        assert isinstance(value, expected), (name, value)
    else:  # Optional[...]
        allowed = tuple(t for t in typing.get_args(expected))
        assert isinstance(value, allowed), (name, value)


def test_effects_cannot_read_anything_a_formula_reads():
    assert not [name for name in MEMBERS if hasattr(Effects, name)]


@pytest.mark.parametrize("name", MEMBERS)
def test_stat_view_exposes_answers_not_parts(name):
    expected = _return_annotation(name)
    candidates = typing.get_args(expected) or (expected,)
    assert not any(
        isinstance(t, type) and issubclass(t, Recorder) for t in candidates
    ), name
