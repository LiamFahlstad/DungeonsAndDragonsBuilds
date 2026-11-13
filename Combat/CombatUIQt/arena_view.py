"""The battle map's view (Notes/combat-arena-plan.md, steps 4-5): a grid
with a token for every combatant on the map. It draws token rows, never a
combatant dict (the plan's Decision 6), and has no rules in it: the cells
come from Combat/Arena's grid shape, the rows from token_rows.

Left click a token: the source. Right click: the target (Ctrl adds one,
Shift a range), as on the cards. Ctrl+wheel zooms; dragging empty space
pans."""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Callable

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
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
    `on_select(name)` and `on_target(name, ctrl, shift)`."""

    def __init__(
        self,
        on_select: Callable[[str], None],
        on_target: Callable[[str, bool, bool], None],
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
        self._settings = ArenaSettings()
        self._rows: list[TokenRow] = []
        self._drawn: tuple | None = None
        # The whole map fits the view until the GM zooms (Ctrl+wheel).
        self._zoomed = False

    @property
    def rows(self) -> list[TokenRow]:
        return list(self._rows)

    def show_rows(self, settings: ArenaSettings, rows: list[TokenRow]):
        """Draw the map of `settings` with `rows`; nothing when nothing
        changed since the last time."""
        key = (settings.to_dict().items(), tuple(rows))
        if key == self._drawn:
            return
        self._drawn = key
        self._settings, self._rows = settings, list(rows)
        self._scene.clear()
        self._draw_grid()
        for row in rows:
            self._draw_token(row)
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
            if first_row:
                self._coord(str(cell.col + 1), x, y - CELL_PX, font)
            if first_col:
                self._coord(str(cell.row + 1), x - CELL_PX, y, font)

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

    def mousePressEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        point = self.mapToScene(event.position().toPoint())
        row = self.token_at(point.x(), point.y())
        if row is not None and event.button() in (
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.RightButton,
        ):
            self.click(row, event.button(), event.modifiers())
            event.accept()
            return
        super().mousePressEvent(event)

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
