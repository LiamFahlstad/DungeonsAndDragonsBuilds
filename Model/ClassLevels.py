from typing import Optional

import attr

from Core.Definitions import CharacterClass


@attr.dataclass
class ClassLevels:
    """A character's classes: how many levels in each, the level-by-level
    pick history, the class taken first (the "base class" - grants starting
    equipment/gold and full saving throw proficiencies, see
    ClassProficiencies) and the subclass chosen for each class that has
    reached its subclass level.

    Built up by ClassBuilder.create() as each class builder grants into the
    character's CharacterSources.
    """

    base_class: Optional[CharacterClass] = None
    level_per_class: dict[CharacterClass, int] = attr.Factory(dict)
    # Which class a given total character level was taken in, e.g. {1:
    # FIGHTER, 2: FIGHTER, 3: WIZARD}. Reflects the actual level-by-level
    # pick history (including dips and resumed classes), not just the final
    # per-class totals in level_per_class.
    class_by_character_level: dict[int, CharacterClass] = attr.Factory(dict)
    # {class: subclass} for every class that has reached its subclass level,
    # in the order gained - character_subclass shows them joined with " / ".
    active_subclasses: dict[CharacterClass, str] = attr.Factory(dict)
    # The first subclass a class builder names, shown while no class has
    # reached its subclass level yet (a Fighter 1 already says "Champion").
    first_subclass: Optional[str] = None

    def copy(self) -> "ClassLevels":
        return attr.evolve(
            self,
            level_per_class=dict(self.level_per_class),
            class_by_character_level=dict(self.class_by_character_level),
            active_subclasses=dict(self.active_subclasses),
        )

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

    @property
    def character_subclass(self) -> Optional[str]:
        """Every class's subclass on a multiclass sheet ("Oath of Glory /
        Bladesinger"), not only the last builder's. Classes that haven't
        reached their subclass level are left out; if none has, the first
        subclass named is shown."""
        if self.active_subclasses:
            return " / ".join(self.active_subclasses.values())
        return self.first_subclass

    def add_subclass(
        self, character_class: CharacterClass, subclass: str, *, reached: bool
    ) -> None:
        """`reached`: the class's level grants subclass features (a Fighter 1
        dip has named its subclass but doesn't have it yet)."""
        if self.first_subclass is None:
            self.first_subclass = subclass
        if reached:
            self.active_subclasses[character_class] = subclass

    def get_class_level(self, character_class: CharacterClass) -> int:
        return self.level_per_class.get(character_class, 0)

    def record_class_level(
        self, character_level: int, character_class: CharacterClass
    ) -> None:
        self.class_by_character_level[character_level] = character_class

    def get_class_level_segments(self) -> list[tuple[int, int, CharacterClass]]:
        """Contiguous (start_level, end_level, class) ranges describing which
        class was being leveled at each total character level, in
        chronological order. A class taken again after a dip into another
        class (e.g. Artificer 1-7, Wizard 8, Artificer 9-15) appears as two
        separate segments rather than being merged into one."""
        segments: list[tuple[int, int, CharacterClass]] = []
        current_class = None
        start = None
        for level in range(1, self.character_level + 1):
            character_class = self.class_by_character_level.get(level)
            if character_class != current_class:
                if current_class is not None:
                    assert start is not None
                    segments.append((start, level - 1, current_class))
                current_class = character_class
                start = level
        if current_class is not None:
            assert start is not None
            segments.append((start, self.character_level, current_class))
        return segments
