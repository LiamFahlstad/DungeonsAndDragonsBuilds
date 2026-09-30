from typing import TYPE_CHECKING, Optional

from Core.Definitions import Ability
from StatBlocks.Bonuses import Bonuses, DerivedBonus

if TYPE_CHECKING:
    from StatBlocks.CharacterStatBlock import CharacterStatBlock


class SavingThrows:
    def __init__(
        self,
        proficiencies: Optional[dict[Ability, bool]] = None,
        advantages: Optional[dict[Ability, bool]] = None,
    ):
        self.proficiencies = proficiencies if proficiencies is not None else {}
        self.advantages = advantages if advantages is not None else {}
        # Per-ability flat and formula-valued bonuses, each with a source
        # (see StatBlocks/Bonuses.py).
        self._bonuses: dict[Ability, Bonuses] = {}
        # "Proficiency in X; if you already have it, in Y instead" grants, as
        # (X, (Y, ...)) - resolved on read, see _resolved_proficiencies.
        self._conditional_proficiencies: list[tuple[Ability, tuple[Ability, ...]]] = []

    def is_proficient(self, ability: Ability) -> bool:
        return ability in self._resolved_proficiencies()

    def add_proficiency(self, ability: Ability) -> None:
        self.proficiencies[ability] = True

    def add_proficiency_or_alternative(
        self, ability: Ability, alternatives: list[Ability]
    ) -> None:
        """Proficiency in `ability`, or - if the character is proficient in it
        from anything else - in the first of `alternatives` they lack."""
        self._conditional_proficiencies.append((ability, tuple(alternatives)))

    def _resolved_proficiencies(self) -> set[Ability]:
        """Every proficient ability. Conditional grants resolve against all
        the other grants, not just those applied before them, and in a fixed
        order, so the result doesn't depend on grant order."""
        proficient = {ability for ability, has in self.proficiencies.items() if has}
        order = list(Ability)
        for ability, alternatives in sorted(
            self._conditional_proficiencies,
            key=lambda grant: [order.index(a) for a in (grant[0], *grant[1])],
        ):
            choices = [ability, *alternatives]
            granted = next((a for a in choices if a not in proficient), None)
            if granted is not None:
                proficient.add(granted)
        return proficient

    def is_advantaged(self, ability: Ability) -> bool:
        return self.advantages.get(ability, False)

    def add_advantage(self, ability: Ability) -> None:
        self.advantages[ability] = True

    def _bonuses_for(self, ability: Ability) -> Bonuses:
        return self._bonuses.setdefault(ability, Bonuses())

    def add_bonus(self, ability: Ability, bonus: int) -> None:
        self._bonuses_for(ability).add(bonus)

    def add_derived_bonus(self, ability: Ability, bonus: DerivedBonus) -> None:
        self._bonuses_for(ability).add_formula(bonus)

    def get_total_bonus(self, ability: Ability, character: "CharacterStatBlock") -> int:
        """The flat bonus plus every formula-valued bonus, resolved against
        `character` (not the ability modifier or proficiency bonus - see
        CharacterStatBlock.get_saving_throw_modifier)."""
        bonuses = self._bonuses.get(ability)
        return bonuses.total(character) if bonuses is not None else 0
