"""Where a grant comes from: GrantKind and GrantStamp. Plain records - they
import nothing from the rest of the Model."""

from enum import Enum

import attr


class GrantKind(Enum):
    """Who a grant comes from. The definition order is the order the sheet
    lists features that tie on level, passiveness and name (see
    Character.feature_sort_key)."""

    SPECIES = "species"
    BACKGROUND = "background"
    ORIGIN_FEAT = "origin feat"
    CLASS = "class"
    SUBCLASS = "subclass"
    OTHER = "other"

    @property
    def is_class_level(self) -> bool:
        """Granted at a class or subclass level (so labeled "<class> Level N"
        and listed on that level's page)."""
        return self in (GrantKind.CLASS, GrantKind.SUBCLASS)

    @property
    def sheet_rank(self) -> int:
        """Position in the sheet's tie-breaking order (definition order)."""
        return list(GrantKind).index(self)


@attr.s(frozen=True, auto_attribs=True)
class GrantStamp:
    """Where a grant comes from: the class-relative level it was granted at,
    what kind of source granted it, and which one ("Wizard", "Rock Gnome",
    "Alert"). Stamped by the builder's Grants scope (Model/Grants.py)."""

    level: int = 1
    kind: GrantKind = GrantKind.OTHER
    granted_by: str = "Other"
