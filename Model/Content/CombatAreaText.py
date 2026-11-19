"""Drafts a CombatArea (Model/Content/CombatArea.py) from rules text: "Each
creature in a 20-foot-radius Sphere centered on that point", Moonbeam's "take
a Magic action on later turns to move the Cylinder up to 60 feet", Wall of
Force's "Nothing can physically pass through the wall".

For writing content, not for a fight (Notes/explicit-attributes-plan.md,
Phase 3): CharacterContent/Spells/SpellClassConverter.py drafts a new
spell's SpellRules.area with it, for a person to check, and a spell's class
keeps the area as fields from then on. The battle map reads only the
fields. The one exception, until the plan's Phase 4 gives stat blocks
fields of their own, is a monster ability without combat effects
(effect_options.py reads its description with read_combat_area).
"""

import re
from dataclasses import replace

from Model.Content.ActionType import ActionType
from Model.Content.CombatArea import (
    AreaCover,
    AreaSight,
    AreaTiming,
    CombatArea,
    CombatAreaShape,
)

_SHAPES = "|".join(s.value for s in CombatAreaShape)
_NUMBER = r"(\d[\d,]*)"
_FOOT = r"[- ](?:foot|feet|ft\.?)"
# "20-foot-radius Sphere", "10-foot-radius, 40-foot-high Cylinder",
# "Self (10-foot-radius sphere)", "20-foot radius sphere".
_RADIUS = re.compile(
    rf"{_NUMBER}{_FOOT}[- ]radius,?(?:\s+{_NUMBER}{_FOOT}[- ]high,?)?\s+"
    r"(sphere|cylinder|emanation)?",
    re.IGNORECASE,
)
# "100-foot-long, 5-foot-wide Line", "Line 100 feet long and 5 feet wide".
_LONG_LINE = re.compile(
    rf"{_NUMBER}{_FOOT}[- ]long,?\s+{_NUMBER}{_FOOT}[- ]wide\s+line",
    re.IGNORECASE,
)
# "5-foot-wide, 60-foot-long Line" (Sunbeam).
_WIDE_LINE = re.compile(
    rf"{_NUMBER}{_FOOT}[- ]wide,?\s+{_NUMBER}{_FOOT}[- ]long\s+line",
    re.IGNORECASE,
)
# A 2014 range of "Self (10-foot radius)": a Sphere around the source.
_SELF_RADIUS = re.compile(
    rf"self\s*\(\s*{_NUMBER}{_FOOT}[- ]radius(?:\s+sphere)?\s*\)", re.IGNORECASE
)
# How far away the point an area is centred on may be: "a point you can see
# within 60 feet of you", "centered on a point within 120 feet".
_POINT_WITHIN = re.compile(
    rf"\bpoint\b[^.]{{0,30}}?within {_NUMBER}{_FOOT}", re.IGNORECASE
)
_LINE_LONG = re.compile(
    rf"\bline\b(?:\s+of\s+[a-z ]{{1,30}}?)?\s+{_NUMBER}\s+(?:foot|feet)\s+long"
    rf"(?:\s+and\s+{_NUMBER}\s+"
    r"(?:foot|feet)\s+wide)?",
    re.IGNORECASE,
)
# "15-foot Cone", "30-foot Emanation", "15-foot cube", "60-foot line", and
# "20-foot square" (Entangle, Grease): a Cube on the ground.
_SIZED = re.compile(rf"{_NUMBER}{_FOOT}\s+({_SHAPES}|square)\b", re.IGNORECASE)
# "Each creature within 5 feet of that point" (Call Lightning): a Sphere.
_WITHIN_POINT = re.compile(
    rf"(?:each|every|all)(?: other)? creatures?[^.]{{0,40}}?within {_NUMBER}"
    rf"{_FOOT} of (?:that|the|a) point\b",
    re.IGNORECASE,
)
# "each creature within 5 feet of you", "All other creatures within 5 feet of
# you" (Sword Burst), "within 10 feet of it": an Emanation.
_WITHIN = re.compile(
    rf"(?:each|every|all)(?: other)? creatures?[^.]{{0,40}}?within {_NUMBER}"
    rf"{_FOOT} of (?!(?:that|the|a) point\b)"
    r"(?:you|it|itself|the \w+|him|her|them)\b",
    re.IGNORECASE,
)
# What says the area is the source's own: "Self (15-foot cube)", "centered on
# you", "originating from you".
_AROUND_SOURCE = re.compile(
    r"\bself\s*\(|centered on (?:you|yourself|itself|himself|herself)\b"
    r"|originat\w* from (?:you|yourself|itself)\b",
    re.IGNORECASE,
)
# A light's reach isn't an area: Flaming Sphere "sheds Bright Light in a
# 20-foot radius" (DI-096).
_LIGHT_BEFORE = re.compile(r"\blight\s+(?:in|for)\s+(?:a|an)?\s*$", re.IGNORECASE)
# Flaming Sphere's "Any creature that ends its turn within 5 feet of the
# sphere": a Sphere that far around the cell it's on (DI-096).
_WITHIN_SPHERE = re.compile(
    rf"\bwithin {_NUMBER}{_FOOT} of (?:the|that) sphere\b", re.IGNORECASE
)
# A wall (arena step 25): "make the wall up to 60 feet long, 20 feet high,
# and 1 foot thick" (Wall of Fire, Wall of Thorns), "a straight wall up to
# 100 feet long" (Blade Barrier).
_WALL_LONG = re.compile(
    rf"\bwall\b[^.]{{0,40}}?\bup to {_NUMBER}{_FOOT} long", re.IGNORECASE
)
_THICK = re.compile(rf"{_NUMBER}{_FOOT}\s+thick", re.IGNORECASE)
# Wall of Force's "a flat surface made up of ten 10-foot-by-10-foot panels".
_COUNTS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
_PANELS = re.compile(
    rf"\b({'|'.join(_COUNTS)}|\d+) {_NUMBER}-foot(?:-by-\d+-foot|-square) panels\b",
    re.IGNORECASE,
)
# A wall's ring, as its text gives the choice: "a ringed wall up to 20 feet
# in diameter", "a circle that has a 20-foot diameter", "a globe with a
# radius of up to 10 feet" (twice that across).
_RING_ACROSS = re.compile(
    rf"\bring(?:ed)? wall up to {_NUMBER}{_FOOT} in diameter"
    rf"|\bcircle that has an? {_NUMBER}{_FOOT} diameter",
    re.IGNORECASE,
)
_RING_RADIUS = re.compile(
    rf"\b(?:dome|globe)\b[^.]{{0,30}}?\bradius of up to {_NUMBER}{_FOOT}",
    re.IGNORECASE,
)
# Wall of Fire's "One side of the wall ... deals 5d8 Fire damage to each
# creature that ends its turn within 10 feet of that side".
_SIDE_WITHIN = re.compile(
    rf"\bone side of the wall\b[^.]*?\bwithin {_NUMBER}{_FOOT} of that side",
    re.IGNORECASE,
)
# A wall its text calls a barrier, or says nothing passes through (Wall of
# Force); the cover a wall "provides", and a space that "is Difficult
# Terrain" (Blade Barrier).
_BARRIER = re.compile(
    r"\bbarrier\b|\bnothing can (?:physically )?pass through\b", re.IGNORECASE
)
_PROVIDES_COVER = re.compile(
    r"\bprovides (Half|Three-Quarters|Total) Cover\b", re.IGNORECASE
)
_COVERS = {
    "half": AreaCover.HALF,
    "three-quarters": AreaCover.THREE_QUARTERS,
    "total": AreaCover.TOTAL,
}
_SPACE_DIFFICULT = re.compile(r"\bspace is Difficult Terrain\b", re.IGNORECASE)
# What the area is called in a spell's text, after "enters the ...".
_AREA_WORDS = (
    r"(?:spell's |spell’s )?(?:area|cylinder|emanation|sphere|cube|cloud|fog|"
    r"wall|square|line|ring|aura|vortex|mist|smoke|storm|zone|webs?)"
)
_ENTERS = re.compile(
    rf"\benters? (?:the |that |its |this )?{_AREA_WORDS}|\benters? it for the first"
    r" time|\bfirst time on a turn\b",
    re.IGNORECASE,
)
# Moonbeam's "when the spell's area moves into its space", Spirit Guardians'
# "whenever the Emanation enters a creature's space", Flaming Sphere's "If
# you move the sphere into a creature's space".
_MOVED_ONTO = re.compile(
    rf"\b{_AREA_WORDS} (?:moves |enters )(?:in)?(?:to )?(?:a creature's |a creature’s"
    r" |its |their )space|\bmove (?:the|it) \w* ?into a creature's space"
    r"|\bmove (?:the|it) \w* ?into a creature’s space",
    re.IGNORECASE,
)
_STARTS = re.compile(r"\bstarts? (?:its|their) turns?\b", re.IGNORECASE)
_ENDS = re.compile(r"\bends? (?:its|their) turns?\b", re.IGNORECASE)
# How an area is moved, in its text: Moonbeam's "take a Magic action on
# later turns to move the Cylinder up to 60 feet", Flaming Sphere's "As a
# Bonus Action, you can move the sphere up to 30 feet".
_MOVE_SENTENCE = re.compile(r"[^.]*\bmove (?:the|it)\b[^.]*", re.IGNORECASE)
_MOVE_FEET = re.compile(r"\bup to (\d+) (?:feet|foot|ft\.?)", re.IGNORECASE)
_BONUS_ACTION = re.compile(r"\bBonus Action\b", re.IGNORECASE)
_AN_ACTION = re.compile(r"\baction\b", re.IGNORECASE)
# What an area makes its space to sight: the Darkness spell's "Darkvision
# can't see through it", "magical Darkness" otherwise (Hunger of Hadar's
# "Sphere of Darkness"), "Heavily Obscured" (Fog Cloud, Stinking Cloud).
_DARKVISION_CANT = re.compile(r"\bdarkvision can['’]t see through\b", re.IGNORECASE)
_DARKNESS = re.compile(r"\bmagical darkness\b|\bsphere of darkness\b", re.IGNORECASE)
_HEAVILY_OBSCURED = re.compile(r"\bHeavily Obscured\b", re.IGNORECASE)


