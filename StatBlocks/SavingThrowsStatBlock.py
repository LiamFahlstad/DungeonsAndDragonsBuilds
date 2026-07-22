from typing import Optional

from Core.Definitions import Ability
from StatBlocks.StatBlock import StatBlock


def _proficiency_map(*abilities: Ability) -> dict[Ability, bool]:
    return {ability: True for ability in abilities}


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
            proficiencies=_proficiency_map(Ability.WISDOM, Ability.CHARISMA)
        )


class FighterSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.STRENGTH, Ability.CONSTITUTION)
        )


class WarlockSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.WISDOM, Ability.CHARISMA)
        )


class RangerSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.STRENGTH, Ability.DEXTERITY)
        )


class WizardSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.WISDOM, Ability.INTELLIGENCE)
        )


class BarbarianSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.STRENGTH, Ability.CONSTITUTION)
        )


class RogueSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.DEXTERITY, Ability.INTELLIGENCE)
        )


class DruidSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.WISDOM, Ability.INTELLIGENCE)
        )


class BardSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.DEXTERITY, Ability.CHARISMA)
        )


class ClericSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.WISDOM, Ability.CHARISMA)
        )


class SorcererSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.CONSTITUTION, Ability.CHARISMA)
        )


class MonkSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.STRENGTH, Ability.DEXTERITY)
        )


class ArtificerSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies=_proficiency_map(Ability.CONSTITUTION, Ability.INTELLIGENCE)
        )
