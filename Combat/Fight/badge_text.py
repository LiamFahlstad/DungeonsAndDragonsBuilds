"""What a badge shows when its card is clicked or hovered, Qt-free
(Notes/combat-ui-refactor-plan.md, step 5.4, R44): a spell's card, a
feature's, and the colors of their badges. The cards view draws them, and
what gives a badge (effects_given.py, Cast Spell, Enable Feature) stores
them on the combatant (Combat/Effects/active_effects.py's describe)."""

from Presentation.FeatureCards import feature_label

# The color of a condition badge a feature puts on a creature.
FEATURE_BADGE_COLOR = "#4c7ac9"


def spell_badge_description(spell) -> str:
    """What a condition badge a spell put on a creature shows when clicked or
    hovered: the spell's card (level, school, casting time, range, target,
    components, duration) and its rules text, as HTML."""
    tags = []
    if spell.is_concentration:
        tags.append("Concentration")
    if spell.is_ritual:
        tags.append("Ritual")
    tag_text = f" [{', '.join(tags)}]" if tags else ""
    level = "Cantrips" if spell.level == 0 else f"Level {spell.level}"
    target_text = (
        spell.target.value.replace("_", " ").title()
        if spell.target is not None
        else "None"
    )
    return (
        f"<b style='color:#c9a84c; font-size:14px;'>{spell.name}</b>{tag_text}"
        f"<br><span style='color:#a0a0b0;'>{level} · {spell.school}</span>"
        f"<br><br><b>Casting Time:</b> {spell.casting_time}"
        f"<br><b>Range:</b> {spell.range}"
        f"<br><b>Target:</b> {target_text}"
        f"<br><b>Components:</b> {spell.components}"
        f"<br><b>Duration:</b> {spell.duration}"
        f"<br><br>{spell.description.replace(chr(10) + chr(10), '<br><br>')}"
    )


def spell_badge_color(spell) -> str:
    """A spell's condition badge's color: its school's."""
    from CharacterContent.Spells.SpellFactory import Spell

    return Spell.get_school_color(spell.school)


def feature_uses_text(char: dict, feature, sb) -> str:
    """'<remaining>/<max>' for a limited-use feature, or 'None' for a
    passive/unlimited one. Remaining is tracked in char['feature_uses_used'],
    keyed by feature name, and reset by a long/short rest (see Combat/CombatUIQt/rest.py).
    """
    if feature.uses is None:
        return "None"
    max_uses = feature.number_of_uses(sb) if sb is not None else feature.uses.max_uses
    used = char.get("feature_uses_used", {}).get(feature.name, 0)
    remaining = max(max_uses - used, 0)
    return f"{remaining}/{max_uses}"


def feature_condition_tooltip(char: dict, feature) -> str:
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
    uses_text = feature_uses_text(char, feature, sb)

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
