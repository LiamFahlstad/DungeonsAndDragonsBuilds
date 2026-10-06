from typing import Optional

import attr

from Core.Definitions import Ability
from Model.Contracts import StatView
from Model.Recorder import Recorder, records


@attr.s(frozen=True, auto_attribs=True)
class CappedIncrease:
    """+`bonus` to `ability`, to a maximum of `max_score`."""

    ability: Ability
    bonus: int
    max_score: int


class AbilityIncreases(Recorder):
    """Every increase granted on top of the base scores (Model/AbilityScores.py).

    Increases are recorded, never summed as they arrive, and resolved on every
    read - so the order features and items grant them in doesn't matter:

    - A capped increase ("to a maximum of 20") never raises a score above its
      cap, and never lowers one something else already pushed past it. Capped
      increases resolve lowest cap first - the order the rules grant them in
      (ASIs and feats before level-20 capstones that raise the cap to 25) - and
      with equal caps their order can't change the result.
    - An uncapped increase is an equipment bonus (a magic item) and applies on
      top of the character's own score. Requirements such as an armor's
      Strength or a multiclass minimum read own_score(), which excludes it.

    Merge rule: capped increases resolve lowest cap first (saturating at
    each cap), uncapped increases sum."""

    def __init__(self):
        self._capped: list[CappedIncrease] = []
        # Uncapped (equipment) bonuses, summed per ability.
        self._equipment_bonus: dict[Ability, int] = {}

    @records
    def add(self, ability: Ability, bonus: int, max_score: Optional[int] = None):
        if not isinstance(bonus, int):
            raise ValueError("Bonus must be an integer.")
        if not isinstance(ability, Ability):
            raise ValueError("Invalid ability.")
        if max_score is None:
            current = self._equipment_bonus.get(ability, 0)
            self._equipment_bonus[ability] = current + bonus
        else:
            self._capped.append(CappedIncrease(ability, bonus, max_score))

    def own_score(self, ability: Ability, view: StatView) -> int:
        """The base score plus capped increases (species, background, ASIs,
        feats, class features) - everything but equipment bonuses."""
        score = view.get_base_ability_score(ability)
        for increase in self._capped_lowest_cap_first(ability):
            room_below_cap = max(0, increase.max_score - score)
            score += min(increase.bonus, room_below_cap)
        return score

    def score(self, ability: Ability, view: StatView) -> int:
        """The final score: own_score() plus every equipment bonus."""
        equipment_bonus = self._equipment_bonus.get(ability, 0)
        return self.own_score(ability, view) + equipment_bonus

    def _capped_lowest_cap_first(self, ability: Ability) -> list[CappedIncrease]:
        capped = [increase for increase in self._capped if increase.ability == ability]
        return sorted(capped, key=_max_score)


def _max_score(increase: CappedIncrease) -> int:
    return increase.max_score
