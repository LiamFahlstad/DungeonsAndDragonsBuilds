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
        self.armor_class_without_bonus = 10
        self.armor_class_bonus = 0
        self.initiative_bonus = 0  # Overridden during character creation
        self.weapons_masteries = []

    @property
    def armor_class(self) -> int:
        return self.armor_class_without_bonus + self.armor_class_bonus

    @property
    def initiative(self) -> int:
        return self.initiative_bonus

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
