from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WarlockSubclass2014
from Features.SubClassFeatures2014.Warlock import WarlockHexbladeFeatures
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class HexbladeWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockHexbladeFeatures.HexbladeExpandedSpells())
        data.add_feature(WarlockHexbladeFeatures.HexbladesCurse())
        data.add_feature(WarlockHexbladeFeatures.HexWarrior())
        return data


@attr.dataclass
class HexbladeWarlockLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockHexbladeFeatures.AccursedSpecter())
        return data


@attr.dataclass
class HexbladeWarlockLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockHexbladeFeatures.ArmorOfHexes())
        return data


@attr.dataclass
class HexbladeWarlockLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockHexbladeFeatures.MasterOfHexes())
        return data


class WarlockHexbladeCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass2014.HEXBLADE.value,
            skills=skills,
        )


class HexbladeWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass2014.HEXBLADE.value,
            replace_spells=replace_spells,
        )
