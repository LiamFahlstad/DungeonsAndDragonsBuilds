import Definitions
from StatBlocks.StatBlock import StatBlock


class CombatStatBlock(StatBlock):
    def __init__(
        self,
        speed: int,
        size: Definitions.CreatureSize,
    ):
        self.hit_points_bonus = 0
        self.speed = speed
        self.size = size
        self.armor_class = 10  # Overridden during character creation
        self.initiative_bonus = 0  # Overridden during character creation

    @property
    def initiative(self) -> int:
        return self.initiative_bonus

    def update_armor_class(self, new_armor_class: int, pick_max: bool = True):
        if pick_max:
            self.armor_class = max(self.armor_class, new_armor_class)
        else:
            self.armor_class = new_armor_class

    def increase_armor_class(self, increase_by: int):
        self.armor_class += increase_by

    def calculate_hit_points(
        self,
        starter_class: Definitions.CharacterClass,
        level_per_class: dict[Definitions.CharacterClass, int],
        constitution_modifier: int,
    ) -> int:
        # First level: max hit die + constitution modifier

        hit_points = starter_class.hit_die + constitution_modifier
        # Subsequent levels: average hit die + constitution modifier
        for character_class, level in level_per_class.items():
            start = 1 if character_class == starter_class else 0
            for _ in range(start, level):
                hit_points += character_class.average_hit_die + constitution_modifier
        return hit_points + self.hit_points_bonus
