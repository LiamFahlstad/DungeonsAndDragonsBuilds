from Model.Recorder import Recorder, records


class CarryingCapacity(Recorder):
    """Carrying capacity sources, in item slots. The dynamic "Person" base (3
    + Strength modifier) isn't stored here - it depends on the character's
    final Strength score, so every query takes that modifier in.

    Merge rule: sum. Reads list Person first, then sources sorted by
    (source, slots)."""

    def __init__(self):
        # (source, slots) pairs; bonus sources only (Person is computed
        # dynamically in sources()).
        self._bonus_sources: list[tuple[str, int]] = []

    @records
    def add_bonus(self, source: str, bonus: int) -> None:
        self._bonus_sources.append((source, bonus))

    def sources(self, strength_modifier: int) -> list[tuple[str, int]]:
        """Every carrying capacity source, including the dynamic 'Person' base."""
        person_slots = 3 + strength_modifier
        return [("Person", person_slots)] + sorted(self._bonus_sources)

    def total(self, strength_modifier: int) -> int:
        """Total carrying capacity in item slots (base 3 + STR mod + bonuses)."""
        return sum(slots for _, slots in self.sources(strength_modifier))
