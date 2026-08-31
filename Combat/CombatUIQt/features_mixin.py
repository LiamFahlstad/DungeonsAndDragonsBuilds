"""Features mixin for CombatAppQt."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from CharacterContent.Features.Core.BaseFeatures import FeatureTarget
from Combat.Definitions import Action
from .stats import _default_stats, increment_named_stat
from .styles import QSS


class FeaturesMixin:
    """Mixin for feature-related methods."""

    def _feature_uses_text(self, char: dict, feature, sb) -> str:
        """'<remaining>/<max>' for a limited-use feature, or 'None' for a
        passive/unlimited one. Remaining is tracked in char['feature_uses_used'],
        keyed by feature name, and reset by a long/short rest (see Combat/CombatUIQt/rest.py)."""
        if feature.uses is None:
            return "None"
        max_uses = feature.number_of_uses(sb) if sb is not None else feature.uses.max_uses
        used = char.get("feature_uses_used", {}).get(feature.name, 0)
        remaining = max(max_uses - used, 0)
        return f"{remaining}/{max_uses}"

    def _feature_condition_tooltip(self, char: dict, feature) -> str:
        """Build the HTML tooltip for a feature's condition badge (name, origin,
        action/target/duration/recovery/uses, description). Shared by _apply_feature
        (when the badge is first applied) and _make_card's fallback (when a badge's
        tooltip wasn't persisted — e.g. player-log conditions restored via replay,
        see logging_mixin._apply_replay_action)."""
        sb = char.get("_stat_block")
        feature_target = feature.target(sb) if sb is not None else None
        description = None
        if sb and hasattr(feature, "get_description"):
            description = feature.get_description(sb)

        tooltip_html = f"<b style='color:#c9a84c; font-size:14px;'>{feature.name}</b>"
        if feature.origin:
            tooltip_html += f"<br><span style='color:#a0a0b0;'>{feature.origin}</span>"
        tooltip_html += "<br><br>"

        regained_on = feature.regained_on(sb) if sb is not None else None
        action_text = (
            feature.activation.action_type.value.replace("_", " ").title()
            if feature.activation and feature.activation.action_type is not None
            else "None"
        )
        target_text = (
            feature_target.value.replace("_", " ").title()
            if feature_target is not None
            else "None"
        )
        duration_text = (
            feature.activation.duration
            if feature.activation and feature.activation.duration
            else "None"
        )
        recovery_text = (
            regained_on.value.replace("_", " ").title()
            if regained_on is not None
            else "None"
        )
        uses_text = self._feature_uses_text(char, feature, sb)

        tooltip_html += (
            f"<span style='color:#7a9fd4;'><b>Action Type:</b> {action_text}</span><br>"
        )
        tooltip_html += (
            f"<span style='color:#7a9fd4;'><b>Target:</b> {target_text}</span><br>"
        )
        tooltip_html += (
            f"<span style='color:#7a9fd4;'><b>Duration:</b> {duration_text}</span><br>"
        )
        tooltip_html += (
            f"<span style='color:#7a9fd4;'><b>Recovery:</b> {recovery_text}</span><br>"
        )
        tooltip_html += (
            f"<span style='color:#7a9fd4;'><b>Uses:</b> {uses_text}</span><br><br>"
        )

        tooltip_html += (
            description.replace(chr(10) + chr(10), "<br><br>")
            if description
            else "No description available."
        )
        return tooltip_html

    def _show_enable_feature_dialog(self):
        """Search the feature list for the selected combatant and enable a feature."""
        if not self.selected_character:
            return

        features = self.selected_character.get("_feature_objects", [])
        dlg = QDialog(self._window)
        dlg.setWindowTitle(f"Enable Feature — {self.selected_character['name']}")
        dlg.setMinimumSize(760, 560)
        dlg.setStyleSheet(QSS)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(8)

        search_box = QLineEdit()
        search_box.setPlaceholderText("Search features…")
        outer.addWidget(search_box)

        if self.target_characters:
            target_names = ", ".join(t["name"] for t in self.target_characters)
            target_text = f"Target(s): {target_names}"
        else:
            target_text = "Target(s): None selected — features that require a target will be unavailable"
        target_info_lbl = QLabel(target_text)
        target_info_lbl.setObjectName("secondary")
        target_info_lbl.setWordWrap(True)
        outer.addWidget(target_info_lbl)

        body = QHBoxLayout()
        body.setSpacing(10)
        outer.addLayout(body)

        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setMinimumWidth(260)
        body.addWidget(tree, stretch=1)

        detail = QTextEdit()
        detail.setReadOnly(True)
        body.addWidget(detail, stretch=2)

        category_items: dict[str, QTreeWidgetItem] = {}
        for feature in features:
            category = feature.origin or "Other"
            cat_item = category_items.get(category)
            if cat_item is None:
                cat_item = QTreeWidgetItem([category])
                cat_item.setFirstColumnSpanned(True)
                tree.addTopLevelItem(cat_item)
                category_items[category] = cat_item
            feature_item = QTreeWidgetItem([feature.name])
            feature_item.setData(0, Qt.ItemDataRole.UserRole, feature)
            cat_item.addChild(feature_item)

        selected_feature: dict[str, object] = {"feature": None}

        def show_feature(feature):
            sb = self.selected_character.get("_stat_block")
            feature_target = feature.target(sb) if sb is not None else None
            regained_on = feature.regained_on(sb) if sb is not None else None
            description = None
            if sb and hasattr(feature, "get_description"):
                description = feature.get_description(sb)

            action_text = (
                feature.activation.action_type.value.replace("_", " ").title()
                if feature.activation and feature.activation.action_type is not None
                else "None"
            )
            target_text = (
                feature_target.value.replace("_", " ").title()
                if feature_target is not None
                else "None"
            )
            duration_text = (
                feature.activation.duration
                if feature.activation and feature.activation.duration
                else "None"
            )
            recovery_text = (
                regained_on.value.replace("_", " ").title()
                if regained_on is not None
                else "None"
            )
            uses_text = self._feature_uses_text(self.selected_character, feature, sb)

            html_content = f"<b style='color:#c9a84c; font-size:14px;'>{feature.name}</b>"
            if feature.origin:
                html_content += f"<br><span style='color:#a0a0b0;'>{feature.origin}</span>"
            html_content += "<br><br>"
            html_content += (
                f"<span style='color:#7a9fd4;'><b>Action Type:</b> {action_text}</span><br>"
            )
            html_content += (
                f"<span style='color:#7a9fd4;'><b>Target:</b> {target_text}</span><br>"
            )
            html_content += (
                f"<span style='color:#7a9fd4;'><b>Duration:</b> {duration_text}</span><br>"
            )
            html_content += (
                f"<span style='color:#7a9fd4;'><b>Recovery:</b> {recovery_text}</span><br>"
            )
            html_content += (
                f"<span style='color:#7a9fd4;'><b>Uses Left:</b> {uses_text}</span><br><br>"
            )
            if description:
                html_content += description.replace(chr(10) + chr(10), "<br><br>")
            else:
                html_content += "No description available."

            detail.setHtml(html_content)
            selected_feature["feature"] = feature

            if feature_target is None or feature_target == FeatureTarget.SELF:
                apply_btn.setEnabled(True)
                apply_btn.setToolTip(
                    f"Apply to {self.selected_character['name']} (self-applied)"
                )
            elif self.target_characters:
                apply_btn.setEnabled(True)
                target_names = ", ".join(t["name"] for t in self.target_characters)
                apply_btn.setToolTip(
                    f"Apply to {target_names} (requires: {feature_target.value})"
                )
            else:
                apply_btn.setEnabled(False)
                apply_btn.setToolTip(
                    f"This feature requires a target ({feature_target.value}) — "
                    "select a target first (right-click a card)"
                )

        def on_selection_changed():
            items = tree.selectedItems()
            if not items:
                return
            feature = items[0].data(0, Qt.ItemDataRole.UserRole)
            if feature is not None:
                show_feature(feature)

        tree.itemSelectionChanged.connect(on_selection_changed)

        def apply_filter(query: str):
            query = query.strip().lower()
            for category, cat_item in category_items.items():
                any_visible = False
                for i in range(cat_item.childCount()):
                    child = cat_item.child(i)
                    feature = child.data(0, Qt.ItemDataRole.UserRole)
                    visible = query in feature.name.lower()
                    child.setHidden(not visible)
                    any_visible = any_visible or visible
                cat_item.setHidden(not any_visible)
                if query:
                    cat_item.setExpanded(any_visible)

        search_box.textChanged.connect(apply_filter)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setEnabled(False)

        def do_apply():
            feature = selected_feature["feature"]
            if feature is None:
                return
            self._apply_feature(feature)
            dlg.accept()

        apply_btn.clicked.connect(do_apply)

        close_btn2 = QPushButton("Close")
        close_btn2.clicked.connect(dlg.reject)
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(close_btn2)
        outer.addLayout(btn_row)

        dlg.exec()

    def _apply_feature(self, feature):
        """Apply a feature. The feature's own declared metadata decides what happens:
        feature.target() decides who is affected (SELF/None always means the source
        itself; any other target type requires a target to be selected first),
        feature.activation.action_type logs the action-economy cost on the source,
        and feature.activation.duration_to_seconds() (if positive) adds a ticking
        duration bar on every recipient. Every application also adds a condition
        badge (with the description as a hover tooltip) on its recipient(s) and
        increments the source's features_enabled stat."""
        source = self.selected_character
        if source is None:
            QMessageBox.warning(self._window, "Error", "Select a source (character) first.")
            return

        sb = source.get("_stat_block")
        feature_target = feature.target(sb) if sb is not None else None

        if feature_target is None or feature_target == FeatureTarget.SELF:
            recipients = [source]
        else:
            if not self.target_characters:
                QMessageBox.warning(
                    self._window,
                    "Error",
                    f"{feature.name} requires a target ({feature_target.value}) — select a target before applying.",
                )
                return
            recipients = self.target_characters

        # Usage bookkeeping on the source
        source.setdefault("stats", _default_stats())
        source["stats"]["features_enabled"] = source["stats"].get("features_enabled", 0) + 1
        increment_named_stat(source["stats"], "features_enabled_by_name", feature.name)
        feature_value = {"feature_name": feature.name}
        self.history.append((Action.ENABLE_FEATURE, feature_value))
        self._log_event(
            f"{source['name']} uses {feature.name}",
            character=source["name"],
            action=Action.ENABLE_FEATURE,
            value=feature_value,
        )
        if feature.uses is not None:
            used = source.setdefault("feature_uses_used", {})
            used[feature.name] = used.get(feature.name, 0) + 1

        # Action economy: the source spends the action, regardless of who it affects
        if feature.activation and feature.activation.action_type is not None:
            action_type_map = {
                "action": "Action",
                "bonus_action": "Bonus Action",
                "reaction": "Reaction",
            }
            action_label = action_type_map.get(feature.activation.action_type.value)
            if action_label:
                self._add_action_use(action_label)

        # Condition badge + tooltip on every recipient
        tooltip_html = self._feature_condition_tooltip(source, feature)
        badge_color = "#4c7ac9"

        # Duration -> a ticking bar on every recipient
        duration_value = (
            feature.activation.duration_to_seconds() if feature.activation else None
        )
        has_duration = isinstance(duration_value, int) and duration_value > 0

        for char in list(recipients):
            char.setdefault("feature_condition_descriptions", {})[feature.name] = tooltip_html
            char.setdefault("feature_condition_colors", {})[feature.name] = badge_color
            self._add_condition_to(char, feature.name, source=source)

            if has_duration:
                char.setdefault("active_features", []).append(
                    {
                        "name": feature.name,
                        "time_left": duration_value,
                        "duration": duration_value,
                    }
                )

        self._refresh_selected_card()

    def _tick_active_features(self):
        """Deduct 6 seconds (one round) from every combatant's active feature timers,
        expiring and logging any that reach zero."""
        for char in self.characters:
            active_features = char.get("active_features")
            if not active_features:
                continue
            remaining = []
            for entry in active_features:
                entry["time_left"] = max(entry["time_left"] - 6, 0)
                if entry["time_left"] > 0:
                    remaining.append(entry)
                else:
                    self._log_event(
                        f"{char['name']}'s {entry['name']} expires", note_turn=False
                    )
            char["active_features"] = remaining
        self._rebuild_cards()

    def _remove_active_feature(self, char: dict, entry: dict):
        """Manually dismiss an active feature before its duration timer runs out —
        also clears the matching condition badge so the two stay in sync."""
        active_features = char.get("active_features") or []
        if entry not in active_features:
            return
        active_features.remove(entry)
        self._log_event(f"{char['name']}'s {entry['name']} ends early")
        if entry["name"] in char.get("conditions", []):
            self._remove_condition_from(char, entry["name"], source=char)
        else:
            self._rebuild_card(char)
