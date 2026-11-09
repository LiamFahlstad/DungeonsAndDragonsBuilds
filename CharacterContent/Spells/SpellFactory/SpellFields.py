"""The four lines at the top of a spell's card as dataclasses: CastingTime,
Range, Components and Duration.

Each one reads the sources' wordings with from_text() (2024 "Action" and
2014 "1 action", "Concentration up to 10 minutes" without its comma, "60ft",
"Component: V, S") and writes the 2024 card's wording back with `text`. A
ClassSpell's rules hold them. A JSON spell (DataSpell) parses its record's
text into them, so both kinds of spell get casting_time_type, range_feet,
duration_seconds and the rest from the same code. from_text() raises
ValueError on a wording it can't read.

    CastingTime(CastingTimeType.ACTION)                       # "Action"
    CastingTime(CastingTimeType.MINUTE, 10, ritual=True)      # "10 minutes or Ritual"
    CastingTime(CastingTimeType.REACTION, trigger="which you take in response to taking damage")
    Range(RangeType.FOOT, 150)                                # "150 feet"
    Range(RangeType.SELF, area=Area(15, AreaShape.CONE))      # "Self (15-foot cone)"
    Components(verbal=True, somatic=True, material="a pinch of salt")
    Duration(DurationType.MINUTE, 1, concentration=True)      # "Concentration, up to 1 minute"
    Duration(DurationType.INSTANTANEOUS)                      # "Instantaneous"
"""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from Core.Rules import SECONDS_PER_ROUND

from .Enums import AreaShape, CastingTimeType, DurationType, RangeType

FEET_PER_MILE = 5280


def _count(amount: int, word: str) -> str:
    """ "1 minute", "10 minutes", "1,000 feet"."""
    if word == "foot":
        word = "foot" if amount == 1 else "feet"
    elif amount != 1:
        word += "s"
    return f"{amount:,} {word}"


def _check_amount(owner: str, kind, measured: bool, amount: Optional[int]) -> None:
    if measured and (amount is None or amount < 1):
        raise ValueError(f"{owner} {kind} needs an amount of 1 or more")
    if not measured and amount is not None:
        raise ValueError(f"{owner} {kind} takes no amount")


def _number(text: str) -> int:
    return int(text.replace(",", ""))


# ---------------------------------------------------------------------------
# Casting time

