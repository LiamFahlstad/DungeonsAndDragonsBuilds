"""Fight: the state of one fight, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.2). Who is in it, the turn order, whose turn it is, the round, where
the window is (between encounters, rolling Initiative or in the turns) and
the battle map's settings.

The combat window holds one (CombatAppQt.fight) and reads and writes it
through attributes of the same names (CombatWindowState's properties), so
code written against those attributes didn't change. The rules move here
from the window's mixins one area at a time (step 5.3), as functions of a
Fight; until then this is the state they share."""

from dataclasses import dataclass, field, replace

from Combat.Arena.arena import DASHES_KEY, MOVED_KEY, ArenaSettings, distance_ft
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
from Combat.Summons import place_after_owners

from .auras import aura_modifiers, pack_tactics, with_auras
from .health import DEAD, death_state

# Each combatant's initiative roll this fight, once it's started. Not
# logged ("_"): a fight continued from its log has only the turn order.
INITIATIVE_KEY = "_initiative"


def initiative_units(chars: list[dict]) -> list[list[dict]]:
    """`chars` as the turns they take: each initiative group (the
    "initiative_group" its members share, at its first member's place) as
    one, and everyone else on their own."""
    units: list[list[dict]] = []
    groups: dict[str, list[dict]] = {}
    for char in chars:
        group = char.get("initiative_group")
        if group is None:
            units.append([char])
        elif group in groups:
            groups[group].append(char)
        else:
            groups[group] = [char]
            units.append(groups[group])
    return units


def unit_label(unit: list[dict]) -> str:
    """How the initiative screen names a turn: "Goblin Warriors (6)" for a
    group, the combatant's name otherwise."""
    group = unit[0].get("initiative_group")
    return f"{group} ({len(unit)})" if group else unit[0]["name"]


