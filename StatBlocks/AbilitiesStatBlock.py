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

    def get_spell_casting_ability_with_highest_modifier(
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
        if not abilities:
            raise ValueError("No abilities found.")
        return max(abilities, key=self.get_modifier)


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


class PointBuyAbilitiesStatBlock(AbilitiesStatBlock):
    _BUDGET = 27
    _MIN_SCORE = 8
    _MAX_SCORE = 15

    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ):
        scores = {
            Ability.STRENGTH: strength,
            Ability.DEXTERITY: dexterity,
            Ability.CONSTITUTION: constitution,
            Ability.INTELLIGENCE: intelligence,
            Ability.WISDOM: wisdom,
            Ability.CHARISMA: charisma,
        }
        for ability, score in scores.items():
            if not (self._MIN_SCORE <= score <= self._MAX_SCORE):
                raise ValueError(
                    f"Point Buy {ability.name.title()} score must be between "
                    f"{self._MIN_SCORE} and {self._MAX_SCORE}, got {score}."
                )

        spent = sum(self._point_cost(score) for score in scores.values())
        if spent != self._BUDGET:
            raise ValueError(
                f"Point Buy scores must spend exactly {self._BUDGET} points, got {spent}."
            )

        super().__init__(
            strength, dexterity, constitution, intelligence, wisdom, charisma
        )

    @staticmethod
    def _point_cost(score: int) -> int:
        if score <= 13:
            return score - 8
        return 5 + 2 * (score - 13)
