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
