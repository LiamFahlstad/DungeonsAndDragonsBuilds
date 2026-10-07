"""Feature cards: how a Feature is rendered on the sheet. A Feature itself only
supplies content (name, description hooks, uses, activation, usage tags);
everything here turns that into HTML."""

import re
from typing import Literal, Sequence, TextIO

from CharacterContent.Features.Core.BaseFeatures import (
    ActionType,
    Feature,
    FeatureUses,
)
from Model.Character import Character
from Model.Records.GrantStamp import GrantStamp
from Presentation import Html
from Presentation.FeatureOrder import ordered_extensions

DescriptionMode = Literal["table", "concise"] | None

# An origin label naming the level it's granted at: "Bard Level 3",
# "Oath of Glory Paladin Level 7" (not "General Feat Level 4+").
_LEVEL_LABEL = re.compile(r"^(.*\S)\s+Level (\d+)$")


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


# ── Labels ───────────────────────────────────────────────────────────────────


def feature_label(feature: Feature, character: Character) -> str:
    """The origin label on a feature's card ("Bard Level 9"): its own `origin`
    text, made to agree with where `character` granted it. A feature the
    character didn't grant keeps `origin`."""
    if not character.has_granted(feature):
        return feature.origin or ""
    return _label_for(feature, character.stamp_of(feature))


def _label_for(feature: Feature, stamp: GrantStamp) -> str:
    """A feat or boon taken at a class level reads "<class> Level N". A
    "... Level N" origin takes its level from the stamp; an empty one becomes
    "<class> Level N" for a class grant; anything else ("Human Trait",
    "Maneuver") is kept as written."""
    if feature.labeled_by_class_level and stamp.kind.is_class_level:
        return f"{stamp.granted_by} Level {stamp.level}"
    origin = feature.origin or ""
    match = _LEVEL_LABEL.match(origin)
    if match:
        return f"{match.group(1)} Level {stamp.level}"
    if not origin and stamp.kind.is_class_level:
        return f"{stamp.granted_by} Level {stamp.level}"
    return origin


# ── Descriptions ─────────────────────────────────────────────────────────────


def render_feature_description(
    feature: Feature,
    character: Character,
    description_mode: DescriptionMode = None,
) -> str | None:
    """The card body's HTML, or None when the card isn't shown in this mode
    (a passive feature on a condensed sheet, or no description at all)."""
    if description_mode is not None and feature.skippable_in_concise:
        return None

    if description_mode == "table":
        table_rows = feature.get_table_description(character)
        if table_rows is not None:
            return Html.highlight_damage_types(Html.key_value_table_to_html(table_rows))

    if description_mode == "concise":
        concise_description = feature.get_concise_description(character)
        if concise_description is not None:
            return description_to_html(concise_description)

    description = feature.get_description(character)
    if description is None:
        return None
    return description_to_html(description)


