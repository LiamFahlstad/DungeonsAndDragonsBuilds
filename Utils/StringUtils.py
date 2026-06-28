def _bold_prefix(line: str, separator: str, max_words: int):
    if separator not in line:
        return None

    first, rest = line.split(separator, 1)
    if len(first.split()) < max_words and rest.strip():
        return f"<strong>{first.strip()}{separator}</strong> {rest.strip()}"

    return None


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


_RESET_PREFIX = "[RESET:"
_RESET_SUFFIX = "]"


def add_boxes(description: str, box_count: int, reset: str = None) -> str:
    """Append box symbols to *description*.

    Args:
        description: The feature text to append boxes to.
        box_count: How many checkbox symbols to add.
        reset: Optional reset cadence label, e.g. ``"long rest"``,
            ``"short rest"``, or ``"dawn"``.  When supplied a small note is
            rendered beneath the boxes in the HTML output.
    """
    box_symbol = "⬜"

    boxes = " ".join([box_symbol] * box_count)

    result = f"{description}\n{boxes}\n"
    if reset is not None:
        result += f"{_RESET_PREFIX}{reset}{_RESET_SUFFIX}\n"
    return result


def boxes_to_html(description: str) -> str:
    def normalize_box_line(line: str) -> str:
        stripped = line.strip()
        if stripped.endswith("<br>"):
            stripped = stripped[:-4].rstrip()
        return stripped

    def box_count(line: str, token: str) -> int:
        parts = line.split()
        if parts and all(part == token for part in parts):
            return len(parts)
        return 0

    def parse_reset_label(line: str) -> str | None:
        """Return the reset label text if *line* is a reset sentinel, else None."""
        normalized = normalize_box_line(line)
        if normalized.startswith(_RESET_PREFIX) and normalized.endswith(_RESET_SUFFIX):
            return normalized[len(_RESET_PREFIX) : -len(_RESET_SUFFIX)]
        return None

    lines = description.split("\n")
    new_lines = []
    index = 0

    while index < len(lines):
        top_line = normalize_box_line(lines[index])
        top_count = box_count(top_line, "⬜")

        if top_count:
            boxes_html = '<span class="slot-box"></span>' * top_count

            # Peek at the next line to see if it carries a reset label.
            reset_label = None
            if index + 1 < len(lines):
                reset_label = parse_reset_label(lines[index + 1])

            if reset_label is not None:
                reset_html = f'<span class="slot-reset-label">Resets on {reset_label}</span>'
                new_lines.append(
                    '<div class="slot-box-group">'
                    + boxes_html
                    + "</div>"
                    + "\n"
                    + reset_html
                )
                index += 2  # consume both the box line and the reset sentinel
            else:
                new_lines.append('<div class="slot-box-group">' + boxes_html + "</div>")
                index += 1
            continue

        # Skip bare reset sentinel lines that appear without a preceding box line
        # (shouldn't normally happen, but guard against it).
        if parse_reset_label(lines[index]) is not None:
            index += 1
            continue

        new_lines.append(lines[index])
        index += 1

    return "\n".join(new_lines)


def _is_reset_sentinel_line(line: str) -> bool:
    """Return True if *line* is (possibly followed by <br>) a reset sentinel."""
    stripped = line.strip()
    if stripped.endswith("<br>"):
        stripped = stripped[:-4].rstrip()
    return stripped.startswith(_RESET_PREFIX) and stripped.endswith(_RESET_SUFFIX)


def bolden_text_html(text: str) -> str:
    new_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped == "<br>":
            new_lines.append(line)
            continue

        # Preserve reset sentinel lines so that boxes_to_html can process them.
        if _is_reset_sentinel_line(line):
            new_lines.append(line)
            continue

        bolded_line = _bold_prefix(stripped, ".", 5)
        if bolded_line is not None:
            new_lines.append(bolded_line)
            continue

        bolded_line = _bold_prefix(stripped, ":", 10)
        if bolded_line is not None:
            new_lines.append(bolded_line)
            continue

        new_lines.append(line)

    return "\n".join(new_lines)
