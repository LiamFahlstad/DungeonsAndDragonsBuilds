from typing import Optional

import Definitions
from Definitions import Ability, CharacterClass, Skill
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock


class CharacterStatBlock:
    def __init__(
        self,
        name: str,
        character_subclass: str,
        base_class: CharacterClass,
        level_per_class: dict[CharacterClass, int],
        abilities: AbilitiesStatBlock,
        skills: SkillsStatBlock,
        combat: CombatStatBlock,
        saving_throws: SavingThrowsStatBlock,
        spell_casting_ability: Optional[Ability] = None,
        spell_slots: Optional[dict[int, int]] = None,
    ):
        self.name = name
        self.character_subclass = character_subclass
        self.base_class = base_class
        self.level_per_class = level_per_class
        self.abilities = abilities
        self.skills = skills
        self.combat = combat
        self.saving_throws = saving_throws
        self.spell_casting_ability = spell_casting_ability
        self.spell_slots = spell_slots
        self.pact_magic_slots: dict[int, int] = {}
        self._caster_registry: dict = {}
        self.initiative_proficiency = False
        self.initiative_roll_condition = Definitions.DiceRollCondition.NEUTRAL
        # (source, slots) pairs; every creature carries 3 slots on their person
        self.carrying_capacity_sources: list[tuple[str, int]] = [("Person", 3)]

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

    @property
    def initiative(self) -> int:
        modifier = self.abilities.get_modifier(Ability.DEXTERITY)
        if self.initiative_proficiency:
            modifier += self.get_proficiency_bonus()
        return modifier

    def get_carrying_capacity(self) -> int:
        """Returns the total carrying capacity in item slots (base 3 + bonuses)."""
        return sum(slots for _, slots in self.carrying_capacity_sources)

    def _require_spell_casting_ability(self) -> Ability:
        if self.spell_casting_ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        return self.spell_casting_ability

    def add_initiative_proficiency(self):
        self.initiative_proficiency = True

    def add_initiative_roll_condition(self, condition: Definitions.DiceRollCondition):
        self.initiative_roll_condition = condition

    def get_class_level(self, character_class: CharacterClass) -> int:
        return self.level_per_class.get(character_class, 0)

    def get_proficiency_bonus(self) -> int:
        return 2 + (self.character_level - 1) // 4

    def get_ability_score(self, ability: Ability) -> int:
        return self.abilities.get_score(ability)

    def get_ability_modifier(self, ability: Ability) -> int:
        return self.abilities.get_modifier(ability)

    def is_proficient_in_skill(self, skill: Skill) -> bool:
        return self.skills.is_proficient(skill)

    def has_expertise_in_skill(self, skill: Skill) -> bool:
        return self.skills.has_expertise(skill)

    def get_skill_ability(self, skill: Skill) -> Ability:
        return self.skills.get_skill_ability(skill)

    def get_skill_modifier(self, skill: Skill) -> int:
        ability_modifier = self.get_ability_modifier(self.get_skill_ability(skill))
        if self.has_expertise_in_skill(skill):
            proficiency_bonus = self.get_proficiency_bonus() * 2
        elif self.is_proficient_in_skill(skill):
            proficiency_bonus = self.get_proficiency_bonus()
        else:
            proficiency_bonus = 0
        bonus = self.skills.bonuses.get(skill, 0)
        return ability_modifier + proficiency_bonus + bonus

    def get_skill_bonus(self, skill: Skill) -> int:
        return self.skills.bonuses.get(skill, 0)

    def get_skill_bonus_sources(self, skill: Skill) -> list[tuple[int, str]]:
        return self.skills.get_bonus_sources(skill)

    def is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_proficient(ability)

    def add_proficiency_in_saving_throw(self, ability: Ability) -> None:
        self.saving_throws.add_proficiency(ability)

    def has_advantage_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_advantaged(ability)

    def add_advantage_in_saving_throw(self, ability: Ability) -> None:
        self.saving_throws.add_advantage(ability)

    def get_skill_roll_condition(self, skill: Skill):
        return self.skills.get_roll_condition(skill)

    def set_skill_roll_condition(
        self, skill: Skill, condition: Definitions.DiceRollCondition
    ):
        self.skills.set_roll_condition(skill, condition)

    def get_saving_throw_modifier(self, ability: Ability) -> int:
        base_modifier = self.get_ability_modifier(ability)
        proficiency_bonus = (
            self.get_proficiency_bonus()
            if self.is_proficient_in_saving_throw(ability)
            else 0
        )
        return base_modifier + proficiency_bonus

    def calculate_hit_points(self) -> int:
        constitution_modifier = self.get_ability_modifier(Ability.CONSTITUTION)
        return self.combat.calculate_hit_points(
            base_class=self.base_class,
            level_per_class=self.level_per_class,
            constitution_modifier=constitution_modifier,
        )

    def calculate_armor_class(self) -> int:
        ability_modifier = sum(
            self.get_ability_modifier(ability)
            for ability in self.combat.armor_class_abilities
        )
        return (
            self.combat.armor_class_base
            + ability_modifier
            + self.combat.armor_class_modifier
        )

    def get_spell_casting_ability(self) -> Ability:
        return self._require_spell_casting_ability()

    def calculate_difficulty_class(self) -> int:
        return self.calculate_difficulty_class_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_difficulty_class_for_ability(self, ability: Ability) -> int:
        modifier = self.get_ability_modifier(ability)
        return 8 + self.get_proficiency_bonus() + modifier

    def calculate_attack_bonus(self) -> int:
        return self.calculate_attack_bonus_for_ability(
            self._require_spell_casting_ability()
        )

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        ability_modifier = self.get_ability_modifier(ability)
        return self.get_proficiency_bonus() + ability_modifier

    def get_spell_slots(self) -> dict[int, int]:
        if self.spell_slots is None:
            raise ValueError("Character does not have spell slots.")
        return self.spell_slots
