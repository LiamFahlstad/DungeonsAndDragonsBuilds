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


def add_boxes(description: str, box_count: int) -> str:
    box_symbol = "⬜"

    boxes = " ".join([box_symbol] * box_count)

    return f"{description}\n{boxes}\n"


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

    lines = description.split("\n")
    new_lines = []
    index = 0

    while index < len(lines):
        top_line = normalize_box_line(lines[index])
        top_count = box_count(top_line, "⬜")

        if top_count:
            boxes_html = '<span class="slot-box"></span>' * top_count
            new_lines.append('<div class="slot-box-group">' + boxes_html + "</div>")
            index += 1
            continue

        new_lines.append(lines[index])
        index += 1

    return "\n".join(new_lines)


def bolden_text_html(text: str) -> str:
    new_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped == "<br>":
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
