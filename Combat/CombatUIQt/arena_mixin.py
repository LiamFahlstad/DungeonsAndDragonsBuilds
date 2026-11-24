"""The battle map in the combat window (Notes/combat-arena-plan.md, steps
4-6): the Arena page beside the cards, the Cards/Arena switch (G and the
turn column's button, the view last used remembered in the settings
store), the map brought up to date with the cards, and moving: a token
dragged, or clicked (picked up) and then a cell clicked, one undo step
each, logged with where from and to and the movement left (Shift held as
it's dropped teleports it, Alt pushes it: no movement spent and no
Opportunity Attack, step 17), with the "Not
on the map" strip for whoever has no place yet. Selection, the
control panel, the turn column and undo are the window's, shared by both
views (the plan's Decision 2).

Targets in an area (step 10): the Custom Effect dialog's "Select targets in
area" closes it and brings up the map with the area bar, its shape and size
read from the pick's rules text (or the last ones used) and changeable
there. Hovering aims the area, a click makes whoever is in it the targets
and opens the dialog again on the same pick; a right click, Esc, G or the
bar's Cancel goes back to the dialog with the targets it had. The bar's
colour is what the area is shaded in.

Areas that stay (step 11): with the bar's "Keep on the map" (on for a pick
that lasts: a spell with a duration), the dialog opens again with "Keep the
area on the map", and its Apply puts the area on an active spell of the
source's (Combat/Arena/lasting.py): it ends with the spell's time, the
caster's concentration or the card's ✕. Such an area may be put down with
nobody in it (Moonbeam on empty ground). Whoever walks into one is named in
the status line, and walking in or starting or ending a turn in one is a
GM-only log line.

Selecting a kept area (step 12): a click on an empty cell of one brings up
the area panel over the map: whose it is, where, how long it has left and
its rules text, with its colour to change, Target who's in it, Move, End
spell, and Close (or Esc). The selection is the window's, as the source is,
but an area is never a source.

Areas acting (step 24): when a kept area's rules say it acts on a creature
(entering it, the area moved onto it, a turn starting or ending there),
that creature gets a turn-column button (an AreaPrompt) that opens Use /
Cast on the area's effect at no cost. Move aims a kept area again in the
area bar from where it is, keeping its time and concentration, spending
what its rules say moving it costs (its CombatArea, kept as "rules").

Walls (step 25): the bar's Wall is aimed by two clicks, its two ends (or,
ticked Ring, one on its middle), and for one with a damaging side (Wall of
Fire) a third on the side that deals damage. While it lasts, a wall its
text calls a barrier (Wall of Force) blocks movement and is Total Cover, as
a painted wall is: every rule reads the map through `_map_settings`, the
painted terrain with the kept walls laid over it, which is never saved into
the painted map.

Speeds (step 26): the speed bar over the map, for a source on it with
more than one speed (or aloft), picks the speed it moves by (Walk, Fly,
Swim, Climb, Burrow; Combat/Arena/speeds.py), what it has moved counting
against the new one, and how high a flyer is: flying up or down spends its
movement, and its altitude counts into its distances. A flyer that can't
stay aloft (Prone, Incapacitated, its Fly Speed 0 or gone, and no hover)
falls as the views are brought up to date: it lands, and the status and a
GM-only line say how far and what it takes.

The painted map (Notes/map-painter-plan.md): a fight starting puts whoever
the encounter's map gives a starting cell there; the hover names what's
painted on a cell, the target label says when a target is Lightly or
Heavily Obscured, and walking onto a hazard (a campfire, a trap) or starting
a turn on one is a reminder, as an area that stays is."""

