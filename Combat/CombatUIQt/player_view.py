"""The players' screen (a second monitor or a TV): the turn order, whose turn
it is and who's next, so players plan during other turns. player_view_rows
decides what they may see. The Informative view has everyone's Hit Points, as on
the GM's cards, size, AC and speed. The Limited view is the same for players,
who can tell each other all of it anyway, but a monster's row has only
its speed, the damage it's taken, a word for how hurt it is and what attack rolls
have shown of its AC. In both, a monster they can't perceive isn't listed, and
nothing else of its stat block is shown."""

import math
from dataclasses import dataclass, replace
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QGuiApplication, QKeyEvent
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import CombatStatus
from Core.Definitions import Condition
from .attack_rolls import known_ac_text
from .cards_mixin import _hp_chunk_color
from .dialogs_mixin import _display, _speed_text
from .monster_actions import first_number
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
# The log can say Bloodied as well, since they can see the HP it comes from.
LOGGED_MONSTER_CONDITIONS = SHOWN_MONSTER_CONDITIONS | {CombatStatus.BLOODIED.value}
# The Limited view's words: the highest percentage of Hit Points each one covers,
# lowest first. Bloodied is the rules' own, half or fewer.
_HEALTH_WORDS = ((25, "Dying"), (50, "Bloodied"), (75, "Injured"), (100, "Healthy"))

_STYLE = """
QWidget#playerView { background-color: #1a1a2e; }
QLabel { color: #eaeaea; font-size: 26px; background: transparent; }
QLabel#playerViewRound { color: #c9a84c; font-size: 34px; font-weight: bold; }
QFrame#playerViewRow { border-radius: 6px; }
QFrame#playerViewRow[turn="now"] { background-color: #3a2e00; }
QFrame#playerViewRow[turn="next"] { background-color: #0f3460; }
QLabel#playerViewMark { color: #c9a84c; font-weight: bold; }
QLabel#playerViewConditions { color: #a0c4ff; font-size: 22px; }
QLabel#playerViewDetails { color: #a0a0b0; font-size: 20px; }
QLabel#playerViewMember { font-size: 22px; }
QProgressBar {
    background-color: #8a8a9a;
    font-size: 22px;
    min-height: 34px;
    max-height: 34px;
}
"""
_BAR_WIDTH = 320


@dataclass(frozen=True)
class PlayerViewHealth:
    name: str  # whose it is, to tell an initiative group's members apart
    text: str  # "12 / 30", or how they stand at 0 HP
    percent: int  # how full the bar is
    color: str  # the bar's color, the same as on the GM's card


@dataclass(frozen=True)
class PlayerViewRow:
    name: str
    details: str  # "Large · AC 13 · Speed 40 ft.", or "" if nothing's known
    health: tuple[PlayerViewHealth, ...]  # one bar for each combatant on this turn
    conditions: tuple[str, ...]
    turn: str  # "now", "next" or ""


def _health_text(char: dict, death_state: str) -> str:
    if death_state == "dead":
        return "Dead" if char.get("_is_player") else "Defeated"
    if death_state == "stabilized":
        return "Stable"
    if death_state == "dying":
        fails, saves = char.get("death_saves_fail", 0), char.get(
            "death_saves_success", 0
        )
        return f"Dying ({fails} failed, {saves} saved)"
    temp = char.get("temp_hp", 0)
    return f"{char['hp']} / {char['max_hp']}" + (f" (+{temp} temp)" if temp else "")


def _health(char: dict, death_state: str) -> PlayerViewHealth:
    hp, max_hp = max(char["hp"], 0), max(char["max_hp"], 1)
    return PlayerViewHealth(
        char["name"],
        _health_text(char, death_state),
        # Rounded up, so a bar is only empty at 0 HP.
        min(math.ceil(100 * hp / max_hp), 100),
        _hp_chunk_color(hp, max_hp),
    )


def _limited_health(char: dict, death_state: str) -> PlayerViewHealth:
    """_health without the numbers: a word, and a bar that only moves when the
    word does, since an exact bar would give the HP away just the same."""
    if death_state != "alive":
        text = "Dying" if death_state == "dying" else _health_text(char, death_state)
        return PlayerViewHealth(char["name"], text, 0, _hp_chunk_color(0, 1))
    # A summon whose HP isn't set yet (max HP 0) has nothing to be hurt from.
    left = min(100 * char["hp"] / char["max_hp"], 100) if char["max_hp"] > 0 else 100
    percent, word = next(band for band in _HEALTH_WORDS if left <= band[0])
    return PlayerViewHealth(char["name"], word, percent, _hp_chunk_color(percent, 100))


def _can_be_seen(char: dict) -> bool:
    states = set(char.get("conditions", [])) | set(char.get("visibility_states", []))
    return bool(char.get("_is_player")) or not states & HIDDEN_STATES


def _unit_speeds(unit: list[dict]) -> list[str]:
    return list(
        dict.fromkeys(f"Speed {speed}" for speed in map(_speed_text, unit) if speed)
    )


