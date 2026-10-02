from Model.Contracts import Formula, StatView
from Model.Recorder import Recorder, records

# A bonus whose value depends on other stats (e.g. "equal to your Wisdom
# modifier"). Stored as a formula and evaluated at read time, so it always
# reflects the final stats no matter which feature, armor or item applied
# first - snapshotting such a value inside apply() would freeze it at
# whatever the stat was when that feature happened to run. An alias of
# Formula (Model/Contracts.py), kept until Step 11 of
# Notes/model-refactor-plan.md.
DerivedBonus = Formula


class Bonuses(Recorder):
    """Flat values and formula values (see DerivedBonus), each with a source
    label - the "a flat bonus, plus formula bonuses, each with a source"
    shape shared by Initiative, ArmorClass, HitPoints, Speed, Skills and
    SavingThrows. A value object: it has no character of its own, and every
    query that resolves formulas takes a StatView of the finished character
    as an argument.

    Merge rule: sum. Reads list flat sources, then formula sources, each
    sorted by (source, value)."""

    def __init__(self):
        self._flat: list[tuple[int, str]] = []
        self._formulas: list[tuple[DerivedBonus, str]] = []

    @records
    def add(self, value: int, source: str = "Other") -> None:
        self._flat.append((value, source))

    @records
    def add_formula(self, formula: DerivedBonus, source: str = "Other") -> None:
        self._formulas.append((formula, source))

    def total(self, view: StatView) -> int:
        flat = sum(value for value, _source in self._flat)
        resolved = sum(formula(view) for formula, _source in self._formulas)
        return flat + resolved

    def sources(self, view: StatView) -> list[tuple[int, str]]:
        """Every source: flat sources, then non-zero resolved formula
        sources, each sorted by (source, value). A formula that currently
        evaluates to 0 (e.g. Jack of All Trades on a skill you're proficient
        in) isn't a source worth listing."""

        def by_source(entry: tuple[int, str]) -> tuple[str, int]:
            return entry[1], entry[0]

        resolved = [(formula(view), source) for formula, source in self._formulas]
        return sorted(self._flat, key=by_source) + sorted(
            ((value, source) for value, source in resolved if value != 0),
            key=by_source,
        )
