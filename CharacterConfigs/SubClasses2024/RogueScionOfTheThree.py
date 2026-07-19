from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RogueSubclass
from Features.SubClassFeatures.Rogue import RogueScionOfTheThreeFeatures
from Features.ClassFeatures.Rogue import RogueFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueScionOfTheThreeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueScionOfTheThreeFeatures.Bloodthirst())
        data.add_feature(RogueScionOfTheThreeFeatures.DreadAllegiance())
        return data


@attr.dataclass
class RogueScionOfTheThreeLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.extend_feature(RogueScionOfTheThreeFeatures.StrikeFear())
        return data


@attr.dataclass
class RogueScionOfTheThreeLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueScionOfTheThreeFeatures.AuraofMalevolence())
        return data


@attr.dataclass
class RogueScionOfTheThreeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueScionOfTheThreeFeatures.DreadIncarnate())
        return data


class RogueScionOfTheThreeCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.SCION_OF_THE_THREE.value,
            skills=skills,
        )


class RogueScionOfTheThreeMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.SCION_OF_THE_THREE.value,
            replace_spells=replace_spells,
        )