_CASTING_MEASURED = {
    CastingTimeType.MINUTE: "minute",
    CastingTimeType.HOUR: "hour",
}
_CASTING_WORDS = {
    "action": CastingTimeType.ACTION,
    "bonus action": CastingTimeType.BONUS_ACTION,
    "reaction": CastingTimeType.REACTION,
    "minute": CastingTimeType.MINUTE,
    "hour": CastingTimeType.HOUR,
}
_CASTING_PART = re.compile(
    r"(?:(?P<amount>\d+) )?(?P<word>bonus action|action|reaction|minute|hour)s?"
    r"(?: \((?P<note>[^()]+)\))?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CastingTime:
    """ "Action", "10 minutes or Ritual", "Reaction, which you take when ...".

    `amount` goes with MINUTE and HOUR only. `trigger` is the clause after
    the comma, as the source words it ("which you take when you fall").
    `note` names an alternative ("Action (Overgrowth) or 8 hours
    (Enrichment)"), and `alternative` is the casting time after an "or".
    `ritual` is the trailing "or Ritual"."""

    kind: CastingTimeType
    amount: Optional[int] = None
    trigger: str = ""
    ritual: bool = False
    note: str = ""
    alternative: Optional[CastingTime] = None

    def __post_init__(self):
        _check_amount(
            "Casting time", self.kind, self.kind in _CASTING_MEASURED, self.amount
        )
        if self.trigger and self.alternative is not None:
            raise ValueError("A casting time with a trigger has no alternative")
        if self.trigger and self.ritual:
            raise ValueError("A casting time with a trigger isn't a ritual")
        if self.alternative is not None and self.alternative.ritual:
            raise ValueError("'or Ritual' goes on the first casting time")

    @property
    def text(self) -> str:
        word = _CASTING_MEASURED.get(self.kind)
        text = self.kind.value if word is None else _count(self.amount or 0, word)
        if self.note:
            text += f" ({self.note})"
        if self.trigger:
            text += f", {self.trigger}"
        if self.alternative is not None:
            text += f" or {self.alternative.text}"
        if self.ritual:
            text += " or Ritual"
        return text

    @classmethod
    def from_text(cls, text: str) -> CastingTime:
        return _casting_time(text)


@lru_cache(maxsize=None)
def _casting_time(text: str) -> CastingTime:
    head, _, trigger = text.strip().partition(", ")
    parts = re.split(r" or ", head.strip(), flags=re.IGNORECASE)
    ritual = len(parts) > 1 and parts[-1].strip().lower() == "ritual"
    if ritual:
        parts = parts[:-1]
    made: Optional[CastingTime] = None
    for part in reversed(parts):
        match = _CASTING_PART.fullmatch(part.strip())
        if match is None:
            raise ValueError(f"Can't read the casting time {text!r}")
        kind = _CASTING_WORDS[match["word"].lower()]
        amount = int(match["amount"]) if match["amount"] else None
        if kind not in _CASTING_MEASURED:
            if amount not in (None, 1):  # "1 action" is an Action
                raise ValueError(f"Can't read the casting time {text!r}")
            amount = None
        made = CastingTime(kind, amount, note=match["note"] or "", alternative=made)
    assert made is not None
    return dataclasses.replace(made, trigger=trigger.strip(), ritual=ritual)


# ---------------------------------------------------------------------------
# Range

_RANGE_WORDS = {
    kind.value.lower(): kind
    for kind in RangeType
    if kind not in (RangeType.FOOT, RangeType.MILE)
}
_RANGE = re.compile(
    r"(?:(?P<word>self|touch|sight|unlimited|special)"
    r"|(?P<amount>[\d,]+) ?(?P<unit>feet|foot|ft|miles?)\.?)"
    r"(?: \((?P<area>[^()]+)\))?",
    re.IGNORECASE,
)
_AREA = re.compile(
    r"(?P<size>[\d,]+)-(?P<unit>foot|mile)(?P<radius>-radius)?"
    r"(?: (?P<shape>cone|cube|line|radius|sphere|hemisphere))?",
    re.IGNORECASE,
)
# Shapes the card sizes by their radius: "10-foot-radius sphere".
_BY_RADIUS = (AreaShape.SPHERE, AreaShape.HEMISPHERE)


@dataclass(frozen=True)
class Area:
    """The area in a 2014 range: "Self (15-foot cone)", "Self (10-foot-radius
    sphere)". `size` is in feet, or in miles when `miles`."""

    size: int
    shape: AreaShape
    miles: bool = False

    def __post_init__(self):
        if self.size < 1:
            raise ValueError(f"An area of size {self.size}")

    @property
    def text(self) -> str:
        unit = "mile" if self.miles else "foot"
        shape = self.shape.value.lower()
        if self.shape in _BY_RADIUS:
            return f"{self.size:,}-{unit}-radius {shape}"
        return f"{self.size:,}-{unit} {shape}"


@dataclass(frozen=True)
class Range:
    """ "150 feet", "1 mile", "Touch", "Self (30-foot radius)". `amount` goes
    with FOOT and MILE only, `area` with SELF only."""

    kind: RangeType
    amount: Optional[int] = None
    area: Optional[Area] = None

    def __post_init__(self):
        _check_amount(
            "Range",
            self.kind,
            self.kind in (RangeType.FOOT, RangeType.MILE),
            self.amount,
        )
        if self.area is not None and self.kind is not RangeType.SELF:
            raise ValueError("Only a range of Self has an area")

    @property
    def feet(self) -> Optional[int]:
        """The distance in feet, or None for a range that isn't one (Self,
        Touch, Sight, Unlimited, Special)."""
        if self.kind is RangeType.FOOT:
            return self.amount
        if self.kind is RangeType.MILE:
            return (self.amount or 0) * FEET_PER_MILE
        return None

    @property
    def text(self) -> str:
        if self.kind is RangeType.FOOT:
            text = _count(self.amount or 0, "foot")
        elif self.kind is RangeType.MILE:
            text = _count(self.amount or 0, "mile")
        else:
            text = self.kind.value
        if self.area is not None:
            text += f" ({self.area.text})"
        return text

    @classmethod
    def from_text(cls, text: str) -> Range:
        return _range(text)


@lru_cache(maxsize=None)
def _range(text: str) -> Range:
    match = _RANGE.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"Can't read the range {text!r}")
    area = None
    if match["area"]:
        found = _AREA.fullmatch(match["area"])
        shape = found and (found["shape"] or ("radius" if found["radius"] else None))
        if not found or not shape:
            raise ValueError(f"Can't read the area in the range {text!r}")
        area = Area(
            _number(found["size"]),
            AreaShape(shape.capitalize()),
            miles=found["unit"].lower() == "mile",
        )
    if match["word"]:
        return Range(_RANGE_WORDS[match["word"].lower()], area=area)
    kind = (
        RangeType.MILE if match["unit"].lower().startswith("mile") else RangeType.FOOT
    )
    return Range(kind, _number(match["amount"]), area=area)


# ---------------------------------------------------------------------------
# Components

_COMPONENT_PREFIX = re.compile(r"^components?:\s*", re.IGNORECASE)


@dataclass(frozen=True)
class Components:
    """ "V, S, M (a pinch of salt)". `material` is what the M is: None for no
    M, "" for an M the source says nothing about."""

    verbal: bool = False
    somatic: bool = False
    material: Optional[str] = None

    @property
    def has_material(self) -> bool:
        return self.material is not None

    @property
    def text(self) -> str:
        parts = [
            letter
            for letter, there in (("V", self.verbal), ("S", self.somatic))
            if there
        ]
        if self.material:
            parts.append(f"M ({self.material})")
        elif self.material is not None:
            parts.append("M")
        return ", ".join(parts)

    @classmethod
    def from_text(cls, text: str) -> Components:
        return _components(text)


