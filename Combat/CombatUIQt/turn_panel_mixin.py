"""The turn column beside the cards, and what a monster's turn runs on: who's
up and next, what to remember as the turn starts, and the source's stat-block
actions as buttons that roll and fill in the Damage field, so a monster's turn
needs no dialog. Legendary actions, recharges and per-day uses are counted in
the combatant's public keys, so undo and a saved fight keep them. The encounter
log fills the bottom of the column, with its own scrollbar. Between encounters
the column says there are no turns, and shows the between-encounters log."""

import random
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from textwrap import shorten

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

import Combat.PlayerLog as PlayerLog
from Model.Content.CombatTriggers import TriggerAim
from Combat.Effects.modifiers import attack_plan, hit_notes, hit_plan, hit_point_maximum
from Combat.Effects.triggers import (
    AttackOutcome,
    DropOutcome,
    attack_roll_firings,
    Firing,
    HitFiring,
    Outcome,
    PendingAttack,
    TriggerChoice,
    TriggerMode,
    drop_firings,
    firings,
    hit_by_firings,
    outcome_firings,
    still_hits,
)

from .attack_rolls import armor_bonus, armor_in_use
from .log_feed import LogFeed
from .monster_actions import (
    DIE,
    LEGENDARY_ACTIONS_PER_ROUND,
    MonsterAction,
    first_number,
    is_spent,
    legendary_actions_left,
    legendary_resistances_left,
    monster_actions,
    roll_dice,
    start_of_turn_traits,
)
from .player_server import PLAYER_PORT
from .resources import legendary_resistance_lack, monster_action_lack
from .effect_options import trigger_option, triggered_rows
from .saves import (
    ATTACK_ROLL,
    HEALING,
    TEMP_HP,
    EffectOption,
    roll_bonuses,
    roll_extra_damage,
)
from .trigger_prompt import ask_triggers
from .player_view import (
    PlayerViewRow,
    PlayerViewWindow,
    _player_names,
    _seen,
    player_view_rows,
)
from .state import CombatWindowState
from .turns_mixin import unit_label
from .undo import undoable

_TURN_PANEL_WIDTH = 330
_ACTION_RESULT_HEIGHT = 84  # fixed, so a result never moves the buttons
_RIDER_LENGTH = 130
# Stands in for a damage type the monster chooses. It isn't one, so Enter stops
# until the GM types over it, where a blank would take another part's type.
_CHOOSE_A_TYPE = "type"


def _applies_nothing(option: EffectOption) -> bool:
    """Whether a picker row puts nothing on a creature the simulator can show:
    no roll, amount, condition, uses regained or condition ended (Push)."""
    return not (
        option.rolls
        or option.condition
        or option.ability
        or option.bonus is not None
        or option.regains
        or option.drops_to
        or option.ends_conditions
    )


