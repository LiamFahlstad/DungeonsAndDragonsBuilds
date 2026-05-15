from typing import Any, TextIO


def _expand_multiline_rows(
    headers: list[str], rows: list[list[Any]]
) -> list[list[Any]]:
    expanded_rows: list[list[Any]] = []

    for row in rows:
        multiline_index = None
        split_values = None

        for index, value in enumerate(row):
            if isinstance(value, str) and "\n" in value:
                if index != len(headers) - 1:
                    raise ValueError(
                        "Multi-line values are only supported in the last column"
                    )
                multiline_index = index
                split_values = value.split("\n")
                break

        if multiline_index is None:
            expanded_rows.append(row)
            continue

        first_row = row.copy()
        first_row[multiline_index] = split_values[0]
        expanded_rows.append(first_row)

        for split_value in split_values[1:]:
            expanded_rows.append([""] * (len(headers) - 1) + [split_value])

    return expanded_rows


def _column_widths(headers: list[str], rows: list[list[Any]]) -> list[int]:
    return [
        max(len(str(header)), *(len(str(row[index])) for row in rows if row))
        for index, header in enumerate(headers)
    ]


def _format_row(row: list[Any], col_widths: list[int], separator: str) -> str:
    return separator.join(
        f"{str(row[index]):<{col_widths[index]}}" for index in range(len(col_widths))
    )


def write_table(headers: list[str], rows: list[list[Any]], file: TextIO):
    """
    Write a table with given headers and rows into a file.

    :param headers: list of column names, e.g. ["Height", "Age", "Gender"]
    :param rows: list of lists of values, e.g. [[183, 24, "Male"], [170, 30, "Female"]]
    :param file: an open file object (opened with 'w' mode)
    """
    rows = _expand_multiline_rows(headers, rows)
    col_widths = _column_widths(headers, rows)

    header_line = _format_row(headers, col_widths, " | ")
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    # Write header and separator
    file.write(header_line + "\n")
    file.write(separator + "\n")

    # Write each row
    for row in rows:
        if not row:
            file.write(separator + "\n")
            continue
        file.write(_format_row(row, col_widths, " | ") + "\n")


def write_table_with_title(
    title: str, headers: list[str], rows: list[list[str]], file: TextIO
):
    col_widths = _column_widths(headers, rows)
    header_line = "| " + _format_row(headers, col_widths, " | ") + " |"
    separator = (
        "+-" + "-+-".join("-" * col_widths[i] for i in range(len(headers))) + "-+"
    )

    # Write header and separator
    file.write(f" {title} ".center(len(header_line), "=") + "\n")
    file.write(header_line + "\n")
    file.write(separator + "\n")

    # Write each row
    for row in rows:
        if not row:
            file.write(separator + "\n")
            continue
        file.write("| " + _format_row(row, col_widths, " | ") + " |\n")
    file.write(separator + "\n")


def write_separator(file: TextIO, text=None, length=80):
    """Write a separator line or titled separator block to a file."""
    if text:
        file.write("#" * length + "\n")
        file.write("# " + f" {text} ".center(length - 4, "=") + " #\n")
        file.write("#" * length + "\n")
    else:
        file.write("#" * length + "\n")
