"""The battle map's view (Notes/combat-arena-plan.md, steps 4-5): a grid
with a token for every combatant on the map. It draws token rows, never a
combatant dict (the plan's Decision 6), and has no rules in it: the cells
come from Combat/Arena's grid shape, the rows from token_rows.

Left click a token: the source, picked up to move. Right click: the target
(Ctrl adds one, Shift a range), as on the cards. A token picked up shades
the cells it can reach this turn with what each costs, and the next click on
an empty cell moves it there; clicking it again puts it down where it was.
Or drag a token to a cell (step 6). Shift held as the token is dropped (the
drag's release, or the click on the cell) teleports it there, Alt pushes it
(step 17, MoveKind): neither is the creature's own movement. Whose turn it is stands on gold cells,
as its card is gold. With a source selected, hovering a cell or a token
shows how far it is (step 7). Ctrl+wheel zooms; dragging empty space
pans. Columns are lettered and rows numbered, so a cell is "C7".

Picking targets in an area (step 10, start_area): the cells an area covers
where the mouse is are shaded orange, with an orange ring on each token in
it; a left click picks them, a right click cancels. Nothing is picked up or
moved meanwhile. The shading is the colour the area bar picked.

Areas that stay (step 11, Combat/Arena/lasting.py): each drawn over the grid
in its own colour, with its name, the edge dashed while its caster
concentrates on it. A click on an empty cell of one selects it (step 12),
edged brighter; another click there goes to the next area on that cell. A
wall's damaging side (Wall of Fire, step 25) is shaded fainter, unedged.

The terrain painted in the Map Painter (draw_terrain; Notes/
map-painter-plan.md) is drawn over the grid, under the areas and tokens."""

from __future__ import annotations

import re

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from Combat.Arena.arena import ArenaSettings, footprint
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import DEFAULT_AREA_COLOR, LastingArea
from Combat.Arena.terrain import BRIGHT, DARK, DIFFICULT, WALL, WATER
from Combat.Effects.triggers import on_party_side

from .player_view import _can_be_seen

CELL_PX = 40.0

# The cards' colours (styles.py): white the source, gold whose turn it is,
# red the target; the party's side blue, everyone else red (the plan's Q5).
_BACKGROUND = QColor("#1a1a2e")
_GRID = QColor("#2c3550")
_COORDS = QColor("#6b7390")
_PARTY = QColor("#2f6fb5")
_ENEMY = QColor("#a8323e")
_DOWN = QColor("#4a4a55")
_SOURCE = QColor("#ffffff")
_TURN = QColor("#c9a84c")
_TARGET = QColor("#e74c3c")
_HP_BAR = QColor("#5ec269")
_HP_BAR_LOW = QColor("#e0a030")
_REACH = QColor(94, 194, 105, 60)
# Under whose turn it is: the active card's gold border on its gold tint.
_TURN_CELL = QColor(201, 168, 76, 110)
_REACH_TEXT = QColor("#b8e6be")
_HOVER_TEXT = QColor("#ffffff")
_HOVER_BACK = QColor(10, 10, 20, 200)
# An area of effect being aimed (step 10): its fill's and edge's opacity,
# out of 255, in the colour picked (orange unless the bar says otherwise).
_AREA_ALPHA = 110
_AREA_EDGE_ALPHA = 200
# An area that stays (step 11): fainter, so what's aimed shows over it.
_LASTING_ALPHA = 70
_LASTING_EDGE_ALPHA = 220
# A wall's damaging side (step 25): fainter still.
_LASTING_SIDE_ALPHA = 30
# How far the mouse goes before a press on a token is a drag, not a click.
_DRAG_PX = 6
# The painted terrain (draw_terrain; Notes/map-painter-plan.md).
_WALL = QColor("#5b544c")
_WALL_EDGE = QColor("#7a7166")
_WATER = QColor(52, 120, 200, 120)
_DIFFICULT = QColor("#a88c5a")
_HIGH = QColor("#ffffff")
_LOW = QColor("#000000")
_HEIGHT_ALPHA_MAX = 90
_HEIGHT_TEXT = QColor("#e8dcb0")
_CLIFF = QColor("#e4ddcc")  # not gold: gold is whose turn it is
_HAZARD = QColor(192, 57, 43, 200)
_BLOCKING = QColor(125, 104, 78, 230)
_FURNITURE = QColor(160, 138, 96, 170)
_DIM = QColor(0, 0, 0, 80)
_DARKNESS = QColor(0, 0, 0, 165)


