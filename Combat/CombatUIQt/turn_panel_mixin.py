"""The turn column beside the cards, and what a monster's turn runs on: who's
up and next, what to remember as the turn starts, and the source's stat-block
actions as buttons that roll and fill in the Damage field, so a monster's turn
needs no dialog. Legendary actions, recharges and per-day uses are counted in
the combatant's public keys, so undo and a saved fight keep them."""

import random
from textwrap import shorten

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .monster_actions import (
    LEGENDARY_ACTIONS_PER_ROUND,
    MonsterAction,
    first_number,
    legendary_actions_left,
    legendary_resistances_left,
    monster_actions,
    roll_dice,
    start_of_turn_traits,
)
from .player_view import PlayerViewWindow, player_view_rows
from .state import CombatWindowState
from .turns_mixin import unit_label
from .undo import undoable

_TURN_PANEL_WIDTH = 330
_ACTION_RESULT_HEIGHT = 84  # fixed, so a result never moves the buttons
_RIDER_LENGTH = 130
# Stands in for a damage type the monster chooses. It isn't one, so Enter stops
# until the GM types over it, where a blank would take another part's type.
_CHOOSE_A_TYPE = "type"


def _is_spent(char: dict, action: MonsterAction) -> bool:
    return char.get("spent_abilities", {}).get(action.name, 0) >= (action.per_day or 1)


