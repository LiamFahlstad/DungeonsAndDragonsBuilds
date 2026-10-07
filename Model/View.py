"""CharacterView: everything the Model's parts, formulas and content may read
from a character (Notes/engine-simplification-plan.md, section 2b).

Parts and content name this instead of Character, so they never import the
class that holds them. A bonus "equal to your Wisdom modifier" is a Formula,
evaluated against the finished character when it's read (see
Model/Bonuses.py); a feature's description reads its numbers the same way.
Character satisfies it structurally; Effects - the write-only record apply()
gets - deliberately does not, so a formula can never read a stat in the
middle of evaluation.

Keep CharacterView minimal: answers and sources only, never a part. A new
member is a new thing every formula and description may depend on - add one
only when content reads it. The source reads (base scores, base speed, class
levels, fixed spell slots) are what the parts' resolvers need, since no part
holds a copy of a source.
"""

from typing import Callable, Optional, Protocol

from Core.Definitions import Ability, ArmorType, CharacterClass, Skill
from Model.ClassLevels import ClassLevels


class CharacterView(Protocol):
    # ── Sources ──────────────────────────────────────────────────────────

    @property
    def class_levels(self) -> ClassLevels: ...

    @property
    def fixed_spell_slots(self) -> dict[int, int]: ...

    def get_base_ability_score(self, ability: Ability) -> int: ...

    def get_base_speed(self) -> int: ...

    # ── Answers ──────────────────────────────────────────────────────────

    @property
    def character_level(self) -> int: ...

    def get_class_level(self, character_class: CharacterClass) -> int: ...

    def get_proficiency_bonus(self) -> int: ...

    def get_own_ability_score(self, ability: Ability) -> int: ...

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

    @property
    def has_shield_training(self) -> bool: ...

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool: ...

    def has_feature(self, feature_type: type) -> bool: ...

    # ── Spellcasting ─────────────────────────────────────────────────────

    def calculate_difficulty_class(self) -> int: ...

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int: ...

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int: ...


# A value that depends on other stats, worked out when it's read.
Formula = Callable[[CharacterView], int]

# A bonus: a flat number, or a Formula worked out when it's read.
Value = int | Formula
