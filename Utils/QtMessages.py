"""Qt's own console messages (style sheet and font warnings and the like),
each printed once instead of every time Qt repeats it.

Qt repeats a warning for every widget it hits: an unknown style sheet
property is reported once per widget that uses it, on every card rebuild.
Printing each distinct message once, marked as Qt's, keeps the terminal
readable and still shows anything new worth fixing.
"""

import sys

from PyQt6.QtCore import QMessageLogContext, QtMsgType, qInstallMessageHandler

_LABELS = {
    QtMsgType.QtDebugMsg: "debug",
    QtMsgType.QtInfoMsg: "info",
    QtMsgType.QtWarningMsg: "warning",
    QtMsgType.QtCriticalMsg: "critical",
    QtMsgType.QtFatalMsg: "fatal",
}

_seen: set[str] = set()


def _handle(
    mode: QtMsgType, context: QMessageLogContext | None, message: str | None
) -> None:
    if not message or message in _seen:
        return
    _seen.add(message)
    print(
        f"Qt {_LABELS.get(mode, 'message')}: {message} (shown once)",
        file=sys.stderr,
    )


def install_qt_message_handler() -> None:
    """Route Qt's console messages through _handle. Safe to call again."""
    qInstallMessageHandler(_handle)
