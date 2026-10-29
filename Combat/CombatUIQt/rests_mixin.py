"""Rests mixin for CombatAppQt: the Short Rest and Long Rest buttons, for the
tracked party between encounters or before a loaded encounter is started.

A rest is an entry of its own in the player log (Combat/PlayerLog.py), and
the party's state is replayed in that order. A long rest's entry is just the
rest; a short rest's carries its few events (heals, regained feature uses),
since nothing between encounters has a log of its own. A loaded encounter
that hasn't started gets its entry only once something happens in it, so a
rest taken before it comes first."""

from typing import Callable

from PyQt6.QtWidgets import QMessageBox

import Combat.PlayerLog as PlayerLog
from Combat.EncounterLogs import read_log_status

from .state import CombatWindowState


class RestsMixin(CombatWindowState):
    """Mixin for short and long rests from the combat window."""

    def _can_rest(self) -> bool:
        """The party is tracked, and no fight is underway: between
        encounters, or an encounter not started yet."""
        if not self.player_log_file:
            return False
        if self.phase == "PARTY":
            return True
        return self.phase != "COMBAT" and read_log_status(self.log_file) is None

    def _refresh_rest_buttons(self):
        enabled = self._can_rest()
        self._short_rest_btn.setEnabled(enabled)
        self._long_rest_btn.setEnabled(enabled)
        tip = (
            ""
            if enabled
            else "Rests need a tracked party (--player-log) and no fight underway."
        )
        self._short_rest_btn.setToolTip(tip)
        self._long_rest_btn.setToolTip(tip)

    def _after_rest(self):
        """Undo stops at a rest; the window shows the rested party."""
        self.history = []
        if self.phase == "PARTY":
            self._show_party_view()
        self._log_status_label.setText(self._log_status_text())

    def _long_rest(self):
        if not self._can_rest():
            return
        answer = QMessageBox.question(
            self._window,
            "Long Rest",
            "Take a long rest?\n\nThe party is fully restored: HP, spell slots, "
            "feature uses and conditions. What came before still counts in "
            "the statistics.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.player_log_data["sessions"].append(PlayerLog.long_rest_entry())
        self._write_player_log()
        self._rebuild_players_from_log()
        self._after_rest()

    def _record_short_rest(self, take_rest: Callable[[], object]):
        """Run `take_rest` (the short-rest window) with every event it logs
        collected, then record them as one short-rest entry in the player log
        (none if nothing happened)."""
        self._rest_events = []
        try:
            take_rest()
        finally:
            events, self._rest_events = self._rest_events, None
        if events:
            self.player_log_data["sessions"].append(
                {
                    "type": PlayerLog.SHORT_REST,
                    "started_at": PlayerLog.now(),
                    "events": events,
                }
            )
            self._write_player_log()

    def _short_rest(self):
        """Open the short-rest window on the party as they are, then go back
        to what the window was doing."""
        if not self._can_rest():
            return
        from .rest import short_rest_dialog

        self._record_short_rest(
            lambda: short_rest_dialog(self, self._window).exec()  # type: ignore[arg-type]
        )
        self._after_rest()
