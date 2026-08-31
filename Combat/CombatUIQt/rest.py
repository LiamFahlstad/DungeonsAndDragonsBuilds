"""Long-rest checkpointing and the short-rest healing window.

A long rest empties the current player log in place: the tracked party's
character sheets are always built at full HP, full spell slots, and zero
feature uses spent, so an empty log already replays to a fully rested party
on the next run — no manual restoration needed. Before it's cleared, the
log's full session history is archived to a new, timestamped sibling path
so nothing is lost.

A short rest reuses CombatAppQt to reconstruct the party's current state (it
already knows how to replay a player log onto freshly-built characters —
see LoggingMixin._init_player_log) without ever calling `.run()`, and opens
a small standalone window — not the main combat window — to manually heal
each player and regain any short-rest-cadence feature uses (e.g. Channel
Divinity), appending the result to the same log.
"""

import json
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
from CharacterContent.Features.Core.BaseFeatures import RegainedOn
from Combat.Definitions import Action

from .app import CombatAppQt
from .styles import QSS

SHORT_REST_CADENCES = {RegainedOn.SHORT_REST, RegainedOn.SHORT_OR_LONG_REST}


def _rest_checkpoint_path(player_log_path: str, suffix: str) -> str:
    """A new, timestamped sibling path next to player_log_path, e.g.
    'main_party.json' -> 'main_party_long_rest_20260831_071200.json'."""
    src = Path(player_log_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(src.with_name(f"{src.stem}_{suffix}_{timestamp}{src.suffix}"))


def _build_party_state(player_log_path: str) -> CombatAppQt:
    """Headlessly replay player_log_path onto a fresh CombatAppQt instance
    (no window, no event loop — .run() is never called)."""
    players = CombatantGroups.get_players_group()
    return CombatAppQt(
        combatants=[],
        character_sheets=players,
        player_log_path=player_log_path,
        scenario_name=None,
    )


def _restore_feature_uses(app: CombatAppQt, char: dict, cadences: set, note: str):
    stat_block = char.get("_stat_block")
    if stat_block is None:
        return
    used = char.setdefault("feature_uses_used", {})
    for feature in char.get("_feature_objects", []):
        if feature.uses is None:
            continue
        if feature.regained_on(stat_block) not in cadences:
            continue
        for _ in range(used.get(feature.name, 0)):
            used[feature.name] = max(used.get(feature.name, 0) - 1, 0)
            app.history.append((Action.REGAIN_FEATURE_CHARGE, feature.name))
            app._log_event(
                f"{char['name']} regains a use of {feature.name} ({note})",
                character=char["name"],
                action=Action.REGAIN_FEATURE_CHARGE,
                value=feature.name,
            )


def apply_long_rest(player_log_path: str) -> str:
    """Archive the current player log's full session history to a new,
    timestamped sibling path, then empty the current log in place and
    return the backup path. An empty log already replays to a fully rested
    party — full HP, full spell slots, zero feature uses spent — since
    character sheets are always built that way. Never opens a window."""
    src = Path(player_log_path)
    backup_path = Path(_rest_checkpoint_path(player_log_path, "long_rest"))
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        backup_path.write_text(src.read_text())
    else:
        backup_path.write_text(json.dumps({"sessions": []}, indent=2))
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(json.dumps({"sessions": []}, indent=2))
    return str(backup_path)


def run_short_rest(player_log_path: str):
    """Open a small standalone healing window (not the main combat window)
    letting each tracked player be healed a manually-entered amount, and
    automatically regain any short-rest-cadence feature uses. Heals and
    regains are appended to the same player log passed in — no new file is
    created."""
    app = _build_party_state(player_log_path)
    players = [c for c in app.characters if c.get("_is_player")]
    for char in players:
        _restore_feature_uses(app, char, SHORT_REST_CADENCES, note="short rest")

    qapp = QApplication.instance() or QApplication(sys.argv)
    qapp.setStyleSheet(QSS)

    dlg = QDialog()
    dlg.setWindowTitle(f"Short Rest — {Path(player_log_path).name}")
    dlg.setMinimumSize(420, 120 + 40 * len(players))
    dlg.setStyleSheet(QSS)

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(14, 14, 14, 14)
    outer.setSpacing(10)

    info_lbl = QLabel(
        "Enter a heal amount for each player who spends Hit Dice, then Apply."
    )
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
            heal_value = {
                "heal": actual_heal,
                "source_name": None,
                "target_name": char["name"],
            }
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