class TurnPanelMixin(CombatWindowState):
    """Mixin for the turn column, monster turns and the players' screen."""

    # The players' screen, while it's open.
    _player_view: PlayerViewWindow | None

    # ── Building and refreshing ─────────────────────────────────────────────

    def _build_turn_panel(self) -> QWidget:
        content = QFrame()
        content.setObjectName("turnPanel")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self._turn_now_label = QLabel("")
        self._turn_now_label.setObjectName("turnNowLabel")
        self._turn_now_label.setWordWrap(True)
        layout.addWidget(self._turn_now_label)
        self._turn_next_label = QLabel("")
        self._turn_next_label.setObjectName("secondary")
        self._turn_next_label.setWordWrap(True)
        layout.addWidget(self._turn_next_label)

        self._turn_reminders_label = QLabel("")
        self._turn_reminders_label.setObjectName("statusLabel")
        self._turn_reminders_label.setWordWrap(True)
        layout.addWidget(self._turn_reminders_label)

        self._legendary_ready_label = QLabel("")
        self._legendary_ready_label.setObjectName("secondary")
        self._legendary_ready_label.setWordWrap(True)
        layout.addWidget(self._legendary_ready_label)

        layout.addWidget(self._make_divider())

        self._action_result_label = QLabel("")
        self._action_result_label.setObjectName("actionResultLabel")
        self._action_result_label.setWordWrap(True)
        self._action_result_label.setFixedHeight(_ACTION_RESULT_HEIGHT)
        self._action_result_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._action_result_label)

        self._actions_box = QWidget()
        self._actions_layout = QVBoxLayout(self._actions_box)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(4)
        layout.addWidget(self._actions_box)
        layout.addStretch()

        self._turn_panel = QScrollArea()
        self._turn_panel.setObjectName("controlPanelScroll")
        self._turn_panel.setWidget(content)
        self._turn_panel.setWidgetResizable(True)
        self._turn_panel.setFrameShape(QFrame.Shape.NoFrame)
        self._turn_panel.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._turn_panel.setFixedWidth(_TURN_PANEL_WIDTH)
        self._turn_panel.hide()
        return self._turn_panel

    def _refresh_views(self):
        """Bring the turn column and the players' screen up to date."""
        if self.phase == "COMBAT" and self.initiative_order:
            self._refresh_turn_labels()
            self._refresh_action_buttons()
            self._refresh_next_button()
        self._refresh_player_view()

    def _refresh_turn_labels(self):
        self._turn_now_label.setText(f"Now: {self._current_turn_label()}")
        upcoming = [unit_label(unit) for unit in self._upcoming_turns()[:2]]
        self._turn_next_label.setText(
            "Next: " + ", then ".join(upcoming) if upcoming else ""
        )
        self._turn_reminders_label.setText("\n".join(self._turn_reminders))
        ready = [
            f"{c['name']} ({legendary_actions_left(c)})"
            for c in self.characters
            if legendary_actions_left(c) > 0
            and self._char_death_state(c) != "dead"
            and not any(c is active for active in self._current_turn_group())
        ]
        self._legendary_ready_label.setText(
            f"Legendary actions ready: {', '.join(ready)}" if ready else ""
        )

    def _current_turn_label(self) -> str:
        return unit_label(self._current_turn_group())

    def _refresh_action_buttons(self):
        """The stat-block actions of the source, or of whoever's turn it is."""
        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        char = self.selected_character or self._current_turn_character()
        sections = monster_actions(char) if char is not None else []
        if char is None or not sections:
            return
        self._actions_layout.addWidget(self._section_header(char["name"]))
        if char.get("legendary_resistances"):
            self._actions_layout.addWidget(self._legendary_resistance_button(char))
        for title, actions in sections:
            if title == "Legendary Actions":
                title = f"{title} ({legendary_actions_left(char)} left)"
            self._actions_layout.addWidget(self._section_header(title))
            for action in actions:
                self._actions_layout.addWidget(self._action_row(char, action))

    def _legendary_resistance_button(self, char: dict) -> QPushButton:
        left = legendary_resistances_left(char)
        button = QPushButton(f"Use Legendary Resistance ({left} left)")
        button.setEnabled(left > 0)
        button.clicked.connect(lambda: self._use_legendary_resistance(char))
        return button

    def _action_row(self, char: dict, action: MonsterAction) -> QWidget:
        """A button that uses the action, or plain text for one with nothing
        to roll or count, like Multiattack."""
        if not (action.is_rollable or action.is_limited or action.legendary_cost):
            label = QLabel(f"{action.name}: {action.description}")
            label.setObjectName("secondary")
            label.setWordWrap(True)
            return label

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        spent = _is_spent(char, action)
        name = f"{action.name} (spent)" if spent else action.name
        button = QPushButton(f"{name}\n{action.summary}" if action.summary else name)
        button.setObjectName("monsterActionBtn")
        button.setToolTip(action.description)
        button.setEnabled(not spent)
        button.clicked.connect(lambda: self._use_monster_action(char, action))
        layout.addWidget(button, stretch=1)
        if spent or char.get("spent_abilities", {}).get(action.name):
            restore = QPushButton("↺")
            restore.setFixedWidth(28)
            restore.setToolTip(f"Make {action.name} ready again")
            restore.clicked.connect(lambda: self._restore_ability(char, action))
            layout.addWidget(restore)
        return row

    # ── Using actions ───────────────────────────────────────────────────────

    @undoable
    def _use_monster_action(self, char: dict, action: MonsterAction):
        """Count the action's use, if it's one that's counted, and roll it."""
        if action.is_limited and _is_spent(char, action):
            self._show_status(f"{action.name} isn't ready.")
            return
        if action.legendary_cost:
            left = legendary_actions_left(char)
            if left < action.legendary_cost:
                self._show_status(f"{char['name']} has {left} legendary actions left.")
                return
            char["legendary_actions_left"] = left - action.legendary_cost
        if action.is_limited:
            spent = char.setdefault("spent_abilities", {})
            spent[action.name] = spent.get(action.name, 0) + 1
        if action.is_limited or action.legendary_cost:
            self._log_event(
                f"{char['name']} uses {action.name}", character=char["name"]
            )
            self._rebuild_card(char)
        self._roll_action(action)
        self._refresh_views()

    def _roll_action(self, action: MonsterAction):
        """Roll the attack against the target, then its damage into the Damage
        field, where Enter applies it (and a miss leaves nothing to apply)."""
        result = [action.name]
        critical = False
        hit: bool | None = None
        if action.to_hit is not None:
            d20 = self._roll_d20_for_attack()
            total = d20 + action.to_hit
            critical = d20 == 20
            result.append(f"rolled {total} ({d20}{action.to_hit:+d})")
            hit = self._attack_hits(d20, total)
            if len(self.target_characters) == 1:
                armor = self.target_characters[0]["ac"]
                result.append(f"vs AC {first_number(armor)}")
            if critical:
                result.append("CRITICAL HIT")
            elif hit is not None:
                result.append("HIT" if hit else "MISS")
        if action.save_ability is not None:
            result.append(f"DC {action.save_dc or '?'} {action.save_ability} save")
            if action.half_on_save:
                result.append("half on success")
        text = ": ".join(result[:1] + [" ".join(result[1:])]) if result[1:] else ""
        if hit is not False and action.rider:
            rider = shorten(action.rider, _RIDER_LENGTH, placeholder="...")
            text = f"{text}\nAlso: {rider}" if text else f"{action.name}: {rider}"
        self._action_result_label.setText(text)
        self._action_result_label.setToolTip(action.description)

        self.damage_input.clear()
        self._rolled_damage_text = ""
        if hit is False or not action.damage:
            return
        rolled = " + ".join(
            f"{roll_dice(roll.dice, critical)} {roll.damage_type or _CHOOSE_A_TYPE}"
            for roll in action.damage
        )
        self.damage_input.setText(rolled)
        self._rolled_damage_text = rolled
        self._focus_damage_input()
        word = rolled.find(_CHOOSE_A_TYPE)
        if word >= 0:
            self.damage_input.setSelection(word, len(_CHOOSE_A_TYPE))

    def _roll_d20_for_attack(self) -> int:
        """A d20 under the d20 Roll section's Advantage or Disadvantage."""
        first, second = random.randint(1, 20), random.randint(1, 20)
        mode = self.roll_mode_combo.currentText()
        if mode == "Advantage":
            return max(first, second)
        return min(first, second) if mode == "Disadvantage" else first

    def _attack_hits(self, d20: int, total: int) -> bool | None:
        """Whether the attack hits the one target; a 20 always does and a 1
        never. None when it can't be told: no target, or several."""
        if d20 == 20:
            return True
        if d20 == 1:
            return False
        if len(self.target_characters) != 1:
            return None
        armor = first_number(self.target_characters[0]["ac"])
        return None if armor is None else total >= armor

    @undoable
    def _use_legendary_resistance(self, char: dict):
        left = legendary_resistances_left(char)
        if left <= 0:
            return
        char["legendary_resistances_left"] = left - 1
        self._log_event(
            f"{char['name']} uses Legendary Resistance ({left - 1} left)",
            character=char["name"],
        )
        self._rebuild_card(char)
        self._refresh_views()

    @undoable
    def _restore_ability(self, char: dict, action: MonsterAction):
        """Give back one use, for a recharge rolled at the table or a use the
        GM takes back."""
        spent = char.get("spent_abilities", {})
        if spent.get(action.name, 0) > 1:
            spent[action.name] -= 1
        else:
            spent.pop(action.name, None)
        self._log_event(f"{char['name']}'s {action.name} is ready again")
        self._rebuild_card(char)
        self._refresh_views()

    # ── Turns starting ──────────────────────────────────────────────────────

    def _start_monster_turn(self, char: dict):
        """What the rules do by themselves as char's turn starts: it regains
        its legendary actions and rolls to recharge what it has spent. Notes
        what happened in _turn_start_notes."""
        name = f"{char['name']}: " if len(self._current_turn_group()) > 1 else ""
        if char.get("legendary_actions_left", LEGENDARY_ACTIONS_PER_ROUND) < (
            LEGENDARY_ACTIONS_PER_ROUND
        ):
            char["legendary_actions_left"] = LEGENDARY_ACTIONS_PER_ROUND
            self._turn_start_notes.append(
                f"{name}Legendary actions back to {LEGENDARY_ACTIONS_PER_ROUND}"
            )
        spent = char.get("spent_abilities", {})
        for _, actions in monster_actions(char):
            for action in actions:
                if action.recharge_on is None or action.name not in spent:
                    continue
                roll = self._recharge_roll(char, action)
                if roll >= action.recharge_on:
                    del spent[action.name]
                    text = f"{action.name} recharged (rolled {roll})"
                    self._log_event(f"{char['name']}'s {text}", character=char["name"])
                else:
                    text = f"{action.name} not recharged (rolled {roll})"
                self._turn_start_notes.append(f"{name}{text}")

    def _recharge_roll(self, char: dict, action: MonsterAction) -> int:
        """The d6 for action on this turn. Undoing the turn and pressing Next
        again gets the same one, so a failed recharge has no second chance.
        It's in an underscore key so undo leaves it alone."""
        rolls = char.setdefault("_recharge_rolls", {})
        turn = (self.round_number, self.current_turn_idx, action.name)
        if turn not in rolls:
            rolls[turn] = random.randint(1, 6)
        return rolls[turn]

    def _take_turn_reminders(self):
        """What to remember this turn: what starting it did (once), and what's
        true of whoever's turn it is. It's fixed for the turn, so the buttons
        below it stay put while the turn is played."""
        reminders = list(self._turn_start_notes)
        self._turn_start_notes = []
        seen = set()
        for char in self._current_turn_group():
            if self._char_death_state(char) == "dying":
                reminders.append(f"{char['name']} is dying: death save")
            for _ in char.get("concentration_checks", []):
                reminders.append(f"{char['name']}: Concentration save to make")
            for name, sentence in start_of_turn_traits(char):
                if name not in seen and self._char_death_state(char) != "dead":
                    seen.add(name)
                    reminders.append(f"{name}: {sentence}")
        self._turn_reminders = reminders

    # ── The players' screen ─────────────────────────────────────────────────

    def _toggle_player_view(self):
        """Open the players' screen, or close it if it's open."""
        if self._player_view is not None:
            self._player_view.close()
            return
        self._player_view = PlayerViewWindow(on_close=self._player_view_closed)
        self._refresh_player_view()
        self._player_view.show_on_spare_screen(self._window)

    def _player_view_closed(self):
        self._player_view = None

    def _refresh_player_view(self):
        view = self._player_view
        if view is None:
            return
        if self.phase != "COMBAT" or not self.initiative_order:
            view.show_rows("Waiting for the fight to start", [])
            return
        view.show_rows(
            f"Round {self.round_number}",
            player_view_rows(
                self.initiative_order,
                self._current_turn_group(),
                self._upcoming_turns(),
                self._char_death_state,
            ),
        )
