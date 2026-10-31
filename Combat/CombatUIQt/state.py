"""CombatWindowState: what the Combat UI's mixins share.

CombatAppQt is assembled from mixins (cards, conditions, damage, dialogs,
...) that read each other's state and call each other's methods. Each mixin
inherits this class, so those shared names are declared - with types - in one
place, and the type checker can verify every use.

- Attributes are declared here and assigned in CombatAppQt.__init__ or while
  the window is built (WindowMixin, TimerMixin).
- Methods are implemented in exactly one mixin (named in the error each stub
  raises); the stubs only declare their signatures. CombatWindowState comes
  last in CombatAppQt's method resolution order, so a stub is never called.
"""

from pathlib import Path

from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QWidget,
)

from Combat.Rules import Rule
from Combat.Scenario import CombatScenario
from Model.Creatures.Combatants import BasicCombatantData

from .settings import CombatSettings
from .undo import UndoPoint


class CombatWindowState:
    # ── Class constants (CombatAppQt) ──────────────────────────────────────

    ACTION_ECONOMY_TYPES: list[str]
    ACTION_ECONOMY_SHORTCUTS: dict[str, str]

    # ── Data (CombatAppQt.__init__) and widgets (WindowMixin, TimerMixin) ─

    characters: list[dict]
    combatants_per_column: int
    conditions: list[str]
    visibility_states: list[str]
    selected_character: dict | None
    target_characters: list[dict]
    # The card a Shift + right click range of targets starts from.
    _target_anchor: dict | None
    # Targets marked as having saved, for half damage (DamageMixin).
    _saved_targets: list[dict]
    # What a monster's action rolled into the Damage field, if it's there.
    _rolled_damage_text: str
    # What to remember this turn, and what starting it did (TurnPanelMixin).
    _turn_reminders: list[str]
    _turn_start_notes: list[str]
    # Settings (DialogsMixin._show_settings_dialog), kept between runs in
    # _settings_store; None (tests, scripts) keeps them for this run only.
    settings: CombatSettings
    _settings_store: QSettings | None
    round_number: int
    # Undo steps, oldest first, and the one being recorded (undo.py).
    history: list[UndoPoint]
    _open_undo_point: UndoPoint | None
    phase: str
    initiative_order: list[dict]
    current_turn_idx: int
    player_log_file: Path | None
    # The encounter log events are written to (LoggingMixin._use_log_file);
    # None between encounters, when nothing is logged.
    log_file: Path | None
    # The tracked party's character sheets by character name (_set_party).
    _party_sheets: dict
    # A short rest's events while it's being taken (RestsMixin).
    _rest_events: list[dict] | None
    _initiative_widget: QWidget | None
    player_log_data: dict
    # This run's entry in the party's journal (see Combat/PlayerLog.py).
    _player_log_session: dict | None
    _scenario_name: str | None
    # The campaign's scenarios, offered by Load Encounter, and the folder
    # holding their encounter logs.
    _scenarios: list[CombatScenario]
    _combat_log_dir: Path
    _card_widgets: dict
    _initiative_inputs: dict
    _initiative_hp_inputs: dict
    _window: QMainWindow
    _scroll_area: QScrollArea
    _cards_container: QWidget
    _grid_layout: QGridLayout
    _init_tracker_container: QWidget
    _turn_divider: QFrame
    _turn_counter_label: QLabel
    _prev_turn_btn: QPushButton
    _next_turn_btn: QPushButton
    round_label: QLabel
    _end_encounter_btn: QPushButton
    _add_combatant_btn: QPushButton
    _short_rest_btn: QPushButton
    _long_rest_btn: QPushButton
    _log_status_label: QLabel
    selected_label: QLabel
    target_label: QLabel
    _status_label: QLabel
    _status_timer: QTimer
    _views_timer: QTimer
    _half_btn: QPushButton
    _more_controls: QWidget
    _more_controls_btn: QPushButton
    _turn_panel: QScrollArea
    _action_result_label: QLabel
    roll_result_label: QLabel
    damage_input: QLineEdit
    heal_input: QLineEdit
    temp_hp_input: QLineEdit
    damage_type_combo: QComboBox
    condition_combo: QComboBox
    visibility_combo: QComboBox
    roll_mode_combo: QComboBox
    spell_combo: QComboBox

    # ── Methods one mixin calls on another ──────────────────────────────────

    def _add_action_use(self, action_type: str):
        raise NotImplementedError("ConditionsMixin._add_action_use")

    def _add_ad_hoc_combatant(self, name: str, hp: int = 10, ac: int = 10):
        raise NotImplementedError("TurnsMixin._add_ad_hoc_combatant")

    def _add_from_character_sheet(self, character_sheet):
        raise NotImplementedError("CombatAppQt._add_from_character_sheet")

    def _add_basic_combatant(self, combatant: BasicCombatantData):
        raise NotImplementedError("CombatAppQt._add_basic_combatant")

    def _add_condition(self):
        raise NotImplementedError("ConditionsMixin._add_condition")

    def _add_condition_to(self, char: dict, cond: str, source: dict | None = None):
        raise NotImplementedError("ConditionsMixin._add_condition_to")

    def _add_visibility(self):
        raise NotImplementedError("ConditionsMixin._add_visibility")

    def _advance_turn(self):
        raise NotImplementedError("TurnsMixin._advance_turn")

    def _apply_bloodied_condition(self, char: dict, source: dict | None = None):
        raise NotImplementedError("DamageMixin._apply_bloodied_condition")

    def _apply_damage(self):
        raise NotImplementedError("DamageMixin._apply_damage")

    def _apply_damage_checked(self):
        raise NotImplementedError("DamageMixin._apply_damage_checked")

    def _apply_failed_death_save(self, char: dict):
        raise NotImplementedError("DamageMixin._apply_failed_death_save")

    def _apply_heal(self):
        raise NotImplementedError("DamageMixin._apply_heal")

    def _apply_success_death_save(self, char: dict):
        raise NotImplementedError("DamageMixin._apply_success_death_save")

    def _apply_temp_hp(self):
        raise NotImplementedError("DamageMixin._apply_temp_hp")

    def _build_initiative_widget(self) -> QWidget:
        raise NotImplementedError("TurnsMixin._build_initiative_widget")

    def _build_turn_panel(self) -> QWidget:
        raise NotImplementedError("TurnPanelMixin._build_turn_panel")

    def _build_timer_section(self) -> QWidget:
        raise NotImplementedError("TimerMixin._build_timer_section")

    def _cast_spell_slot_level(self, level: int):
        raise NotImplementedError("SpellsMixin._cast_spell_slot_level")

    @staticmethod
    def _char_death_state(char: dict) -> str:
        raise NotImplementedError("CardsMixin._char_death_state")

    def _clear_status(self):
        raise NotImplementedError("WindowMixin._clear_status")

    def _report_uncaught_error(self, error_type, error, traceback_):
        raise NotImplementedError("WindowMixin._report_uncaught_error")

    def _con_save_mod(self, char: dict) -> int:
        raise NotImplementedError("DamageMixin._con_save_mod")

    def _apply_panel_settings(self):
        raise NotImplementedError("WindowMixin._apply_panel_settings")

    def _card_right_clicked(self, char: dict, ctrl: bool, shift: bool):
        raise NotImplementedError("CardsMixin._card_right_clicked")

    def _focus_damage_input(self):
        raise NotImplementedError("WindowMixin._focus_damage_input")

    def _focus_heal_input(self):
        raise NotImplementedError("WindowMixin._focus_heal_input")

    def _focus_temp_hp_input(self):
        raise NotImplementedError("WindowMixin._focus_temp_hp_input")

    def _refresh_next_button(self):
        raise NotImplementedError("TurnsMixin._refresh_next_button")

    def _refresh_views(self):
        raise NotImplementedError("TurnPanelMixin._refresh_views")

    def _roll_concentration(self, char: dict, dc: int):
        raise NotImplementedError("DamageMixin._roll_concentration")

    @staticmethod
    def _section_header(text: str) -> QLabel:
        raise NotImplementedError("WindowMixin._section_header")

    def _set_targets(self, targets: list[dict]):
        raise NotImplementedError("WindowMixin._set_targets")

    def _settle_concentration(
        self, char: dict, dc: int, kept: bool, roll: int | None = None
    ):
        raise NotImplementedError("DamageMixin._settle_concentration")

    def _show_source_damage_type(self, source: dict | None):
        raise NotImplementedError("DamageMixin._show_source_damage_type")

    def _show_typed_damage_type(self, text: str):
        raise NotImplementedError("DamageMixin._show_typed_damage_type")

    def _start_monster_turn(self, char: dict):
        raise NotImplementedError("TurnPanelMixin._start_monster_turn")

    def _take_turn_reminders(self):
        raise NotImplementedError("TurnPanelMixin._take_turn_reminders")

    def _toggle_player_view(self):
        raise NotImplementedError("TurnPanelMixin._toggle_player_view")

    def _toggle_saved(self, char: dict):
        raise NotImplementedError("DamageMixin._toggle_saved")

    def _toggle_saved_for_all(self):
        raise NotImplementedError("DamageMixin._toggle_saved_for_all")

    def _upcoming_turns(self) -> list[list[dict]]:
        raise NotImplementedError("TurnsMixin._upcoming_turns")

    def _compute_player_log_stats(self) -> dict[str, dict]:
        raise NotImplementedError("LoggingMixin._compute_player_log_stats")

    def _current_turn_character(self) -> dict | None:
        raise NotImplementedError("LoggingMixin._current_turn_character")

    def _current_turn_group(self) -> list[dict]:
        raise NotImplementedError("TurnsMixin._current_turn_group")

    def _end_concentration_spells(self, char: dict):
        raise NotImplementedError("SpellsMixin._end_concentration_spells")

    def _feature_condition_tooltip(self, char: dict, feature) -> str:
        raise NotImplementedError("FeaturesMixin._feature_condition_tooltip")

    @staticmethod
    def _hp_not_set(char: dict) -> bool:
        raise NotImplementedError("TurnsMixin._hp_not_set")

    def _load_log_from_path(self, path: str):
        raise NotImplementedError("LoggingMixin._load_log_from_path")

    def _log_event(
        self,
        text: str,
        note_turn: bool = True,
        character: str | None = None,
        action=None,
        value=None,
    ):
        raise NotImplementedError("LoggingMixin._log_event")

    def _follow_turn_with_source(self):
        raise NotImplementedError("TurnsMixin._follow_turn_with_source")

    def _on_turn_changed(self):
        raise NotImplementedError("TurnsMixin._on_turn_changed")

    def _log_status_text(self) -> str:
        raise NotImplementedError("LoggingMixin._log_status_text")

    @staticmethod
    def _make_divider() -> QFrame:
        raise NotImplementedError("WindowMixin._make_divider")

    def _previous_turn(self):
        raise NotImplementedError("TurnsMixin._previous_turn")

    def _rebuild_card(self, char: dict):
        raise NotImplementedError("CardsMixin._rebuild_card")

    def _rebuild_cards(self):
        raise NotImplementedError("CardsMixin._rebuild_cards")

    def _refresh_cards(self):
        raise NotImplementedError("CardsMixin._refresh_cards")

    def _refresh_initiative_tracker(self):
        raise NotImplementedError("TurnsMixin._refresh_initiative_tracker")

    def _refresh_rest_buttons(self):
        raise NotImplementedError("RestsMixin._refresh_rest_buttons")

    def _long_rest(self):
        raise NotImplementedError("RestsMixin._long_rest")

    def _short_rest(self):
        raise NotImplementedError("RestsMixin._short_rest")

    def _rebuild_players_from_log(self):
        raise NotImplementedError("LoggingMixin._rebuild_players_from_log")

    def _refresh_turn(self):
        raise NotImplementedError("TurnsMixin._refresh_turn")

    def _refresh_selected_card(self):
        raise NotImplementedError("CardsMixin._refresh_selected_card")

    def _regain_spell_slot(self):
        raise NotImplementedError("SpellsMixin._regain_spell_slot")

    def _remove_action_use(self, action_type: str):
        raise NotImplementedError("ConditionsMixin._remove_action_use")

    def _remove_active_feature(self, char: dict, entry: dict):
        raise NotImplementedError("FeaturesMixin._remove_active_feature")

    def _remove_active_spell(self, char: dict, entry: dict):
        raise NotImplementedError("SpellsMixin._remove_active_spell")

    def _remove_condition(self):
        raise NotImplementedError("ConditionsMixin._remove_condition")

    def _remove_condition_from(self, char: dict, cond: str, source: dict | None = None):
        raise NotImplementedError("ConditionsMixin._remove_condition_from")

    def _remove_visibility(self):
        raise NotImplementedError("ConditionsMixin._remove_visibility")

    def _reset_player_timer(self):
        raise NotImplementedError("TimerMixin._reset_player_timer")

    def _revive(self, char: dict):
        raise NotImplementedError("DamageMixin._revive")

    def _roll_d20(self):
        raise NotImplementedError("RollsMixin._roll_d20")

    def _select_character(self, char: dict):
        raise NotImplementedError("WindowMixin._select_character")

    def _select_target_character(
        self, char: dict, ctrl: bool = False, shift: bool = False
    ):
        raise NotImplementedError("WindowMixin._select_target_character")

    def _shortcut_add_concentration(self):
        raise NotImplementedError("ConditionsMixin._shortcut_add_concentration")

    def _shortcut_clear_target_conditions(self):
        raise NotImplementedError("ConditionsMixin._shortcut_clear_target_conditions")

    def _shortcut_next_turn(self):
        raise NotImplementedError("TurnsMixin._shortcut_next_turn")

    def _shortcut_previous_turn(self):
        raise NotImplementedError("TurnsMixin._shortcut_previous_turn")

    def _shortcut_remove_concentration(self):
        raise NotImplementedError("ConditionsMixin._shortcut_remove_concentration")

    def _show_add_combatant_dialog(self):
        raise NotImplementedError("DialogsMixin._show_add_combatant_dialog")

    def _show_cast_spell_dialog(self):
        raise NotImplementedError("SpellsMixin._show_cast_spell_dialog")

    def _show_condition_info(self, condition_name: str):
        raise NotImplementedError("DialogsMixin._show_condition_info")

    def _show_custom_condition_dialog(self):
        raise NotImplementedError("ConditionsMixin._show_custom_condition_dialog")

    def _show_current_log(self):
        raise NotImplementedError("LoggingMixin._show_current_log")

    def _show_enable_feature_dialog(self):
        raise NotImplementedError("FeaturesMixin._show_enable_feature_dialog")

    def _end_encounter(self):
        raise NotImplementedError("EncountersMixin._end_encounter")

    def _show_load_encounter_dialog(self):
        raise NotImplementedError("EncountersMixin._show_load_encounter_dialog")

    def _show_more_info(self):
        raise NotImplementedError("DialogsMixin._show_more_info")

    def _show_player_log(self):
        raise NotImplementedError("LoggingMixin._show_player_log")

    def _show_rule_popup(self, title: str, heading: str, body: str):
        raise NotImplementedError("DialogsMixin._show_rule_popup")

    def _show_rules(self):
        raise NotImplementedError("DialogsMixin._show_rules")

    def _show_settings_dialog(self):
        raise NotImplementedError("DialogsMixin._show_settings_dialog")

    def _show_status(self, text: str):
        raise NotImplementedError("WindowMixin._show_status")

    def _show_statistics(self):
        raise NotImplementedError("DialogsMixin._show_statistics")

    def _show_visibility_info(self, visibility_name: str):
        raise NotImplementedError("DialogsMixin._show_visibility_info")

    def _read_log(self) -> dict:
        raise NotImplementedError("LoggingMixin._read_log")

    def _set_party(self, names: list[str] | None):
        raise NotImplementedError("LoggingMixin._set_party")

    def _show_party_view(self):
        raise NotImplementedError("EncountersMixin._show_party_view")

    def _build_party_view(self) -> QWidget:
        raise NotImplementedError("EncountersMixin._build_party_view")

    def _use_log_file(self, path: Path | None):
        raise NotImplementedError("LoggingMixin._use_log_file")

    def _write_log(self, data: dict):
        raise NotImplementedError("LoggingMixin._write_log")

    def _write_player_log(self):
        raise NotImplementedError("LoggingMixin._write_player_log")

    def _switch_to_combat(self):
        raise NotImplementedError("TurnsMixin._switch_to_combat")

    def _start_player_timer(self):
        raise NotImplementedError("TimerMixin._start_player_timer")

    def _switch_to_initiative(self):
        raise NotImplementedError("TurnsMixin._switch_to_initiative")

    def _tick_active_features(self):
        raise NotImplementedError("FeaturesMixin._tick_active_features")

    def _tick_active_spells(self):
        raise NotImplementedError("SpellsMixin._tick_active_spells")

    def _tick_timed_conditions(
        self, ended: list[dict], started: list[dict], new_round: bool
    ):
        raise NotImplementedError("ConditionsMixin._tick_timed_conditions")

    def _undo_last(self):
        raise NotImplementedError("LoggingMixin._undo_last")

    def _update_target_label(self):
        raise NotImplementedError("WindowMixin._update_target_label")

    def _visibility_rule(self, visibility_name: str) -> Rule | None:
        raise NotImplementedError("DialogsMixin._visibility_rule")
