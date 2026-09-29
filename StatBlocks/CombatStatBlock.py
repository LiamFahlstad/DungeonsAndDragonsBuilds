from dataclasses import dataclass
from typing import Optional

import Core.Definitions as Definitions
from StatBlocks.StatBlock import StatBlock


@dataclass(frozen=True)
class ArmorClassFormula:
    """One way to calculate base AC: `base` + the summed modifiers of
    `abilities`, capped at `ability_modifier_cap` (None = uncapped).

    A character with several formulas uses the best one that applies (the
    rules let you pick one), so granting another never overwrites anything:
    - is_armor: worn body armor. While any is worn, only armor formulas apply
      - it replaces every "while you aren't wearing armor" formula.
    - allows_shield: False for formulas that stop working while a Shield is
      wielded (Monk's Unarmored Defense).
    """

    base: int
    abilities: frozenset[Definitions.Ability]
    ability_modifier_cap: Optional[int] = None
    is_armor: bool = False
    allows_shield: bool = True


# Everyone's AC without armor or a feature: 10 + Dexterity modifier.
UNARMORED_ARMOR_CLASS = ArmorClassFormula(
    base=10, abilities=frozenset({Definitions.Ability.DEXTERITY})
)


class CombatStatBlock(StatBlock):
    def __init__(
        self,
        speed: int,
        size: Definitions.CreatureSize,
    ):
        self.hit_points_bonus = 0
        self.speed = speed
        self.size = size
        self.armor_class_formulas: list[ArmorClassFormula] = [UNARMORED_ARMOR_CLASS]
        self.armor_class_modifier = 0  # Non-ability related modifier

    def add_armor_class_formula(self, formula: ArmorClassFormula):
        self.armor_class_formulas.append(formula)

    def get_applicable_armor_class_formulas(
        self, is_wielding_shield: bool
    ) -> list[ArmorClassFormula]:
        armor = [formula for formula in self.armor_class_formulas if formula.is_armor]
        if armor:
            return armor
        return [
            formula
            for formula in self.armor_class_formulas
            if formula.allows_shield or not is_wielding_shield
        ]

    def increase_armor_class(self, increase_by: int):
        self.armor_class_modifier += increase_by

    def calculate_hit_points(
        self,
        base_class: Definitions.CharacterClass,
        level_per_class: dict[Definitions.CharacterClass, int],
        constitution_modifier: int,
    ) -> int:
        # First level: max hit die + constitution modifier.
        hit_points = base_class.hit_die + constitution_modifier
        for character_class, level in level_per_class.items():
            levels_to_add = level - (1 if character_class == base_class else 0)
            if levels_to_add <= 0:
                continue
            hit_points += levels_to_add * (
                character_class.average_hit_die + constitution_modifier
            )
        return hit_points + self.hit_points_bonus