@lru_cache(maxsize=None)
def _components(text: str) -> Components:
    """Reads "V, S, M (...)", and the scraped slips "V,S", "M(...)" and a
    stray "Component: " in front. The letters come once each, in card order."""
    rest = _COMPONENT_PREFIX.sub("", text.strip())
    head, paren, inside = rest.partition("(")
    letters = [part.strip() for part in head.split(",") if part.strip()]
    in_order = set(letters) <= set("VSM") and letters == sorted(
        set(letters), key="VSM".index
    )
    if not in_order:
        raise ValueError(f"Can't read the components {text!r}")
    material = None
    if "M" in letters:
        material = ""
        if paren:
            if not inside.endswith(")") or letters[-1] != "M":
                raise ValueError(f"Can't read the components {text!r}")
            material = inside[:-1].strip()
    elif paren:
        raise ValueError(f"A material without an M in {text!r}")
    return Components("V" in letters, "S" in letters, material)


# ---------------------------------------------------------------------------
# Duration

_DURATION_SECONDS = {
    DurationType.ROUND: SECONDS_PER_ROUND,
    DurationType.MINUTE: 60,
    DurationType.HOUR: 3600,
    DurationType.DAY: 86400,
}
_DURATION_WORDS = {
    "instantaneous": DurationType.INSTANTANEOUS,
    "instantanous": DurationType.INSTANTANEOUS,  # a 2014 record's typo
    "until dispelled or triggered": DurationType.UNTIL_DISPELLED_OR_TRIGGERED,
    "until dispelled": DurationType.UNTIL_DISPELLED,
    "special": DurationType.SPECIAL,
}
_DURATION_PART = re.compile(
    r"(?P<concentration>concentration,? )?(?P<up_to>up to )?"
    r"(?:(?P<amount>\d+) (?P<unit>round|minute|hour|day)s?"
    r"|(?P<word>" + "|".join(_DURATION_WORDS) + r"))"
    r"(?: \((?P<note>[^()]+)\))?",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Duration:
    """ "Instantaneous", "1 hour", "Concentration, up to 1 minute", "Up to 8
    hours", "Until dispelled". `amount` goes with ROUND to DAY only.
    `concentration` says "Concentration, up to"; `up_to` is the "Up to" of a
    duration without Concentration. `note` is a trailing "(see below)", and
    `alternative` the duration after an "or"."""

    kind: DurationType
    amount: Optional[int] = None
    concentration: bool = False
    up_to: bool = False
    note: str = ""
    alternative: Optional[Duration] = None

    def __post_init__(self):
        measured = self.kind in _DURATION_SECONDS
        _check_amount("Duration", self.kind, measured, self.amount)
        if (self.concentration or self.up_to) and not measured:
            raise ValueError(f"Duration {self.kind} can't be 'up to'")
        if self.concentration and self.up_to:
            raise ValueError("Concentration already says 'up to'")

    @property
    def seconds(self) -> Optional[int]:
        """How long it lasts (Instantaneous is 0), or None when it isn't a
        fixed length (Until dispelled, Special). An alternative is ignored."""
        if self.kind is DurationType.INSTANTANEOUS:
            return 0
        per_unit = _DURATION_SECONDS.get(self.kind)
        return None if per_unit is None else (self.amount or 0) * per_unit

    @property
    def text(self) -> str:
        if self.kind in _DURATION_SECONDS:
            text = _count(self.amount or 0, self.kind.value.lower())
        else:
            text = self.kind.value
        if self.concentration:
            text = f"Concentration, up to {text}"
        elif self.up_to:
            text = f"Up to {text}"
        if self.note:
            text += f" ({self.note})"
        if self.alternative is not None:
            # "... or until dispelled": a word goes on in lower case.
            alternative = self.alternative.text
            text += f" or {alternative[:1].lower()}{alternative[1:]}"
        return text

    @classmethod
    def from_text(cls, text: str) -> Duration:
        return _duration(text)


@lru_cache(maxsize=None)
def _duration(text: str) -> Duration:
    text = text.strip()
    parts = []
    position = 0
    while True:
        match = _DURATION_PART.match(text, position)
        if match is None:
            raise ValueError(f"Can't read the duration {text!r}")
        parts.append(match)
        position = match.end()
        if position == len(text):
            break
        if text[position : position + 4].lower() != " or ":
            raise ValueError(f"Can't read the duration {text!r}")
        position += 4
    made: Optional[Duration] = None
    for match in reversed(parts):
        if match["word"]:
            kind = _DURATION_WORDS[match["word"].lower()]
            amount = None
        else:
            kind = DurationType(match["unit"].capitalize())
            amount = int(match["amount"])
        made = Duration(
            kind,
            amount,
            concentration=bool(match["concentration"]),
            up_to=bool(match["up_to"]) and not match["concentration"],
            note=match["note"] or "",
            alternative=made,
        )
    assert made is not None
    return made
