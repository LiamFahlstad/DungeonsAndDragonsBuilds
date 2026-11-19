"""The area of effect a spell or a feature's use covers on the battle map, and
what it does there while it lasts, as fields instead of words the combat
simulator reads out of its rules text (Notes/explicit-attributes-plan.md,
Phase 3):

    CombatArea(CombatAreaShape.SPHERE, 20)                     # Fireball
    CombatArea(CombatAreaShape.CONE, 15)                       # Burning Hands
    CombatArea(CombatAreaShape.CUBE, 15, from_source=True)     # Thunderwave
    CombatArea(
        CombatAreaShape.CYLINDER, 5,
        acts=(AreaTiming.ENTERS, AreaTiming.MOVED_ONTO, AreaTiming.ENDS),
        move_ft=60, move_action=ActionType.ACTION,
    )                                                          # Moonbeam
    CombatArea(
        CombatAreaShape.WALL, 100, width_ft=1, ring_ft=20,
        blocks=True, cover=AreaCover.TOTAL,
    )                                                          # Wall of Force

A spell says its area in its rules (SpellRules.area); a row whose area
differs from its spell's, or a feature's use, in its CombatEffect.area. The
battle map (Combat/Arena) works out cells from it; the area bar starts from
it, and the GM can change the shape there.

Model/Content/CombatAreaText.py drafts one from rules text, for writing a
spell's class: never while a fight runs.
"""

from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any

from Model.Content.ActionType import ActionType


class CombatAreaShape(StrEnum):
    """The Rules Glossary's six shapes (Areas of Effect), and a Wall, which
    isn't one of them: aimed by its two ends or, as a ring, by its middle."""

    SPHERE = "Sphere"
    CYLINDER = "Cylinder"
    CUBE = "Cube"
    CONE = "Cone"
    LINE = "Line"
    EMANATION = "Emanation"
    WALL = "Wall"


class AreaTiming(StrEnum):
    """When an area that stays acts on a creature: as it enters the area, as
    the area moves onto it (moved, or an Emanation following its caster), as
    its turn starts there, or as its turn ends there."""

    ENTERS = "enters"
    MOVED_ONTO = "moved onto"
    STARTS = "starts"
    ENDS = "ends"


# When an area acts that doesn't say: as a creature enters it or starts its
# turn in it (what the reminders said before arena step 24).
DEFAULT_TIMING = (AreaTiming.ENTERS, AreaTiming.STARTS)


class AreaCover(StrEnum):
    """The cover a wall gives (the battle map's terrain cover keys)."""

    HALF = "half"
    THREE_QUARTERS = "three_quarters"
    TOTAL = "total"


class AreaSight(StrEnum):
    """What an area makes its space to sight, from the least hidden:
    Darkness (Darkvision and Truesight see in it), magical Darkness
    Darkvision can't see through (Truesight only), and a Heavily Obscured
    fog (no sight but Blindsight)."""

    DARKNESS = "Darkness"
    DEEP_DARKNESS = "magical Darkness"
    HEAVILY_OBSCURED = "Heavily Obscured"


# What only a Wall has.
_WALL_FIELDS = ("ring_ft", "side_ft", "blocks", "cover", "difficult")
_MOVE_ACTIONS = (ActionType.ACTION, ActionType.BONUS_ACTION)


def _is_feet(value: Any, least: int = 1) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value >= least


