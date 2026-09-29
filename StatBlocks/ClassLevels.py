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

    Built up by ClassBuilder.create() as each class builder's partial
    CharacterSheetData merges into the character's one CharacterSheetData
    (see merge), and shared - not copied - with the CharacterStatBlock built
    from that sheet, so both read the same levels, history and subclasses no
    matter which changed first.
    """

    base_class: Optional[CharacterClass] = None
    level_per_class: dict[CharacterClass, int] = attr.Factory(dict)
    # Which class a given total character level was taken in, e.g. {1:
    # FIGHTER, 2: FIGHTER, 3: WIZARD}. Reflects the actual level-by-level
    # pick history (including dips and resumed classes), not just the final
    # per-class totals in level_per_class.
    class_by_character_level: dict[int, CharacterClass] = attr.Factory(dict)
    # The sheet's current subclass display string, e.g. "Oath of Glory /
    # Bladesinger" once every multiclassed class that has one has reached its
    # subclass level - see ClassBuilder._update_subclass_name.
    character_subclass: Optional[str] = None
    # {class: subclass} for every class that has reached its subclass level,
    # in the order gained - character_subclass shows them joined with " / ".
    active_subclasses: dict[CharacterClass, str] = attr.Factory(dict)

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

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

    def merge(self, other: "ClassLevels") -> "ClassLevels":
        """A new ClassLevels combining `other` (a later class builder's
        partial ClassLevels) on top of self, matching
        CharacterSheetData.merge_with's per-field-kind rules: dicts combine
        with `other`'s entries winning on key collisions (so a later builder
        redeclaring an existing class states that class's final total level,
        e.g. a starter Paladin 1 resumed by a Paladin 19 builder ends at 19,
        not 20) and scalars are overwritten only when `other`'s value is
        actually set, so an untouched default never erases an earlier
        builder's value (e.g. a MulticlassBuilder, which never sets
        base_class, can't clear the character's starting class)."""
        return ClassLevels(
            base_class=(
                other.base_class if other.base_class is not None else self.base_class
            ),
            level_per_class={**self.level_per_class, **other.level_per_class},
            class_by_character_level={
                **self.class_by_character_level,
                **other.class_by_character_level,
            },
            character_subclass=other.character_subclass or self.character_subclass,
            active_subclasses={**self.active_subclasses, **other.active_subclasses},
        )
