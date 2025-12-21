from typing import Optional
from Definitions import Ability, Skill, CharacterClass
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from Utils.CharacterSheetUtils import write_table, write_separator


class CharacterStatBlock:
    def __init__(
        self,
        name: str,
        character_subclass: str,
        starter_class: CharacterClass,
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
        self.starter_class = starter_class
        self.level_per_class = level_per_class
        self.abilities = abilities
        self.skills = skills
        self.combat = combat
        self.saving_throws = saving_throws
        self.spell_casting_ability = spell_casting_ability
        self.spell_slots = spell_slots

        self.combat.initiative_bonus = self.abilities.get_modifier(Ability.DEXTERITY)

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

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
            starter_class=self.starter_class,
            level_per_class=self.level_per_class,
            constitution_modifier=constitution_modifier,
        )

    def calculate_armor_class(self) -> int:
        return self.combat.armor_class

    def calculate_spell_save_dc(self) -> int:
        if self.spell_casting_ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        spellcasting_modifier = self.get_ability_modifier(self.spell_casting_ability)
        return 8 + self.get_proficiency_bonus() + spellcasting_modifier

    def calculate_spell_attack_bonus(self) -> int:
        if self.spell_casting_ability is None:
            raise ValueError("Character does not have a spell casting ability.")
        spellcasting_modifier = self.get_ability_modifier(self.spell_casting_ability)
        return self.get_proficiency_bonus() + spellcasting_modifier

    def get_spell_slots(self) -> dict[int, int]:
        if self.spell_slots is None:
            raise ValueError("Character does not have spell slots.")
        return self.spell_slots
