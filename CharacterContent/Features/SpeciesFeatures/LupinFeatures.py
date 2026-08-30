from Core.Definitions import MAX_PROFICIENCY_BONUS, Sense, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn, FeatureTarget
from CharacterContent.Features.Core.Improvements import SkillProficiencyChoice, GrantSense
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Lupin Trait")
        self._sense = GrantSense(Sense.DARKVISION, 60, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._sense.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class FeralPounce(Feature):
    def __init__(self):
        super().__init__(name="Feral Pounce", origin="Lupin Trait", usage_tags=["damage", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Your Unarmed Strikes deal Slashing damage instead of Bludgeoning damage. "
            "In addition, when you hit a creature with an Unarmed Strike as part of the Attack action on your turn, "
            "you can use both the Damage and the Shove options. You can use this benefit only once per turn."
        )

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Howl(Feature):
    def __init__(self):
        super().__init__(name="Howl", origin="Lupin Trait", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="Until Start of Next Turn", range="15-Foot Radius"), usage_tags=["control"], uses=FeatureUses(max_uses=MAX_PROFICIENCY_BONUS, current_formula="Current amount: equal to your proficiency bonus."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you let out an unearthly howl. "
            "Each creature of your choice within 15 feet of you must succeed on a Wisdom saving throw "
            "(DC 8 plus your Constitution modifier and Proficiency Bonus) or have Disadvantage on attack rolls "
            "and saving throws until the start of your next turn.\n"
            "You can use this trait, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        constitution_modifier = character_stat_block.get_constitution_modifier()
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return 8 + constitution_modifier + proficiency_bonus

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.get_proficiency_bonus()


class WerewolfInstincts(Feature):
    VALID_SKILLS = [Skill.PERCEPTION, Skill.STEALTH, Skill.SURVIVAL]

    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(name="Werewolf Instincts", origin="Lupin Trait")
        self._choice = SkillProficiencyChoice(
            [skill], self.VALID_SKILLS, count=1, error_prefix="Werewolf Instincts"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You gain proficiency in the {self.skill.value} skill."
