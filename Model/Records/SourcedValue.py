"""SourcedValue: a number and the label of where it comes from. A plain
record - it imports nothing from the rest of the Model."""

import attr


@attr.s(frozen=True, auto_attribs=True)
class SourcedValue:
    """One contribution to a total, e.g. a +2 skill bonus from "Guidance" or
    2 carrying capacity slots from a "Backpack"."""

    value: int
    source: str