def start_turn(char: dict):
    """char's turn starts: its Action, Bonus Action and Reaction are back,
    and its movement on the map starts over (feet moved, Dashes taken).
    Everyone else keeps theirs until their own turn starts."""
    char["action_uses"] = {}
    char.pop(MOVED_KEY, None)
    char.pop(DASHES_KEY, None)


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
            return self.with_auras(target)
        return self.with_auras(with_cover(target, reading))

    def with_auras(self, char: dict) -> dict:
        """Char as a roll for it reads it, with what its allies' auras give
        it from where they stand (Combat/Fight/auras.py: Aura of
        Protection's bonus to saving throws): a copy to read, never to
        change. Fight.covered gives it too."""
        found = aura_modifiers(char, self.characters, self._feet)
        return with_auras(char, found)

    def _feet(self, a: dict, b: dict) -> int | None:
        return None if a is b else self.distance_ft(a, b)

    def range_check(
        self, source: dict | None, target: dict | None, attack: AttackRange | None
    ) -> RangeCheck:
        """What the map says of `attack`'s reach or range from source to
        target (Combat/Arena/ranges.py): Long range's Disadvantage, an enemy
        within 5 feet of a ranged attacker, past its reach or range."""
        # Pack Tactics' Advantage, from where the attacker's allies stand
        # (Combat/Fight/auras.py), noted when the map can't say.
        pack = tuple(pack_tactics(source, target, self.characters, self._feet))
        if not self.arena_settings.in_use:
            return replace(NO_RANGE_CHECK, extra=pack)
        check = check_attack_range(
            attack, source, target, self.characters, self.map_settings()
        )
        return replace(check, extra=check.extra + pack)

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

    # ---- The turn order ----
    # An initiative group (initiative_units) stands together in the order and
    # takes one turn: current_turn_idx is its first member.

    def turn_span(self, idx: int) -> tuple[int, int]:
        """The slice [start, end) of initiative_order whose turn idx is in:
        its initiative group's run, or idx alone."""
        order = self.initiative_order
        group = order[idx].get("initiative_group")
        start, end = idx, idx + 1
        if group is None:
            return start, end
        while start > 0 and order[start - 1].get("initiative_group") == group:
            start -= 1
        while end < len(order) and order[end].get("initiative_group") == group:
            end += 1
        return start, end

    def current_turn_group(self) -> list[dict]:
        """Everyone whose turn it is (the active combatant's initiative
        group, or just them); [] outside combat."""
        if self.phase != Phase.COMBAT or not self.initiative_order:
            return []
        start, end = self.turn_span(self.current_turn_idx)
        return self.initiative_order[start:end]

    def is_last_turn(self) -> bool:
        if not self.initiative_order:
            return True
        return self.turn_span(self.current_turn_idx)[1] >= len(self.initiative_order)

    def is_first_turn(self) -> bool:
        """Whether it's round 1's first turn, so there is no turn before it."""
        return self.round_number <= 1 and (
            not self.initiative_order or self.turn_span(self.current_turn_idx)[0] == 0
        )

    def turn_is_dead(self) -> bool:
        """Whether everyone whose turn it is is dead. Someone dying still has
        a turn: it's when they make their death save."""
        return all(death_state(c) == DEAD for c in self.current_turn_group())

    def upcoming_turns(self, skip_dead: bool) -> list[list[dict]]:
        """The turns after this one, soonest first, once round the order;
        with `skip_dead`, leaving out the ones Next would pass over."""
        order = self.initiative_order
        turns = []
        start = 0
        while start < len(order):
            span_end = self.turn_span(start)[1]
            turns.append(order[start:span_end])
            start = span_end
        now = next(
            i
            for i, turn in enumerate(turns)
            if any(c is order[self.current_turn_idx] for c in turn)
        )
        upcoming = turns[now + 1 :] + turns[:now]
        if not skip_dead:
            return upcoming
        return [turn for turn in upcoming if any(death_state(c) != DEAD for c in turn)]

    def pass_turn(self) -> bool:
        """Make it the next turn's; True when that starts a new round (counted
        in round_number). What the turn passing ticks is the caller's."""
        new_round = self.is_last_turn()
        if not new_round:
            self.current_turn_idx = self.turn_span(self.current_turn_idx)[1]
        else:
            self.round_number += 1
            self.current_turn_idx = 0
        return new_round

    def step_back(self, skip_dead: bool) -> bool:
        """Make it the previous turn's (the last one of the round before,
        from a round's first turn), changing nothing else; with `skip_dead`,
        the last turn Next wouldn't have passed over. True when it went back
        a round."""
        went_back_a_round = False
        for _ in initiative_units(self.initiative_order):
            start = self.turn_span(self.current_turn_idx)[0]
            if start > 0:
                self.current_turn_idx = self.turn_span(start - 1)[0]
            else:
                self.round_number -= 1
                last = len(self.initiative_order) - 1
                self.current_turn_idx = self.turn_span(last)[0]
                went_back_a_round = True
            if not (skip_dead and self.turn_is_dead()) or self.is_first_turn():
                break
        return went_back_a_round

    # ---- Joining and leaving the fight ----
    # Whoever's turn it is keeps it as others join or leave the turn order.

    def place_in_turn_order(self, char: dict, value: int):
        """Give char (not in the turn order) the initiative `value` and put
        it in the turn order by it: before the first turn that rolled lower,
        keeping whoever's turn it is. A turn whose roll isn't known (a fight
        continued from its log) isn't compared; with none known, it goes
        last."""
        char[INITIATIVE_KEY] = value
        order = self.initiative_order
        current = order[self.current_turn_idx] if order else None
        at = next(
            (
                self.turn_span(i)[0]
                for i, c in enumerate(order)
                if c.get(INITIATIVE_KEY) is not None and c[INITIATIVE_KEY] < value
            ),
            len(order),
        )
        order.insert(at, char)
        if current is not None:
            now = next(i for i, c in enumerate(order) if c is current)
            self.current_turn_idx = self.turn_span(now)[0]

    def place_as_in_turn_order(self, char: dict):
        """Put char (in the turn order, not yet in characters) in characters
        where it is in the turn order: before the next one after it there."""
        order = self.initiative_order
        at = next(i for i, c in enumerate(order) if c is char)
        later = next(
            (
                i
                for c in order[at + 1 :]
                for i, w in enumerate(self.characters)
                if w is c
            ),
            len(self.characters),
        )
        self.characters.insert(later, char)

    def move_in_turn_order(self, char: dict, value: int):
        """char (with a turn of its own in the turn order) has the
        initiative `value`: it moves in the turn order by it, as
        place_in_turn_order puts one in, and in characters. Whoever's turn
        it is keeps it; char keeps its turn if it was its."""
        order = self.initiative_order
        current = order[self.current_turn_idx]
        order.remove(char)
        if current is not char:
            # Its index moved if char's turn was before it.
            at = next(i for i, c in enumerate(order) if c is current)
            self.current_turn_idx = self.turn_span(at)[0]
        elif order:
            self.current_turn_idx = min(self.current_turn_idx, len(order) - 1)
        self.place_in_turn_order(char, value)
        if current is char:
            self.current_turn_idx = next(i for i, c in enumerate(order) if c is char)
        if any(c is char for c in self.characters):
            self.characters.remove(char)
            self.place_as_in_turn_order(char)

    def follow_owners_in_turn_order(self, follow: list[dict]):
        """Put the summons `follow` in the turn order right after their
        owners (place_after_owners), keeping whoever's turn it is. Putting
        them in characters is the caller's."""
        current = self.initiative_order[self.current_turn_idx]
        self.initiative_order = place_after_owners(self.initiative_order, follow)
        at = next(i for i, c in enumerate(self.initiative_order) if c is current)
        self.current_turn_idx = self.turn_span(at)[0]

    def remove(self, char: dict):
        """Take char out of characters and, in the turns, out of the turn
        order, keeping whoever's turn it is (the next one's, when it was
        char's)."""
        order = self.initiative_order
        if self.phase == Phase.COMBAT and any(c is char for c in order):
            current = order[self.current_turn_idx]
            at = next(i for i, c in enumerate(order) if c is char)
            self.initiative_order = [c for c in order if c is not char]
            if not self.initiative_order:
                self.current_turn_idx = 0
            elif current is char:
                at %= len(self.initiative_order)
                self.current_turn_idx = self.turn_span(at)[0]
            else:
                at = next(
                    i for i, c in enumerate(self.initiative_order) if c is current
                )
                self.current_turn_idx = self.turn_span(at)[0]
        self.characters[:] = [c for c in self.characters if c is not char]
