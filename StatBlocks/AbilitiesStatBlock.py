import numpy as np

import Definitions
from Definitions import Ability
from StatBlocks.StatBlock import StatBlock


class AbilitiesStatBlock(StatBlock):
    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

    def add_bonus(self, ability: Ability, bonus: int):
        if not isinstance(bonus, int):
            raise ValueError("Bonus must be an integer.")
        if ability == Ability.STRENGTH:
            self.strength += bonus
        elif ability == Ability.DEXTERITY:
            self.dexterity += bonus
        elif ability == Ability.CONSTITUTION:
            self.constitution += bonus
        elif ability == Ability.INTELLIGENCE:
            self.intelligence += bonus
        elif ability == Ability.WISDOM:
            self.wisdom += bonus
        elif ability == Ability.CHARISMA:
            self.charisma += bonus
        else:
            raise ValueError("Invalid ability.")

    def get_score(self, ability: Ability):
        return getattr(self, ability.name.lower())

    def get_modifier(self, ability: Ability):
        score = self.get_score(ability)
        return (score - 10) // 2

    def get_ability_with_highest_modifier(
        self,
    ) -> Definitions.Ability:
        return self._get_ability_with_highest_modifier(list(Definitions.Ability))

    def get_spellcasting_ability_with_highest_modifier(
        self,
    ) -> Definitions.Ability:
        return self._get_ability_with_highest_modifier(
            [
                Definitions.Ability.INTELLIGENCE,
                Definitions.Ability.WISDOM,
                Definitions.Ability.CHARISMA,
            ]
        )

    def _get_ability_with_highest_modifier(
        self, abilities: list[Definitions.Ability]
    ) -> Definitions.Ability:
        highest_ability = None
        highest_modifier = -np.inf
        for ability in abilities:
            modifier = self.get_modifier(ability)
            if modifier > highest_modifier:
                highest_modifier = modifier
                highest_ability = ability
        if highest_ability is None:
            raise ValueError("No abilities found.")
        return highest_ability


class StandardArrayAbilitiesStatBlock(AbilitiesStatBlock):
    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ):
        values_needed = {8, 10, 12, 13, 14, 15}
        provided_values = {
            strength,
            dexterity,
            constitution,
            intelligence,
            wisdom,
            charisma,
        }
        if values_needed != provided_values:
            raise ValueError(
                "StandardArrayAbilitiesStatBlock must use the standard array values: 15, 14, 13, 12, 10, 8"
            )
        super().__init__(
            strength, dexterity, constitution, intelligence, wisdom, charisma
        )
