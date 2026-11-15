"""The Map Painter (Notes/map-painter-plan.md): a dialog to design an
encounter's battle map before (or during) the fight - its size, walls,
Difficult Terrain and water, the ground's height, Dim Light and Darkness,
objects (tables, barrels, pillars, a campfire) and where each combatant
starts. Saved to Combat/Campaigns/<Campaign>/Maps/<encounter id>.json
(Combat/Arena/maps.py); the fight that starts plays on it.

Painting: pick a tool's tab (Ground, Height, Light, Objects, Start), then
left-drag over cells to paint and right-drag to clear what that tab paints;
Shift+drag fills the block between where the drag starts and ends. On the
Start tab, pick a combatant in the list and click the cell it starts on
(the next one not placed is picked for you); click a token to pick it
again, right-click it to take its start away. Ctrl+Z undoes a stroke,
Ctrl+S saves.

Saving the map of the encounter that's open also puts it under the fight:
before the fight, it's the map the fight starts on; during it, one undo
step, and anyone standing where a wall now is moves to the nearest free
cell."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QKeySequence, QMouseEvent, QShortcut
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from Combat import PartyAllies
from Combat.Arena.arena import (
    POSITION_KEY,
    footprint,
    footprint_at,
    nearest_free,
    position,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.maps import MapDesign, map_path, read_map, write_map
from Combat.Arena.terrain import (
    BRIGHT,
    COVERS,
    DARK,
    DIFFICULT,
    DIM,
    GROUNDS,
    LIGHTS,
    MAX_HEIGHT_FT,
    NO_COVER,
    OBJECT_PRESETS,
    OPEN,
    WALL,
    WATER,
    MapObject,
    Terrain,
)
from Combat.Effects.triggers import on_party_side
from Combat.PlayerCombatant import combatant_from_stat_block
from Combat.Summons import owner_name

from .arena_view import CELL_PX, ArenaView, TokenRow, token_label
from .state import CombatWindowState
from .styles import QSS
from .undo import undoable

GROUND_TAB, HEIGHT_TAB, LIGHT_TAB, OBJECT_TAB, START_TAB = range(5)
MIN_CELLS, MAX_CELLS = 4, 100
# How many strokes Ctrl+Z goes back.
UNDO_DEPTH = 200
# A Shift+drag's block, shown as it's dragged.
_PREVIEW = "#f0f0f0"
_TOOLS_WIDTH = 340
_HINT = (
    "Left-drag paints, right-drag clears what this tab paints, Shift+drag"
    " fills a block. Ctrl+wheel zooms, Ctrl+Z undoes, Ctrl+S saves."
)
_START_HINT = (
    "Pick a combatant, then click the cell it starts on. Click a token to"
    " pick it again; right-click it to take its start away. Whoever has no"
    " start is placed as before: the party on the left, the rest on the right."
)
_CUSTOM = "Custom"


class PainterView(ArenaView):
    """The map being painted: an ArenaView whose mouse paints rather than
    moves. A stroke (a drag with a button held) goes to `on_paint(cells,
    erase)` a cell at a time; with Shift, the block from where it started
    to where it's let go, shaded while it's dragged. With `click_only` (the
    Start tab) only the press counts. `on_stroke(started)` is told as a
    stroke starts and ends (the dialog's undo)."""

    def __init__(
        self,
        on_paint: Callable[[list[Cell], bool], None],
        describe: Callable[[Cell], str | None],
        on_stroke: Callable[[bool], None] = lambda started: None,
    ):
        super().__init__(
            lambda name: None, lambda name, ctrl, shift: None, distance_at=describe
        )
        self.setObjectName("mapPainterView")
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._on_paint = on_paint
        self._on_stroke = on_stroke
        self._erasing: bool | None = None  # a stroke going on: whether it clears
        self._stroke: set[Cell] = set()
        self._block: tuple[Cell, Cell] | None = None
        self.click_only = False
        self.set_area_color(_PREVIEW)

    @property
    def stroking(self) -> bool:
        return self._erasing is not None

    def block_shown(self) -> set[Cell]:
        """The block a Shift+drag would fill now (tests)."""
        return set(self._area_cells) if self._block is not None else set()

    def start_stroke(self, cell: Cell, erase: bool = False, block: bool = False):
        """A press on `cell`: paint it (clear it with `erase`), or with
        `block` start a block there."""
        if not self._settings.on_map(cell):
            return
        self._on_stroke(True)
        self._erasing = erase
        self._stroke = set()
        if block and not self.click_only:
            self._block = (cell, cell)
            self._show_block()
        else:
            self.stroke_to(cell)

    def stroke_to(self, cell: Cell):
        """The mouse moved to `cell` with the button held."""
        if self._erasing is None or not self._settings.on_map(cell):
            return
        if self._block is not None:
            if cell != self._block[1]:
                self._block = (self._block[0], cell)
                self._show_block()
            return
        if cell in self._stroke or (self.click_only and self._stroke):
            return
        self._stroke.add(cell)
        self._on_paint([cell], self._erasing)

    def end_stroke(self):
        """The button let go: a block is filled now."""
        if self._erasing is None:
            return
        erase, block = self._erasing, self._block
        self._erasing, self._block, self._stroke = None, None, set()
        if block is not None:
            self._area_cells = set()
            shape = self._settings.distance_rule.shape
            self._on_paint(shape.between(*block), erase)
            self._redraw()
        self._on_stroke(False)

    def _show_block(self):
        assert self._block is not None
        shape = self._settings.distance_rule.shape
        self._area_cells = set(shape.between(*self._block))
        self._redraw()

    def _cell_of(self, event: QMouseEvent) -> tuple[Cell, QPointF]:
        point = self.mapToScene(event.position().toPoint())
        shape = self._settings.distance_rule.shape
        return shape.cell_at(point.x(), point.y(), CELL_PX), point

    def mousePressEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        buttons = (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton)
        if event.button() not in buttons or self.stroking:
            event.accept()
            return
        cell, _ = self._cell_of(event)
        shift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        self.start_stroke(cell, event.button() == Qt.MouseButton.RightButton, shift)
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent | None):
        """A quick second click paints too, as the first did."""
        self.mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        cell, point = self._cell_of(event)
        if self._settings.on_map(cell):
            self.hover(cell, point)
        elif self._hover is not None:
            self._hover = None
            self._redraw()
        self.stroke_to(cell)
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent | None):
        if event is None:
            return
        self.end_stroke()
        event.accept()


