from typing import Optional
from Definitions import Ability
import Definitions
from StatBlocks.StatBlock import StatBlock


class CombatStatBlock(StatBlock):
    def __init__(self, hit_die: int, speed: int, size: Definitions.CreatureSize):
        self.hit_die = hit_die
        self.hit_points_bonus = 0
        self.speed = speed
        self.size = size
        self.armor_class_without_bonus = 10
        self.armor_class_bonus = 0
        self.initiative_bonus = 0  # Overridden during character creation
        self.weapons_masteries = []

    @property
    def average_hit_die(self) -> int:
        return (self.hit_die // 2) + 1

    @property
    def armor_class(self) -> int:
        return self.armor_class_without_bonus + self.armor_class_bonus

    @property
    def initiative(self) -> int:
        return self.initiative_bonus

    def calculate_hit_points(self, level: int, constitution_modifier: int) -> int:
        # First level: max hit die + constitution modifier
        hit_points = self.hit_die + constitution_modifier
        # Subsequent levels: average hit die + constitution modifier
        for _ in range(1, level):
            hit_points += self.average_hit_die + constitution_modifier
        return hit_points + self.hit_points_bonus