def _feet(text: str | None) -> int:
    return int((text or "0").replace(",", ""))


def _walls(text: str) -> list[tuple[int, CombatArea]]:
    """The walls `text` states, by where each is said: a straight one, as
    long and (when it says) as thick as its text, or Wall of Force's
    panels side by side."""
    found = []
    for match in _WALL_LONG.finditer(text):
        sentence_end = text.find(".", match.end())
        rest = text[match.end() : sentence_end if sentence_end >= 0 else None]
        thick = _THICK.search(rest)
        width = max(1, _feet(thick.group(1))) if thick else 5
        found.append(
            (
                match.start(),
                CombatArea(CombatAreaShape.WALL, _feet(match.group(1)), width),
            )
        )
    for match in _PANELS.finditer(text):
        count = match.group(1).lower()
        panels = _COUNTS.get(count) or int(count)
        found.append(
            (
                match.start(),
                CombatArea(CombatAreaShape.WALL, panels * _feet(match.group(2)), 1),
            )
        )
    return found


def wall_ring_ft(text: str) -> int | None:
    """How far across a wall's ring may be, as its text offers one (Wall of
    Fire's "ringed wall up to 20 feet in diameter", Wall of Force's globe
    "with a radius of up to 10 feet"); None when it offers none."""
    match = _RING_ACROSS.search(text)
    if match:
        return _feet(match.group(1) or match.group(2))
    match = _RING_RADIUS.search(text)
    return 2 * _feet(match.group(1)) if match else None


