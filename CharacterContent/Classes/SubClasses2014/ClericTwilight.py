from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericTwilightFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericTwilightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericTwilightFeatures.BonusProficiencies())
        data.add_feature(ClericTwilightFeatures.TwilightDomainSpells())
        data.add_feature(ClericTwilightFeatures.EyesOfNight())
        data.add_feature(ClericTwilightFeatures.VigilantBlessing())
        data.add_feature(ClericTwilightFeatures.TwilightSanctuaryChannelDivinity())
        return data


@attr.dataclass
class ClericTwilightLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericTwilightFeatures.StepsOfNight())
        return data


@attr.dataclass
class ClericTwilightLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericTwilightFeatures.DivineStrike())
        return data


@attr.dataclass
class ClericTwilightLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        twilight_sanctuary: ClericTwilightFeatures.TwilightSanctuaryChannelDivinity = (
            data.get_features_by_type(
                ClericTwilightFeatures.TwilightSanctuaryChannelDivinity
            )[0]
        )
        twilight_sanctuary.extend_feature(ClericTwilightFeatures.TwilightShroud())
        return data


class ClericTwilightCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.TWILIGHT.value,
            skills=skills,
        )


class ClericTwilightMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.TWILIGHT.value,
            replace_spells=replace_spells,
        )
