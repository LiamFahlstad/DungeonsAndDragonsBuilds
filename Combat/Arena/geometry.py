"""The battle map's geometry, with no Qt (Notes/combat-arena-plan.md, step 1).

Two separate choices make a map: the grid's shape (how cells are laid out and
drawn, which are next to each other) and the distance rule (how far apart
two cells are on that shape). Several rules share one shape, so each
DistanceRule names the GridShape it works on, and RULES lists them by key.

Nothing outside this module does arithmetic on a cell's coordinates
(the plan's Decision 3): the arena and the view go through these two
interfaces, so a new shape or rule needs no change elsewhere.
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Cell:
    """One cell of the map. On squares, its column and row from the top-left
    (0, 0); a hex grid (later) keeps axial (q, r) in the same two fields."""

    col: int
    row: int

    @classmethod
    def of(cls, data) -> Cell:
        """A cell from what a combatant keeps (`[col, row]`), or a Cell."""
        if isinstance(data, Cell):
            return data
        col, row = data
        return cls(int(col), int(row))

    def to_list(self) -> list[int]:
        """What a combatant keeps as its "position": plain JSON."""
        return [self.col, self.row]


class GridShape(ABC):
    """How cells are laid out: which are next to each other, where each is
    drawn and which one a point falls in."""

    key: str

    @abstractmethod
    def neighbours(self, cell: Cell) -> list[Cell]:
        """The cells one step away, all of them: the map's edge is the
        arena's to cut."""

    @abstractmethod
    def center(self, cell: Cell, size_px: float) -> tuple[float, float]:
        """Where the cell's middle is drawn, for cells `size_px` across."""

    @abstractmethod
    def polygon(self, cell: Cell, size_px: float) -> list[tuple[float, float]]:
        """The cell's outline, corner by corner."""

    @abstractmethod
    def cell_at(self, x: float, y: float, size_px: float) -> Cell:
        """The cell the point (x, y) falls in."""

    @abstractmethod
    def footprint(self, anchor: Cell, cells: int) -> list[Cell]:
        """The cells a creature `cells` across covers, from its anchor."""

    @abstractmethod
    def in_bounds(self, cell: Cell, width: int, height: int) -> bool:
        """Whether the cell is on a map `width` by `height` cells."""

    @abstractmethod
    def cells(self, width: int, height: int) -> list[Cell]:
        """Every cell of a map `width` by `height` cells, row by row."""

    @abstractmethod
    def offset(self, cell: Cell, cols: int, rows: int) -> Cell:
        """The cell `cols` across and `rows` down from `cell` (the arena
        lines tokens up with it without touching coordinates)."""

    @abstractmethod
    def shifted(self, cell: Cell, start: Cell, end: Cell) -> Cell:
        """`cell` moved as far and the same way as from `start` to `end`:
        where a grappled creature keeps its place beside its grappler."""

    @abstractmethod
    def from_edge(self, width: int, height: int, left: bool) -> list[Cell]:
        """Every cell, from the left (or right) edge inward column by
        column, and in each column from the middle row outward: where
        tokens start (the plan's Q1)."""

    @abstractmethod
    def between(self, a: Cell, b: Cell) -> list[Cell]:
        """The cells of the block with a and b at opposite corners, a and b
        included: what the Map Painter's Shift+drag fills."""

    @abstractmethod
    def edges(
        self, cell: Cell, size_px: float
    ) -> list[tuple[Cell, tuple[tuple[float, float], tuple[float, float]]]]:
        """Each side of the cell's outline, with the cell on its other side:
        where the map draws a cliff between two heights."""

    @abstractmethod
    def crossed(self, a: Cell, b: Cell) -> list[tuple[Cell, ...]]:
        """The cells a straight line from a's middle to b's crosses on its
        way, in order, a and b left out: what cover is counted along. Where
        the line passes exactly through a corner, between two cells it only
        touches, those two are one step together."""

    @abstractmethod
    def labels(self, cell: Cell) -> tuple[str, str]:
        """The cell's column and row as the map's edges label them: ("C",
        "7")."""

    def cell_name(self, cell: Cell) -> str:
        """The cell's name in the log and on the map's edges: "C7"."""
        column, row = self.labels(cell)
        return f"{column}{row}"


def _letters(index: int) -> str:
    """0 A, 25 Z, 26 AA: a column's letters, as a spreadsheet names them."""
    letters = ""
    index += 1
    while index > 0:
        index, rest = divmod(index - 1, 26)
        letters = chr(ord("A") + rest) + letters
    return letters


