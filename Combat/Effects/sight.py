"""Whether one creature sees another, as the battle map reads it
(Combat/Arena/senses.py, the arena plan's step 28), in the shape the rules
that ask take it: an attack roll's (modifiers.attack_plan: Invisible's
"If a creature can somehow see you", Heavily Obscured's Blinded) and a
trigger's ("you can see it"). Nothing here imports Qt or the map."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Seen:
    """Whether a viewer sees another creature: `can` True or False, or None
    when that isn't known (either off the map, or the map not in use: the
    GM's). `why` says what settled it ("Darkness at C4", "Ogre is
    Invisible", "Blindsight 10 ft."; "" when it's plainly seen).
    `obscured`: it can't because of the space the other is in (Heavily
    Obscured: Darkness, a fog), so the viewer has the Blinded condition
    while trying to see there (Rules Glossary, Heavily Obscured)."""

    can: bool | None = None
    why: str = ""
    obscured: bool = False


UNKNOWN = Seen()


@dataclass(frozen=True)
class Sight:
    """What an attack roll asks of sight: whether the attacker sees the
    target, and whether the target sees the attacker."""

    attacker: Seen = UNKNOWN
    target: Seen = UNKNOWN


NO_SIGHT = Sight()