from collections.abc import Iterable
from dataclasses import replace
from html import escape

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from Combat.Definitions import Phase
from Combat.Arena.arena import (
    MOVED_KEY,
    POSITION_KEY,
    ArenaSettings,
    can_end_at,
    distance_ft,
    distance_to_cell_ft,
    drag_costs_extra,
    footprint,
    grappled_by,
    dashes,
    move_cost,
    movement_ft,
    movement_rules,
    nearest_free,
    opportunity_attackers,
    occupied,
    reactive_strikers,
    place_new,
    position,
    reachable,
    remaining_ft,
    stand_up_ft,
    straight_ft,
    walk_path,
    walking_speed_ft,
)
from Combat.Arena.areas import (
    AreaOfEffect,
    AreaShape,
    area_cells,
    area_of,
    creatures_in,
    side_cells,
    side_name,
    side_of,
    wall_cells,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import (
    ACTIVE_SPELLS_KEY,
    AREA_KEY,
    DEFAULT_AREA_COLOR,
    ENDS,
    ENTERS,
    MOVED_ONTO,
    STARTS,
    AreaPrompt,
    LastingArea,
    area_key,
    area_record,
    areas_at,
    areas_beside,
    areas_holding,
    entered,
    find_area,
    lasting_areas,
    record_area,
    record_cells,
    record_end,
    record_move,
    record_timing,
    time_left_text,
    who_is_in,
)
from Combat.Arena.maps import place_at_starts
from Combat.Arena.grapples import dragged_to, stretched
from Combat.Arena.pushes import push_destination, push_order, too_big
from Combat.Arena.speeds import (
    ALTITUDE_KEY,
    FLY,
    LABELS,
    MAX_ALTITUDE_FT,
    MODE_KEY,
    SPEED_NAMES,
    VERBS,
    WALK,
    altitude_ft,
    hovers,
    mode_of,
    speed_of_mode,
    speeds,
)
from Combat.Arena.terrain import BRIGHT, DARK, DIM, OBSCURED, MapObject
from Combat.Effects.modifiers import has_condition
from Combat.Effects.triggers import OpportunityAttack
from Model.Content.CombatEffect import CombatPush
from Model.Content.StandardActions import DISENGAGE
from Core.Definitions import Condition
from Core.Rules import SECONDS_PER_ROUND

from .arena_view import ArenaView, MoveKind, token_rows
from Combat.Fight.effects_given import area_where, log_area_kept
from Combat.Fight.falling import land_fallers
from Combat.Fight.effect_options import (
    _spell_named,
    area_effect_row,
    opportunity_attack_row,
    spell_range_ft,
)
from Combat.Fight.saves import SPELL, CustomEffect, EffectOption
from .settings import ARENA_VIEW_KEY
from .state import CombatWindowState
from .steps import run_step
from .undo import undoable

CARDS_PAGE, ARENA_PAGE = 0, 1
# The area the bar starts with when the pick states none.
DEFAULT_AREA = AreaOfEffect(AreaShape.SPHERE, 20)
# The biggest area the bar takes, in feet (Meteor Swarm's 40-foot radius,
# a 300-foot Line, with room).
MAX_AREA_FT = 1000
# The colours the bar offers an area in, then "Other..." for any colour.
AREA_COLORS = (
    ("Orange", DEFAULT_AREA_COLOR),
    ("Red", "#e74c3c"),
    ("Blue", "#3498db"),
    ("Green", "#2ecc71"),
    ("Purple", "#9b59b6"),
    ("Yellow", "#f1c40f"),
    ("Teal", "#1abc9c"),
    ("Grey", "#95a5a6"),
)
OTHER_COLOR = "other"
_SWATCH_PX = 12
# The area panel's rules text: tall enough for a few lines, scrolled past.
_AREA_TEXT_HEIGHT = 96
# How long an area kept with no time of its own lasts: an hour, for the GM
# to end on the card (as a concentration effect with no time does).
LONGEST_AREA = 60 * 60


class ArenaMixin(CombatWindowState):
    def _build_view_stack(self, cards: QWidget) -> QStackedWidget:
        """The cards' scroll area (`cards`) as page 0 and the map as page 1,
        in the cards' place in the window."""
        self._arena_view = ArenaView(
            self._arena_select,
            self._arena_target,
            on_move=self._arena_move,
            on_cell=self._arena_cell,
            reach_of=self._arena_reach,
            distance_at=self._arena_distance,
            on_area=self._select_area,
        )
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._build_off_map_strip())
        layout.addWidget(self._build_speed_bar())
        layout.addWidget(self._build_area_bar())
        layout.addWidget(self._build_area_panel())
        layout.addWidget(self._arena_view, stretch=1)
        self._view_stack = QStackedWidget()
        self._view_stack.addWidget(cards)
        self._view_stack.addWidget(page)
        return self._view_stack

    def _build_off_map_strip(self) -> QWidget:
        """The "Not on the map" strip: a button for each combatant without a
        place, which makes it the source and picks it up; a click on a cell
        then puts it there. Hidden while everyone is on the map."""
        self._off_map_strip = QWidget()
        self._off_map_layout = QHBoxLayout(self._off_map_strip)
        self._off_map_layout.setContentsMargins(4, 4, 4, 0)
        self._off_map_layout.setSpacing(4)
        self._off_map_names: tuple[str, ...] = ()
        self._off_map_strip.hide()
        return self._off_map_strip

    def _refresh_off_map_strip(self):
        names = tuple(c["name"] for c in self.characters if position(c) is None)
        if names == self._off_map_names:
            return
        self._off_map_names = names
        while self._off_map_layout.count():
            item = self._off_map_layout.takeAt(0)
            widget = item.widget() if item is not None else None
            if widget is not None:
                widget.deleteLater()
        if not names:
            self._off_map_strip.hide()
            return
        self._off_map_layout.addWidget(QLabel("Not on the map:"))
        for name in names:
            button = QPushButton(name)
            button.setObjectName("offMapBtn")
            button.setToolTip(f"Pick up {name}, then click a cell to put it there")
            button.clicked.connect(lambda _=False, n=name: self._arena_pick(n))
            self._off_map_layout.addWidget(button)
        self._off_map_layout.addStretch()
        self._off_map_strip.show()

    def _build_speed_bar(self) -> QWidget:
        """The bar over the map for the source's speeds (step 26): the speed
        it moves by, and how high it flies. Shown for a source on the map
        in a fight with more than one speed, or one aloft."""
        bar = QWidget()
        bar.setObjectName("speedBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(4, 4, 4, 0)
        layout.setSpacing(6)
        self._speed_label = QLabel("")
        self._speed_label.setObjectName("speedLabel")
        layout.addWidget(self._speed_label)
        self._move_mode = QComboBox()
        self._move_mode.setObjectName("moveMode")
        self._move_mode.setToolTip(
            "The speed it moves by. Switching mid-move counts what it has"
            " moved against the new speed (Rules Glossary, Speed)."
        )
        layout.addWidget(self._move_mode)
        self._altitude_label = QLabel("Altitude")
        layout.addWidget(self._altitude_label)
        self._move_altitude = QSpinBox()
        self._move_altitude.setObjectName("moveAltitude")
        self._move_altitude.setRange(0, MAX_ALTITUDE_FT)
        self._move_altitude.setSingleStep(5)
        self._move_altitude.setSuffix(" ft. up")
        self._move_altitude.setKeyboardTracking(False)
        self._move_altitude.setToolTip(
            "How high it flies above the ground: going up or down spends its"
            " movement, and it counts into its distances"
        )
        layout.addWidget(self._move_altitude)
        layout.addStretch()
        self._move_mode.currentIndexChanged.connect(lambda: self._move_mode_picked())
        self._move_altitude.valueChanged.connect(lambda: self._altitude_picked())
        bar.hide()
        self._speed_bar = bar
        return bar

    def _refresh_speed_bar(self):
        """The speed bar for the source, or hidden."""
        char = self.selected_character
        have = speeds(char) if char is not None else {}
        aloft = char is not None and altitude_ft(char) > 0
        if (
            char is None
            or self.phase != Phase.COMBAT
            or position(char) is None
            or (len(have) < 2 and not aloft)
        ):
            self._speed_bar.hide()
            return
        mode = mode_of(char)
        self._speed_label.setText(f"{char['name']} moves by:")
        self._move_mode.blockSignals(True)
        self._move_mode.clear()
        for key, feet in have.items():
            hover = " (hover)" if key == FLY and hovers(char) else ""
            self._move_mode.addItem(f"{LABELS[key]} {feet} ft.{hover}", key)
        self._move_mode.setCurrentIndex(max(0, self._move_mode.findData(mode)))
        self._move_mode.blockSignals(False)
        flying = mode == FLY
        self._altitude_label.setVisible(flying)
        self._move_altitude.setVisible(flying)
        self._move_altitude.blockSignals(True)
        self._move_altitude.setValue(altitude_ft(char))
        self._move_altitude.blockSignals(False)
        self._speed_bar.show()

    def _move_mode_picked(self):
        char = self.selected_character
        mode = self._move_mode.currentData()
        if char is not None and mode and mode != mode_of(char):
            self._set_move_mode(char, mode)

    def _altitude_picked(self):
        char = self.selected_character
        if char is not None and self._move_altitude.value() != altitude_ft(char):
            self._set_altitude(char, self._move_altitude.value())

    @undoable
    def _set_move_mode(self, char: dict, mode: str):
        """Char moves by `mode` from now on (one undo step): what it has
        moved this turn counts against that speed (Rules Glossary, Speed).
        It can't stop flying while it's aloft: it lands first. A GM-only
        log line says what's left."""
        name = char["name"]
        if mode_of(char) == FLY and mode != FLY and altitude_ft(char) > 0:
            self._show_status(
                f"{name} is {altitude_ft(char)} ft. up: bring it down to 0 ft."
                " to land first."
            )
            self._refresh_views()
            return
        if mode == WALK:
            char.pop(MODE_KEY, None)
        else:
            char[MODE_KEY] = mode
        if mode != FLY:
            char.pop(ALTITUDE_KEY, None)
        speed = speed_of_mode(char)
        left = remaining_ft(char)
        line = f"{name} moves by its {SPEED_NAMES[mode_of(char)]} now" + (
            f" ({speed} ft.; {left} ft. left this turn)." if speed is not None else "."
        )
        self._log_event(line, character=name, public=False)
        self._show_status(line)
        self._refresh_views()

    @undoable
    def _set_altitude(self, char: dict, feet: int):
        """Char flies up or down to `feet` above the ground (one undo step),
        spending as much of its movement (a move by its Fly Speed), the map
        put in use; going past its movement is warned about, not refused,
        as a walk's is (Q2)."""
        name = char["name"]
        if mode_of(char) != FLY:
            return
        before = altitude_ft(char)
        change = abs(feet - before)
        if not change:
            return
        if feet:
            char[ALTITUDE_KEY] = feet
        else:
            char.pop(ALTITUDE_KEY, None)
        char[MOVED_KEY] = int(char.get(MOVED_KEY, 0)) + change
        self.arena_settings.in_use = True
        way = "up" if feet > before else "down"
        where = f"to {feet} ft. up" if feet else "to the ground"
        lines = [
            f"{name} flies {way} {change} ft. ({where}; {remaining_ft(char)} ft."
            " left this turn)."
        ]
        self._log_event(lines[0], character=name, public=False)
        movement = movement_ft(char)
        if movement is not None and char[MOVED_KEY] > movement:
            lines.append(
                f"{name} moved {char[MOVED_KEY]} ft., Fly Speed"
                f" {speed_of_mode(char)} ft."
            )
        self._show_status(" ".join(lines))
        self._refresh_views()

    def _land_fallers(self):
        """Whoever is aloft and can't stay so falls to the ground, with a
        GM-only line and the status saying how far it fell and what that
        deals (Combat/Fight/falling.py's land_fallers). Run as the views are
        brought up to date, so whatever made it fall (a condition, a spell
        ending) is in the same undo step."""
        lines = land_fallers(self.fight, self.logger)
        if lines:
            self._show_status(" ".join(lines))

    def _build_area_bar(self) -> QWidget:
        """The bar over the map while an area is aimed: what to do and who
        is in it, the area's shape, size, a Line's width and whether a
        Sphere, Cylinder or Cube starts at the source, and Cancel. Hidden
        otherwise."""
        self._area_targeting: dict | None = None
        self._last_area = DEFAULT_AREA
        self._aimed_area = None
        bar = QWidget()
        bar.setObjectName("areaBar")
        # What it is and who's in it on a line of its own, over the controls.
        rows = QVBoxLayout(bar)
        rows.setContentsMargins(4, 4, 4, 0)
        rows.setSpacing(4)
        self._area_label = QLabel("")
        self._area_label.setObjectName("areaLabel")
        self._area_label.setWordWrap(True)
        rows.addWidget(self._area_label)
        layout = QHBoxLayout()
        layout.setSpacing(6)
        rows.addLayout(layout)
        self._area_shape = QComboBox()
        self._area_shape.setObjectName("areaShape")
        for shape in AreaShape:
            self._area_shape.addItem(shape.value, shape)
        layout.addWidget(self._area_shape)
        self._area_size = QSpinBox()
        self._area_size.setObjectName("areaSize")
        self._area_size.setRange(5, MAX_AREA_FT)
        self._area_size.setSingleStep(5)
        self._area_size.setSuffix(" ft.")
        layout.addWidget(self._area_size)
        self._area_width_label = QLabel("wide")
        self._area_width = QSpinBox()
        self._area_width.setObjectName("areaWidth")
        self._area_width.setRange(5, MAX_AREA_FT)
        self._area_width.setSingleStep(5)
        self._area_width.setSuffix(" ft.")
        self._area_width.setToolTip("How wide the Line is")
        layout.addWidget(self._area_width_label)
        layout.addWidget(self._area_width)
        self._area_from_source = QCheckBox("From the source")
        self._area_from_source.setObjectName("areaFromSource")
        self._area_from_source.setToolTip(
            "A Sphere or Cylinder centred on the source, which leaves it out"
            " (Self (10-foot radius)), or a Cube against the source's side"
            " (Thunderwave)"
        )
        layout.addWidget(self._area_from_source)
        self._area_ring = QCheckBox("Ring")
        self._area_ring.setObjectName("areaRing")
        self._area_ring.setToolTip(
            "A wall in a ring as far across as the size (Wall of Fire's"
            " ringed wall), aimed by a click on its middle; unticked, a"
            " straight wall aimed by its two ends"
        )
        layout.addWidget(self._area_ring)
        self._area_color = _color_combo("areaColor")
        self._last_area_color = DEFAULT_AREA_COLOR
        layout.addWidget(self._area_color)
        self._area_keep = QCheckBox("Keep on the map")
        self._area_keep.setObjectName("areaKeep")
        self._area_keep.setToolTip(
            "The area stays on the map after Apply, in its colour, for as"
            " long as the effect lasts or its caster concentrates on it."
            " It can then be put down with nobody in it."
        )
        layout.addWidget(self._area_keep)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("areaCancelBtn")
        cancel.setToolTip("Back to the Custom Effect, targets as they were (Esc)")
        cancel.clicked.connect(lambda: self._cancel_area_targeting())
        layout.addWidget(cancel)
        layout.addStretch()
        self._area_shape.currentIndexChanged.connect(self._area_changed)
        self._area_size.valueChanged.connect(self._area_changed)
        self._area_width.valueChanged.connect(self._area_changed)
        self._area_from_source.toggled.connect(self._area_changed)
        self._area_ring.toggled.connect(self._area_ring_toggled)
        self._area_color.currentIndexChanged.connect(self._area_color_changed)
        self._area_keep.toggled.connect(self._area_changed)
        bar.hide()
        self._area_bar = bar
        return bar

    def _area_in_bar(self) -> AreaOfEffect:
        shape = self._area_shape.currentData()
        return AreaOfEffect(
            shape,
            self._area_size.value(),
            self._area_width.value(),
            self._area_from_source.isChecked()
            and shape in (AreaShape.SPHERE, AreaShape.CYLINDER, AreaShape.CUBE),
            ring=shape is AreaShape.WALL and self._area_ring.isChecked(),
        )

    def _area_boxes(self) -> tuple:
        """The bar's controls that make up the area."""
        return (
            self._area_shape,
            self._area_size,
            self._area_width,
            self._area_from_source,
            self._area_ring,
        )

    def _show_area_in_bar(self, area: AreaOfEffect):
        for box in self._area_boxes():
            box.blockSignals(True)
        self._area_shape.setCurrentIndex(self._area_shape.findData(area.shape))
        self._area_size.setValue(area.size_ft)
        # A Wall's thickness is no width the bar offers (it's one cell).
        self._area_width.setValue(max(5, area.width_ft))
        self._area_from_source.setChecked(area.from_source)
        self._area_ring.setChecked(area.ring)
        for box in self._area_boxes():
            box.blockSignals(False)
        self._show_area_controls()

    def _show_area_controls(self):
        """A Line's width, From the source for the shapes it changes, and
        Ring for a Wall."""
        shape = self._area_shape.currentData()
        self._area_width_label.setVisible(shape is AreaShape.LINE)
        self._area_width.setVisible(shape is AreaShape.LINE)
        self._area_from_source.setVisible(
            shape in (AreaShape.SPHERE, AreaShape.CYLINDER, AreaShape.CUBE)
        )
        self._area_ring.setVisible(shape is AreaShape.WALL)

    def _area_ring_toggled(self):
        """Ring ticked or not: the size the pick's text gives that kind of
        wall (Wall of Fire's 20-foot ring, its 60-foot wall), and the clicks
        so far forgotten."""
        request = self._area_targeting
        if request is not None and not request.get("move"):
            feet = request.get("ring_ft" if self._area_ring.isChecked() else "wall_ft")
            if feet:
                self._area_size.blockSignals(True)
                self._area_size.setValue(feet)
                self._area_size.blockSignals(False)
            request["ends"] = []
        self._area_changed()

    def _area_changed(self):
        self._show_area_controls()
        if self._area_targeting is not None:
            if self._area_shape.currentData() is not AreaShape.WALL:
                self._area_targeting["ends"] = []
            if not self._area_targeting.get("move"):
                self._last_area = self._area_in_bar()
            self._arena_view.refresh_area()

    def _area_color_in_bar(self) -> str:
        color = self._area_color.currentData()
        return color if color and color != OTHER_COLOR else self._last_area_color

    def _show_area_color(self, color: str):
        """Select `color` in the bar (show_color)."""
        show_color(self._area_color, color)
        self._last_area_color = color
        self._arena_view.set_area_color(color)

    def _area_color_changed(self):
        """A colour picked in the bar: the area is shaded in it, and the
        next one starts with it. "Other..." asks for any colour."""
        self._show_area_color(
            self._picked_color(self._area_color, self._last_area_color)
        )

    def _picked_color(self, combo: QComboBox, current: str) -> str:
        """The colour picked in `combo`; for "Other...", the one asked for,
        or `current` when that's cancelled."""
        color = combo.currentData()
        if color != OTHER_COLOR:
            return color
        chosen = QColorDialog.getColor(QColor(current), self._window, "Area colour")
        return chosen.name() if chosen.isValid() else current

    def _start_area_targeting(
        self, option: EffectOption | None, what: str = ""
    ) -> bool:
        """Bring up the map to aim an area for the Custom Effect's pick
        `option` (None for an effect typed by hand): its area and range read
        from it (area_reading), or the last area used. `what` names it in
        the bar. False, having said why, when the source isn't on the map."""
        source = self.selected_character or self._current_turn_character()
        if self.phase != Phase.COMBAT or source is None or position(source) is None:
            self._show_status("Targets in an area need the source on the map.")
            return False
        area, range_ft = area_reading(option)
        rules = option.area if option is not None else None
        pick = option.name if option is not None else ""
        self._aimed_area = None
        self._area_keep.setChecked(area_lasts(option))
        self._show_area_color(self._last_area_color)
        self._area_targeting = {
            "pick": pick,
            "source": source,
            "what": what or pick,
            "read": area is not None,
            "range": range_ft,
            "about": option.tooltip if option is not None else "",
            # Its pick's CombatArea, for the record kept (when it acts, how
            # it's moved, what it hides, a wall's terrain).
            "rules": rules,
            # A Wall's clicks so far (its ends, a ring's middle), the ring
            # and straight sizes its rules give, and how far its damaging
            # side reaches (Wall of Fire's 10 feet), if it has one.
            "ends": [],
            "wall_ft": area.size_ft if area is not None and area.is_wall else None,
            "ring_ft": rules.ring_ft if rules is not None else None,
            "side_ft": rules.side_ft if rules is not None else None,
        }
        self._show_area_in_bar(area or self._last_area)
        self._last_area = self._area_in_bar()
        self._area_keep.show()
        self._area_color.show()
        self._enable_area_shape(True)
        self._begin_aiming()
        return True

    def _move_selected_area(self):
        """The area panel's Move: aim the kept area selected again in the
        area bar, from where it is (Moonbeam's Magic action, Flaming
        Sphere's Bonus Action); a click puts it there (_move_area), keeping
        its time, concentration and colour. The bar says how far it went
        against the "up to" its text gives; Esc or a right click leaves it."""
        found = self._selected_lasting()
        if found is None or self.phase != Phase.COMBAT:
            return
        caster, entry = found
        record = entry[AREA_KEY]
        if record.get("follows") or record.get("aim") is None:
            return
        if record_area(record).is_wall:
            return
        rule = record_move(record, entry["name"])
        self._aimed_area = None
        self._area_targeting = {
            "pick": "",
            "source": caster,
            "what": f"Move {caster['name']}'s {entry['name']}",
            "read": True,
            "range": rule.feet,
            "about": "",
            "move": area_key(caster, entry),
            "from": Cell.of(record["aim"]),
        }
        self._show_area_in_bar(record_area(record))
        self._area_keep.hide()
        self._area_color.hide()
        self._enable_area_shape(False)  # it keeps its shape as it moves
        self._arena_view.set_area_color(record.get("color") or DEFAULT_AREA_COLOR)
        self._begin_aiming()

    def _enable_area_shape(self, enabled: bool):
        """The bar's shape, size, width and From the source, changeable or
        not (not while a kept area is moved)."""
        for box in self._area_boxes():
            box.setEnabled(enabled)

    def _begin_aiming(self):
        """Bring up the map and the area bar to aim `_area_targeting`."""
        self._view_stack.setCurrentIndex(ARENA_PAGE)
        self._view_toggle_btn.setText("Cards")
        self._area_bar.show()
        self._refresh_arena()
        self._arena_view.start_area(
            self._area_cells_at,
            self._area_picked,
            self._cancel_area_targeting,
            self._show_area_count,
        )
        self._arena_view.setFocus()

    def _area_cells_at(self, aim: Cell | None) -> set[Cell]:
        request = self._area_targeting
        if request is None:
            return set()
        area, settings = self._area_in_bar(), self._map_settings()
        if area.is_wall and not request.get("move"):
            return self._wall_cells_at(area, request, aim, settings)
        return area_cells(area, request["source"], aim, settings)

    def _wall_cells_at(
        self, area: AreaOfEffect, request: dict, aim: Cell | None, settings
    ) -> set[Cell]:
        """What a Wall being aimed covers with the mouse on `aim`: its first
        end there, then the wall from it to there (a ring around there);
        once put, the wall, and its damaging side on aim's side, to click."""
        ends = request.get("ends") or []
        if not _wall_placed(area, ends):
            if aim is None or not settings.on_map(aim):
                return set()
            if area.ring or not ends:
                return wall_cells(area, aim, None, settings)
            return wall_cells(area, ends[0], aim, settings)
        first, end = ends[0], (None if area.ring else ends[1])
        cells = wall_cells(area, first, end, settings)
        reach = request.get("side_ft")
        if aim is not None and reach is not None:
            side = side_of(area, first, end, aim, settings)
            cells |= side_cells(area, first, end, side, reach, settings)
        return cells

    def _wall_text(self, area: AreaOfEffect, request: dict) -> str | None:
        """What the bar says while a Wall is aimed: which click comes next,
        how long it is so far, the side the mouse is on; None once it's put
        and has no side to pick (the bar then names who's in it)."""
        ends = request.get("ends") or []
        aim = self._arena_view.area_aim
        settings = self._map_settings()
        if not _wall_placed(area, ends):
            if area.ring:
                return "click its middle."
            if not ends:
                return "click one end."
            text = "click its other end"
            if aim is not None:
                rule = settings.distance_rule
                feet = rule.feet(ends[0], aim, settings.cell_ft) + settings.cell_ft
                text += f" ({min(feet, area.size_ft)} ft. long"
                text += ", as far as it goes)" if feet > area.size_ft else ")"
            return text + "."
        if request.get("side_ft") is None:
            return None
        first, end = ends[0], (None if area.ring else ends[1])
        side = side_of(area, first, end, aim, settings) if aim is not None else 0
        which = f" (the {side_name(area, first, end, side)} side)" if side else ""
        return (
            f"click the side that deals damage{which}: within"
            f" {request['side_ft']} ft. of it."
        )

    def _show_area_count(self, cells: set[Cell]):
        """The bar's text: the area, and who is in it where it's aimed."""
        request = self._area_targeting
        if request is None:
            return
        area = self._area_in_bar()
        head = f"{request['what']}: " if request["what"] else ""
        if not request["read"] and request["pick"]:
            head += "no area given for it, so check the shape. "
        inside = creatures_in(self.characters, cells, self.arena_settings)
        wall = (
            self._wall_text(area, request)
            if area.is_wall and not request.get("move")
            else None
        )
        if wall is not None:
            text = f"{head}{area.text}: {wall}"
        elif request.get("move") and cells:
            onto = ", ".join(c["name"] for c in inside)
            text = f"{head}{area.text}: click to move it there" + (
                f" (onto {onto})." if onto else "."
            )
        elif not cells:
            how = (
                "hover over the map to aim it"
                if area.is_aimed
                else "the source isn't on the map"
            )
            text = f"{head}{area.text}: {how}."
        elif not inside and self._area_keep.isChecked():
            text = f"{head}{area.text}: nobody in it. Click to put it there."
        elif not inside:
            text = f"{head}{area.text}: nobody in it."
        else:
            names = ", ".join(c["name"] for c in inside)
            text = f"{head}{area.text}: {names}. Click to target them."
        far = self._area_range_text()
        self._area_label.setText(
            text + (f" {far}" if far else "") + " Right-click or Esc cancels."
        )

    def _area_out_of_range(self) -> tuple[int, int] | None:
        """How far the point aimed at is from the source, and the range,
        when it's past the range; None when it isn't, or can't be told."""
        request = self._area_targeting
        aim = self._arena_view.area_aim
        area = self._area_in_bar()
        if request is None or aim is None or request["range"] is None:
            return None
        if area.starts_at_source and not request.get("move"):
            return None
        feet = self._aim_feet(request, aim)
        if feet is None or feet <= request["range"]:
            return None
        return feet, request["range"]

    def _aim_feet(self, request: dict, aim: Cell) -> int | None:
        """How far `aim` is from the source, or for a kept area being moved,
        from where it was aimed before (how far it moves)."""
        start = request.get("from")
        if start is not None:
            settings = self._map_settings()
            return settings.distance_rule.feet(start, aim, settings.cell_ft)
        return distance_to_cell_ft(request["source"], aim, self.arena_settings)

    def _area_range_text(self) -> str:
        """The point aimed at against the range: "Aimed 45 ft. away, range
        150 ft." or "Aimed 160 ft. away: past its 150 ft. range!"; "" for an
        area that starts at the source, or without a range or an aim."""
        request = self._area_targeting
        aim = self._arena_view.area_aim
        if request is not None and aim is not None and request.get("move"):
            feet = self._aim_feet(request, aim)
            if request["range"] is None:
                return f"Moves {feet} ft."
            if feet is not None and feet > request["range"]:
                return f"Moves {feet} ft.: past its {request['range']} ft.!"
            return f"Moves {feet} ft., up to {request['range']} ft."
        if request is None or aim is None or request["range"] is None:
            return ""
        if self._area_in_bar().starts_at_source:
            return ""
        past = self._area_out_of_range()
        if past is not None:
            return f"Aimed {past[0]} ft. away: past its {past[1]} ft. range!"
        feet = distance_to_cell_ft(request["source"], aim, self.arena_settings)
        return f"Aimed {feet} ft. away, range {request['range']} ft."

    def _end_area_targeting(self) -> dict | None:
        """Stop aiming, and put back the view the GM had."""
        request = self._area_targeting
        if request is None:
            return None
        self._area_targeting = None
        self._arena_view.stop_area()
        self._area_bar.hide()
        self._show_view()
        return request

    def _area_picked(self, cell: Cell):
        """A click while aiming: whoever is in the area becomes the targets,
        and the Custom Effect opens again on the same pick. Nobody in it
        changes nothing."""
        request = self._area_targeting
        if request is None:
            return
        if request.get("move"):
            self._end_area_targeting()
            self._move_area(request["move"], cell)
            return
        area, source = self._area_in_bar(), request["source"]
        settings = self._map_settings()
        aim, end, side = (cell if area.is_aimed else None), None, 0
        if area.is_wall:
            ends = request.setdefault("ends", [])
            if not _wall_placed(area, ends):
                ends.append(cell)
                if not _wall_placed(area, ends) or request.get("side_ft") is not None:
                    self._arena_view.refresh_area()  # the next click
                    return
            else:
                side = side_of(area, ends[0], _wall_end(area, ends), cell, settings)
                if side == 0:
                    self._show_status(
                        "Click a cell on the side that deals damage, off the"
                        " wall's line."
                    )
                    return
            aim, end = ends[0], _wall_end(area, ends)
            cells = wall_cells(area, aim, end, settings)
        else:
            cells = self._area_cells_at(cell)
        inside = creatures_in(self.characters, cells, self.arena_settings)
        keep = self._area_keep.isChecked()
        if not inside and not (keep and cells):
            if area.is_wall:
                request["ends"] = []
                self._arena_view.refresh_area()
            self._show_status("Nobody is in that area: aim it somewhere else.")
            return
        past = self._area_out_of_range()
        record = area_record(
            area,
            source,
            aim,
            settings,
            self._area_color_in_bar(),
            pick=request["pick"],
            about=request["about"],
            end=end,
            side=side,
            rules=request.get("rules"),
        )
        self._end_area_targeting()
        # What the dialog, opened again, offers to keep on the map.
        self._aimed_area = {
            "source": source["name"],
            "record": record,
            "text": area.text
            + (
                f", its {side_name(area, aim, end, side)} side dealing damage"
                if side and aim is not None
                else ""
            ),
            "keep": keep,
        }
        self._set_targets(inside)
        if past is not None:
            # Allowed, as a move past the Speed is: the GM knows why.
            self._show_status(
                f"Aimed {past[0]} ft. away, past its {past[1]} ft. range."
            )
        self._reopen_custom_effect(request["pick"])

    def _cancel_area_targeting(self) -> bool:
        """Stop aiming and go back to the Custom Effect, with the targets it
        had; False when no area was being aimed."""
        request = self._end_area_targeting()
        if request is None:
            return False
        if not request.get("move"):  # a kept area being moved just stays
            self._reopen_custom_effect(request["pick"])
        return True

    def _reopen_custom_effect(self, pick: str):
        """Open the Custom Effect on `pick` once the click that got here is
        over, not inside the map's mouse handler."""
        QTimer.singleShot(0, lambda: self._show_custom_condition_dialog(pick))

    def _build_view_toggle(self) -> QPushButton:
        """The turn column's Arena / Cards button (hidden with the column
        outside combat)."""
        self._view_toggle_btn = QPushButton("Arena")
        self._view_toggle_btn.setObjectName("viewToggleBtn")
        self._view_toggle_btn.setToolTip("Switch between the cards and the map (G)")
        self._view_toggle_btn.clicked.connect(lambda: self._toggle_view())
        return self._view_toggle_btn

    def _arena_shown(self) -> bool:
        stack = getattr(self, "_view_stack", None)
        return stack is not None and stack.currentIndex() == ARENA_PAGE

    def _toggle_view(self):
        """Cards <-> Arena, during combat only; the choice is remembered."""
        if self.phase != Phase.COMBAT:
            return
        if self._cancel_area_targeting():
            return
        self.arena_view_on = not self._arena_shown()
        if self._settings_store is not None:
            self._settings_store.setValue(ARENA_VIEW_KEY, self.arena_view_on)
        self._show_view()

    def _show_view(self):
        """The page the phase and the settings call for: the map only in
        combat, when it's picked; the initiative screen and the party view
        are cards-only."""
        stack = getattr(self, "_view_stack", None)
        if stack is None:
            return
        arena = self.phase == Phase.COMBAT and self.arena_view_on
        stack.setCurrentIndex(ARENA_PAGE if arena else CARDS_PAGE)
        self._view_toggle_btn.setText("Cards" if arena else "Arena")
        self._view_toggle_btn.setVisible(self.phase == Phase.COMBAT)
        if arena:
            self._refresh_arena()

    def _place_on_arena(self):
        """Starting cells for whoever isn't on the map yet, as a fight
        starts or is continued: the cell the encounter's painted map gives
        them, else the party's side on the left and the rest on the right
        (the plan's Q1). Someone put on a painted start puts the map in use
        (Decision 29): the fight was set up on it."""
        painted = self._encounter_map(self._scenario_name)
        if painted is not None and place_at_starts(
            self.characters, painted.starts, self.arena_settings
        ):
            self.arena_settings.in_use = True
        place_new(self.characters, self._map_settings())

    def _refresh_arena(self):
        """Bring the map up to date (from _refresh_views), when it's shown."""
        if not self._arena_shown():
            return
        self._refresh_off_map_strip()
        self._refresh_speed_bar()
        # A token stays picked up only while it's the source: Escape, the
        # turn moving on or another source puts it down.
        picked, source = self._arena_view.picked, self.selected_character
        if picked is not None and (source is None or source["name"] != picked):
            self._arena_view.unpick()
        group = self._current_turn_group() if self.initiative_order else []
        self._arena_view.show_rows(
            self.arena_settings,
            token_rows(
                self.characters,
                self.arena_settings,
                group,
                self.selected_character,
                self.target_characters,
            ),
            self._lasting_rows(),
        )
        self._refresh_area_panel()
        if self._area_targeting is not None:
            # Someone moved, or was added: the area catches who's there now.
            self._arena_view.refresh_area()

    def _map_settings(self) -> ArenaSettings:
        """Fight.map_settings (Combat/Fight/fight.py)."""
        return self.fight.map_settings()

    def _lasting_rows(self) -> list[LastingArea]:
        """The kept areas the map draws, the one selected marked; a
        selection whose area has ended (or covers nothing now) is dropped."""
        rows = lasting_areas(self.characters, self._map_settings())
        if self._selected_area not in {row.key for row in rows}:
            self._selected_area = None
        return [replace(row, selected=row.key == self._selected_area) for row in rows]

    def _build_area_panel(self) -> QWidget:
        """The panel over the map for the kept area selected: what it is,
        its colour, Target who's in it, End spell and Close, and its rules
        text under them. Hidden while none is selected."""
        self._selected_area: str | None = None
        panel = QWidget()
        panel.setObjectName("areaPanel")
        rows = QVBoxLayout(panel)
        rows.setContentsMargins(4, 4, 4, 0)
        rows.setSpacing(4)
        self._area_panel_title = QLabel("")
        self._area_panel_title.setObjectName("areaPanelTitle")
        self._area_panel_title.setWordWrap(True)
        rows.addWidget(self._area_panel_title)
        top = QHBoxLayout()
        top.setSpacing(6)
        self._area_panel_color = _color_combo("areaPanelColor")
        self._area_panel_color.currentIndexChanged.connect(
            lambda: self._area_panel_color_changed()
        )
        top.addWidget(self._area_panel_color)
        target = QPushButton("Target who's in it")
        target.setObjectName("areaPanelTargetBtn")
        target.setToolTip("Make whoever is in the area the targets")
        target.clicked.connect(lambda: self._target_selected_area())
        top.addWidget(target)
        self._area_panel_move = QPushButton("Move")
        self._area_panel_move.setObjectName("areaPanelMoveBtn")
        self._area_panel_move.clicked.connect(lambda: self._move_selected_area())
        top.addWidget(self._area_panel_move)
        end = QPushButton("End spell")
        end.setObjectName("areaPanelEndBtn")
        end.setToolTip(
            "End it now, as the card's ✕ does: the area goes, and what"
            " it holds by concentration comes off"
        )
        end.clicked.connect(lambda: self._end_selected_area())
        top.addWidget(end)
        close = QPushButton("Close")
        close.setObjectName("areaPanelCloseBtn")
        close.setToolTip("Deselect the area (Esc)")
        close.clicked.connect(lambda: self._deselect_area())
        top.addWidget(close)
        top.addStretch()
        rows.addLayout(top)
        self._area_panel_text = QTextBrowser()
        self._area_panel_text.setObjectName("areaPanelText")
        self._area_panel_text.setMaximumHeight(_AREA_TEXT_HEIGHT)
        rows.addWidget(self._area_panel_text)
        panel.hide()
        self._area_panel = panel
        return panel

    def _selected_lasting(self) -> tuple[dict, dict] | None:
        """The caster and active spell of the kept area selected, if any."""
        if self._selected_area is None:
            return None
        return find_area(self.characters, self._selected_area)

    def _select_area(self, key: str):
        """A kept area clicked on the map: select it, and show the panel."""
        self._selected_area = key
        self._refresh_arena()

    def _deselect_area(self) -> bool:
        """Deselect the kept area; False when none was selected."""
        if self._selected_area is None:
            return False
        self._selected_area = None
        self._refresh_arena()
        return True

    def _refresh_area_panel(self):
        """The panel for the area selected, or hidden without one."""
        found = self._selected_lasting()
        if found is None:
            self._area_panel.hide()
            return
        caster, entry = found
        record = entry[AREA_KEY]
        where = self._area_where(record)
        if record.get("follows"):
            where = f"around {caster['name']}"
        parts = [record_area(record).text + (f" {where}" if where else "")]
        parts += _wall_notes(record)
        if entry.get("concentration"):
            parts.append("Concentration")
        left = time_left_text(entry.get("time_left"))
        if left:
            parts.append(left)
        title = escape(f"{caster['name']}'s {entry['name']}", quote=False)
        self._area_panel_title.setText(
            f"<b>{title}</b> · " + " · ".join(escape(p, quote=False) for p in parts)
        )
        about = record.get("about") or self._rules_text_of(record, entry)
        # An area that follows its caster moves with it, not by itself; a
        # wall's text doesn't move it (it's ended and cast again).
        self._area_panel_move.setVisible(
            not record.get("follows") and not record_area(record).is_wall
        )
        how = record_move(record, entry["name"]).text
        self._area_panel_move.setToolTip(
            "Aim it again on the map, keeping its time and concentration"
            + (f" ({how})" if how else "")
        )
        shown = (
            escape(about, quote=False).replace("\n", "<br>")
            if about
            else ("<i>No rules text kept for it.</i>")
        )
        if self._area_panel_text.property("shown") != shown:
            self._area_panel_text.setProperty("shown", shown)
            self._area_panel_text.setHtml(shown)
        self._area_panel_color.blockSignals(True)
        show_color(self._area_panel_color, record.get("color") or DEFAULT_AREA_COLOR)
        self._area_panel_color.blockSignals(False)
        self._area_panel.show()

    def _rules_text_of(self, record: dict, entry: dict) -> str:
        """A kept area's rules text when its record has none: the spell's
        it's named after, if it is one."""
        spell = _spell_named(record.get("pick") or entry["name"])
        return spell.description if spell is not None else ""

    def _area_panel_color_changed(self):
        found = self._selected_lasting()
        if found is None:
            return
        record = found[1][AREA_KEY]
        current = record.get("color") or DEFAULT_AREA_COLOR
        color = self._picked_color(self._area_panel_color, current)
        if color != current:
            self._set_area_color(found[0], found[1], color)
        else:
            self._refresh_area_panel()

    @undoable
    def _set_area_color(self, caster: dict, entry: dict, color: str):
        """Shade caster's kept area `entry` in `color`: one undo step."""
        entry[AREA_KEY]["color"] = color
        self._refresh_arena()

    def _target_selected_area(self):
        """Whoever is in the kept area selected becomes the targets (to
        apply its damage at the start of a turn, say)."""
        found = self._selected_lasting()
        if found is None:
            return
        caster, entry = found
        cells = record_cells(entry[AREA_KEY], caster, self._map_settings())
        inside = creatures_in(self.characters, cells, self.arena_settings)
        if not inside:
            self._show_status(f"Nobody is in {caster['name']}'s {entry['name']}.")
            return
        self._set_targets(inside)
        self._refresh_views()

    def _end_selected_area(self):
        """End the kept area selected, with its active spell (one undo
        step, as the card's ✕): concentration on it ends too."""
        found = self._selected_lasting()
        if found is None:
            return
        self._selected_area = None
        self._remove_active_spell(*found)
        self._refresh_views()

    @undoable
    def _move_area(self, key: str, cell: Cell):
        """Put kept area `key` where `cell` aims it (the panel's Move): one
        undo step, its key, time, concentration and colour kept. What its
        rules say moving it costs (record_move: Flaming Sphere's Bonus
        Action) is spent from its caster, asked about first when that's
        used already; past its "up to" is warned about, not refused (as
        Decision 19). Whoever it's moved onto gets its button, when its
        rules act then (Moonbeam: "when the spell's area moves into its
        space"). A GM-only log line says where from and to."""
        found = find_area(self.characters, key)
        if found is None:
            return
        caster, entry = found
        record, settings = entry[AREA_KEY], self._map_settings()
        rule = record_move(record, entry["name"])
        title = f"{caster['name']}'s {entry['name']}"
        if (
            rule.action is not None
            and self.phase == Phase.COMBAT
            and not self._go_ahead_anyway(
                caster, f"Move {title}", [self._action_lack(caster, rule.action)]
            )
        ):
            return
        before = who_is_in(self.characters, settings)
        start = Cell.of(record["aim"]) if record.get("aim") is not None else None
        cells = area_cells(record_area(record), caster, cell, settings)
        record["aim"] = cell.to_list()
        record["cells"] = [c.to_list() for c in sorted(cells)]
        shape = settings.distance_rule.shape
        feet = (
            settings.distance_rule.feet(start, cell, settings.cell_ft)
            if start is not None
            else None
        )
        moved = f" from {shape.cell_name(start)}" if start is not None else ""
        line = f"{title} moves{moved} to {shape.cell_name(cell)}" + (
            f" ({feet} ft.)." if feet is not None else "."
        )
        self._log_event(line, character=caster["name"], public=False)
        lines = [line]
        if rule.feet is not None and feet is not None and feet > rule.feet:
            lines.append(f"That's past its {rule.feet} ft.")
        if rule.action is not None:
            self._add_action_use(rule.action, caster, ask=False)
        after = who_is_in(self.characters, settings)
        for who, (owner, area) in entered(before, after):
            text = f"{who} is in {owner}'s {area} now."
            self._log_event(text, character=who, public=False)
            lines.append(text)
            self._area_entered(who, owner, area, MOVED_ONTO)
        self._show_status(" ".join(lines))
        self._refresh_views()

    def _arena_char(self, name: str) -> dict | None:
        return next((c for c in self.characters if c["name"] == name), None)

    def _arena_select(self, name: str):
        char = self._arena_char(name)
        if char is not None:
            self._select_character(char)

    def _arena_pick(self, name: str):
        """Make `name` the source and pick it up: a click on a cell moves or
        puts it there."""
        self._arena_select(name)
        if self.selected_character is not None:
            self._arena_view.pick(name)

    def _arena_target(self, name: str, ctrl: bool, shift: bool):
        char = self._arena_char(name)
        if char is not None:
            self._select_target_character(char, ctrl, shift)

    def _arena_reach(self, name: str) -> dict[Cell, int]:
        """Where `name` can still move this turn, and what each costs: its
        walking speed in use less what it has moved (the plan's Q7)."""
        char = self._arena_char(name)
        if char is None:
            return {}
        return reachable(
            char, self.characters, self._map_settings(), remaining_ft(char)
        )

    def _arena_move(self, name: str, cell: Cell, kind: MoveKind = MoveKind.WALK):
        char = self._arena_char(name)
        if char is not None:
            self._move_combatant(char, cell, kind)

    def _arena_cell(self, cell: Cell):
        """An empty cell clicked with nobody picked up, and no kept area on
        it: nothing moves, as a stray click shouldn't move whoever's turn it
        is, and a kept area selected is deselected."""
        self._deselect_area()
        self._show_status("Click a combatant, then the cell it moves to.")

    @undoable
    def _move_combatant(self, char: dict, cell: Cell, kind: MoveKind = MoveKind.WALK):
        """Put char's anchor on `cell`: one undo step. One not on the map yet
        is placed there, or on the nearest free cell (the plan's Q4), and
        moves nothing. One on it walks there, by the cheapest way, and its
        feet moved this turn grow by that, or by the straight distance when
        no walk gets there (walled in); it can't end on anyone (Q4), but
        where what it has lets it (can_end_at: a Swarm's space, inside a
        wall with Incorporeal Movement). The move is a GM-only log line
        (Q3), and going past its Speed is warned about, not refused (Q2).

        A teleport or a push (`kind`, step 17) isn't char's own movement:
        it spends none (Rules Glossary, Teleportation: it "doesn't expend
        movement"), reminds of no Opportunity Attack ("never provokes"), and
        its line says which, with the straight distance. It ends only where
        a walk could (a teleport onto someone appears "in the nearest
        unoccupied space of your choice": the GM clicks that one), and
        areas and hazards entered are reminded of as for a walk."""
        lines = self._relocate(char, cell, kind)
        lines += self._end_stretched_grapples()
        if lines:
            self._show_status(" ".join(lines))
        self._refresh_views()

    def _relocate(
        self,
        char: dict,
        cell: Cell,
        kind: MoveKind = MoveKind.WALK,
        pulled: bool = False,
    ) -> list[str]:
        """_move_combatant's move, without the status line or the redraw:
        what it has to say (a refusal, the warnings and reminders), for the
        caller to show. A push from the Custom Effect moves several in one
        Apply this way (_push_targets)."""
        settings, name = self._map_settings(), char["name"]
        if position(char) is None:
            anchor = nearest_free(char, [cell], self.characters, settings)
            if anchor is None:
                return [f"No room on the map for {name}."]
            char[POSITION_KEY] = anchor.to_list()
            self.arena_settings.in_use = True
            return []
        if position(char) == cell:
            return []
        if not can_end_at(char, cell, self.characters, settings):
            what = {
                MoveKind.WALK: "end a move",
                MoveKind.TELEPORT: "teleport",
                MoveKind.PUSH: "be pushed",
                MoveKind.DRAG: "be dragged",
            }[kind]
            nearest = (
                " A teleport there appears in the nearest unoccupied space of"
                " your choice instead (Teleportation): click that one."
                if kind is MoveKind.TELEPORT
                else ""
            )
            return [
                f"{name} can't {what} there: it's off the map, a wall,"
                " an object that blocks movement or someone else's space." + nearest
            ]
        start = position(char)
        before = who_is_in(self.characters, settings)
        hazards_before = hazards_under(char, settings)
        # Someone moved on the map: it's in use, and its distances count
        # from now on (Decision 29).
        settings.in_use = self.arena_settings.in_use = True
        warnings = []
        if kind is not MoveKind.WALK:
            feet = straight_ft(char, cell, settings) or 0
            char[POSITION_KEY] = cell.to_list()
            line = forced_move_line(char, start, cell, feet, kind, settings, pulled)
            self._log_event(line, public=False)
            warnings.append(line)
        else:
            walked = move_cost(char, self.characters, settings, cell)
            # The way it's taken to have walked, for whose reach it passed.
            path = walk_path(char, self.characters, settings, cell)
            feet = walked if walked is not None else straight_ft(char, cell, settings)
            feet = feet or 0
            # Whom it drags along (Rules Glossary, Grappled: Movable).
            held = [h for h in grappled_by(char, self.characters) if position(h)]
            char[POSITION_KEY] = cell.to_list()
            char[MOVED_KEY] = int(char.get(MOVED_KEY, 0)) + feet
            mode = mode_of(char)
            speed = speed_of_mode(char)
            if speed is None:
                speed = walking_speed_ft(char)
            self._log_event(
                move_line(
                    char, start, cell, feet, walked is not None, speed, settings, mode
                ),
                public=False,
            )
            movement = movement_ft(char)
            if movement is not None and char[MOVED_KEY] > movement:
                with_dash = f" ({movement} ft. with its {_dashes_text(char)})"
                warnings.append(
                    f"{name} moved {char[MOVED_KEY]} ft., {SPEED_NAMES[mode]}"
                    f" {speed} ft." + (with_dash if dashes(char) else "")
                )
            # Dragged first: the creature it holds is still beside it when
            # its walk is measured for Opportunity Attacks.
            if held and start is not None:
                warnings += self._drag(char, start, held)
            if walked is not None and start is not None:
                warnings += self._opportunity_attack_reminders(char, start, path)
        if kind is MoveKind.WALK and has_condition(char, Condition.PRONE):
            stand = stand_up_ft(char)
            costs = "half its Speed" if stand is None else f"{stand} ft."
            warnings.append(f"{name} is Prone and crawls; standing up costs {costs}.")
        if any(
            settings.terrain.blocks(c) for c in footprint(char, settings.distance_rule)
        ):
            sources = ", ".join(movement_rules(char).sources)
            warnings.append(
                f"{name} is inside a wall or an object ({sources}): Incorporeal"
                " Movement deals 1d10 Force damage if its turn ends there."
            )
        # Whoever is in an area now that wasn't: the mover walking in, or
        # someone its Emanation moved onto. Each gets the area's button, when
        # its rules say it acts then (step 24).
        after = who_is_in(self.characters, settings)
        for who, (caster, area) in entered(before, after):
            line = f"{who} enters {caster}'s {area}."
            self._log_event(line, character=who, public=False)
            warnings.append(line)
            self._area_entered(who, caster, area, ENTERS if who == name else MOVED_ONTO)
        for hazard in hazards_under(char, settings):
            if hazard not in hazards_before:
                line = f"{name} enters a hazard: {hazard}."
                self._log_event(line, character=name, public=False)
                warnings.append(line)
        return warnings

    def _drag(self, grappler: dict, start: Cell, held: list[dict]) -> list[str]:
        """Take each of `held`, Grappled by `grappler`, along on its walk
        from `start` (grapples.dragged_to: as far and the same way, else the
        nearest cell within the grapple's range), as a drag: no movement of
        its own spent, no Opportunity Attack for it. Says what it cost the
        grappler: 1 extra foot a foot unless the creature is Tiny or two
        sizes smaller, counted in the walk already (arena.reachable). One
        with nowhere to go stays, and the grapple's range may end it."""
        settings = self._map_settings()
        lines = []
        for creature in held:
            to = dragged_to(creature, grappler, start, self.characters, settings)
            if to is not None and to != position(creature):
                lines += self._relocate(creature, to, MoveKind.DRAG)
        costly = [h["name"] for h in held if drag_costs_extra(grappler, h)]
        if costly:
            lines.append(
                f"{grappler['name']} drags {_and(costly)}: each foot of the walk"
                " costs 1 extra foot."
            )
        return lines

    def _end_stretched_grapples(self) -> list[str]:
        """End each grapple a move has pulled past its range (Rules
        Glossary, Grappling: it ends "if the distance between the Grappled
        target and the grappler exceeds the grapple's range"): Grappled
        comes off, logged, and a line for the status."""
        lines = []
        for gap in stretched(self.characters, self._map_settings()):
            name = gap.held["name"]
            self._remove_condition_from(
                gap.held, Condition.GRAPPLED.value, source=gap.grappler
            )
            line = (
                f"{gap.grappler['name']}'s grapple on {name} ends: {gap.feet} ft."
                f" apart, past its {gap.range_ft} ft. range."
            )
            self._log_event(line, character=name, public=False)
            lines.append(line)
        return lines

    def _push_targets(
        self, pusher: dict, push: CombatPush, targets: list[dict], label: str
    ) -> list[str]:
        """Move each of `targets` (those `label` landed on) as `push` says,
        straight away from `pusher` or toward it (Combat/Arena/pushes.py), as
        Push moves: no movement spent, no Opportunity Attack, areas and
        hazards entered reminded of. Only once the map is in use (Decision
        29) and with both on it; one too big for it ("Large or smaller")
        stays. Part of the Apply's undo step. Returns the lines to show:
        each move's, and what stopped one short ("Goblin stops after 5 of
        10 ft.: the map's edge.")."""
        settings = self._map_settings()
        if not settings.in_use or position(pusher) is None:
            return []
        lines = []
        for target in push_order(targets, pusher, push, settings):
            if not any(target is c for c in self.characters):
                continue  # a summon that vanished
            name = target["name"]
            if too_big(target, push):
                size = push.largest.value if push.largest else ""
                line = f"{name} isn't moved by {label}: only {size} or smaller is."
                self._log_event(line, character=name, public=False)
                lines.append(line)
                continue
            result = push_destination(target, pusher, push, self.characters, settings)
            if result is None:
                continue
            if result.feet:
                lines += self._relocate(target, result.to, MoveKind.PUSH, push.toward)
            if result.stopped_by:
                line = (
                    f"{name} stops after {result.feet} of {push.feet} ft.:"
                    f" {result.stopped_by}."
                )
                self._log_event(line, character=name, public=False)
                lines.append(line)
        return lines + self._end_stretched_grapples()

    def _opportunity_attack_reminders(
        self, char: dict, start: Cell, path: list[Cell] | None = None
    ) -> list[str]:
        """Who can make an Opportunity Attack on char, whose walk from
        `start` on its own turn took it out of their reach anywhere along
        `path`, the way it walked (opportunity_attackers, step 23), as
        GM-only log lines and for the status line, and a turn-column button
        for each that opens Use / Cast with it as the source, char as the
        target, its melee attack picked and its Reaction as the cost: none
        for a Disengaged char (Rules Glossary, Disengage); for one with
        Flyby, the GM judges whether it flew. Polearm Master's Reactive
        Strike too, for a walk that entered such a reach, Disengaged or
        not. A creature char drags isn't one: it went along. A move on
        someone else's turn (a shove, a correction) reminds of nothing: it
        may not be char's own movement."""
        if not any(char is c for c in self._current_turn_group()):
            return []
        dragged = grappled_by(char, self.characters)
        attackers = [
            a
            for a in opportunity_attackers(
                char, start, self.characters, self._map_settings(), path
            )
            if not any(a is d for d in dragged)
        ]
        strikers = [
            a
            for a in (
                reactive_strikers(char, path, self.characters, self._map_settings())
                if path
                else []
            )
            if not any(a is d for d in dragged)
        ]
        name = char["name"]
        lines = []
        new: list[OpportunityAttack] = []
        if attackers:
            names = _and([a["name"] for a in attackers])
            if DISENGAGE in char["conditions"]:
                line = (
                    f"{name} leaves {names}'s reach, Disengaged: no Opportunity"
                    " Attack."
                )
            elif _has_trait(char, "Flyby"):
                line = (
                    f"{name} leaves {names}'s reach: no Opportunity Attack if it"
                    " flies (Flyby)."
                )
            else:
                each = " each" if len(attackers) > 1 else ""
                line = (
                    f"{name} leaves {names}'s reach: an Opportunity Attack{each},"
                    " a Reaction, if they can see it. Disengage would have"
                    " stopped it."
                )
            lines.append(line)
            if DISENGAGE not in char["conditions"]:
                new += [
                    OpportunityAttack(a, char, opportunity_attack_row(a))
                    for a in attackers
                ]
        if strikers:
            names = _and([a["name"] for a in strikers])
            lines.append(
                f"{name} enters {names}'s reach: Reactive Strike (Polearm"
                " Master), a Reaction."
            )
            new += [
                OpportunityAttack(
                    a, char, opportunity_attack_row(a), name="Reactive Strike"
                )
                for a in strikers
            ]
        if new:
            # One button per attacker, mover and kind, however often it walks.
            pending = {
                (id(p.attacker), id(p.target), p.name)
                for p in self._hit_prompts
                if isinstance(p, OpportunityAttack)
            }
            self._hit_prompts = (
                *self._hit_prompts,
                *(
                    p
                    for p in new
                    if (id(p.attacker), id(p.target), p.name) not in pending
                ),
            )
            self._refresh_turn_prompts()
        for line in lines:
            self._log_event(line, character=name, public=False)
        return lines

    def _distance_note(self, target: dict) -> str:
        """ " (25 ft.)": how far `target` is from the source, for the target
        label in either view, and its cover from the source on the map once
        it's in use (" (25 ft., Half Cover from Barrel at C4)"), and
        whether the source sees it (" (25 ft., Edmund can't see it: Ogre is
        Invisible)"); "" unless both are on the map and differ."""
        source = self.selected_character
        notes = []
        if source is not None and source is not target:
            feet = distance_ft(source, target, self.arena_settings)
            if feet is not None:
                notes.append(f"{feet} ft.")
            reading = self._map_cover(source, target)
            if reading.total:
                notes.append(f"Total Cover from {reading.by}: can't be targeted")
            elif reading:
                notes.append(f"{reading.state} from {reading.by}")
        obscured = obscured_text(target, self.arena_settings)
        seen = self._sees(source, target) if source is not target else None
        if obscured and not (seen is not None and seen.obscured):
            notes.append(obscured)
        # What the source sees of it (step 28): "Edmund can't see it: Ogre
        # is Invisible", "Edmund sees it by Darkvision 60 ft.".
        if seen is not None and source is not None and seen.can is not None:
            who = source["name"]
            if not seen.can:
                notes.append(f"{who} can't see it: {seen.why}")
            elif seen.why:
                notes.append(f"{who} sees it by {seen.why}")
        return f" ({', '.join(notes)})" if notes else ""

    def _arena_distance(self, cell: Cell) -> str | None:
        """What hovering `cell` shows: how far it, or the creature on it, is
        from the source ("25 ft."); None without a source on the map, or
        over the source itself."""
        source = self.selected_character
        lasting = lasting_areas(self.characters, self._map_settings())
        names = [area.name for area in areas_at(cell, lasting)]
        names += [
            f"{area.name}'s damaging side"
            for area in lasting
            if cell in area.side and cell not in area.cells
        ]
        names += self.arena_settings.terrain.describe(cell)
        inside = " · ".join(names) if names else None
        if source is None:
            return inside
        rule = self.arena_settings.distance_rule
        on_it = occupied(self.characters, rule).get(cell)
        if on_it is source:
            return inside
        if on_it is not None:
            feet = distance_ft(source, on_it, self.arena_settings)
        else:
            feet = distance_to_cell_ft(source, cell, self.arena_settings)
        if feet is None:
            return inside
        return f"{feet} ft." + (f" · {inside}" if inside else "")

    def _area_where(self, record: dict) -> str:
        """Where a kept area is, for the log: Combat/Fight/effects_given.py's
        area_where."""
        return run_step(self, area_where, record)

    def _log_area_kept(self, holder: dict, label: str, record: dict):
        """The GM-only log line for an area put on the map:
        effects_given.py's log_area_kept."""
        run_step(self, log_area_kept, holder, label, record)

    def _hold_area(self, holder: dict, label: str, effect: CustomEffect):
        """Keep effect's area on the map with no concentration: an active
        spell of holder's that lasts as long as the spell does (Grease's
        minute, by its pick or its name), else the effect's time (a
        turn-long one, a round; none, an hour), and holds nothing else, so
        ending it takes only the area away (Grease's Prone stays)."""
        record = effect.area
        if record is None:
            return
        pick = effect.pick
        name = (pick.spell_name or pick.name) if pick is not None else effect.name
        spell = _spell_named(name) if name else None
        seconds = spell.duration_seconds if spell is not None else None
        if not seconds:
            duration = effect.duration or {}
            seconds = duration.get("seconds")
            if seconds is None and "until" in duration:
                seconds = SECONDS_PER_ROUND
        seconds = seconds or LONGEST_AREA
        turn = self._current_turn_group()
        holder.setdefault("active_spells", []).append(
            {
                "name": label,
                "time_left": seconds,
                "duration": seconds,
                "concentration": False,
                "applied": [],
                "ticks_on": turn[0]["name"] if turn else None,
                AREA_KEY: record,
            }
        )
        self._log_area_kept(holder, label, record)
        self._rebuild_card(holder)

    def _remind_lasting_areas(self, group: list[dict], ended: list[dict] | None = None):
        """Whoever starts its turn in an area that stays, or in a hazard, and
        whoever just ended its turn in an area (`ended`): a GM-only log line
        each ("Goblin starts its turn in Clover's Moonbeam."), and for an
        area whose rules act then (record_timing: Web as a turn starts,
        Moonbeam as one ends), its button in the turn column (an
        AreaPrompt, step 24). A hazard is a reminder in the turn column, as
        what starting the turn did."""
        if self.phase != Phase.COMBAT:
            return
        settings = self._map_settings()
        areas = lasting_areas(self.characters, settings)
        for when, chars, verb in (
            (ENDS, ended or [], "ends"),
            (STARTS, group, "starts"),
        ):
            for char in chars:
                if self._char_death_state(char) == "dead":
                    continue
                holding = areas_holding(char, areas, settings) if areas else []
                for area in holding:
                    self._offer_area_prompt(
                        area.key, char, when, self._turn_start_prompts
                    )
                # By a wall's damaging side (Wall of Fire): as a turn ends.
                beside = (
                    areas_beside(char, areas, settings)
                    if areas and when == ENDS
                    else []
                )
                for area in beside:
                    self._offer_area_prompt(
                        area.key, char, when, self._turn_start_prompts, beside=True
                    )
                    line = (
                        f"{char['name']} ends its turn by {area.title}'s damaging side."
                    )
                    self._log_event(line, character=char["name"], public=False)
                names = [area.title for area in holding]
                hazards = hazards_under(char, settings) if when == STARTS else []
                if not names and not hazards:
                    continue
                line = (
                    f"{char['name']} {verb} its turn in {', '.join(names + hazards)}."
                )
                self._log_event(line, character=char["name"], public=False)
                if hazards:
                    self._turn_start_notes.append(
                        f"{char['name']} starts its turn in {', '.join(hazards)}."
                    )

    def _area_entered(self, who: str, caster: str, area: str, when: str):
        """`who` is in caster's kept area `area` now (walked in, ENTERS, or
        the area came onto it, MOVED_ONTO): its button, when its rules act
        then, kept with the hit prompts for the rest of the turn."""
        char = self._arena_char(who)
        owner = self._arena_char(caster)
        if char is None or owner is None:
            return
        prompts = list(self._hit_prompts)
        for entry in owner.get(ACTIVE_SPELLS_KEY) or []:
            if entry.get(AREA_KEY) and entry["name"] == area:
                self._offer_area_prompt(
                    area_key(owner, entry), char, when, prompts, self._turn_prompts
                )
        if len(prompts) != len(self._hit_prompts):
            self._hit_prompts = tuple(prompts)
            self._refresh_turn_prompts()

    def _offer_area_prompt(
        self,
        key: str,
        char: dict,
        when: str,
        prompts: list,
        also: Iterable = (),
        beside: bool = False,
    ):
        """Add to `prompts` the button for kept area `key` acting on char
        `when`, if its rules say it acts then (an area acting on who enters
        it acts on who it's moved onto too), it's in combat, and there isn't
        one for the same area and creature in `prompts` or `also` already
        (a creature makes its save "only once per turn"). `beside`: char
        ended its turn by a wall's damaging side, not in it."""
        found = find_area(self.characters, key)
        if self.phase != Phase.COMBAT or found is None:
            return
        caster, entry = found
        if self._char_death_state(char) == "dead":
            return
        if when not in record_timing(entry[AREA_KEY], entry["name"]):
            return
        if any(
            isinstance(p, AreaPrompt) and p.key == key and p.target is char
            for p in (*prompts, *also)
        ):
            return
        prompts.append(
            AreaPrompt(caster, char, entry["name"], key, when, beside=beside)
        )

    def _kept_area_answers(self, firing) -> bool:
        """Whether a badge's turn trigger (Spirit Guardians' "if it ends its
        turn in the Emanation") is answered by its area on the map instead:
        the badge's caster keeps an area of the badge's name, the map is in
        use and the creature is on it, so the area's own button comes when
        it's in it, and none when it isn't."""
        caster = self._arena_char(firing.caster or firing.bearer["name"])
        if caster is None or not self.arena_settings.in_use:
            return False
        if position(firing.target) is None:
            return False
        return any(
            entry.get(AREA_KEY) and entry["name"] == firing.badge
            for entry in caster.get(ACTIVE_SPELLS_KEY) or []
        )

    def _use_area_prompt(self, prompt: AreaPrompt):
        """A kept area's button pressed: the Use / Cast dialog on its effect
        (area_effect_row: Spirit Guardians' damage row, Moonbeam's own),
        its caster the source and the creature the target, costing nothing
        (the dialog's kept_area). The button goes once it's used, or when
        the area has ended."""
        target = self._find_character_by_name(prompt.target["name"])
        if target is None:
            self._show_status(f"{prompt.target['name']} is no longer in the fight.")
            return
        self._hit_prompts = tuple(p for p in self._hit_prompts if p is not prompt)
        self._turn_prompts = [p for p in self._turn_prompts if p is not prompt]
        found = find_area(self.characters, prompt.key)
        if found is None:
            self._refresh_turn_prompts()
            self._show_status(f"{prompt.title} has ended.")
            return
        caster, entry = found
        row = area_effect_row(caster, entry[AREA_KEY].get("pick") or entry["name"])
        self._select_character(caster)
        self._set_targets([target])
        self._refresh_views()
        self._refresh_turn_prompts()
        self._show_custom_condition_dialog(pick=row, kept_area=prompt.key)


def _wall_placed(area: AreaOfEffect, ends: list[Cell]) -> bool:
    """Whether a Wall's clicks so far put it: a ring's middle, or a
    straight wall's two ends."""
    return len(ends) >= (1 if area.ring else 2)


def _wall_end(area: AreaOfEffect, ends: list[Cell]) -> Cell | None:
    """A straight wall's second end once clicked; None for a ring."""
    return ends[1] if not area.ring and len(ends) > 1 else None


def _wall_notes(record: dict) -> list[str]:
    """What the area panel says of a kept wall besides its shape: its
    terrain ("blocks movement, Total Cover") and its damaging side ("the
    south side deals damage")."""
    area = record_area(record)
    if not area.is_wall:
        return []
    notes = []
    data = record.get("terrain")
    if isinstance(data, dict):
        thing = MapObject.from_dict(data)
        said = thing.describe()[len(thing.name) :].strip(" ()")
        if said:
            notes.append(said)
    side = record.get("side")
    if side and record.get("aim") is not None:
        aim = Cell.of(record["aim"])
        name = side_name(area, aim, record_end(record), int(side))
        notes.append(f"the {name} side deals damage")
    return notes


def hazards_under(char: dict, settings: ArenaSettings) -> list[str]:
    """The hazards painted under char ("Campfire at C7"), in cell order."""
    shape = settings.distance_rule.shape
    found = []
    for cell in sorted(footprint(char, settings.distance_rule)):
        hazard = settings.terrain.hazard(cell)
        if hazard is not None:
            found.append(f"{hazard.name} at {shape.cell_name(cell)}")
    return found


def obscured_text(char: dict, settings: ArenaSettings) -> str:
    """ "Heavily Obscured" when every cell char is on is in Darkness,
    "Lightly Obscured" when none is brighter than Dim Light, else "" (a
    creature partly in the light can be seen there)."""
    cells = footprint(char, settings.distance_rule)
    if not cells:
        return ""
    lights = {settings.terrain.at(cell).light for cell in cells}
    if BRIGHT in lights:
        return ""
    return OBSCURED[DIM] if DIM in lights else OBSCURED[DARK]


def area_reading(option: EffectOption | None) -> tuple[AreaOfEffect | None, int | None]:
    """The area a Custom Effect pick has (EffectOption.area: its
    CombatEffect's, or its spell's SpellRules.area) and how far away its
    point may be: the area's own point_within_ft ("a point you can see
    within 60 feet"), else the range of the spell it casts ("150 feet").
    (None, None) for no pick; (None, range) for a pick without an area."""
    if option is None:
        return None, None
    name = option.spell_name or (option.name if option.kind == SPELL else "")
    spell = _spell_named(name) if name else None
    range_ft = spell_range_ft(spell) if spell is not None else None
    rules = option.area
    if rules is not None and rules.point_within_ft is not None:
        range_ft = rules.point_within_ft
    return area_of(rules), range_ft


def area_lasts(option: EffectOption | None) -> bool:
    """Whether a pick's area stays on the map once used, as the bar's "Keep
    on the map" starts: a spell's (or the spell a feature casts) when it
    isn't Instantaneous, anything else when it needs Concentration."""
    if option is None:
        return False
    name = option.spell_name or (option.name if option.kind == SPELL else "")
    spell = _spell_named(name) if name else None
    if spell is not None:
        return bool(spell.duration_seconds)
    return option.concentration


def _color_combo(object_name: str) -> QComboBox:
    """A list of AREA_COLORS, each with its swatch, then "Other..."."""
    combo = QComboBox()
    combo.setObjectName(object_name)
    combo.setToolTip("The colour the area is shaded in")
    for name, color in AREA_COLORS:
        combo.addItem(_swatch(color), name, color)
    combo.addItem("Other...", OTHER_COLOR)
    return combo


def show_color(combo: QComboBox, color: str):
    """Select `color` in a colour list (without its signal), adding it
    before "Other..." when it isn't one of the colours there yet."""
    index = combo.findData(color)
    if index < 0:
        index = combo.count() - 1
        combo.insertItem(index, _swatch(color), color, color)
    combo.blockSignals(True)
    combo.setCurrentIndex(index)
    combo.blockSignals(False)


def _swatch(color: str) -> QIcon:
    """A small square of `color`, for the bar's colour list."""
    pixmap = QPixmap(_SWATCH_PX, _SWATCH_PX)
    pixmap.fill(QColor(color))
    return QIcon(pixmap)


def _and(names: list[str]) -> str:
    """ "A", "A and B", "A, B and C"."""
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"


def _has_trait(char: dict, name: str) -> bool:
    """Whether char's stat block has a trait called `name` (Flyby)."""
    return any(
        (t.get("name") if isinstance(t, dict) else getattr(t, "name", None)) == name
        for t in char.get("traits") or ()
    )


def _dashes_text(char: dict) -> str:
    """ "Dash", "2 Dashes": the Dash actions char took this turn."""
    count = dashes(char)
    return "Dash" if count == 1 else f"{count} Dashes"


def move_line(
    char: dict,
    start: Cell | None,
    to: Cell,
    feet: int,
    walked: bool,
    speed: int | None,
    settings: ArenaSettings,
    mode: str = WALK,
) -> str:
    """The encounter log's line for char's move from `start` to `to`, which
    cost `feet` (char's "moved_ft" already counts it): "Clover moves from A7
    to C8 (15 ft.; 15 of 30 ft. left this turn)." With no walk there (walled
    in), it "goes" and the feet are the straight line's. By another speed
    (`mode`, step 26), its verb and that speed's name: "Wyvern flies from
    ... (all of its 80 ft. Fly Speed used)"."""
    shape = settings.distance_rule.shape
    where = f"from {shape.cell_name(start) if start else '?'} to {shape.cell_name(to)}"
    name = char["name"]
    head = (
        f"{name} {VERBS[mode]} {where}"
        if walked
        else f"{name} goes {where}, with no way to walk there"
    )
    cost = f"{feet} ft." if walked else f"{feet} ft. in a straight line"
    if speed is None:
        return f"{head} ({cost})."
    moved = int(char.get(MOVED_KEY, 0))
    # With a Dash, its Speed more (movement_ft).
    total = speed + dashes(char) * (walking_speed_ft(char) or speed)
    speed_name = SPEED_NAMES[mode]
    of = f"its {total} ft. with its {_dashes_text(char)}" if dashes(char) else ""
    if moved < total:
        left = f"{total - moved} of {total} ft. left this turn"
        if of:
            left += f" ({_dashes_text(char)})"
    elif moved == total:
        left = (
            f"all of {of} used" if of else f"all of its {speed} ft. {speed_name} used"
        )
    else:
        left = f"{moved - total} ft. past {of or f'its {speed} ft. {speed_name}'}"
    return f"{head} ({cost}; {left})."


def forced_move_line(
    char: dict,
    start: Cell | None,
    to: Cell,
    feet: int,
    kind: MoveKind,
    settings: ArenaSettings,
    pulled: bool = False,
) -> str:
    """The encounter log's line for a move that isn't char's own (step 17),
    `feet` the straight distance: "Kivi teleports from A7 to D7 (15 ft.;
    no movement spent)." or "Goblin is pushed from C4 to C5 (5 ft.; no
    movement spent)." for a push ("is pulled" for a pull, step 21)."""
    shape = settings.distance_rule.shape
    where = f"from {shape.cell_name(start) if start else '?'} to {shape.cell_name(to)}"
    if kind is MoveKind.TELEPORT:
        verb = "teleports"
    elif kind is MoveKind.DRAG:
        verb = "is dragged"
    else:
        verb = "is pulled" if pulled else "is pushed"
    return f"{char['name']} {verb} {where} ({feet} ft.; no movement spent)."
