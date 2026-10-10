"""A CharacterView with fixed answers, for unit-testing a part without a
Character: a part's resolvers take nothing but the view, so these tests need
no builder and no Character. Scores have no increases - own score, final
score and base score are the same number.

It answers what the parts read (scores, levels, proficiency bonus, base
speed, the Shield). Everything else a CharacterView offers raises, so a part
that starts reading it fails loudly instead of getting a made-up answer."""

from typing import NoReturn, Optional

from Core.Definitions import Ability, ArmorType, CharacterClass, Skill
from Core.Rules import ability_modifier
from Core.Weapons import WeaponTraits
from Model.ClassLevels import ClassLevels


def _not_answered(member: str) -> NoReturn:
    raise NotImplementedError(f"FakeView has no fixed answer for {member}.")


class FakeView:
    def __init__(
        self,
        scores: Optional[dict[Ability, int]] = None,
        class_levels: Optional[ClassLevels] = None,
        fixed_spell_slots: Optional[dict[int, int]] = None,
        base_speed: int = 30,
        proficiency_bonus: int = 2,
        is_wielding_shield: bool = False,
        has_shield_training: bool = False,
        untrained_armor: bool = False,
    ):
        self._scores = {ability: 10 for ability in Ability} | (scores or {})
        self.class_levels = class_levels or ClassLevels(
            base_class=CharacterClass.FIGHTER,
            level_per_class={CharacterClass.FIGHTER: 1},
        )
        self.fixed_spell_slots = fixed_spell_slots or {}
        self._base_speed = base_speed
        self._proficiency_bonus = proficiency_bonus
        self.is_wielding_shield = is_wielding_shield
        self.has_shield_training = has_shield_training
        self._untrained_armor = untrained_armor

    def get_base_ability_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_own_ability_score(self, ability: Ability) -> int:
        return self._scores[ability]

    def get_ability_modifier(self, ability: Ability) -> int:
        return ability_modifier(self._scores[ability])

    def get_strength_modifier(self) -> int:
        return self.get_ability_modifier(Ability.STRENGTH)

    def get_dexterity_modifier(self) -> int:
        return self.get_ability_modifier(Ability.DEXTERITY)

    def get_constitution_modifier(self) -> int:
        return self.get_ability_modifier(Ability.CONSTITUTION)

    def get_intelligence_modifier(self) -> int:
        return self.get_ability_modifier(Ability.INTELLIGENCE)

    def get_wisdom_modifier(self) -> int:
        return self.get_ability_modifier(Ability.WISDOM)

    def get_charisma_modifier(self) -> int:
        return self.get_ability_modifier(Ability.CHARISMA)

    @property
    def base_speed(self) -> int:
        return self._base_speed

    @property
    def character_level(self) -> int:
        return self.class_levels.character_level

    def get_class_level(self, character_class: CharacterClass) -> int:
        return self.class_levels.get_class_level(character_class)

    def get_proficiency_bonus(self) -> int:
        return self._proficiency_bonus

    def has_untrained_armor_disadvantage(self, ability: Ability) -> bool:
        return self._untrained_armor and ability in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        )

    # ── Not answered: no part reads these ───────────────────────────────

    def is_proficient_in_skill(self, skill: Skill) -> bool:
        _not_answered("is_proficient_in_skill")

    def get_skill_ability(self, skill: Skill) -> Ability:
        _not_answered("get_skill_ability")

    @property
    def is_wearing_armor(self) -> bool:
        _not_answered("is_wearing_armor")

    @property
    def worn_armor_type(self) -> Optional[ArmorType]:
        _not_answered("worn_armor_type")

    def has_feature(self, feature_type: type) -> bool:
        _not_answered("has_feature")

    def is_proficient_with_weapon(self, weapon: WeaponTraits) -> bool:
        _not_answered("is_proficient_with_weapon")

    def get_weapon_attack_bonuses(self, weapon: WeaponTraits) -> list[tuple[int, str]]:
        _not_answered("get_weapon_attack_bonuses")

    def get_weapon_damage_bonuses(self, weapon: WeaponTraits) -> list[tuple[int, str]]:
        _not_answered("get_weapon_damage_bonuses")

    def calculate_difficulty_class(self) -> int:
        _not_answered("calculate_difficulty_class")

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int:
        _not_answered("calculate_difficulty_class_for_ability")

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        _not_answered("calculate_attack_bonus_for_ability")
