from typing import Any, TextIO


def write_table(headers: list[str], rows: list[list[Any]], file: TextIO):
    """
    Write a table with given headers and rows into a file.

    :param headers: list of column names, e.g. ["Height", "Age", "Gender"]
    :param rows: list of lists of values, e.g. [[183, 24, "Male"], [170, 30, "Female"]]
    :param file: an open file object (opened with 'w' mode)
    """
    new_rows = []

    for row in rows:
        # Find if there's a multiline cell
        multiline_index = None
        split_values = None

        for i, value in enumerate(row):
            if "\n" in value:
                if i != len(headers) - 1:
                    raise ValueError(
                        "Multi-line values are only supported in the last column"
                    )
                multiline_index = i
                split_values = value.split("\n")
                break

        # If no multiline cell → keep row as-is
        if multiline_index is None:
            new_rows.append(row)
            continue

        # First row: keep original values, but replace last column with first split
        first_row = row.copy()
        first_row[multiline_index] = split_values[0]
        new_rows.append(first_row)

        # Remaining rows: empty columns except last
        for split_value in split_values[1:]:
            new_rows.append([""] * (len(headers) - 1) + [split_value])

    rows = new_rows
    # Determine column widths (max length among header and each column's data)
    col_widths = [
        max(len(str(header)), *(len(str(row[i])) for row in rows if row))
        for i, header in enumerate(headers)
    ]

    # Build the header row
    header_line = " | ".join(
        f"{header:<{col_widths[i]}}" for i, header in enumerate(headers)
    )
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    # Write header and separator
    file.write(header_line + "\n")
    file.write(separator + "\n")

    # Write each row
    for row in rows:
        if not row:
            file.write(separator + "\n")
            continue
        row_line = " | ".join(
            f"{str(row[i]):<{col_widths[i]}}" for i in range(len(headers))
        )
        file.write(row_line + "\n")


def write_table_with_title(
    title: str, headers: list[str], rows: list[list[str]], file: TextIO
):
    # Determine column widths (max length among header and each column's data)
    col_widths = [
        max(len(str(header)), *(len(str(row[i])) for row in rows if row))
        for i, header in enumerate(headers)
    ]

    # Build the header row
    header_line = (
        "| "
        + " | ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers))
        + " |"
    )
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
        row_line = " | ".join(
            f"{str(row[i]):<{col_widths[i]}}" for i in range(len(headers))
        )
        file.write("| " + row_line + " |\n")
    file.write(separator + "\n")


def write_separator(file: TextIO, text=None, length=80):
    """Write a separator line or titled separator block to a file."""
    if text:
        file.write("#" * length + "\n")
        file.write("# " + f" {text} ".center(length - 4, "=") + " #\n")
        file.write("#" * length + "\n")
    else:
        file.write("#" * length + "\n")
