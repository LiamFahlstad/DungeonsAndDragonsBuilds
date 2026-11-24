"""Falling, Qt-free (Notes/combat-ui-refactor-plan.md, R34): whoever is
aloft on the battle map and can't stay so falls to the ground (Rules
Glossary, Falling). The window lands them each time it brings its views up
to date (ArenaMixin._land_fallers), and so does leaving a Wild Shape form,
at the point in its cascade where the window used to."""

from Combat.Arena.speeds import (
    ALTITUDE_KEY,
    MODE_KEY,
    altitude_ft,
    fall_reason,
    falling_dice,
)
from Combat.Definitions import Phase

from .fight import Fight
from .logger import Logger


def land_fallers(fight: Fight, logger: Logger) -> list[str]:
    """Whoever is aloft and can't stay so (speeds.fall_reason: Prone,
    Incapacitated, its Fly Speed 0 or gone, and it can't hover) falls to
    the ground: its altitude goes and it moves by its Speed, with a GM-only
    line saying how far it fell and what that deals. Returns those lines,
    for the status line. Only in a fight."""
    if fight.phase != Phase.COMBAT:
        return []
    lines = []
    for char in fight.characters:
        why = fall_reason(char)
        if why is None:
            continue
        feet = altitude_ft(char)
        char.pop(ALTITUDE_KEY, None)
        char.pop(MODE_KEY, None)
        dice = falling_dice(feet)
        hurt = (
            f" {dice} Bludgeoning damage, and it lands Prone unless it takes"
            " none (Falling)."
            if dice
            else " No damage: less than 10 ft. (Falling)."
        )
        line = f"{char['name']} falls {feet} ft. ({why}):" + hurt
        logger.log(line, character=char["name"], public=False)
        lines.append(line)
    return lines
