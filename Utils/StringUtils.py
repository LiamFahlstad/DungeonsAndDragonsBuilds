def wrap_text(description: str, max_sentence_length: int, html: bool = False) -> str:
    """
    Wraps text so that no line exceeds max_sentence_length.
    Breaks at the last space before the limit when possible,
    otherwise forces a hard split.
    """
    if max_sentence_length <= 0:
        raise ValueError("max_sentence_length must be > 0")

    parts = description.split("\n")
    new_parts = []

    for line in parts:
        while len(line) > max_sentence_length:
            last_space = line.rfind(" ", 0, max_sentence_length)
            if last_space == -1:
                last_space = max_sentence_length

            new_parts.append(line[:last_space])
            line = line[last_space:].lstrip()

        new_parts.append(line)

    return "\n".join(new_parts)


def compress_level_progression(
    level_to_value: dict, max_level: int = 20
) -> list[tuple[str, str]]:
    """Collapse a level->value mapping into compact (level range, value)
    pairs, merging consecutive levels that share the same value into one
    range - e.g. {1: "1d6", 2: "1d6", 3: "1d6", 4: "1d6", 5: "1d8", ...}
    becomes [("1-4", "1d6"), ("5-...", "1d8"), ...]. Used to show a
    feature's full level progression (e.g. a martial arts die stepping up)
    in a compact strip rather than one row per level.
    """
    levels = sorted(level for level in level_to_value if 1 <= level <= max_level)
    ranges: list[list] = []
    for level in levels:
        value = str(level_to_value[level])
        if ranges and ranges[-1][2] == value and ranges[-1][1] == level - 1:
            ranges[-1][1] = level
        else:
            ranges.append([level, level, value])
    return [
        (str(start) if start == end else f"{start}-{end}", value)
        for start, end, value in ranges
    ]


def add_boxes(
    description: str,
    box_count: int,
    regain_all_on: str = None,
    regain_x_on: tuple = None,
    max_box_count: int | None = None,
    current_formula: str | None = None,
) -> str:
    """Append box symbols to *description*.

    Args:
        description: The feature text to append boxes to.
        box_count: How many checkbox symbols to add (the "current"/build
            value, used on the full character sheet).
        regain_all_on: Optional reset cadence label for full recovery, e.g.
            ``"long rest"``, ``"short rest"``, or ``"dawn"``. When supplied a
            note is rendered beneath the boxes in the HTML output.
        regain_x_on: Optional tuple of (count: int, cadence: str) for partial
            recovery on a shorter rest, e.g. ``(2, "short rest")``. If both
            this and ``regain_all_on`` are provided, the description will be
            "Regain <N> on <cadence>, all on <regain_all_on>".
        max_box_count: Optional ceiling value used instead of box_count on
            per-level feature shard pages, which are generated once and never
            regenerated as the player levels up in play - so they show the
            maximum the underlying formula could ever reach, letting the
            player track on paper how many of those boxes they can currently
            use. Defaults to box_count (no current/max distinction) when
            omitted. Must be >= box_count.
        current_formula: Optional short plain-English fragment describing how
            the build's real "current" count is derived (e.g. "equal to your
            Monk level."). Only rendered on level shard pages (where the
            boxes above show max_box_count rather than box_count), directly
            beneath the boxes/reset label, so the player can work out their
            real current count by hand. Ignored on the full character sheet,
            where the boxes already show the current count directly.
    """
    from Utils.Html import (
        BOXES_PREFIX,
        BOXES_SUFFIX,
        CURRENT_PREFIX,
        CURRENT_SUFFIX,
        RESET_PREFIX,
        RESET_SUFFIX,
    )

    if max_box_count is None:
        max_box_count = box_count
    if max_box_count < box_count:
        raise ValueError(
            f"max_box_count ({max_box_count}) must be >= box_count ({box_count})"
        )

    result = f"{description}\n{BOXES_PREFIX}{box_count}:{max_box_count}{BOXES_SUFFIX}\n"

    # Determine the reset label to append
    reset_label = None

    if regain_x_on is not None:
        if not isinstance(regain_x_on, tuple) or len(regain_x_on) != 2:
            raise ValueError(
                "regain_x_on must be a tuple of (count: int, cadence: str)"
            )
        count, cadence = regain_x_on
        if not isinstance(count, int) or count < 0:
            raise ValueError("regain_x_on count must be a non-negative integer")
        if count >= box_count:
            raise ValueError(
                f"regain_x_on count ({count}) must be less than box_count ({box_count})"
            )
        # Pluralize "box" or "boxes"
        box_word = "box" if count == 1 else "boxes"
        if regain_all_on is not None:
            reset_label = (
                f"regain {count} {box_word} on a {cadence}, all on a {regain_all_on}"
            )
        else:
            reset_label = f"regain {count} {box_word} on a {cadence}"
    elif regain_all_on is not None:
        reset_label = f"regain all on a {regain_all_on}"

    if reset_label is not None:
        result += f"{RESET_PREFIX}{reset_label}{RESET_SUFFIX}\n"

    if current_formula is not None:
        result += f"{CURRENT_PREFIX}{current_formula}{CURRENT_SUFFIX}\n"

    return result
