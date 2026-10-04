from typing import Optional

from Core.Definitions import Ability
from Model.Contracts import StatView
from Model.Recorder import Recorder, records


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
        # (ability, bonus, max_score); max_score None = uncapped.
        self._increases: list[tuple[Ability, int, Optional[int]]] = []

    @records
    def add(self, ability: Ability, bonus: int, max_score: Optional[int] = None):
        if not isinstance(bonus, int):
            raise ValueError("Bonus must be an integer.")
        if not isinstance(ability, Ability):
            raise ValueError("Invalid ability.")
        self._increases.append((ability, bonus, max_score))

    def own_score(self, ability: Ability, view: StatView) -> int:
        """The base score plus capped increases (species, background, ASIs,
        feats, class features) - everything but equipment bonuses."""
        score = view.get_base_ability_score(ability)
        capped = sorted(
            (
                (max_score, bonus)
                for increased, bonus, max_score in self._increases
                if increased == ability and max_score is not None
            ),
            key=lambda increase: increase[0],
        )
        for max_score, bonus in capped:
            score += min(bonus, max(0, max_score - score))
        return score

    def score(self, ability: Ability, view: StatView) -> int:
        """The final score: own_score() plus every equipment bonus."""
        return self.own_score(ability, view) + sum(
            bonus
            for increased, bonus, max_score in self._increases
            if increased == ability and max_score is None
        )
