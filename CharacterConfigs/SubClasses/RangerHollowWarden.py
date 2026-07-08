from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RangerSubclass
from Features.ClassFeatures import RangerFeatures
from Spells.Definitions import (
    IllusionLevel3Spells,
    NecromancyLevel1Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
    TransmutationLevel2Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerHollowWardenLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.HollowWardenSpells())
        data.add_feature(RangerFeatures.WrathOfTheWild())
        data.add_spell(NecromancyLevel1Spells.WRATHFUL_SMITE)
        return data


@attr.dataclass
class RangerHollowWardenLevel5(ClassBuilder.SubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(TransmutationLevel2Spells.ALTER_SELF)
        return data


@attr.dataclass
class RangerHollowWardenLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.HungeringMight())
        return data


@attr.dataclass
class RangerHollowWardenLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(IllusionLevel3Spells.PHANTOM_STEED)
        return data


@attr.dataclass
class RangerHollowWardenLevel11(ClassBuilder.SubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.RotAndViolence())
        return data


@attr.dataclass
class RangerHollowWardenLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(RangerLevel4Spells.DOMINATE_BEAST)
        return data


@attr.dataclass
class RangerHollowWardenLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeatures.AncientMight())
        return data


@attr.dataclass
class RangerHollowWardenLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

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
