"""Fight: the state of one fight, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.2). Who is in it, the turn order, whose turn it is, the round, where
the window is (between encounters, rolling Initiative or in the turns) and
the battle map's settings.

The combat window holds one (CombatAppQt.fight) and reads and writes it
through attributes of the same names (CombatWindowState's properties), so
code written against those attributes didn't change. The rules move here
from the window's mixins one area at a time (step 5.3), as functions of a
Fight; until then this is the state they share."""

from dataclasses import dataclass, field

from Combat.Arena.arena import ArenaSettings
from Combat.Definitions import Phase


@dataclass
class Fight:
    # Everyone in the window: the party, the encounter's combatants, allies
    # and summons, as combatant dicts (Combat/Fight/combatant.py).
    characters: list[dict] = field(default_factory=list)
    # The turn order once Initiative is rolled (the same dicts), and whose
    # turn it is in it.
    initiative_order: list[dict] = field(default_factory=list)
    current_turn_idx: int = 0
    round_number: int = 1
    phase: Phase = Phase.INITIATIVE
    arena_settings: ArenaSettings = field(default_factory=ArenaSettings)
