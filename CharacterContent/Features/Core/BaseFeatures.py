import re
from dataclasses import dataclass
from enum import Enum
from typing import Literal, TextIO

from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import Html


@dataclass
class FeatureUses:
    """Limited-use tracking for a feature, rendered as checkbox slots on its card.

    max_uses is always the formula's maximum value - the boxes never show a
    build's "current" count directly, since level shard pages are generated
    once and never regenerated as the player levels up in play. A feature
    whose count varies by level or by another stat (e.g. equal to proficiency
    bonus) should explain how to derive the current count via
    current_formula instead.
    """

    max_uses: int
    # Reset cadence label for full recovery, e.g. "long rest", "short rest", "dawn".
    regain_all_on: str | None = None
    # (count, cadence) for partial recovery on a shorter rest, e.g. (1, "short rest").
    # If both this and regain_all_on are set, renders as "Regain <n> on a <cadence>,
    # all on a <regain_all_on>."
    regain_x_on: tuple[int, str] | None = None
    # Short plain-English fragment describing how to derive the build's real current
    # count from the max shown by the boxes (e.g. "equal to your proficiency bonus.").
    current_formula: str | None = None


class ActionType(str, Enum):
    """Action economy cost to activate a feature."""

    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"


class RegainedOn(str, Enum):
    """Cadence on which a feature's expended resource (uses, hit points, etc.)
    comes back, as stated in the feature's own description."""

    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    SHORT_OR_LONG_REST = "short_or_long_rest"
    # A regain condition tied to something other than a rest/time cadence
    # (e.g. "regains a use when you roll initiative", "on a kill").
    OTHER = "other"


_RANGE_SHAPE_RE = re.compile(
    r"(\d+)-Foot[- ](Cone|Cube|Sphere|Line|Emanation|Cylinder|Radius(?: Sphere)?)",
    re.IGNORECASE,
)

_DURATION_RE = re.compile(r"(?:up to\s+)?(\d+)\s+(\w+)", re.IGNORECASE)

_DURATION_UNIT_SECONDS = {
    "second": 1,
    "seconds": 1,
    "round": 6,
    "rounds": 6,
    "turn": 6,
    "turns": 6,
    "minute": 60,
    "minutes": 60,
    "hour": 3600,
    "hours": 3600,
    "day": 86400,
    "days": 86400,
}


@dataclass
class FeatureActivation:
    """Action economy, duration, and range/shape for how a feature is activated,
    rendered as tag chips on its card (mirrors FeatureUses' role for limited-use tracking).

    range_shape captures an area-of-effect shape (e.g. "Cone", "Sphere", "Radius")
    when the range text states one - split out automatically from a combined
    range string like "30-Foot Cone" unless range_shape is passed explicitly.
    Left None when no shape is stated (e.g. "30 Feet", "Self", "Touch").
    """

    action_type: "ActionType | Literal['action', 'bonus_action', 'reaction'] | None" = (
        None
    )
    duration: str | None = None
    range: str | None = None
    range_shape: str | None = None

    def __post_init__(self):
        if self.action_type is not None and not isinstance(
            self.action_type, ActionType
        ):
            self.action_type = ActionType(self.action_type)
        if self.range is not None and self.range_shape is None:
            match = _RANGE_SHAPE_RE.fullmatch(self.range.strip())
            if match:
                self.range = f"{match.group(1)} Feet"
                self.range_shape = match.group(2).title()

    def duration_to_seconds(self) -> int | str | None:
        """Convert duration to a whole number of seconds (a turn/round is 6 seconds).
        Returns the original duration string unchanged when it isn't a plain
        "<number> <unit>" time span (e.g. "Until Incapacitated", "1d6 Long Rests")."""
        if self.duration is None:
            return None
        match = _DURATION_RE.fullmatch(self.duration.strip())
        if match:
            count, unit = match.groups()
            seconds_per_unit = _DURATION_UNIT_SECONDS.get(unit.lower())
            if seconds_per_unit is not None:
                return int(count) * seconds_per_unit
        return self.duration


def parse_feature_level(origin: str | None) -> int:
    """Parse the level from a feature's origin string (e.g. 'Bard Level 3' -> 3).
    Features without a parseable level (background, species, origin feats) default to 1.
    """
    if not origin or "Level " not in origin:
        return 1
    try:
        return int(origin.split("Level ")[1].split()[0])
    except (ValueError, IndexError):
        return 1


