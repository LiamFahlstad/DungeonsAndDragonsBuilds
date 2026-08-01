from typing import TYPE_CHECKING, TextIO

from Utils import StringUtils

if TYPE_CHECKING:
    from .spell import Spell


def write_spell_to_file(
    spell: "Spell",
    file: TextIO,
    show_preparation_checkbox: bool = False,
    show_classes: bool = False,
):  # writes HTML
    # ── Detect special tags ──────────────────────────────────────────────
    is_concentration = spell.is_concentration
    is_ritual = spell.is_ritual

    # ── Process description ──────────────────────────────────────────────
    description = spell.description.strip()

    # Split off the higher-level note, if present
    higher_level_marker = "Using a Higher-Level Spell Slot."
    higher_level_html = ""
    if higher_level_marker in description:
        main_desc, higher_rest = description.split(higher_level_marker, 1)
        main_desc = StringUtils.boxes_to_html(main_desc.strip())
        main_desc = StringUtils.bolden_text_html(main_desc).replace("\n", "<br>")
        higher_rest = StringUtils.boxes_to_html(higher_rest.strip())
        higher_rest = StringUtils.bolden_text_html(higher_rest).replace(
            "\n", "<br>"
        )
        higher_level_html = f"<strong>{higher_level_marker}</strong> {higher_rest}"
    else:
        main_desc = StringUtils.boxes_to_html(description)
        main_desc = StringUtils.bolden_text_html(main_desc).replace("\n", "<br>")

    # ── Level label ──────────────────────────────────────────────────────
    level_label = "Cantrip" if spell.level == 0 else f"Level {spell.level}"

    # ── Build tag chips ──────────────────────────────────────────────────
    tags_html = ""
    if is_concentration:
        tags_html += "<span class='stag stag-concentration'>Concentration</span> "
    if is_ritual:
        tags_html += "<span class='stag stag-ritual'>Ritual</span> "

    # ── Quick-stats cells ────────────────────────────────────────────────
    # Left ~35%: level, school, components
    school_color = spell.get_school_color(spell.school)
    left_cell = (
        f"<span class='slabel'>{level_label}</span>"
        f"<span class='ssep'>·</span>"
        f"<span class='slabel'>School</span> <span style='color: {school_color}; print-color-adjust: exact; -webkit-print-color-adjust: exact;'>{spell.school}</span>"
        f"<span class='ssep'>·</span>"
        f"<span class='slabel'>Components</span> {spell.components}"
    )
    # Right ~65%: casting time, range, duration
    duration_display = spell.duration
    if is_concentration:
        # Strip the "Concentration, " prefix for display; the tag already shows it
        duration_display = (
            spell.duration[len("Concentration, ") :]
            if spell.duration.lower().startswith("concentration, ")
            else spell.duration
        )
    right_cell = (
        f"<span class='slabel'>Cast</span> {spell.casting_time}"
        f"<span class='ssep'>·</span>"
        f"<span class='slabel'>Range</span> {spell.range}"
        f"<span class='ssep'>·</span>"
        f"<span class='slabel'>Duration</span> {duration_display}"
    )

    # ── Classes row (optional) ─────────────────────────────────────────────
    classes_html = ""
    if show_classes and spell.classes:
        class_chips = " ".join(
            f"<span class='sclass-chip'>{cls}</span>" for cls in spell.classes
        )
        classes_html = (
            f"<span class='slabel'>Classes</span> {class_chips}"
        )

    # ── Spell name with optional checkbox ─────────────────────────────────
    spell_name_display = spell.name
    if (
        show_preparation_checkbox and spell.level > 0
    ):  # Don't show checkbox for cantrips
        spell_name_display = (
            f"<span class='spell-prep-checkbox'></span> {spell.name}"
        )

    # ── Write card ───────────────────────────────────────────────────────
    file.write("<table class='spell-card'>\n")

    # Name header row (full width)
    file.write(
        f"<tr><th class='spell-name' colspan='2'>{spell_name_display}"
        f"{(' ' + tags_html.strip()) if tags_html else ''}"
        f"</th></tr>\n"
    )

    # Quick-stats row
    file.write(
        f"<tr class='spell-quickstats'>"
        f"<td class='sqs-left'>{left_cell}</td>"
        f"<td class='sqs-right'>{right_cell}</td>"
        f"</tr>\n"
    )

    # Classes row (if requested)
    if classes_html:
        file.write(
            f"<tr class='spell-classes-row'>"
            f"<td colspan='2'>{classes_html}</td>"
            f"</tr>\n"
        )

    # Description row
    file.write(
        f"<tr class='spell-desc-row'>"
        f"<td class='sdesc-text' colspan='2'>{main_desc}</td>"
        f"</tr>\n"
    )

    # Higher-level row (if present)
    if higher_level_html:
        file.write(
            f"<tr class='spell-higher-row'>"
            f"<td class='sdesc-text' colspan='2'>{higher_level_html}</td>"
            f"</tr>\n"
        )

    # Additional ruling row (if present) - e.g. a Channel Divinity option
    # that lets this specific character cast the spell without a slot.
    if spell.additional_ruling:
        ruling_html = StringUtils.bolden_text_html(
            StringUtils.boxes_to_html(spell.additional_ruling.strip())
        ).replace("\n", "<br>")
        file.write(
            f"<tr class='spell-higher-row'>"
            f"<td class='sdesc-text' colspan='2'><strong>Ruling.</strong> {ruling_html}</td>"
            f"</tr>\n"
        )

    file.write("</table>\n")
