from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WarlockSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Warlock import WarlockTheCelestialFeatures
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class WarlockTheCelestialLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheCelestialFeatures.CelestialExpandedSpells())
        data.add_feature(WarlockTheCelestialFeatures.BonusCantrips())
        data.add_feature(WarlockTheCelestialFeatures.HealingLight())
        return data


@attr.dataclass
class WarlockTheCelestialLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheCelestialFeatures.RadiantSoul())
        return data


@attr.dataclass
class WarlockTheCelestialLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheCelestialFeatures.CelestialResistance())
        return data


@attr.dataclass
class WarlockTheCelestialLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheCelestialFeatures.SearingVengeance())
        return data


class WarlockTheCelestialCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass2014.THE_CELESTIAL.value,
            skills=skills,
        )


class WarlockTheCelestialMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass2014.THE_CELESTIAL.value,
            replace_spells=replace_spells,
        )
