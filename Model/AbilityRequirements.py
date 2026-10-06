import attr

from Core.Definitions import Ability
from Core.Rules import MULTICLASS_MIN_SCORE
from Model.Contracts import StatView
from Model.Recorder import Recorder, records


@attr.s(frozen=True, auto_attribs=True)
class AbilityMinimum:
    """`ability` must be at least `min_score`, because of `reason`."""

    ability: Ability
    min_score: int
    reason: str

    def sort_key(self) -> tuple[int, int, str]:
        """Ability order, then minimum, then reason."""
        return list(Ability).index(self.ability), self.min_score, self.reason


class AbilityRequirements(Recorder):
    """Ability score minimums recorded by features (e.g. an armor's Strength
    requirement) and checked once everything has applied - so what meets a
    requirement may be granted before or after the one that imposes it. Also
    checks the multiclass ability-score prerequisites, which are minimums of
    the same shape (MULTICLASS_MIN_SCORE+ in one of a class's prerequisite abilities) fixed by
    the character's classes rather than recorded by a feature.

    Merge rule: every minimum must hold (a set). They're checked in a fixed
    order (Ability, minimum, reason), so the first failure reported doesn't
    depend on the order they were recorded in."""

    def __init__(self):
        # Checked by validate() once everything has applied, against the
        # character's own score.
        self._minimums: list[AbilityMinimum] = []

    @records
    def add_ability_requirement(
        self, ability: Ability, min_score: int, reason: str
    ) -> None:
        self._minimums.append(AbilityMinimum(ability, min_score, reason))

    def validate(self, view: StatView) -> None:
        for minimum in sorted(self._minimums, key=AbilityMinimum.sort_key):
            if view.get_own_ability_score(minimum.ability) < minimum.min_score:
                raise ValueError(
                    f"{minimum.ability.value} score must be at least "
                    f"{minimum.min_score} ({minimum.reason})."
                )
        self._validate_multiclass_prerequisites(view)

    def _validate_multiclass_prerequisites(self, view: StatView) -> None:
        """A multiclass character needs MULTICLASS_MIN_SCORE+ in the prerequisite abilities of
        every class it has. Checked on the character's own final scores
        (equipment bonuses don't count) - the engine has no per-level score
        history, so this is the end-of-build approximation of "at the time
        you multiclass"."""
        class_levels = view.class_levels
        if len(class_levels.level_per_class) < 2:
            return
        for character_class in class_levels.level_per_class:
            for group in character_class.multiclass_prerequisites:
                if not any(
                    view.get_own_ability_score(a) >= MULTICLASS_MIN_SCORE for a in group
                ):
                    needed = " or ".join(a.value for a in group)
                    raise ValueError(
                        f"Multiclassing into or out of {character_class.value} "
                        f"requires {needed} {MULTICLASS_MIN_SCORE}+."
                    )
