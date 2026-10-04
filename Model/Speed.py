from Model.Bonuses import Bonuses, DerivedBonus
from Model.Contracts import StatView
from Model.Recorder import Recorder, records


class Speed(Recorder):
    """Every bonus to walking speed (flat or formula-valued - see Bonuses),
    e.g. "+10 feet while you aren't wearing Heavy armor". The base speed is
    the species' (Character.base_speed, a source), read on total().

    Merge rule: sum."""

    def __init__(self):
        self.bonuses = Bonuses()

    @records
    def add_bonus(self, bonus: int) -> None:
        self.bonuses.add(bonus)

    @records
    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def total(self, view: StatView) -> int:
        return view.get_base_speed() + self.bonuses.total(view)
