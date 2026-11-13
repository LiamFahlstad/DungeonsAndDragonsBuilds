"""The battle map in the combat window (Notes/combat-arena-plan.md, steps
4-6): the Arena page beside the cards, the Cards/Arena switch (G and the
turn column's button, the view last used remembered in the settings
store), the map brought up to date with the cards, and moving: a token
dragged, or the source sent to a clicked cell, one undo step each, with
the "Not on the map" strip for whoever has no place yet. Selection, the
control panel, the turn column and undo are the window's, shared by both
views (the plan's Decision 2)."""

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from Combat.Arena.arena import (
    MOVED_KEY,
    POSITION_KEY,
    fits_at,
    move_cost,
    nearest_free,
    place_new,
    position,
    reachable,
    remaining_ft,
    straight_ft,
    walking_speed_ft,
)
from Combat.Arena.geometry import Cell
from Combat.Effects.modifiers import has_condition
from Core.Definitions import Condition

from .arena_view import ArenaView, token_rows
from .settings import ARENA_VIEW_KEY
from .state import CombatWindowState
from .undo import undoable

CARDS_PAGE, ARENA_PAGE = 0, 1


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
        )
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self._build_off_map_strip())
        layout.addWidget(self._arena_view, stretch=1)
        self._view_stack = QStackedWidget()
        self._view_stack.addWidget(cards)
        self._view_stack.addWidget(page)
        return self._view_stack

    def _build_off_map_strip(self) -> QWidget:
        """The "Not on the map" strip: a button for each combatant without a
        place, which makes it the source; a click on a cell then puts it
        there (_arena_cell). Hidden while everyone is on the map."""
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
            button.setToolTip(f"Select {name}, then click a cell to put it there")
            button.clicked.connect(lambda _=False, n=name: self._arena_select(n))
            self._off_map_layout.addWidget(button)
        self._off_map_layout.addStretch()
        self._off_map_strip.show()

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
        """Starting cells for whoever isn't on the map yet (the plan's Q1),
        as a fight starts or is continued."""
        place_new(self.characters, self.arena_settings)

    def _refresh_arena(self):
        """Bring the map up to date (from _refresh_views), when it's shown."""
        if not self._arena_shown():
            return
        self._refresh_off_map_strip()
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
        )

    def _arena_char(self, name: str) -> dict | None:
        return next((c for c in self.characters if c["name"] == name), None)

    def _arena_select(self, name: str):
        char = self._arena_char(name)
        if char is not None:
            self._select_character(char)

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

    def _arena_move(self, name: str, cell: Cell):
        char = self._arena_char(name)
        if char is not None:
            self._move_combatant(char, cell)

    def _arena_cell(self, cell: Cell):
        """An empty cell clicked: the source goes there."""
        if self.selected_character is None:
            self._show_status("Select a combatant, then click where it goes.")
            return
        self._move_combatant(self.selected_character, cell)

    @undoable
    def _move_combatant(self, char: dict, cell: Cell):
        """Put char's anchor on `cell`: one undo step. One not on the map yet
        is placed there, or on the nearest free cell (the plan's Q4), and
        moves nothing. One on it walks there, by the cheapest way, and its
        feet moved this turn grow by that, or by the straight distance when
        no walk gets there (a teleport); it can't end on anyone (Q4). The
        move is a GM-only log line (Q3), and going past its Speed is warned
        about, not refused (Q2)."""
        settings, name = self.arena_settings, char["name"]
        if position(char) is None:
            anchor = nearest_free(char, [cell], self.characters, settings)
            if anchor is None:
                self._show_status(f"No room on the map for {name}.")
                return
            char[POSITION_KEY] = anchor.to_list()
            self._refresh_views()
            return
        if position(char) == cell:
            return
        if not fits_at(char, cell, self.characters, settings):
            self._show_status(
                f"{name} can't end a move there: it's off the map or"
                " someone else's space."
            )
            return
        walked = move_cost(char, self.characters, settings, cell)
        feet = walked if walked is not None else straight_ft(char, cell, settings)
        feet = feet or 0
        char[POSITION_KEY] = cell.to_list()
        char[MOVED_KEY] = int(char.get(MOVED_KEY, 0)) + feet
        how = "moves" if walked is not None else "goes (no walk gets there)"
        self._log_event(f"{name} {how} {feet} ft.", public=False)
        warnings = []
        speed = walking_speed_ft(char)
        if speed is not None and char[MOVED_KEY] > speed:
            warnings.append(f"{name} moved {char[MOVED_KEY]} ft., Speed {speed} ft.")
        if has_condition(char, Condition.PRONE):
            warnings.append(
                f"{name} is Prone and crawls; standing up costs half its Speed."
            )
        if warnings:
            self._show_status(" ".join(warnings))
        self._refresh_views()