class MoveKind(Enum):
    """How a token dropped on a cell gets there (step 17). A walk is the
    creature's own movement. A teleport (Rules Glossary, Teleportation) and
    a push (a Shove, Thunderwave) aren't: they spend no movement and
    provoke no Opportunity Attack. A drag (step 22) is a Grappled creature
    taken along by its grappler's walk: no key asks for it."""

    WALK = "walk"
    TELEPORT = "teleport"
    PUSH = "push"
    DRAG = "drag"


def move_kind(modifiers) -> MoveKind:
    """The move the keys held as a token is dropped ask for: Shift a
    teleport, Alt a push (Shift wins when both are held), else a walk."""
    if modifiers & Qt.KeyboardModifier.ShiftModifier:
        return MoveKind.TELEPORT
    if modifiers & Qt.KeyboardModifier.AltModifier:
        return MoveKind.PUSH
    return MoveKind.WALK


@dataclass(frozen=True)
class TokenRow:
    """What the view draws for one combatant on the map."""

    name: str
    label: str  # "G2", "HD": its first letters
    cells: tuple[Cell, ...]
    party: bool  # the party's side: blue, else red
    hp_fraction: float | None  # None: no Hit Points to show
    turn: bool = False  # whose turn it is: a gold ring
    source: bool = False
    target: bool = False
    down: bool = False  # at 0 HP: greyed (the plan's Q9)
    hidden: bool = False  # unseen by the players: dashed


def token_label(name: str) -> str:
    """A token's letters: "Goblin 2" G2, "(1) Accursed Group of 5" A1,
    "Accursed Group of 3" AG, "Hanna's Drake Companion" HD, "Ogre" OG."""
    number = ""
    numbered = re.match(r"\((\d+)\)\s*(.*)", name)
    rest = name
    if numbered:
        number, rest = numbered.groups()
    words = rest.replace("'s ", " ").split()
    # "Group of 3" is how many, not which one.
    counted = len(words) > 2 and words[-2].lower() == "of"
    if not number and len(words) > 1 and words[-1].isdigit() and not counted:
        number, words = words[-1], words[:-1]
    words = [w for w in words if w[:1].isalpha()]
    if not words:
        return number or "?"
    if number:
        return f"{words[0][0].upper()}{number}"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[1][0]).upper()


def token_rows(
    chars: list[dict],
    settings: ArenaSettings,
    turn: list[dict],
    source: dict | None,
    targets: list[dict],
) -> list[TokenRow]:
    """A row for each of `chars` on the map, in their order: `turn` the
    ones whose turn it is, `source` and `targets` the selection."""
    rule = settings.distance_rule
    rows = []
    for char in chars:
        cells = footprint(char, rule)
        if not cells:
            continue
        hp, max_hp = char.get("hp"), char.get("max_hp")
        fraction, down = None, False
        if isinstance(hp, (int, float)) and isinstance(max_hp, (int, float)):
            down = hp <= 0
            if max_hp > 0:
                fraction = max(0.0, min(1.0, hp / max_hp))
        rows.append(
            TokenRow(
                name=char["name"],
                label=token_label(char["name"]),
                cells=tuple(cells),
                party=on_party_side(char),
                hp_fraction=fraction,
                turn=any(char is c for c in turn),
                source=char is source,
                target=any(char is t for t in targets),
                down=down,
                hidden=not _can_be_seen(char),
            )
        )
    return rows


