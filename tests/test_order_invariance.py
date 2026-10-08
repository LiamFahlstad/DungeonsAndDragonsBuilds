"""The rendered sheet must not depend on order (Notes/model-refactor-plan.md,
Step 0).

test_feature_apply_order.py proves the *stats* don't depend on the order
effects apply in. These tests check the whole sheet, in full and concise mode,
against the golden hashes in tests/snapshots/sheet_hashes.json:

- apply order: every effect (features, extensions, armor, weapons, items,
  fighting styles) applied in a different order;
- grant order: the features, the extensions, and the spells listed in a
  different order, as if the builder had granted them in another order.

Each build gets one shuffle, seeded from its name. Reversed order and three
more shuffles run under `-m slow` (about 80 s for the full matrix).
"""

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


def _params():
    params = []
    for name in BUILD_PARAMS:
        for order in _orders(name):
            marks = [] if order == "shuffle" else [pytest.mark.slow]
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

    def reorder_effects(data: Character) -> Character:
        return Character(data.sources, apply_order=reorder)

    sheets = render_and_hash(name, tmp_path, prepare=reorder_effects)
    _assert_sheet_unchanged(name, sheets, f"effect apply order ({order})")


@pytest.mark.parametrize("name, order", _params())
def test_grant_order_keeps_sheet(name: str, order: str, tmp_path: Path):
    reorder = _orders(name)[order]

    def regrant(data: Character) -> Character:
        sources = data.sources
        sources.feature_grants = reorder(sources.feature_grants)
        sources.spell_grants = reorder(sources.spell_grants)
        sources.spell_replacements = reorder(sources.spell_replacements)
        return Character(sources)

    sheets = render_and_hash(name, tmp_path, prepare=regrant)
    _assert_sheet_unchanged(name, sheets, f"grant order ({order})")
