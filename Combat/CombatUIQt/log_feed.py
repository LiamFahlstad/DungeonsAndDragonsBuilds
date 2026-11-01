"""The encounter log in the turn column: always open, with the newest line at
the bottom. It shows the whole log, lines the player link hides included, and
stays where the GM scrolled to until they scroll back down to the end."""

import re
from html import escape

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit

from Combat.EncounterLogs import event_text
from Combat.PlayerLog import is_round_key

_MINIMUM_HEIGHT = 120
_TURN_PREFIX = re.compile(r"\[(.+?)'s turn\] (.*)", re.DOTALL)
_ROUND_STYLE = "color: #c9a84c; font-weight: bold; margin: 8px 0 0 0;"
_TURN_STYLE = "color: #5ac8f5; font-weight: bold; margin: 5px 0 0 0;"
_LINE_STYLE = "margin: 1px 0 0 8px;"


def _paragraph(style: str, text: str) -> str:
    return f'<p style="{style}">{escape(text)}</p>'


def log_feed_html(data: dict) -> str:
    """The rounds of the encounter log `data`, oldest first. A heading per turn
    replaces the "[Goblin's turn]" every line starts with, which would take up
    the column's width, and one per round the round's own "--- Round 2 ---"."""
    parts = []
    for number in sorted(int(k.split("_", 1)[1]) for k in filter(is_round_key, data)):
        parts.append(_paragraph(_ROUND_STYLE, f"Round {number}"))
        turn = None
        for event in data[f"round_{number}"]:
            text = event_text(event)
            if text == f"--- Round {number} ---":
                continue
            found = _TURN_PREFIX.fullmatch(text)
            if found:
                if found[1] != turn:
                    turn = found[1]
                    parts.append(_paragraph(_TURN_STYLE, turn))
                text = found[2]
            parts.append(_paragraph(_LINE_STYLE, text))
    return "".join(parts)


class LogFeed(QTextEdit):
    """It never takes the keyboard focus, so scrolling it or clicking in it
    leaves Enter and the Damage field where they were."""

    def __init__(self):
        super().__init__()
        self.setObjectName("logFeed")
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setPlaceholderText("Nothing has happened yet.")
        self.setMinimumHeight(_MINIMUM_HEIGHT)
        self._html: str | None = None
        self._follows_end = True
        self._replacing = False
        bar = self.verticalScrollBar()
        assert bar is not None
        self._bar = bar
        bar.valueChanged.connect(self._scrolled)
        bar.rangeChanged.connect(self._range_changed)

    def show_log(self, data: dict):
        """Show the encounter log `data`, if that isn't what's showing."""
        html = log_feed_html(data)
        if html == self._html:
            return
        self._html = html
        position = self._bar.value()
        # Replacing the text empties it first, which isn't the GM scrolling.
        self._replacing = True
        self.setHtml(html)
        self._replacing = False
        # A log too short to scroll has nothing to have scrolled back from.
        self._follows_end = self._follows_end or self._bar.maximum() == 0
        self._bar.setValue(self._bar.maximum() if self._follows_end else position)

    def _scrolled(self, value: int):
        if not self._replacing:
            self._follows_end = value >= self._bar.maximum()

    def _range_changed(self, _minimum: int, maximum: int):
        if self._follows_end and not self._replacing:
            self._bar.setValue(maximum)
