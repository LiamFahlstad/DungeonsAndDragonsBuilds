"""The rendered sheet must not depend on order (Notes/model-refactor-plan.md,
Step 0).

test_feature_apply_order.py proves the *stats* don't depend on the order
effects apply in. These tests check the whole sheet, in full and concise mode,
against the golden hashes in tests/snapshots/sheet_hashes.json:

- apply order: every effect (features, extensions, armor, weapons, items,
  fighting styles) applied in a different order;
- grant order: the features, every feature's extensions, and the spells listed
  in a different order, as if the builder had granted them in another order.

Each build gets one shuffle, seeded from its name. Reversed order and three
more shuffles run under `-m slow`: one render pass of every build takes about
90 s, so the full matrix is kept for the steps that touch ordering.
"""

import copy
import random
import zlib
from pathlib import Path
from typing import Callable

import pytest

from Model.Character import Character
from tests._snapshot_helpers import (
    BUILD_PARAMS,
    HASHES_PATH,
    load,
    render_and_hash,
    sheet_differences,
)

Reorder = Callable[[list], list]


def _shuffled(seed: int) -> Reorder:
    def reorder(items: list) -> list:
        items = list(items)
        random.Random(seed).shuffle(items)
        return items

    return reorder


def _reversed(items: list) -> list:
    return items[::-1]


def _orders(name: str) -> dict[str, Reorder]:
    """The default order first, then the slow ones."""
    seed = zlib.crc32(name.encode())
    return {
        "shuffle": _shuffled(seed),
        "reversed": _reversed,
        **{f"shuffle-{i}": _shuffled(seed + i) for i in range(1, 4)},
    }


# Builds whose sheet changes under the default grant-order shuffle, until
# Step 10 gives the sheet a complete canonical order. The sheet already sorts
# each level's feature cards by (passive, name), so only ties leak: two
# features of one name on one level (Expertise, Alert, Spell Slots, Tough,
# Lucky), and the extensions nested under a feature, which are listed in the
# order they were attached. Strict, so a build that stops leaking must come
# off the list. The slow orders shuffle differently and leak in other builds,
# so they're expected to fail everywhere, without being strict.
_GRANT_ORDER_LEAKS = frozenset(
    {
        "SpellSlotTestPaladin4Wizard3",
        "SpellSlotTestPaladin5",
        "Y2014BarbarianAncestralGuardianKodiakStonewatchCharacterBuilder",
        "Y2014BarbarianBattleragerGruddaIronscarCharacterBuilder",
        "Y2014BarbarianStormHeraldTorvidStormcallerCharacterBuilder",
        "Y2014BarbarianWildMagicFenwickChaosbornCharacterBuilder",
        "Y2014BardCreationPiperWrenhollowCharacterBuilder",
        "Y2014BardEloquenceCorvinusTalebrightCharacterBuilder",
        "Y2014BardWhispersNyraHollowechoCharacterBuilder",
        "Y2014DruidWildfireEmberAshgroveCharacterBuilder",
        "Y2014FighterArcaneArcherSylvaineFarshotCharacterBuilder",
        "Y2014FighterEchoKnightLucianMirrorstrikeCharacterBuilder",
        "Y2014FighterRuneKnightBjornGiantforgeCharacterBuilder",
        "Y2014MonkAstralSelfIndraStarformCharacterBuilder",
        "Y2014MonkDrunkenMasterChenWobblejarCharacterBuilder",
        "Y2014MonkKenseiHanaSteeldriftCharacterBuilder",
        "Y2014MonkLongDeathYorrinPaleboneCharacterBuilder",
        "Y2014MonkSunSoulSolaraBrightpalmCharacterBuilder",
        "Y2014PaladinConquestMalacharIronwillCharacterBuilder",
        "Y2014PaladinCrownRegaliaTrueheartCharacterBuilder",
        "Y2014PaladinOathbreakerVorlagCurseboundCharacterBuilder",
        "Y2014PaladinRedemptionPaxMercywardCharacterBuilder",
        "Y2014RangerHorizonWalkerDashiellFarstrideCharacterBuilder",
        "Y2014RangerMonsterSlayerVanthaBeastbaneCharacterBuilder",
        "Y2014RangerSwarmkeeperWispThornwhistleCharacterBuilder",
        "Y2014RogueMastermindDelphineWebswornCharacterBuilder",
        "Y2014RogueScoutFennickQuickstepCharacterBuilder",
        "Y2014RogueSwashbucklerCosimoDuelaireCharacterBuilder",
        "Y2014SorcererLunarSorcerySeleneMoonflareCharacterBuilder",
        "Y2014WarlockGenieKalindaBottleboundCharacterBuilder",
        "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder",
        "Y2014WizardOrderOfScribesQuillonInkboundCharacterBuilder",
        "Y2024BardLoreOdalysVerseholtCharacterBuilder",
        "Y2024DruidLandRowanThistledownCharacterBuilder",
        "Y2024FighterBanneretRoderickVanguardCharacterBuilder",
        "Y2024FighterBattleMasterAldricStormbladeCharacterBuilder",
        "Y2024FighterPsiWarriorKestrelMindshardCharacterBuilder",
        "Y2024MonkElementsKaidaEmberfistCharacterBuilder",
        "Y2024MonkMercyAmritaSofthandCharacterBuilder",
        "Y2024MonkMysticArtsZephyrMoonpetalCharacterBuilder",
        "Y2024MonkOpenHandWeiStonefistCharacterBuilder",
        "Y2024MonkShadowKiraNightstepCharacterBuilder",
        "Y2024RangerBeastMasterFennWildstriderCharacterBuilder",
        "Y2024RoguePhantomWraithGrimscarCharacterBuilder",
        "Y2024WizardTransmutationAlistairFormbendCharacterBuilder",
        "Y2024_Bard_Lore_TobiasGreyquill",
        "Y2024_Fighter_BattleMaster_ReynardSteelvow",
        "Y2024_Monk_Elements_KiviJatti",
        "Y2024_Monk_Elements_KragStormfist",
        "Y2024_Monk_Shadow_UmbraSilentfang",
        "Y2024_Paladin_Devotion_ElricPactsworn",
        "Y2024_Ranger_BeastMaster_OrinPackleader",
        "Y2024_Rogue_ShadowMonk_KagenVoidstep",
    }
)


