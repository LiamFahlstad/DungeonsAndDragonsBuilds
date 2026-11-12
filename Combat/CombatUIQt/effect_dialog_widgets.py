"""Building blocks of the Custom Effect dialog (ConditionsMixin.
_show_custom_condition_dialog): one-click chips that stand in for a combo box,
framed sections, the row per target for a roll made at the table, and moving
through the picker from the search box."""

from typing import Any, Callable, Hashable, Iterable, Mapping, Sequence

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# How far down the rows for rolls made at the table go before they scroll:
# about four targets.
TYPED_ROWS_MAX_HEIGHT = 140
_TARGET_NAME_WIDTH = 150
# The least an extra roll's box gets, beside its label.
_EXTRA_BOX_WIDTH = 110


def row_widget(object_name: str = "") -> tuple[QWidget, QHBoxLayout]:
    """A widget holding a row of a section's widgets, with no background of
    its own (styles.py: [effectRow="true"])."""
    row = QWidget()
    row.setProperty("effectRow", True)
    if object_name:
        row.setObjectName(object_name)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    return row, layout


def chip(text: str, tooltip: str = "") -> QPushButton:
    """A checkable button of a chip row (styles.py: [segment="true"])."""
    button = QPushButton(text)
    button.setCheckable(True)
    button.setAutoDefault(False)
    button.setProperty("segment", True)
    button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
    if tooltip:
        button.setToolTip(tooltip)
    return button


def chip_row(
    combo: QComboBox,
    choices: Iterable[tuple[int, str, str]],
    object_name: str,
) -> QWidget:
    """A row of chips for some of combo's entries, as (combo index, text,
    tooltip). The combo stays the value, hidden: a click sets it, and setting
    it checks its chip (none, for an entry without one). Disabling the combo
    disables the row too."""
    row, layout = row_widget(object_name)
    layout.setSpacing(3)
    buttons: dict[int, QPushButton] = {}
    for index, text, tooltip in choices:
        button = chip(text, tooltip)
        button.clicked.connect(lambda _=False, i=index: _choose(combo, i, buttons))
        layout.addWidget(button, stretch=1)
        buttons[index] = button

    def show_choice():
        for index, button in buttons.items():
            button.setChecked(index == combo.currentIndex())

    combo.currentIndexChanged.connect(show_choice)
    combo.installEventFilter(_EnabledFollower(row, combo))
    combo.hide()
    show_choice()
    return row


def _choose(combo: QComboBox, index: int, buttons: dict[int, QPushButton]):
    combo.setCurrentIndex(index)
    # Clicking the chip already checked would uncheck it otherwise.
    buttons[index].setChecked(True)


class _EnabledFollower(QObject):
    """Keeps a chip row as enabled as the hidden combo box it stands in for."""

    def __init__(self, row: QWidget, combo: QComboBox):
        super().__init__(row)
        self._row = row
        row.setEnabled(combo.isEnabled())

    def eventFilter(self, a0, a1):  # noqa: N802 (Qt's names)
        if a1 is not None and a1.type() == QEvent.Type.EnabledChange:
            self._row.setEnabled(isinstance(a0, QWidget) and a0.isEnabled())
        return False


def section(title: str) -> tuple[QFrame, QVBoxLayout, QLabel]:
    """A framed part of the form with its title: (frame, layout, title)."""
    frame = QFrame()
    frame.setObjectName("effectSection")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(10, 8, 10, 10)
    layout.setSpacing(6)
    header = QLabel(title)
    header.setObjectName("effectSectionTitle")
    layout.addWidget(header)
    return frame, layout, header


