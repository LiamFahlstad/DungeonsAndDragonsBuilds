from typing import TYPE_CHECKING

from Model.Bonuses import Bonuses, DerivedBonus
from Model.ClassLevels import ClassLevels

if TYPE_CHECKING:
    from Model.Character import Character


class HitPoints:
    """The hit point bonus granted by features (e.g. Tough, Draconic
    Resilience) - flat or formula-valued (see Bonuses) - on top of the roll
    worked out from class levels and Constitution. See calculate()."""

    def __init__(self):
        self.bonuses = Bonuses()

    def add_bonus(self, amount: int) -> None:
        self.bonuses.add(amount)

    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def calculate(
        self,
        class_levels: ClassLevels,
        constitution_modifier: int,
        character: "Character",
    ) -> int:
        # Guaranteed set by the time hit points are calculated - see
        # Character.base_class.
        base_class = class_levels.base_class
        assert base_class is not None
        # First level: max hit die + constitution modifier.
        hit_points = base_class.hit_die + constitution_modifier
        for character_class, level in class_levels.level_per_class.items():
            levels_to_add = level - (1 if character_class == base_class else 0)
            if levels_to_add <= 0:
                continue
            hit_points += levels_to_add * (
                character_class.average_hit_die + constitution_modifier
            )
        return hit_points + self.bonuses.total(character)
