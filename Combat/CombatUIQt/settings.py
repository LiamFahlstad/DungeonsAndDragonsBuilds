"""The combat UI's settings (the Settings dialog, DialogsMixin): what each one
does, its default (how the window behaved before the setting existed), and how
they're kept between runs."""

from dataclasses import dataclass, fields

from PyQt6.QtCore import QSettings


@dataclass
class CombatSettings:
    # Turns (TurnsMixin._on_turn_changed)
    source_follows_turn: bool = True
    clear_targets_on_turn: bool = True
    restart_player_timer_on_turn: bool = False
    scroll_to_active_card: bool = True
    skip_dead_turns: bool = True
    # Damage (DamageMixin._do_apply_damage)
    remember_damage_type: bool = True
    reset_damage_type_after_hit: bool = True
    ask_concentration_saves: bool = True
    monsters_roll_concentration: bool = False
    focus_damage_on_target: bool = False
    # Initiative (TurnsMixin._start_combat)
    ask_initiative_ties: bool = True
    # Panel (WindowMixin._apply_panel_settings)
    show_more_controls: bool = False

    def load(self, store: QSettings):
        """Take each setting saved in `store`, keeping the default for the rest."""
        for f in fields(self):
            setattr(self, f.name, store.value(f.name, getattr(self, f.name), type=bool))

    def save(self, store: QSettings):
        for f in fields(self):
            store.setValue(f.name, getattr(self, f.name))


def open_settings_store() -> QSettings:
    """Where the combat UI keeps its settings between runs (the registry on
    Windows)."""
    return QSettings("DungeonsAndDragonsBuilds", "CombatEngine")


@dataclass(frozen=True)
class SettingInfo:
    name: str  # the CombatSettings field
    label: str
    hint: str


# The Settings dialog's sections, in order.
SETTING_SECTIONS: list[tuple[str, list[SettingInfo]]] = [
    (
        "Turns",
        [
            SettingInfo(
                "source_follows_turn",
                "Source follows the turn",
                "When the turn changes, whoever's turn it is becomes the source"
                " (an initiative group's first member). You can still click"
                " another source; it stays until the next turn.",
            ),
            SettingInfo(
                "clear_targets_on_turn",
                "Clear targets when the turn changes",
                "Start every turn with no targets picked. Off keeps them for"
                " the next turn.",
            ),
            SettingInfo(
                "restart_player_timer_on_turn",
                "Restart the player timer each turn",
                "When the turn changes, the player timer goes back to 00:00 and"
                " runs during a player's turn (it stays stopped on others').",
            ),
            SettingInfo(
                "scroll_to_active_card",
                "Scroll to the active card",
                "Scroll the card grid so whoever's turn it is can be seen.",
            ),
            SettingInfo(
                "skip_dead_turns",
                "Skip dead combatants' turns",
                "Next passes straight over a turn where everyone is dead. Anyone"
                " dying still gets theirs, for the death save, and durations"
                " count skipped turns as usual.",
            ),
        ],
    ),
    (
        "Damage",
        [
            SettingInfo(
                "remember_damage_type",
                "Remember each source's damage type",
                "Picking a source sets the damage type it last dealt. Typing a"
                " type in the Damage field (12 fi) always wins.",
            ),
            SettingInfo(
                "reset_damage_type_after_hit",
                "Reset the damage type after each hit",
                "Back to the source's remembered type, or blank. Off keeps the"
                " last one picked, for several hits of a type in a row.",
            ),
            SettingInfo(
                "ask_concentration_saves",
                "Ask for a Concentration save",
                "When a concentrating creature takes damage, show the"
                " Constitution save on its card. Off leaves the save to you"
                " (Ctrl+C removes Concentrating from the source).",
            ),
            SettingInfo(
                "monsters_roll_concentration",
                "Roll monsters' Concentration saves",
                "Monsters roll the save themselves and the result is logged;"
                " players' saves stay on their cards.",
            ),
            SettingInfo(
                "focus_damage_on_target",
                "Jump to Damage after picking a target",
                "Right-click a card, then just type the amount. Letter and"
                " number shortcuts type into the field until Esc.",
            ),
        ],
    ),
    (
        "Initiative",
        [
            SettingInfo(
                "ask_initiative_ties",
                "Ask how to break initiative ties",
                "Off puts the higher Dexterity first and starts straight away.",
            ),
        ],
    ),
    (
        "Panel",
        [
            SettingInfo(
                "show_more_controls",
                "Show Visibility, Spell Slots and Action Economy",
                "Their keyboard shortcuts work either way.",
            ),
        ],
    ),
]