class ArenaView(QGraphicsView):
    """The map: the grid of `settings` and a token per row. Clicks go to
    `on_select(name)` and `on_target(name, ctrl, shift)`; a token picked up
    (a left click) or dragged goes to the cell clicked or dropped on with
    `on_move(name, anchor, kind)`, kind the MoveKind the keys held ask
    for; a click on an empty cell with nothing picked up
    to `on_cell(cell)`; `reach_of(name)` is what a picked-up token shades."""

    def __init__(
        self,
        on_select: Callable[[str], None],
        on_target: Callable[[str, bool, bool], None],
        on_move: Callable[[str, Cell, MoveKind], None] = lambda name, cell, kind: None,
        on_cell: Callable[[Cell], None] = lambda cell: None,
        reach_of: Callable[[str], dict[Cell, int]] = lambda name: {},
        distance_at: Callable[[Cell], str | None] = lambda cell: None,
        on_area: Callable[[str], None] = lambda key: None,
    ):
        super().__init__()
        self.setObjectName("arenaView")
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QBrush(_BACKGROUND))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._on_select = on_select
        self._on_target = on_target
        self._on_move = on_move
        self._on_cell = on_cell
        self._reach_of = reach_of
        self._distance_at = distance_at
        self._on_area = on_area
        # The hover distance by the cursor ("25 ft.", step 7): its text and
        # where it's drawn, so a redraw keeps it.
        self._hover: tuple[str, QPointF] | None = None
        viewport = self.viewport()
        if viewport is not None:
            viewport.setMouseTracking(True)
        # A press: where, and on which token (None: empty space).
        self._press: QPointF | None = None
        self._press_row: TokenRow | None = None
        self._grabbed: Cell | None = None
        # While a token is dragged, or picked up by a click to be moved by
        # the next click on a cell: the cells it can reach, and costs.
        self._dragging: str | None = None
        self._picked: str | None = None
        self._reach: dict[Cell, int] = {}
        self._settings = ArenaSettings()
        self._rows: list[TokenRow] = []
        self._drawn: tuple | None = None
        # The whole map fits the view until the GM zooms (Ctrl+wheel).
        self._zoomed = False
        # An area being aimed (start_area): the cells it covers for a cell
        # aimed at, what a click and a cancel do, what to tell as it moves;
        # and where it's aimed now, and the cells it covers there.
        self._area: (
            tuple[
                Callable[[Cell | None], set[Cell]],
                Callable[[Cell], None],
                Callable[[], object],
                Callable[[set[Cell]], None],
            ]
            | None
        ) = None
        self._area_aim: Cell | None = None
        self._area_cells: set[Cell] = set()
        self._area_color = QColor(DEFAULT_AREA_COLOR)
        # The areas that stay on the map (step 11), drawn under the tokens.
        self._lasting: list[LastingArea] = []

    @property
    def rows(self) -> list[TokenRow]:
        return list(self._rows)

    @property
    def lasting(self) -> list[LastingArea]:
        """The areas that stay, drawn now (tests)."""
        return list(self._lasting)

    def show_rows(
        self,
        settings: ArenaSettings,
        rows: list[TokenRow],
        lasting: list[LastingArea] | None = None,
    ):
        """Draw the map of `settings` with `rows`, and the areas that stay
        (`lasting`; None keeps those drawn); nothing when nothing changed
        since the last time."""
        if lasting is not None:
            self._lasting = list(lasting)
        key = (
            settings.to_dict(),
            tuple(rows),
            tuple(self._lasting),
            self._area_color.name(),
        )
        if key == self._drawn:
            return
        self._drawn = key
        self._settings, self._rows = settings, list(rows)
        self._scene.clear()
        self._draw_grid()
        draw_terrain(self._scene, settings)
        for area in self._lasting:
            self._draw_lasting(area)
        if self._picked is not None and self._dragging is None:
            # Whoever moved since it was picked up changes where it can go.
            self._reach = self._reach_of(self._picked)
        if self._dragging is not None or self._picked is not None:
            self._draw_reach()
        self._draw_area()
        for row in rows:
            if row.turn:
                self._draw_turn_cells(row)
        for row in rows:
            self._draw_token(row)
            if self._area_cells.intersection(row.cells):
                self._draw_area_ring(row)
        self._draw_hover()
        margin = CELL_PX
        width, height = settings.width * CELL_PX, settings.height * CELL_PX
        self._scene.setSceneRect(
            QRectF(-margin, -margin, width + 2 * margin, height + 2 * margin)
        )
        self._fit()

    def _fit(self):
        if not self._zoomed:
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()

    def showEvent(self, event):
        super().showEvent(event)
        self._fit()

    def _draw_reach(self):
        """Shade the cells the picked-up token can reach, with their costs."""
        shape = self._settings.distance_rule.shape
        font = QFont("Segoe UI", 7)
        for cell, feet in self._reach.items():
            points = [QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)]
            self._scene.addPolygon(
                QPolygonF(points), QPen(Qt.PenStyle.NoPen), QBrush(_REACH)
            )
            if feet:
                label = QGraphicsSimpleTextItem(str(feet))
                label.setFont(font)
                label.setBrush(QBrush(_REACH_TEXT))
                self._scene.addItem(label)
                x, y = shape.polygon(cell, CELL_PX)[0]
                label.setPos(x + 2, y + 1)

    def _draw_area(self):
        """Shade the cells the area being aimed covers, edged, in the
        colour picked."""
        shape = self._settings.distance_rule.shape
        pen = QPen(_with_alpha(self._area_color, _AREA_EDGE_ALPHA))
        pen.setWidthF(1.0)
        brush = QBrush(_with_alpha(self._area_color, _AREA_ALPHA))
        for cell in self._area_cells:
            points = [QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)]
            self._scene.addPolygon(QPolygonF(points), pen, brush)

    def _draw_lasting(self, area: LastingArea):
        """An area that stays: its cells in its colour, edged (dashed while
        its caster concentrates on it), its name in its top-left cell and
        as the cells' tooltip."""
        shape = self._settings.distance_rule.shape
        colour = QColor(area.color)
        pen = QPen(_with_alpha(colour, _LASTING_EDGE_ALPHA))
        pen.setWidthF(1.0)
        if area.selected:
            pen = QPen(colour.lighter(170))
            pen.setWidthF(2.5)
        if area.concentration:
            pen.setStyle(Qt.PenStyle.DashLine)
        brush = QBrush(_with_alpha(colour, _LASTING_ALPHA))
        tip = area.title + (" (concentration)" if area.concentration else "")
        side = QBrush(_with_alpha(colour, _LASTING_SIDE_ALPHA))
        for cell in area.side - area.cells:
            points = [QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)]
            item = self._scene.addPolygon(
                QPolygonF(points), QPen(Qt.PenStyle.NoPen), side
            )
            if item is not None:
                item.setToolTip(f"{area.title}: its damaging side")
        for cell in area.cells:
            points = [QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)]
            item = self._scene.addPolygon(QPolygonF(points), pen, brush)
            if item is not None:
                item.setToolTip(tip)
        corner = min(area.cells, key=lambda c: (c.row, c.col))
        label = QGraphicsSimpleTextItem(area.name)
        label.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        label.setBrush(QBrush(colour.lighter(150)))
        self._scene.addItem(label)
        x, y = shape.polygon(corner, CELL_PX)[0]
        label.setPos(x + 2, y + 1)

    def set_area_color(self, color: str):
        """The colour the area being aimed is shaded in ("#e67e22")."""
        colour = QColor(color)
        if not colour.isValid() or colour == self._area_color:
            return
        self._area_color = colour
        self._redraw()

    @property
    def area_color(self) -> str:
        """The aiming shading's colour, as "#rrggbb" (tests)."""
        return self._area_color.name()

    def _draw_area_ring(self, row: TokenRow):
        """An orange ring around a token in the area being aimed."""
        shape = self._settings.distance_rule.shape
        corners = [p for cell in row.cells for p in shape.polygon(cell, CELL_PX)]
        xs, ys = [x for x, _ in corners], [y for _, y in corners]
        box = QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        ring = QPen(self._area_color)
        ring.setWidthF(2.5)
        inside = box.adjusted(1.5, 1.5, -1.5, -1.5)
        if len(row.cells) == 1:
            self._scene.addEllipse(inside, ring)
        else:
            self._scene.addRect(inside, ring)

    @property
    def aiming_area(self) -> bool:
        """Whether an area is being aimed (start_area)."""
        return self._area is not None

    @property
    def area_aim(self) -> Cell | None:
        """The cell the area being aimed is aimed at, if any yet."""
        return self._area_aim if self._area is not None else None

    def area_shown(self) -> set[Cell]:
        """The cells the area being aimed covers now (tests)."""
        return set(self._area_cells)

    def start_area(
        self,
        cells_at: Callable[[Cell | None], set[Cell]],
        on_pick: Callable[[Cell], None],
        on_cancel: Callable[[], object],
        on_aim: Callable[[set[Cell]], None] = lambda cells: None,
    ):
        """Aim an area: `cells_at(cell)` is what it covers aimed at the cell
        (None: not aimed yet, which is all an Emanation needs). Hovering
        aims it, a left click goes to `on_pick(cell)`, a right click to
        `on_cancel()`, and each change of the cells to `on_aim(cells)`.
        Whoever was picked up is put down."""
        self._dragging, self._reach = None, {}
        self._picked = None
        self._area = (cells_at, on_pick, on_cancel, on_aim)
        self._area_aim = None
        self.refresh_area()

    def refresh_area(self):
        """Work the area's cells out again where it's aimed (its shape or
        size changed, or someone moved)."""
        if self._area is None:
            return
        self._area_cells = set(self._area[0](self._area_aim))
        self._area[3](set(self._area_cells))
        self._redraw()

    def aim_area(self, cell: Cell):
        """Aim the area at `cell`; the map is redrawn when what it covers
        changes."""
        if self._area is None or cell == self._area_aim:
            return
        self._area_aim = cell
        cells = set(self._area[0](cell))
        if cells != self._area_cells:
            self._area_cells = cells
            self._area[3](set(cells))
            self._redraw()

    def stop_area(self):
        """Stop aiming: the shading goes."""
        if self._area is None:
            return
        self._area, self._area_aim, self._area_cells = None, None, set()
        self._redraw()

    def _draw_turn_cells(self, row: TokenRow):
        """Whose turn it is stands on gold: the cells under it tinted and
        edged gold, as the active card is."""
        shape = self._settings.distance_rule.shape
        pen = QPen(_TURN)
        pen.setWidthF(2.0)
        for cell in row.cells:
            points = [QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)]
            self._scene.addPolygon(
                QPolygonF(points), QPen(Qt.PenStyle.NoPen), QBrush(_TURN_CELL)
            )
        corners = [p for cell in row.cells for p in shape.polygon(cell, CELL_PX)]
        xs, ys = [x for x, _ in corners], [y for _, y in corners]
        self._scene.addRect(
            QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)), pen
        )

    def _draw_hover(self):
        if self._hover is None:
            return
        text, at = self._hover
        label = QGraphicsSimpleTextItem(text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        label.setBrush(QBrush(_HOVER_TEXT))
        box = label.boundingRect()
        back = QGraphicsRectItem(QRectF(0, 0, box.width() + 8, box.height() + 4))
        back.setBrush(QBrush(_HOVER_BACK))
        back.setPen(QPen(Qt.PenStyle.NoPen))
        back.setZValue(10)
        label.setZValue(11)
        self._scene.addItem(back)
        self._scene.addItem(label)
        self._hover_items = (back, label)
        self._place_hover(at)

    def _place_hover(self, at: QPointF):
        back, label = self._hover_items
        back.setPos(at.x() + 12, at.y() + 12)
        label.setPos(at.x() + 16, at.y() + 14)

    def hover(self, cell: Cell, at: QPointF | None = None):
        """Show how far `cell` is from the source next to `at` (the cell's
        middle when not given), or nothing when there's nothing to say. The
        map is redrawn only when the text changes; otherwise the label just
        follows the cursor."""
        text = self._distance_at(cell)
        if at is None:
            x, y = self._settings.distance_rule.shape.center(cell, CELL_PX)
            at = QPointF(x, y)
        shown = self._hover[0] if self._hover is not None else None
        self._hover = (text, at) if text is not None else None
        if text != shown:
            self._redraw()
        elif text is not None:
            self._place_hover(at)

    def hover_text(self) -> str | None:
        """The hover distance shown now (tests)."""
        return self._hover[0] if self._hover is not None else None

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        if self._hover is not None:
            self._hover = None
            self._redraw()

    def reach_shown(self) -> dict[Cell, int]:
        """The cells shaded now (tests)."""
        moving = self._dragging is not None or self._picked is not None
        return dict(self._reach) if moving else {}

    def _redraw(self):
        self._drawn = None
        self.show_rows(self._settings, self._rows)

    def _draw_grid(self):
        settings = self._settings
        shape = settings.distance_rule.shape
        pen = QPen(_GRID)
        pen.setWidthF(1.0)
        for cell in shape.cells(settings.width, settings.height):
            points = [QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)]
            self._scene.addPolygon(QPolygonF(points), pen)
        font = QFont("Segoe UI", 8)
        for cell in shape.cells(settings.width, settings.height):
            first_row = not settings.on_map(shape.offset(cell, 0, -1))
            first_col = not settings.on_map(shape.offset(cell, -1, 0))
            x, y = shape.center(cell, CELL_PX)
            column, row = shape.labels(cell)
            if first_row:
                self._coord(column, x, y - CELL_PX, font)
            if first_col:
                self._coord(row, x - CELL_PX, y, font)

    def _coord(self, text: str, x: float, y: float, font: QFont):
        item = QGraphicsSimpleTextItem(text)
        item.setFont(font)
        self._scene.addItem(item)
        item.setBrush(QBrush(_COORDS))
        box = item.boundingRect()
        item.setPos(x - box.width() / 2, y - box.height() / 2)

    def _draw_token(self, row: TokenRow):
        shape = self._settings.distance_rule.shape
        corners = [p for cell in row.cells for p in shape.polygon(cell, CELL_PX)]
        xs, ys = [x for x, _ in corners], [y for _, y in corners]
        inset = 4.0
        box = QRectF(
            min(xs) + inset,
            min(ys) + inset,
            max(xs) - min(xs) - 2 * inset,
            max(ys) - min(ys) - 2 * inset,
        )
        fill = _DOWN if row.down else (_PARTY if row.party else _ENEMY)
        pen = QPen(
            _SOURCE if row.source else _TARGET if row.target else fill.lighter(140)
        )
        pen.setWidthF(3.0 if row.source or row.target else 1.5)
        if row.hidden:
            pen.setStyle(Qt.PenStyle.DashLine)
        brush = QBrush(fill)
        token = (
            QGraphicsEllipseItem(box) if len(row.cells) == 1 else QGraphicsRectItem(box)
        )
        token.setPen(pen)
        token.setBrush(brush)
        token.setToolTip(row.name)
        self._scene.addItem(token)
        if row.turn:
            ring = QPen(_TURN)
            ring.setWidthF(3.0)
            grown = box.adjusted(-3, -3, 3, 3)
            if len(row.cells) == 1:
                self._scene.addEllipse(grown, ring)
            else:
                self._scene.addRect(grown, ring)
        if row.source and row.target:
            inner = QPen(_TARGET)
            inner.setWidthF(2.0)
            shrunk = box.adjusted(4, 4, -4, -4)
            if len(row.cells) == 1:
                self._scene.addEllipse(shrunk, inner)
            else:
                self._scene.addRect(shrunk, inner)
        font = QFont("Segoe UI", 10 if len(row.cells) == 1 else 14, QFont.Weight.Bold)
        text = QGraphicsSimpleTextItem(row.label)
        text.setFont(font)
        self._scene.addItem(text)
        text.setBrush(QBrush(QColor("#9a9aa5") if row.down else QColor("#ffffff")))
        rect = text.boundingRect()
        text.setPos(
            box.center().x() - rect.width() / 2, box.center().y() - rect.height() / 2
        )
        if row.hp_fraction is not None:
            bar_w = box.width() * 0.8
            left = box.center().x() - bar_w / 2
            top = box.bottom() - 6
            self._scene.addRect(
                QRectF(left, top, bar_w, 3), QPen(Qt.PenStyle.NoPen), QBrush(_DOWN)
            )
            if row.hp_fraction > 0:
                colour = _HP_BAR if row.hp_fraction > 0.5 else _HP_BAR_LOW
                self._scene.addRect(
                    QRectF(left, top, bar_w * row.hp_fraction, 3),
                    QPen(Qt.PenStyle.NoPen),
                    QBrush(colour),
                )

    def token_at(self, scene_x: float, scene_y: float) -> TokenRow | None:
        """The token covering the scene point, if any."""
        shape = self._settings.distance_rule.shape
        cell = shape.cell_at(scene_x, scene_y, CELL_PX)
        return next((row for row in self._rows if cell in row.cells), None)

    def cell_center(self, cell: Cell) -> QPointF:
        """Where a cell's middle is in the view's own coordinates (tests)."""
        x, y = self._settings.distance_rule.shape.center(cell, CELL_PX)
        return QPointF(self.mapFromScene(QPointF(x, y)))

    def click(self, row: TokenRow, button: Qt.MouseButton, modifiers):
        """What a click on `row`'s token does."""
        if button == Qt.MouseButton.LeftButton:
            self._on_select(row.name)
        elif button == Qt.MouseButton.RightButton:
            self._on_target(
                row.name,
                bool(modifiers & Qt.KeyboardModifier.ControlModifier),
                bool(modifiers & Qt.KeyboardModifier.ShiftModifier),
            )

    def pick_up(self, row: TokenRow, grabbed: Cell | None = None):
        """Start dragging `row`'s token, held by its cell `grabbed` (its
        anchor when not given): shade where it can go."""
        self._dragging = row.name
        self._grabbed = grabbed if grabbed is not None else row.cells[0]
        self._reach = self._reach_of(row.name)
        self._redraw()

    def drop(self, cell: Cell, kind: MoveKind = MoveKind.WALK):
        """Put the dragged token down with its held cell on `cell`, moved
        there as `kind`."""
        name, row = self._dragging, self._row_named(self._dragging)
        self._dragging, self._picked, self._reach = None, None, {}
        if name is None or row is None:
            return
        anchor = self._anchor_for(row, cell)
        if anchor is not None and anchor != row.cells[0]:
            self._on_move(name, anchor, kind)
        self._redraw()

    @property
    def picked(self) -> str | None:
        """Who a click picked up, to be moved by the next click on a cell."""
        return self._picked

    def pick(self, name: str, grabbed: Cell | None = None):
        """Pick up `name` by a click, held by its cell `grabbed` (its anchor
        when not given), shading where it can go; the next click on an empty
        cell moves it there (move_picked). One not on the map yet is put on
        the cell clicked."""
        row = self._row_named(name)
        self._picked = name
        held = row.cells[0] if row is not None else None
        self._grabbed = grabbed if grabbed is not None else held
        self._reach = self._reach_of(name)
        self._redraw()

    def unpick(self):
        """Put the picked-up token down where it is (no move); the map is
        redrawn by the next show_rows or _redraw."""
        if self._picked is None:
            return
        self._picked = None
        if self._dragging is None:
            self._reach = {}
        self._drawn = None

    def move_picked(self, cell: Cell, kind: MoveKind = MoveKind.WALK):
        """Move the picked-up token to `cell`, by the cell it was picked up
        by, as `kind`, as a drop does."""
        name, row = self._picked, self._row_named(self._picked)
        self._picked, self._reach = None, {}
        if name is None:
            return
        if row is None:
            self._on_move(name, cell, kind)  # not on the map yet: put it there
        else:
            anchor = self._anchor_for(row, cell)
            if anchor is not None and anchor != row.cells[0]:
                self._on_move(name, anchor, kind)
        self._redraw()

    def _row_named(self, name: str | None) -> TokenRow | None:
        return next((r for r in self._rows if r.name == name), None)

    def _anchor_for(self, row: TokenRow, cell: Cell) -> Cell | None:
        """The anchor that puts row's held cell on `cell`: for one cell, the
        cell itself; for a Large token held by another cell, the anchor whose
        footprint has that cell where the held one is in it now."""
        shape = self._settings.distance_rule.shape
        across = round(len(row.cells) ** 0.5)
        held = row.cells.index(self._grabbed) if self._grabbed in row.cells else 0
        corner = shape.offset(cell, 1 - across, 1 - across)
        for anchor in shape.footprint(corner, across):
            if shape.footprint(anchor, across)[held] == cell:
                return anchor
        return None

    def mousePressEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        point = self.mapToScene(event.position().toPoint())
        row = self.token_at(point.x(), point.y())
        self._press = event.position()
        self._press_row = None
        if self._area is not None:
            # Aiming: a right click cancels, a left press only pans until
            # its release picks.
            if event.button() == Qt.MouseButton.RightButton:
                self._press = None
                self._area[2]()
                event.accept()
                return
            super().mousePressEvent(event)
            return
        if row is not None and event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            if event.button() == Qt.MouseButton.LeftButton:
                shape = self._settings.distance_rule.shape
                self._press_row = row
                self._grabbed = shape.cell_at(point.x(), point.y(), CELL_PX)
            self.click(row, event.button(), event.modifiers())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent | None):
        """A quick second click is a click too, as on the cards (the view's
        own double-click would only go to the scene)."""
        self.mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        point = self.mapToScene(event.position().toPoint())
        cell = self._settings.distance_rule.shape.cell_at(point.x(), point.y(), CELL_PX)
        if self._settings.on_map(cell):
            self.hover(cell, point)
            self.aim_area(cell)
        elif self._hover is not None:
            self._hover = None
            self._redraw()
        row = self._press_row
        if row is not None and self._dragging is None and self._press is not None:
            if (event.position() - self._press).manhattanLength() >= _DRAG_PX:
                self.pick_up(self._row_named(row.name) or row, self._grabbed)
        if self._dragging is not None:
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        point = self.mapToScene(event.position().toPoint())
        shape = self._settings.distance_rule.shape
        cell = shape.cell_at(point.x(), point.y(), CELL_PX)
        pressed, self._press = self._press, None
        pressed_row, self._press_row = self._press_row, None
        kind = move_kind(event.modifiers())
        if self._dragging is not None:
            self.drop(cell, kind)
            event.accept()
            return
        super().mouseReleaseEvent(event)
        clicked = (
            pressed is not None
            and (event.position() - pressed).manhattanLength() < _DRAG_PX
        )
        if not clicked or event.button() != Qt.MouseButton.LeftButton:
            return
        if self._area is not None:
            if self._settings.on_map(cell):
                self.aim_area(cell)
                self._area[1](cell)
            return
        if pressed_row is not None:
            # A click on a token picks it up, or puts it down again.
            if self._picked == pressed_row.name:
                self.unpick()
                self._redraw()
            else:
                self.pick(pressed_row.name, self._grabbed)
        elif self.token_at(point.x(), point.y()) is None:
            if not self._settings.on_map(cell):
                return
            if self._picked is not None:
                self.move_picked(cell, kind)
            else:
                self.click_cell(cell)

    def click_cell(self, cell: Cell):
        """An empty cell clicked with nothing picked up: the area that stays
        on it is selected (`on_area`), the next one on it when the one
        selected is there too; with none, `on_cell`."""
        here = [area for area in self._lasting if cell in area.cells]
        if not here:
            self._on_cell(cell)
            return
        chosen = next((i for i, area in enumerate(here) if area.selected), -1)
        self._on_area(here[(chosen + 1) % len(here)].key)

    def wheelEvent(self, event: QWheelEvent | None):
        if event is None:
            return
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            zoom = self.transform().m11() * factor
            if 0.3 <= zoom <= 4.0:
                self.scale(factor, factor)
                self._zoomed = True
            event.accept()
            return
        super().wheelEvent(event)