def damaging_side_ft(text: str) -> int | None:
    """How far from a wall's damaging side it reaches (Wall of Fire's 10
    feet "of that side"), or None for a wall without one."""
    match = _SIDE_WITHIN.search(text)
    return _feet(match.group(1)) if match else None


def point_range_ft(text: str) -> int | None:
    """How far away a rules text lets the point an area is centred on be
    ("a 20-foot-radius Sphere centered on a point within 120 feet"), or
    None when it doesn't say."""
    match = _POINT_WITHIN.search(text)
    return _feet(match.group(1)) if match else None


def parse_area(text: str) -> CombatArea | None:
    """The first area of effect `text` states ("Each creature in a
    20-foot-radius Sphere centered on that point"), its shape and size
    only, or None when it states none."""
    found: list[tuple[int, CombatArea]] = _walls(text)
    for match in _WITHIN_SPHERE.finditer(text):
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), CombatArea(CombatAreaShape.SPHERE, size)))
    for match in _RADIUS.finditer(text):
        if _LIGHT_BEFORE.search(text[max(0, match.start() - 20) : match.start()]):
            continue
        shape = CombatAreaShape((match.group(3) or "sphere").title())
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), CombatArea(shape, size)))
    for match in _LONG_LINE.finditer(text):
        found.append(
            (
                match.start(),
                CombatArea(
                    CombatAreaShape.LINE, _feet(match.group(1)), _feet(match.group(2))
                ),
            )
        )
    for match in _WIDE_LINE.finditer(text):
        found.append(
            (
                match.start(),
                CombatArea(
                    CombatAreaShape.LINE, _feet(match.group(2)), _feet(match.group(1))
                ),
            )
        )
    for match in _SELF_RADIUS.finditer(text):
        found.append(
            (
                match.start(),
                CombatArea(
                    CombatAreaShape.SPHERE, _feet(match.group(1)), from_source=True
                ),
            )
        )
    for match in _LINE_LONG.finditer(text):
        width = _feet(match.group(2)) or 5
        found.append(
            (
                match.start(),
                CombatArea(CombatAreaShape.LINE, _feet(match.group(1)), width),
            )
        )
    for match in _SIZED.finditer(text):
        size = _feet(match.group(1))
        if size:
            name = match.group(2).title()
            shape = CombatAreaShape.CUBE if name == "Square" else CombatAreaShape(name)
            found.append((match.start(), CombatArea(shape, size)))
    for match in _WITHIN_POINT.finditer(text):
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), CombatArea(CombatAreaShape.SPHERE, size)))
    for match in _WITHIN.finditer(text):
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), CombatArea(CombatAreaShape.EMANATION, size)))
    if not found:
        return None
    start, area = min(found, key=lambda item: item[0])
    if area.shape in (
        CombatAreaShape.SPHERE,
        CombatAreaShape.CYLINDER,
        CombatAreaShape.CUBE,
    ):
        # "Self (15-foot cube)", or the area's own sentence says so.
        end = text.find(".", start)
        sentence = text[text.rfind(".", 0, start) + 1 : end if end >= 0 else None]
        before = text[max(0, start - 8) : start]
        if _AROUND_SOURCE.search(sentence) or _AROUND_SOURCE.search(before):
            area = replace(area, from_source=True)
    return area


