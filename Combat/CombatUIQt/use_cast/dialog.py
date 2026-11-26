"""The Use / Cast dialog (ConditionsMixin._show_custom_condition_dialog
opens it): what the source uses on its targets, picked from what it has or
typed in, with its roll, damage or healing, condition and duration.

Moved here from conditions_mixin.py with the helpers only it uses
(Notes/combat-ui-refactor-plan.md, step 3c)."""

from html import escape

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextBrowser,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from Combat.Arena.arena import (
    position,
)
from Combat.Arena.ranges import (
    NO_RANGE_CHECK,
    RangeCheck,
    spell_range_warning,
)
from Combat.Arena.lasting import AREA_KEY, find_area, record_origin
from Combat.Definitions import (
    Phase,
)
from Combat.Effects.modifiers import (
    RollPlan,
    armor_class_notes,
    attack_plan,
    bonus_reminder,
    cover,
    extra_text,
    hit_extras,
    signed,
)
from Core.Definitions import DamageType
from Core.Rules import SECONDS_PER_ROUND
from Model.Content.CombatModifiers import HitPointMaximum

from Combat.Fight.amounts import AmountError
from Combat.Fight.attack_rolls import (
    AttackRoll,
    armor_bonus,
    cover_bonus,
    has_shield,
    is_shield_off,
    stored_armor,
    SHIELD_OFF,
)
from ..effect_dialog_widgets import (
    SearchKeys,
    chip,
    chip_row,
    row_widget,
    section,
    target_roll_rows,
)
from Combat.Fight.effect_options import (
    amount_text as _amount_text,
    pick_attack_range,
    pick_spell_range_ft,
    spell_slot_choices,
)
from Combat.Fight.monster_actions import legendary_resistances_left
from Combat.Fight.saves import (
    ABILITIES,
    AMOUNT_KINDS,
    ATTACK_ROLL,
    DAMAGE_AMOUNT,
    FEATURE,
    HEALING,
    MONSTER_ACTION,
    ROLL_MODES,
    SAVING_THROW,
    SPELL,
    TEMP_HP,
    EffectOption,
    known_attack_bonus,
    known_save_dc,
    rolled_damage,
    save_against,
    save_modifier,
    save_reminder,
)
from ..state import CombatWindowState
from ..tree_filter import first_visible_item
from . import form as use_cast_form
from .form import DICELESS, read_or_say

# The durations the Custom Condition dialog offers, as (label, duration). A
# duration is None (until removed), {"seconds": n} (counted down a round at a
# time, on the turn it was given in), or {"until": "start" | "end", "of":
# "source" | "target"} (ends at the start or end of the source's, or each
# target's, next turn), or {"until": "end", "of": "current"} (ends as the
# turn being taken ends). "{source}" in a label is the source's name.
CUSTOM_CONDITION_DURATIONS: list[tuple[str, dict | None]] = [
    ("Until removed", None),
    ("Until the end of this turn", {"until": "end", "of": "current"}),
    ("Until the start of {source}'s next turn", {"until": "start", "of": "source"}),
    ("Until the end of {source}'s next turn", {"until": "end", "of": "source"}),
    ("Until the start of the target's next turn", {"until": "start", "of": "target"}),
    ("Until the end of the target's next turn", {"until": "end", "of": "target"}),
    ("1 round (6 seconds)", {"seconds": SECONDS_PER_ROUND}),
    ("1 minute (10 rounds)", {"seconds": 60}),
    ("10 minutes", {"seconds": 10 * 60}),
    ("1 hour", {"seconds": 60 * 60}),
]


# The Custom Effect dialog: as wide as the screen allows up to the preferred
# width, never narrower than the minimum, which the chip rows need.
_CUSTOM_DIALOG_WIDTH = 1040


_PREFERRED_DIALOG_WIDTH = 1200


_SCREEN_MARGIN = 60


_PICKER_WIDTH = 340


_SUMMARY_COLOR = "#9fb4d0"


_DETAILS_MIN_HEIGHT = 90


# Room above the dialog's first minimum height, for what a pick shows (a note,
# extra rows: up to ~95px more). Opened at its bare minimum, the dialog had to
# grow while shown, and Windows printed "QWindowsWindow::setGeometry: Unable
# to set geometry".
_DIALOG_HEADROOM = 120


_BUTTON_WIDTH = 110


# The dialog's target boxes: how many to a line, and their + and × buttons.
_TARGETS_PER_LINE = 4


_TARGET_BUTTON_WIDTH = 28


_NO_TARGET = "— Pick a target —"


# The roll kind with neither a saving throw nor an attack roll.
NO_ROLL = "No roll"


# The amount box's title and hint, for what it holds.
_AMOUNT_TITLES = {
    DAMAGE_AMOUNT: "Damage",
    HEALING: "Healing (every target)",
    TEMP_HP: "Temporary Hit Points (every target)",
}


_AMOUNT_HINTS = {
    DAMAGE_AMOUNT: "e.g. 8d6, 28, 2d6 sl + 1d4 fi",
    HEALING: "e.g. 2d8 + 3, 10",
    TEMP_HP: "e.g. 2d4 + 4, 5",
}


_DETAILS_HINT = (
    "<p style='color:#a0a0b0'>Pick what was used and it fills in the form;"
    " its rules text shows here. Or fill in the form by hand.</p>"
    "<p style='color:#a0a0b0'><b>↑/↓</b> browse · <b>Enter</b> picks the top"
    " match, <b>Enter</b> again applies · <b>Esc</b> empties the search</p>"
)


MAX_SAVE_DC = 40


MIN_ATTACK_BONUS = -10


MAX_ATTACK_BONUS = 30


# The most times one Apply repeats an effect (Scorching Ray at a level 9
# slot has 10 rays).
MAX_EFFECT_TIMES = 20


# The units a custom duration can be typed in, as seconds per unit.
CUSTOM_DURATION_UNITS = {"rounds": SECONDS_PER_ROUND, "minutes": 60, "seconds": 1}


MAX_DURATION_AMOUNT = 9999


def custom_duration(seconds: int) -> tuple[int, str] | None:
    """`seconds` as the Custom... duration's amount and unit, the biggest unit
    that fits it exactly. None if it's longer than that can say (days)."""
    for unit, per_unit in sorted(CUSTOM_DURATION_UNITS.items(), key=lambda u: -u[1]):
        if seconds % per_unit == 0 and seconds // per_unit <= MAX_DURATION_AMOUNT:
            return seconds // per_unit, unit
    return None


def _where_from(option: EffectOption) -> str:
    """Where a spell's or feature's pick got its numbers, or "" for an attack
    or a monster's action, whose numbers are its own."""
    if option.kind == SPELL:
        if option.is_described:
            return "Filled in from checked spell data."
        return "Read from its rules text: check the form."
    if option.kind == FEATURE:
        of = ""
        if option.feature_name and option.feature_name != option.name:
            of = f"{escape(option.feature_name, quote=False)}: "
        if option.is_described:
            return f"{of}filled in from the feature's combat data."
        return f"{of}read from its rules text: check the form."
    action = option.monster_action
    if option.kind == MONSTER_ACTION and option.is_described and action is not None:
        of = ""
        if action.name != option.name:
            of = f"{escape(action.name, quote=False)}: "
        return f"{of}filled in from the stat block's combat data."
    return ""


def _option_details(option: EffectOption) -> str:
    """The Custom Effect dialog's rules text pane for a pick: its name, its
    numbers, where its numbers came from, and its rules text."""
    name = escape(option.row_name or option.name, quote=False)
    lines = [f"<p style='margin:0'><b style='color:#c9a84c'>{name}</b></p>"]
    if option.summary:
        summary = escape(option.summary, quote=False)
        lines.append(f"<p style='margin:0;color:{_SUMMARY_COLOR}'>{summary}</p>")
    where = _where_from(option)
    if where:
        lines.append(f"<p style='margin:0;color:#a0a0b0'><i>{where}</i></p>")
    if option.tooltip:
        text = escape(option.tooltip, quote=False).replace("\n", "<br>")
        lines.append(f"<p style='margin-top:6px'>{text}</p>")
    return "".join(lines)


def _source_text(source: dict | None) -> str:
    """The Custom Effect dialog's first line, before its target boxes: the
    source and an arrow to them."""
    if source is None:
        return "<span style='color:#a0a0b0'>No source</span> →"
    who = escape(source["name"], quote=False)
    return f"<span style='color:#c9a84c'>{who}</span> →"


def _with_shield(target: dict, wielding: bool | None) -> dict:
    """Target as it is with its Shield wielded or set down (`wielding`, the
    Custom Effect dialog's Shield box), to work its AC out by; target itself
    for None, or one without a Shield."""
    if wielding is None or not has_shield(target):
        return target
    return {**target, SHIELD_OFF: not wielding}


def _ignores_cover(pick: EffectOption | None) -> bool:
    """Whether a pick takes Half and Three-Quarters Cover away
    (EffectOption.ignores_cover: Sacred Flame), so only the map's Total
    Cover is left."""
    return pick is not None and pick.ignores_cover


