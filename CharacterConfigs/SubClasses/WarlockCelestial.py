from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WarlockSubclass
from Features.ClassFeatures.Warlock import WarlockCelestialFeatures
from Spells.Definitions import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    SorcererLevel4Spells,
)
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class CelestialWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockCelestialFeatures.CelestialSpells())
        data.add_feature(WarlockCelestialFeatures.HealingLight())
        data.add_cantrip(ClericLevel0Spells.LIGHT)
        data.add_cantrip(ClericLevel0Spells.SACRED_FLAME)
        data.add_spell(ClericLevel1Spells.CURE_WOUNDS)
        data.add_spell(ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(ClericLevel2Spells.AID)
        data.add_spell(ClericLevel2Spells.LESSER_RESTORATION)
        return data


@attr.dataclass
class CelestialWarlockLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel3Spells.DAYLIGHT)
        data.add_spell(ClericLevel3Spells.REVIVIFY)
        return data


@attr.dataclass
class CelestialWarlockLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockCelestialFeatures.RadiantSoul())
        return data


@attr.dataclass
class CelestialWarlockLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel4Spells.GUARDIAN_OF_FAITH)
        data.add_spell(SorcererLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class CelestialWarlockLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel5Spells.GREATER_RESTORATION)
        data.add_spell(ClericLevel5Spells.SUMMON_CELESTIAL)
        return data


@attr.dataclass
class CelestialWarlockLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockCelestialFeatures.CelestialResilience())
        return data


@attr.dataclass
class CelestialWarlockLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockCelestialFeatures.SearingVengeance())
        return data


class WarlockCelestialCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_CELESTIAL.value,
            skills=skills,
        )


class CelestialWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_CELESTIAL.value,
            replace_spells=replace_spells,
        )
