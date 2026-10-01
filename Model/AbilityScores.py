from typing import Optional

import Core.Definitions as Definitions
from Core.Definitions import Ability
from Model.Recorder import Recorder, records


def _score_property(ability: Ability) -> property:
    """`abilities.strength` etc.: reads the final score, writes the base score."""

    def get(self: "AbilityScores") -> int:
        return self.get_score(ability)

    @records
    def set(self: "AbilityScores", score: int) -> None:
        self._base_scores[ability] = score

    return property(get, set)


class AbilityScores(Recorder):
    """Base scores plus every increase granted on top of them.

    Increases are recorded, never summed as they arrive, and resolved on every
    read - so the order features and items grant them in doesn't matter:

    - A capped increase ("to a maximum of 20") never raises a score above its
      cap, and never lowers one something else already pushed past it. Capped
      increases resolve lowest cap first - the order the rules grant them in
      (ASIs and feats before level-20 capstones that raise the cap to 25) - and
      with equal caps their order can't change the result.
    - An uncapped increase is an equipment bonus (a magic item) and applies on
      top of the character's own score. Requirements such as an armor's
      Strength or a multiclass minimum read get_own_score(), which excludes it.
    """

    strength = _score_property(Ability.STRENGTH)
    dexterity = _score_property(Ability.DEXTERITY)
    constitution = _score_property(Ability.CONSTITUTION)
    intelligence = _score_property(Ability.INTELLIGENCE)
    wisdom = _score_property(Ability.WISDOM)
    charisma = _score_property(Ability.CHARISMA)

    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ):
        self._base_scores: dict[Ability, int] = {
            Ability.STRENGTH: strength,
            Ability.DEXTERITY: dexterity,
            Ability.CONSTITUTION: constitution,
            Ability.INTELLIGENCE: intelligence,
            Ability.WISDOM: wisdom,
            Ability.CHARISMA: charisma,
        }
        # (ability, bonus, max_score) in grant order; max_score None = uncapped.
        self._increases: list[tuple[Ability, int, Optional[int]]] = []

    @records
    def add_bonus(self, ability: Ability, bonus: int, max_score: Optional[int] = None):
        if not isinstance(bonus, int):
            raise ValueError("Bonus must be an integer.")
        if ability not in self._base_scores:
            raise ValueError("Invalid ability.")
        self._increases.append((ability, bonus, max_score))

    def get_own_score(self, ability: Ability) -> int:
        """The score from the base plus capped increases (species, background,
        ASIs, feats, class features) - everything but equipment bonuses."""
        score = self._base_scores[ability]
        capped = sorted(
            (
                (max_score, bonus)
                for increased, bonus, max_score in self._increases
                if increased == ability and max_score is not None
            ),
            key=lambda increase: increase[0],
        )
        for max_score, bonus in capped:
            score += min(bonus, max(0, max_score - score))
        return score

    def get_score(self, ability: Ability) -> int:
        return self.get_own_score(ability) + sum(
            bonus
            for increased, bonus, max_score in self._increases
            if increased == ability and max_score is None
        )

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


class StandardArrayAbilityScores(AbilityScores):
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
                "StandardArrayAbilityScores must use the standard array values: 15, 14, 13, 12, 10, 8"
            )
        super().__init__(
            strength, dexterity, constitution, intelligence, wisdom, charisma
        )


class PointBuyAbilityScores(AbilityScores):
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
        """
        Point costs:
            8  -> 0
            9  -> 1
            10 -> 2
            11 -> 3
            12 -> 4
            13 -> 5
            14 -> 7
            15 -> 9
        """
        if score <= 13:
            return score - 8
        return 5 + 2 * (score - 13)
