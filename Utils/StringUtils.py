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

            # If no space found, force break at max length
            if last_space == -1:
                last_space = max_sentence_length

            new_parts.append(line[:last_space])
            line = line[last_space:].lstrip()

        new_parts.append(line)

    if html:
        # return "<br>\n".join(new_parts)
        return "\n".join(new_parts)

    return "\n".join(new_parts)


def bolden_text_html(text: str) -> str:
    new_lines = []

    for line in text.split("\n"):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped == "<br>":
            new_lines.append(line)
            continue

        # --- Check for short first sentence (period) ---
        if "." in stripped:
            first, rest = stripped.split(".", 1)
            if len(first.split()) < 5:  # and rest.strip():
                new_lines.append(f"<strong>{first.strip()}.</strong> {rest.strip()}")
                continue

        # --- Check for short label (colon) ---
        if ":" in stripped:
            first, rest = stripped.split(":", 1)
            if len(first.split()) < 10 and rest.strip():
                new_lines.append(f"<strong>{first.strip()}:</strong> {rest.strip()}")
                continue

        # --- Default ---
        new_lines.append(line)

    return "\n".join(new_lines)
