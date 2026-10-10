"""The Character Creator can load every build file and write it back out.

For every build: Loader (build file -> BuildSpec) -> CodeGen (BuildSpec ->
source) -> import the generated file -> build -> the same stats as the
build's golden (tests/snapshots/build_stats.json).

This guards what the other tests don't import: the import lines CodeGen
writes, and the Registry finding classes by their module. Moving a module
(Notes/engine-simplification-plan.md, Steps 5, 6 and 9) breaks a generated
build here first.

NOT_REPRODUCED lists the builds the Creator can't reproduce today, each with
the reason. They're strict xfails: once one round-trips, remove it from the
list.
"""

import importlib.util
import inspect
import json
from pathlib import Path

import pytest

from Builds.CharacterBuilder import BuildClass, is_build_class
from Builds.CharacterCreator.CodeGen import generate
from Builds.CharacterCreator.Loader import load_build_file
from tests._snapshot_helpers import ALL_BUILDS, BUILD_PARAMS, STATS_PATH, compute_stats
from tests._snapshot_helpers import load as load_json

GOLDEN_STATS = load_json(STATS_PATH)

_MULTICLASS = "the BuildSpec has no multiclass builders"
_ADVENTURING_GEAR = "the BuildSpec has no adventuring gear, so AC and weapons differ"
_MONK_2014_LEVEL_4 = "the generated 2014 MonkLevel4 call is missing general_feat"

NOT_REPRODUCED = {
    "SpellSlotTestPaladin4Wizard3": _MULTICLASS,
    "SpellSlotTestWizard3Warlock3": _MULTICLASS,
    "Y2024_Paladin_Devotion_ElricPactsworn": _MULTICLASS,
    "Y2024_Warlock_Archfey_CaelumBladefey": _MULTICLASS,
    "Y2024_Rogue_ShadowMonk_KagenVoidstep": (
        "the Loader doesn't know RogueCustomStarterClassArgs (it guesses Fighter), "
        "and " + _MULTICLASS
    ),
    "Y2024_Artificer_Cartographer_ObmarStalskagg": _ADVENTURING_GEAR,
    "Y2024_Bard_Valor_Clover": _ADVENTURING_GEAR,
    "Y2024_Cleric_Light_GabrielGreybeard": _ADVENTURING_GEAR,
    "Y2024_Paladin_Devotion_Edmund": _ADVENTURING_GEAR,
    "Y2024_Rogue_ArcaneTrickster_ThumSchtock": _ADVENTURING_GEAR,
    "Y2014MonkAstralSelfIndraStarformCharacterBuilder": _MONK_2014_LEVEL_4,
    "Y2014MonkDrunkenMasterChenWobblejarCharacterBuilder": _MONK_2014_LEVEL_4,
    "Y2014MonkKenseiHanaSteeldriftCharacterBuilder": _MONK_2014_LEVEL_4,
    "Y2014MonkLongDeathYorrinPaleboneCharacterBuilder": _MONK_2014_LEVEL_4,
    "Y2014MonkSunSoulSolaraBrightpalmCharacterBuilder": _MONK_2014_LEVEL_4,
    "Y2024DruidLandRowanThistledownCharacterBuilder": (
        "the generated file uses the module constant _EARLY_LAND without defining it"
    ),
    "Y2024_Monk_Elements_KiviJatti": (
        "the generated file uses the local name martial_arts_die without defining it"
    ),
}


def _params():
    for name in BUILD_PARAMS:
        marks = []
        if name in NOT_REPRODUCED:
            marks.append(pytest.mark.xfail(strict=True, reason=NOT_REPRODUCED[name]))
        yield pytest.param(name, marks=marks, id=name)


def _import_generated(source: str, folder: Path, module_name: str):
    path = folder / f"{module_name}.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _builder_class(module) -> BuildClass:
    builders = [
        value
        for value in vars(module).values()
        if is_build_class(value, module.__name__)
    ]
    assert len(builders) == 1, f"Expected one CharacterBuilder, found {builders}"
    return builders[0]


def test_every_not_reproduced_build_exists():
    unknown = sorted(set(NOT_REPRODUCED) - set(ALL_BUILDS))
    assert not unknown, f"Not a registered build any more: {unknown}"


@pytest.mark.parametrize("name", list(_params()))
def test_creator_reproduces_build(name: str, tmp_path: Path):
    build_file = inspect.getfile(ALL_BUILDS[name])
    spec, _warnings = load_build_file(build_file)
    source = generate(spec)
    module = _import_generated(source, tmp_path, f"creator_roundtrip_{name}")
    character = _builder_class(module)().build()

    # Through JSON, like the golden file, so tuples compare equal to lists.
    stats = json.loads(json.dumps(compute_stats(character)))
    assert stats == GOLDEN_STATS[name]
