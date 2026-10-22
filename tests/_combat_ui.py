"""Helpers for driving the PyQt6 combat UI headlessly in tests: an offscreen
QApplication, a CombatAppQt with its window built (but never shown or run),
and a way to open its modal dialogs without blocking."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QDialog  # noqa: E402

from Combat.CombatUIQt import CombatAppQt  # noqa: E402

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
    """A CombatAppQt whose log goes under tmp_path, with its window built."""
    qapp()
    ui = CombatAppQt(
        list(combatants), list(character_sheets), combat_log_dir=tmp_path / "logs"
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
