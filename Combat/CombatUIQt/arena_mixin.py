"""The battle map in the combat window (Notes/combat-arena-plan.md, steps
4-5): the Arena page beside the cards, the Cards/Arena switch (G and the
turn column's button, the view last used remembered in the settings store), and the map brought up
to date with the cards. Selection, the control panel, the turn column and
undo are the window's, shared by both views (the plan's Decision 2)."""

from PyQt6.QtWidgets import QPushButton, QStackedWidget, QWidget

from Combat.Arena.arena import place_new

from .arena_view import ArenaView, token_rows
from .settings import ARENA_VIEW_KEY
from .state import CombatWindowState

CARDS_PAGE, ARENA_PAGE = 0, 1


class ArenaMixin(CombatWindowState):
    def _build_view_stack(self, cards: QWidget) -> QStackedWidget:
        """The cards' scroll area (`cards`) as page 0 and the map as page 1,
        in the cards' place in the window."""
        self._arena_view = ArenaView(self._arena_select, self._arena_target)
        self._view_stack = QStackedWidget()
        self._view_stack.addWidget(cards)
        self._view_stack.addWidget(self._arena_view)
        return self._view_stack

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