def draw_terrain(scene: QGraphicsScene, settings: ArenaSettings):
    """The map's painted terrain (Combat/Arena/terrain.py), over the grid
    and under everything else: walls solid stone, Difficult Terrain dotted,
    water blue; ground above 0 lighter and below darker, with its height in
    the corner and a pale edge where it drops to a lower cell; objects as
    labelled blocks (hazards red); Dim Light and Darkness shading the cells
    last, so they dim what's on them but never the tokens drawn after."""
    terrain = settings.terrain
    shape = settings.distance_rule.shape
    cells = [cell for cell in terrain.cells if settings.on_map(cell)]
    if not cells:
        return
    none = QPen(Qt.PenStyle.NoPen)

    def outline(cell: Cell) -> QPolygonF:
        return QPolygonF([QPointF(x, y) for x, y in shape.polygon(cell, CELL_PX)])

    small = QFont("Segoe UI", 7)
    for cell in cells:
        spot = terrain.at(cell)
        tip = "\n".join([shape.cell_name(cell), *terrain.describe(cell)])
        if spot.ground == WALL:
            item = scene.addPolygon(outline(cell), QPen(_WALL_EDGE), QBrush(_WALL))
        elif spot.ground == WATER:
            item = scene.addPolygon(outline(cell), none, QBrush(_WATER))
        elif spot.ground == DIFFICULT:
            item = scene.addPolygon(
                outline(cell), none, QBrush(_DIFFICULT, Qt.BrushStyle.Dense6Pattern)
            )
        else:
            item = scene.addPolygon(outline(cell), none, QBrush(Qt.BrushStyle.NoBrush))
        if item is not None:
            item.setToolTip(tip)
        if spot.height_ft:
            shade = _HIGH if spot.height_ft > 0 else _LOW
            alpha = min(_HEIGHT_ALPHA_MAX, 25 + abs(spot.height_ft) * 2)
            scene.addPolygon(outline(cell), none, QBrush(_with_alpha(shade, alpha)))
            label = QGraphicsSimpleTextItem(f"{spot.height_ft:+d}")
            label.setFont(small)
            label.setBrush(QBrush(_HEIGHT_TEXT))
            scene.addItem(label)
            box = label.boundingRect()
            corners = shape.polygon(cell, CELL_PX)
            right, bottom = max(x for x, _ in corners), max(y for _, y in corners)
            label.setPos(right - box.width() - 2, bottom - box.height())
    cliff = QPen(_CLIFF)
    cliff.setWidthF(2.5)
    for cell in cells:
        for other, (a, b) in shape.edges(cell, CELL_PX):
            if settings.on_map(other) and terrain.height(other) < terrain.height(cell):
                scene.addLine(a[0], a[1], b[0], b[1], cliff)
    for cell in cells:
        thing = terrain.at(cell).thing
        if thing is not None:
            _draw_object(scene, settings, cell, thing)
    for cell in cells:
        light = terrain.at(cell).light
        if light != BRIGHT:
            scene.addPolygon(
                outline(cell), none, QBrush(_DARKNESS if light == DARK else _DIM)
            )


