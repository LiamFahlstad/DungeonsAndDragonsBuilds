from Core.Definitions import Ability
from Core.Rules import CARRYING_CAPACITY_BASE_SLOTS
from Model.Bonuses import by_source
from Model.Contracts import StatView
from Model.Recorder import Recorder, records
from Model.Records.SourcedValue import SourcedValue

# The label of the base slots every person has, listed first.
PERSON_SOURCE = "Person"


class CarryingCapacity(Recorder):
    """Carrying capacity sources, in item slots. The dynamic "Person" base
    (CARRYING_CAPACITY_BASE_SLOTS + Strength modifier) isn't stored here - it depends on the character's
    final Strength score, read through the view.

    Merge rule: sum. Reads list Person first, then sources sorted by
    (source, slots)."""

    def __init__(self):
        # Bonus sources only (Person is computed dynamically in sources()).
        self._bonus_sources: list[SourcedValue] = []

    @records
    def add_bonus(self, source: str, bonus: int) -> None:
        self._bonus_sources.append(SourcedValue(bonus, source))

    def sources(self, view: StatView) -> list[SourcedValue]:
        """Every carrying capacity source, including the dynamic 'Person' base."""
        person_slots = CARRYING_CAPACITY_BASE_SLOTS + view.get_ability_modifier(
            Ability.STRENGTH
        )
        person = SourcedValue(person_slots, PERSON_SOURCE)
        return [person] + sorted(self._bonus_sources, key=by_source)

    def total(self, view: StatView) -> int:
        """Total carrying capacity in item slots (base 3 + STR mod + bonuses)."""
        return sum(source.value for source in self.sources(view))
