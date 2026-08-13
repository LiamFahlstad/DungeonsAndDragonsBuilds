from typing import TYPE_CHECKING, TextIO

from Utils import Html

SPELL_CARD_CSS = """/* ── Spell entries ────────────────────────────────────────────────── */
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

        /* Each spell, stacked without an outer box */
        .spell-entry {
            font-size: 0.85rem;
            padding: 0.35rem 0;
            max-width: none;
        }

        /* Separator line between consecutive spells */
        .spell-entry + .spell-entry {
            border-top: 2px solid #6888a8;
        }

        /* Spell name */
        .spell-name {
            display: block;
            color: #3a5a7a;
            font-size: 1rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin: 0 0 0.2rem 0;
        }

        /* Quick-stats — two flexible columns, wrapping if the page is narrow */
        .spell-quickstats {
            display: flex;
            flex-wrap: wrap;
            gap: 0.15rem 1.2rem;
            font-size: 0.82rem;
            margin: 0 0 0.2rem 0;
        }

        .sqs-left, .sqs-right {
            flex: 1 1 45%;
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

        /* Classes list (only rendered when show_classes=True) */
        .spell-classes {
            font-size: 0.78rem;
            margin: 0 0 0.2rem 0;
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

        /* Description */
        .spell-desc,
        .spell-higher {
            font-size: 0.8rem;
            color: #333;
            margin: 0.2rem 0 0 0;
        }

        /* Higher-level note / ruling get a subtle accent */
        .spell-higher {
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

    # ── Write entry ──────────────────────────────────────────────────────
    file.write("<div class='spell-entry'>\n")

    # Name
    file.write(
        f"<span class='spell-name'>{spell_name_display}"
        f"{(' ' + tags_html.strip()) if tags_html else ''}"
        f"</span>\n"
    )

    # Quick-stats
    file.write(
        f"<div class='spell-quickstats'>"
        f"<span class='sqs-left'>{left_cell}</span>"
        f"<span class='sqs-right'>{right_cell}</span>"
        f"</div>\n"
    )

    # Classes (if requested)
    if classes_html:
        file.write(f"<div class='spell-classes'>{classes_html}</div>\n")

    # Description
    file.write(f"<div class='spell-desc'>{main_desc}</div>\n")

    # Higher-level note (if present)
    if higher_level_html:
        file.write(f"<div class='spell-higher'>{higher_level_html}</div>\n")

    # Additional ruling (if present) - e.g. a Channel Divinity option
    # that lets this specific character cast the spell without a slot.
    if spell.additional_ruling:
        ruling_html = Html.bolden_text_html(
            Html.boxes_to_html(spell.additional_ruling.strip())
        ).replace("\n", "<br>")
        file.write(
            f"<div class='spell-higher'><strong>Ruling.</strong> {ruling_html}</div>\n"
        )

    file.write("</div>\n")