def _armor_text(target: dict, wielding: bool | None = None) -> str:
    """What an attack roll against target has to meet: "AC 15", with its
    cover in it ("AC 17 (cover)"), or "AC ?" when that isn't known.
    `wielding`: whether it wields its Shield, None as it is now."""
    target = _with_shield(target, wielding)
    armor = stored_armor(target)
    if armor is None:
        return "AC ?"
    armor += armor_bonus(target)
    return f"AC {armor} (cover)" if cover_bonus(target) else f"AC {armor}"


def _bonus_notes(plan: RollPlan) -> list[str]:
    """What adds to a roll, for a tooltip: "Bless: +1d4"."""
    return [f"{label}: {signed(amount)}" for label, amount in plan.bonuses]


def _attack_text(
    source: dict | None,
    target: dict,
    wielding: bool | None = None,
    distance_ft: int | None = None,
    covered: dict | None = None,
    reach: RangeCheck = NO_RANGE_CHECK,
) -> str:
    """A target's row for an attack roll: what it has to meet, the mode the
    modifiers give it and what they add to it, to roll it that way at the
    table ("AC 15, Advantage", "AC 15, +1d4 to hit"). The extra damage a hit
    on it deals has a row of its own under it (target_roll_rows' extras).
    `wielding`: whether it wields its Shield (_armor_text). `distance_ft`:
    how far the source is on the map, which settles Prone's "within 5
    feet" (attack_plan). `covered`: target with the map's cover from the
    source in it (_covered), whose AC it has to meet. `reach`: what the map
    says of its range (Long range's Disadvantage counted, past its reach
    warned about after the rest: "AC 15; past the 5 ft. reach")."""
    plan = attack_plan(
        source,
        target,
        "Neutral",
        distance_ft=distance_ft,
        extra=reach.modifiers,
        sight=reach.sight,
    )
    parts = [_armor_text(covered or target, wielding)]
    if plan.mode != "Neutral":
        parts.append(plan.mode)
    flat, dice = bonus_reminder(plan)
    added = " ".join(p for p in (f"{flat:+d}" if flat else "", dice) if p)
    if added:
        parts.append(f"{added} to hit")
    return "; ".join([", ".join(parts), *_short_warnings(reach)])


def _short_warnings(reach: RangeCheck) -> list[str]:
    """A range warning as a row says it, without the target's name and
    distance its row already shows: "past the 5 ft. reach"."""
    return [w.split(" away, ", 1)[-1] for w in reach.warnings]


def _attack_tooltip(
    source: dict | None,
    target: dict,
    distance_ft: int | None = None,
    cover_text: str = "",
    reach: RangeCheck = NO_RANGE_CHECK,
) -> str:
    """The attack row's tooltip: what changes the AC, with `cover_text`, the
    map's cover from the source ("Half Cover from Barrel at C4: +2 AC and
    DEX saves"), how it's rolled (`reach`: the map's range, counted) and
    what a hit adds."""
    plan = attack_plan(
        source,
        target,
        "Neutral",
        distance_ft=distance_ft,
        extra=reach.modifiers,
        sight=reach.sight,
    )
    extras = [f"{label}: {extra_text(m)}" for label, m in hit_extras(source, target)]
    if extras:
        extras.append(
            "Rolled and added to a hit's damage, or typed in its box on this"
            " row if rolled at the table. A damage total typed in has it"
            " already, unless it's typed in its box."
        )
    return "\n".join(
        [
            "What the attack roll has to meet, cover included",
            *([cover_text] if cover_text else []),
            *armor_class_notes(target),
            *plan.notes,
            *reach.notes,
            *reach.warnings,
            *_bonus_notes(plan),
            *extras,
        ]
    )


def _save_row(target: dict, ability: str, plan: RollPlan) -> tuple[str, str]:
    """A target's row for a saving throw made as `plan` says, and its tooltip:
    its bonus with what its modifiers add, and what they do to the roll, to
    roll it that way at the table ("DEX +3, Disadvantage", "DEX +5 (cover)",
    "WIS +1 +1d4", "DEX fails"), and why."""
    why = [plan.auto_fail] if plan.auto_fail else [*plan.notes, *_bonus_notes(plan)]
    tooltip = "\n".join([f"{target['name']}'s {ability} saving throw bonus", *why])
    if plan.auto_fail:
        return f"{ability} fails", tooltip
    flat, dice = bonus_reminder(plan)
    text = f"{ability} {save_modifier(target, ability) + flat:+d}"
    if dice:
        text = f"{text} {dice}"
    if any(label == cover(target) for label, _ in plan.bonuses):
        text = f"{text} (cover)"
    return (text if plan.mode == "Neutral" else f"{text}, {plan.mode}"), tooltip


def _damage_preview(text: str, chosen_type: str | None) -> str:
    """The damage typed, for the preview line, with the dropdown's type when
    the text names none. Nothing is rolled."""
    text = text.strip()
    if not text:
        return ""
    try:
        parts = rolled_damage(DICELESS.sub("1", text))
    except AmountError:
        return f"{text} (can't be read)"
    if chosen_type is None or all(damage_type for _, damage_type in parts):
        return text
    return f"{text} {chosen_type}"


def _with_slot(record: dict, slot: int | None) -> dict:
    """A kept area's record with the slot level it was cast with, for its
    damage when it acts again (arena step 24); as it was without a slot."""
    if slot is None:
        return record
    return {**record, "slot_level": int(slot)}


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _effect_dialog_width(window: QWidget | None) -> int:
    """The Custom Effect dialog's width on the window's screen."""
    screen = window.screen() if window is not None else None
    if screen is None:
        return _CUSTOM_DIALOG_WIDTH
    room = screen.availableGeometry().width() - _SCREEN_MARGIN
    return max(_CUSTOM_DIALOG_WIDTH, min(_PREFERRED_DIALOG_WIDTH, room))


def _effect_dialog_height(dialog: QWidget) -> int:
    """The Custom Effect dialog's height: its minimum plus room to grow into
    (_DIALOG_HEADROOM), as far as its screen allows."""
    minimum = dialog.minimumSizeHint().height()
    screen = dialog.screen()
    if screen is None:
        return minimum + _DIALOG_HEADROOM
    room = screen.availableGeometry().height() - _SCREEN_MARGIN
    return max(minimum, min(minimum + _DIALOG_HEADROOM, room))


