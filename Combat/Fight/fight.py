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

from Combat.Arena.arena import ArenaSettings, distance_ft
from Combat.Arena.cover import (
    NO_COVER_READING,
    CoverReading,
    cover_between,
    cover_from,
    with_cover,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import with_kept_walls
from Combat.Arena.ranges import (
    NO_RANGE_CHECK,
    AttackRange,
    RangeCheck,
    check_attack_range,
)
from Combat.Arena.senses import sees
from Combat.Definitions import Phase
from Combat.Effects.modifiers import makes_critical_hit
from Combat.Effects.sight import UNKNOWN, Seen


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

    # ---- The battle map, as the rules read it ----
    # Distances, sight, cover and range count only once the map is in use (a
    # token moved, or a painted map's starts: arena plan Decision 29); before
    # that each answers "not known", and what asks stays the GM's.

    def map_settings(self) -> ArenaSettings:
        """The map as the rules read it (arena step 25): the painted terrain
        with each kept wall's laid over it while it lasts (with_kept_walls).
        A copy for reading, or `arena_settings` itself with no such wall up,
        so a wall is never saved into the painted map."""
        return with_kept_walls(self.arena_settings, self.characters)

    def distance_ft(self, attacker: dict | None, target: dict | None) -> int | None:
        """How far attacker is from target, for the rules that ask (Prone's
        and Paralyzed's "within 5 feet"). None without either, with either
        off the map, or before the map is in use."""
        if attacker is None or target is None or attacker is target:
            return None
        if not self.arena_settings.in_use:
            return None
        return distance_ft(attacker, target, self.arena_settings)

    def sees(self, viewer: dict | None, other: dict | None) -> Seen:
        """Whether viewer sees other, and why (Combat/Arena/senses.py):
        Darkness, a kept Fog Cloud, Invisible, Blinded, Darkvision,
        Blindsight, Truesight. UNKNOWN without either or before the map is
        in use."""
        if viewer is None or other is None or not self.arena_settings.in_use:
            return UNKNOWN
        return sees(viewer, other, self.characters, self.map_settings())

    def map_cover(
        self,
        source: dict | None,
        target: dict | None,
        origin: list[Cell] | None = None,
    ) -> CoverReading:
        """The cover target has against source, or against an area's point
        of origin `origin` (a Fireball's cell): what's between them
        (Combat/Arena/cover.py)."""
        if target is None or not self.arena_settings.in_use:
            return NO_COVER_READING
        if origin is not None:
            leave = [source] if source is not None else []
            return cover_between(
                origin, target, self.characters, self.map_settings(), leave
            )
        if source is None:
            return NO_COVER_READING
        return cover_from(source, target, self.characters, self.map_settings())

    def covered(
        self,
        source: dict | None,
        target: dict,
        origin: list[Cell] | None = None,
        ignores_cover: bool = False,
    ) -> dict:
        """Target as a roll against it from source reads it: the map's cover
        among its own (with_cover: a copy to read, never to change).
        `ignores_cover`: what's rolled takes Half and Three-Quarters Cover
        away (Sacred Flame), so only Total Cover is left of the map's."""
        reading = self.map_cover(source, target, origin)
        if ignores_cover and not reading.total:
            return target
        return with_cover(target, reading)

    def range_check(
        self, source: dict | None, target: dict | None, attack: AttackRange | None
    ) -> RangeCheck:
        """What the map says of `attack`'s reach or range from source to
        target (Combat/Arena/ranges.py): Long range's Disadvantage, an enemy
        within 5 feet of a ranged attacker, past its reach or range."""
        if not self.arena_settings.in_use:
            return NO_RANGE_CHECK
        return check_attack_range(
            attack, source, target, self.characters, self.map_settings()
        )

    def cover_warning(self, source: dict | None, target: dict) -> str:
        """ "Goblin is behind Total Cover (Wall at D5): it can't be targeted
        directly", for a roll made anyway (warned about, not refused: arena
        plan Decision 19); "" otherwise."""
        reading = self.map_cover(source, target)
        if not reading.total:
            return ""
        return (
            f"{target['name']} is behind Total Cover ({reading.by}): it can't"
            " be targeted directly"
        )

    def critical_against(self, attacker: dict | None, target: dict | None) -> bool:
        """Whether a hit by attacker on target is a Critical Hit by what
        target has, whatever the d20 showed: Paralyzed's or Unconscious's,
        with attacker within 5 feet on the map."""
        if target is None:
            return False
        return makes_critical_hit(target, self.distance_ft(attacker, target))