FEATURE_CARD_CSS = """/* ── Feature cards ───────────────────────────────────────────────── */
        .features {
            max-width: 100%;
        }

        .feature-card {
            margin: 0 0 0.4rem 0;
            max-width: none;
            padding: 0 0 0.4rem 0;
            break-inside: avoid;
            -webkit-column-break-inside: avoid;
        }

        .feature-card + .feature-card {
            border-top: 2px solid #9a7040;
            padding-top: 0.4rem;
        }

        .feature-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.8rem;
            padding: 5px 10px;
            border-bottom: 1px solid #d8c8a8;
            max-width: none;
            margin: 0;
        }

        .feature-name-group {
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
        }

        .feature-name {
            font-size: 1rem;
            font-weight: 700;
            color: #4a3020;
            letter-spacing: 0.02em;
        }

        /* Shown on full-mode sheets for features normally skipped in concise
           mode — flags at a glance that there's nothing here to actively track. */
        .feature-passive-tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted-color);
            border: 1px solid #bbb;
            border-radius: 3px;
            padding: 1px 6px;
        }

        /* Dims passive feature cards so the eye is drawn to features that
           need active tracking, without hiding the passive ones entirely. */
        .feature-card.is-passive {
            opacity: 0.62;
        }

        /* Flags the action economy a feature costs to use - Action, Bonus
           Action, or Reaction - the same way .feature-passive-tag flags a
           feature as passive. Colors mirror the spell tag chips (.stag-*)
           so the two systems read consistently. */
        .feature-action-tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-radius: 3px;
            padding: 1px 6px;
        }

        .feature-action-tag.tag-action {
            border: 1px solid #3a6090;
            color: #3a6090;
        }

        .feature-action-tag.tag-bonus_action {
            border: 1px solid #2a9d5f;
            color: #1a7a45;
        }

        .feature-action-tag.tag-reaction {
            border: 1px solid #c8672a;
            color: #a8501a;
        }

        /* Flags a feature's effect duration (e.g. "10 Minutes", "1 Minute or
           Until Incapacitated") the same way .feature-action-tag flags action
           economy. Free-text rather than a fixed set of values, so it gets
           its own neutral color rather than one of the action-type colors. */
        .feature-duration-tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid #7a4f9e;
            color: #7a4f9e;
            border-radius: 3px;
            padding: 1px 6px;
        }

        /* Flags a feature's range/area (e.g. "30 Feet", "20-Foot Cone", "Self")
           the same way .feature-duration-tag flags duration. Free-text, own
           neutral color distinct from the other chips. */
        .feature-range-tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid #2a8f96;
            color: #227277;
            border-radius: 3px;
            padding: 1px 6px;
        }

        /* Flags what a feature's effect *does* - Heal, Buff, Control, Damage -
           so the card can be scanned for role at a glance. A feature can carry
           more than one (e.g. an attack that also imposes a condition is both
           Damage and Control), so each tag renders as its own chip. */
        .feature-usage-tag {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-radius: 3px;
            padding: 1px 6px;
        }

        .feature-usage-tag.tag-heal {
            border: 1px solid #2a9d5f;
            color: #1a7a45;
        }

        .feature-usage-tag.tag-buff {
            border: 1px solid #4a6fd4;
            color: #34519e;
        }

        .feature-usage-tag.tag-control {
            border: 1px solid #b8447a;
            color: #96335f;
        }

        .feature-usage-tag.tag-damage {
            border: 1px solid #c23b3b;
            color: #a52a2a;
        }

        .feature-usage-tag.tag-utility {
            border: 1px solid #6b7280;
            color: #4b5563;
        }

        .feature-usage-tag.tag-summon {
            border: 1px solid #8b5cf6;
            color: #6d28d9;
        }

        .feature-card.is-passive .feature-name {
            color: var(--muted-color);
        }

        .feature-card.is-passive .feature-origin {
            color: #a89a80;
        }

        .feature-origin {
            font-size: 0.75rem;
            color: #9a7040;
            font-style: italic;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .feature-body {
            padding: 0.4rem 0.7rem;
            font-size: 0.88rem;
            max-width: none;
            margin: 0;
        }

        .feature-body p {
            margin: 0.3em 0;
        }

        .feature-body ul,
        .feature-body ol {
            margin: 0.3em 0 0.3em 1.2em;
        }

        /* Core resource numbers (e.g. Martial Arts die, Focus Points) called
           out at the top of a feature's own card - reuses .stat-tile /
           .stat-tile-resource from the base sheet CSS, just laid out to fit
           inside a card instead of the overview row. The sheet isn't
           reprinted every level-up, so every level's value is shown as an
           equally-weighted box - there's no "current level" callout, since
           that would go stale the moment the player levels up without a
           reprint. */
        .feature-resource-section {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin: 0 0 0.5rem 0;
        }

        .feature-resource-group-label {
            display: block;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6a5636;
            margin-bottom: 0.2rem;
        }

        .feature-resource-tiles {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        /* Tables embedded inside feature descriptions (e.g. item/plan lists) */
        .feature-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            margin: 0.4rem 0;
        }

        .feature-table td,
        .feature-table th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
            text-align: left;
        }

        .feature-table th {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid #9a7040;
        }

        /* Feature upgrade blocks (nested inside .feature-body) */
        .feature-upgrade {
            margin-top: 0.5rem;
            border-left: 3px solid #9abbe0;
            border-radius: 0 3px 3px 0;
            padding: 0.3rem 0.6rem;
            max-width: none;
        }

        .feature-upgrade-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #3a6090;
            margin-bottom: 0.15rem;
        }

        .feature-upgrade-body {
            font-size: 0.85rem;
            color: #333;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        .inv-source {
            font-size: 0.75em;
            color: #999;
            font-style: italic;
            margin-top: 0.35em;
        }

        """


