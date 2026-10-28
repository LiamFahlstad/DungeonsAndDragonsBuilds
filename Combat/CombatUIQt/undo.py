"""Undo for the combat UI: one Ctrl+Z takes back one thing the GM did.

Every operation the GM can do (apply damage, cast a spell, Next Turn, ...)
is an @undoable method. Before it runs, an UndoPoint records the combat
state - each combatant's own data (HP, conditions, slots, stats, timers,
...), who is in the fight, the turn order, the round and the turn - and while
it runs, which log lines it writes. Undoing it puts that state back and
deletes exactly those lines from the encounter log. So a cast's condition
badges, Concentrating, spent action and duration bar go back together, and an
undone hit isn't left in the log to be replayed onto the party next session.

An operation that calls others (casting a spell adds conditions) is one
step: only the outermost @undoable records one. An operation that changes
nothing (no source selected, ...) leaves no step behind.
"""

import functools
import inspect
from dataclasses import dataclass, field


def _plain_copy(value):
    """value with its dicts and lists copied all the way down. Anything else
    (numbers, strings, enums, stat-block dataclasses) isn't changed in place
    during a fight, so it's shared, not copied."""
    if isinstance(value, dict):
        return {key: _plain_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain_copy(item) for item in value]
    return value


def _combat_data(char: dict) -> dict:
    """A copy of what a fight can change about a combatant: its public keys.
    The "_"-prefixed ones (its Character, feature objects, ...) stay fixed."""
    return {
        key: _plain_copy(value)
        for key, value in char.items()
        if not key.startswith("_")
    }


@dataclass
class UndoPoint:
    """The combat state just before one operation, and the log lines it wrote.
    `app` below is the CombatAppQt (not imported: state.py imports this)."""

    characters: list[dict]
    initiative_order: list[dict]
    current_turn_idx: int
    round_number: int
    # _combat_data of each of `characters`, in the same order.
    combat_data: list[dict]
    # (round key, index in the encounter log's round) of each line the
    # operation logged, in order.
    log_entries: list[tuple[str, int]] = field(default_factory=list)

    @classmethod
    def capture(cls, app) -> "UndoPoint":
        return cls(
            characters=list(app.characters),
            initiative_order=list(app.initiative_order),
            current_turn_idx=app.current_turn_idx,
            round_number=app.round_number,
            combat_data=[_combat_data(char) for char in app.characters],
        )

    def changed_since(self, app) -> bool:
        """Whether the operation logged anything or changed the combat state."""
        now = UndoPoint.capture(app)
        return bool(self.log_entries) or (
            [id(c) for c in self.characters] != [id(c) for c in now.characters]
            or [id(c) for c in self.initiative_order]
            != [id(c) for c in now.initiative_order]
            or self.current_turn_idx != now.current_turn_idx
            or self.round_number != now.round_number
            or self.combat_data != now.combat_data
        )

    def restore(self, app):
        """Put app's combat state back. Each combatant dict is refilled in
        place: cards, the turn order and the selection hold the dicts
        themselves. A combatant added since drops out of the fight."""
        for char, data in zip(self.characters, self.combat_data):
            for key in [key for key in char if not key.startswith("_")]:
                del char[key]
            char.update(data)
        app.characters[:] = self.characters
        app.initiative_order = list(self.initiative_order)
        app.current_turn_idx = self.current_turn_idx
        app.round_number = self.round_number


def undoable(method):
    """Make a CombatAppQt method one step of undo (see the module docstring).
    Before combat starts there's nothing to undo, so it just runs."""
    params = inspect.signature(method).parameters.values()
    takes_varargs = any(p.kind is p.VAR_POSITIONAL for p in params)
    positional = sum(
        p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in params
    )

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not takes_varargs:
            # A Qt signal passes its own arguments (clicked's `checked`) to
            # whatever it's connected to; drop the ones the method doesn't take.
            args = args[: positional - 1]
        if self._open_undo_point is not None or self.phase != "COMBAT":
            return method(self, *args, **kwargs)
        point = UndoPoint.capture(self)
        self._open_undo_point = point
        try:
            return method(self, *args, **kwargs)
        finally:
            self._open_undo_point = None
            if point.changed_since(self):
                self.history.append(point)

    return wrapper
