"""The Protocols the Model is written against (L1 in
Notes/model-refactor-plan.md, section 2a). Parts name these instead of
Character, so a part never imports the class that imports it.

StatView is everything a formula may read: a bonus "equal to your Wisdom
modifier" is a Formula, evaluated against the finished character when it's
read (see Model/Bonuses.py). Character satisfies it structurally; Effects -
the write-only record apply() gets - deliberately does not, so a formula can
never read a stat in the middle of evaluation.

Keep StatView minimal: answers only (numbers, booleans), never a part. A new
member is a new thing every formula may depend on.
"""

from typing import Callable, Optional, Protocol

from Core.Definitions import Ability, ArmorType, CharacterClass, Skill


class StatView(Protocol):
    @property
    def character_level(self) -> int: ...

    def get_class_level(self, character_class: CharacterClass) -> int: ...

    def get_proficiency_bonus(self) -> int: ...

    def get_ability_modifier(self, ability: Ability) -> int: ...

    def get_strength_modifier(self) -> int: ...

    def get_dexterity_modifier(self) -> int: ...

    def get_constitution_modifier(self) -> int: ...

    def get_intelligence_modifier(self) -> int: ...

    def get_wisdom_modifier(self) -> int: ...

    def get_charisma_modifier(self) -> int: ...

    def is_proficient_in_skill(self, skill: Skill) -> bool: ...

    def get_skill_ability(self, skill: Skill) -> Ability: ...

    @property
    def is_wearing_armor(self) -> bool: ...

    @property
    def worn_armor_type(self) -> Optional[ArmorType]: ...

    @property
    def is_wielding_shield(self) -> bool: ...


# A value that depends on other stats, worked out when it's read.
Formula = Callable[[StatView], int]
