from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidMulticlassBuilder,
    DruidCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import DruidSubclass2014
from Features.SubClassFeatures2014.Druid import DruidSporesFeatures
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidSporesLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSporesFeatures.CircleSporesSpells())
        data.add_feature(DruidSporesFeatures.HaloOfSpores())
        data.add_feature(DruidSporesFeatures.SymbioticEntity())
        return data


@attr.dataclass
class DruidSporesLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSporesFeatures.FungalInfestation())
        return data


@attr.dataclass
class DruidSporesLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSporesFeatures.SpreadingSpores())
        return data


@attr.dataclass
class DruidSporesLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidSporesFeatures.FungalBody())
        return data


class DruidSporesCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass2014.SPORES.value,
            skills=skills,
        )


class DruidSporesMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass2014.SPORES.value,
            replace_spells=replace_spells,
        )
