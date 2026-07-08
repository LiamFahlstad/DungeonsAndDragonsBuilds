from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import SorcererSubclass
from Features.ClassFeatures import SorcererFeatures
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererDraconicLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.DraconicResilience())
        return data


@attr.dataclass
class SorcererDraconicLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.ElementalAffinity())
        return data


@attr.dataclass
class SorcererDraconicLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.DragonWings())
        return data


@attr.dataclass
class SorcererDraconicLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.DragonCompanion())
        return data


class SorcererDraconicCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.DRACONIC.value,
            skills=skills,
        )


class SorcererDraconicMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.DRACONIC.value,
            replace_spells=replace_spells,
        )
