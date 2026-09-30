from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from StatBlocks.CharacterStatBlock import CharacterStatBlock

# A bonus whose value depends on other stats (e.g. "equal to your Wisdom
# modifier"). Stored as a formula and evaluated at read time, so it always
# reflects the final stats no matter which feature, armor or item applied
# first - snapshotting such a value inside apply() would freeze it at
# whatever the stat was when that feature happened to run. Shared by every
# StatBlocks part so none of them need to import CharacterStatBlock except
# under TYPE_CHECKING (see Notes/feature-application-model.md).
DerivedBonus = Callable[["CharacterStatBlock"], int]


class Bonuses:
    """Flat values and formula values (see DerivedBonus), each with a source
    label - the "a flat bonus, plus formula bonuses, each with a source"
    shape shared by Initiative, ArmorClass, HitPoints, Speed, Skills and
    SavingThrows. A value object: it has no character of its own, and every
    query that resolves formulas takes the finished CharacterStatBlock as an
    argument."""

    def __init__(self):
        self._flat: list[tuple[int, str]] = []
        self._formulas: list[tuple[DerivedBonus, str]] = []

    def add(self, value: int, source: str = "Other") -> None:
        self._flat.append((value, source))

    def add_formula(self, formula: DerivedBonus, source: str = "Other") -> None:
        self._formulas.append((formula, source))

    def total(self, character: "CharacterStatBlock") -> int:
        flat = sum(value for value, _source in self._flat)
        resolved = sum(formula(character) for formula, _source in self._formulas)
        return flat + resolved

    def sources(self, character: "CharacterStatBlock") -> list[tuple[int, str]]:
        """Every source: flat sources in insertion order, then non-zero
        resolved formula sources in insertion order. A formula that currently
        evaluates to 0 (e.g. Jack of All Trades on a skill you're proficient
        in) isn't a source worth listing."""
        resolved = [(formula(character), source) for formula, source in self._formulas]
        return list(self._flat) + [
            (value, source) for value, source in resolved if value != 0
        ]
