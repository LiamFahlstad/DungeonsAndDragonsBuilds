"""Features mixin for CombatAppQt."""

from CharacterContent.Features.ClassFeatures.Druid.DruidFeatures import WildShape
from Model.Content.Feature import FeatureTarget
from Combat.Definitions import Action
from Combat.Effects.active_effects import (
    FEATURE,
    badge_modifiers,
    describe,
    note_origin,
)
from Presentation.FeatureCards import feature_label
from Combat.Fight.effect_options import feature_action_cost
from .resources import feature_lack
from Combat.Fight.stats import _default_stats, increment_named_stat
from .state import CombatWindowState
from .undo import undoable

# The color of a condition badge a feature puts on a creature.
FEATURE_BADGE_COLOR = "#4c7ac9"


class FeaturesMixin(CombatWindowState):
    """Mixin for feature-related methods."""

    def _feature_uses_text(self, char: dict, feature, sb) -> str:
        """'<remaining>/<max>' for a limited-use feature, or 'None' for a
        passive/unlimited one. Remaining is tracked in char['feature_uses_used'],
        keyed by feature name, and reset by a long/short rest (see Combat/CombatUIQt/rest.py).
        """
        if feature.uses is None:
            return "None"
        max_uses = (
            feature.number_of_uses(sb) if sb is not None else feature.uses.max_uses
        )
        used = char.get("feature_uses_used", {}).get(feature.name, 0)
        remaining = max(max_uses - used, 0)
        return f"{remaining}/{max_uses}"

    def _feature_condition_tooltip(self, char: dict, feature) -> str:
        """Build the HTML tooltip for a feature's condition badge (name, origin,
        action/target/duration/recovery/uses, description). Shared by _apply_feature
        (when the badge is first applied) and _make_card's fallback (when a badge's
        tooltip wasn't persisted — e.g. player-log conditions restored via replay,
        see Combat/Fight/log.py's apply_replay_action)."""
        sb = char.get("_stat_block")
        feature_target = feature.target(sb) if sb is not None else None
        description = None
        if sb and hasattr(feature, "get_description"):
            description = feature.get_description(sb)

        tooltip_html = f"<b style='color:#c9a84c; font-size:14px;'>{feature.name}</b>"
        origin = feature_label(feature, sb) if sb is not None else feature.origin
        if origin:
            tooltip_html += f"<br><span style='color:#a0a0b0;'>{origin}</span>"
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
            feature.activation.duration_text
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

    def _count_feature_use(
        self, source: dict, name: str, counts_uses: bool, count: int = 1
    ):
        """Count a use of the feature `name` in source's stats, and `count` of
        its uses if it has any (counts_uses; Elemental Burst spends 2 of Monk's
        Focus), and log it so the party's replay counts it too. Enable Feature
        and the Custom Effect dialog share it."""
        stats = source.setdefault("stats", _default_stats())
        stats["features_enabled"] = stats.get("features_enabled", 0) + 1
        increment_named_stat(stats, "features_enabled_by_name", name)
        value: dict = {"feature_name": name}
        text = f"{source['name']} uses {name}"
        if count != 1:
            value["count"] = count
            text += f" ({count} uses)"
        self._log_event(
            text,
            character=source["name"],
            action=Action.ENABLE_FEATURE,
            value=value,
        )
        if counts_uses:
            used = source.setdefault("feature_uses_used", {})
            used[name] = used.get(name, 0) + count

    @undoable
    def _apply_feature(self, feature):
        """Apply a feature. The feature's own declared metadata decides what happens:
        feature.target() decides who is affected (SELF/None always means the source
        itself; any other target type requires a target to be selected first),
        feature.activation.action_type logs the action-economy cost on the source,
        and feature.activation.duration_to_seconds() (a FeatureDuration's, if
        positive) adds a ticking duration bar on every recipient. Every application also adds a condition
        badge (with the description as a hover tooltip) on its recipient(s) and
        increments the source's features_enabled stat."""
        source = self.selected_character
        if source is None:
            self._show_status("No feature used: left-click a card to pick a source.")
            return
        if isinstance(feature, WildShape):
            self._pick_wild_shape_form(source)
            return

        sb = source.get("_stat_block")
        if source.get("_is_player") and feature.summons(sb):
            self._pick_summon(source, feature)
            return
        feature_target = feature.target(sb) if sb is not None else None

        if feature_target is None or feature_target == FeatureTarget.SELF:
            recipients = [source]
        else:
            if not self.target_characters:
                self._show_status(
                    f"No feature used: {feature.name} needs a target"
                    f" ({feature_target.value}). Right-click a card."
                )
                return
            recipients = self.target_characters

        # Action economy: the source spends the action, regardless of who it affects
        action_cost = feature_action_cost(feature)
        lacks = [
            feature_lack(source, feature.name),
            self._action_lack(source, action_cost),
        ]
        if not self._go_ahead_anyway(source, f"Use {feature.name}", lacks):
            return

        self._count_feature_use(source, feature.name, feature.uses is not None)
        if action_cost is not None:
            self._add_action_use(action_cost, ask=False)

        # Condition badge + tooltip on every recipient
        tooltip_html = self._feature_condition_tooltip(source, feature)
        badge_color = FEATURE_BADGE_COLOR

        # Duration -> a ticking bar on every recipient
        duration_value = (
            feature.activation.duration_to_seconds() if feature.activation else None
        )
        has_duration = isinstance(duration_value, int) and duration_value > 0

        # What the badge does while it's on, as the feature's effects say.
        effects = feature.combat_effects(sb) if sb is not None else None
        modifiers = badge_modifiers(effects, feature.name)
        for char in list(recipients):
            describe(char, feature.name, tooltip_html, badge_color, FEATURE)
            self._add_condition_to(char, feature.name, source=source)
            note_origin(char, feature.name, source=feature.name, caster=source["name"])
            self._give_badge_modifiers(char, feature.name, modifiers, source=source)

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
                        f"{char['name']}'s {entry['name']} expires",
                        note_turn=False,
                        character=char["name"],
                    )
            char["active_features"] = remaining
        self._rebuild_cards()

    @undoable
    def _remove_active_feature(self, char: dict, entry: dict):
        """Manually dismiss an active feature before its duration timer runs out —
        also clears the matching condition badge so the two stay in sync."""
        active_features = char.get("active_features") or []
        if entry not in active_features:
            return
        active_features.remove(entry)
        self._log_event(
            f"{char['name']}'s {entry['name']} ends early", character=char["name"]
        )
        if entry["name"] in char.get("conditions", []):
            self._remove_condition_from(char, entry["name"], source=char)
        else:
            self._rebuild_card(char)
