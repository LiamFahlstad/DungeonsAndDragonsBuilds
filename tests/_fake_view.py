"""A StatView with fixed answers, for unit-testing a part without a
Character. Scores have no increases: own score, final score and base score
are the same number."""

from typing import Optional

from Core.Definitions import Ability, CharacterClass
from Model.AbilityScores import ability_modifier
from Model.ClassLevels import ClassLevels


class FakeView:
    def __init__(
        self,
        scores: Optional[dict[Ability, int]] = None,
        class_levels: Optional[ClassLevels] = None,
        fixed_spell_slots: Optional[dict[int, int]] = None,
        base_speed: int = 30,
    ):
        self._scores = {ability: 10 for ability in Ability} | (scores or {})
        self.class_levels = class_levels or ClassLevels(
            base_class=CharacterClass.FIGHTER,
            level_per_class={CharacterClass.FIGHTER: 1},
        )
        self.fixed_spell_slots = fixed_spell_slots or {}
        self._base_speed = base_speed

    def get_base_ability_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_own_ability_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_ability_modifier(self, ability: Ability) -> int:
        return ability_modifier(self._scores[ability])

    def get_base_speed(self) -> int:
        return self._base_speed
