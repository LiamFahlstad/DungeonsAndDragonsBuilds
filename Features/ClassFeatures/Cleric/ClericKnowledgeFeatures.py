from Definitions import Ability, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillProficiencyChoice, SkillExpertiseChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock

CLERIC_HIT_DIE = 8


class BlessingsOfKnowledge(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(name="Blessings of Knowledge", origin="Knowledge Domain Cleric Level 3")
        allowed_skills = [
            Skill.ARCANA,
            Skill.HISTORY,
            Skill.NATURE,
            Skill.RELIGION,
        ]
        self._proficiency_choice = SkillProficiencyChoice(
            [skill_1, skill_2],
            allowed_skills,
            count=2,
            error_prefix="Blessings of Knowledge",
        )
        self._expertise_choice = SkillExpertiseChoice(
            [skill_1, skill_2],
            allowed_skills,
            count=2,
            error_prefix="Blessings of Knowledge",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._proficiency_choice.apply(character_stat_block)
        self._expertise_choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with one type of Artisan's Tools of your choice and in two of the following skills of your choice: Arcana, History, Nature, or Religion. You have Expertise in those two skills."
        return description


class KnowledgeDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Knowledge Domain Spells", origin="Knowledge Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Cleric level specified in the Knowledge Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class MindMagic(Feature):
    def __init__(self):
        super().__init__(name="Mind Magic", origin="Knowledge Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to manifest your magical knowledge. Choose one spell from the Divination school on the Knowledge Domain Spells table that you have prepared. As part of that action, you cast that spell without expending a spell slot or needing Material components."
        return description


class UnfetteredMind(Feature):
    def __init__(self):
        super().__init__(
            name="Unfettered Mind", origin="Knowledge Domain Cleric Level 6"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        # Check if already has Intelligence saving throw proficiency
        if not character_stat_block.saving_throws.is_proficient(Ability.INTELLIGENCE):
            character_stat_block.add_proficiency_in_saving_throw(Ability.INTELLIGENCE)
        else:
            # If already proficient in Intelligence, find the first ability not proficient and add it
            abilities = [Ability.STRENGTH, Ability.DEXTERITY, Ability.CONSTITUTION,
                        Ability.WISDOM, Ability.CHARISMA]
            for ability in abilities:
                if not character_stat_block.saving_throws.is_proficient(ability):
                    character_stat_block.add_proficiency_in_saving_throw(ability)
                    break

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain telepathy out to 60 feet. When you use this telepathy, you can simultaneously contact a number of creatures equal to your Wisdom modifier (minimum of one).\n"
            "Additionally, you gain proficiency in Intelligence saving throws. If you already have this proficiency, you instead gain saving throw proficiency with one ability in which you lack it."
        )
        return description


class DivineForeknowledge(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Foreknowledge", origin="Knowledge Domain Cleric Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Bonus Action, you magically expand your mind to the future. For 1 hour, you have Advantage on D20 Tests. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of this feature by expending a level 6+ spell slot (no action required)."
        return description
