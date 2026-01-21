from typing import Optional

from Definitions import Ability
from StatBlocks.StatBlock import StatBlock


class SavingThrowsStatBlock(StatBlock):
    def __init__(
        self,
        proficiencies: Optional[dict[Ability, bool]] = None,
        advantages: Optional[dict[Ability, bool]] = None,
    ):
        self.proficiencies = proficiencies if proficiencies is not None else {}
        self.advantages = advantages if advantages is not None else {}

    def is_proficient(self, ability: Ability) -> bool:
        return self.proficiencies.get(ability, False)

    def add_proficiency(self, ability: Ability) -> None:
        self.proficiencies[ability] = True

    def is_advantaged(self, ability: Ability) -> bool:
        return self.advantages.get(ability, False)

    def add_advantage(self, ability: Ability) -> None:
        self.advantages[ability] = True


class PaladinSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.CHARISMA: True,
            }
        )


class FighterSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.STRENGTH: True,
                Ability.CONSTITUTION: True,
            }
        )


class WarlockSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.CHARISMA: True,
            }
        )


class RangerSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.STRENGTH: True,
                Ability.DEXTERITY: True,
            }
        )


class WizardSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.INTELLIGENCE: True,
            }
        )


class BarbarianSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.STRENGTH: True,
                Ability.CONSTITUTION: True,
            }
        )


class RogueSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.DEXTERITY: True,
                Ability.INTELLIGENCE: True,
            }
        )


class DruidSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.INTELLIGENCE: True,
            }
        )


class BardSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.DEXTERITY: True,
                Ability.CHARISMA: True,
            }
        )


class ClericSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.CHARISMA: True,
            }
        )


class SorcererSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.CONSTITUTION: True,
                Ability.CHARISMA: True,
            }
        )


class MonkSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.STRENGTH: True,
                Ability.DEXTERITY: True,
            }
        )
