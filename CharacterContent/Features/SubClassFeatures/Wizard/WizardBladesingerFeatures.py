from Core.Definitions import Skill, WIZARD_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import SkillProficiencyChoice, GrantWeaponProficiency
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class Bladesong(Feature):
    def __init__(self):
        super().__init__(
            name="Bladesong",
            origin="Bladesinger Wizard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph("Invoke an elven magic of blade and song."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Requirement", "You aren't wearing armor or using a Shield"),
                    (
                        "Duration",
                        "1 minute. Ends early if you're Incapacitated, don armor or a Shield, or attack with a weapon using two hands; dismiss it any time (no action required).",
                    ),
                    (
                        "Recharge",
                        "All uses on a Long Rest; one use when you use Arcane Recovery",
                    ),
                )
            ),
            Option(
                "While active",
                (
                    Facts(
                        (
                            (
                                "Agility",
                                "AC + Intelligence modifier (minimum +1), Speed +10 feet, and Advantage on Dexterity (Acrobatics) checks",
                            ),
                            (
                                "Bladework",
                                "Use Intelligence for the attack and damage rolls of weapons you're proficient with",
                            ),
                            (
                                "Focus",
                                "Add your Intelligence modifier to Constitution saves to maintain Concentration",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you invoke an elven magic called the Bladesong, provided you aren't wearing armor or using a Shield.\n"
            "The Bladesong lasts for 1 minute and ends early if you have the Incapacitated condition, if you don armor or a Shield, or if you use two hands to make an attack with a weapon. You can dismiss the Bladesong at any time (no action required).\n"
            "While the Bladesong is active, you gain the following benefits. You can invoke the Bladesong a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest. You regain one expended use when you use Arcane Recovery.\n"
            "    * Agility: You gain a bonus to your AC equal to your Intelligence modifier (minimum of +1), and your Speed increases by 10 feet. In addition, you have Advantage on Dexterity (Acrobatics) checks.\n"
            "    * Bladework: Whenever you attack with a weapon with which you have proficiency, you can use your Intelligence modifier for the attack and damage rolls instead of using Strength or Dexterity.\n"
            "    * Focus: When you make a Constitution saving throw to maintain Concentration, you can add your Intelligence modifier to the total."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TrainingInWarAndSong(Feature):
    VALID_SKILLS = [
        Skill.ACROBATICS,
        Skill.ATHLETICS,
        Skill.PERFORMANCE,
        Skill.PERSUASION,
    ]

    def __init__(self, skill: Skill):
        self._choice = SkillProficiencyChoice(
            [skill], self.VALID_SKILLS, count=1, error_prefix="Training in War and Song"
        )
        super().__init__(
            name="Training in War and Song",
            origin="Bladesinger Wizard Level 3",
            passive=True,
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "...proficiency with all Melee Martial weapons that don't have the
        # Two-Handed or Heavy property."
        GrantWeaponProficiency(
            [WeaponProficiency.MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED]
        ).apply(ledger_writer)
        self._choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Weapons",
                        "Proficiency with Melee Martial weapons that don't have the Two-Handed or Heavy property",
                    ),
                    (
                        "Focus",
                        "Use a Melee weapon you're proficient with as a Spellcasting Focus for your Wizard spells",
                    ),
                    ("Skill", f"Proficiency in {self._choice.skills[0].value}"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain proficiency with all Melee Martial weapons that don't have the Two-Handed or Heavy property. You can use a Melee weapon with which you have proficiency as a Spellcasting Focus for your Wizard spells.\n"
            f"You also gain proficiency in {self._choice.skills[0].value}."
        )
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Bladesinger Wizard Level 6")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Attack action", "Attack twice instead of once"),
                    (
                        "Cantrip",
                        "Replace one of the attacks with a Wizard cantrip that has a casting time of an action",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can attack twice, instead of once, whenever you take the Attack action on your turn. Moreover, you can cast one of your Wizard cantrips that has a casting time of an action in place of one of those attacks."
        return description


class SongOfDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Song of Defense",
            origin="Bladesinger Wizard Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "You take damage while your Bladesong is active"),
                    ("Cost", "One spell slot"),
                    ("Effect", "Reduce the damage by five times the slot's level"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you take damage while your Bladesong is active, you can take a Reaction to expend one spell slot and reduce the damage taken by an amount equal to five times the spell slot's level."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class SongOfVictory(Feature):
    def __init__(self):
        super().__init__(
            name="Song of Victory",
            origin="Bladesinger Wizard Level 14",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Trigger",
                        "After you cast a spell that has a casting time of an action",
                    ),
                    ("Effect", "Make one attack with a weapon"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "After you cast a spell that has a casting time of an action, you can make one attack with a weapon as a Bonus Action."
        return description
