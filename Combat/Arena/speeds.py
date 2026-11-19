"""A creature's speeds on the battle map, with no Qt (Notes/combat-arena-plan.md,
step 26): which ones it has, which one it moves by, how high it flies, and
when it falls.

Rules Glossary, Speed: "If you have more than one speed, choose which one to
use when you move; you can switch between the speeds during your move.
Whenever you switch, subtract the distance already moved from the new speed.
The result determines how much farther you can move." Every special speed
changes as its Speed does (speed_in_use). Flying: "you fall if you have the
Incapacitated or Prone condition or your Fly Speed is reduced to 0. You can
stay aloft in those circumstances if you can hover." Falling: "1d6
Bludgeoning damage at the end of the fall for every 10 feet it fell, to a
maximum of 20d6", and Prone unless it takes none.

Where they come from: a stat block's Speed, Fly, Climb, Swim and Burrow
fields and its `hover` (its speed text is only shown); a player's Speed; and a
Movement on a badge, a feature or a trait (Fly's "a Fly Speed of 60 feet and
can hover": Movement(fly_ft=60, hovers=True)). The speed a creature moves by
is kept on it, `char["moving_by"] = "fly"` (none: its Speed), and how high
it flies above the ground under it, `char["altitude_ft"] = 30`, which counts
into every distance as the ground's height does.
"""

from __future__ import annotations

from Combat.Effects.modifiers import has_condition, modifiers_on, speed_in_use
from Core.Definitions import Condition
from Model.Content.CombatModifiers import Movement

MODE_KEY = "moving_by"
ALTITUDE_KEY = "altitude_ft"

# The speeds, in the order the map offers them.
WALK = "walk"
FLY = "fly"
SWIM = "swim"
CLIMB = "climb"
BURROW = "burrow"
MODES = (WALK, FLY, SWIM, CLIMB, BURROW)
# Each one's name in the rules ("Fly Speed") and the verb a move by it takes
# in the log ("Wyvern flies from ...").
SPEED_NAMES = {
    WALK: "Speed",
    FLY: "Fly Speed",
    SWIM: "Swim Speed",
    CLIMB: "Climb Speed",
    BURROW: "Burrow Speed",
}
VERBS = {WALK: "moves", FLY: "flies", SWIM: "swims", CLIMB: "climbs", BURROW: "burrows"}
# The bar's name for each.
LABELS = {WALK: "Walk", FLY: "Fly", SWIM: "Swim", CLIMB: "Climb", BURROW: "Burrow"}

# How high the bar lets a flyer go, in feet.
MAX_ALTITUDE_FT = 1000
# Falling: 1d6 for every 10 feet, to a maximum of 20d6.
FEET_PER_DIE = 10
MAX_FALLING_DICE = 20

# Stat-block traits that are rules for moving, by name: every monster's
# Incorporeal Movement reads "can move through other creatures and objects
# as if they were Difficult Terrain", every Swarm "can occupy another
# creature's space and vice versa".
TRAIT_MOVEMENT = {
    "Incorporeal Movement": Movement(through_creatures=True, through_objects=True),
    "Swarm": Movement(shares_space=True),
}


def _trait_names(char: dict) -> list[str]:
    return [
        str(t.get("name") if isinstance(t, dict) else getattr(t, "name", ""))
        for t in char.get("traits") or ()
    ]


def movements(char: dict) -> list[tuple[str, Movement]]:
    """Each Movement char has, with what gives it: its badges' (Freedom of
    Movement), its always-on features' (a player's Halfling Nimbleness) and
    its stat block's traits (TRAIT_MOVEMENT)."""
    found = [
        (str(source), modifier)
        for source, modifier in modifiers_on(char)
        if isinstance(modifier, Movement)
    ]
    sheet = char.get("_stat_block")
    for feature in char.get("_feature_objects") or ():
        given = feature.movement(sheet)
        if given is not None:
            found.append((feature.name, given))
    found += [
        (name, TRAIT_MOVEMENT[name])
        for name in _trait_names(char)
        if name in TRAIT_MOVEMENT
    ]
    return found


