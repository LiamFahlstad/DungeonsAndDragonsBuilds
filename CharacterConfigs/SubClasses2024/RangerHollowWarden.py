from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import RangerSubclass
from Features.SubClassFeatures.Ranger import RangerHollowWardenFeatures
from Spells.SpellLists import (
    IllusionLevel3Spells,
    NecromancyLevel1Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
    TransmutationLevel2Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerHollowWardenLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHollowWardenFeatures.HollowWardenSpells())
        data.add_feature(RangerHollowWardenFeatures.WrathOfTheWild())
        data.add_spell(NecromancyLevel1Spells.WRATHFUL_SMITE)
        return data


@attr.dataclass
class RangerHollowWardenLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(TransmutationLevel2Spells.ALTER_SELF)
        return data


@attr.dataclass
class RangerHollowWardenLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHollowWardenFeatures.HungeringMight())
        return data


@attr.dataclass
class RangerHollowWardenLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(IllusionLevel3Spells.PHANTOM_STEED)
        return data


@attr.dataclass
class RangerHollowWardenLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHollowWardenFeatures.RotAndViolence())
        return data


@attr.dataclass
class RangerHollowWardenLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(RangerLevel4Spells.DOMINATE_BEAST)
        return data


@attr.dataclass
class RangerHollowWardenLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHollowWardenFeatures.AncientMight())
        return data


@attr.dataclass
class RangerHollowWardenLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(RangerLevel5Spells.STEEL_WIND_STRIKE)
        return data


class RangerHollowWardenCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass.HOLLOW_WARDEN.value,
            skills=skills,
        )


class RangerHollowWardenMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.HOLLOW_WARDEN.value,
            replace_spells=replace_spells,
        )
