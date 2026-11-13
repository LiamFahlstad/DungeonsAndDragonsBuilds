"""The battle map's geometry (Combat/Arena/geometry.py): the square grid and
the Manhattan rule, and the contract every registered rule keeps."""

import pytest

from Combat.Arena.geometry import (
    DEFAULT_RULE,
    RULES,
    Cell,
    ManhattanRule,
    SquareGrid,
    rule_named,
)

MANHATTAN = ManhattanRule()
SQUARES = SquareGrid()


# ---------------------------------------------------------------------------
# Manhattan


def test_a_straight_line_counts_its_cells():
    assert MANHATTAN.steps(Cell(2, 3), Cell(2, 9)) == 6
    assert MANHATTAN.steps(Cell(0, 0), Cell(4, 0)) == 4


def test_a_diagonal_costs_two_steps():
    assert MANHATTAN.steps(Cell(0, 0), Cell(1, 1)) == 2
    assert MANHATTAN.steps(Cell(5, 5), Cell(2, 8)) == 6


def test_feet_on_5_foot_cells():
    assert MANHATTAN.feet(Cell(0, 0), Cell(3, 2), 5) == 25
    assert MANHATTAN.feet(Cell(0, 0), Cell(1, 0), 10) == 10


def test_a_square_has_four_neighbours_even_at_the_edge():
    """The map's edge is the arena's to cut, not the shape's."""
    assert set(SQUARES.neighbours(Cell(0, 0))) == {
        Cell(0, -1),
        Cell(1, 0),
        Cell(0, 1),
        Cell(-1, 0),
    }


def test_a_two_cell_footprint_is_four_cells_from_its_top_left():
    assert set(SQUARES.footprint(Cell(3, 4), 2)) == {
        Cell(3, 4),
        Cell(4, 4),
        Cell(3, 5),
        Cell(4, 5),
    }
    assert SQUARES.footprint(Cell(3, 4), 1) == [Cell(3, 4)]


def test_the_cell_a_point_falls_in():
    assert SQUARES.cell_at(0, 0, 40) == Cell(0, 0)
    assert SQUARES.cell_at(79.9, 40, 40) == Cell(1, 1)
    assert SQUARES.cell_at(-1, 5, 40) == Cell(-1, 0), "left of the map"


def test_tokens_start_from_the_edge_and_the_middle_row():
    order = SQUARES.from_edge(4, 5, left=True)
    assert order[:5] == [Cell(0, 2), Cell(0, 1), Cell(0, 3), Cell(0, 0), Cell(0, 4)]
    assert order[5] == Cell(1, 2)
    right = SQUARES.from_edge(4, 5, left=False)
    assert right[0] == Cell(3, 2)
    assert len(right) == len(set(right)) == 20


def test_a_cell_round_trips_as_a_position():
    assert Cell.of([3, 7]) == Cell(3, 7)
    assert Cell.of(Cell(3, 7)).to_list() == [3, 7]


def test_an_unknown_rule_is_the_default():
    """An old log with a rule since removed still opens."""
    assert rule_named("no such rule") is RULES[DEFAULT_RULE]
    assert rule_named("manhattan").key == "manhattan"


# ---------------------------------------------------------------------------
# Every registered rule keeps the same contract, so a new one is tested by
# being registered.

CELLS = [Cell(0, 0), Cell(3, 1), Cell(-2, 5), Cell(7, 7)]


@pytest.mark.parametrize("rule", list(RULES.values()), ids=list(RULES))
def test_every_rule_keeps_the_contract(rule):
    assert rule.key in RULES and rule.label and rule.shape is not None
    for a in CELLS:
        assert rule.steps(a, a) == 0
        assert rule.feet(a, a, 5) == 0
        for b in CELLS:
            assert rule.steps(a, b) == rule.steps(b, a)
            if a != b:
                assert rule.steps(a, b) > 0
        for step in rule.neighbours(a):
            assert rule.steps(a, step) == 1
            assert rule.step_cost(a, step) >= 1
        for size in (10, 37.5):
            x, y = rule.shape.center(a, size)
            assert rule.shape.cell_at(x, y, size) == a
            assert len(rule.shape.polygon(a, size)) >= 3
