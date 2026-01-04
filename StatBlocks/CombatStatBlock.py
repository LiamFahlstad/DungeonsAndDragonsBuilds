from typing import Optional

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
        self.armor_class_base = 10  # Overridden during character creation
        self.armor_class_abilities = {Definitions.Ability.DEXTERITY}
        self.armor_class_modifier = 0  # Non-ability related modifier

    def update_armor_class_base(self, new_armor_class_base: int):
        self.armor_class_base = new_armor_class_base

    def increase_armor_class(self, increase_by: int):
        self.armor_class_modifier += increase_by

    def add_armor_class_ability(self, ability: Definitions.Ability):
        self.armor_class_abilities.add(ability)

    def change_armor_class_ability(self, new_ability: Optional[Definitions.Ability]):
        if new_ability is None:
            self.armor_class_abilities.clear()
        else:
            self.armor_class_abilities = {new_ability}

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
