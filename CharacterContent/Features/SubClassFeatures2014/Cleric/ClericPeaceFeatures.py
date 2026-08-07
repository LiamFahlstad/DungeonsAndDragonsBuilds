from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
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
        super().__init__(name="Emboldening Bond", origin="Peace Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You can forge an empowering bond among people who are at peace with one another. As an action, you choose a number of willing creatures within 30 feet of you (this can include yourself) equal to your proficiency bonus. You create a magical bond among them for 10 minutes or until you use this feature again. While any bonded creature is within 30 feet of another, the creature can roll a d4 and add the number rolled to an attack roll, an ability check, or a saving throw it makes. Each creature can add the d4 no more than once per turn.\n"
            "You can use this feature a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("Action", "Action"),
            ("Range", "30 feet"),
            ("Targets", f"Willing creatures (up to {proficiency_bonus})"),
            ("Duration", "10 minutes or until you use this feature again"),
            ("Bonus", "+1d4 to attack roll, ability check, or saving throw (once per turn)"),
            ("Uses", f"Proficiency bonus ({proficiency_bonus})"),
            ("Recharge", "Long rest"),
        ]


class BalmOfPeaceChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Balm of Peace",
            origin="Peace Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use your Channel Divinity to make your very presence a soothing balm. As an action, you can move up to your speed, without provoking opportunity attacks, and when you move within 5 feet of any other creature during this action, you can restore a number of hit points to that creature equal to 2d6 + your Wisdom modifier (minimum of 1 hit point). A creature can receive this healing only once whenever you take this action."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Movement", "Up to your speed (no opportunity attacks)"),
            ("Healing per Creature", "2d6 + Wisdom modifier (minimum 1)"),
            ("Range of Healing", "Within 5 feet of you during movement"),
            ("Limit", "Once per creature per action"),
        ]


class ProtectiveBond(Feature):
    def __init__(self):
        super().__init__(name="Protective Bond", origin="Peace Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The bond you forge between people helps them protect each other. When a creature affected by your Emboldening Bond feature is about to take damage, a second bonded creature within 30 feet of the first can use its reaction to teleport to an unoccupied space within 5 feet of the first creature. The second creature then takes all the damage instead."
        return description


class PotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(name="Potent Spellcasting", origin="Peace Domain Cleric Level 8")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You add your Wisdom modifier to the damage you deal with any cleric cantrip."
        return description


class ExpansiveBond(Feature):
    def __init__(self):
        super().__init__(name="Expansive Bond", origin="Peace Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The benefits of your Emboldening Bond and Protective Bond features now work when the creatures are within 60 feet of each other. Moreover, when a creature uses Protective Bond to take someone else's damage, the creature has resistance to that damage."
        return description
