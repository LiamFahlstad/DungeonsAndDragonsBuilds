from Definitions import Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from Features.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

SPEED = 30  # Given by your species


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Lupin Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class FeralPounce(TextFeature):
    def __init__(self):
        super().__init__(name="Feral Pounce", origin="Lupin Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Your Unarmed Strikes deal Slashing damage instead of Bludgeoning damage. "
            "In addition, when you hit a creature with an Unarmed Strike as part of the Attack action on your turn, "
            "you can use both the Damage and the Shove options. You can use this benefit only once per turn."
        )


class Howl(TextFeature):
    def __init__(self):
        super().__init__(name="Howl", origin="Lupin Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "As a Bonus Action, you let out an unearthly howl. "
            "Each creature of your choice within 15 feet of you must succeed on a Wisdom saving throw "
            "(DC 8 plus your Constitution modifier and Proficiency Bonus) or have Disadvantage on attack rolls "
            "and saving throws until the start of your next turn.\n"
            f"You can use this trait a number of times equal to your Proficiency Bonus ({proficiency_bonus}), "
            "and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class WerewolfInstincts(CharacterFeature):
    VALID_SKILLS = [Skill.PERCEPTION, Skill.STEALTH, Skill.SURVIVAL]

    def __init__(self, skill: Skill):
        self._choice = SkillProficiencyChoice(
            [skill],
            self.VALID_SKILLS,
            count=1,
            error_prefix="Werewolf Instincts"
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)
