"""Rests mixin for CombatAppQt: the Short Rest and Long Rest buttons, for the
tracked party between fights (in an adventure session, or before a loaded
encounter is started).

A rest is an entry of its own in the player log (Combat/PlayerLog.py), and
the party's state is replayed in that order, so whatever the party does after
a rest goes in a log whose entry comes after it: an adventure carries on in a
new adventure log, and a loaded encounter that hasn't started gets its entry
only once something happens in it."""

from PyQt6.QtWidgets import QMessageBox

import Combat.PlayerLog as PlayerLog
from Combat.EncounterLogs import read_log_status

from .state import CombatWindowState

SHORT_REST = "short_rest"


class RestsMixin(CombatWindowState):
    """Mixin for short and long rests from the combat window."""

    def _can_rest(self) -> bool:
        """The party is tracked, and no fight is underway: an adventure
        session, or an encounter not started yet."""
        if not self.player_log_file:
            return False
        if self._scenario_name is None:
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

    def _in_journal(self) -> bool:
        session = self._player_log_session
        return session is not None and any(
            s is session for s in self.player_log_data["sessions"]
        )

    def _after_rest(self):
        """An adventure that already has an entry before the rest carries on
        in a new log after it. Undo stops at a rest."""
        if self._scenario_name is None and self._in_journal():
            self._start_unscripted_log()
        self.history = []
        if self.phase == "COMBAT":
            self._rebuild_cards()
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

    def _short_rest(self):
        """Open the short-rest window on the party as they are, logging to a
        short-rest log of its own, then go back to what the window was doing."""
        if not self._can_rest():
            return
        from .rest import short_rest_dialog

        encounter_log = self.log_file if self._scenario_name else None
        self._start_unscripted_log(SHORT_REST)
        short_rest_dialog(self, self._window).exec()  # type: ignore[arg-type]
        if encounter_log is not None:
            self._use_log_file(encounter_log)
        else:
            self._start_unscripted_log()
        self._after_rest()
