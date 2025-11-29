from typing import Optional
from Definitions import Ability, Skill, CharacterClass
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from Utils import write_table, write_separator


class CharacterStatBlock:
    def __init__(
        self,
        name: str,
        character_class: CharacterClass,
        character_subclass: str,
        level: int,
        abilities: AbilitiesStatBlock,
        skills: SkillsStatBlock,
        combat: CombatStatBlock,
        saving_throws: SavingThrowsStatBlock,
        spell_casting_ability: Optional[Ability] = None,
        spell_slots: Optional[dict[int, int]] = None,
    ):
        self.name = name
        self.character_class = character_class
        self.character_subclass = character_subclass
        self.level = level
        self.abilities = abilities
        self.skills = skills
        self.combat = combat
        self.saving_throws = saving_throws
        self.spell_casting_ability = spell_casting_ability
        self.spell_slots = spell_slots

        self.combat.initiative_bonus = self.abilities.get_modifier(Ability.DEXTERITY)

    def get_proficiency_bonus(self) -> int:
        return 2 + (self.level - 1) // 4

    def get_ability_score(self, ability: Ability) -> int:
        return self.abilities.get_score(ability)

    def get_ability_modifier(self, ability: Ability) -> int:
        return self.abilities.get_modifier(ability)

    def is_proficient_in_skill(self, skill: Skill) -> bool:
        return self.skills.is_proficient(skill)

    def get_skill_ability(self, skill: Skill) -> Ability:
        return self.skills.get_skill_ability(skill)

    def get_skill_modifier(self, skill: Skill) -> int:
        base_modifier = self.get_ability_modifier(self.get_skill_ability(skill))
        proficiency_bonus = (
            self.get_proficiency_bonus() if self.is_proficient_in_skill(skill) else 0
        )
        bonus = self.skills.bonuses.get(skill, 0)
        return base_modifier + proficiency_bonus + bonus

    def is_proficient_in_saving_throw(self, ability: Ability) -> bool:
        return self.saving_throws.is_proficient(ability)

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
        return self.combat.calculate_hit_points(self.level, constitution_modifier)

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

    def save_character_to_file(self, file):
        write_separator(file, "General Info")
        write_table(
            headers=["Field", "Value"],
            rows=[
                ["Name", self.name],
                ["Level", self.level],
                ["Character Class", self.character_class.value],
                ["Character Subclass", self.character_subclass],
                ["Proficiency Bonus", self.get_proficiency_bonus()],
            ],
            file=file,
        )

        file.write("\n")
        write_separator(file, "Combat Stats")
        write_table(
            headers=["Field", "Value"],
            rows=[
                ["Max Hit Points", self.calculate_hit_points()],
                ["Armor Class", self.calculate_armor_class()],
                ["Initiative", f"d20 + {self.combat.initiative}"],
                ["Speed (ft)", self.combat.speed],
                ["Size", self.combat.size.value],
            ],
            file=file,
        )

        file.write("\n")
        write_separator(file, "Abilities")
        headings = ["Ability", "Score", "Modifier", "Saving Throw", "Proficient"]
        write_table(
            headings,
            [
                [
                    ability.value,
                    self.get_ability_score(ability),
                    self.get_ability_modifier(ability),
                    self.get_saving_throw_modifier(ability),
                    "Yes" if self.is_proficient_in_saving_throw(ability) else "No",
                ]
                for ability in Ability
            ],
            file,
        )
        file.write("\n")
        write_separator(file, "Skills")
        headings = ["Skill", "Modifier", "Proficient", "Ability", "RollCondition"]
        write_table(
            headings,
            [
                [
                    skill.value,
                    self.get_skill_modifier(skill),
                    "Yes" if self.is_proficient_in_skill(skill) else "No",
                    self.get_skill_ability(skill).value,
                    self.get_skill_roll_condition(skill).value,
                ]
                for skill in Skill
            ],
            file,
        )
