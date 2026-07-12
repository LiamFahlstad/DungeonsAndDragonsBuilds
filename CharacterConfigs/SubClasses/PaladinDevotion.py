from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import PaladinSubclass
from Features.ClassFeatures import PaladinDevotionFeatures
from Spells.Definitions import (
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    PaladinLevel1Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class DevotionPaladinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinDevotionFeatures.SacredWeapon())
        data.add_spell(ClericLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        data.add_spell(PaladinLevel1Spells.SHIELD_OF_FAITH)
        return data


@attr.dataclass
class DevotionPaladinLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.AID)
        data.add_spell(ClericLevel2Spells.ZONE_OF_TRUTH)
        return data


@attr.dataclass
class DevotionPaladinLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinDevotionFeatures.AuraOfDevotion())
        return data


@attr.dataclass
class DevotionPaladinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel3Spells.BEACON_OF_HOPE)
        data.add_spell(ClericLevel3Spells.DISPEL_MAGIC)
        return data


@attr.dataclass
class DevotionPaladinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        data.add_spell(ClericLevel4Spells.GUARDIAN_OF_FAITH)
        return data


@attr.dataclass
class DevotionPaladinLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinDevotionFeatures.SmiteOfProtection())
        return data


@attr.dataclass
class DevotionPaladinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel5Spells.COMMUNE)
        data.add_spell(ClericLevel5Spells.FLAME_STRIKE)
        return data


@attr.dataclass
class DevotionPaladinLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinDevotionFeatures.HolyNimbus())
        return data


class PaladinDevotionCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_DEVOTION.value,
            skills=skills,
        )


class DevotionPaladinMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_DEVOTION.value,
            replace_spells=replace_spells,
        )
