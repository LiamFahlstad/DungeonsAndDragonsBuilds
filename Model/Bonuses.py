import attr

from Model.View import Formula, CharacterView, Value
from Model.Recorder import Recorder, records
from Model.Records.SourcedValue import SourcedValue

# The source label of a bonus granted without one.
OTHER_SOURCE = "Other"


@attr.s(frozen=True, auto_attribs=True)
class SourcedFormula:
    """A bonus worked out on read (a Formula), and its source label."""

    formula: Formula
    source: str


class Bonuses(Recorder):
    """Flat values and formula values (a Formula - see Model/View.py),
    each with a source label - the "a flat bonus, plus formula bonuses, each
    with a source"
    shape shared by Initiative, ArmorClass, HitPoints, Speed, Skills and
    SavingThrows. A value object: it has no character of its own, and every
    query that resolves formulas takes a CharacterView of the finished character
    as an argument.

    Merge rule: sum. Reads list flat sources, then formula sources, each
    sorted by (source, value)."""

    def __init__(self):
        self._flat: list[SourcedValue] = []
        self._formulas: list[SourcedFormula] = []

    @records
    def add(self, value: Value, source: str = OTHER_SOURCE) -> None:
        """A flat bonus, or a formula worked out on every read."""
        if callable(value):
            self._formulas.append(SourcedFormula(value, source))
        else:
            self._flat.append(SourcedValue(value, source))

    def total(self, view: CharacterView) -> int:
        flat = sum(bonus.value for bonus in self._flat)
        resolved = sum(bonus.formula(view) for bonus in self._formulas)
        return flat + resolved

    def sources(self, view: CharacterView) -> list[SourcedValue]:
        """Every source: flat sources, then non-zero resolved formula
        sources, each sorted by (source, value). A formula that currently
        evaluates to 0 (e.g. Jack of All Trades on a skill you're proficient
        in) isn't a source worth listing."""
        resolved = []
        for bonus in self._formulas:
            value = bonus.formula(view)
            if value != 0:
                resolved.append(SourcedValue(value, bonus.source))
        return sorted(self._flat, key=by_source) + sorted(resolved, key=by_source)


def by_source(bonus: SourcedValue) -> tuple[str, int]:
    """The canonical order of a list of sources: by label, then value."""
    return bonus.source, bonus.value
