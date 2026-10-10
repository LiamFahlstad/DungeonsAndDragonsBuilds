from Core.Definitions import Sense, Skill
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import SkillProficiencyChoice, GrantSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_PROFICIENCY_BONUS
from Model.View import CharacterView

SPEED = 30  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Lupin Trait")
        self._sense = GrantSense(Sense.DARKVISION, 60)

    def apply(self, effects: LedgerWriter):
        self._sense.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return "You have Darkvision with a range of 60 feet."


class FeralPounce(Feature):
    def __init__(self):
        super().__init__(
            name="Feral Pounce", origin="Lupin Trait", usage_tags=["damage", "control"]
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            "Your Unarmed Strikes deal Slashing damage instead of Bludgeoning damage. "
            "In addition, when you hit a creature with an Unarmed Strike as part of the Attack action on your turn, "
            "you can use both the Damage and the Shove options. You can use this benefit only once per turn."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Howl(Feature):
    def __init__(self):
        super().__init__(
            name="Howl",
            origin="Lupin Trait",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Start of Next Turn",
                range="15-Foot Radius",
            ),
            usage_tags=["control"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                current_formula="Current amount: equal to your proficiency bonus.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you let out an unearthly howl. "
            "Each creature of your choice within 15 feet of you must succeed on a Wisdom saving throw "
            "(DC 8 plus your Constitution modifier and Proficiency Bonus) or have Disadvantage on attack rolls "
            "and saving throws until the start of your next turn.\n"
            "You can use this trait, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        constitution_modifier = character.get_constitution_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + constitution_modifier + proficiency_bonus

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class WerewolfInstincts(Feature):
    VALID_SKILLS = [Skill.PERCEPTION, Skill.STEALTH, Skill.SURVIVAL]

    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(name="Werewolf Instincts", origin="Lupin Trait")
        self._choice = SkillProficiencyChoice(
            [skill], self.VALID_SKILLS, count=1, error_prefix="Werewolf Instincts"
        )

    def apply(self, effects: LedgerWriter):
        self._choice.apply(effects)

    def get_description(self, character: CharacterView) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."
