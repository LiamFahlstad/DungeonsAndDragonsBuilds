from Core.Definitions import Ability
from Model.AbilityScores import AbilityScores
from Model.ClassLevels import ClassLevels
from Model.Recorder import Recorder, records


class AbilityRequirements(Recorder):
    """Ability score minimums recorded by features (e.g. an armor's Strength
    requirement) and checked once everything has applied - so what meets a
    requirement may be granted before or after the one that imposes it. Also
    checks the multiclass ability-score prerequisites, which are minimums of
    the same shape (13+ in one of a class's prerequisite abilities) fixed by
    the character's classes rather than recorded by a feature."""

    def __init__(self):
        # (ability, minimum score, reason) - checked by validate() once
        # everything has applied, against the character's own score.
        self._minimums: list[tuple[Ability, int, str]] = []

    @records
    def add_ability_requirement(
        self, ability: Ability, min_score: int, reason: str
    ) -> None:
        self._minimums.append((ability, min_score, reason))

    def validate(self, abilities: AbilityScores, class_levels: ClassLevels) -> None:
        for ability, min_score, reason in self._minimums:
            if abilities.get_own_score(ability) < min_score:
                raise ValueError(
                    f"{ability.value} score must be at least {min_score} ({reason})."
                )
        self._validate_multiclass_prerequisites(abilities, class_levels)

    def _validate_multiclass_prerequisites(
        self, abilities: AbilityScores, class_levels: ClassLevels
    ) -> None:
        """A multiclass character needs 13+ in the prerequisite abilities of
        every class it has. Checked on the character's own final scores
        (equipment bonuses don't count) - the engine has no per-level score
        history, so this is the end-of-build approximation of "at the time
        you multiclass"."""
        if len(class_levels.level_per_class) < 2:
            return
        for character_class in class_levels.level_per_class:
            for group in character_class.multiclass_prerequisites:
                if not any(abilities.get_own_score(a) >= 13 for a in group):
                    needed = " or ".join(a.value for a in group)
                    raise ValueError(
                        f"Multiclassing into or out of {character_class.value} "
                        f"requires {needed} 13+."
                    )
