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


def add_boxes(
    description: str,
    box_count: int,
    regain_all_on: str = None,
    regain_x_on: tuple = None,
) -> str:
    """Append box symbols to *description*.

    Args:
        description: The feature text to append boxes to.
        box_count: How many checkbox symbols to add.
        regain_all_on: Optional reset cadence label for full recovery, e.g.
            ``"long rest"``, ``"short rest"``, or ``"dawn"``. When supplied a
            note is rendered beneath the boxes in the HTML output.
        regain_x_on: Optional tuple of (count: int, cadence: str) for partial
            recovery on a shorter rest, e.g. ``(2, "short rest")``. If both
            this and ``regain_all_on`` are provided, the description will be
            "Regain <N> on <cadence>, all on <regain_all_on>".
    """
    from Utils.Html import RESET_PREFIX, RESET_SUFFIX

    box_symbol = "⬜"

    boxes = " ".join([box_symbol] * box_count)

    result = f"{description}\n{boxes}\n"

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

    return result
