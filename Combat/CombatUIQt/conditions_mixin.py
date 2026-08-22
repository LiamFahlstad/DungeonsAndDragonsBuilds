"""Conditions mixin for CombatAppQt."""

from Combat.Definitions import Action, Condition
from .stats import _default_stats, increment_named_stat

# Conditions that incapacitate a creature and break concentration per 2024 D&D rules
INCAPACITATING_CONDITIONS = {"Incapacitated", "Paralyzed", "Petrified", "Stunned", "Unconscious"}


class ConditionsMixin:
    """Mixin for condition and visibility management."""

    def _add_condition_to(self, char: dict, cond: str, source: dict | None = None):
        if cond not in char["conditions"]:
            char["conditions"].append(cond)
            char.setdefault("stats", _default_stats())
            char["stats"]["conditions_received"] = char["stats"].get("conditions_received", 0) + 1
            increment_named_stat(char["stats"], "conditions_received_by_name", cond)
            source_name = source["name"] if source is not None else None
            if source is not None:
                source.setdefault("stats", _default_stats())
                source["stats"]["conditions_given"] = source["stats"].get("conditions_given", 0) + 1
                increment_named_stat(source["stats"], "conditions_given_by_name", cond)
            cond_value = {"condition": cond, "source_name": source_name, "target_name": char["name"]}
            self.history.append((Action.ADD_CONDITION, cond_value))
            source_suffix = (
                f" from {source_name}" if source_name and source_name != char["name"] else ""
            )
            self._log_event(
                f"{char['name']} gains {cond}{source_suffix}",
                character=char["name"],
                action=Action.ADD_CONDITION,
                value=cond_value,
            )
            self._rebuild_card(char)
            # Break concentration if an incapacitating condition is applied to a concentrating character
            if cond in INCAPACITATING_CONDITIONS and cond != "Concentrating" and "Concentrating" in char.get("conditions", []):
                self._remove_condition_from(char, "Concentrating", source=char)

    def _remove_condition_from(self, char: dict, cond: str, source: dict | None = None):
        if cond in char["conditions"]:
            char["conditions"].remove(cond)
            char.get("spell_condition_descriptions", {}).pop(cond, None)
            char.get("spell_condition_colors", {}).pop(cond, None)
            source_name = source["name"] if source is not None else None
            cond_value = {"condition": cond, "source_name": source_name, "target_name": char["name"]}
            self.history.append((Action.REMOVE_CONDITION, cond_value))
            source_suffix = (
                f" from {source_name}" if source_name and source_name != char["name"] else ""
            )
            self._log_event(
                f"{char['name']} loses {cond}{source_suffix}",
                character=char["name"],
                action=Action.REMOVE_CONDITION,
                value=cond_value,
            )
            if cond == Condition.CONCENTRATING.value:
                self._end_concentration_spells(char)
            self._rebuild_card(char)

    def _add_condition(self):
        """Add the selected condition to every target, attributed to the source
        (mirrors Damage/Heal/Temp HP's source → target model)."""
        if not self.target_characters:
            return
        source = self.selected_character or self._current_turn_character()
        cond = self.condition_combo.currentText()
        for target in list(self.target_characters):
            self._add_condition_to(target, cond, source=source)

    def _remove_condition(self):
        if not self.target_characters:
            return
        source = self.selected_character or self._current_turn_character()
        cond = self.condition_combo.currentText()
        for target in list(self.target_characters):
            self._remove_condition_from(target, cond, source=source)

    def _shortcut_add_concentration(self):
        """Keyboard shortcut 'C': the source starts Concentrating. Self-applied —
        a caster is always the source of their own concentration."""
        if not self.selected_character:
            return
        self._add_condition_to(
            self.selected_character, Condition.CONCENTRATING.value, source=self.selected_character
        )

    def _shortcut_remove_concentration(self):
        """Keyboard shortcut 'Ctrl+C': remove Concentrating from the source."""
        if not self.selected_character:
            return
        self._remove_condition_from(
            self.selected_character, Condition.CONCENTRATING.value, source=self.selected_character
        )

    def _shortcut_clear_target_conditions(self):
        """Keyboard shortcut 'Ctrl+Shift+C': remove every condition from every target."""
        if not self.target_characters:
            return
        for target in list(self.target_characters):
            for cond in list(target.get("conditions", [])):
                self._remove_condition_from(target, cond)

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