def _unit_details(unit: list[dict]) -> str:
    """Everyone's size, AC and speed. A player's AC is a sentence once they have
    a Shield, so only the number they have now is shown."""
    sizes = [_display(c["size"]) for c in unit if c.get("size")]
    armor = [
        f"AC {first_number(c.get('ac'))}"
        for c in unit
        if first_number(c.get("ac")) is not None
    ]
    return " · ".join(dict.fromkeys(sizes + armor + _unit_speeds(unit)))


def _limited_view(
    unit: list[dict], death_state: Callable[[dict], str]
) -> tuple[str, tuple[PlayerViewHealth, ...]]:
    """A monster's details and bars on the Limited view. Damage taken and what's
    known of the AC go under a lone monster's name, and by each member's name in
    a group, where each bar already has one. A phone's narrow column shouldn't
    break inside either, so damage taken goes first on a row of its own, and
    neither can break by a member's name."""
    notes = [
        [f"{c.get('stats', {}).get('damage_taken', 0)} damage taken", known_ac_text(c)]
        for c in unit
    ]
    health = tuple(_limited_health(c, death_state(c)) for c in unit)
    if len(unit) == 1:
        return " · ".join(list(filter(None, notes[0])) + _unit_speeds(unit)), health
    return (
        " · ".join(_unit_speeds(unit)),
        tuple(
            replace(
                h,
                name=" · ".join(
                    [h.name]
                    + [t.replace(" ", "\N{NO-BREAK SPACE}") for t in filter(None, n)]
                ),
            )
            for h, n in zip(health, notes)
        ),
    )


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
    limited: bool = False,
) -> list[PlayerViewRow]:
    """A row for each turn in `order` that the players can see. `now` is the
    current turn and `upcoming` the turns after it; "next" goes on the first
    of those they can see, so a hidden monster's place doesn't give it away.
    On that monster's own turn, "now" stays where it was, for the same reason.
    `limited` is the Limited view, for monsters' rows: a player is never in an
    initiative group, so a row is all monsters or one player."""
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
        if limited and not shown[0].get("_is_player"):
            details, health = _limited_view(shown, death_state)
        else:
            details = _unit_details(shown)
            health = tuple(_health(c, death_state(c)) for c in shown)
        rows.append(
            PlayerViewRow(
                unit_label(shown), details, health, _unit_conditions(shown), turn
            )
        )
    return rows


def _health_line(health: PlayerViewHealth, in_group: bool) -> QHBoxLayout:
    """A combatant's HP bar, with its name when it shares a row with others."""
    line = QHBoxLayout()
    if in_group:
        member = QLabel(health.name)
        member.setObjectName("playerViewMember")
        line.addWidget(member, stretch=1)
    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(health.percent)
    bar.setFormat(health.text)
    bar.setTextVisible(True)
    bar.setFixedWidth(_BAR_WIDTH)
    bar.setStyleSheet(
        f"QProgressBar::chunk {{ background-color: {health.color};"
        " border-radius: 3px; }"
    )
    line.addWidget(bar)
    return line


def may_read_log_line(
    text: str, character: str | None, value: object, chars: list[dict]
) -> bool:
    """Whether players may read an encounter log line. It's asked when the line
    is logged, because it depends on who they can perceive at that moment: a
    hidden monster's attack stays private after it's revealed.

    A line about a monster says which condition or effect it's about in
    `value`, since the text can't be trusted to name it: it may already be gone,
    and "keeps concentration" doesn't say Concentrating. The whole text is also
    checked, not just `character`: a hidden monster can be named as the source
    of a line about someone else, or in its turn's prefix."""
    private = {c["name"] for c in chars if not _can_be_seen(c)}
    for unit in initiative_units(chars):
        group = unit[0].get("initiative_group")
        if group and not any(_can_be_seen(c) for c in unit):
            private.add(group)
    if character in private:
        return False
    condition = value.get("condition", "") if isinstance(value, dict) else ""
    # Every one by that name: nothing stops two monsters sharing one.
    for subject in chars:
        if subject["name"] != character or subject.get("_is_player"):
            continue
        if condition and condition not in LOGGED_MONSTER_CONDITIONS:
            return False
        private |= set(subject.get("conditions", [])) - LOGGED_MONSTER_CONDITIONS
    return not any(name in text for name in private)


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
        if row.details:
            details = QLabel(row.details)
            details.setObjectName("playerViewDetails")
            grid.addWidget(details, 1, 1)
        in_group = len(row.health) > 1
        bars = QVBoxLayout()
        bars.setSpacing(4)
        for health in row.health:
            bars.addLayout(_health_line(health, in_group))
        if in_group:
            grid.addLayout(bars, 2, 1, 1, 2)
        else:
            grid.addLayout(bars, 0, 2, 2, 1)
        if row.conditions:
            conditions = QLabel(", ".join(row.conditions))
            conditions.setObjectName("playerViewConditions")
            conditions.setWordWrap(True)
            grid.addWidget(conditions, 3, 1, 1, 2)
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
