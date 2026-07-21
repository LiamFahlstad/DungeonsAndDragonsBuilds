"""Conditions mixin for CombatAppQt."""

from Combat.Definitions import Action, Condition


class ConditionsMixin:
    """Mixin for condition and visibility management."""

    def _add_condition_to(self, char: dict, cond: str):
        if cond not in char["conditions"]:
            char["conditions"].append(cond)
            self.history.append((Action.ADD_CONDITION, cond))
            self._log_event(f"{char['name']} gains {cond}")
            self._rebuild_card(char)

    def _remove_condition_from(self, char: dict, cond: str):
        if cond in char["conditions"]:
            char["conditions"].remove(cond)
            self.history.append((Action.REMOVE_CONDITION, cond))
            self._log_event(f"{char['name']} loses {cond}")
            self._rebuild_card(char)

    def _add_condition(self):
        if not self.selected_character:
            return
        self._add_condition_to(self.selected_character, self.condition_combo.currentText())

    def _remove_condition(self):
        if not self.selected_character:
            return
        self._remove_condition_from(self.selected_character, self.condition_combo.currentText())

    def _shortcut_add_concentration(self):
        """Keyboard shortcut 'C': add Concentrating to the source."""
        if not self.selected_character:
            return
        self._add_condition_to(self.selected_character, Condition.CONCENTRATING.value)

    def _shortcut_remove_concentration(self):
        """Keyboard shortcut 'Ctrl+C': remove Concentrating from the source."""
        if not self.selected_character:
            return
        self._remove_condition_from(self.selected_character, Condition.CONCENTRATING.value)

    def _shortcut_clear_target_conditions(self):
        """Keyboard shortcut 'Ctrl+Shift+C': remove every condition from the target."""
        if not self.target_character:
            return
        for cond in list(self.target_character.get("conditions", [])):
            self._remove_condition_from(self.target_character, cond)

    def _add_action_use(self, action_type: str):
        """Log a use of Action/Bonus Action/Reaction for the source, this round.
        Tallies reset when it becomes that combatant's turn again (see _advance_turn)."""
        if not self.selected_character:
            return
        counts = self.selected_character.setdefault("action_uses", {})
        counts[action_type] = counts.get(action_type, 0) + 1
        self._log_event(f"{self.selected_character['name']} uses {action_type}")
        self._refresh_selected_card()

    def _remove_action_use(self, action_type: str):
        """Correct a mis-logged Action/Bonus Action/Reaction use for the source."""
        if not self.selected_character:
            return
        counts = self.selected_character.setdefault("action_uses", {})
        if counts.get(action_type, 0) > 0:
            counts[action_type] -= 1
            self._log_event(f"{self.selected_character['name']} refunds {action_type}")
            self._refresh_selected_card()

    def _add_visibility(self):
        if not self.selected_character:
            return
        vis = self.visibility_combo.currentText()
        visibility_states = self.selected_character.get("visibility_states", [])
        if vis not in visibility_states:
            visibility_states.append(vis)
            self._log_event(f"{self.selected_character['name']} gains {vis}")
            self._refresh_selected_card()

    def _remove_visibility(self):
        if not self.selected_character:
            return
        vis = self.visibility_combo.currentText()
        visibility_states = self.selected_character.get("visibility_states", [])
        if vis in visibility_states:
            visibility_states.remove(vis)
            self._log_event(f"{self.selected_character['name']} loses {vis}")
            self._refresh_selected_card()
