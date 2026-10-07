from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from CharacterContent.Features.Core.Improvements import (
    SavingThrowProficiencyOrAlternative,
    SkillExpertiseChoice,
    SkillProficiencyChoice,
)
from Core.Definitions import Ability, Skill
from Model.Effects import Effects
from Model.View import CharacterView


class BlessingsOfKnowledge(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(
            name="Blessings of Knowledge",
            origin="Knowledge Domain Cleric Level 3",
            skippable_in_concise=True,
        )
        self._skill_1 = skill_1
        self._skill_2 = skill_2
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

    def apply(self, effects: Effects):
        self._proficiency_choice.apply(effects)
        self._expertise_choice.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        description = f"You gain proficiency with one type of Artisan's Tools of your choice and in {self._skill_1.value} and {self._skill_2.value}. You have Expertise in those two skills."
        return description


class KnowledgeDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Knowledge Domain Spells", origin="Knowledge Domain Cleric Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = "When you reach a Cleric level specified in the Knowledge Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class MindMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Mind Magic",
            origin="Knowledge Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION),
        )

    def get_description(self, character: CharacterView) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to manifest your magical knowledge. Choose one spell from the Divination school on the Knowledge Domain Spells table that you have prepared. As part of that action, you cast that spell without expending a spell slot or needing Material components."
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("What", "Cast Divination spell from Knowledge Domain table"),
            ("Trigger", "Magic action, Channel Divinity"),
            ("Components", "None (Material components waived)"),
            ("Cost", "No spell slot required"),
            ("Special", "Spell must be prepared"),
        ]


class UnfetteredMind(Feature):
    def __init__(self):
        super().__init__(
            name="Unfettered Mind",
            origin="Knowledge Domain Cleric Level 6",
            skippable_in_concise=False,
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["buff", "utility"],
        )

    def apply(self, effects: Effects):
        # Intelligence, or - if already proficient - the first ability that isn't.
        SavingThrowProficiencyOrAlternative(
            Ability.INTELLIGENCE,
            [
                Ability.STRENGTH,
                Ability.DEXTERITY,
                Ability.CONSTITUTION,
                Ability.WISDOM,
                Ability.CHARISMA,
            ],
        ).apply(effects)

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain telepathy out to 60 feet. When you use this telepathy, you can simultaneously contact a number of creatures equal to your Wisdom modifier (minimum of one).\n"
            "Additionally, you gain proficiency in Intelligence saving throws. If you already have this proficiency, you instead gain saving throw proficiency with one ability in which you lack it."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class DivineForeknowledge(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Foreknowledge",
            origin="Knowledge Domain Cleric Level 17",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Hour"
            ),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "As a Bonus Action, you magically expand your mind to the future. For 1 hour, you have Advantage on D20 Tests. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of this feature by expending a level 6+ spell slot (no action required)."
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("What", "Gain Advantage on all D20 Tests"),
            ("Trigger", "Bonus Action"),
            ("Duration", "1 hour"),
            ("Recharge", "Long Rest"),
            ("Alternative", "Expend level 6+ spell slot (no action)"),
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