def _number(value) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def stored_speeds(char: dict) -> dict[str, int]:
    """Char's own speeds, before anything changes them: its Speed (a
    monster's speed_ground_ft, a player's speed), its stat block's Fly,
    Climb, Swim and Burrow Speeds, and those a Movement gives (the highest, where several do).
    """
    found: dict[str, int] = {}

    def give(mode: str, feet: int | None):
        if feet is not None and feet > found.get(mode, -1):
            found[mode] = feet

    walk = _number(char.get("speed_ground_ft"))
    if walk is None:
        walk = _number(char.get("speed"))
    give(WALK, walk)
    give(FLY, _number(char.get("speed_fly_ft")))
    give(CLIMB, _number(char.get("speed_climb_ft")))
    give(SWIM, _number(char.get("speed_swim_ft")))
    give(BURROW, _number(char.get("speed_burrow_ft")))
    for _, movement in movements(char):
        give(FLY, movement.fly_ft)
        give(SWIM, movement.swim_ft)
        if walk is not None:
            give(FLY, walk if movement.flies else None)
            give(SWIM, walk if movement.swims else None)
    return {mode: found[mode] for mode in MODES if mode in found}


def speeds(char: dict) -> dict[str, int]:
    """Char's speeds in use, in MODES order: each from its own with what
    changes its Speed (Haste doubles a Fly Speed too, Grappled makes every
    one 0)."""
    return {
        mode: speed_in_use(char, feet) for mode, feet in stored_speeds(char).items()
    }


def hovers(char: dict) -> bool:
    """Whether char can hover: its stat block's `hover`, or a Movement's
    (Fly)."""
    if char.get("hover"):
        return True
    return any(m.hovers for _, m in movements(char))


def mode_of(char: dict) -> str:
    """The speed char moves by: the one it was set to, while it still has
    it; else its Speed; else its first speed (a creature that only flies)."""
    have = stored_speeds(char)
    chosen = char.get(MODE_KEY)
    if chosen in have:
        return chosen
    if WALK in have or not have:
        return WALK
    return next(iter(have))


def speed_of_mode(char: dict) -> int | None:
    """The speed in use that char moves by now; None with no speed known."""
    return speeds(char).get(mode_of(char))


def altitude_ft(char: dict) -> int:
    """How high above the ground char is: the altitude it was flown to
    while it was set to fly (kept even once its Fly Speed is gone, until it
    falls: fall_reason), else 0."""
    if char.get(MODE_KEY) != FLY:
        return 0
    feet = char.get(ALTITUDE_KEY)
    return feet if isinstance(feet, int) and feet > 0 else 0


def fall_reason(char: dict) -> str | None:
    """Why char falls now, aloft and unable to hover (Rules Glossary,
    Flying): "Prone", "Incapacitated", "its Fly Speed is 0", or "it can't
    fly any more" (Fly ended: "the target falls if it is still aloft");
    None when it doesn't (on the ground, hovering, or flying as it may)."""
    if altitude_ft(char) <= 0:
        return None
    if FLY not in stored_speeds(char):
        return "it can't fly any more" if not hovers(char) else None
    if hovers(char):
        return None
    if has_condition(char, Condition.PRONE):
        return Condition.PRONE.value
    if has_condition(char, Condition.INCAPACITATED):
        return Condition.INCAPACITATED.value
    if not speeds(char).get(FLY):
        return "its Fly Speed is 0"
    return None


def falling_dice(feet: int) -> str:
    """The damage of a fall of `feet` feet: "3d6" for 30 to 39 feet, up to
    "20d6"; "" for less than 10 feet."""
    dice = min(MAX_FALLING_DICE, max(0, feet) // FEET_PER_DIE)
    return f"{dice}d6" if dice else ""


def speeds_text(char: dict) -> str:
    """ "Walk 30 ft., Fly 60 ft. (hover)": char's speeds in use, for the bar."""
    parts = [f"{LABELS[mode]} {feet} ft." for mode, feet in speeds(char).items()]
    text = ", ".join(parts)
    return text + (" (hover)" if FLY in speeds(char) and hovers(char) else "")