class SquareGrid(GridShape):
    """Square cells, `size_px` on a side, (0, 0) at the top-left."""

    key = "square"

    def neighbours(self, cell: Cell) -> list[Cell]:
        c, r = cell.col, cell.row
        return [Cell(c, r - 1), Cell(c + 1, r), Cell(c, r + 1), Cell(c - 1, r)]

    def center(self, cell: Cell, size_px: float) -> tuple[float, float]:
        return ((cell.col + 0.5) * size_px, (cell.row + 0.5) * size_px)

    def polygon(self, cell: Cell, size_px: float) -> list[tuple[float, float]]:
        x, y = cell.col * size_px, cell.row * size_px
        return [(x, y), (x + size_px, y), (x + size_px, y + size_px), (x, y + size_px)]

    def cell_at(self, x: float, y: float, size_px: float) -> Cell:
        return Cell(math.floor(x / size_px), math.floor(y / size_px))

    def footprint(self, anchor: Cell, cells: int) -> list[Cell]:
        return [
            Cell(anchor.col + dc, anchor.row + dr)
            for dr in range(cells)
            for dc in range(cells)
        ]

    def in_bounds(self, cell: Cell, width: int, height: int) -> bool:
        return 0 <= cell.col < width and 0 <= cell.row < height

    def cells(self, width: int, height: int) -> list[Cell]:
        return [Cell(c, r) for r in range(height) for c in range(width)]

    def offset(self, cell: Cell, cols: int, rows: int) -> Cell:
        return Cell(cell.col + cols, cell.row + rows)

    def shifted(self, cell: Cell, start: Cell, end: Cell) -> Cell:
        return Cell(cell.col + end.col - start.col, cell.row + end.row - start.row)

    def from_edge(self, width: int, height: int, left: bool) -> list[Cell]:
        columns = range(width) if left else range(width - 1, -1, -1)
        middle = (height - 1) / 2
        rows = sorted(range(height), key=lambda r: (abs(r - middle), r))
        return [Cell(c, r) for c in columns for r in rows]

    def between(self, a: Cell, b: Cell) -> list[Cell]:
        cols = range(min(a.col, b.col), max(a.col, b.col) + 1)
        rows = range(min(a.row, b.row), max(a.row, b.row) + 1)
        return [Cell(c, r) for r in rows for c in cols]

    def edges(
        self, cell: Cell, size_px: float
    ) -> list[tuple[Cell, tuple[tuple[float, float], tuple[float, float]]]]:
        top_left, top_right, bottom_right, bottom_left = self.polygon(cell, size_px)
        up, right, down, left = self.neighbours(cell)
        return [
            (up, (top_left, top_right)),
            (right, (top_right, bottom_right)),
            (down, (bottom_right, bottom_left)),
            (left, (bottom_left, top_left)),
        ]

    def crossed(self, a: Cell, b: Cell) -> list[tuple[Cell, ...]]:
        # The line crosses a column edge at t = (0.5 + i) / |dc| and a row
        # edge at (0.5 + j) / |dr|; whichever comes first is the next step,
        # and both at once is a corner.
        dc, dr = b.col - a.col, b.row - a.row
        nc, nr = abs(dc), abs(dr)
        sc, sr = (dc > 0) - (dc < 0), (dr > 0) - (dr < 0)
        col, row, i, j = a.col, a.row, 0, 0
        steps: list[tuple[Cell, ...]] = []
        while i < nc or j < nr:
            order = (1 + 2 * i) * nr - (1 + 2 * j) * nc
            if order == 0:
                steps.append((Cell(col + sc, row), Cell(col, row + sr)))
                col, row, i, j = col + sc, row + sr, i + 1, j + 1
            elif order < 0:
                col, i = col + sc, i + 1
            else:
                row, j = row + sr, j + 1
            steps.append((Cell(col, row),))
        return steps[:-1]

    def labels(self, cell: Cell) -> tuple[str, str]:
        """Columns lettered from A at the left, rows numbered from 1 at the
        top."""
        return _letters(cell.col), str(cell.row + 1)


SQUARE_GRID = SquareGrid()


class DistanceRule(ABC):
    """How far apart two cells are on its shape, and what a step between
    neighbours costs."""

    key: str
    label: str
    shape: GridShape

    @abstractmethod
    def steps(self, a: Cell, b: Cell) -> float:
        """How many cells apart a and b are; a whole number for grid rules."""

    def feet(self, a: Cell, b: Cell, cell_ft: int) -> int:
        """The distance the UI shows, in feet, rounded down to whole feet."""
        return int(self.steps(a, b) * cell_ft)

    def step_cost(self, a: Cell, b: Cell) -> float:
        """What moving from a to its neighbour b costs, in cells."""
        return 1

    def neighbours(self, cell: Cell) -> list[Cell]:
        """The cells a move can step to from `cell`."""
        return self.shape.neighbours(cell)

    def with_height(self, flat_ft: int, rise_ft: int) -> int:
        """How far apart two points are, `flat_ft` across the map and
        `rise_ft` up or down (Notes/map-painter-plan.md, Decision 5): by
        default up counts as one more direction to step in, as Manhattan
        counts across and down, so the two add up."""
        return flat_ft + rise_ft


class ManhattanRule(DistanceRule):
    """Moves go up, down, left and right; a diagonal costs two steps."""

    key = "manhattan"
    label = "Manhattan (diagonals cost 2)"
    shape = SQUARE_GRID

    def steps(self, a: Cell, b: Cell) -> int:
        return abs(a.col - b.col) + abs(a.row - b.row)


RULES: dict[str, DistanceRule] = {rule.key: rule for rule in (ManhattanRule(),)}
DEFAULT_RULE = "manhattan"


def rule_named(key: str) -> DistanceRule:
    """The rule registered as `key`; the default one for a key nobody knows,
    so an old log with a rule removed since still opens."""
    return RULES.get(key, RULES[DEFAULT_RULE])
