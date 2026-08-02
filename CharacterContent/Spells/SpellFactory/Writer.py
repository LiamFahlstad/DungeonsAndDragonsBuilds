from typing import TYPE_CHECKING, TextIO

from Utils import Html

SPELL_CARD_CSS = """/* ── Spell cards ──────────────────────────────────────────────────── */
        .spells {
            max-width: 100%;
        }

        /* Level section header */
        h3.spell-level-header {
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #4a5568;
            margin: 0.8rem 0 0.3rem 0;
            padding: 0;
            border-bottom: 1px solid #c8ccd8;
        }

        /* Gap between consecutive spell cards */
        .spell-gap {
            height: 0;
            max-width: none;
            margin: 0;
            padding: 0;
            border-bottom: none;
            display: none;
        }

        /* Each spell is its own bordered card table */
        table.spell-card {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            border: 2px solid #a8c4d8;
            border-radius: 4px;
            margin: 0 0 8px 0;
            table-layout: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }

        table.spell-card td,
        table.spell-card th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
        }

        /* Add bottom border to spell rows for clearer separation within card */
        table.spell-card tr {
            border-bottom: 1px solid #ddd;
        }

        table.spell-card tr:last-child {
            border-bottom: none;
        }

        /* Spell name — full-width header row */
        .spell-name {
            color: #3a5a7a;
            font-size: 1rem;
            font-weight: 700;
            text-align: left;
            letter-spacing: 0.02em;
            padding: 4px 7px;
            border-bottom: 2px solid #6888a8;
        }

        /* Quick-stats row — two cells side by side */
        tr.spell-quickstats td {
            font-size: 0.82rem;
            white-space: normal;
            padding: 3px 7px;
        }

        .sqs-left {
            width: 50%;
        }

        .sqs-right {
            width: 50%;
        }

        /* Inline label within quick-stats */
        .slabel {
            font-weight: 600;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 2px;
        }

        /* Bullet separator between quick-stat items */
        .ssep {
            color: #aaa;
            margin: 0 5px;
        }

        /* Classes row (only rendered when show_classes=True) */
        tr.spell-classes-row td {
            font-size: 0.78rem;
            padding: 3px 7px;
        }

        .sclass-chip {
            display: inline-block;
            background: #eef2f7;
            color: #3a5a7a;
            border-radius: 3px;
            padding: 1px 6px;
            margin: 1px 3px 1px 0;
            font-size: 0.78rem;
        }

        /* Description rows */
        tr.spell-desc-row td,
        tr.spell-higher-row td {
            font-size: 0.8rem;
            padding: 3px 7px;
        }

        .sdesc-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .sdesc-text {
            color: #333;
        }

        /* Higher-level row gets a subtle accent */
        tr.spell-higher-row td {
            font-style: italic;
            color: #3a5a7a;
        }

        /* Concentration chip — gold */
        .stag {
            display: inline-block;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 0.72rem;
            font-weight: 600;
            margin-left: 5px;
            vertical-align: middle;
            white-space: nowrap;
        }

        .stag-concentration {
            border: 1px solid #c8a227;
            color: #7a5c00;
        }

        /* Ritual chip — teal */
        .stag-ritual {
            border: 1px solid #2a9d8f;
            color: #1a5f58;
        }

        """

if TYPE_CHECKING:
    from .Spell import Spell


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
        main_desc = Html.boxes_to_html(main_desc.strip())
        main_desc = Html.bolden_text_html(main_desc).replace("\n", "<br>")
        higher_rest = Html.boxes_to_html(higher_rest.strip())
        higher_rest = Html.bolden_text_html(higher_rest).replace("\n", "<br>")
        higher_level_html = f"<strong>{higher_level_marker}</strong> {higher_rest}"
    else:
        main_desc = Html.boxes_to_html(description)
        main_desc = Html.bolden_text_html(main_desc).replace("\n", "<br>")

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
        classes_html = f"<span class='slabel'>Classes</span> {class_chips}"

    # ── Spell name with optional checkbox ─────────────────────────────────
    spell_name_display = spell.name
    if (
        show_preparation_checkbox and spell.level > 0
    ):  # Don't show checkbox for cantrips
        spell_name_display = f"<span class='spell-prep-checkbox'></span> {spell.name}"

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
        ruling_html = Html.bolden_text_html(
            Html.boxes_to_html(spell.additional_ruling.strip())
        ).replace("\n", "<br>")
        file.write(
            f"<tr class='spell-higher-row'>"
            f"<td class='sdesc-text' colspan='2'><strong>Ruling.</strong> {ruling_html}</td>"
            f"</tr>\n"
        )

    file.write("</table>\n")