def _note(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet("color: #a0a0b0; font-size: 11px;")
    return label


def _radio_group(
    parent: QVBoxLayout, choices: dict[str, str], keys: list[str]
) -> QButtonGroup:
    group = QButtonGroup(parent)
    for index, key in enumerate(keys):
        button = QRadioButton(choices[key])
        button.setObjectName(f"choice_{key}")
        button.setProperty("key", key)
        button.setChecked(index == 0)
        group.addButton(button)
        parent.addWidget(button)
    return group


class MapPainterDialog(QDialog):
    """The painter, on one of `encounters` ((id, title) pairs) at a time,
    `current` first. `load(id)` gives an encounter's map and the combatants
    who can be given a starting cell (combatant dicts, read only);
    `save(id, design)` keeps a map."""

    def __init__(
        self,
        parent: QWidget | None,
        encounters: list[tuple[str, str]],
        current: str,
        load: Callable[[str], tuple[MapDesign, list[dict]]],
        save: Callable[[str, MapDesign], None],
    ):
        super().__init__(parent)
        self.setObjectName("mapPainter")
        self.setStyleSheet(QSS)
        self.resize(1240, 780)
        self._load, self._save = load, save
        self._encounter = current
        self._titles = dict(encounters)
        self._design = MapDesign()
        self._roster: list[dict] = []
        self._saved: dict = {}
        self._undo: list[dict] = []
        self._stroke_from: dict | None = None
        self._build(encounters)
        self._open(current)

    # ---- building ----------------------------------------------------------

    def _build(self, encounters: list[tuple[str, str]]):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.addWidget(QLabel("Encounter"))
        self.encounter_combo = QComboBox()
        self.encounter_combo.setObjectName("painterEncounter")
        for encounter_id, title in encounters:
            self.encounter_combo.addItem(title, encounter_id)
        self.encounter_combo.currentIndexChanged.connect(self._encounter_picked)
        top.addWidget(self.encounter_combo, stretch=1)
        top.addSpacing(16)
        self.width_spin = self._size_spin("painterWidth")
        self.height_spin = self._size_spin("painterHeight")
        top.addWidget(QLabel("Width"))
        top.addWidget(self.width_spin)
        top.addWidget(QLabel("Height"))
        top.addWidget(self.height_spin)
        self.size_label = QLabel()
        self.size_label.setStyleSheet("color: #a0a0b0;")
        top.addWidget(self.size_label)
        layout.addLayout(top)

        body = QHBoxLayout()
        tools = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setObjectName("painterTools")
        self.tabs.setFixedWidth(_TOOLS_WIDTH)
        self.tabs.addTab(self._ground_tab(), "Ground")
        self.tabs.addTab(self._height_tab(), "Height")
        self.tabs.addTab(self._light_tab(), "Light")
        self.tabs.addTab(self._object_tab(), "Objects")
        self.tabs.addTab(self._start_tab(), "Start")
        self.tabs.currentChanged.connect(self._tool_changed)
        tools.addWidget(self.tabs, stretch=1)
        self.hint = _note(_HINT)
        self.hint.setFixedWidth(_TOOLS_WIDTH)
        tools.addWidget(self.hint)
        clear_btn = QPushButton("Clear terrain")
        clear_btn.setToolTip("Make every cell open, level, bright ground again")
        clear_btn.clicked.connect(self.clear_terrain)
        tools.addWidget(clear_btn)
        body.addLayout(tools)
        self.view = PainterView(self._paint, self._describe, self._stroke_changed)
        body.addWidget(self.view, stretch=1)
        layout.addLayout(body, stretch=1)

        bottom = QHBoxLayout()
        self.status = QLabel()
        self.status.setObjectName("painterStatus")
        self.status.setStyleSheet("color: #c9a84c;")
        bottom.addWidget(self.status, stretch=1)
        undo_btn = QPushButton("Undo (Ctrl+Z)")
        undo_btn.clicked.connect(self.undo)
        bottom.addWidget(undo_btn)
        save_btn = QPushButton("Save (Ctrl+S)")
        save_btn.setObjectName("painterSave")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_and_close)
        bottom.addWidget(save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bottom.addWidget(cancel_btn)
        layout.addLayout(bottom)

        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_and_close)

    def _size_spin(self, name: str) -> QSpinBox:
        spin = QSpinBox()
        spin.setObjectName(name)
        spin.setRange(MIN_CELLS, MAX_CELLS)
        spin.setSuffix(" cells")
        spin.valueChanged.connect(self._size_changed)
        return spin

    def _ground_tab(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        self.ground_group = _radio_group(column, GROUNDS, [WALL, DIFFICULT, WATER])
        column.addWidget(
            _note(
                "Nobody enters a wall. Difficult Terrain and water cost 1 extra"
                " foot per foot moved (not on top of a creature's space)."
            )
        )
        column.addStretch()
        return page

    def _height_tab(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        row = QHBoxLayout()
        row.addWidget(QLabel("Ground height"))
        self.height_value = QSpinBox()
        self.height_value.setObjectName("painterHeightValue")
        self.height_value.setRange(-MAX_HEIGHT_FT, MAX_HEIGHT_FT)
        self.height_value.setSingleStep(5)
        self.height_value.setValue(10)
        self.height_value.setSuffix(" ft.")
        row.addWidget(self.height_value)
        column.addLayout(row)
        column.addWidget(
            _note(
                "Higher ground is lighter, lower darker, a pale edge marks a"
                " drop. Height counts into distances, and a step up or down"
                " is a climb: each foot costs 1 extra (none with a Climb Speed)."
            )
        )
        column.addStretch()
        return page

    def _light_tab(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        self.light_group = _radio_group(column, LIGHTS, [DIM, DARK])
        column.addWidget(
            _note(
                "Dim Light is Lightly Obscured (Disadvantage on Perception to"
                " see there); Darkness is Heavily Obscured (Blinded while"
                " trying to see there). The hover and the target label say so."
            )
        )
        column.addStretch()
        return page

    def _object_tab(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        self.preset_combo = QComboBox()
        self.preset_combo.setObjectName("painterPreset")
        for preset in OBJECT_PRESETS:
            self.preset_combo.addItem(preset.name)
        self.preset_combo.addItem(_CUSTOM)
        self.preset_combo.currentIndexChanged.connect(self._preset_picked)
        column.addWidget(self.preset_combo)
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Name"))
        self.object_name = QLineEdit()
        self.object_name.setObjectName("painterObjectName")
        name_row.addWidget(self.object_name)
        column.addLayout(name_row)
        self.object_blocks = QCheckBox("Blocks movement")
        self.object_difficult = QCheckBox("Difficult Terrain")
        self.object_hazard = QCheckBox("Hazard (a reminder on entering)")
        for box in (self.object_blocks, self.object_difficult, self.object_hazard):
            column.addWidget(box)
        cover_row = QHBoxLayout()
        cover_row.addWidget(QLabel("Cover"))
        self.object_cover = QComboBox()
        for key, label in COVERS.items():
            self.object_cover.addItem(label, key)
        cover_row.addWidget(self.object_cover)
        column.addLayout(cover_row)
        column.addWidget(
            _note(
                "Cover is shown on the hover, not counted into attacks. A"
                " hazard reminds the GM when someone enters it or starts a"
                " turn on it."
            )
        )
        column.addStretch()
        self._preset_picked(0)
        return page

    def _start_tab(self) -> QWidget:
        page = QWidget()
        column = QVBoxLayout(page)
        self.start_list = QListWidget()
        self.start_list.setObjectName("painterStarts")
        self.start_list.currentRowChanged.connect(lambda _row: self._refresh())
        column.addWidget(self.start_list, stretch=1)
        clear_btn = QPushButton("Clear all starts")
        clear_btn.clicked.connect(self.clear_starts)
        column.addWidget(clear_btn)
        return page

    # ---- the encounter -----------------------------------------------------

    @property
    def design(self) -> MapDesign:
        return self._design

    @property
    def encounter(self) -> str:
        return self._encounter

    @property
    def dirty(self) -> bool:
        """Whether there's anything not saved."""
        return self._design.cropped().to_dict() != self._saved

    def _open(self, encounter_id: str):
        design, roster = self._load(encounter_id)
        self._encounter = encounter_id
        self._design, self._roster = design, list(roster)
        self._saved = design.cropped().to_dict()
        self._undo = []
        index = self.encounter_combo.findData(encounter_id)
        self.encounter_combo.blockSignals(True)
        self.encounter_combo.setCurrentIndex(max(index, 0))
        self.encounter_combo.blockSignals(False)
        for spin, value in (
            (self.width_spin, design.settings.width),
            (self.height_spin, design.settings.height),
        ):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)
        self._fill_start_list()
        self._pick_next_unplaced()
        self.status.setText("")
        self._refresh()

    def _encounter_picked(self, index: int):
        encounter_id = self.encounter_combo.itemData(index)
        if encounter_id is None or encounter_id == self._encounter:
            return
        if self.dirty and not self._settle_changes():
            self.encounter_combo.blockSignals(True)
            self.encounter_combo.setCurrentIndex(
                self.encounter_combo.findData(self._encounter)
            )
            self.encounter_combo.blockSignals(False)
            return
        self._open(encounter_id)

    def _settle_changes(self) -> bool:
        """Ask what to do with unsaved changes before leaving them: save,
        discard, or (False) stay."""
        answer = QMessageBox.question(
            self,
            "Unsaved map",
            f"Save the changes to the map of {self._titles.get(self._encounter)}?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Save:
            self.save()
            return True
        return answer == QMessageBox.StandardButton.Discard

    def save(self):
        design = self._design.cropped()
        self._save(self._encounter, design)
        self._saved = design.to_dict()
        self._refresh()

    def save_and_close(self):
        self.save()
        self.accept()

    def reject(self):
        """Cancel (or Esc): unsaved changes are asked about first."""
        if self.dirty:
            answer = QMessageBox.question(
                self,
                "Unsaved map",
                "Close the Map Painter without saving the changes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        super().reject()

    # ---- painting ------------------------------------------------------------

    def _size_changed(self, _value: int):
        self._remember()
        settings = self._design.settings
        settings.width = self.width_spin.value()
        settings.height = self.height_spin.value()
        self._refresh()

    def _tool_changed(self, index: int):
        self.view.click_only = index == START_TAB
        self.hint.setText(_START_HINT if index == START_TAB else _HINT)

    def _preset_picked(self, index: int):
        if index >= len(OBJECT_PRESETS):
            return  # Custom: keep what's there to change
        preset = OBJECT_PRESETS[index]
        self.object_name.setText(preset.name)
        self.object_blocks.setChecked(preset.blocks)
        self.object_difficult.setChecked(preset.difficult)
        self.object_hazard.setChecked(preset.hazard)
        self.object_cover.setCurrentIndex(self.object_cover.findData(preset.cover))

    def set_object(self, thing: MapObject):
        """Fill the Objects tab with `thing` (tests, and a preset)."""
        self.preset_combo.setCurrentIndex(self.preset_combo.findText(_CUSTOM))
        self.object_name.setText(thing.name)
        self.object_blocks.setChecked(thing.blocks)
        self.object_difficult.setChecked(thing.difficult)
        self.object_hazard.setChecked(thing.hazard)
        self.object_cover.setCurrentIndex(self.object_cover.findData(thing.cover))

    def current_object(self) -> MapObject:
        return MapObject(
            name=self.object_name.text().strip() or "Object",
            blocks=self.object_blocks.isChecked(),
            difficult=self.object_difficult.isChecked(),
            cover=self.object_cover.currentData() or NO_COVER,
            hazard=self.object_hazard.isChecked(),
        )

    @staticmethod
    def _checked_key(group: QButtonGroup) -> str:
        button = group.checkedButton()
        return button.property("key") if button is not None else ""

    def pick_choice(self, key: str):
        """Check the Ground or Light tab's choice `key` (tests)."""
        for group in (self.ground_group, self.light_group):
            for button in group.buttons():
                if button.property("key") == key:
                    button.setChecked(True)

    def _paint(self, cells: list[Cell], erase: bool):
        """A stroke over `cells` with the tool of the tab shown."""
        tool = self.tabs.currentIndex()
        if tool == START_TAB:
            if cells:
                self._start_click(cells[0], erase)
            return
        terrain = self._design.settings.terrain
        changed = False
        for cell in cells:
            if tool == GROUND_TAB:
                ground = OPEN if erase else self._checked_key(self.ground_group)
                changed |= terrain.change(cell, ground=ground)
            elif tool == HEIGHT_TAB:
                feet = 0 if erase else self.height_value.value()
                changed |= terrain.change(cell, height_ft=feet)
            elif tool == LIGHT_TAB:
                light = BRIGHT if erase else self._checked_key(self.light_group)
                changed |= terrain.change(cell, light=light)
            elif tool == OBJECT_TAB:
                thing = None if erase else self.current_object()
                changed |= terrain.change(cell, thing=thing)
        if changed:
            self._refresh()

    def paint(self, cells: list[Cell], erase: bool = False):
        """One stroke over `cells`, as a drag over them does (tests)."""
        self._stroke_changed(True)
        self._paint(cells, erase)
        self._stroke_changed(False)

    def clear_terrain(self):
        self._remember()
        self._design.settings.terrain = Terrain()
        self._refresh()

    def clear_starts(self):
        self._remember()
        self._design.starts.clear()
        self._refresh()
        self._pick_next_unplaced()

    # ---- undo ------------------------------------------------------------------

    def _stroke_changed(self, started: bool):
        if started:
            self._stroke_from = self._design.to_dict()
            return
        before, self._stroke_from = self._stroke_from, None
        if before is not None and before != self._design.to_dict():
            self._undo.append(before)
            del self._undo[:-UNDO_DEPTH]

    def _remember(self):
        """Keep the map as it is now, for Ctrl+Z (a change not by a stroke)."""
        self._undo.append(self._design.to_dict())
        del self._undo[:-UNDO_DEPTH]

    def undo(self):
        if not self._undo:
            self.status.setText("Nothing to undo.")
            return
        self._design = MapDesign.from_dict(self._undo.pop())
        for spin, value in (
            (self.width_spin, self._design.settings.width),
            (self.height_spin, self._design.settings.height),
        ):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)
        self._refresh()

    # ---- starting cells --------------------------------------------------------

    def _char_named(self, name: str) -> dict:
        return next((c for c in self._roster if c["name"] == name), {"name": name})

    def _start_cells(self, name: str) -> list[Cell]:
        start = self._design.starts.get(name)
        if start is None:
            return []
        rule = self._design.settings.distance_rule
        return footprint_at(self._char_named(name), start, rule)

    def _start_on(self, cell: Cell) -> str | None:
        return next(
            (name for name in self._design.starts if cell in self._start_cells(name)),
            None,
        )

    def picked_start(self) -> str | None:
        item = self.start_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None

    def pick_start(self, name: str):
        for row in range(self.start_list.count()):
            item = self.start_list.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == name:
                self.start_list.setCurrentRow(row)
                self._refresh()
                return

    def _pick_next_unplaced(self):
        for row in range(self.start_list.count()):
            item = self.start_list.item(row)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) not in (
                self._design.starts
            ):
                self.start_list.setCurrentRow(row)
                return

    def _start_click(self, cell: Cell, erase: bool):
        on = self._start_on(cell)
        if erase:
            if on is not None:
                del self._design.starts[on]
                self._refresh()
            return
        if on is not None:
            self.pick_start(on)
            return
        name = self.picked_start()
        if name is None:
            self.status.setText("Pick a combatant in the list first.")
            return
        settings = self._design.settings
        cells = footprint_at(self._char_named(name), cell, settings.distance_rule)
        if not all(settings.standable(c) for c in cells):
            self.status.setText(
                f"{name} can't start there: it's off the map, a wall or an"
                " object that blocks movement."
            )
            return
        taken = {
            c
            for other in self._design.starts
            if other != name
            for c in self._start_cells(other)
        }
        if taken.intersection(cells):
            self.status.setText(f"{name} can't start on someone else's cells.")
            return
        self._design.starts[name] = cell
        self.status.setText("")
        self._pick_next_unplaced()
        self._refresh()

    def _fill_start_list(self):
        self.start_list.blockSignals(True)
        self.start_list.clear()
        names = [c["name"] for c in self._roster]
        names += [n for n in self._design.starts if n not in names]
        for name in names:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            party = on_party_side(self._char_named(name))
            item.setForeground(QBrush(QColor("#7fb2ea" if party else "#e07b84")))
            self.start_list.addItem(item)
        self.start_list.blockSignals(False)

    def _refresh_start_list(self):
        shape = self._design.settings.distance_rule.shape
        known = {c["name"] for c in self._roster}
        for row in range(self.start_list.count()):
            item = self.start_list.item(row)
            if item is None:
                continue
            name = item.data(Qt.ItemDataRole.UserRole)
            start = self._design.starts.get(name)
            where = shape.cell_name(start) if start is not None else "not placed"
            gone = "" if name in known else " (not in this encounter)"
            item.setText(f"{name}  ·  {where}{gone}")

    def start_rows(self) -> list[TokenRow]:
        """The tokens the map shows: each starting cell, the one picked
        white-edged as a source is."""
        settings = self._design.settings
        picked = self.picked_start()
        rows = []
        for name in self._design.starts:
            cells = self._start_cells(name)
            if not cells or not all(settings.on_map(c) for c in cells):
                continue
            rows.append(
                TokenRow(
                    name=name,
                    label=token_label(name),
                    cells=tuple(cells),
                    party=on_party_side(self._char_named(name)),
                    hp_fraction=None,
                    source=name == picked,
                )
            )
        return rows

    # ---- showing ---------------------------------------------------------------

    def _describe(self, cell: Cell) -> str | None:
        """What the hover says: the cell's name, what's painted on it and
        who starts there."""
        settings = self._design.settings
        parts = [settings.distance_rule.shape.cell_name(cell)]
        parts += settings.terrain.describe(cell)
        on = self._start_on(cell)
        if on is not None:
            parts.append(f"{on} starts here")
        return " · ".join(parts)

    def _refresh(self):
        settings = self._design.settings
        self.view.show_rows(settings, self.start_rows())
        self._refresh_start_list()
        feet = settings.cell_ft
        self.size_label.setText(
            f"{settings.width * feet} × {settings.height * feet} ft."
            f" ({feet}-ft. squares)"
        )
        title = self._titles.get(self._encounter, self._encounter)
        self.setWindowTitle(f"Map Painter: {title}" + (" *" if self.dirty else ""))


class MapPainterMixin(CombatWindowState):
    """The window's side of the Map Painter: which encounters it paints, an
    encounter's map read and saved, and a saved map put under the fight of
    the encounter that's open."""

    def _encounter_map(self, encounter_id: str | None) -> MapDesign | None:
        """The map painted for `encounter_id`, if any."""
        if not encounter_id:
            return None
        return read_map(map_path(self._combat_log_dir, encounter_id))

    def _show_map_painter(self):
        """Open the Map Painter (Ctrl+M) on the encounter that's open, or the
        campaign's first."""
        if not self._scenarios:
            self._show_status("There are no encounters to paint a map for.")
            return
        encounters = [(s.name, s.display_title) for s in self._scenarios]
        ids = [encounter_id for encounter_id, _ in encounters]
        current = self._scenario_name if self._scenario_name in ids else ids[0]
        dialog = MapPainterDialog(
            self._window,
            encounters,
            current,
            self._painter_load,
            self._save_painted_map,
        )
        self._map_painter = dialog  # tests
        dialog.exec()

    def _painter_load(self, encounter_id: str) -> tuple[MapDesign, list[dict]]:
        """An encounter's map (an empty one when none is painted yet) and
        who can start on it."""
        design = self._encounter_map(encounter_id) or MapDesign()
        return design, self._painter_roster(encounter_id)

    def _painter_roster(self, encounter_id: str) -> list[dict]:
        """Who takes part in the encounter, as combatant dicts read only for
        their names, sides and sizes: the window's own for the encounter
        that's open (summons left out), else built from its config."""
        if encounter_id == self._scenario_name and self.phase != "PARTY":
            return [c for c in self.characters if owner_name(c) is None]
        scenario = self._scenario(encounter_id)
        if scenario is None:
            return []
        roster: list[dict] = []
        try:
            members = scenario.members_taking_part(self._party_names)
        except KeyError:
            members = []
        for name in members:
            known = next((c for c in self.characters if c["name"] == name), None)
            roster.append(known or {"name": name, "_is_player": True})
        taking_part = set(scenario.party_allies_taking_part())
        for spec in scenario.party_allies:
            for combatant in spec.build():
                char = combatant_from_stat_block(combatant)
                if char["name"] in taking_part:
                    char[PartyAllies.PARTY_ALLY_KEY] = True
                    roster.append(char)
        for combatant in scenario.allies():
            char = combatant_from_stat_block(combatant)
            char[PartyAllies.ENCOUNTER_ALLY_KEY] = True
            roster.append(char)
        roster += [combatant_from_stat_block(c) for c in scenario.combatants()]
        return roster

    def _save_painted_map(self, encounter_id: str, design: MapDesign):
        """Keep the map painted for `encounter_id`; for the encounter that's
        open, the fight plays on it from now on."""
        write_map(map_path(self._combat_log_dir, encounter_id), design)
        self._show_status(f"Saved the map of {self._scenario_title(encounter_id)}.")
        if encounter_id == self._scenario_name and self.phase in (
            "INITIATIVE",
            "COMBAT",
        ):
            self._use_painted_map(design)

    @undoable
    def _use_painted_map(self, design: MapDesign):
        """Put the fight on `design`'s map (one undo step during combat).
        Anyone now off its edge or on a wall or blocking object moves to the
        nearest free cell (off the map when there's none), and a GM-only
        line says the map changed."""
        settings = design.settings.copy()
        self.arena_settings = settings
        if self.phase != "COMBAT":
            return
        rule = settings.distance_rule
        moved = []
        for char in self.characters:
            if position(char) is None:
                continue
            cells = footprint(char, rule)
            if all(settings.standable(cell) for cell in cells):
                continue
            near = [cell for cell in cells if settings.on_map(cell)] or [
                cell
                for cell in rule.shape.cells(settings.width, settings.height)
                if settings.standable(cell)
            ][:1]
            anchor = nearest_free(char, near, self.characters, settings)
            if anchor is None:
                del char[POSITION_KEY]
            else:
                char[POSITION_KEY] = anchor.to_list()
            moved.append(char["name"])
        line = "The battle map changes (Map Painter)."
        if moved:
            line += f" Moved to make room: {', '.join(moved)}."
        self._log_event(line, public=False)
        self._refresh_views()
