import Core.Definitions as Definitions
from Core.Definitions import DamageType
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import DamageImmunity, DamageResistance
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Forge Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with heavy armor and smith's tools."
        return description


class BlessingOfTheForge(Feature):
    def __init__(self):
        super().__init__(
            name="Blessing of the Forge",
            origin="Forge Domain Cleric Level 3",
            duration="Until End of Next Long Rest or Until You Die",
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to imbue magic into a weapon or armor. At the end of a long rest, you can touch one nonmagical object that is a suit of armor or a simple or martial weapon. Until the end of your next long rest or until you die, the object becomes a magic item, granting a +1 bonus to AC if it's armor or a +1 bonus to attack and damage rolls if it's a weapon.\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description