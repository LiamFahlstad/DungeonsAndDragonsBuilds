import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from CharacterContent.Features.Core.Improvements import (
    JackOfAllTradesBonus,
    SkillExpertiseChoice,
)
from Core.Definitions import Skill
from Model.Character import Character
from Model.Effects import Effects
from Utils import StringUtils
from Core.Rules import ALL_LEVELS, MAX_ABILITY_MODIFIER


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Bard Level 1")

    def get_description(self, character: Character) -> str:
        description = (
            "Spellcasting:\n"
            "    * Replacing cantrips: Whenever you gain a Bard level\n"
            "    * Replacing prepared spells: Whenever you gain a Bard level\n"
            "    * Spellcasting Ability: Charisma\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
        )
        return description

    def regained_on(self, character: Character) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class BardicInspiration(Feature):
    def __init__(self):
        super().__init__(
            name="Bardic Inspiration",
            origin="Bard Level 1",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Hour", range="60 Feet"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Charisma modifier.",
            ),
        )

    def get_description(self, character: Character) -> str:
        description = (
            "You can supernaturally inspire others through words, music, or dance. This inspiration is represented by your Bardic Inspiration die.\n"
            "    * Using Bardic Inspiration: As a Bonus Action, you can inspire another creature within 60 feet of yourself who can see or hear you. That creature gains one of your Bardic Inspiration dice. A creature can have only one Bardic Inspiration die at a time. Once within the next hour when the creature fails a D20 Test, the creature can roll the Bardic Inspiration die and add the number rolled to the d20, potentially turning the failure into a success. A Bardic Inspiration die is expended when it's rolled.\n"
            "    * Number of Uses. You can confer a Bardic Inspiration die a number of times equal to your Charisma modifier, and you regain all expended uses when you finish a Long Rest.\n"
            "    * At Higher Levels. Your Bardic Inspiration die changes when you reach certain Bard levels, as shown in the Bardic Die column of the Bard Features table. The die becomes a d8 at level 5, a d10 at level 10, and a d12 at level 15.\n"
        )
        return description

    def get_resource_tiles(
        self, character: Character
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        die_by_level = {}
        for level in ALL_LEVELS:
            if level >= 15:
                die_by_level[level] = "1d12"
            elif level >= 10:
                die_by_level[level] = "1d10"
            elif level >= 5:
                die_by_level[level] = "1d8"
            else:
                die_by_level[level] = "1d6"
        steps = [
            (f"Lv {level_range}", value)
            for level_range, value in StringUtils.compress_level_progression(
                die_by_level
            )
        ]
        return [("Bardic Inspiration Die", steps)]

    def regained_on(self, character: Character) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: Character) -> int:
        return character.get_charisma_modifier()

    def get_table_description(self, character: Character) -> list[tuple[str, str]]:
        charisma_modifier = character.get_charisma_modifier()
        bard_level = character.get_class_level(Definitions.CharacterClass.BARD)
        if bard_level >= 15:
            die = "d12"
        elif bard_level >= 10:
            die = "d10"
        elif bard_level >= 5:
            die = "d8"
        else:
            die = "d6"
        return [
            ("Action", "Bonus Action"),
            ("Range", "60 feet"),
            ("Inspiration Die", die),
            ("Uses", f"{max(1, charisma_modifier)} per Long Rest"),
            ("Duration", "1 hour (until creature fails a D20 Test)"),
            (
                "Effect",
                "Creature adds die result to d20 to potentially turn failure into success",
            ),
        ]

    def target(self, character: Character) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ExpertiseLevel1(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(
            name="Expertise", origin="Bard Level 1", skippable_in_concise=True
        )
        self._choice = SkillExpertiseChoice(
            [skill_1, skill_2], list(Skill), count=2, error_prefix="Bard Expertise"
        )

    def apply(self, effects: Effects):
        self._choice.apply(effects)

    def get_description(self, character: Character) -> str:
        description = "You gain proficiency with two skills of your choice. When you make an ability check using a proficient skill, you add double your Proficiency Bonus to the check instead of adding the Proficiency Bonus once."
        return description


class ExpertiseLevel9(Feature):
    def __init__(self, skill_1: Skill, skill_2: Skill):
        super().__init__(
            name="Expertise", origin="Bard Level 9", skippable_in_concise=True
        )
        self._choice = SkillExpertiseChoice(
            [skill_1, skill_2], list(Skill), count=2, error_prefix="Bard Expertise"
        )

    def apply(self, effects: Effects):
        self._choice.apply(effects)

    def get_description(self, character: Character) -> str:
        description = "You gain proficiency with two more skills of your choice. When you make an ability check using a proficient skill, you add double your Proficiency Bonus to the check instead of adding the Proficiency Bonus once."
        return description


class JackOfAllTrades(Feature):
    def __init__(self):
        super().__init__(
            name="Jack of All Trades",
            origin="Bard Level 2",
            skippable_in_concise=True,
            usage_tags=["buff"],
        )
        self._bonus = JackOfAllTradesBonus()

    def apply(self, effects: Effects):
        self._bonus.apply(effects)

    def get_description(self, character: Character) -> str:
        description = "You can add half your Proficiency Bonus (round up) to any ability check you make that doesn't already use your Proficiency Bonus. In addition, you can use this bonus when you use a weapon and add your Proficiency Bonus to the damage roll."
        return description


class FontOfInspiration(Feature):
    def __init__(self):
        super().__init__(name="Font of Inspiration", origin="Bard Level 5")

    def get_description(self, character: Character) -> str:
        description = (
            "You now regain all your expended uses of Bardic Inspiration when you finish a Short or Long Rest.\n"
            "In addition, you can expend a spell slot (no action required) to regain one expended use of Bardic Inspiration."
        )
        return description

    def get_table_description(self, character: Character) -> list[tuple[str, str]]:
        return [
            ("Regain Uses On", "Short or Long Rest"),
            ("Alternative Cost", "1 spell slot (no action required)"),
        ]

    def regained_on(self, character: Character) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST


class Countercharm(Feature):
    def __init__(self):
        super().__init__(
            name="Countercharm",
            origin="Bard Level 7",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
        )

    def get_description(self, character: Character) -> str:
        description = "You can use musical notes or words of power to disrupt mind-influencing effects. If you or a creature within 30 feet of you fails a saving throw against an effect that applies the Charmed or Frightened condition, you can take a Reaction to cause the save to be rerolled, and the new roll has Advantage."
        return description

    def get_table_description(self, character: Character) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Creature within 30 feet fails save vs Charmed or Frightened"),
            ("Action", "Reaction"),
            ("Effect", "Reroll save with Advantage"),
        ]

    def target(self, character: Character) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MagicalSecrets(Feature):
    def __init__(self):
        super().__init__(name="Magical Secrets", origin="Bard Level 10")

    def get_description(self, character: Character) -> str:
        description = "You've learned secrets from various magical traditions. Whenever you reach a Bard level (including this level) and the Prepared Spells number in the Bard Features table increases, you can choose any of your new prepared spells from the Bard, Cleric, Druid, and Wizard spell lists, and the chosen spells count as Bard spells for you (see a class's section for its spell list). In addition, whenever you replace a spell prepared for this class, you can replace it with a spell from those lists."
        return description


class SuperiorInspiration(Feature):
    def __init__(self):
        super().__init__(name="Superior Inspiration", origin="Bard Level 18")

    def get_description(self, character: Character) -> str:
        description = "When you roll Initiative, you regain expended uses of Bardic Inspiration until you have two if you have fewer than that."
        return description

    def regained_on(self, character: Character) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL


class WordsOfCreation(Feature):
    def __init__(self):
        super().__init__(
            name="Words of Creation",
            origin="Bard Level 20",
            activation=FeatureActivation(range="10 Feet"),
        )

    def get_description(self, character: Character) -> str:
        description = "You have mastered two of the Words of Creation: the words of life and death. You therefore always have the Power Word: Heal and Power Word: Kill spells prepared. When you cast either spell, you can target a second creature with it if that creature is within 10 feet of the first target."
        return description

    def target(self, character: Character) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE
