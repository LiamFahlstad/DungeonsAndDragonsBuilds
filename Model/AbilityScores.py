from types import MappingProxyType

import Core.Definitions as Definitions
from Core.Definitions import Ability
from Core.Rules import (
    POINT_BUY_BUDGET,
    POINT_BUY_MAX_SCORE,
    POINT_BUY_MIN_SCORE,
    STANDARD_ARRAY,
    ability_modifier,
    point_buy_cost,
)


def _score_property(ability: Ability) -> property:
    """`abilities.strength` etc.: the base score, read-only."""

    def get(self: "AbilityScores") -> int:
        return self.get_score(ability)

    return property(get)


class AbilityScores:
    """The player's ability scores before any increase: a source, and
    immutable. A Character works out the final scores from these plus every
    increase its effects record (Model/AbilityIncreases.py) whenever they're
    read, so nothing ever writes into these. To change a score, assign a new
    one: `character.base_abilities = character.base_abilities.with_scores(
    strength=16)`."""

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
        self._scores = MappingProxyType(
            {
                Ability.STRENGTH: strength,
                Ability.DEXTERITY: dexterity,
                Ability.CONSTITUTION: constitution,
                Ability.INTELLIGENCE: intelligence,
                Ability.WISDOM: wisdom,
                Ability.CHARISMA: charisma,
            }
        )

    def get_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_modifier(self, ability: Ability) -> int:
        return ability_modifier(self.get_score(ability))

    def with_scores(self, **scores: int) -> "AbilityScores":
        """A copy with some scores replaced, e.g. `with_scores(strength=16)`.
        A plain AbilityScores: the replaced scores needn't fit the standard
        array or point buy any more."""
        current = {
            ability.value.lower(): self.get_score(ability) for ability in Ability
        }
        unknown = set(scores) - set(current)
        if unknown:
            raise ValueError(f"Unknown abilities: {sorted(unknown)}")
        return AbilityScores(**{**current, **scores})

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
        provided_values = [
            strength,
            dexterity,
            constitution,
            intelligence,
            wisdom,
            charisma,
        ]
        if sorted(provided_values) != sorted(STANDARD_ARRAY):
            array = ", ".join(str(score) for score in STANDARD_ARRAY)
            raise ValueError(
                f"StandardArrayAbilityScores must use the standard array values: {array}"
            )
        super().__init__(
            strength, dexterity, constitution, intelligence, wisdom, charisma
        )


class PointBuyAbilityScores(AbilityScores):
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
            if not (POINT_BUY_MIN_SCORE <= score <= POINT_BUY_MAX_SCORE):
                raise ValueError(
                    f"Point Buy {ability.name.title()} score must be between "
                    f"{POINT_BUY_MIN_SCORE} and {POINT_BUY_MAX_SCORE}, got {score}."
                )

        spent = sum(point_buy_cost(score) for score in scores.values())
        if spent != POINT_BUY_BUDGET:
            raise ValueError(
                f"Point Buy scores must spend exactly {POINT_BUY_BUDGET} points, "
                f"got {spent}."
            )

        super().__init__(
            strength, dexterity, constitution, intelligence, wisdom, charisma
        )