def _params(expected_leaks=None):
    params = []
    for name in BUILD_PARAMS:
        for order in _orders(name):
            marks = [] if order == "shuffle" else [pytest.mark.slow]
            if expected_leaks is not None:
                if order != "shuffle":
                    marks.append(pytest.mark.xfail(strict=False, reason="Step 10"))
                elif name in expected_leaks:
                    marks.append(pytest.mark.xfail(strict=True, reason="Step 10"))
            params.append(pytest.param(name, order, marks=marks, id=f"{name}-{order}"))
    return params


def _assert_sheet_unchanged(name: str, sheets: dict, what: str) -> None:
    golden = load(HASHES_PATH)
    assert name in golden, f"No golden sheet hashes for {name!r}."
    problems = sheet_differences(golden[name], sheets)
    assert not problems, f"{name}: {what} changed the sheet:\n  " + "\n  ".join(
        problems
    )


@pytest.mark.parametrize("name, order", _params())
def test_apply_order_keeps_sheet(name: str, order: str, tmp_path: Path):
    reorder = _orders(name)[order]

    def reorder_effects(data: Character) -> None:
        data._apply_order = reorder

    sheets = render_and_hash(name, tmp_path, prepare=reorder_effects)
    _assert_sheet_unchanged(name, sheets, f"effect apply order ({order})")


@pytest.mark.parametrize("name, order", _params(expected_leaks=_GRANT_ORDER_LEAKS))
def test_grant_order_keeps_sheet(name: str, order: str, tmp_path: Path):
    reorder = _orders(name)[order]

    def regrant(data: Character) -> None:
        # Copies, so reordering extensions can't reach a feature instance
        # that another build shares (a builder field default, say).
        features = copy.deepcopy(data.features)
        for feature in features:
            _reorder_extensions(feature, reorder)
        data.features = reorder(features)
        data.spells = reorder(data.spells)

    sheets = render_and_hash(name, tmp_path, prepare=regrant)
    _assert_sheet_unchanged(name, sheets, f"grant order ({order})")


def _reorder_extensions(feature, reorder: Reorder) -> None:
    feature.extensions = reorder(feature.extensions)
    for extension in feature.extensions:
        _reorder_extensions(extension, reorder)
