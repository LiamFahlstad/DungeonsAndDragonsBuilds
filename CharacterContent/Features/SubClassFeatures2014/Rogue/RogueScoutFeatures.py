from Core.Definitions import ROGUE_HIT_DIE, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import SkillProficiency, SkillExpertise
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class Skirmisher(Feature):
    def __init__(self):
        super().__init__(name="Skirmisher", origin="Scout Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 3rd level, you are difficult to pin down during a fight. You can move up to half your speed as a reaction when an enemy ends its turn within 5 feet of you. This movement doesn't provoke opportunity attacks."
        )
        return description


class Survivalist(Feature):
    def __init__(self):
        super().__init__(name="Survivalist", origin="Scout Rogue Level 3")
        self._proficiency = SkillProficiency([Skill.NATURE, Skill.SURVIVAL])
        self._expertise = SkillExpertise([Skill.NATURE, Skill.SURVIVAL])

    def apply(self, character_stat_block: CharacterStatBlock):
        self._proficiency.apply(character_stat_block)
        self._expertise.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you choose this archetype at 3rd level, you gain proficiency in the Nature and Survival skills if you don't already have it. Your proficiency bonus is doubled for any ability check you make that uses either of those proficiencies."
        )
        return description


class SuperiorMobility(Feature):
    def __init__(self):
        super().__init__(name="Superior Mobility", origin="Scout Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 9th level, your walking speed increases by 10 feet. If you have a climbing or swimming speed, this increase applies to that speed as well."
        return description


class AmbushMaster(Feature):
    def __init__(self):
        super().__init__(name="Ambush Master", origin="Scout Rogue Level 13")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 13th level, you excel at leading ambushes and acting first in a fight.\n"
            "\n"
            "You have advantage on initiative rolls. In addition, the first creature you hit during the first round of a combat becomes easier for you and others to strike; attack rolls against that target have advantage until the start of your next turn."
        )
        return description


class SuddenStrike(Feature):
    def __init__(self):
        super().__init__(name="Sudden Strike", origin="Scout Rogue Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 17th level, you can strike with deadly speed. If you take the Attack action on your turn, you can make one additional attack as a bonus action. This attack can benefit from your Sneak Attack even if you have already used it this turn, but you can't use your Sneak Attack against the same target more than once in a turn."
        return description
