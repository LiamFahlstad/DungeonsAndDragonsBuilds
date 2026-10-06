from Model.Bonuses import Bonuses
from Model.Contracts import StatView, Value
from Model.Recorder import Recorder, records


class HitPoints(Recorder):
    """The hit point bonus granted by features (e.g. Tough, Draconic
    Resilience) - flat or formula-valued (see Bonuses) - on top of the roll
    worked out from class levels and Constitution. See total().

    Merge rule: sum."""

    def __init__(self):
        self.bonuses = Bonuses()

    @records
    def add_bonus(self, amount: Value) -> None:
        self.bonuses.add(amount)

    def total(self, view: StatView) -> int:
        class_levels = view.class_levels
        constitution_modifier = view.get_constitution_modifier()
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
        return hit_points + self.bonuses.total(view)