def description_to_html(description: str) -> str:
    """A feature's description text as HTML: boxes, tables, indented bullet
    lists ("    * ", "        - ", "            > "), bolded lead-ins and
    colored damage types."""
    processed = Html.boxes_to_html(description)
    processed = Html.tables_to_html(processed)

    bullet_prefixes = [
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
        for prefix, level in bullet_prefixes:
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
            html_parts.append(f"<li>{_bolden_line(bullet_text)}</li>")
        else:
            close_all_levels()
            stripped = line.strip()
            if stripped:
                if stripped.startswith("<"):
                    html_parts.append(stripped)
                else:
                    html_parts.append(f"<p>{_bolden_line(stripped)}</p>")

    close_all_levels()

    result = "\n".join(html_parts)
    if result and not result.endswith("\n"):
        result += "\n"
    return Html.highlight_damage_types(result)


def _bolden_line(text: str) -> str:
    bolded = Html.bold_lead_in(text)
    if bolded is not None:
        return bolded
    return text


# ── Cards ────────────────────────────────────────────────────────────────────


def write_feature_card(
    feature: Feature,
    character: Character,
    file: TextIO,
    description_mode: DescriptionMode = None,
    max_level: int | None = None,
) -> None:
    """The feature's card, with its extensions nested as upgrade blocks. On a
    per-level page (max_level set), extensions granted above the page's level,
    or above the parent's level (they get a card of their own there), are
    left out."""
    html_description = render_feature_description(feature, character, description_mode)
    if html_description is None:
        return

    _write_card_open(feature, file, description_mode, feature_label(feature, character))

    resource_tiles = feature.get_resource_tiles(character)
    if resource_tiles:
        file.write("<div class='feature-resource-section'>\n")
        for group_label, steps in resource_tiles:
            file.write("<div class='feature-resource-group'>\n")
            file.write(
                f"<span class='feature-resource-group-label'>{group_label}</span>\n"
            )
            file.write("<div class='feature-resource-tiles'>\n")
            for step_label, value in steps:
                file.write(_resource_tile_html(step_label, value))
            file.write("</div>\n")
            file.write("</div>\n")
        file.write("</div>\n")

    file.write(f"{html_description}\n")
    if feature.uses is not None:
        file.write(_uses_html(feature.uses) + "\n")

    parent_level = character.stamp_of(feature).level
    for extension in ordered_extensions(character, feature):
        extension_level = character.stamp_of(extension).level
        if max_level is not None:
            if extension_level > max_level:
                continue
            if extension_level > parent_level:
                continue

        extension_html = render_feature_description(
            extension, character, description_mode
        )
        if extension_html is None:
            continue
        extension_tags = "".join(
            f" {tag}" for tag in _header_tags_html(extension, description_mode)
        )
        label = feature_label(extension, character)
        file.write(
            _upgrade_block_html(
                f"{label}: {extension.name}{extension_tags}",
                extension_html,
                extension.uses,
            )
        )

    _write_card_close(file)


def write_extension_card(
    feature: Feature,
    character: Character,
    file: TextIO,
    parent_name: str,
    description_mode: DescriptionMode = None,
) -> None:
    """An extension as a card of its own on its level page, flagged as
    extending `parent_name` (with the same blue-label styling as a nested
    upgrade block)."""
    html_description = render_feature_description(feature, character, description_mode)
    if html_description is None:
        return

    # The card header already carries this feature's tags (Passive included),
    # so the label only names the parent.
    _write_card_open(feature, file, description_mode, feature_label(feature, character))
    file.write(
        _upgrade_block_html(f"Extends {parent_name}", html_description, feature.uses)
    )
    _write_card_close(file)


def _write_card_open(
    feature: Feature,
    file: TextIO,
    description_mode: DescriptionMode,
    label: str,
) -> None:
    """Write a card's header (name, tag chips, origin) and open its body.
    Close with _write_card_close."""
    if _shows_passive_tag(feature, description_mode):
        card_class = "feature-card is-passive"
    else:
        card_class = "feature-card"
    file.write(f"<div class='{card_class}'>\n")
    file.write("<div class='feature-header'>\n")
    file.write("<span class='feature-name-group'>\n")
    file.write(f"<span class='feature-name'>{feature.name}</span>\n")
    for tag in _header_tags_html(feature, description_mode):
        file.write(f"{tag}\n")
    file.write("</span>\n")
    file.write(f"<span class='feature-origin'>{label}</span>\n")
    file.write("</div>\n")
    file.write("<div class='feature-body'>\n")


def _write_card_close(file: TextIO) -> None:
    file.write("</div>\n")
    file.write("</div>\n")


def _upgrade_block_html(label: str, body_html: str, uses: FeatureUses | None) -> str:
    """An extension rendered as a blue-labelled .feature-upgrade block."""
    uses_html = "\n" + _uses_html(uses) if uses is not None else ""
    return (
        f"<div class='feature-upgrade'>\n"
        f"<span class='feature-upgrade-label'>{label}</span>\n"
        f"<div class='feature-upgrade-body'>{body_html}{uses_html}</div>\n"
        f"</div>\n"
    )


# ── Tag chips ────────────────────────────────────────────────────────────────


def _shows_passive_tag(feature: Feature, description_mode: DescriptionMode) -> bool:
    # A skippable-in-concise feature that's still showing means we're on a
    # full-mode sheet - flag it as passive so the player knows there's
    # nothing here to actively track.
    return description_mode is None and feature.skippable_in_concise


def _header_tags_html(feature: Feature, description_mode: DescriptionMode) -> list[str]:
    """The tag chips shown beside a feature's name (Passive, action economy,
    duration, range, usage roles), in display order."""
    activation = feature.activation
    if _shows_passive_tag(feature, description_mode):
        passive_tag = "<span class='feature-passive-tag'>Passive</span>"
    else:
        passive_tag = ""
    tags = [
        passive_tag,
        _action_tag_html(activation.action_type),
        _duration_tag_html(activation.duration),
        _range_tag_html(activation.range, activation.range_shape),
        _usage_tags_html(feature.usage_tags),
    ]
    return [tag for tag in tags if tag]


_ACTION_LABELS = {
    "action": "Action",
    "bonus_action": "Bonus Action",
    "reaction": "Reaction",
}


def _action_tag_html(
    action_type: "ActionType | Literal['action', 'bonus_action', 'reaction'] | None",
) -> str:
    if action_type is None:
        return ""
    if isinstance(action_type, ActionType):
        value = action_type.value
    else:
        value = action_type
    label = _ACTION_LABELS[value]
    return f"<span class='feature-action-tag tag-{value}'>{label}</span>"


def _duration_tag_html(duration: str | None) -> str:
    if duration is None:
        return ""
    return f"<span class='feature-duration-tag'>Duration: {duration}</span>"


def _range_tag_html(range_text: str | None, range_shape: str | None = None) -> str:
    if range_text is None:
        return ""
    label = f"{range_text} ({range_shape})" if range_shape else range_text
    return f"<span class='feature-range-tag'>Range: {label}</span>"


# In display order, regardless of the order a feature lists them in.
_USAGE_LABELS = {
    "damage": "Damage",
    "heal": "Heal",
    "buff": "Buff",
    "control": "Control",
    "utility": "Utility",
    "summon": "Summon",
}


def _usage_tags_html(usage_tags: Sequence[str] | None) -> str:
    if not usage_tags:
        return ""
    ordered = [tag for tag in _USAGE_LABELS if tag in usage_tags]
    return " ".join(
        f"<span class='feature-usage-tag tag-{tag}'>{_USAGE_LABELS[tag]}</span>"
        for tag in ordered
    )


def _uses_html(uses: FeatureUses) -> str:
    return Html.render_slot_boxes(
        uses.max_uses,
        regain_all_on=uses.regain_all_on,
        regain_x_on=uses.regain_x_on,
        current_formula=uses.current_formula,
    )


def _resource_tile_html(label: str, value) -> str:
    return (
        "<div class='stat-tile stat-tile-resource'>"
        f"<span class='stat-tile-label'>{label}</span>"
        f"<span class='stat-tile-value'>{value}</span>"
        "</div>\n"
    )
