from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidCustomStarterClassArgs,
    DruidMulticlassBuilder,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import DruidSubclass
from Features.SubClassFeatures.Druid import DruidSeaFeatures
from Spells.SpellLists import (
    ArtificerLevel0Spells,
    BardLevel5Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    SorcererLevel3Spells,
)
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidSeaLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSeaFeatures.CircleOfTheSeaSpells())
        data.add_feature(DruidSeaFeatures.WrathOfTheSea())
        data.add_spell(DruidLevel1Spells.FOG_CLOUD)
        data.add_spell(DruidLevel2Spells.GUST_OF_WIND)
        data.add_spell(ArtificerLevel0Spells.RAY_OF_FROST)
        data.add_spell(DruidLevel1Spells.THUNDERWAVE)
        return data


@attr.dataclass
class DruidSeaLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.LIGHTNING_BOLT)
        data.add_spell(DruidLevel3Spells.WATER_BREATHING)
        return data


@attr.dataclass
class DruidSeaLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSeaFeatures.AquaticAffinity())
        return data


@attr.dataclass
class DruidSeaLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.CONTROL_WATER)
        data.add_spell(DruidLevel4Spells.ICE_STORM)
        return data


@attr.dataclass
class DruidSeaLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.CONJURE_ELEMENTAL)
        data.add_spell(BardLevel5Spells.HOLD_MONSTER)
        return data


@attr.dataclass
class DruidSeaLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSeaFeatures.Stormborn())
        return data


@attr.dataclass
class DruidSeaLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSeaFeatures.OceanicGift())
        return data


class DruidSeaCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass.SEA.value,
            skills=skills,
        )


class DruidSeaMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.SEA.value,
            replace_spells=replace_spells,
        )
