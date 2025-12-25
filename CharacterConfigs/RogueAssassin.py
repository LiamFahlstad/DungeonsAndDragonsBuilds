from typing import Optional
import attr
from CharacterConfigs.CharacterClasses.RogueBase import (
    RogueFeaturePerLevel,
    RogueSubclassLevel13,
    RogueSubclassLevel17,
    RogueSubclassLevel3,
    RogueSubclassLevel9,
)
from CharacterSheetCreator import CharacterSheetData
from Features.ClassFeatures import RogueFeatures


@attr.dataclass
class AssassinRogueLevel3(RogueSubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.Assassinate())
        data.add_feature(RogueFeatures.AssassinsTools())
        return data


@attr.dataclass
class AssassinRogueLevel9(RogueSubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.InfiltrationExpertise())
        return data


@attr.dataclass
class AssassinRogueLevel13(RogueSubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.EnvenomWeapons())
        return data


@attr.dataclass
class AssassinRogueLevel17(RogueSubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.DeathStrike())
        return data


@attr.dataclass
class AssassinRogueFeaturePerLevel(RogueFeaturePerLevel):
    subclass_level_3: Optional[AssassinRogueLevel3] = None
    subclass_level_9: Optional[AssassinRogueLevel9] = None
    subclass_level_13: Optional[AssassinRogueLevel13] = None
    subclass_level_17: Optional[AssassinRogueLevel17] = None