class UseCastDialog:
    """The Use / Cast dialog, one opening of it: what
    ConditionsMixin._show_custom_condition_dialog says it does. It was that
    function, with its nested functions (Notes/combat-ui-refactor-plan.md,
    step 3b): what they shared is attributes now, and they are methods.
    `app` is the window it opens over."""

    def __init__(self, app: CombatWindowState):
        self.app = app

    def run(self, pick: str, cost: str | None, kept_area: str):
        self.pick = pick
        self.cost = cost
        self.kept_area = kept_area
        self._prepare()
        self._build_targets()
        self._build_picker()
        self._build_roll_section()
        self._build_amount_section()
        self._build_condition_section()
        self._build_cost_section()
        self._build_footer()
        self._connect()
        self._start()

    def _prepare(self):
        """What the opening works on: the source, an area aimed or acting
        again, the targets."""
        self.source = self.app.selected_character or self.app._current_turn_character()
        self.aimed, self.app._aimed_area = self.app._aimed_area, None
        if self.aimed is not None and (
            self.source is None or self.aimed["source"] != self.source["name"]
        ):
            self.aimed = None
        # The kept area acting again, if this is its prompt: it spends nothing.
        self.again = (
            find_area(self.app.characters, self.kept_area) if self.kept_area else None
        )
        again_record: dict | None = (
            self.again[1][AREA_KEY] if self.again is not None else None
        )
        self.again_level = (again_record or {}).get("slot_level")
        if again_record is not None:
            self.aimed = None
        # The map's cover against a save is counted from where the aimed
        # area spreads (a Fireball's cell), else from the source.
        self.cover_origin = (
            record_origin(self.aimed["record"]) if self.aimed is not None else None
        )
        if again_record is not None:
            self.cover_origin = record_origin(again_record)
        self.caster = self.app.selected_character
        # The targets as the boxes at the top pick them, changed in place.
        self.targets: list[dict] = list(self.app.target_characters)
        self.choices = list(self.app.characters)
        self.source_name = self.source["name"] if self.source is not None else ""
        # The pick, and the damage and search it was made with, to tell the
        # GM's edits by.
        self.picked: dict = {"option": None, "damage": "", "times": 1, "search": ""}

        self.dlg = QDialog(self.app._window)
        self.dlg.setObjectName("customEffectDialog")
        self.dlg.setWindowTitle("Use / Cast")
        self.dlg.setMinimumWidth(_CUSTOM_DIALOG_WIDTH)
        self.dlg.resize(_effect_dialog_width(self.app._window), 0)
        self.outer = QVBoxLayout(self.dlg)
        self.outer.setContentsMargins(14, 12, 14, 12)
        self.outer.setSpacing(10)

    def _build_targets(self):
        """The source, and a box per target at the top."""
        # Who uses it on whom: the source, then a box per target.
        who_row = QHBoxLayout()
        who_row.setSpacing(8)
        self.outer.addLayout(who_row)
        who_lbl = QLabel(_source_text(self.source))
        who_lbl.setObjectName("effectWho")
        who_lbl.setTextFormat(Qt.TextFormat.RichText)
        who_lbl.setToolTip("Left-click a card for the source before opening this.")
        who_row.addWidget(who_lbl, alignment=Qt.AlignmentFlag.AlignTop)
        self.target_boxes = QWidget()
        self.target_boxes.setObjectName("effectTargets")
        self.target_grid = QGridLayout(self.target_boxes)
        self.target_grid.setContentsMargins(0, 0, 0, 0)
        self.target_grid.setHorizontalSpacing(6)
        self.target_grid.setVerticalSpacing(4)
        self.target_grid.setColumnStretch(_TARGETS_PER_LINE + 1, 1)
        who_row.addWidget(self.target_boxes, stretch=1)
        # A pick that goes on its user (Second Wind) instead of the boxes.
        self.itself_lbl = QLabel("")
        self.itself_lbl.setObjectName("targetItself")
        self.itself_lbl.hide()
        who_row.addWidget(
            self.itself_lbl, stretch=1, alignment=Qt.AlignmentFlag.AlignTop
        )
        self.add_target_btn = QPushButton("+")
        self.add_target_btn.setObjectName("addTarget")
        self.add_target_btn.setAutoDefault(False)
        self.add_target_btn.setFixedWidth(_TARGET_BUTTON_WIDTH)
        self.missing_lbl = QLabel("Target: missing")
        self.missing_lbl.setObjectName("targetMissing")
        self.missing_lbl.setToolTip("Pick who it's used on in a box to the left.")
        # Each box and the row holding it with its × button, in order.
        self.target_slots: list[tuple[QWidget, QComboBox]] = []

        self.add_target_btn.clicked.connect(self.add_empty_target_slot)
        for target in self.targets or [None]:
            self.add_target_slot(target)

        self.body = QHBoxLayout()
        self.body.setSpacing(14)
        self.outer.addLayout(self.body, stretch=1)

    def _build_picker(self):
        """What the source can use, on the left, and the form's columns."""
        # What the source can use, on the left: a pick fills in the form, and
        # its rules text shows under the list.
        self.search_box, self.tree, self.category_items = self.app._effect_picker(
            self.source
        )
        self.details = QTextBrowser()
        self.details.setObjectName("effectDetails")
        self.details.setOpenLinks(False)
        self.details.setMinimumHeight(_DETAILS_MIN_HEIGHT)
        picker_box = QWidget()
        picker_box.setFixedWidth(_PICKER_WIDTH)
        picker = QVBoxLayout(picker_box)
        picker.setContentsMargins(0, 0, 0, 0)
        picker.setSpacing(6)
        picker.addWidget(self.search_box)
        picker.addWidget(self.tree, stretch=3)
        picker.addWidget(self.details, stretch=2)
        self.body.addWidget(picker_box)

        form = QVBoxLayout()
        form.setSpacing(8)
        self.body.addLayout(form, stretch=1)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("effectName")
        self.name_input.setPlaceholderText("Name for the log (optional), e.g. Fireball")
        form.addWidget(self.name_input)

        # What to check about a pick, and what a monster's action does besides.
        self.note_lbl = QLabel("")
        self.note_lbl.setObjectName("effectNote")
        self.note_lbl.setWordWrap(True)
        self.note_lbl.hide()
        form.addWidget(self.note_lbl)

        columns = QHBoxLayout()
        columns.setSpacing(10)
        # The columns keep their widths whatever they show, so switching
        # between a saving throw and an attack roll doesn't move anything.
        column_widgets = []
        for stretch in (6, 5):
            column = QWidget()
            column.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
            )
            column_layout = QVBoxLayout(column)
            column_layout.setContentsMargins(0, 0, 0, 0)
            column_layout.setSpacing(8)
            columns.addWidget(column, stretch=stretch)
            column_widgets.append(column_layout)
        self.roll_col, self.effect_col = column_widgets
        form.addLayout(columns, stretch=1)

    def _build_roll_section(self):
        """The Roll section: none, a saving throw or an attack roll, and the
        rows per target."""
        # ── Roll: none, a saving throw or an attack roll, and what it decides
        roll_frame, roll_box, _ = section("Roll")
        self.roll_col.addWidget(roll_frame)
        # The roll's value is two combo boxes, hidden behind the chips: an
        # attack, or a saving throw with an ability, or None for no roll.
        self.roll_combo = QComboBox()
        self.roll_combo.setObjectName("rollKind")
        self.roll_combo.addItems((SAVING_THROW, ATTACK_ROLL))
        self.roll_combo.setCurrentText(self.app._custom_save["roll"])
        self.roll_combo.hide()
        roll_box.addWidget(self.roll_combo)
        self.ability_combo = QComboBox()
        self.ability_combo.setObjectName("saveAbility")
        self.ability_combo.addItem("No saving throw", None)
        for full, short in ABILITIES:
            self.ability_combo.addItem(full, short)
        self.ability_combo.setCurrentIndex(
            max(self.ability_combo.findData(self.app._custom_save["ability"]), 0)
        )
        roll_box.addWidget(self.ability_combo)

        kind_row, kind_layout = row_widget("rollKindButtons")
        kind_layout.setSpacing(3)
        self.kind_buttons = {
            NO_ROLL: chip("&No roll", "Damage and the condition for everyone (Alt+N)"),
            SAVING_THROW: chip("&Saving throw", "Each target saves (Alt+S)"),
            ATTACK_ROLL: chip(
                "&Attack roll", "The source rolls against each target's AC (Alt+A)"
            ),
        }
        for button in self.kind_buttons.values():
            button.setProperty("rollKind", True)
            kind_layout.addWidget(button, stretch=1)
        roll_box.addWidget(kind_row)

        self.save_line, save_layout = row_widget()
        save_layout.setSpacing(8)
        ability_chips = chip_row(
            self.ability_combo,
            [(i, short, full) for i, (full, short) in enumerate(ABILITIES, start=1)],
            "saveAbilityButtons",
        )
        save_layout.addWidget(ability_chips, stretch=1)
        self.dc_label = QLabel("DC")
        save_layout.addWidget(self.dc_label)
        self.dc_input = QSpinBox()
        self.dc_input.setObjectName("saveDc")
        self.dc_input.setRange(1, MAX_SAVE_DC)
        same_source = self.app._custom_save["source"] is self.source
        known_dc = None if same_source else known_save_dc(self.source)
        self.dc_input.setValue(known_dc or self.app._custom_save["dc"])
        save_layout.addWidget(self.dc_input)
        roll_box.addWidget(self.save_line)

        self.attack_line, attack_layout = row_widget()
        bonus_label = QLabel("Attack bonus")
        attack_layout.addWidget(bonus_label)
        self.bonus_input = QSpinBox()
        self.bonus_input.setObjectName("attackBonus")
        self.bonus_input.setRange(MIN_ATTACK_BONUS, MAX_ATTACK_BONUS)
        self.bonus_input.setToolTip("What the source adds to its d20")
        known_bonus = None if same_source else known_attack_bonus(self.source)
        self.bonus_input.setValue(
            self.app._custom_save["bonus"] if known_bonus is None else known_bonus
        )
        attack_layout.addWidget(self.bonus_input)
        attack_layout.addStretch()
        roll_box.addWidget(self.attack_line)

        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("saveMode")
        self.mode_combo.addItems(ROLL_MODES)
        roll_box.addWidget(self.mode_combo)
        self.mode_chips = chip_row(
            self.mode_combo,
            [
                (0, "Neutral", "One d20"),
                (1, "Advantage", "Two d20s, the higher counts, for every target"),
                (2, "Disadvantage", "Two d20s, the lower counts, for every target"),
            ],
            "saveModeButtons",
        )
        roll_box.addWidget(self.mode_chips)

        self.half_box = QCheckBox("Half damage on a save")
        self.half_box.setObjectName("halfOnSave")
        self.half_box.setChecked(self.app._custom_save["half"])
        roll_box.addWidget(self.half_box)

        self.repeat_box = QCheckBox("Repeat the save at the end of each turn")
        self.repeat_box.setObjectName("repeatSave")
        self.repeat_box.setToolTip(
            "A save ends the condition. Monsters roll by themselves; players"
            " get a reminder."
        )
        roll_box.addWidget(self.repeat_box)

        self.resist_box = QCheckBox("Use Legendary Resistance on a failed save")
        self.resist_box.setObjectName("useLegendaryResistance")
        roll_box.addWidget(self.resist_box)

        # A roll made at the table is typed in; the rest are rolled. Each target
        # rolls a save for itself, and the source an attack against each one.
        self.rolls_hint = QLabel("Rolled at the table? Type it; blank rolls.")
        self.rolls_hint.setObjectName("secondary")
        roll_box.addWidget(self.rolls_hint)
        # The rows per target, built again whenever the targets change: the
        # boxes and labels by id(target), filled in place so what reads them
        # always has the current ones.
        rolls_holder = QWidget()
        self.rolls_layout = QVBoxLayout(rolls_holder)
        self.rolls_layout.setContentsMargins(0, 0, 0, 0)
        self.rolls_layout.setSpacing(6)
        roll_box.addWidget(rolls_holder)
        self.roll_rows: dict[str, QWidget] = {}
        self.typed_inputs: dict[int, QLineEdit] = {}
        self.save_infos: dict[int, QLabel] = {}
        self.attack_inputs: dict[int, QLineEdit] = {}
        self.attack_infos: dict[int, QLabel] = {}
        self.extra_rows: dict = {}
        self.shield_boxes: dict[int, QCheckBox] = {}

        self.build_roll_rows()
        self.roll_col.addStretch()

    def _build_amount_section(self):
        """The Damage section: damage, Hit Points regained or Temporary Hit Points."""
        # ── Damage, or Hit Points regained, or Temporary Hit Points
        damage_frame, damage_box, self.amount_header = section("Damage")
        self.effect_col.addWidget(damage_frame)
        self.amount_combo = QComboBox()
        self.amount_combo.setObjectName("amountKind")
        self.amount_combo.addItems(AMOUNT_KINDS)
        damage_box.addWidget(self.amount_combo)
        amount_chips = chip_row(
            self.amount_combo,
            [
                (0, DAMAGE_AMOUNT, "Each target it lands on takes it"),
                (1, HEALING, "Every target regains it, whatever the roll"),
                (2, TEMP_HP, "Every target gains it, whatever the roll"),
            ],
            "amountKindButtons",
        )
        damage_box.addWidget(amount_chips)
        damage_row = QHBoxLayout()
        self.damage_input = QLineEdit()
        self.damage_input.setObjectName("effectDamage")
        self.damage_input.setPlaceholderText("e.g. 8d6, 28, 2d6 sl + 1d4 fi")
        self.damage_input.setToolTip("Dice are rolled once, for everyone it hits")
        damage_row.addWidget(self.damage_input, stretch=3)
        self.type_combo = QComboBox()
        self.type_combo.setObjectName("damageType")
        self.type_combo.addItem("— Type —", None)
        for damage_type in DamageType:
            self.type_combo.addItem(damage_type.value, damage_type.value)
        if self.source is not None and self.app.settings.remember_damage_type:
            self.type_combo.setCurrentIndex(
                max(self.type_combo.findData(self.source.get("_last_damage_type")), 0)
            )
        damage_row.addWidget(self.type_combo, stretch=2)
        damage_box.addLayout(damage_row)

        self.resistances_box = QCheckBox("Count resistances and immunities")
        self.resistances_box.setObjectName("countResistances")
        self.resistances_box.setChecked(True)
        damage_box.addWidget(self.resistances_box)
        times_line, times_layout = row_widget()
        times_layout.addWidget(QLabel("Times"))
        self.times_input = QSpinBox()
        self.times_input.setObjectName("effectTimes")
        self.times_input.setRange(1, MAX_EFFECT_TIMES)
        self.times_input.setToolTip(
            "Repeat it against each target, each time with its own attack roll,"
            " save and damage roll (Scorching Ray's rays, Eldritch Blast's"
            " beams). It costs the source once."
        )
        times_layout.addWidget(self.times_input)
        times_layout.addStretch()
        damage_box.addWidget(times_line)

    def _build_condition_section(self):
        """The Condition section: what it gives, for how long, and a note."""
        # ── Condition
        condition_frame, condition_box, self.condition_header = section("Condition")
        self.effect_col.addWidget(condition_frame)
        self.name_combo = QComboBox()
        self.name_combo.setObjectName("conditionName")
        self.name_combo.setEditable(True)
        self.name_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.suggestions = self.app._custom_condition_suggestions()
        self.name_combo.addItems(self.suggestions)
        self.name_combo.setCurrentText("")
        name_edit = self.name_combo.lineEdit()
        assert name_edit is not None  # an editable combo box has one
        self.name_edit = name_edit
        self.name_edit.setPlaceholderText("e.g. Hexed, Restrained by vines, -2 AC...")
        condition_box.addWidget(self.name_combo)

        self.notes_input = QLineEdit()
        self.notes_input.setObjectName("conditionNotes")
        self.notes_input.setPlaceholderText("Notes (optional, shown on hover)")
        condition_box.addWidget(self.notes_input)

        # A Hit Point maximum the badge rolls (Heroes' Feast's 2d10), rolled at
        # the table instead (plan step 8.6); shown for a pick that has one.
        self.maximum_input = QLineEdit()
        self.maximum_input.setObjectName("typedHitPointMaximum")
        self.maximum_input.setToolTip(
            "The Hit Point maximum rolled at the table, upcast and all: one"
            " total for every target, or one per target in the order they're"
            " listed (12, 9, 15). Blank rolls it for each."
        )
        self.maximum_input.hide()
        condition_box.addWidget(self.maximum_input)

        self.duration_combo = QComboBox()
        self.duration_combo.setObjectName("conditionDuration")
        self.duration_combo.setToolTip("How long the condition lasts")
        for label, duration in CUSTOM_CONDITION_DURATIONS:
            if duration is not None and duration.get("of") == "source":
                if self.source is None:
                    continue
                label = label.format(source=self.source["name"])
            self.duration_combo.addItem(label, duration)
        self.duration_combo.addItem("Custom...", "custom")
        condition_box.addWidget(self.duration_combo)

        custom_row = QHBoxLayout()
        self.amount_input = QSpinBox()
        self.amount_input.setObjectName("durationAmount")
        self.amount_input.setRange(1, MAX_DURATION_AMOUNT)
        custom_row.addWidget(self.amount_input)
        self.unit_combo = QComboBox()
        self.unit_combo.setObjectName("durationUnit")
        self.unit_combo.addItems(list(CUSTOM_DURATION_UNITS))
        custom_row.addWidget(self.unit_combo, stretch=1)
        self.custom_widgets = (self.amount_input, self.unit_combo)
        condition_box.addLayout(custom_row)

    def _build_cost_section(self):
        """What it costs the source, how many it may target, an area to keep
        and a push."""
        # ── What it costs the source
        cost_title = (
            f"Cost to {self.caster['name']}" if self.caster is not None else "Cost"
        )
        cost_frame, cost_box, _ = section(cost_title)
        self.effect_col.addWidget(cost_frame)
        self.slot_combo = QComboBox()
        self.slot_combo.setObjectName("spellSlot")
        self.slot_combo.addItem("No spell slot", None)
        for label, level in spell_slot_choices(self.caster or {}, 1):
            if level is not None:
                self.slot_combo.addItem(label, level)
        cost_box.addWidget(self.slot_combo)
        # How many creatures the pick may target (Bless: 3), at the slot chosen.
        self.target_count_lbl = QLabel("")
        self.target_count_lbl.setObjectName("targetCount")
        self.target_count_lbl.setWordWrap(True)
        self.target_count_lbl.hide()
        cost_box.addWidget(self.target_count_lbl)
        self.action_combo = QComboBox()
        self.action_combo.setObjectName("actionCost")
        self.action_combo.addItem("No action", None)
        for action_type in self.app.ACTION_ECONOMY_TYPES:
            self.action_combo.addItem(action_type, str(action_type))
        cost_box.addWidget(self.action_combo)
        action_chips = chip_row(
            self.action_combo,
            [(0, "None", "Spends no action")]
            + [
                (i, action_type, f"Spends the source's {action_type}")
                for i, action_type in enumerate(self.app.ACTION_ECONOMY_TYPES, start=1)
            ],
            "actionCostButtons",
        )
        cost_box.addWidget(action_chips)
        self.concentrate_box = QCheckBox("Source concentrates on it")
        self.concentrate_box.setObjectName("sourceConcentrates")
        self.concentrate_box.setToolTip(
            "Starts Concentrating, ending any other concentration. When it"
            " ends, the condition comes off the targets."
        )
        cost_box.addWidget(self.concentrate_box)
        # The area aimed on the map, to keep there (arena step 11).
        self.keep_area_box = QCheckBox(
            f"Keep the {self.aimed['text']} on the map"
            if self.aimed
            else "Keep the area"
        )
        self.keep_area_box.setObjectName("keepArea")
        self.keep_area_box.setToolTip(
            "The area stays on the map in its colour, as one of the source's"
            " Active Spells: for as long as the effect lasts, and with"
            " 'Source concentrates on it', until concentration ends."
        )
        self.keep_area_box.setChecked(bool(self.aimed and self.aimed["keep"]))
        self.keep_area_box.setVisible(self.aimed is not None)
        cost_box.addWidget(self.keep_area_box)
        # A pick that moves who it lands on (CombatEffect.push), once the map
        # is in use with the source on it (arena step 21).
        self.push_box = QCheckBox("")
        self.push_box.setObjectName("pushTargets")
        self.push_box.setToolTip(
            "Moves each target that fails the save or is hit (every target with"
            " no roll) straight away from the source on the battle map, as a"
            " push: no movement spent, no Opportunity Attack. It stops short"
            " of a wall, the map's edge or someone's space. 'Up to': the whole"
            " way here; Alt-drag a token back for less."
        )
        self.push_box.setChecked(True)
        self.push_box.hide()
        cost_box.addWidget(self.push_box)
        self.pushes_on_map = (
            self.app.phase == Phase.COMBAT
            and self.source is not None
            and position(self.source) is not None
            and self.app.arena_settings.in_use
        )

        for widget in (self.slot_combo, self.action_combo, self.concentrate_box):
            widget.setEnabled(self.caster is not None and self.again is None)
        if self.again is not None:
            at = f", at level {int(self.again_level)}" if self.again_level else ""
            free_lbl = QLabel(
                f"{self.again[0]['name']}'s {self.again[1]['name']} acting again: its"
                f" cast is spent already, so this costs nothing{at}."
            )
            free_lbl.setObjectName("keptAreaFree")
            free_lbl.setWordWrap(True)
            cost_box.addWidget(free_lbl)
        if self.caster is None:
            no_cost = QLabel("No source picked: left-click a card to spend from it.")
            no_cost.setObjectName("secondary")
            no_cost.setWordWrap(True)
            cost_box.addWidget(no_cost)
        self.effect_col.addStretch()

    def _build_footer(self):
        """What Apply will do, what's wrong, and the buttons."""
        # ── What Apply will do, what's wrong, and the buttons
        self.preview_lbl = QLabel("")
        self.preview_lbl.setObjectName("effectPreview")
        self.preview_lbl.setWordWrap(True)
        self.outer.addWidget(self.preview_lbl)

        btn_row = QHBoxLayout()
        footer = QVBoxLayout()
        footer.setSpacing(2)
        self.problem_lbl = QLabel("")
        self.problem_lbl.setObjectName("statusLabel")
        self.problem_lbl.setWordWrap(True)
        footer.addWidget(self.problem_lbl)
        keys_lbl = QLabel(
            "↑↓ browse · Enter picks, again applies · Ctrl+Enter apply"
            " · Alt+N/S/A roll · Ctrl+F search"
        )
        keys_lbl.setObjectName("secondary")
        footer.addWidget(keys_lbl)
        btn_row.addLayout(footer, stretch=1)
        # Targets in an area: the map aims the pick's area, and this dialog
        # opens again on the same pick with whoever is in it (arena step 10).
        area_btn = QPushButton("Select targets in a&rea")
        area_btn.setObjectName("areaTargetsBtn")
        area_btn.setAutoDefault(False)
        on_map = (
            self.app.phase == Phase.COMBAT
            and self.source is not None
            and position(self.source) is not None
        )
        area_btn.setEnabled(on_map)
        area_btn.setToolTip(
            "Aim the area on the map: whoever is in it becomes the targets,"
            " and this opens again on the same pick (Alt+R)"
            if on_map
            else "Needs a fight with the source on the map"
        )
        self.area_request: list[bool] = []

        area_btn.clicked.connect(self.select_in_area)
        btn_row.addWidget(area_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setMinimumWidth(_BUTTON_WIDTH)
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setObjectName("primaryBtn")
        self.apply_btn.setAutoDefault(False)
        self.apply_btn.setMinimumWidth(_BUTTON_WIDTH)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.apply_btn)
        self.outer.addLayout(btn_row)

    def _connect(self):
        """Wire the form: what each box and button changes, then show it all once."""
        # The ability a saving throw goes back to after "No roll".
        self.last_ability = {"value": self.ability_combo.currentData() or "DEX"}

        for kind, button in self.kind_buttons.items():
            button.clicked.connect(lambda _=False, k=kind: self.choose_kind(k))

        self.duration_combo.currentIndexChanged.connect(self.show_custom_row)
        self.roll_combo.currentIndexChanged.connect(self.show_roll_controls)
        self.ability_combo.currentIndexChanged.connect(self.show_roll_controls)
        self.amount_combo.currentIndexChanged.connect(self.show_amount_controls)
        self.amount_combo.currentIndexChanged.connect(self.show_roll_controls)
        self.damage_input.textChanged.connect(self.show_typed_type)
        self.name_combo.currentTextChanged.connect(lambda _: self.show_save_bonuses())
        for signal in (
            self.amount_combo.currentIndexChanged,
            self.roll_combo.currentIndexChanged,
            self.ability_combo.currentIndexChanged,
            self.mode_combo.currentIndexChanged,
            self.dc_input.valueChanged,
            self.bonus_input.valueChanged,
            self.half_box.toggled,
            self.repeat_box.toggled,
            self.damage_input.textChanged,
            self.type_combo.currentIndexChanged,
            self.name_combo.currentTextChanged,
            self.duration_combo.currentIndexChanged,
            self.amount_input.valueChanged,
            self.unit_combo.currentIndexChanged,
            self.slot_combo.currentIndexChanged,
            self.action_combo.currentIndexChanged,
            self.concentrate_box.toggled,
        ):
            signal.connect(self.show_preview)
        self.show_custom_row()
        self.show_amount_controls()
        self.show_roll_controls()
        self.show_preview()

        # Enter in a text box and the Apply button can both fire; apply once.
        self.applied: list[bool] = []

        # The rolls typed for each of the Times, as do_apply read them.
        self.typed_rolls: dict[str, dict] = {"totals": {}, "attacks": {}, "extras": {}}

    def _start(self):
        """Keys, the first pick, and opening the dialog."""
        # Up and Down from the search box pick as they go (fill_from), so
        # Enter applies the row they reached.
        SearchKeys(self.search_box, self.tree)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.tree.currentItemChanged.connect(self.on_current_changed)
        self.tree.itemActivated.connect(self.item_activated)
        self.search_box.returnPressed.connect(self.search_entered)
        self.slot_combo.currentIndexChanged.connect(self.upcast)
        self.name_input.textEdited.connect(self.drop_pick)

        self.apply_btn.clicked.connect(self.do_apply)
        self.name_edit.returnPressed.connect(self.do_apply)
        self.notes_input.returnPressed.connect(self.do_apply)
        self.damage_input.returnPressed.connect(self.do_apply)
        self.name_input.returnPressed.connect(self.do_apply)
        self.keep_area_box.toggled.connect(
            lambda _=False: self.show_target_slots(self.picked["option"])
        )
        self.cancel_btn.clicked.connect(self.dlg.reject)
        for keys, action in (
            ("Ctrl+Return", self.do_apply),
            ("Ctrl+Enter", self.do_apply),
            ("Ctrl+F", self.focus_search),
        ):
            QShortcut(QKeySequence(keys), self.dlg).activated.connect(action)

        self.show_details(None)
        self.show_target_slots(None)
        self.search_box.setFocus()
        start = next(
            (
                category.child(i)
                for category in self.category_items.values()
                for i in range(category.childCount())
                if (option := self.option_of(category.child(i))) is not None
                and option.name == self.pick
            ),
            None,
        )
        if self.pick and start is not None:
            self.tree.setCurrentItem(start)
            self.tree.scrollToItem(start)
        if self.cost:
            self.action_combo.setCurrentIndex(
                max(self.action_combo.findData(str(self.cost)), 0)
            )
        self.dlg.resize(self.dlg.width(), _effect_dialog_height(self.dlg))
        self.dlg.exec()
        if self.area_request:
            self.app._start_area_targeting(
                self.picked["option"], self.name_input.text().strip()
            )

    def lay_out_target_slots(self):
        while self.target_grid.count():
            self.target_grid.takeAt(0)
        cells = [row for row, _ in self.target_slots] + [
            self.add_target_btn,
            self.missing_lbl,
        ]
        for index, widget in enumerate(cells):
            self.target_grid.addWidget(
                widget,
                index // (_TARGETS_PER_LINE + 1),
                index % (_TARGETS_PER_LINE + 1),
            )

    def add_target_slot(self, char: dict | None) -> QComboBox:
        """A box picking `char` (None: nobody yet), with its × button."""
        row, layout = row_widget()
        layout.setSpacing(2)
        combo = QComboBox()
        combo.setObjectName("targetPick")
        combo.addItem(_NO_TARGET, -1)
        for index, choice in enumerate(self.choices):
            combo.addItem(f"{choice['name']}{self.app._distance_note(choice)}", index)
        if char is not None:
            at = next((i for i, c in enumerate(self.choices) if c is char), -1)
            combo.setCurrentIndex(max(combo.findData(at), 0))
        remove = QPushButton("×")
        remove.setObjectName("removeTarget")
        remove.setAutoDefault(False)
        remove.setFixedWidth(_TARGET_BUTTON_WIDTH)
        remove.setToolTip("Take this target away")
        layout.addWidget(combo, stretch=1)
        layout.addWidget(remove)
        slot = (row, combo)
        self.target_slots.append(slot)
        combo.currentIndexChanged.connect(lambda _=0: self.targets_changed())
        remove.clicked.connect(lambda _=False: self.remove_target_slot(slot))
        self.lay_out_target_slots()
        return combo

    def remove_target_slot(self, slot: tuple[QWidget, QComboBox]):
        """Take a box away; the last one empties instead."""
        if slot not in self.target_slots:
            return
        self.target_slots.remove(slot)
        slot[0].setParent(None)
        slot[0].deleteLater()
        if not self.target_slots:
            self.add_target_slot(None)
        self.lay_out_target_slots()
        self.targets_changed()

    def add_empty_target_slot(self):
        combo = self.add_target_slot(None)
        combo.setFocus()
        self.show_target_slots(self.picked["option"])

    def resisters(self) -> list[dict]:
        return [t for t in self.targets if legendary_resistances_left(t) > 0]

    def covered(self, target: dict, origin=None) -> dict:
        """Target with the map's cover against what's picked in it."""
        ignores = _ignores_cover(self.picked["option"])
        return self.app._covered(self.source, target, origin, ignores)

    def spell_range_text(self, target: dict) -> str:
        """ "past the spell's 60 ft. range" for a spell aimed at target
        from too far, on the map in use; "" for one aimed as an area
        (its point is what's checked, in the area bar)."""
        option = self.picked["option"]
        if self.aimed is not None or not self.app.arena_settings.in_use:
            return ""
        if option is None or option.area is not None:
            return ""
        warning = spell_range_warning(
            pick_spell_range_ft(option), self.source, target, self.app.arena_settings
        )
        return warning.split(" away, ", 1)[-1] if warning else ""

    def reach_of(self, target: dict) -> RangeCheck:
        """What the map says of the pick's range to target."""
        attack = pick_attack_range(self.picked["option"], self.source)
        return self.app._range_check(self.source, target, attack)

    def show_attack_info(self, target: dict):
        box = self.shield_boxes.get(id(target))
        wielding = None if box is None else box.isChecked()
        feet = self.app._attacker_distance_ft(self.source, target)
        reach = self.reach_of(target)
        info = self.attack_infos[id(target)]
        info.setText(
            _attack_text(
                self.source, target, wielding, feet, self.covered(target), reach
            )
        )
        info.setToolTip(
            _attack_tooltip(
                self.source,
                target,
                feet,
                self.app._map_cover(self.source, target).text,
                reach,
            )
        )

    def show_pick_rows(self):
        """The target rows again once a pick is made: its range and
        whether it ignores cover count in them."""
        for target in self.targets:
            if id(target) in self.attack_infos:
                self.show_attack_info(target)
        self.show_save_bonuses()

    def build_roll_rows(self):
        """The rows for the targets now picked, keeping what was typed
        (and each Shield box) for a target still picked."""
        typed = {
            **{("total", k): box.text() for k, box in self.typed_inputs.items()},
            **{("attack", k): box.text() for k, box in self.attack_inputs.items()},
            **{("extra", k): box.text() for k, (_, box) in self.extra_rows.items()},
        }
        wielded = {k: box.isChecked() for k, box in self.shield_boxes.items()}
        for widget in self.roll_rows.values():
            widget.setParent(None)
            widget.deleteLater()
        save_rows, totals, infos, _, _ = target_roll_rows(
            self.targets,
            "typedTotal",
            "The total with the save bonus already in it, like 14 or 9+5."
            " Blank rolls for them.",
        )
        # A hit's extra damage (Hunter's Mark) is a roll of its own: a box
        # more on its target's row, for what was rolled at the table.
        extra_boxes = {
            id(target): [
                (
                    (id(target), label),
                    f"{label[len(self.source['name']) + 3:]}: {extra_text(extra)}",
                    f"{label}: what was rolled at the table for its"
                    f" {extra_text(extra)}, its dice twice over on a Critical"
                    " Hit. Blank rolls it, unless the damage is a total typed"
                    " in, which has it already. 0 leaves it out.",
                )
                for label, extra in hit_extras(self.source, target)
            ]
            for target in self.targets
            if self.source is not None
        }
        # A target with a Shield can be wielding it or not: a box on its
        # row, its AC worked out by it.
        shield_checks = {
            id(target): (
                "Shield",
                f"Whether {target['name']} wields their Shield. The attack is"
                f" against AC {stored_armor(_with_shield(target, True))} with"
                f" it and {stored_armor(_with_shield(target, False))} without"
                " it (before effects and cover), and it stays as set here.",
                wielded.get(id(target), not is_shield_off(target)),
            )
            for target in self.targets
            if has_shield(target)
        }
        attack_rows, attacks, attack_labels, extras, shields = target_roll_rows(
            self.targets,
            "typedAttack",
            "The total with the bonus already in it, like 17 or 12+5, or"
            " nat 20 or nat 1. Blank rolls for the source.",
            extra_boxes,
            shield_checks,
        )
        for kept in (
            self.typed_inputs,
            self.save_infos,
            self.attack_inputs,
            self.attack_infos,
            self.extra_rows,
            self.shield_boxes,
        ):
            kept.clear()
        self.typed_inputs.update(totals)
        self.save_infos.update(infos)
        self.attack_inputs.update(attacks)
        self.attack_infos.update(attack_labels)
        self.extra_rows.update(extras)
        self.shield_boxes.update(shields)
        self.roll_rows.update(save=save_rows, attack=attack_rows)
        self.rolls_layout.addWidget(save_rows)
        self.rolls_layout.addWidget(attack_rows)
        for kind, boxes in (("total", totals), ("attack", attacks)):
            for key, box in boxes.items():
                box.setText(typed.get((kind, key), ""))
        for key, (_, box) in extras.items():
            box.setText(typed.get(("extra", key), ""))
        for box in [
            *totals.values(),
            *attacks.values(),
            *(box for _, box in extras.values()),
        ]:
            box.returnPressed.connect(lambda: self.do_apply())
        for target in self.targets:
            self.show_attack_info(target)
            if id(target) in self.shield_boxes:
                self.shield_boxes[id(target)].toggled.connect(
                    lambda _=False, t=target: self.show_attack_info(t)
                )
        self.resist_box.setToolTip(
            "Left: "
            + ", ".join(
                f"{t['name']} {legendary_resistances_left(t)}" for t in self.resisters()
            )
        )

    def amount_kind(self) -> str:
        return self.amount_combo.currentText()

    def show_amount_controls(self):
        """The box's title, hint and the damage-only controls, for what
        the amount is."""
        kind = self.amount_kind()
        is_damage = kind == DAMAGE_AMOUNT
        self.amount_header.setText(_AMOUNT_TITLES[kind])
        self.damage_input.setPlaceholderText(_AMOUNT_HINTS[kind])
        self.damage_input.setToolTip(
            "Dice are rolled once, for everyone it hits"
            if is_damage
            else "Dice are rolled once, for every target"
        )
        for widget in (self.type_combo, self.resistances_box):
            widget.setVisible(is_damage)

    def show_push(self, option: EffectOption | None):
        push = option.push if option is not None else None
        if push is None or not self.pushes_on_map or self.source is None:
            self.push_box.hide()
            return
        way = "toward" if push.toward else "away from"
        size = f" ({push.largest.value} or smaller)" if push.largest else ""
        self.push_box.setText(
            f"Who it lands on is {push.text} {way} {self.source['name']}{size}"
        )
        self.push_box.setChecked(True)
        self.push_box.show()

    def select_in_area(self):
        self.area_request.append(True)
        self.dlg.reject()

    def roll_kind(self) -> str:
        if self.roll_combo.currentText() == ATTACK_ROLL:
            return ATTACK_ROLL
        return SAVING_THROW if self.ability_combo.currentData() is not None else NO_ROLL

    def choose_kind(self, kind: str):
        self.roll_combo.setCurrentText(
            ATTACK_ROLL if kind == ATTACK_ROLL else SAVING_THROW
        )
        if kind == NO_ROLL:
            self.ability_combo.setCurrentIndex(0)
        elif kind == SAVING_THROW and self.ability_combo.currentData() is None:
            self.ability_combo.setCurrentIndex(
                max(self.ability_combo.findData(self.last_ability["value"]), 1)
            )
        self.show_roll_controls()

    def show_custom_row(self):
        for widget in self.custom_widgets:
            widget.setVisible(self.duration_combo.currentData() == "custom")

    def show_save_bonuses(self):
        ability = self.ability_combo.currentData()
        if ability is not None:
            self.last_ability["value"] = ability
        against = save_against(self.picked["option"], self.name_combo.currentText())
        for target in self.targets:
            info = self.save_infos[id(target)]
            if ability is None:
                info.setText("")
                continue
            seen = self.covered(target, self.cover_origin)
            far = self.spell_range_text(target)
            text, tip = _save_row(seen, ability, save_reminder(seen, ability, against))
            info.setText(text + (f"; {far}" if far else ""))
            info.setToolTip(tip)

    def show_roll_controls(self):
        kind = self.roll_kind()
        is_attack = kind == ATTACK_ROLL
        has_save = kind == SAVING_THROW
        for name, button in self.kind_buttons.items():
            button.setChecked(name == kind)
        self.save_line.setVisible(not is_attack)
        for widget in (self.dc_label, self.dc_input):
            widget.setVisible(has_save)
        self.attack_line.setVisible(is_attack)
        self.mode_chips.setVisible(kind != NO_ROLL)
        self.repeat_box.setVisible(has_save)
        # Hit Points aren't halved by a save: every target gets them.
        self.half_box.setVisible(has_save and self.amount_kind() == DAMAGE_AMOUNT)
        self.resist_box.setVisible(bool(self.resisters()) and has_save)
        self.rolls_hint.setVisible(kind != NO_ROLL)
        self.roll_rows["save"].setVisible(bool(self.typed_inputs) and has_save)
        self.roll_rows["attack"].setVisible(bool(self.attack_inputs) and is_attack)
        for row in self.extra_rows.values():
            for widget in row:
                widget.setVisible(self.amount_kind() == DAMAGE_AMOUNT)
        self.mode_combo.setEnabled(has_save or is_attack)
        for widget in (self.dc_input, self.half_box, self.repeat_box, self.resist_box):
            widget.setEnabled(has_save)
        for total_input in self.typed_inputs.values():
            total_input.setEnabled(has_save)
        self.condition_header.setText(
            {
                ATTACK_ROLL: "Condition (on a hit)",
                SAVING_THROW: "Condition (on a failed save)",
            }.get(kind, "Condition")
        )
        self.show_save_bonuses()

    def show_typed_type(self, text: str):
        if self.amount_kind() != DAMAGE_AMOUNT:
            return  # healing has no type
        try:
            parts = rolled_damage(DICELESS.sub("1", text))
        except AmountError:
            return
        if parts[0][1] is not None:
            self.type_combo.setCurrentIndex(self.type_combo.findData(parts[0][1]))

    def show_preview(self):
        """What Apply will do, in a line, so a wrong pick shows before it
        lands. Nothing here is rolled."""
        kind = self.roll_kind()
        mode = self.mode_combo.currentText()
        with_mode = f" with {mode}" if kind != NO_ROLL and mode != "Neutral" else ""
        parts = []
        if kind == SAVING_THROW:
            parts.append(
                f"DC {self.dc_input.value()} {self.ability_combo.currentText()} save{with_mode}"
            )
        elif kind == ATTACK_ROLL:
            parts.append(f"Attack {self.bonus_input.value():+d} vs AC{with_mode}")
        amount = self.amount_kind()
        if amount == DAMAGE_AMOUNT:
            damage = _damage_preview(
                self.damage_input.text(), self.type_combo.currentData()
            )
            if damage and kind == SAVING_THROW:
                damage += (
                    ", half on a save"
                    if self.half_box.isChecked()
                    else ", none on a save"
                )
            if damage:
                parts.append(damage)
        elif self.damage_input.text().strip():
            parts.append(
                _amount_text(self.damage_input.text().strip(), amount) + " for all"
            )
        condition = self.name_combo.currentText().strip()
        if condition:
            lasts = self.duration_combo.currentText()
            if self.duration_combo.currentData() == "custom":
                lasts = f"{self.amount_input.value()} {self.unit_combo.currentText()}"
            if self.duration_combo.currentData() is not None:
                condition += f" ({lasts[0].lower()}{lasts[1:]})"
            if kind == SAVING_THROW and self.repeat_box.isChecked():
                condition += ", save ends"
            parts.append(condition)
        costs = []
        if self.caster is not None:
            if self.slot_combo.currentData() is not None:
                costs.append(self.slot_combo.currentText())
            if self.action_combo.currentData() is not None:
                costs.append(self.action_combo.currentText())
            if self.concentrate_box.isChecked():
                costs.append("concentration")
        if costs:
            parts.append("costs " + ", ".join(costs))
        if not parts:
            self.preview_lbl.setText(
                "Pick something on the left, or fill in a roll, damage,"
                " healing or a condition."
            )
            return
        on = (
            self.source_name
            if self.on_itself(self.picked["option"])
            else _count(len(self.targets), "target")
        )
        self.preview_lbl.setText(f"On {on}: " + " · ".join(parts))

    def on_itself(self, option: EffectOption | None) -> bool:
        """Whether the pick goes on its user alone, whoever is targeted
        (_apply_custom_effect: Second Wind)."""
        return option is not None and option.targets_self and self.source is not None

    def show_target_slots(self, option: EffectOption | None):
        """The target boxes for the pick: none for one that goes on its
        user, + only while it may target more, and "Target: missing"
        while it needs one and has none."""
        itself = self.on_itself(option)
        self.target_boxes.setVisible(not itself)
        self.itself_lbl.setVisible(itself)
        name = option.name if option is not None else ""
        if itself:
            self.itself_lbl.setText(f"itself ({name} goes on its user)")
        count = option.targets_at(self.slot_combo.currentData()) if option else None
        room = count is None or len(self.target_slots) < count
        self.add_target_btn.setEnabled(room)
        self.add_target_btn.setToolTip(
            "Add another target"
            if count is None or room
            else f"{name} may target {_count(count, 'creature')}"
        )
        keeps_area = self.aimed is not None and self.keep_area_box.isChecked()
        self.missing_lbl.setVisible(not itself and not self.targets and not keeps_area)
        if itself:
            self.apply_btn.setToolTip(f"Apply to {self.source_name} (Ctrl+Enter)")
        elif self.targets:
            self.apply_btn.setToolTip(
                f"Apply to {_count(len(self.targets), 'target')} (Ctrl+Enter)"
            )
        elif keeps_area:
            self.apply_btn.setToolTip(
                "Put the area on the map, with no targets (Ctrl+Enter)"
            )
        else:
            self.apply_btn.setToolTip("Pick a target first")

    def targets_changed(self):
        """The boxes' picks, in order and once each, are the targets; the
        rows per target follow them."""
        chosen: list[dict] = []
        for _, combo in self.target_slots:
            index = combo.currentData()
            if isinstance(index, int) and index >= 0:
                char = self.choices[index]
                if not any(char is c for c in chosen):
                    chosen.append(char)
        if [id(c) for c in chosen] != [id(t) for t in self.targets]:
            self.targets[:] = chosen
            self.build_roll_rows()
            self.show_roll_controls()
            self.show_target_count(self.picked["option"])
            self.show_preview()
        self.show_target_slots(self.picked["option"])

    # Each reads what's typed for every target, or says what's wrong
    # under the form and gives None (use_cast/form.py).
    def say(self, problem: str):
        self.problem_lbl.setText(problem)

    def typed_totals(self) -> dict[int, list[int | None]] | None:
        texts = {key: box.text() for key, box in self.typed_inputs.items()}
        times = self.times_input.value()
        return read_or_say(lambda: use_cast_form.typed_totals(texts, times), self.say)

    def typed_attacks(self) -> dict[int, list[AttackRoll | None]] | None:
        texts = {key: box.text() for key, box in self.attack_inputs.items()}
        times = self.times_input.value()
        return read_or_say(lambda: use_cast_form.typed_attacks(texts, times), self.say)

    def typed_extras(self) -> dict[int, dict[str, list[int | None]]] | None:
        texts = {key: box.text() for key, (_, box) in self.extra_rows.items()}
        times = self.times_input.value()
        return read_or_say(lambda: use_cast_form.typed_extras(texts, times), self.say)

    def typed_maximum(self) -> dict[int, int] | None:
        shown = self.maximum_input.isVisibleTo(self.dlg)
        text = self.maximum_input.text() if shown else ""
        keys = [id(t) for t in self.targets]
        return read_or_say(lambda: use_cast_form.typed_maximum(text, keys), self.say)

    def _read_form(self) -> use_cast_form.FormValues:
        """What the boxes hold, as plain values."""
        pick: EffectOption | None = self.picked["option"]
        keeps_area = self.aimed is not None and self.keep_area_box.isChecked()
        duration = self.duration_combo.currentData()
        if duration == "custom":
            unit = CUSTOM_DURATION_UNITS[self.unit_combo.currentText()]
            duration = {"seconds": self.amount_input.value() * unit}
        acting_again = self.again is not None
        return use_cast_form.FormValues(
            roll=self.roll_combo.currentText(),
            ability=self.ability_combo.currentData(),
            condition_text=self.name_combo.currentText(),
            suggestions=list(self.suggestions),
            amount_kind=self.amount_kind(),
            amount_text=self.damage_input.text(),
            damage_type=self.type_combo.currentData(),
            pick=pick,
            pick_damage=self.picked["damage"],
            has_caster=self.caster is not None,
            has_targets=bool(self.targets),
            on_itself=self.on_itself(pick),
            keeps_area=keeps_area,
            name=self.name_input.text(),
            notes=self.notes_input.text(),
            duration=duration,
            count_resistances=self.resistances_box.isChecked(),
            slot_level=(
                self.again_level if acting_again else self.slot_combo.currentData()
            ),
            action_cost=self.action_combo.currentData(),
            concentration=self.concentrate_box.isChecked(),
            from_area=self.kept_area if acting_again else "",
            area=(
                _with_slot(self.aimed["record"], self.slot_combo.currentData())
                if self.aimed is not None and keeps_area
                else None
            ),
            cover_origin=self.cover_origin,
            attack_bonus=self.bonus_input.value(),
            dc=self.dc_input.value(),
            mode=self.mode_combo.currentText(),
            half_on_save=self.half_box.isChecked(),
            use_legendary_resistance=self.resist_box.isChecked(),
            repeat_save=self.repeat_box.isChecked(),
            shields={key: box.isChecked() for key, box in self.shield_boxes.items()},
            pushes=not self.push_box.isHidden() and self.push_box.isChecked(),
        )

    def do_apply(self):
        """Apply: check the form, read the rolls typed in, build the effect
        (use_cast/form.py) and use it on the targets, Times over."""
        if self.applied:
            return
        values = self._read_form()
        amount = read_or_say(lambda: use_cast_form.read_amount(values), self.say)
        if amount is None:
            return
        checked = read_or_say(
            lambda: use_cast_form.check_applicable(values, amount), self.say
        )
        if not checked:
            return
        is_damage = values.amount_kind == DAMAGE_AMOUNT
        totals = self.typed_totals() if values.save_ability is not None else {}
        attacks = self.typed_attacks() if values.is_attack else {}
        extras = self.typed_extras() if values.is_attack and is_damage else {}
        maximum = self.typed_maximum()
        if totals is None or attacks is None or extras is None or maximum is None:
            return
        self.typed_rolls.update(totals=totals, attacks=attacks, extras=extras)
        self.applied.append(True)
        self.app._custom_save = {
            "roll": values.roll,
            "ability": values.ability,
            "dc": values.dc,
            "half": values.half_on_save,
            "bonus": values.attack_bonus,
            "source": self.source,
        }
        rolls = use_cast_form.TypedRolls(totals, attacks, extras, maximum)
        effect = use_cast_form.build_effect(values, amount, rolls)
        # The boxes' picks become the targets, as if clicked on the cards.
        if [id(t) for t in self.targets] != [id(t) for t in self.app.target_characters]:
            self.app._set_targets(list(self.targets))
        times = self.times_input.value()
        if times == 1:
            self.app._apply_custom_effect(effect)
        else:
            copies = use_cast_form.repeated(
                effect,
                times,
                amount_text=values.amount_text,
                damage_type=values.damage_type,
                kind=values.amount_kind,
                typed_rolls=self.typed_rolls,
            )
            self.app._apply_custom_effects(copies)
        self.dlg.accept()

    def show_details(self, option: EffectOption | None):
        self.details.setHtml(
            _option_details(option) if option is not None else _DETAILS_HINT
        )

    def show_duration(self, seconds: int | None, until: tuple[str, str] | None):
        """Select a pick's duration: a turn, a time, or until removed. A
        turn of a source that isn't there falls back to until removed."""
        index = 0
        if until is not None:
            wanted_turn = {"until": until[0], "of": until[1]}
            index = next(
                (
                    i
                    for i in range(self.duration_combo.count())
                    if self.duration_combo.itemData(i) == wanted_turn
                ),
                0,
            )
        elif seconds:
            wanted = {"seconds": seconds}
            index = next(
                (
                    i
                    for i in range(self.duration_combo.count())
                    if self.duration_combo.itemData(i) == wanted
                ),
                -1,
            )
            fit = custom_duration(seconds) if index < 0 else None
            if fit is not None:
                self.amount_input.setValue(fit[0])
                self.unit_combo.setCurrentText(fit[1])
                index = self.duration_combo.findData("custom")
        self.duration_combo.setCurrentIndex(max(index, 0))

    def fill_from(self, option: EffectOption):
        """Replace everything a pick says with what this one does, and
        clear what it doesn't say. A None DC or bonus keeps the dialog's."""
        self.picked["option"] = None  # so the slot below isn't taken for an edit
        self.name_input.setText(option.name)
        self.note_lbl.setText(option.note)
        self.note_lbl.setVisible(bool(option.note))
        self.roll_combo.setCurrentText(option.roll)
        self.ability_combo.setCurrentIndex(
            max(self.ability_combo.findData(option.ability), 0) if option.ability else 0
        )
        if option.dc is not None:
            self.dc_input.setValue(option.dc)
        if option.bonus is not None:
            self.bonus_input.setValue(option.bonus)
        self.half_box.setChecked(option.half_on_save)
        self.repeat_box.setChecked(option.repeat_save)
        # What the source doesn't have (no slot left, no source) is "No ...".
        # findData never finds a PactSlot, and == alone can't tell one
        # from a spell slot of its level.
        self.slot_combo.setCurrentIndex(
            next(
                (
                    index
                    for index in range(self.slot_combo.count())
                    if self.slot_combo.itemData(index) == option.slot_level
                    and type(self.slot_combo.itemData(index)) is type(option.slot_level)
                ),
                0,
            )
            if self.again is None
            else 0
        )
        spends = self.cost or option.action_cost
        if self.again is not None:
            spends = None  # a kept area acting: its cast was spent
        action_index = self.action_combo.findData(str(spends))
        self.action_combo.setCurrentIndex(max(action_index, 0) if spends else 0)
        self.concentrate_box.setChecked(option.concentration and self.again is None)
        # A type left from before would disagree with the pick's damage.
        self.type_combo.setCurrentIndex(0)
        self.amount_combo.setCurrentText(option.amount_kind)
        level = (
            self.again_level
            if self.again is not None
            else self.slot_combo.currentData()
        )
        damage = option.damage_at(level)
        self.damage_input.setText(damage)
        times = option.instances_at(level)
        self.times_input.setValue(times)
        self.name_combo.setCurrentText(option.condition)
        self.notes_input.clear()
        self.show_duration(option.duration_seconds, option.until)
        self.problem_lbl.setText("")
        self.show_details(option)
        self.show_target_count(option)
        self.show_maximum_box(option)
        self.show_push(option)
        self.picked.update(
            option=option, damage=damage, times=times, search=self.search_box.text()
        )
        self.show_pick_rows()

    def drop_pick(self, name: str):
        """Typing another name makes it the GM's own effect: nothing is
        spent for the pick, and the slot box no longer upcasts it."""
        option = self.picked["option"]
        if option is None or name == option.name:
            return
        self.picked["option"] = None
        self.tree.clearSelection()
        self.note_lbl.setText("")
        self.note_lbl.hide()
        self.show_details(None)
        self.show_target_count(None)
        self.show_maximum_box(None)
        self.show_push(None)
        self.show_pick_rows()

    def show_maximum_box(self, option: EffectOption | None):
        """The Hit Point maximum box, for a pick whose badge rolls one."""
        dice = [
            m.amount
            for _, modifiers in (option.badge_modifiers if option else ())
            for m in modifiers
            if isinstance(m, HitPointMaximum) and "d" in m.amount + m.upcast
        ]
        self.maximum_input.clear()
        self.maximum_input.setPlaceholderText(
            f"Hit Point maximum ({dice[0]}) rolled, or blank to roll" if dice else ""
        )
        self.maximum_input.setVisible(bool(dice))

    def show_target_count(self, option: EffectOption | None):
        """How many creatures the pick may target at the slot chosen
        ("Targets: 4 at level 2" for Bless), and when more are targeted,
        how many too many. It warns; the GM can still apply it."""
        self.show_target_slots(option)
        slot = self.slot_combo.currentData()
        count = option.targets_at(slot) if option is not None else None
        if option is None or count is None:
            self.target_count_lbl.hide()
            return
        at = f" at level {int(slot)}" if option.target_upcast and slot else ""
        text = f"Targets: {count}{at}"
        if len(self.targets) > count:
            text += (
                f" ({len(self.targets)} targeted: {len(self.targets) - count} too many)"
            )
        self.target_count_lbl.setText(text)
        self.target_count_lbl.show()

    def upcast(self):
        """A pick's damage and times at the slot now chosen, unless they've
        been edited."""
        option = self.picked["option"]
        self.show_target_count(option)
        if option is None:
            return
        if self.times_input.value() == self.picked["times"]:
            self.picked["times"] = option.instances_at(self.slot_combo.currentData())
            self.times_input.setValue(self.picked["times"])
        if self.damage_input.text() != self.picked["damage"]:
            return
        damage = option.damage_at(self.slot_combo.currentData())
        self.damage_input.setText(damage)
        self.picked["damage"] = damage

    def option_of(self, item: QTreeWidgetItem | None) -> EffectOption | None:
        """What a row offers: nothing for a category or a greyed row."""
        if item is None or item.isHidden() or item.isDisabled():
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    def on_selection_changed(self):
        items = self.tree.selectedItems()
        option = self.option_of(items[0]) if items else None
        if option is not None:
            self.fill_from(option)

    def on_current_changed(self, item: QTreeWidgetItem | None):
        """A greyed row can't be picked, but its rules text can be read."""
        if item is not None and item.isDisabled():
            self.show_details(item.data(0, Qt.ItemDataRole.UserRole))

    def first_pickable(self) -> QTreeWidgetItem | None:
        match = first_visible_item(self.category_items)
        if match is None or not match.isDisabled():
            return match
        for category in self.category_items.values():
            for i in range(category.childCount()):
                if self.option_of(category.child(i)) is not None:
                    return category.child(i)
        return None

    def search_entered(self):
        """Enter picks the top match, and then applies what's picked. Once
        the search has changed since the pick, it picks the top match again."""
        current = self.tree.currentItem()
        option = self.option_of(current)
        searched = self.search_box.text() == self.picked["search"]
        if option is not None and option is self.picked["option"] and searched:
            self.do_apply()
            return
        match = self.first_pickable()
        if match is None:
            return
        again = self.option_of(match)
        if match is current and again is not None:
            self.fill_from(again)  # no selection change to do it
        else:
            self.tree.setCurrentItem(match)

    def item_activated(self, item: QTreeWidgetItem):
        option = self.option_of(item)
        if option is None:
            return
        if self.picked["option"] is not option:
            self.fill_from(option)
        self.do_apply()

    def focus_search(self):
        self.search_box.setFocus()
        self.search_box.selectAll()