def read_timing(text: str) -> tuple[AreaTiming, ...]:
    """When an area with rules text `text` acts on a creature, as the text
    says it (Moonbeam's "when the spell's area moves into its space and
    when it enters the spell's area or ends its turn there"); () when it
    says none. An area that acts on who enters it acts on who it's moved
    onto too, as a table can't tell the two apart."""
    found = set()
    if _ENTERS.search(text):
        found |= {AreaTiming.ENTERS, AreaTiming.MOVED_ONTO}
    if _MOVED_ONTO.search(text):
        found.add(AreaTiming.MOVED_ONTO)
    if _STARTS.search(text):
        found.add(AreaTiming.STARTS)
    if _ENDS.search(text):
        found.add(AreaTiming.ENDS)
    return tuple(when for when in AreaTiming if when in found)


def read_move(text: str) -> tuple[int | None, ActionType | None]:
    """How far and at what cost an area moves, read from the first sentence
    of `text` that moves it: (its "up to N feet", a Bonus Action (Flaming
    Sphere) or an Action ("a Magic action", Moonbeam)); None for what it
    doesn't say."""
    sentence = _MOVE_SENTENCE.search(text)
    if sentence is None:
        return None, None
    words = sentence.group(0)
    feet = _MOVE_FEET.search(words)
    action = None
    if _BONUS_ACTION.search(words):
        action = ActionType.BONUS_ACTION
    elif _AN_ACTION.search(words):
        action = ActionType.ACTION
    return (int(feet.group(1)) if feet else None), action


def read_wall_terrain(text: str) -> tuple[bool, AreaCover | None, bool]:
    """What a wall is as terrain, from its rules text: (blocks, cover,
    difficult). One it calls a barrier (Wall of Force) blocks movement and
    is Total Cover, as a painted wall is; one that "provides Three-Quarters
    Cover" and whose "space is Difficult Terrain" (Blade Barrier) is that."""
    if _BARRIER.search(text):
        return True, AreaCover.TOTAL, False
    cover = _PROVIDES_COVER.search(text)
    degree = _COVERS[cover.group(1).lower()] if cover else None
    return False, degree, bool(_SPACE_DIFFICULT.search(text))


def read_obscures(text: str) -> AreaSight | None:
    """What an area's rules text makes its space to sight: magical Darkness
    Darkvision can't see through (the Darkness spell), Darkness ("magical
    Darkness" otherwise), Heavily Obscured (Fog Cloud), or None."""
    if _DARKVISION_CANT.search(text):
        return AreaSight.DEEP_DARKNESS
    if _DARKNESS.search(text):
        return AreaSight.DARKNESS
    if _HEAVILY_OBSCURED.search(text):
        return AreaSight.HEAVILY_OBSCURED
    return None


def read_combat_area(description: str, range_text: str = "") -> CombatArea | None:
    """The CombatArea a rules text states, for a person to check: its area
    (from the range too, for a spell: "Self (15-foot cone)" is the area),
    how far away its point may be, when it acts, how it's moved, what it
    hides, and a wall's ring, damaging side and terrain. None when it
    states no area."""
    text = f"Range: {range_text}. {description}" if range_text else description
    area = parse_area(text)
    if area is None:
        return None
    feet, action = read_move(description)
    area = replace(
        area,
        point_within_ft=point_range_ft(description),
        acts=read_timing(description),
        move_ft=feet,
        move_action=action,
        obscures=read_obscures(description),
    )
    if not area.is_wall:
        return area
    blocks, cover, difficult = read_wall_terrain(description)
    return replace(
        area,
        ring_ft=wall_ring_ft(description),
        side_ft=damaging_side_ft(description),
        blocks=blocks,
        cover=cover,
        difficult=difficult,
    )
