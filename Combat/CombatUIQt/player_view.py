"""The players' screen (a second monitor or a TV): the turn order, whose turn
it is and who's next, so players plan during other turns. player_view_rows
decides what they may see: a monster's health is only a word, and a monster
they can't perceive isn't listed."""

from collections import Counter
from dataclasses import dataclass
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QGuiApplication, QKeyEvent
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from Core.Definitions import Condition
from .turns_mixin import initiative_units, unit_label

# A monster with one of these (a condition, a Visibility, or the spell's badge)
# isn't shown to the players.
HIDDEN_STATES = {
    "Darkness",
    "Greater Invisibility",
    "Heavily Obscured",
    "Hidden",
    "Invisibility",
    "Invisible",
    "Total Cover",
}
# All the players see of a monster's conditions: the rules' own, which show on
# the table. Spell badges and a GM's custom conditions are private notes.
SHOWN_MONSTER_CONDITIONS = {c.value for c in Condition} - HIDDEN_STATES

_STYLE = """
QWidget#playerView { background-color: #1a1a2e; }
QLabel { color: #eaeaea; font-size: 26px; background: transparent; }
QLabel#playerViewRound { color: #c9a84c; font-size: 34px; font-weight: bold; }
QFrame#playerViewRow { border-radius: 6px; }
QFrame#playerViewRow[turn="now"] { background-color: #3a2e00; }
QFrame#playerViewRow[turn="next"] { background-color: #0f3460; }
QLabel#playerViewMark { color: #c9a84c; font-weight: bold; }
QLabel#playerViewConditions { color: #a0c4ff; font-size: 22px; }
"""


@dataclass(frozen=True)
class PlayerViewRow:
    name: str
    health: str
    conditions: tuple[str, ...]
    turn: str  # "now", "next" or ""


def _player_health(char: dict, death_state: str) -> str:
    if death_state == "dead":
        return "Dead"
    if death_state == "stabilized":
        return "Stable"
    if death_state == "dying":
        fails, saves = char.get("death_saves_fail", 0), char.get(
            "death_saves_success", 0
        )
        return f"Dying ({fails} failed, {saves} saved)"
    temp = char.get("temp_hp", 0)
    return f"{char['hp']} / {char['max_hp']}" + (f" (+{temp})" if temp else "")


def _monster_health(char: dict, death_state: str) -> str:
    if death_state == "dead":
        return "Defeated"
    if char["hp"] <= 0:
        return "Down"
    return "Bloodied" if char["hp"] <= char["max_hp"] / 2 else "Healthy"


def _can_be_seen(char: dict) -> bool:
    states = set(char.get("conditions", [])) | set(char.get("visibility_states", []))
    return bool(char.get("_is_player")) or not states & HIDDEN_STATES


def _unit_health(unit: list[dict], death_state: Callable[[dict], str]) -> str:
    """One combatant's health, or a group's count of each."""
    if unit[0].get("_is_player"):
        return _player_health(unit[0], death_state(unit[0]))
    words = Counter(_monster_health(c, death_state(c)) for c in unit)
    if len(unit) == 1:
        return next(iter(words))
    return ", ".join(f"{count} {word}" for word, count in words.items())


def _unit_conditions(unit: list[dict]) -> tuple[str, ...]:
    names: dict[str, None] = {}
    for char in unit:
        for cond in char.get("conditions", []):
            if char.get("_is_player") or cond in SHOWN_MONSTER_CONDITIONS:
                names[cond] = None
    return tuple(names)


def player_view_rows(
    order: list[dict],
    now: list[dict],
    upcoming: list[list[dict]],
    death_state: Callable[[dict], str],
) -> list[PlayerViewRow]:
    """A row for each turn in `order` that the players can see. `now` is the
    current turn and `upcoming` the turns after it; "next" goes on the first
    of those they can see, so a hidden monster's place doesn't give it away.
    On that monster's own turn, "now" stays where it was, for the same reason."""
    next_unit = next(
        (unit for unit in upcoming if any(_can_be_seen(c) for c in unit)), []
    )
    units = initiative_units(order)
    now_index = next(
        (i for i, unit in enumerate(units) if any(c is n for c in unit for n in now)),
        0,
    )
    shown_now = next(
        (
            units[(now_index - back) % len(units)]
            for back in range(len(units))
            if any(_can_be_seen(c) for c in units[(now_index - back) % len(units)])
        ),
        [],
    )
    rows = []
    for unit in units:
        shown = [c for c in unit if _can_be_seen(c)]
        if not shown:
            continue
        turn = ""
        if unit is shown_now:
            turn = "now"
        elif any(c is n for c in unit for n in next_unit):
            turn = "next"
        rows.append(
            PlayerViewRow(
                unit_label(shown),
                _unit_health(shown, death_state),
                _unit_conditions(shown),
                turn,
            )
        )
    return rows


class PlayerViewWindow(QWidget):
    """Shows the rows it's given. It reads nothing itself, so all it can ever
    show the players is what player_view_rows let through."""

    def __init__(self, on_close: Callable[[], None]):
        super().__init__()
        self._on_close = on_close
        self.setObjectName("playerView")
        # It goes when the main window does, instead of keeping the app open.
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setWindowTitle("Players")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(_STYLE)
        self.resize(900, 700)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self._title = QLabel("")
        self._title.setObjectName("playerViewRound")
        layout.addWidget(self._title)
        self._rows_box = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_box)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(6)
        layout.addWidget(self._rows_box)
        layout.addStretch()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self._on_close()
        super().closeEvent(a0)

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        # Full screen on a TV, it has no X to click.
        if a0 is not None and a0.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(a0)

    def show_rows(self, title: str, rows: list[PlayerViewRow]):
        self._title.setText(title)
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        for row in rows:
            self._rows_layout.addWidget(self._row_widget(row))

    @staticmethod
    def _row_widget(row: PlayerViewRow) -> QFrame:
        frame = QFrame()
        frame.setObjectName("playerViewRow")
        frame.setProperty("turn", row.turn)
        grid = QGridLayout(frame)
        grid.setContentsMargins(12, 6, 12, 6)
        grid.setColumnStretch(1, 1)
        mark = QLabel({"now": "NOW", "next": "NEXT"}.get(row.turn, ""))
        mark.setObjectName("playerViewMark")
        mark.setFixedWidth(100)
        grid.addWidget(mark, 0, 0)
        grid.addWidget(QLabel(row.name), 0, 1)
        grid.addWidget(QLabel(row.health), 0, 2)
        if row.conditions:
            conditions = QLabel(", ".join(row.conditions))
            conditions.setObjectName("playerViewConditions")
            conditions.setWordWrap(True)
            grid.addWidget(conditions, 1, 1, 1, 2)
        return frame

    def show_on_spare_screen(self, main_window: QWidget):
        """Fill a screen the main window isn't on, or else open as a window."""
        main_screen = main_window.screen()
        spare = [s for s in QGuiApplication.screens() if s is not main_screen]
        if not spare:
            self.show()
            return
        self.setGeometry(spare[0].geometry())
        self.showFullScreen()
