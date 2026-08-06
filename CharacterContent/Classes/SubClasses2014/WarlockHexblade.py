from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WarlockSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Warlock import WarlockHexbladeFeatures
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class WarlockHexbladeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockHexbladeFeatures.HexbladeExpandedSpells())
        data.add_feature(WarlockHexbladeFeatures.HexbladesCurse())
        data.add_feature(WarlockHexbladeFeatures.HexWarrior())
        return data


@attr.dataclass
class WarlockHexbladeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockHexbladeFeatures.AccursedSpecter())
        return data


@attr.dataclass
class WarlockHexbladeLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        hexblades_curse: WarlockHexbladeFeatures.HexbladesCurse = data.get_features_by_type(
            WarlockHexbladeFeatures.HexbladesCurse
        )[0]
        hexblades_curse.extend_feature(WarlockHexbladeFeatures.ArmorOfHexes())
        return data


@attr.dataclass
class WarlockHexbladeLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        hexblades_curse: WarlockHexbladeFeatures.HexbladesCurse = data.get_features_by_type(
            WarlockHexbladeFeatures.HexbladesCurse
        )[0]
        hexblades_curse.extend_feature(WarlockHexbladeFeatures.MasterOfHexes())
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


class WarlockHexbladeMulticlassBuilder(WarlockMulticlassBuilder):

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