def target_roll_rows(
    chars: list[dict],
    object_name: str,
    tooltip: str,
    extras: Mapping[int, Sequence[tuple[Hashable, str, str]]] | None = None,
    checks: Mapping[int, tuple[str, str, bool]] | None = None,
) -> tuple[
    QScrollArea,
    dict[int, QLineEdit],
    dict[int, QLabel],
    dict[Any, tuple[QLabel, QLineEdit]],
    dict[int, QCheckBox],
]:
    """A row for each of chars: its name, what it rolls against or with (an
    "AC 15" or "DEX +3" the caller keeps up to date), and a box for what was
    rolled at the table. `extras`, by id(char): a row under its own for each
    other roll that comes with it (key, what it is, tooltip), a hit's extra
    damage, with a box named "typedExtra" (plan principle 13). `checks`, by
    id(char): a checkbox at the end of its row (text, tooltip, checked), a
    Shield it wields or not. Returns (the rows, scrolling past about four, so
    the dialog still fits the smallest window), their boxes and their middle
    labels, by id(char), each extra row's label and box, by key, and the
    checkboxes, by id(char)."""
    extras = extras or {}
    checks = checks or {}
    rows = QWidget()
    grid = QGridLayout(rows)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(8)
    grid.setVerticalSpacing(4)
    grid.setColumnStretch(2, 1)
    inputs: dict[int, QLineEdit] = {}
    infos: dict[int, QLabel] = {}
    extra_rows: dict[Any, tuple[QLabel, QLineEdit]] = {}
    check_boxes: dict[int, QCheckBox] = {}
    line = 0
    for char in chars:
        name = QLabel(char["name"])
        name.setObjectName("targetRowName")
        name.setToolTip(char["name"])
        name.setFixedWidth(_TARGET_NAME_WIDTH)
        name.ensurePolished()  # the stylesheet's font, to measure with
        metrics = name.fontMetrics()
        name.setText(
            metrics.elidedText(
                char["name"], Qt.TextElideMode.ElideRight, _TARGET_NAME_WIDTH
            )
        )
        info = QLabel("")
        info.setObjectName("targetRowInfo")
        box = QLineEdit()
        box.setObjectName(object_name)
        box.setPlaceholderText("Total, or blank to roll")
        box.setAccessibleName(char["name"])
        box.setToolTip(tooltip)
        grid.addWidget(name, line, 0)
        grid.addWidget(info, line, 1)
        grid.addWidget(box, line, 2)
        inputs[id(char)] = box
        infos[id(char)] = info
        line += 1
        if id(char) in checks:
            # A line of its own, under the name, so the row's box keeps its
            # width.
            text, hint, checked = checks[id(char)]
            check = QCheckBox(text)
            check.setObjectName("targetRowCheck")
            check.setAccessibleName(f"{char['name']}: {text}")
            check.setToolTip(hint)
            check.setChecked(checked)
            grid.addWidget(check, line, 0, 1, 3)
            check_boxes[id(char)] = check
            line += 1
        for key, what, hint in extras.get(id(char), ()):
            label = QLabel(what)
            label.setObjectName("extraRowInfo")
            label.setWordWrap(True)  # a long one wraps rather than crowd the box
            extra = QLineEdit()
            extra.setObjectName("typedExtra")
            extra.setMinimumWidth(_EXTRA_BOX_WIDTH)
            extra.setPlaceholderText("Rolled, or blank to roll")
            extra.setAccessibleName(f"{char['name']}: {what}")
            extra.setToolTip(hint)
            grid.addWidget(label, line, 0, 1, 2, Qt.AlignmentFlag.AlignRight)
            grid.addWidget(extra, line, 2)
            extra_rows[key] = (label, extra)
            line += 1
    scroll = QScrollArea()
    scroll.setObjectName("targetRolls")
    scroll.setWidget(rows)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setFixedHeight(min(rows.sizeHint().height(), TYPED_ROWS_MAX_HEIGHT))
    return scroll, inputs, infos, extra_rows, check_boxes


def pickable_rows(tree: QTreeWidget) -> list[QTreeWidgetItem]:
    """The picker's rows that can be picked as it shows them now: not a
    category, not filtered out, not in a folded category, not greyed out."""
    rows = []
    for i in range(tree.topLevelItemCount()):
        category = tree.topLevelItem(i)
        if category is None or category.isHidden() or not category.isExpanded():
            continue
        for j in range(category.childCount()):
            row = category.child(j)
            if row is not None and not row.isHidden() and not row.isDisabled():
                rows.append(row)
    return rows


def step_through(tree: QTreeWidget, steps: int) -> QTreeWidgetItem | None:
    """Make the row `steps` on from the current one current (from before the
    first, with none), stopping at either end. Returns it, or None with no
    row to go to."""
    rows = pickable_rows(tree)
    if not rows:
        return None
    current = tree.currentItem()
    at = next((i for i, row in enumerate(rows) if row is current), None)
    if at is None:
        at = 0 if steps > 0 else len(rows) - 1
    else:
        at = max(0, min(len(rows) - 1, at + steps))
    tree.setCurrentItem(rows[at])
    tree.scrollToItem(rows[at])
    return rows[at]


class SearchKeys(QObject):
    """The picker's keys: from the search box, Up and Down (and Page Up and
    Page Down) move through the rows and Escape empties a search before it
    closes the dialog; typing in the list types in the search box."""

    _PAGE = 8

    def __init__(
        self,
        search_box: QLineEdit,
        tree: QTreeWidget,
        on_step: Callable[[], None] = lambda: None,
    ):
        super().__init__(search_box)
        self._search = search_box
        self._tree = tree
        self._on_step = on_step
        search_box.installEventFilter(self)
        tree.installEventFilter(self)

    def eventFilter(self, a0, a1):  # noqa: N802 (Qt's names)
        watched, event = a0, a1
        if not isinstance(event, QKeyEvent) or event.type() != QEvent.Type.KeyPress:
            return False
        key = event.key()
        if watched is self._search:
            steps = {
                Qt.Key.Key_Down.value: 1,
                Qt.Key.Key_Up.value: -1,
                Qt.Key.Key_PageDown.value: self._PAGE,
                Qt.Key.Key_PageUp.value: -self._PAGE,
            }.get(key)
            if steps is not None:
                if step_through(self._tree, steps) is not None:
                    self._on_step()
                return True
            if key == Qt.Key.Key_Escape.value and self._search.text():
                self._search.clear()
                return True
            return False
        # The list: a letter goes to the search box, as if typed there.
        text = event.text()
        # Shift is a capital letter; Ctrl, Alt and Meta are shortcuts.
        held = event.modifiers() & (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        )
        if text and text.isprintable() and not text.isspace() and not held:
            self._search.setFocus()
            self._search.insert(text)
            return True
        return False
