"""Helpers for driving the PyQt6 combat UI headlessly in tests: an offscreen
QApplication, a CombatAppQt with its window built (but never shown or run),
a way to open its modal dialogs without blocking, and a plain-data dump of a
widget tree for golden snapshots (tests/snapshots/combat_ui_*.json)."""

import hashlib
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt  # noqa: E402
from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QBoxLayout,
    QDialog,
    QFrame,
    QLabel,
    QLayout,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QWidget,
)

import pytest  # noqa: E402

from Combat.CombatUIQt import CombatAppQt  # noqa: E402
from tests._snapshot_helpers import UPDATE_SNAPSHOTS, load, save  # noqa: E402

_app: QApplication | None = None


def qapp() -> QApplication:
    """The process-wide QApplication. Held in a module global: if it's
    garbage-collected, Qt aborts the whole process at the next widget."""
    global _app
    if _app is None:
        existing = QApplication.instance()
        assert existing is None or isinstance(existing, QApplication)
        _app = existing or QApplication([])
    return _app


def make_ui(tmp_path, combatants=(), character_sheets=()) -> CombatAppQt:
    """A CombatAppQt fighting `combatants` (with `character_sheets` as the
    party) and logging to tmp_path/logs/fight.json, with its window built."""
    qapp()
    ui = CombatAppQt(
        list(combatants),
        list(character_sheets),
        combat_log_dir=tmp_path / "logs",
        log_path=tmp_path / "logs" / "fight.json",
    )
    ui._build_window()
    return ui


def open_dialog(monkeypatch, show) -> QDialog:
    """Call `show()` (e.g. ui._show_more_info) and return the dialog it
    exec()s, without blocking on the modal event loop."""
    opened: list[QDialog] = []

    def fake_exec(self):
        opened.append(self)
        return 0

    monkeypatch.setattr(QDialog, "exec", fake_exec)
    show()
    assert len(opened) == 1, opened
    return opened[0]


# ---------------------------------------------------------------------------
# Widget-tree dumps

_QT_MAX_SIZE = 16777215
# Long texts (feature/spell descriptions) are pinned by hash so the goldens
# stay reviewable; the prefix keeps a diff readable.
_LONG_TEXT = 160


def _text(value: str) -> str:
    if len(value) <= _LONG_TEXT:
        return value
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return f"{value[:60]}... [{len(value)} chars, sha1 {digest}]"


def _enum_name(value) -> str:
    return getattr(value, "name", str(value))


