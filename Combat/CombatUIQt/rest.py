"""Headless long-rest checkpointing and the short-rest healing window.

Both paths reuse CombatAppQt to reconstruct the party's current state (it
already knows how to replay a player log onto freshly-built characters —
see LoggingMixin._init_player_log) without ever calling `.run()`, so no
combat window or QApplication event loop is created for a long rest.
"""

import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import Combat.CombatantGroups as CombatantGroups
from Combat.Definitions import Action

from .app import CombatAppQt
from .styles import QSS


def _rest_checkpoint_path(player_log_path: str, suffix: str) -> str:
    """A new, timestamped sibling path next to player_log_path, e.g.
    'main_party.json' -> 'main_party_long_rest_20260831_071200.json'."""
    src = Path(player_log_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(src.with_name(f"{src.stem}_{suffix}_{timestamp}{src.suffix}"))


def _build_party_state(player_log_path: str, write_path: str | None) -> CombatAppQt:
    """Headlessly replay player_log_path onto a fresh CombatAppQt instance
    (no window, no event loop — .run() is never called). If write_path is
    given, all further writes to the player log go there instead of
    player_log_path, leaving the original file untouched."""
    players = CombatantGroups.get_players_group()
    return CombatAppQt(
        combatants=[],
        character_sheets=players,
        player_log_path=player_log_path,
        player_log_write_path=write_path,
        scenario_name=None,
    )


def _restore_hp(app: CombatAppQt, char: dict, note: str):
    if char["hp"] >= char["max_hp"]:
        return
    was_downed = app._char_death_state(char) != "alive"
    heal = char["max_hp"] - char["hp"]
    char["hp"] = char["max_hp"]
    heal_value = {"heal": heal, "source_name": None, "target_name": char["name"]}
    app.history.append((Action.HEAL, heal_value))
    app._log_event(
        f"{char['name']} heals {heal} HP ({note})",
        character=char["name"],
        action=Action.HEAL,
        value=heal_value,
    )
    if was_downed:
        char["death_saves_fail"] = 0
        char["death_saves_success"] = 0
    app._apply_bloodied_condition(char)


def _restore_spell_slots(app: CombatAppQt, char: dict):
    max_slots = char.get("max_spell_slots", {})
    for level, full_count in max_slots.items():
        current = char["spell_slots"].get(level, 0)
        for _ in range(full_count - current):
            char["spell_slots"][level] = char["spell_slots"].get(level, 0) + 1
            app.history.append((Action.ADD_SPELL_SLOT, level))
            app._log_event(
                f"{char['name']} regains a Level {level} spell slot (long rest)",
                character=char["name"],
                action=Action.ADD_SPELL_SLOT,
                value=level,
            )


def apply_long_rest(player_log_path: str) -> str:
    """Fully heal and restore spell slots for every tracked player, writing
    the result to a NEW, appropriately-named player log file (the original
    is left untouched) and returning its path. Never opens a window."""
    write_path = _rest_checkpoint_path(player_log_path, "long_rest")
    app = _build_party_state(player_log_path, write_path)
    for char in app.characters:
        if not char.get("_is_player"):
            continue
        _restore_hp(app, char, note="long rest")
        _restore_spell_slots(app, char)
    app._write_player_log()
    return write_path


def run_short_rest(player_log_path: str):
    """Open a small standalone healing window (not the main combat window)
    letting each tracked player be healed a manually-entered amount. Heals
    are appended to the same player log passed in — no new file is created."""
    app = _build_party_state(player_log_path, write_path=None)
    players = [c for c in app.characters if c.get("_is_player")]

    qapp = QApplication.instance() or QApplication(sys.argv)
    qapp.setStyleSheet(QSS)

    dlg = QDialog()
    dlg.setWindowTitle(f"Short Rest — {Path(player_log_path).name}")
    dlg.setMinimumSize(420, 120 + 40 * len(players))
    dlg.setStyleSheet(QSS)

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(14, 14, 14, 14)
    outer.setSpacing(10)

    info_lbl = QLabel("Enter a heal amount for each player who spends Hit Dice, then Apply.")
    info_lbl.setObjectName("secondary")
    info_lbl.setWordWrap(True)
    outer.addWidget(info_lbl)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    outer.addWidget(scroll, stretch=1)

    grid_widget = QWidget()
    grid = QGridLayout(grid_widget)
    grid.setSpacing(8)
    scroll.setWidget(grid_widget)

    heal_inputs: dict[str, QLineEdit] = {}
    hp_labels: dict[str, QLabel] = {}
    for row, char in enumerate(players):
        name_lbl = QLabel(char["name"])
        hp_lbl = QLabel(f"{char['hp']}/{char['max_hp']} HP")
        hp_lbl.setObjectName("secondary")
        heal_input = QLineEdit()
        heal_input.setPlaceholderText("Heal amount…")
        grid.addWidget(name_lbl, row, 0)
        grid.addWidget(hp_lbl, row, 1)
        grid.addWidget(heal_input, row, 2)
        heal_inputs[char["name"]] = heal_input
        hp_labels[char["name"]] = hp_lbl

    def do_apply():
        for char in players:
            text = heal_inputs[char["name"]].text().strip()
            if not text:
                continue
            try:
                heal = int(text)
            except ValueError:
                continue
            if heal <= 0:
                continue
            was_downed = app._char_death_state(char) != "alive"
            pre_hp = char["hp"]
            char["hp"] = min(char["hp"] + heal, char["max_hp"])
            actual_heal = char["hp"] - pre_hp
            heal_value = {"heal": actual_heal, "source_name": None, "target_name": char["name"]}
            app.history.append((Action.HEAL, heal_value))
            app._log_event(
                f"{char['name']} heals {actual_heal} HP (short rest)",
                character=char["name"],
                action=Action.HEAL,
                value=heal_value,
            )
            if was_downed and char["hp"] > 0:
                char["death_saves_fail"] = 0
                char["death_saves_success"] = 0
            app._apply_bloodied_condition(char)
            hp_labels[char["name"]].setText(f"{char['hp']}/{char['max_hp']} HP")
            heal_inputs[char["name"]].clear()

    btn_row = QHBoxLayout()
    apply_btn = QPushButton("Apply Short Rest")
    apply_btn.clicked.connect(do_apply)
    close_btn = QPushButton("Close")
    close_btn.clicked.connect(dlg.accept)
    btn_row.addWidget(apply_btn)
    btn_row.addWidget(close_btn)
    outer.addLayout(btn_row)

    dlg.exec()
