"""Model/View.py and Model/Sources.py: the Protocols the Model is
written against (Notes/model-refactor-plan.md, Steps 3 and 4).

CharacterView is everything a formula may read:

- Character really satisfies it: every member is called, not just looked up
  (typing's runtime_checkable only checks that the names exist).
- Effects - what apply() gets - has none of it, so a formula can never read
  a stat in the middle of evaluation.
- It exposes answers, never a part.

The Sources Protocols are what the Model reads off features, fighting
styles, armor, weapons and items; every build's content must satisfy them.
"""

import inspect
import typing

import pytest

from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from Core.Definitions import Ability, CharacterClass, Skill
from Model.View import CharacterView
from CharacterContent.Features.Core.BaseFeatures import Feature
from Model.Effects import Effects
from Model.Recorder import Recorder
from Model.Sources import ArmorGear, Effect, Gear, GrantedFeature
from tests._snapshot_helpers import ALL_BUILDS

MEMBERS = sorted(
    name
    for name, value in vars(CharacterView).items()
    if not name.startswith("_") and (callable(value) or isinstance(value, property))
)

SAMPLE_ARGUMENTS = {
    Ability: Ability.WISDOM,
    Skill: Skill.ARCANA,
    CharacterClass: CharacterClass.PALADIN,
    type: Feature,
}


def _return_annotation(name: str):
    member = vars(CharacterView)[name]
    function = member.fget if isinstance(member, property) else member
    return typing.get_type_hints(function).get("return")


@pytest.fixture(scope="module")
def character():
    return SpellSlotTestPaladin5CharacterBuilder().build().validate()


def test_stat_view_has_members():
    assert "get_proficiency_bonus" in MEMBERS and "character_level" in MEMBERS


@pytest.mark.parametrize("name", MEMBERS)
def test_character_satisfies_stat_view(character, name):
    member = vars(CharacterView)[name]
    if isinstance(member, property):
        value = getattr(character, name)
    else:
        parameters = list(inspect.signature(member).parameters.values())[1:]
        arguments = [SAMPLE_ARGUMENTS[p.annotation] for p in parameters]
        value = getattr(character, name)(*arguments)
    expected = _return_annotation(name)
    origin = typing.get_origin(expected)
    if origin is typing.Union:  # Optional[...]
        allowed = typing.get_args(expected)
    elif origin is not None:  # dict[int, int], ...
        allowed = (origin,)
    else:
        allowed = (expected,)
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


# ── Model/Sources.py: what the Model reads off content ───────────────────────


def _protocol_members(protocol: type) -> set[str]:
    members = set()
    for cls in protocol.__mro__:
        if cls is object or not getattr(cls, "_is_protocol", False):
            continue
        members |= set(getattr(cls, "__annotations__", {}))
        members |= {
            name
            for name, value in vars(cls).items()
            if callable(value) and not name.startswith("_")
        }
    return members


def _missing(obj, protocol: type) -> list[str]:
    return sorted(m for m in _protocol_members(protocol) if not hasattr(obj, m))


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_content_satisfies_the_source_protocols(name):
    data = type(ALL_BUILDS[name])().build()
    problems = []
    for feature in data.iter_features_with_extensions():
        problems += [(feature.name, m) for m in _missing(feature, GrantedFeature)]
    for armor in data.armors:
        problems += [(armor.name, m) for m in _missing(armor, ArmorGear)]
    for gear in [*data.weapons, *data.weapon_masteries, *(i for i, _ in data.items)]:
        problems += [(gear.name, m) for m in _missing(gear, Gear)]
    for style in data.fighting_styles:
        problems += [(type(style).__name__, m) for m in _missing(style, Effect)]
    assert not problems, problems
