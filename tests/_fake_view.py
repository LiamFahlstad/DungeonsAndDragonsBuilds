"""A StatView with fixed answers, for unit-testing a part without a
Character: a part's resolvers take nothing but the view, so these tests need
no builder and no Character. Scores have no increases - own score, final
score and base score are the same number."""

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
        proficiency_bonus: int = 2,
        is_wielding_shield: bool = False,
        has_shield_training: bool = False,
        untrained_armor: bool = False,
    ):
        self._scores = {ability: 10 for ability in Ability} | (scores or {})
        self.class_levels = class_levels or ClassLevels(
            base_class=CharacterClass.FIGHTER,
            level_per_class={CharacterClass.FIGHTER: 1},
        )
        self.fixed_spell_slots = fixed_spell_slots or {}
        self._base_speed = base_speed
        self._proficiency_bonus = proficiency_bonus
        self.is_wielding_shield = is_wielding_shield
        self.has_shield_training = has_shield_training
        self._untrained_armor = untrained_armor

    def get_base_ability_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_own_ability_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_ability_modifier(self, ability: Ability) -> int:
        return ability_modifier(self._scores[ability])

    def get_constitution_modifier(self) -> int:
        return self.get_ability_modifier(Ability.CONSTITUTION)

    def get_base_speed(self) -> int:
        return self._base_speed

    def get_proficiency_bonus(self) -> int:
        return self._proficiency_bonus

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        return self._untrained_armor and ability in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        )
