"""Timer widgets mixin for CombatAppQt."""

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TimerMixin:
    """Mixin for session and player timer widgets."""

    _COMPACT_BTN_STYLE = (
        "padding: 2px 6px; min-height: 18px; font-size: 10px;"
    )

    def _build_timer_section(self) -> QWidget:
        """Build and return a compact widget with the round/session status
        row and the player timer row (label + inline controls)."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Row 1: Round indicator + session clock, sharing one line.
        status_row = QHBoxLayout()
        self.round_label = QLabel(f"Round {self.round_number}")
        self.round_label.setStyleSheet(
            "color: #c9a84c; font-weight: bold; font-size: 12px;"
        )
        status_row.addWidget(self.round_label)
        status_row.addStretch()
        self._session_timer_label = QLabel("Session 00:00:00")
        self._session_timer_label.setStyleSheet(
            "color: #a0a0b0; font-size: 11px;"
        )
        status_row.addWidget(self._session_timer_label)
        layout.addLayout(status_row)

        # Row 2: Player timer label + Start/Pause/Reset, all inline.
        player_row = QHBoxLayout()
        player_row.setSpacing(4)

        self._player_timer_label = QLabel("00:00")
        self._player_timer_label.setStyleSheet(
            "color: #c9a84c; font-weight: bold; font-size: 12px;"
        )
        player_row.addWidget(self._player_timer_label)
        player_row.addStretch()

        self._player_timer_start_btn = QPushButton("Start")
        self._player_timer_start_btn.setStyleSheet(self._COMPACT_BTN_STYLE)
        self._player_timer_start_btn.clicked.connect(self._start_player_timer)
        player_row.addWidget(self._player_timer_start_btn)

        self._player_timer_pause_btn = QPushButton("Pause")
        self._player_timer_pause_btn.setStyleSheet(self._COMPACT_BTN_STYLE)
        self._player_timer_pause_btn.clicked.connect(self._pause_player_timer)
        player_row.addWidget(self._player_timer_pause_btn)

        self._player_timer_reset_btn = QPushButton("Reset")
        self._player_timer_reset_btn.setStyleSheet(self._COMPACT_BTN_STYLE)
        self._player_timer_reset_btn.clicked.connect(self._reset_player_timer)
        player_row.addWidget(self._player_timer_reset_btn)

        layout.addLayout(player_row)

        return container

    def _init_timers(self):
        """Initialize timer state and QTimer objects."""
        self._session_elapsed_seconds = 0
        self._session_qtimer = QTimer()
        self._session_qtimer.timeout.connect(self._tick_session_timer)
        self._session_qtimer.setInterval(1000)

        self._player_elapsed_seconds = 0
        self._player_timer_running = False
        self._player_qtimer = QTimer()
        self._player_qtimer.timeout.connect(self._tick_player_timer)
        self._player_qtimer.setInterval(1000)

    def _start_session_timer(self):
        """Start the always-running session clock."""
        self._session_qtimer.start()

    def _tick_session_timer(self):
        """Increment session timer and update label."""
        self._session_elapsed_seconds += 1
        self._session_timer_label.setText(
            f"Session {self._format_hms(self._session_elapsed_seconds)}"
        )

    def _start_player_timer(self):
        """Start the player timer (or resume if paused)."""
        if not self._player_timer_running:
            self._player_qtimer.start()
            self._player_timer_running = True

    def _pause_player_timer(self):
        """Pause the player timer."""
        self._player_qtimer.stop()
        self._player_timer_running = False

    def _reset_player_timer(self):
        """Reset the player timer to 00:00."""
        self._player_qtimer.stop()
        self._player_timer_running = False
        self._player_elapsed_seconds = 0
        self._player_timer_label.setText("00:00")

    def _tick_player_timer(self):
        """Increment player timer and update label."""
        self._player_elapsed_seconds += 1
        self._player_timer_label.setText(
            self._format_ms(self._player_elapsed_seconds)
        )

    @staticmethod
    def _format_hms(seconds: int) -> str:
        """Format seconds as HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_ms(seconds: int) -> str:
        """Format seconds as MM:SS (minutes may exceed 2 digits)."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