def _draw_object(scene: QGraphicsScene, settings: ArenaSettings, cell: Cell, thing):
    """An object on `cell`: a rounded block, its name on the first cell of a
    run of the same object (left and above), the rest in its tooltip."""
    shape = settings.distance_rule.shape
    corners = shape.polygon(cell, CELL_PX)
    xs, ys = [x for x, _ in corners], [y for _, y in corners]
    box = QRectF(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    fill = _HAZARD if thing.hazard else _BLOCKING if thing.blocks else _FURNITURE
    pen = QPen(fill.lighter(150))
    pen.setWidthF(1.5)
    path = QPainterPath()
    path.addRoundedRect(box.adjusted(5, 5, -5, -5), 6, 6)
    item = scene.addPath(path, pen, QBrush(fill))
    if item is not None:
        item.setToolTip(f"{shape.cell_name(cell)}\n{thing.describe()}")
    terrain = settings.terrain
    same = [
        terrain.at(shape.offset(cell, -1, 0)).thing,
        terrain.at(shape.offset(cell, 0, -1)).thing,
    ]
    if any(other is not None and other.name == thing.name for other in same):
        return
    label = QGraphicsSimpleTextItem(thing.name)
    label.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
    label.setBrush(QBrush(QColor("#f4ecd8")))
    scene.addItem(label)
    label.setPos(box.left() + 3, box.top() + 1)


def _with_alpha(colour: QColor, alpha: int) -> QColor:
    """`colour` with its opacity set to `alpha` (0-255)."""
    faded = QColor(colour)
    faded.setAlpha(alpha)
    return faded
