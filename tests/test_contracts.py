"""Model/View.py: the one Protocol the Model is written against
(Notes/engine-simplification-plan.md, section 2b).

CharacterView is everything a formula may read:

- Character really satisfies it: every member is called, not just looked up
  (typing's runtime_checkable only checks that the names exist).
- Effects - what apply() gets - has none of it, so a formula can never read
  a stat in the middle of evaluation.
- It exposes answers, never a part.

Every build's content is the Model/Content base classes the Character's
fields name (features, armor, weapons, items, fighting styles).
"""

import inspect
import typing

import pytest

from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from Core.Definitions import Ability, CharacterClass, Skill
from Model.View import CharacterView
from Model.Content.Feature import Feature
from CharacterContent.Items.Weapons import Longsword
from Core.Weapons import WeaponTraits
from Model.Bonuses import Bonuses
from Model.Effects import Effects, Ledger
from Model.Content.Armor import AbstractArmor
from Model.Content.FightingStyle import FightingStyle
from Model.Content.Item import Item
from Model.Content.Weapon import AbstractWeapon
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
    WeaponTraits: Longsword().traits,
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


# Every Ledger part, and the Bonuses they share.
PART_TYPES = {type(part) for part in vars(Ledger()).values()} | {Bonuses}


@pytest.mark.parametrize("name", MEMBERS)
def test_stat_view_exposes_answers_not_parts(name):
    expected = _return_annotation(name)
    candidates = typing.get_args(expected) or (expected,)
    assert not any(t in PART_TYPES for t in candidates), name


# ── The content a Character holds: the Model/Content base classes ─────────────


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_content_is_the_model_content_classes(name):
    """Python doesn't check annotations at runtime: every build must hand the
    Character the Model/Content classes its fields name."""
    data = type(ALL_BUILDS[name])().build()
    problems = []
    for feature in data.iter_features_with_extensions():
        if not isinstance(feature, Feature):
            problems.append(("feature", type(feature).__name__))
    for armor in data.armors:
        if not isinstance(armor, AbstractArmor):
            problems.append(("armor", type(armor).__name__))
    for weapon in [*data.weapons, *data.weapon_masteries]:
        if not isinstance(weapon, AbstractWeapon):
            problems.append(("weapon", type(weapon).__name__))
    for item, _quantity in data.items:
        if not isinstance(item, Item):
            problems.append(("item", type(item).__name__))
    for style in data.fighting_styles:
        if not isinstance(style, FightingStyle):
            problems.append(("fighting style", type(style).__name__))
    assert not problems, problems