@dataclass(frozen=True)
class CombatArea:
    """An area of effect: its `shape` and `size_ft` (a Sphere's or
    Cylinder's radius, a Cone's or Line's length, a Cube's side, an
    Emanation's distance, a Wall's length), a Line's width or a Wall's
    thickness (`width_ft`), and whether a Sphere, Cylinder or Cube starts
    at its source rather than at a point (`from_source`: Thunderwave's
    Cube, a Sphere "centered on you"; Cones, Lines and Emanations always
    do).

    `point_within_ft`: how far away the point it's centred on may be, when
    that isn't the spell's range ("a point within 60 feet of you"); None:
    the spell's range.

    While it stays on the map: when it acts on a creature (`acts`; empty is
    DEFAULT_TIMING), how far it can be moved and what moving it costs its
    caster (`move_ft`, `move_action`: Moonbeam's 60 feet for an Action;
    None and None when it isn't moved, or the rules don't say), and what
    it makes its space to sight (`obscures`).

    A Wall's own: how far across it can be as a ring instead (`ring_ft`),
    how far from its damaging side it reaches (`side_ft`: Wall of Fire's
    10 feet), and what it is as terrain while it lasts: it `blocks`
    movement, gives `cover`, makes its space `difficult`."""

    shape: CombatAreaShape
    size_ft: int
    width_ft: int = 5
    from_source: bool = False
    point_within_ft: int | None = None
    acts: tuple[AreaTiming, ...] = ()
    move_ft: int | None = None
    move_action: ActionType | None = None
    obscures: AreaSight | None = None
    ring_ft: int | None = None
    side_ft: int | None = None
    blocks: bool = False
    cover: AreaCover | None = None
    difficult: bool = False

    def __post_init__(self):
        # Text is taken too ("Sphere"), as a log keeps it.
        if self.shape not in set(CombatAreaShape):
            raise ValueError(
                f"shape {self.shape!r} is not one of {list(CombatAreaShape)}"
            )
        object.__setattr__(self, "shape", CombatAreaShape(self.shape))
        for name in ("size_ft", "width_ft"):
            if not _is_feet(getattr(self, name)):
                raise ValueError(
                    f"{name} is feet, 1 or more, not {getattr(self, name)!r}"
                )
        for name in ("point_within_ft", "move_ft", "ring_ft", "side_ft"):
            value = getattr(self, name)
            if value is not None and not _is_feet(value):
                raise ValueError(f"{name} is feet, 1 or more, or None, not {value!r}")
        acts = tuple(self.acts)
        if any(when not in set(AreaTiming) for when in acts):
            raise ValueError(f"acts are AreaTiming, not {self.acts!r}")
        acts = tuple(AreaTiming(when) for when in acts)
        if len(acts) != len(set(acts)):
            raise ValueError(f"A time it acts is given twice: {list(acts)}")
        object.__setattr__(self, "acts", acts)
        if self.move_action is not None:
            if self.move_action not in {a.value for a in _MOVE_ACTIONS}:
                raise ValueError(
                    f"move_action is an Action or a Bonus Action, not"
                    f" {self.move_action!r}"
                )
            object.__setattr__(self, "move_action", ActionType(self.move_action))
        for name, kind in (("obscures", AreaSight), ("cover", AreaCover)):
            value = getattr(self, name)
            if value is not None:
                if value not in set(kind):
                    raise ValueError(f"{name} {value!r} is not one of {list(kind)}")
                object.__setattr__(self, name, kind(value))
        if self.shape is CombatAreaShape.WALL:
            if self.from_source:
                raise ValueError("A Wall doesn't start at its source")
        else:
            given = [
                name
                for name in _WALL_FIELDS
                if getattr(self, name) not in (None, False)
            ]
            if given:
                raise ValueError(f"Only a Wall has {', '.join(given)}")

    @property
    def is_wall(self) -> bool:
        return self.shape is CombatAreaShape.WALL

    @property
    def timing(self) -> frozenset[str]:
        """When it acts, as plain text ("enters", "starts"): `acts`, or
        DEFAULT_TIMING when it says none."""
        return frozenset(when.value for when in (self.acts or DEFAULT_TIMING))

    def to_dict(self) -> dict:
        """The area as plain data, leaving out what's at its default."""
        data: dict = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value == field.default:
                continue
            if isinstance(value, tuple):
                data[field.name] = [item.value for item in value]
            elif isinstance(value, StrEnum):
                data[field.name] = value.value
            else:
                data[field.name] = value
        return data

    @classmethod
    def from_dict(cls, data: Any, where: str = "an area") -> "CombatArea":
        """The area `data` describes (what to_dict writes). ValueError naming
        `where` when a key is unknown or a value is wrong."""
        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid area of {where}: expected an object, got {data!r}"
            )
        known = {field.name for field in fields(cls)}
        unknown = sorted(set(data) - known)
        if unknown:
            raise ValueError(
                f"Invalid area of {where}: unknown key(s) {unknown}, known:"
                f" {sorted(known)}"
            )
        values = dict(data)
        if "acts" in values:
            if not isinstance(values["acts"], (list, tuple)):
                raise ValueError(
                    f"Invalid area of {where}, acts: expected a list,"
                    f" got {values['acts']!r}"
                )
            values["acts"] = tuple(values["acts"])
        try:
            return cls(**values)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid area of {where}: {error}") from error
