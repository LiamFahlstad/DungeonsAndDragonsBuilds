"""Core/Rules.py against the 2024 Player's Handbook. Expected values are
copied from the book's tables, not worked out from the code."""

import pytest

from Core.Rules import (
    ALL_LEVELS,
    MAX_ABILITY_MODIFIER,
    MAX_PROFICIENCY_BONUS,
    POINT_BUY_BUDGET,
    STANDARD_ARRAY,
    ability_modifier,
    point_buy_cost,
    proficiency_bonus,
)

# Character Advancement table: proficiency bonus by level.
PHB_PROFICIENCY_BONUS = {
    **{level: 2 for level in range(1, 5)},
    **{level: 3 for level in range(5, 9)},
    **{level: 4 for level in range(9, 13)},
    **{level: 5 for level in range(13, 17)},
    **{level: 6 for level in range(17, 21)},
}

# Ability Scores and Modifiers table.
PHB_ABILITY_MODIFIER = {
    1: -5,
    2: -4,
    3: -4,
    4: -3,
    5: -3,
    6: -2,
    7: -2,
    8: -1,
    9: -1,
    10: 0,
    11: 0,
    12: 1,
    13: 1,
    14: 2,
    15: 2,
    16: 3,
    17: 3,
    18: 4,
    19: 4,
    20: 5,
    21: 5,
    22: 6,
    23: 6,
    24: 7,
    25: 7,
    26: 8,
    27: 8,
    28: 9,
    29: 9,
    30: 10,
}

# Ability Score Point Costs table.
PHB_POINT_BUY_COST = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}


def test_levels_run_from_1_to_20():
    assert list(ALL_LEVELS) == list(range(1, 21))


@pytest.mark.parametrize("level", sorted(PHB_PROFICIENCY_BONUS))
def test_proficiency_bonus(level):
    assert proficiency_bonus(level) == PHB_PROFICIENCY_BONUS[level]


def test_max_proficiency_bonus():
    assert MAX_PROFICIENCY_BONUS == 6


@pytest.mark.parametrize("score", sorted(PHB_ABILITY_MODIFIER))
def test_ability_modifier(score):
    assert ability_modifier(score) == PHB_ABILITY_MODIFIER[score]


def test_max_ability_modifier():
    assert MAX_ABILITY_MODIFIER == 10


@pytest.mark.parametrize("score", sorted(PHB_POINT_BUY_COST))
def test_point_buy_cost(score):
    assert point_buy_cost(score) == PHB_POINT_BUY_COST[score]


def test_point_buy_budget():
    assert POINT_BUY_BUDGET == 27


def test_standard_array():
    assert sorted(STANDARD_ARRAY) == [8, 10, 12, 13, 14, 15]