def dump_widget(widget: QWidget) -> dict:
    """Everything a refactor of a widget builder could change, in layout
    order: type, text, styles, sizes, flags, and the nested layout."""
    out: dict = {"type": type(widget).__name__}
    if widget.objectName():
        out["object_name"] = widget.objectName()
    if isinstance(widget, QDialog):
        out["title"] = widget.windowTitle()
        out["min_size"] = [widget.minimumWidth(), widget.minimumHeight()]
        out["size"] = [widget.width(), widget.height()]
    if isinstance(widget, (QLabel, QPushButton)):
        out["text"] = _text(widget.text())
    if isinstance(widget, QLabel):
        if widget.textFormat() != Qt.TextFormat.AutoText:
            out["text_format"] = _enum_name(widget.textFormat())
        if widget.wordWrap():
            out["word_wrap"] = True
    if isinstance(widget, QPushButton):
        if widget.isFlat():
            out["flat"] = True
        if widget.isCheckable():
            out["checkable"] = True
            out["checked"] = widget.isChecked()
    if isinstance(widget, QProgressBar):
        out["bar"] = [
            widget.minimum(),
            widget.maximum(),
            widget.value(),
            widget.format(),
            widget.isTextVisible(),
        ]
    if type(widget) in (QFrame, QScrollArea) or isinstance(widget, QLabel):
        if widget.frameShape() != QFrame.Shape.NoFrame:  # type: ignore[union-attr]
            out["frame_shape"] = _enum_name(widget.frameShape())  # type: ignore[union-attr]
    margins = widget.contentsMargins()
    if isinstance(widget, QLabel) and any(
        (margins.left(), margins.top(), margins.right(), margins.bottom())
    ):
        out["margins"] = [
            margins.left(),
            margins.top(),
            margins.right(),
            margins.bottom(),
        ]
    if widget.styleSheet():
        out["style"] = widget.styleSheet()
    if widget.toolTip():
        out["tooltip"] = _text(widget.toolTip())
    if widget.isHidden() and not isinstance(widget, QDialog):
        out["hidden"] = True
    if widget.minimumWidth() == widget.maximumWidth():
        out["fixed_width"] = widget.minimumWidth()
    if widget.minimumHeight() == widget.maximumHeight():
        out["fixed_height"] = widget.minimumHeight()
    policy = widget.sizePolicy()
    if (policy.horizontalPolicy(), policy.verticalPolicy()) != (
        QSizePolicy.Policy.Preferred,
        QSizePolicy.Policy.Preferred,
    ) and not isinstance(widget, (QPushButton, QProgressBar, QScrollArea)):
        out["size_policy"] = [
            _enum_name(policy.horizontalPolicy()),
            _enum_name(policy.verticalPolicy()),
        ]
    if widget.cursor().shape() != Qt.CursorShape.ArrowCursor:
        out["cursor"] = _enum_name(widget.cursor().shape())
    if widget.contextMenuPolicy() != Qt.ContextMenuPolicy.DefaultContextMenu:
        out["context_menu"] = _enum_name(widget.contextMenuPolicy())
    if widget.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents):
        out["mouse_transparent"] = True
    # The UI's own dynamic properties (e.g. a card's "dead"/"selected" flags
    # its stylesheet keys on); Qt's internal "_q_*" ones are skipped.
    names = [name.data().decode() for name in widget.dynamicPropertyNames()]
    properties = {
        name: widget.property(name) for name in names if not name.startswith("_q_")
    }
    if properties:
        out["properties"] = properties
    if isinstance(widget, QScrollArea):
        out["resizable"] = widget.widgetResizable()
        inner = widget.widget()
        if inner is not None:
            out["scroll_widget"] = dump_widget(inner)
    layout = widget.layout()
    if layout is not None:
        out["layout"] = dump_layout(layout)
    return out


def dump_layout(layout: QLayout) -> dict:
    margins = layout.contentsMargins()
    out: dict = {
        "type": type(layout).__name__,
        "margins": [margins.left(), margins.top(), margins.right(), margins.bottom()],
        "spacing": layout.spacing(),
    }
    if layout.alignment():
        out["alignment"] = int(layout.alignment().value)
    items = []
    for i in range(layout.count()):
        item = layout.itemAt(i)
        assert item is not None
        child_widget = item.widget()
        child_layout = item.layout()
        entry: dict
        if child_widget is not None:
            entry = dump_widget(child_widget)
        elif child_layout is not None:
            entry = dump_layout(child_layout)
        else:
            entry = {"type": "spacer"}
        if isinstance(layout, QBoxLayout) and layout.stretch(i):
            entry["stretch"] = layout.stretch(i)
        items.append(entry)
    out["items"] = items
    return out


def check_golden(path, key: str, actual) -> None:
    """Compare `actual` with the golden stored under `key` in `path`; with
    UPDATE_SNAPSHOTS=1, rewrite that entry instead."""
    # Round-trip so tuples and int keys compare like the golden.
    actual = json.loads(json.dumps(actual))
    if UPDATE_SNAPSHOTS:
        golden = load(path)
        golden[key] = actual
        save(path, golden)
        pytest.skip("UPDATE_SNAPSHOTS=1: golden rewritten")
    golden = load(path)
    assert key in golden, f"No golden {key!r} in {path.name}."
    assert actual == golden[key]
