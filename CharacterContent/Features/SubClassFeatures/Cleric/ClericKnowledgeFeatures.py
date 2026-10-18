from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from Model.Content.Improvements import (
    SavingThrowProficiencyOrAlternative,
    SkillExpertiseChoice,
    SkillProficiencyChoice,
)
from Core.Definitions import Ability, Skill
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class BlessingsOfKnowledge(Feature):
    SKILL_POOL = [
        Skill.ARCANA,
        Skill.HISTORY,
        Skill.NATURE,
        Skill.RELIGION,
    ]

    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(
            name="Blessings of Knowledge",
            origin="Knowledge Domain Cleric Level 3",
            passive=True,
        )
        self._skill_1 = skill_1
        self._skill_2 = skill_2
        self._proficiency_choice = SkillProficiencyChoice(
            [skill_1, skill_2],
            self.SKILL_POOL,
            count=2,
            error_prefix="Blessings of Knowledge",
        )
        self._expertise_choice = SkillExpertiseChoice(
            [skill_1, skill_2],
            self.SKILL_POOL,
            count=2,
            error_prefix="Blessings of Knowledge",
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._proficiency_choice.apply(ledger_writer)
        self._expertise_choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Tools",
                        "Proficiency with one type of Artisan's Tools of your choice",
                    ),
                    (
                        "Skills",
                        f"Proficiency and Expertise in {self._skill_1.value} and {self._skill_2.value}",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = f"You gain proficiency with one type of Artisan's Tools of your choice and in {self._skill_1.value} and {self._skill_2.value}. You have Expertise in those two skills."
        return description


class KnowledgeDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Knowledge Domain Spells", origin="Knowledge Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    (
                        "3",
                        "Command, Comprehend Languages, Detect Magic, Detect Thoughts, Identify, Mind Spike",
                    ),
                    ("5", "Dispel Magic, Nondetection, Tongues"),
                    ("7", "Arcane Eye, Banishment, Confusion"),
                    ("9", "Legend Lore, Scrying, Synaptic Static"),
                ),
            ),
        ]

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

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Cost", "One use of Channel Divinity"),
                    (
                        "Spell",
                        "One Divination spell from the Knowledge Domain Spells table that you have prepared",
                    ),
                    (
                        "Effect",
                        "Cast it as part of the action, without expending a spell slot or needing Material components",
                    ),
                )
            ),
            Table(
                ("Cleric level", "Divination spells"),
                (
                    (
                        "3",
                        "Comprehend Languages, Detect Magic, Detect Thoughts, Identify, Mind Spike",
                    ),
                    ("5", "Tongues"),
                    ("7", "Arcane Eye"),
                    ("9", "Legend Lore, Scrying"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Magic action, you can expend one use of your Channel Divinity to manifest your magical knowledge. Choose one spell from the Divination school on the Knowledge Domain Spells table that you have prepared. As part of that action, you cast that spell without expending a spell slot or needing Material components."
        return description


class UnfetteredMind(Feature):
    def __init__(self):
        super().__init__(
            name="Unfettered Mind",
            origin="Knowledge Domain Cleric Level 6",
            passive=False,
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["buff", "utility"],
        )

    def apply(self, ledger_writer: LedgerWriter):
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
        ).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Telepathy",
                        "60 feet; contact a number of creatures at once equal to your Wisdom modifier (minimum of one)",
                    ),
                    (
                        "Saving throws",
                        "Proficiency in Intelligence saves, or, if you already have it, in one ability's saves you lack",
                    ),
                )
            ),
        ]

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
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Magically expand your mind to the future."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Duration", "1 hour"),
                    ("Effect", "Advantage on D20 Tests"),
                    (
                        "Restore",
                        "Expend a level 6+ spell slot (no action required) to regain the use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Bonus Action, you magically expand your mind to the future. For 1 hour, you have Advantage on D20 Tests. Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of this feature by expending a level 6+ spell slot (no action required)."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
