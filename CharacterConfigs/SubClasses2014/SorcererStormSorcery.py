from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import SorcererSubclass2014
from Features.SubClassFeatures2014.Sorcerer import SorcererStormSorceryFeatures
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererStormSorceryLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererStormSorceryFeatures.WindSpeaker())
        data.add_feature(SorcererStormSorceryFeatures.TempestuousMagic())
        return data


@attr.dataclass
class SorcererStormSorceryLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererStormSorceryFeatures.HeartOfTheStorm())
        data.add_feature(SorcererStormSorceryFeatures.StormGuide())
        return data


@attr.dataclass
class SorcererStormSorceryLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererStormSorceryFeatures.StormsFury())
        return data


@attr.dataclass
class SorcererStormSorceryLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererStormSorceryFeatures.WindSoul())
        return data


class SorcererStormSorceryCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass2014.STORM.value,
            skills=skills,
        )


class SorcererStormSorceryMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass2014.STORM.value,
            replace_spells=replace_spells,
        )
