"""How the fight writes its log, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.4). A rule that changes the fight logs what it did through the
Logger it was given, in the order it happens: the combat window appends
each line to the encounter log, with whose turn it is, its Undo step and
whether players may read it (Combat/CombatUIQt/logger.py), and a test keeps
them in a RecordingLogger.

A line that changes someone's state carries `character`, `action` and
`value`: the party's state is replayed from those on the next run
(Combat/Fight/log.py's apply_replay_action)."""

from dataclasses import dataclass, field
from typing import Any, Protocol


class Logger(Protocol):
    def log(
        self,
        text: str,
        *,
        note_turn: bool = True,
        character: str | None = None,
        action: str | None = None,
        value: Any = None,
        public: bool = True,
    ) -> bool:
        """Log `text`. `note_turn`: start it with whose turn it is;
        `public` False keeps it off the player link whatever it says.
        Returns whether players can read it."""
        ...


@dataclass(frozen=True)
class LoggedLine:
    text: str
    character: str | None = None
    action: str | None = None
    value: Any = None
    public: bool = True
    note_turn: bool = True


@dataclass
class RecordingLogger:
    """A Logger that keeps every line, for tests. Players read none."""

    lines: list[LoggedLine] = field(default_factory=list)

    def log(
        self,
        text: str,
        *,
        note_turn: bool = True,
        character: str | None = None,
        action: str | None = None,
        value: Any = None,
        public: bool = True,
    ) -> bool:
        self.lines.append(LoggedLine(text, character, action, value, public, note_turn))
        return False

    @property
    def texts(self) -> list[str]:
        return [line.text for line in self.lines]
