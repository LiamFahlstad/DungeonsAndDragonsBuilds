"""Most feats, species traits and fighting styles, and many subclasses, are
taken by no build, so the sheet tests never render their improved
descriptions. Build each one here, with constructor arguments synthesized
from its signature, and render it."""

import enum
import importlib
import inspect
import pathlib
import typing

import pytest

from CharacterContent.Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    DruidLevel0Spells,
    DruidLevel1Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from Core.Definitions import Ability, CharacterClass, DamageType, Skill
from Model.Content.Feature import Feature
from Model.Content.FightingStyle import FightingStyle
from Presentation.FeatureCards import improved_description_to_html
from tests._snapshot_helpers import ALL_BUILDS

FEATURES_ROOT = pathlib.Path(__file__).parent.parent / "CharacterContent" / "Features"
FEAT_MODULES = tuple(
    ".".join(path.relative_to(FEATURES_ROOT.parent.parent).with_suffix("").parts)
    for path in sorted(FEATURES_ROOT.rglob("*.py"))
    if "FeatureGeneration" not in path.parts and path.name != "__init__.py"
)
STYLE_MODULE = "CharacterContent.Features.CombatFeatures.FightingStyles"


def _defined_in(module_name, base):
    module = importlib.import_module(module_name)
    return [
        cls
        for cls in vars(module).values()
        if inspect.isclass(cls)
        and issubclass(cls, base)
        and cls.__module__ == module_name
        and not inspect.isabstract(cls)
        and not cls.__name__.startswith("_")
    ]


def _argument(cls, name, annotation, damage_type=DamageType.NECROTIC):
    """A valid value for one constructor parameter."""
    if name == "character_level":
        return 20
    if name == "ability" and hasattr(cls, "_ABILITIES"):
        return cls._ABILITIES[0]
    if annotation is Ability:
        return Ability.WISDOM
    if annotation is DamageType:
        valid = getattr(cls, "VALID_DAMAGE_TYPES", None) or [damage_type]
        return sorted(valid, key=lambda d: d.value)[0]
    if annotation is Skill:
        return Skill.INSIGHT
    if annotation is str:
        return name
    options = typing.get_args(annotation) or (annotation,)
    for option in options:
        if inspect.isclass(option) and issubclass(option, enum.Enum):
            members = list(option)
            # Two parameters of the same enum (two cantrips) must differ.
            return (
                members[0]
                if name.endswith("1") or not name[-1].isdigit()
                else members[-1]
            )
    raise LookupError(f"{cls.__name__}: no value for {name}: {annotation}")


def _build(cls):
    """Necrotic suits one feat's damage-type choice, Fire the others'."""
    try:
        return _build_with(cls, DamageType.NECROTIC)
    except ValueError:
        return _build_with(cls, DamageType.FIRE)


# Magic Initiate checks its spell names against the chosen class's lists,
# which a parameter's name and type can't tell.
_MAGIC_INITIATE_LISTS = {
    "MagicInitiate": (CharacterClass.WIZARD, WizardLevel0Spells, WizardLevel1Spells),
    "MagicInitiateCleric": (
        CharacterClass.CLERIC,
        ClericLevel0Spells,
        ClericLevel1Spells,
    ),
    "MagicInitiateDruid": (CharacterClass.DRUID, DruidLevel0Spells, DruidLevel1Spells),
    "MagicInitiateWizard": (
        CharacterClass.WIZARD,
        WizardLevel0Spells,
        WizardLevel1Spells,
    ),
}


def _spell_arguments(cls, parameters) -> dict:
    if cls.__name__ not in _MAGIC_INITIATE_LISTS:
        return {}
    character_class, cantrips, spells = _MAGIC_INITIATE_LISTS[cls.__name__]
    arguments = {
        "cantrip_1": list(cantrips)[0].value,
        "cantrip_2": list(cantrips)[-1].value,
        "spell": list(spells)[0].value,
    }
    if "character_class" in parameters:
        arguments["character_class"] = character_class
    return arguments


def _build_with(cls, damage_type):
    hints = typing.get_type_hints(cls.__init__)
    parameters = inspect.signature(cls.__init__).parameters
    known = _spell_arguments(cls, parameters)
    kwargs = {
        name: known.get(name) or _argument(cls, name, hints.get(name), damage_type)
        for name, parameter in parameters.items()
        if name != "self"
        and parameter.default is inspect.Parameter.empty
        and parameter.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    }
    return cls(**kwargs)


IMPROVED_FEATS = [
    cls
    for module in FEAT_MODULES
    for cls in _defined_in(module, Feature)
    if any(
        "get_improved_description" in base.__dict__
        for base in cls.__mro__
        if base is not Feature
    )
]
IMPROVED_STYLES = [
    cls
    for cls in _defined_in(STYLE_MODULE, FightingStyle)
    if "get_improved_description" in cls.__dict__
]


@pytest.fixture(scope="module")
def character():
    return max(
        (builder().build() for builder in ALL_BUILDS.values()),
        key=lambda c: c.character_level,
    )


def test_feats_and_styles_with_one_are_found():
    assert len(IMPROVED_FEATS) >= 300
    assert len(IMPROVED_STYLES) >= 5


@pytest.mark.parametrize("cls", IMPROVED_FEATS, ids=lambda c: c.__name__)
def test_every_feat_improved_description_renders(cls, character):
    try:
        feature = _build(cls)
    except LookupError as error:
        pytest.skip(str(error))
    improved = feature.get_improved_description(character)
    assert improved, cls.__name__
    assert improved_description_to_html(improved)
    assert feature.get_description(character), cls.__name__


@pytest.mark.parametrize("cls", IMPROVED_STYLES, ids=lambda c: c.__name__)
def test_every_fighting_style_improved_description_renders(cls):
    style = _build(cls)
    improved = style.get_improved_description()
    assert improved, cls.__name__
    assert improved_description_to_html(improved)
    assert style.description()
