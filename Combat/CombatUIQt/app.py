"""Main CombatAppQt class."""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from Combat.Definitions import tracked_condition_names
from Combat.PlayerCombatant import combatant_from_character, combatant_from_stat_block
from Combat.Scenario import CombatScenario
from Model.Creatures.Combatants import BasicCombatantData, Visibility

from .cards_mixin import CardsMixin
from .conditions_mixin import ConditionsMixin
from .damage_mixin import DamageMixin
from .dialogs_mixin import DialogsMixin
from .encounters_mixin import EncountersMixin
from .rests_mixin import RestsMixin
from .features_mixin import FeaturesMixin
from .logging_mixin import LoggingMixin
from .rolls_mixin import RollsMixin
from .spells_mixin import SpellsMixin
from .stats import _default_stats
from .styles import QSS
from .timer_mixin import TimerMixin
from .turns_mixin import TurnsMixin
from .window_mixin import WindowMixin


class CombatAppQt(
    DamageMixin,
    ConditionsMixin,
    SpellsMixin,
    FeaturesMixin,
    TurnsMixin,
    CardsMixin,
    LoggingMixin,
    DialogsMixin,
    EncountersMixin,
    RestsMixin,
    TimerMixin,
    RollsMixin,
    WindowMixin,
):
    ACTION_ECONOMY_TYPES: list[str] = ["Action", "Bonus Action", "Reaction"]
    ACTION_ECONOMY_SHORTCUTS: dict[str, str] = {
        "A": "Action",
        "B": "Bonus Action",
        "R": "Reaction",
    }

    def __init__(
        self,
        combatants: list[BasicCombatantData],
        character_sheets: list,
        combat_log_dir: str | Path,
        combatants_per_column: int = 4,
        log_path: str | Path | None = None,
        player_log_path: str | None = None,
        scenario_name: str | None = None,
        scenarios: list[CombatScenario] | None = None,
    ):
        """`character_sheets` is the tracked party. Encounters come from the
        campaign's `scenarios`, each played from its prepared log in
        `combat_log_dir` (Combat/EncounterLogs.py):

        - With `scenario_name`, `log_path` is that encounter's log, which
          run() opens (asking whether to continue or restart a fight in progress).
        - Without one, `log_path` is a log to fight `combatants` in directly
          (tests and scripts).
        - With neither, the window shows the party between encounters, and
          nothing is logged until an encounter is loaded."""
        self.combatants_per_column = combatants_per_column

        # ---- data ----
        self.characters: list[dict] = []
        # The tracked party by character name; who of them is in the window
        # depends on the encounter (_set_party).
        self._party_sheets = {}
        for cs in character_sheets:
            self._add_from_character_sheet(cs)
            self._party_sheets[self.characters[-1]["name"]] = cs
        for c in combatants:
            self._add_basic_combatant(c)

        self.conditions = tracked_condition_names()
        self.visibility_states = Visibility.list_all()
        self.selected_character: dict | None = None
        self.target_characters: list[dict] = []
        self._target_anchor: dict | None = None
        self.round_number = 1
        self.history = []
        self._open_undo_point = None

        # --- Phase / initiative state ---
        self.phase: str = "INITIATIVE"
        self.initiative_order: list[dict] = []
        self.current_turn_idx: int = 0

        # --- Persistent player log: bring the party to their current state ---
        self.player_log_file = Path(player_log_path) if player_log_path else None
        self._scenario_name = scenario_name
        self._scenarios = list(scenarios or [])
        self.player_log_data: dict = {"sessions": []}
        self._player_log_session: dict | None = None
        # A short rest's events, while it's being taken (RestsMixin).
        self._rest_events: list[dict] | None = None
        if self.player_log_file:
            self._init_player_log()

        self._combat_log_dir = Path(combat_log_dir)
        self.log_file: Path | None = None
        if log_path is not None and scenario_name is None:
            self._use_log_file(Path(log_path))
        elif log_path is None:
            self.phase = "PARTY"
        # With a scenario, run() opens `log_path`.
        self._encounter_log_to_open = (
            Path(log_path) if log_path is not None and scenario_name else None
        )

        # card widget registry: maps id(char_dict) -> QFrame
        self._card_widgets: dict = {}

        # initiative input registry: maps id(char_dict) -> QLineEdit
        self._initiative_inputs: dict = {}

        # HP inputs for combatants whose HP isn't set yet: maps id(char_dict) -> QLineEdit
        self._initiative_hp_inputs: dict = {}

        # Initialize timers
        self._init_timers()

    def _add_from_character_sheet(self, character_sheet):
        char = combatant_from_character(character_sheet)
        char["stats"] = _default_stats()
        self.characters.append(char)

    def _add_basic_combatant(self, combatant: BasicCombatantData):
        char = combatant_from_stat_block(combatant)
        char["stats"] = _default_stats()
        self.characters.append(char)

    def run(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        assert isinstance(app, QApplication)
        app.setStyleSheet(QSS)

        self._build_window()

        if self._encounter_log_to_open is not None:
            if not self._open_scenario_at_start(self._encounter_log_to_open):
                return

        self._window.show()
        self._start_session_timer()
        sys.exit(app.exec())
