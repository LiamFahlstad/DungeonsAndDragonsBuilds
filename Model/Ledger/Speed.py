from Model.Ledger.Bonuses import OTHER_SOURCE, Bonuses
from Model.View import CharacterView, Value


class Speed:
    """Every bonus to walking speed (flat or formula-valued - see Bonuses),
    e.g. "+10 feet while you aren't wearing Heavy armor". The base speed is
    the species' (Character.base_speed, a source), read on total().

    Merge rule: sum."""

    def __init__(self):
        self.bonuses = Bonuses()

    def add_bonus(self, bonus: Value, source: str = OTHER_SOURCE) -> None:
        self.bonuses.add(bonus, source)

    def total(self, view: CharacterView) -> int:
        return view.base_speed + self.bonuses.total(view)
