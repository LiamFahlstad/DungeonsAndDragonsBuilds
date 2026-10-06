import attr

from Core.Definitions import Ability
from Core.Rules import (
    POINT_BUY_BUDGET,
    POINT_BUY_MAX_SCORE,
    POINT_BUY_MIN_SCORE,
    STANDARD_ARRAY,
    ability_modifier,
    point_buy_cost,
)

# The abilities a spellcasting class can cast with.
_SPELLCASTING_ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)


@attr.s(frozen=True, auto_attribs=True)
class AbilityScores:
    """The player's ability scores before any increase: a source, and
    immutable. A Character works out the final scores from these plus every
    increase its effects record (Model/AbilityIncreases.py) whenever they're
    read, so nothing ever writes into these. To change a score, assign a new
    one: `character.base_abilities = character.base_abilities.with_scores(
    strength=16)`."""

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    def get_score(self, ability: Ability) -> int:
        scores = {
            Ability.STRENGTH: self.strength,
            Ability.DEXTERITY: self.dexterity,
            Ability.CONSTITUTION: self.constitution,
            Ability.INTELLIGENCE: self.intelligence,
            Ability.WISDOM: self.wisdom,
            Ability.CHARISMA: self.charisma,
        }
        return scores[ability]

    def get_modifier(self, ability: Ability) -> int:
        return ability_modifier(self.get_score(ability))

    def with_scores(self, **scores: int) -> "AbilityScores":
        """A copy with some scores replaced, e.g. `with_scores(strength=16)`.
        A plain AbilityScores: the replaced scores needn't fit the standard
        array or point buy any more."""
        return AbilityScores(**{**attr.asdict(self), **scores})

    def get_ability_with_highest_modifier(self) -> Ability:
        """Ties go to the first in Ability order."""
        return max(Ability, key=self.get_modifier)

    def get_spell_casting_ability_with_highest_modifier(self) -> Ability:
        """The best of Intelligence, Wisdom and Charisma (ties go to the first
        of those)."""
        return max(_SPELLCASTING_ABILITIES, key=self.get_modifier)


@attr.s(frozen=True, auto_attribs=True)
class StandardArrayAbilityScores(AbilityScores):
    """Scores assigned from the standard array: 15, 14, 13, 12, 10 and 8,
    each used once."""

    def __attrs_post_init__(self) -> None:
        scores = [self.get_score(ability) for ability in Ability]
        if sorted(scores) != sorted(STANDARD_ARRAY):
            array = ", ".join(str(score) for score in STANDARD_ARRAY)
            raise ValueError(
                f"StandardArrayAbilityScores must use the standard array values: {array}"
            )


@attr.s(frozen=True, auto_attribs=True)
class PointBuyAbilityScores(AbilityScores):
    """Scores bought with exactly POINT_BUY_BUDGET points, each between
    POINT_BUY_MIN_SCORE and POINT_BUY_MAX_SCORE."""

    def __attrs_post_init__(self) -> None:
        for ability in Ability:
            score = self.get_score(ability)
            if not (POINT_BUY_MIN_SCORE <= score <= POINT_BUY_MAX_SCORE):
                raise ValueError(
                    f"Point Buy {ability.name.title()} score must be between "
                    f"{POINT_BUY_MIN_SCORE} and {POINT_BUY_MAX_SCORE}, got {score}."
                )

        spent = sum(point_buy_cost(self.get_score(ability)) for ability in Ability)
        if spent != POINT_BUY_BUDGET:
            raise ValueError(
                f"Point Buy scores must spend exactly {POINT_BUY_BUDGET} points, "
                f"got {spent}."
            )