class TurnPanelMixin(CombatWindowState):
    """Mixin for the turn column, monster turns and the players' screen."""

    # The players' screen, while it's open.
    _player_view: PlayerViewWindow | None
    # The heading above the log at the bottom of the column.
    _log_box_header: QLabel
    # The buttons for the turn's prompts (_refresh_turn_prompts).
    _turn_prompts_box: QWidget
    _turn_prompts_layout: QVBoxLayout
    # The once-per-turn triggered rows used, as (owner, row) names, and the
    # turn they were used in, (round, turn index). Not undone: undoing one
    # such use leaves it counted for the turn.
    _trigger_uses: tuple[tuple[int, int] | None, frozenset[tuple[str, str]]] = (
        None,
        frozenset(),
    )

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

        self._turn_prompts_box = QWidget()
        self._turn_prompts_layout = QVBoxLayout(self._turn_prompts_box)
        self._turn_prompts_layout.setContentsMargins(0, 0, 0, 0)
        self._turn_prompts_layout.setSpacing(4)
        layout.addWidget(self._turn_prompts_box)

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

        turn_scroll = QScrollArea()
        turn_scroll.setObjectName("controlPanelScroll")
        turn_scroll.setWidget(content)
        turn_scroll.setWidgetResizable(True)
        turn_scroll.setFrameShape(QFrame.Shape.NoFrame)
        turn_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # A splitter, as a stat block with many actions needs more room than
        # a fight that wants its log.
        self._turn_panel = QSplitter(Qt.Orientation.Vertical)
        self._turn_panel.setObjectName("turnSplitter")
        self._turn_panel.setChildrenCollapsible(False)
        self._turn_panel.addWidget(turn_scroll)
        self._turn_panel.addWidget(self._build_log_box())
        self._turn_panel.setFixedWidth(_TURN_PANEL_WIDTH)
        self._turn_panel.hide()
        return self._turn_panel

    def _build_log_box(self) -> QWidget:
        box = QFrame()
        box.setObjectName("turnPanel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 6, 10, 10)
        layout.setSpacing(4)
        self._log_box_header = self._section_header("Encounter Log")
        layout.addWidget(self._log_box_header)
        self._log_feed = LogFeed()
        layout.addWidget(self._log_feed)
        return box

    def _refresh_views(self):
        """Bring the turn column, the players' screen and the player link up
        to date."""
        between = self.phase == "PARTY" and self.log_file is not None
        self._log_box_header.setText("Log" if between else "Encounter Log")
        if self.phase == "COMBAT" and self.initiative_order:
            self._refresh_turn_labels()
            self._refresh_action_buttons()
            self._refresh_next_button()
            self._log_feed.show_log(self._read_log())
        elif between:
            self._refresh_between_encounters_labels()
            self._refresh_action_buttons()
            self._log_feed.show_log(self._read_log())
        self._refresh_player_view()

    def _refresh_between_encounters_labels(self):
        """The top of the column between encounters, in place of whose turn
        it is: there are none, and where what's done goes."""
        assert self.log_file is not None
        self._turn_now_label.setText(PlayerLog.BETWEEN_ENCOUNTERS_TITLE)
        self._turn_next_label.setText(
            "No turns: spells, heals, damage and conditions are logged to "
            f"{PlayerLog.BETWEEN_ENCOUNTERS_DIR}/{self.log_file.name} and count "
            "for the party like a fight's. Loading an encounter or resting ends "
            "this stretch."
        )
        self._turn_reminders_label.setText("")
        self._turn_prompts = []
        self._hit_prompts = ()
        self._refresh_turn_prompts()
        self._legendary_ready_label.setText("")

    def _hidden_turn_note(self) -> str:
        """During the turn of monsters the players can't see, what the players'
        screen shows instead: it keeps "now" on the last turn they could see,
        so as not to give the hidden ones away (player_view_rows)."""
        turn = self._current_turn_group()
        players = _player_names(self.characters)
        if not turn or any(_seen(c, players) for c in turn):
            return ""
        shown = next(
            (row.name for row in self._player_view_content()[1] if row.turn == "now"),
            None,
        )
        if shown is None:
            return "  (hidden from players)"
        return f"  (hidden: players see {shown} as now)"

    def _refresh_turn_labels(self):
        self._turn_now_label.setText(
            f"Now: {self._current_turn_label()}{self._hidden_turn_note()}"
        )
        upcoming = [unit_label(unit) for unit in self._upcoming_turns()[:2]]
        self._turn_next_label.setText(
            "Next: " + ", then ".join(upcoming) if upcoming else ""
        )
        self._turn_reminders_label.setText("\n".join(self._turn_reminders))
        self._refresh_turn_prompts()
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
        # With none left, it asks whether to anyway.
        button.clicked.connect(lambda: self._use_legendary_resistance(char, ask=True))
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
        spent = is_spent(char, action)
        name = f"{action.name} (spent)" if spent else action.name
        button = QPushButton(f"{name}\n{action.summary}" if action.summary else name)
        button.setObjectName("monsterActionBtn")
        button.setToolTip(action.description)
        # A spent one still works: _spend_monster_action asks first.
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
        if self._spend_monster_action(char, action) is None:
            return
        self._roll_action(action, char)
        self._refresh_views()

    def _spend_monster_action(
        self, char: dict, action: MonsterAction, *, ask: bool = True
    ) -> bool | None:
        """Count a use of the action, if it's one that's counted: a recharge or
        per-day use, or the legendary actions it costs. Shared with the Custom
        Effect dialog. When it's spent or costs more legendary actions than are
        left, the GM is asked whether to use it anyway, unless the caller has
        asked already (ask=False). Returns whether it logged the use, or None
        if the GM said no."""
        lack = monster_action_lack(char, action)
        if ask and not self._go_ahead_anyway(char, f"Use {action.name}", [lack]):
            return None
        if action.legendary_cost:
            left = legendary_actions_left(char)
            char["legendary_actions_left"] = max(left - action.legendary_cost, 0)
        if action.is_limited:
            spent = char.setdefault("spent_abilities", {})
            spent[action.name] = spent.get(action.name, 0) + 1
        if not (action.is_limited or action.legendary_cost):
            return False
        self._log_event(f"{char['name']} uses {action.name}", character=char["name"])
        self._rebuild_card(char)
        return True

    def _roll_action(self, action: MonsterAction, char: dict | None = None):
        """Roll char's attack against the target, then its damage into the
        Damage field, where Enter applies it (and a miss leaves nothing to
        apply). Char's conditions count in the roll (Combat/Effects), and with
        one target its conditions too, and its cover and modifiers in its AC."""
        result = [action.name]
        critical = False
        total: int | None = None
        hit: bool | None = None
        notes: tuple[str, ...] = ()
        if action.to_hit is not None:
            mode = self.roll_mode_combo.currentText()
            target = (
                self.target_characters[0] if len(self.target_characters) == 1 else None
            )
            # What others answer the roll with before it's made (Warding
            # Flare), then, with no target or several, the attacker's own
            # still count.
            self._before_attack_roll(char, target)
            plan = attack_plan(char, target, mode)
            d20 = self._roll_d20_for_attack(plan.mode)
            # What its modifiers add (Bless's 1d4), rolled after the d20.
            added, bonus_notes = roll_bonuses(plan)
            notes = (*plan.notes, *bonus_notes)
            total = d20 + action.to_hit + added
            critical = d20 == 20
            extra = f"{added:+d}" if plan.bonuses else ""
            result.append(f"rolled {total} ({d20}{action.to_hit:+d}{extra})")
            hit = self._attack_hits(d20, total)
            armor = self._target_armor()
            if armor is not None:
                result.append(f"vs AC {armor}")
            if critical:
                result.append("CRITICAL HIT")
            elif hit is not None:
                result.append("HIT" if hit else "MISS")
            if target is not None and hit is not False:
                notes = (*notes, *hit_notes(target))
            # The roll's made: what counted for it once is used up (Sap).
            self._use_up_badges(char, target)
        if action.save_ability is not None:
            result.append(f"DC {action.save_dc or '?'} {action.save_ability} save")
            if action.half_on_save:
                result.append("half on success")
        text = ": ".join(result[:1] + [" ".join(result[1:])]) if result[1:] else ""
        if notes:
            text = f"{text}\n{'; '.join(notes)}"
        if hit is not False and action.rider:
            rider = shorten(action.rider, _RIDER_LENGTH, placeholder="...")
            text = f"{text}\nAlso: {rider}" if text else f"{action.name}: {rider}"
        self._action_result_label.setText(text)
        self._action_result_label.setToolTip(action.description)

        self.attack_roll_input.clear()  # this action has rolled its own
        self.damage_input.clear()
        self._rolled_damage_text = ""
        self._rolled_attack = None
        if hit is False and char is not None and len(self.target_characters) == 1:
            self._after_attack(
                AttackOutcome(char, self.target_characters[0], False, row=action.name)
            )
        if hit is False or not action.damage:
            return
        if action.to_hit is not None and char is not None:
            # Enter in the Damage field deals it as this action's hit, so
            # what the hit triggers knows which row hit (`after=`).
            self._rolled_attack = PendingAttack(
                char, critical, row=action.name, total=None if critical else total
            )
        rolled = " + ".join(
            f"{roll_dice(roll.dice, critical)} {roll.damage_type or _CHOOSE_A_TYPE}"
            for roll in action.damage
        )
        if action.to_hit is not None:
            # What comes with its hit (Hunter's Mark on its caster's), rolled
            # after its own dice; from a target's effect only with one target.
            target = (
                self.target_characters[0] if len(self.target_characters) == 1 else None
            )
            plan = hit_plan(char, target, None)
            extra, lines = roll_extra_damage(plan, critical)
            rolled += "".join(f" + {amount} {kind}" for amount, kind in extra)
            if lines or plan.notes:
                self._action_result_label.setText(
                    f"{text}\n{'; '.join((*lines, *plan.notes))}"
                )
        self.damage_input.setText(rolled)
        self._rolled_damage_text = rolled
        self._focus_damage_input()
        word = rolled.find(_CHOOSE_A_TYPE)
        if word >= 0:
            self.damage_input.setSelection(word, len(_CHOOSE_A_TYPE))

    def _roll_d20_for_attack(self, mode: str) -> int:
        """A d20 with Advantage or Disadvantage, or neither ("Neutral")."""
        first, second = random.randint(1, 20), random.randint(1, 20)
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
        armor = self._target_armor()
        return None if armor is None else total >= armor

    def _target_armor(self) -> int | None:
        """The one target's AC with its cover and modifiers in it; None with
        no target, several, or one with no AC."""
        if len(self.target_characters) != 1:
            return None
        target = self.target_characters[0]
        armor = first_number(target["ac"])
        return None if armor is None else armor + armor_bonus(target)

    @undoable
    def _use_legendary_resistance(self, char: dict, *, ask: bool = False):
        """Spend one of char's Legendary Resistances. With none left, it's
        used only if `ask` (the turn column's button) and the GM says yes."""
        left = legendary_resistances_left(char)
        if left <= 0 and not (
            ask
            and self._go_ahead_anyway(
                char, "Use Legendary Resistance", [legendary_resistance_lack(char)]
            )
        ):
            return
        left = max(left - 1, 0)
        char["legendary_resistances_left"] = left
        self._log_event(
            f"{char['name']} uses Legendary Resistance ({left} left)",
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
                if not self.settings.monsters_roll_turn_dice:
                    # Rolled at the table: ↺ makes it ready (_restore_ability).
                    self._turn_start_notes.append(
                        f"{name}{action.name}: roll its recharge (a d6 of"
                        f" {action.recharge_on} or more), ↺ if it comes back"
                    )
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
        self._hit_prompts = ()
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
        self._turn_prompts = list(self._turn_start_prompts)
        self._turn_start_prompts = []

    # ── Triggers ────────────────────────────────────────────────────────────

    def _turn_triggers(self, turn: list[dict], kind: type):
        """What the badges in the fight do as the turn of `turn` starts or
        ends (`kind`: AtTurnStart or AtTurnEnd; Combat/Effects/triggers.py).
        Hit Points one gives with nothing to decide are given here (Heroism's
        Temporary Hit Points), and noted for the turn; anything else is a
        prompt in the turn column for the GM."""
        for firing in firings(
            self.characters, turn, kind, self._find_character_by_name
        ):
            if self._char_death_state(firing.target) == "dead":
                continue
            if firing.is_prompt or not self._give_trigger_hit_points(firing):
                self._turn_start_prompts.append(firing)

    def _give_trigger_hit_points(self, firing: Firing) -> bool:
        """Give the Hit Points firing's effect gives, if that's all it does
        (no roll, no damage, an amount known). Returns whether it did. Dice a
        player rolls (a player's badge), or a monster's with the setting
        monsters_roll_turn_dice off, are left to the turn-column button,
        whose dialog takes the total rolled at the table (plan step 8.6)."""
        caster = self._find_character_by_name(firing.caster) if firing.caster else None
        option = trigger_option(caster, firing.source, firing.trigger.effect)
        if (
            option is None
            or option.ability is not None
            or option.roll == ATTACK_ROLL
            or option.amount_kind not in (HEALING, TEMP_HP)
            or not option.rolls
        ):
            return False
        dice = option.damage_at(None)
        at_the_table = caster is None or caster.get("_is_player")
        if DIE.search(dice) and (
            at_the_table or not self.settings.monsters_roll_turn_dice
        ):
            return False
        amount = roll_dice(dice)
        target = firing.target
        if option.amount_kind == TEMP_HP:
            if amount > 0:
                self._give_temp_hp(target, amount, caster)
            text = f"{amount} temp HP"
        else:
            self._heal_target(target, amount, caster)
            text = f"{amount} HP regained"
        self._turn_start_notes.append(f"{firing.badge}: {text} for {target['name']}")
        self._rebuild_card(target)
        return True

    def _refresh_turn_prompts(self):
        """A button per prompt the turn's triggers left, under the reminders:
        it opens the Custom Effect dialog with the trigger's caster as the
        source, the creature it's about as the target and its effect picked."""
        while self._turn_prompts_layout.count():
            item = self._turn_prompts_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        prompts: list[Firing | HitFiring] = [*self._turn_prompts, *self._hit_prompts]
        for firing in prompts:
            button = QPushButton(firing.prompt)
            button.setObjectName("turnPromptBtn")
            button.setToolTip(
                "Opens the Custom Effect dialog with this picked, for the GM to"
                " apply or cancel."
            )
            button.clicked.connect(
                lambda checked=False, f=firing: self._use_turn_prompt(f)
            )
            self._turn_prompts_layout.addWidget(button)

    def _use_turn_prompt(self, firing: Firing | HitFiring):
        """Open the Custom Effect dialog for a prompt: its caster (if still
        in the fight) as the source, its creature as the target, its effect
        picked. The prompt goes once it's used."""
        target = self._find_character_by_name(firing.target["name"])
        if target is None:
            self._show_status(f"{firing.target['name']} is no longer in the fight.")
            return
        targets = [target]
        if isinstance(firing, HitFiring) and (
            firing.row.trigger.aim is TriggerAim.ANOTHER
        ):
            # It goes on another creature: the one right-clicked.
            targets = [t for t in self.target_characters if t is not target]
            if not targets:
                self._show_status(
                    f"Right-click the creature {firing.row.name} goes on, then"
                    " press its button again."
                )
                return
        self._turn_prompts = [p for p in self._turn_prompts if p is not firing]
        self._hit_prompts = tuple(p for p in self._hit_prompts if p is not firing)
        caster = self._find_character_by_name(firing.caster) if firing.caster else None
        if caster is not None:
            self._select_character(caster)
        self._set_targets(targets)
        self._refresh_views()
        self._show_custom_condition_dialog(pick=firing.pick)

    # ── What a hit triggers ─────────────────────────────────────────────────

    @contextmanager
    def _one_trigger_prompt(self) -> Iterator[None]:
        """Collect the attack outcomes of everything inside (an Apply's
        Times copies, its targets), and ask about what they trigger once, at
        the end (Q41). Nested, only the outermost asks."""
        if self._attack_outcomes is not None:
            yield
            return
        self._attack_outcomes = ()
        try:
            yield
            outcomes: list[Outcome] = [*(self._attack_outcomes or ())]
        finally:
            self._attack_outcomes = None
        self._resolve_attack_triggers(outcomes)

    def _after_attack(self, outcome: Outcome):
        """What an attack roll's outcome triggers: asked about now, or with
        the rest of its Apply's (_one_trigger_prompt). Every hit path calls
        it: the Custom Effect dialog, the main window's Attack roll and
        Damage fields, a monster's action button. Damage a creature dealt
        another comes this way too (DamageMixin._deal_damage), for what the
        one damaged answers it with (TAKES_DAMAGE: Hellish Rebuke), and a
        creature reduced to 0 Hit Points, for what the one that did it gets
        (REDUCES_TO_ZERO: Dark One's Blessing)."""
        if self._attack_outcomes is not None:
            self._attack_outcomes = (*self._attack_outcomes, outcome)
            return
        self._resolve_attack_triggers([outcome])

    def _resolve_attack_triggers(self, outcomes: list[Outcome]):
        """Apply what `outcomes` trigger that happens by itself (AUTO), then
        ask about the rest in one pop-up (with the setting ask_triggers off,
        as turn-column buttons instead). What's applied goes through the Custom Effect
        dialog's path (_apply_row), inside the hit's undo step; a declined
        one logs a line for the GM only (Q45). Rows with no uses left are
        left out and said in the status line (Q42)."""
        if not outcomes:
            return
        found, spent = outcome_firings(
            outcomes,
            triggered_rows,
            is_dead=lambda char: self._char_death_state(char) == "dead",
            used_this_turn=self._triggers_used_this_turn(),
        )
        status = self._status_label.text()
        notes = list(spent)
        for firing in found:
            if firing.mode is TriggerMode.AUTO:
                self._use_trigger(firing, notes)
        asks = [f for f in found if f.mode is TriggerMode.ASK]
        if asks and not self.settings.ask_triggers:
            # A button each in the turn column, for the rest of the turn.
            self._hit_prompts = (*self._hit_prompts, *asks)
            self._refresh_turn_prompts()
        elif asks:
            self._answer_firings(asks, notes)
        if notes or found:
            # Logging cleared the hit's own status line; it comes back first.
            self._show_status("; ".join(part for part in (status, *notes) if part))

    def _answer_firings(
        self, asks: list[HitFiring], notes: list[str]
    ) -> list[tuple[HitFiring, int | None]]:
        """Ask the GM about `asks` in one pop-up and do what they answer:
        apply the checked ones, open the Custom Effect dialog for those to
        edit, and log a line for the GM about each declined one (Q45).
        Returns the firings applied, each with what was rolled at the table
        for its own roll, if anything (TriggerChoice.rolled)."""
        # A row aimed at other creatures offers who it can go on.
        asks = [
            (
                replace(firing, others=self._others_near(firing))
                if firing.row.trigger.aim is not TriggerAim.TARGET
                else firing
            )
            for firing in asks
        ]
        choice = self._ask_triggers(asks)
        applied = []
        for firing in asks:
            if any(firing is f for f in choice.apply):
                targets = self._aimed_targets(firing, choice.aimed_at(firing))
                if not targets:
                    notes.append(
                        f"{firing.row.name}: no creature picked to go on, not used"
                    )
                    continue
                if self._use_trigger(firing, notes, targets):
                    applied.append((firing, choice.rolled_for(firing)))
            elif not any(firing is f for f in choice.edit):
                self._log_event(
                    f"{firing.caster} didn't use {firing.row.name}"
                    f" on {firing.target['name']}",
                    character=firing.caster,
                    public=False,
                )
        for firing in choice.edit:
            self._edit_trigger(firing)
        return applied

    def _before_attack_roll(self, attacker: dict | None, target: dict | None):
        """What the others in the fight answer attacker's attack roll against
        target with before it's rolled (ATTACKS: Warding Flare), asked now in
        a pop-up of its own, as the roll is about to be made here (the Custom
        Effect dialog's, a monster's action button's; one typed in is rolled
        already). What it applies (Warding Flare's badge of Disadvantage on
        that one roll) goes through _apply_row, inside the roll's undo step,
        and the roll then counts it. With the setting ask_triggers off
        nothing is asked: a turn-column button would come after the roll."""
        if attacker is None or target is None or not self.settings.ask_triggers:
            return
        found = attack_roll_firings(
            attacker,
            target,
            self.characters,
            triggered_rows,
            is_dead=lambda char: self._char_death_state(char) == "dead",
        )
        if not found:
            return
        status = self._status_label.text()
        notes: list[str] = []
        self._answer_firings(found, notes)
        self._show_status("; ".join(part for part in (status, *notes) if part))

    def _before_hit(self, outcome: AttackOutcome) -> tuple[bool, int]:
        """What the creature hit answers the hit with before its damage is
        dealt (HIT_BY: Shield, Deflect Attacks), asked now, in a pop-up of
        its own: the answer changes the hit. What it applies goes through
        the Custom Effect dialog's path (_apply_row), spending its Reaction,
        slot or use, inside the hit's undo step. Returns whether the attack
        still hits (Shield's +5 counted in the AC it's checked against now)
        and the damage to take off it (what Deflect Attacks rolled). With
        the setting ask_triggers off, each is a turn-column button instead,
        and the hit is dealt as it is."""
        found, spent = hit_by_firings(
            outcome,
            triggered_rows,
            is_dead=lambda char: self._char_death_state(char) == "dead",
        )
        if not found:
            return True, 0
        if not self.settings.ask_triggers:
            self._hit_prompts = (*self._hit_prompts, *found)
            self._refresh_turn_prompts()
            return True, 0
        status = self._status_label.text()
        notes = list(spent)
        reduction = 0
        target = outcome.target
        for firing, at_table in self._answer_firings(found, notes):
            dice = firing.row.damage_reduction
            if dice:
                amount = roll_dice(dice) if at_table is None else at_table
                how = dice if at_table is None else f"{dice}, rolled at the table"
                reduction += amount
                self._log_event(
                    f"{target['name']}'s {firing.row.name} takes {amount} off"
                    f" the damage ({how})",
                    character=target["name"],
                )
        hits = still_hits(outcome, armor_in_use(target))
        if not hits:
            self._log_event(
                f"{outcome.attacker['name']}'s attack roll now misses"
                f" {target['name']}",
                character=target["name"],
            )
            notes.append(f"{target['name']}: now a miss")
        # Logging cleared the hit's own status line; it comes back first.
        self._show_status("; ".join(part for part in (status, *notes) if part))
        return hits, reduction

    def _drop_firings(self, outcome: DropOutcome) -> tuple[list[HitFiring], list[str]]:
        """What the creature outcome's damage would drop to 0 Hit Points can
        use instead (drop_firings: Relentless Endurance), for
        DamageMixin._drops_to_instead, which asks."""
        return drop_firings(
            outcome, triggered_rows, maximum=hit_point_maximum(outcome.target)
        )

    def _ask_triggers(self, firings: list[HitFiring]) -> TriggerChoice:
        """The pop-up (trigger_prompt.py). Tests replace this, so no modal
        event loop runs in them."""
        return ask_triggers(self._window, firings)

    def _others_near(self, firing: HitFiring) -> tuple[dict, ...]:
        """Who a row aimed at other creatures can go on besides its target:
        everyone else alive in the fight but its owner. Where they stand is
        the GM's to judge."""
        return tuple(
            char
            for char in self.characters
            if char is not firing.owner
            and char is not firing.target
            and self._char_death_state(char) != "dead"
        )

    @staticmethod
    def _aimed_targets(firing: HitFiring, picked: tuple[dict, ...]) -> list[dict]:
        """Who an applied firing goes on: its target, or for a row aimed at
        another creature the one picked, or its target and those added."""
        aim = firing.row.trigger.aim
        if aim is TriggerAim.ANOTHER:
            return list(picked[:1])
        if aim is TriggerAim.ALSO_OTHERS:
            return [firing.target, *(c for c in picked if c is not firing.target)]
        return [firing.target]

    def _use_trigger(
        self, firing: HitFiring, notes: list[str], targets: list[dict] | None = None
    ) -> bool:
        """Apply a firing's row as picking it in the Custom Effect dialog
        would, on `targets` (its own target if not given), noting in `notes`
        why it couldn't be. Returns whether it was, on any of them."""
        option = firing.row.option
        if not isinstance(option, EffectOption):
            return False
        used = False
        for target in targets if targets is not None else [firing.target]:
            if self._apply_row(firing.owner, target, option):
                used = True
                if _applies_nothing(option):
                    # What it does is done at the table (Push's 10 feet):
                    # the log says it was used.
                    self._log_event(
                        f"{firing.caster} uses {firing.row.name} on {target['name']}",
                        character=firing.caster,
                    )
            else:
                notes.append(f"{firing.row.name} not used on {target['name']}")
        if not used:
            return False
        if firing.row.trigger.once_per_turn:
            turn, used = self._trigger_uses
            used = used if turn == self._turn_key() else frozenset()
            self._trigger_uses = (
                self._turn_key(),
                used | {(firing.caster, firing.row.name)},
            )
        return True

    def _edit_trigger(self, firing: HitFiring):
        """Open the Custom Effect dialog for a firing, its owner the source,
        its target the only target and its row picked; the selection the GM
        had comes back after."""
        owner = self._find_character_by_name(firing.caster)
        target = self._find_character_by_name(firing.target["name"])
        if owner is None or target is None:
            return
        source, targets = self.selected_character, list(self.target_characters)
        self._select_character(owner)
        self._set_targets([target])
        self._show_custom_condition_dialog(pick=firing.pick)
        if source is not None and source is not owner:
            self._select_character(source)
        self._set_targets([t for t in targets if any(t is c for c in self.characters)])

    def _turn_key(self) -> tuple[int, int]:
        return (self.round_number, self.current_turn_idx)

    def _triggers_used_this_turn(self) -> frozenset[tuple[str, str]]:
        """The once-per-turn rows used this turn, as (owner, row) names."""
        turn, used = self._trigger_uses
        return used if turn == self._turn_key() else frozenset()

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

    def _player_view_content(self) -> tuple[str, list[PlayerViewRow]]:
        """The title and rows every player view shows, the screen and the link."""
        if self.phase != "COMBAT" or not self.initiative_order:
            return "Waiting for the fight to start", []
        return (
            f"Round {self.round_number}",
            player_view_rows(
                self.initiative_order,
                self._current_turn_group(),
                self._upcoming_turns(),
                self._char_death_state,
                limited=self.settings.limited_player_view,
            ),
        )

    def _refresh_player_view(self):
        view = self._player_view
        serving = self._player_server.running
        if view is None and not serving:
            return
        title, rows = self._player_view_content()
        if view is not None:
            view.show_rows(title, rows)
        if serving:
            self._publish_player_view(title, rows)

    def _publish_player_view(self, title: str, rows: list[PlayerViewRow]):
        self._player_server.feed.publish(
            title, [row.as_json() for row in rows], self._public_log()
        )

    def _start_player_server(self, host: str):
        """Serve the player link on `host`, with the fight on it from the first
        poll. Raises PlayerServerError if it can't."""
        self._publish_player_view(*self._player_view_content())
        self._player_server.start(host, PLAYER_PORT)
