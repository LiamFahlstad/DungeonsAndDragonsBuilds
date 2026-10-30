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
    # Damage (DamageMixin._do_apply_damage)
    reset_damage_type_after_hit: bool = True
    ask_concentration_saves: bool = True

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
        ],
    ),
    (
        "Damage",
        [
            SettingInfo(
                "reset_damage_type_after_hit",
                "Reset the damage type after each hit",
                "Off keeps the last damage type picked, for several hits of the"
                " same type in a row.",
            ),
            SettingInfo(
                "ask_concentration_saves",
                "Ask for a Concentration save",
                "When a concentrating creature takes damage, open the"
                " Constitution save dialog. Off leaves the save to you (Ctrl+C"
                " removes Concentrating from the source).",
            ),
        ],
    ),
]
