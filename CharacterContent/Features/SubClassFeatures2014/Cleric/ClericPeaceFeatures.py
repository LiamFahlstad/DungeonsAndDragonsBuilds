from Core.Definitions import Ability, MAX_PROFICIENCY_BONUS
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class PeaceDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Peace Domain Spells", origin="Peace Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Peace Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Peace Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tHeroism, Sanctuary\n"
            "3rd\tAid, Warding Bond\n"
            "5th\tBeacon of Hope, Sending\n"
            "7th\tAura of Purity, Otiluke's Resilient Sphere\n"
            "9th\tGreater Restoration, Rary's Telepathic Bond"
        )
        return description


class ImplementOfPeace(Feature):
    def __init__(self):
        super().__init__(name="Implement of Peace", origin="Peace Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency in the Insight, Performance, or Persuasion skill (your choice)."
        return description


class EmboldeningBond(Feature):
    def __init__(self):
        super().__init__(
            name="Emboldening Bond",
            origin="Peace Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="10 Minutes or Until You Use This Feature Again", range="30 Feet"),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=MAX_PROFICIENCY_BONUS, regain_all_on="long rest", current_formula="Current amount: equal to your proficiency bonus."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can forge an empowering bond among people who are at peace with one another. As an action, you choose a number of willing creatures within 30 feet of you (this can include yourself) equal to your proficiency bonus. You create a magical bond among them for 10 minutes or until you use this feature again. While any bonded creature is within 30 feet of another, the creature can roll a d4 and add the number rolled to an attack roll, an ability check, or a saving throw it makes. Each creature can add the d4 no more than once per turn.\n"
            "You regain all expended uses when you finish a long rest."
        )
        return description