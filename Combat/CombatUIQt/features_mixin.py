"""Features mixin for CombatAppQt."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from Combat.Definitions import Action
from .stats import _default_stats, increment_named_stat
from .styles import QSS


class FeaturesMixin:
    """Mixin for feature-related methods."""

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
            target_text = "Target(s): None selected — \"Apply to Target(s)\" will be unavailable"
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
            description = None
            if sb and hasattr(feature, "get_description"):
                description = feature.get_description(sb)

            html_content = f"<b style='color:#c9a84c; font-size:14px;'>{feature.name}</b>"
            if feature.origin:
                html_content += f"<br><span style='color:#a0a0b0;'>{feature.origin}</span>"
            html_content += "<br><br>"
            if description:
                html_content += description.replace(chr(10) + chr(10), "<br><br>")
            else:
                html_content += "No description available."

            detail.setHtml(html_content)
            selected_feature["feature"] = feature
            enable_btn.setEnabled(True)
            condition_source_btn.setEnabled(True)
            condition_target_btn.setEnabled(bool(self.target_characters))

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
        enable_btn = QPushButton("Enable")
        enable_btn.setEnabled(False)

        def do_enable():
            feature = selected_feature["feature"]
            if feature is None:
                return
            self._apply_enable_feature(feature)
            dlg.accept()

        enable_btn.clicked.connect(do_enable)

        condition_source_btn = QPushButton("Apply to Source")
        condition_source_btn.setEnabled(False)
        condition_source_btn.setToolTip(
            f"Add as a condition on {self.selected_character['name']} (self-applied)"
        )

        def do_apply_condition_source():
            feature = selected_feature["feature"]
            if feature is None:
                return
            self._apply_feature_as_condition(feature, apply_to_target=False)
            dlg.accept()

        condition_source_btn.clicked.connect(do_apply_condition_source)

        condition_target_btn = QPushButton("Apply to Target(s)")
        condition_target_btn.setEnabled(False)
        target_names = (
            ", ".join(t["name"] for t in self.target_characters)
            if self.target_characters
            else ""
        )
        condition_target_btn.setToolTip(
            f"Add as a condition on {target_names}"
            if self.target_characters
            else "Select a target first (right-click a card)"
        )

        def do_apply_condition_target():
            feature = selected_feature["feature"]
            if feature is None:
                return
            self._apply_feature_as_condition(feature, apply_to_target=True)
            dlg.accept()

        condition_target_btn.clicked.connect(do_apply_condition_target)

        close_btn2 = QPushButton("Close")
        close_btn2.clicked.connect(dlg.reject)
        btn_row.addWidget(enable_btn)
        btn_row.addWidget(condition_source_btn)
        btn_row.addWidget(condition_target_btn)
        btn_row.addWidget(close_btn2)
        outer.addLayout(btn_row)

        dlg.exec()

    def _apply_enable_feature(self, feature):
        """Apply an enabled feature to the selected combatant: log it and update stats."""
        char = self.selected_character
        if char is None:
            return

        char.setdefault("stats", _default_stats())
        char["stats"]["features_enabled"] = char["stats"].get("features_enabled", 0) + 1
        increment_named_stat(char["stats"], "features_enabled_by_name", feature.name)
        feature_value = {"feature_name": feature.name}
        self.history.append((Action.ENABLE_FEATURE, feature_value))
        self._log_event(
            f"{char['name']} uses {feature.name}",
            character=char["name"],
            action=Action.ENABLE_FEATURE,
            value=feature_value,
        )
        self._refresh_selected_card()

    def _apply_feature_as_condition(self, feature, apply_to_target: bool = False):
        """Add a feature's name as a condition badge — on the source (self-applied)
        or on the current target(s) — with the feature's full description available
        as a hover tooltip. The source is always recorded as the condition's source
        either way, for correct log/stat attribution."""
        source = self.selected_character
        if source is None:
            return
        recipients = self.target_characters if apply_to_target else [source]
        if not recipients:
            return

        # Build tooltip HTML from the feature details
        sb = source.get("_stat_block")
        description = None
        if sb and hasattr(feature, "get_description"):
            description = feature.get_description(sb)

        tooltip_html = f"<b style='color:#c9a84c; font-size:14px;'>{feature.name}</b>"
        if feature.origin:
            tooltip_html += f"<br><span style='color:#a0a0b0;'>{feature.origin}</span>"
        tooltip_html += "<br><br>"
        if description:
            tooltip_html += description.replace(chr(10) + chr(10), "<br><br>")
        else:
            tooltip_html += "No description available."

        badge_color = "#4c7ac9"

        # Store the tooltip description and badge color, and add the condition,
        # on every recipient (the source for a self-cast, each target otherwise).
        for char in list(recipients):
            char.setdefault("feature_condition_descriptions", {})[feature.name] = tooltip_html
            char.setdefault("feature_condition_colors", {})[feature.name] = badge_color
            self._add_condition_to(char, feature.name, source=source)