class Feature:
    """A single feature type. Override apply() to modify the stat block, get_description() to render a card, or both."""

    # Optional alternate renderings: get_table_description() and get_concise_description()
    # both fall back to get_description() when they return None.

    def __init__(
        self,
        name: str | None = None,
        origin: str | None = None,
        skippable_in_concise: bool = False,
        usage_tags: (
            list[Literal["heal", "buff", "control", "damage", "utility", "summon"]]
            | None
        ) = None,
        activation: "FeatureActivation | None" = None,
        uses: "FeatureUses | None" = None,
    ):
        self.name = name if name is not None else type(self).__name__
        self.origin = origin
        self.extensions: list["Feature"] = []
        # Set True for features that only modify the stat block (e.g. a flat bonus
        # or a resource pool) where the prose description adds nothing on a
        # concise/table character sheet. Full-mode sheets always show it.
        self.skippable_in_concise = skippable_in_concise
        # Action economy, duration, and range/shape for activating this feature.
        # Leave unset (or pass an empty FeatureActivation()) for passive features
        # and instantaneous effects with no meaningful range.
        self.activation = activation if activation is not None else FeatureActivation()
        # Set for features whose effect falls into one or more of these functional
        # roles - healing, buffing, imposing a condition/controlling a target,
        # dealing damage, or non-combat utility - so the card can be scanned for
        # role at a glance. A feature can carry more than one (e.g. deals damage
        # and also restrains).
        # Leave None/empty for features with no combat/utility role of this kind
        # (e.g. skill proficiencies, passive stat bonuses).
        self.usage_tags = usage_tags
        # Set for features that have a limited number of uses per rest period
        # (e.g. action surge, channel divinity). The FeatureUses dataclass tracks
        # max uses, what resets them, and optionally a formula explaining the
        # current uses based on character stats.
        self.uses = uses

    def extend_feature(self, feature: "Feature"):
        self.extensions.append(feature)

    def apply(self, character_stat_block: CharacterStatBlock):
        pass

    def get_description(self, character_stat_block: CharacterStatBlock) -> str | None:
        return None

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]] | None:
        """Override to provide a concise label/value table version of the description
        (e.g. [("What", "..."), ("Casting Time", "...")]), used when table descriptions
        are requested. Return None to fall back to get_description()."""
        return None

    def get_concise_description(
        self, character_stat_block: CharacterStatBlock
    ) -> str | None:
        """Override to provide a short prose summary of the description (a sentence
        or two, same formatting rules as get_description), used when concise
        descriptions are requested. Return None to fall back to get_description()."""
        return None

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int | None:
        """Override to return this feature's saving throw DC (e.g. 8 plus an
        ability modifier plus proficiency bonus), so the value can be reused
        anywhere it's needed instead of being recomputed inline. Return None
        (default) for features with no DC."""
        return None

    def regained_on(
        self, character_stat_block: CharacterStatBlock
    ) -> "RegainedOn | None":
        """Override to return when this feature's expended resource (uses, hit
        points, etc.) is regained (e.g. a short rest, long rest, or dawn), so
        the value can be reused anywhere it's needed instead of being re-parsed
        from prose. Return None (default) for features with nothing to regain."""
        return None

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]] | None:
        """Override to surface this feature's core numbers as small stat
        tiles at the top of its own feature card (visually the same idea as
        the Max HP tile, sized down to fit a card) for resources checked
        constantly in play - e.g. a martial arts die size or a resource
        point total. Returns a list of (group_label, steps) tuples, where
        steps is a list of (step_label, value) pairs - typically one tile
        per level or level-range, e.g. [("Martial Arts Die",
        [("Lv 1-4", "1d6"), ("Lv 5-10", "1d8"), ...])], commonly built from
        StringUtils.compress_level_progression(). Every step is shown with
        equal weight and no "current level" is called out: the generated
        page isn't reprinted on every level-up, so a step highlighted as
        "current" at generation time would silently go stale. Return None
        (default) for features with no resource tile at all."""
        return None

    def render_html_description(
        self,
        character_stat_block: CharacterStatBlock,
        description_mode: Literal["table", "concise"] | None = None,
    ) -> str | None:
        if description_mode is not None and self.skippable_in_concise:
            return None

        if description_mode == "table":
            table_rows = self.get_table_description(character_stat_block)
            if table_rows is not None:
                return Html.highlight_damage_types(
                    Html.key_value_table_to_html(table_rows)
                )

        if description_mode == "concise":
            concise_description = self.get_concise_description(character_stat_block)
            if concise_description is not None:
                return self._description_to_html(concise_description)

        description = self.get_description(character_stat_block)
        if description is None:
            return None
        return self._description_to_html(description)

    def write_to_file(
        self,
        character_stat_block: CharacterStatBlock,
        file: TextIO,
        description_mode: Literal["table", "concise"] | None = None,
        max_level: int | None = None,
    ):
        html_description = self.render_html_description(
            character_stat_block, description_mode
        )
        if html_description is None:
            return

        # A skippable-in-concise feature that's still showing means we're on a
        # full-mode sheet — flag it as passive so the player knows there's
        # nothing here to actively track.
        passive_tag = (
            "<span class='feature-passive-tag'>Passive</span>"
            if description_mode is None and self.skippable_in_concise
            else ""
        )

        action_tag = self._action_tag_html(self.activation.action_type)
        duration_tag = self._duration_tag_html(self.activation.duration)
        range_tag = self._range_tag_html(
            self.activation.range, self.activation.range_shape
        )
        usage_tags_html = self._usage_tags_html(self.usage_tags)

        card_class = "feature-card is-passive" if passive_tag else "feature-card"
        file.write(f"<div class='{card_class}'>\n")
        file.write("<div class='feature-header'>\n")
        file.write("<span class='feature-name-group'>\n")
        file.write(f"<span class='feature-name'>{self.name}</span>\n")
        if passive_tag:
            file.write(f"{passive_tag}\n")
        if action_tag:
            file.write(f"{action_tag}\n")
        if duration_tag:
            file.write(f"{duration_tag}\n")
        if range_tag:
            file.write(f"{range_tag}\n")
        if usage_tags_html:
            file.write(f"{usage_tags_html}\n")
        file.write("</span>\n")
        file.write(f"<span class='feature-origin'>{self.origin}</span>\n")
        file.write("</div>\n")
        file.write("<div class='feature-body'>\n")

        resource_tiles = self.get_resource_tiles(character_stat_block)
        if resource_tiles:
            file.write("<div class='feature-resource-section'>\n")
            for group_label, steps in resource_tiles:
                file.write("<div class='feature-resource-group'>\n")
                file.write(
                    f"<span class='feature-resource-group-label'>{group_label}</span>\n"
                )
                file.write("<div class='feature-resource-tiles'>\n")
                for step_label, value in steps:
                    file.write(self._resource_tile_html(step_label, value))
                file.write("</div>\n")
                file.write("</div>\n")
            file.write("</div>\n")

        file.write(f"{html_description}\n")
        if self.uses is not None:
            file.write(self._uses_html(self.uses) + "\n")

        for extension in self.extensions:
            ext_level = parse_feature_level(extension.origin)
            parent_level = parse_feature_level(self.origin)

            # When writing to a per-level shard (max_level set), skip extensions
            # whose origin level exceeds the page's level. Full pages (max_level=None)
            # always show all extensions.
            if max_level is not None:
                if ext_level > max_level:
                    continue
                # Skip extensions that are being rendered as standalone cards on this
                # page (ext_level > parent_level means they'll appear separately)
                if ext_level > parent_level:
                    continue

            ext_html = extension.render_html_description(
                character_stat_block, description_mode
            )
            if ext_html is None:
                continue
            ext_passive_tag = (
                " <span class='feature-passive-tag'>Passive</span>"
                if description_mode is None and extension.skippable_in_concise
                else ""
            )
            ext_action_tag = self._action_tag_html(extension.activation.action_type)
            ext_action_tag = f" {ext_action_tag}" if ext_action_tag else ""
            ext_duration_tag = self._duration_tag_html(extension.activation.duration)
            ext_duration_tag = f" {ext_duration_tag}" if ext_duration_tag else ""
            ext_range_tag = self._range_tag_html(
                extension.activation.range, extension.activation.range_shape
            )
            ext_range_tag = f" {ext_range_tag}" if ext_range_tag else ""
            ext_usage_tags_html = self._usage_tags_html(extension.usage_tags)
            ext_usage_tags_html = (
                f" {ext_usage_tags_html}" if ext_usage_tags_html else ""
            )
            ext_uses_html = (
                "\n" + self._uses_html(extension.uses)
                if extension.uses is not None
                else ""
            )
            file.write(
                f"<div class='feature-upgrade'>\n"
                f"<span class='feature-upgrade-label'>{extension.origin}: {extension.name}{ext_passive_tag}{ext_action_tag}{ext_duration_tag}{ext_range_tag}{ext_usage_tags_html}</span>\n"
                f"<div class='feature-upgrade-body'>{ext_html}{ext_uses_html}</div>\n"
                f"</div>\n"
            )

        file.write("</div>\n")
        file.write("</div>\n")

    def write_extension_card_to_file(
        self,
        character_stat_block: CharacterStatBlock,
        file: TextIO,
        parent_name: str,
        description_mode: Literal["table", "concise"] | None = None,
    ):
        """Write an extension (that is, an enhancement to a parent feature) as a
        standalone feature card on its own level page, visually flagged as extending
        the parent. Reuses the existing .feature-upgrade CSS classes for consistent
        blue-label styling."""
        html_description = self.render_html_description(
            character_stat_block, description_mode
        )
        if html_description is None:
            return

        passive_tag = (
            "<span class='feature-passive-tag'>Passive</span>"
            if description_mode is None and self.skippable_in_concise
            else ""
        )

        card_class = "feature-card is-passive" if passive_tag else "feature-card"
        file.write(f"<div class='{card_class}'>\n")
        file.write("<div class='feature-header'>\n")
        file.write("<span class='feature-name-group'>\n")
        file.write(f"<span class='feature-name'>{self.name}</span>\n")
        action_tag = self._action_tag_html(self.activation.action_type)
        duration_tag = self._duration_tag_html(self.activation.duration)
        range_tag = self._range_tag_html(
            self.activation.range, self.activation.range_shape
        )
        usage_tags_html = self._usage_tags_html(self.usage_tags)
        if passive_tag:
            file.write(f"{passive_tag}\n")
        if action_tag:
            file.write(f"{action_tag}\n")
        if duration_tag:
            file.write(f"{duration_tag}\n")
        if range_tag:
            file.write(f"{range_tag}\n")
        if usage_tags_html:
            file.write(f"{usage_tags_html}\n")
        file.write("</span>\n")
        file.write(f"<span class='feature-origin'>{self.origin}</span>\n")
        file.write("</div>\n")
        file.write("<div class='feature-body'>\n")

        # Write the extension as an upgrade block with the parent feature name
        ext_passive_tag = (
            " <span class='feature-passive-tag'>Passive</span>"
            if description_mode is None and self.skippable_in_concise
            else ""
        )
        uses_html = "\n" + self._uses_html(self.uses) if self.uses is not None else ""
        file.write(
            f"<div class='feature-upgrade'>\n"
            f"<span class='feature-upgrade-label'>{parent_name} Feature Extension{ext_passive_tag}</span>\n"
            f"<div class='feature-upgrade-body'>{html_description}{uses_html}</div>\n"
            f"</div>\n"
        )

        file.write("</div>\n")
        file.write("</div>\n")

    @staticmethod
    def _action_tag_html(
        action_type: "ActionType | Literal['action', 'bonus_action', 'reaction'] | None",
    ) -> str:
        if action_type is None:
            return ""
        value = (
            action_type.value if isinstance(action_type, ActionType) else action_type
        )
        labels = {
            "action": "Action",
            "bonus_action": "Bonus Action",
            "reaction": "Reaction",
        }
        label = labels[value]
        return f"<span class='feature-action-tag tag-{value}'>{label}</span>"

    @staticmethod
    def _duration_tag_html(duration: str | None) -> str:
        if duration is None:
            return ""
        return f"<span class='feature-duration-tag'>Duration: {duration}</span>"

    @staticmethod
    def _range_tag_html(range: str | None, range_shape: str | None = None) -> str:
        if range is None:
            return ""
        label = f"{range} ({range_shape})" if range_shape else range
        return f"<span class='feature-range-tag'>Range: {label}</span>"

    @staticmethod
    def _usage_tags_html(usage_tags: list[str] | None) -> str:
        if not usage_tags:
            return ""
        labels = {
            "damage": "Damage",
            "heal": "Heal",
            "buff": "Buff",
            "control": "Control",
            "utility": "Utility",
            "summon": "Summon",
        }
        # Fixed display order regardless of the order passed in, so cards read
        # consistently across features.
        ordered = [tag for tag in labels if tag in usage_tags]
        return " ".join(
            f"<span class='feature-usage-tag tag-{tag}'>{labels[tag]}</span>"
            for tag in ordered
        )

    @staticmethod
    def _uses_html(uses: "FeatureUses") -> str:
        return Html.render_slot_boxes(
            uses.max_uses,
            regain_all_on=uses.regain_all_on,
            regain_x_on=uses.regain_x_on,
            current_formula=uses.current_formula,
        )

    @staticmethod
    def _resource_tile_html(label: str, value) -> str:
        return (
            "<div class='stat-tile stat-tile-resource'>"
            f"<span class='stat-tile-label'>{label}</span>"
            f"<span class='stat-tile-value'>{value}</span>"
            "</div>\n"
        )

    @staticmethod
    def _bolden_line(text: str) -> str:
        from Utils.Html import _bold_prefix

        bolded = _bold_prefix(text, ".", 5)
        if bolded is not None:
            return bolded
        bolded = _bold_prefix(text, ":", 10)
        if bolded is not None:
            return bolded
        return text

    @staticmethod
    def _description_to_html(description: str) -> str:
        processed = Html.boxes_to_html(description)
        processed = Html.tables_to_html(processed)

        BULLET_PREFIXES = [
            ("            > ", 3),
            ("        - ", 2),
            ("    * ", 1),
        ]

        lines = processed.split("\n")
        html_parts: list[str] = []
        open_levels: list[int] = []

        def close_levels_down_to(target_level: int):
            while open_levels and open_levels[-1] > target_level:
                html_parts.append("</ul>")
                open_levels.pop()

        def close_all_levels():
            while open_levels:
                html_parts.append("</ul>")
                open_levels.pop()

        for line in lines:
            bullet_level = 0
            bullet_text = None
            for prefix, level in BULLET_PREFIXES:
                if line.startswith(prefix):
                    bullet_level = level
                    bullet_text = line[len(prefix) :]
                    break

            if bullet_level > 0:
                assert bullet_text is not None
                close_levels_down_to(bullet_level)
                if not open_levels or open_levels[-1] < bullet_level:
                    html_parts.append("<ul>")
                    open_levels.append(bullet_level)
                bolded_text = Feature._bolden_line(bullet_text)
                html_parts.append(f"<li>{bolded_text}</li>")
            else:
                close_all_levels()
                stripped = line.strip()
                if stripped:
                    if stripped.startswith("<"):
                        html_parts.append(stripped)
                    else:
                        bolded = Feature._bolden_line(stripped)
                        html_parts.append(f"<p>{bolded}</p>")

        close_all_levels()

        result = "\n".join(html_parts)
        if result and not result.endswith("\n"):
            result += "\n"
        return Html.highlight_damage_types(result)
