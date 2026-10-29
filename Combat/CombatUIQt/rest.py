"""Long rests and the short-rest healing window.

A long rest is one line in the party's player log (Combat/PlayerLog.py): the
party's state is replayed only from what came after the last one, onto
character sheets that are always built at full HP, full spell slots and zero
feature uses spent, so the party is fully rested on the next run. Nothing
before it is deleted; the statistics still count it.

A short rest reuses CombatAppQt to reconstruct the party's current state
without ever calling `.run()`, and opens a small standalone window — not the
main combat window — to manually heal each player and regain any
short-rest-cadence feature uses (e.g. Channel Divinity). Those events are
recorded on the short rest's own line in the player log (no encounter log is
written between encounters).
"""

import sys

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

import Combat.PlayerLog as PlayerLog
from Combat.Campaign import Campaign
from Model.Content.Feature import RegainedOn
from Combat.Definitions import Action
from Core.Definitions import Condition

from .app import CombatAppQt
from .styles import QSS

SHORT_REST_CADENCES = {RegainedOn.SHORT_REST, RegainedOn.SHORT_OR_LONG_REST}


def _build_party_state(player_log_path: str, campaign: Campaign) -> CombatAppQt:
    """Headlessly replay player_log_path onto a fresh CombatAppQt instance
    (no window, no event loop — .run() is never called)."""
    return CombatAppQt(
        combatants=[],
        character_sheets=campaign.players(),
        combat_log_dir=campaign.combat_log_dir,
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
            app._log_event(
                f"{char['name']} regains a use of {feature.name} ({note})",
                character=char["name"],
                action=Action.REGAIN_FEATURE_CHARGE,
                value=feature.name,
            )


def apply_long_rest(player_log_path: str):
    """Record a long rest in the player log: from the next run on, the party
    is fully rested (see the module docstring). Never opens a window."""
    PlayerLog.append_long_rest(player_log_path)


def run_short_rest(player_log_path: str, campaign: Campaign):
    """Open the short-rest window on its own (not the main combat window),
    for `--rest short`. Heals and regains are recorded on the short rest's
    line in the player log, once anything is applied."""
    app = _build_party_state(player_log_path, campaign)
    qapp = QApplication.instance()
    if qapp is None:
        qapp = QApplication(sys.argv)
    assert isinstance(qapp, QApplication)
    qapp.setStyleSheet(QSS)
    app._record_short_rest(lambda: short_rest_dialog(app).exec())


def short_rest_dialog(app: CombatAppQt, parent: QWidget | None = None) -> QDialog:
    """A short rest for the tracked party in `app` (inside
    app._record_short_rest, which records what it logs): every
    short-rest-cadence feature use comes back right away, and the
    window built here lets each player be healed a manually-entered amount
    (Hit Dice spent). Returned unopened; the caller exec()s it."""
    players = [c for c in app.characters if c.get("_is_player")]
    for char in players:
        _restore_feature_uses(app, char, SHORT_REST_CADENCES, note="short rest")

    dlg = QDialog(parent)
    title = app.player_log_file.name if app.player_log_file else "party"
    dlg.setWindowTitle(f"Short Rest — {title}")
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
            death_state = app._char_death_state(char)
            # A dead creature can't regain Hit Points until it is revived.
            if death_state == "dead":
                continue
            was_downed = death_state != "alive"
            pre_hp = char["hp"]
            char["hp"] = min(char["hp"] + heal, char["max_hp"])
            actual_heal = char["hp"] - pre_hp
            heal_value = {
                "heal": actual_heal,
                "source_name": None,
                "target_name": char["name"],
            }
            app._log_event(
                f"{char['name']} heals {actual_heal} HP (short rest)",
                character=char["name"],
                action=Action.HEAL,
                value=heal_value,
            )
            if was_downed and char["hp"] > 0:
                char["death_saves_fail"] = 0
                char["death_saves_success"] = 0
                app._remove_condition_from(char, Condition.UNCONSCIOUS.value)
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
    return dlg
