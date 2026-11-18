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
nobody in it (Moonbeam on empty ground). Whoever walks into one, or starts
a turn in one, gets a reminder in the status line and a GM-only log line.

Selecting a kept area (step 12): a click on an empty cell of one brings up
the area panel over the map: whose it is, where, how long it has left and
its rules text, with its colour to change, Target who's in it, End spell,
and Close (or Esc). The selection is the window's, as the source is, but an
area is never a source.

The painted map (Notes/map-painter-plan.md): a fight starting puts whoever
the encounter's map gives a starting cell there; the hover names what's
painted on a cell, the target label says when a target is Lightly or
Heavily Obscured, and walking onto a hazard (a campfire, a trap) or starting
a turn on one is a reminder, as an area that stays is."""

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

from Combat.Arena.arena import (
    MOVED_KEY,
    POSITION_KEY,
    ArenaSettings,
    can_end_at,
    distance_ft,
    distance_to_cell_ft,
    footprint,
    dashes,
    move_cost,
    movement_ft,
    movement_rules,
    nearest_free,
    opportunity_attackers,
    occupied,
    place_new,
    position,
    reachable,
    remaining_ft,
    stand_up_ft,
    straight_ft,
    walking_speed_ft,
)
from Combat.Arena.areas import (
    AreaOfEffect,
    AreaShape,
    area_cells,
    creatures_in,
    parse_area,
    point_range_ft,
    spell_range_ft,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import (
    AREA_KEY,
    DEFAULT_AREA_COLOR,
    LastingArea,
    area_record,
    areas_at,
    areas_holding,
    entered,
    find_area,
    lasting_areas,
    record_area,
    record_cells,
    time_left_text,
    who_is_in,
)
from Combat.Arena.maps import place_at_starts
from Combat.Arena.pushes import push_destination, push_order, too_big
from Combat.Arena.terrain import BRIGHT, DARK, DIM, OBSCURED
from Combat.Effects.modifiers import has_condition
from Combat.Effects.triggers import OpportunityAttack
from Model.Content.CombatEffect import CombatPush
from Model.Content.StandardActions import DISENGAGE
from Core.Definitions import Condition
from Core.Rules import SECONDS_PER_ROUND

from .arena_view import ArenaView, MoveKind, token_rows
from .effect_options import _spell_named, opportunity_attack_row
from .saves import SPELL, CustomEffect, EffectOption
from .settings import ARENA_VIEW_KEY
from .state import CombatWindowState
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
        )

    def _show_area_in_bar(self, area: AreaOfEffect):
        for box in (
            self._area_shape,
            self._area_size,
            self._area_width,
            self._area_from_source,
        ):
            box.blockSignals(True)
        self._area_shape.setCurrentIndex(self._area_shape.findData(area.shape))
        self._area_size.setValue(area.size_ft)
        self._area_width.setValue(area.width_ft)
        self._area_from_source.setChecked(area.from_source)
        for box in (
            self._area_shape,
            self._area_size,
            self._area_width,
            self._area_from_source,
        ):
            box.blockSignals(False)
        self._show_area_controls()

    def _show_area_controls(self):
        """A Line's width, and From the source for the shapes it changes."""
        shape = self._area_shape.currentData()
        self._area_width_label.setVisible(shape is AreaShape.LINE)
        self._area_width.setVisible(shape is AreaShape.LINE)
        self._area_from_source.setVisible(
            shape in (AreaShape.SPHERE, AreaShape.CYLINDER, AreaShape.CUBE)
        )

    def _area_changed(self):
        self._show_area_controls()
        if self._area_targeting is not None:
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
        if self.phase != "COMBAT" or source is None or position(source) is None:
            self._show_status("Targets in an area need the source on the map.")
            return False
        area, range_ft = area_reading(option)
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
        }
        self._show_area_in_bar(area or self._last_area)
        self._last_area = self._area_in_bar()
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
        return True

    def _area_cells_at(self, aim: Cell | None) -> set[Cell]:
        request = self._area_targeting
        if request is None:
            return set()
        return area_cells(
            self._area_in_bar(), request["source"], aim, self.arena_settings
        )

    def _show_area_count(self, cells: set[Cell]):
        """The bar's text: the area, and who is in it where it's aimed."""
        request = self._area_targeting
        if request is None:
            return
        area = self._area_in_bar()
        head = f"{request['what']}: " if request["what"] else ""
        if not request["read"] and request["pick"]:
            head += "no area in its text, so check the shape. "
        inside = creatures_in(self.characters, cells, self.arena_settings)
        if not cells:
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
        if area.starts_at_source:
            return None
        feet = distance_to_cell_ft(request["source"], aim, self.arena_settings)
        if feet is None or feet <= request["range"]:
            return None
        return feet, request["range"]

    def _area_range_text(self) -> str:
        """The point aimed at against the range: "Aimed 45 ft. away, range
        150 ft." or "Aimed 160 ft. away: past its 150 ft. range!"; "" for an
        area that starts at the source, or without a range or an aim."""
        request = self._area_targeting
        aim = self._arena_view.area_aim
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
        cells = self._area_cells_at(cell)
        inside = creatures_in(self.characters, cells, self.arena_settings)
        keep = self._area_keep.isChecked()
        if not inside and not (keep and cells):
            self._show_status("Nobody is in that area: aim it somewhere else.")
            return
        past = self._area_out_of_range()
        area, source = self._area_in_bar(), request["source"]
        aim = cell if area.is_aimed else None
        record = area_record(
            area,
            source,
            aim,
            self.arena_settings,
            self._area_color_in_bar(),
            pick=request["pick"],
            about=request["about"],
        )
        self._end_area_targeting()
        # What the dialog, opened again, offers to keep on the map.
        self._aimed_area = {
            "source": source["name"],
            "record": record,
            "text": area.text,
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
        if self.phase != "COMBAT":
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
        arena = self.phase == "COMBAT" and self.arena_view_on
        stack.setCurrentIndex(ARENA_PAGE if arena else CARDS_PAGE)
        self._view_toggle_btn.setText("Cards" if arena else "Arena")
        self._view_toggle_btn.setVisible(self.phase == "COMBAT")
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
        place_new(self.characters, self.arena_settings)

    def _refresh_arena(self):
        """Bring the map up to date (from _refresh_views), when it's shown."""
        if not self._arena_shown():
            return
        self._refresh_off_map_strip()
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

    def _lasting_rows(self) -> list[LastingArea]:
        """The kept areas the map draws, the one selected marked; a
        selection whose area has ended (or covers nothing now) is dropped."""
        rows = lasting_areas(self.characters, self.arena_settings)
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
        cells = record_cells(entry[AREA_KEY], caster, self.arena_settings)
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
        return reachable(char, self.characters, self.arena_settings, remaining_ft(char))

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
        settings, name = self.arena_settings, char["name"]
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
        settings.in_use = True
        warnings = []
        if kind is not MoveKind.WALK:
            feet = straight_ft(char, cell, settings) or 0
            char[POSITION_KEY] = cell.to_list()
            line = forced_move_line(char, start, cell, feet, kind, settings, pulled)
            self._log_event(line, public=False)
            warnings.append(line)
        else:
            walked = move_cost(char, self.characters, settings, cell)
            feet = walked if walked is not None else straight_ft(char, cell, settings)
            feet = feet or 0
            char[POSITION_KEY] = cell.to_list()
            char[MOVED_KEY] = int(char.get(MOVED_KEY, 0)) + feet
            speed = walking_speed_ft(char)
            self._log_event(
                move_line(char, start, cell, feet, walked is not None, speed, settings),
                public=False,
            )
            movement = movement_ft(char)
            if movement is not None and char[MOVED_KEY] > movement:
                with_dash = f" ({movement} ft. with its {_dashes_text(char)})"
                warnings.append(
                    f"{name} moved {char[MOVED_KEY]} ft., Speed {speed} ft."
                    + (with_dash if dashes(char) else "")
                )
            if walked is not None and start is not None:
                warnings += self._opportunity_attack_reminders(char, start)
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
        # someone its Emanation moved onto.
        after = who_is_in(self.characters, settings)
        for who, (caster, area) in entered(before, after):
            line = f"{who} enters {caster}'s {area}."
            self._log_event(line, character=who, public=False)
            warnings.append(line)
        for hazard in hazards_under(char, settings):
            if hazard not in hazards_before:
                line = f"{name} enters a hazard: {hazard}."
                self._log_event(line, character=name, public=False)
                warnings.append(line)
        return warnings

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
        settings = self.arena_settings
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
        return lines

    def _opportunity_attack_reminders(self, char: dict, start: Cell) -> list[str]:
        """Who can make an Opportunity Attack on char, whose walk from
        `start` on its own turn took it out of their reach
        (opportunity_attackers), as GM-only log lines and for the status
        line, and a turn-column button for each that opens Use / Cast with
        it as the source, char as the target, its melee attack picked and its
        Reaction as the cost: none for a Disengaged char (Rules Glossary,
        Disengage); for one with Flyby, the GM judges whether it flew. A move
        on someone else's turn (a shove, a correction) reminds of nothing: it
        may not be char's own movement."""
        if not any(char is c for c in self._current_turn_group()):
            return []
        attackers = opportunity_attackers(
            char, start, self.characters, self.arena_settings
        )
        if not attackers:
            return []
        name = char["name"]
        names = _and([a["name"] for a in attackers])
        if DISENGAGE in char["conditions"]:
            line = f"{name} leaves {names}'s reach, Disengaged: no Opportunity Attack."
        elif _has_trait(char, "Flyby"):
            line = (
                f"{name} leaves {names}'s reach: no Opportunity Attack if it"
                " flies (Flyby)."
            )
        else:
            each = " each" if len(attackers) > 1 else ""
            line = (
                f"{name} leaves {names}'s reach: an Opportunity Attack{each}, a"
                " Reaction, if they can see it. Disengage would have stopped it."
            )
        if DISENGAGE not in char["conditions"]:
            # One button per attacker and mover, however often it walks out.
            pending = {
                (id(p.attacker), id(p.target))
                for p in self._hit_prompts
                if isinstance(p, OpportunityAttack)
            }
            self._hit_prompts = (
                *self._hit_prompts,
                *(
                    OpportunityAttack(a, char, opportunity_attack_row(a))
                    for a in attackers
                    if (id(a), id(char)) not in pending
                ),
            )
            self._refresh_turn_prompts()
        self._log_event(line, character=name, public=False)
        return [line]

    def _distance_note(self, target: dict) -> str:
        """ " (25 ft.)": how far `target` is from the source, for the target
        label in either view, and its cover from the source on the map once
        it's in use (" (25 ft., Half Cover from Barrel at C4)"); "" unless
        both are on the map and differ."""
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
        if obscured:
            notes.append(obscured)
        return f" ({', '.join(notes)})" if notes else ""

    def _arena_distance(self, cell: Cell) -> str | None:
        """What hovering `cell` shows: how far it, or the creature on it, is
        from the source ("25 ft."); None without a source on the map, or
        over the source itself."""
        source = self.selected_character
        lasting = lasting_areas(self.characters, self.arena_settings)
        names = [area.name for area in areas_at(cell, lasting)]
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
        """Where a kept area is, for the log: "around its caster", or "at
        C7" (the cell it was aimed at)."""
        if record.get("follows"):
            return "around its caster"
        aim = record.get("aim")
        if aim is None:
            return ""
        shape = self.arena_settings.distance_rule.shape
        return f"at {shape.cell_name(Cell.of(aim))}"

    def _log_area_kept(self, holder: dict, label: str, record: dict):
        """The GM-only log line for an area put on the map: "Clover's
        Moonbeam stays on the map at C7."."""
        where = self._area_where(record)
        self._log_event(
            f"{holder['name']}'s {label} stays on the map"
            + (f" {where}" if where else "")
            + ".",
            character=holder["name"],
            public=False,
        )

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

    def _remind_lasting_areas(self, group: list[dict]):
        """Whoever starts its turn in an area that stays: a reminder in the
        turn column, as what starting the turn did, and a GM-only log line
        ("Goblin starts its turn in Clover's Moonbeam."), as its rules may
        ask something of it now."""
        if self.phase != "COMBAT":
            return
        areas = lasting_areas(self.characters, self.arena_settings)
        for char in group:
            holding = [
                area.title
                for area in (
                    areas_holding(char, areas, self.arena_settings) if areas else []
                )
            ]
            holding += hazards_under(char, self.arena_settings)
            if not holding:
                continue
            names = ", ".join(holding)
            line = f"{char['name']} starts its turn in {names}."
            self._log_event(line, character=char["name"], public=False)
            self._turn_start_notes.append(line)


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
    """The area a Custom Effect pick states and how far away its point may
    be: a spell's (its own, or the one a feature or a monster's action
    casts) from its range ("Self (15-foot cone)" is the area, "150 feet"
    the reach) and its text; anything else from its text alone ("each
    creature in a 20-foot-radius Sphere centered on a point within 120
    feet"). A range of Self doesn't make the area start at the source:
    Investiture of Wind's Cube is "centered on a point you can see within
    60 feet". (None, None) for no pick."""
    if option is None:
        return None, None
    name = option.spell_name or (option.name if option.kind == SPELL else "")
    spell = _spell_named(name) if name else None
    text = option.tooltip
    range_ft = None
    if spell is not None:
        text = f"Range: {spell.range}. {text}"
        range_ft = spell_range_ft(spell.range)
    point = point_range_ft(option.tooltip)
    return parse_area(text), point if point is not None else range_ft


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
) -> str:
    """The encounter log's line for char's move from `start` to `to`, which
    cost `feet` (char's "moved_ft" already counts it): "Clover moves from A7
    to C8 (15 ft.; 15 of 30 ft. left this turn)." With no walk there (walled
    in), it "goes" and the feet are the straight line's."""
    shape = settings.distance_rule.shape
    where = f"from {shape.cell_name(start) if start else '?'} to {shape.cell_name(to)}"
    name = char["name"]
    head = (
        f"{name} moves {where}"
        if walked
        else f"{name} goes {where}, with no way to walk there"
    )
    cost = f"{feet} ft." if walked else f"{feet} ft. in a straight line"
    if speed is None:
        return f"{head} ({cost})."
    moved = int(char.get(MOVED_KEY, 0))
    # With a Dash, as much again as its Speed (movement_ft).
    total = speed * (1 + dashes(char))
    of = f"its {total} ft. with its {_dashes_text(char)}" if dashes(char) else ""
    if moved < total:
        left = f"{total - moved} of {total} ft. left this turn"
        if of:
            left += f" ({_dashes_text(char)})"
    elif moved == total:
        left = f"all of {of} used" if of else f"all of its {speed} ft. Speed used"
    else:
        left = f"{moved - total} ft. past {of or f'its {speed} ft. Speed'}"
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
    else:
        verb = "is pulled" if pulled else "is pushed"
    return f"{char['name']} {verb} {where} ({feet} ft.; no movement spent)."
