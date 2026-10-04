from Core.Definitions import Ability, DiceRollCondition, combine_roll_conditions
from Model.Bonuses import Bonuses, DerivedBonus
from Model.Contracts import StatView
from Model.Recorder import Recorder, records


class Initiative(Recorder):
    """Every source of an initiative bonus or roll condition. Initiative is
    a Dexterity check, so total() adds the Dexterity modifier and
    roll_condition() adds untrained-armor Disadvantage, both read through
    the view.

    Merge rule: proficiency is a flag, roll conditions are a set (Advantage
    and Disadvantage cancel), bonuses sum."""

    def __init__(self):
        self.proficiency = False
        self.bonuses = Bonuses()
        self._roll_conditions: set[DiceRollCondition] = set()

    @records
    def add_proficiency(self) -> None:
        self.proficiency = True

    @records
    def add_roll_condition(self, condition: DiceRollCondition) -> None:
        self._roll_conditions.add(condition)

    @records
    def add_bonus(self, bonus: int) -> None:
        self.bonuses.add(bonus)

    @records
    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def total(self, view: StatView) -> int:
        """The Dexterity modifier, plus the full proficiency bonus if
        proficient, plus every flat and formula-valued bonus."""
        proficiency = view.get_proficiency_bonus() if self.proficiency else 0
        return (
            view.get_ability_modifier(Ability.DEXTERITY)
            + proficiency
            + self.bonuses.total(view)
        )

    def roll_condition(self, view: StatView) -> DiceRollCondition:
        """Every recorded condition together with untrained-armor
        Disadvantage - combined at once, so two sources that would each
        cancel out on their own still cancel correctly."""
        conditions = set(self._roll_conditions)
        if view.has_untrained_armor_disadvantage(Ability.DEXTERITY):
            conditions.add(DiceRollCondition.DISADVANTAGE)
        return combine_roll_conditions(conditions)
