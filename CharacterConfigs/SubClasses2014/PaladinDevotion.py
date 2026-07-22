from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import PaladinSubclass2014
from Features.SubClassFeatures2014.Paladin import PaladinDevotionFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class DevotionPaladinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinDevotionFeatures.DevotionSpells())
        data.add_feature(PaladinDevotionFeatures.SacredWeapon())
        data.add_feature(PaladinDevotionFeatures.TurnTheUnholy())
        data.add_spell(PaladinLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        data.add_spell(ClericLevel1Spells.SANCTUARY)
        return data


@attr.dataclass
class DevotionPaladinLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel2Spells.LESSER_RESTORATION)
        data.add_spell(PaladinLevel2Spells.ZONE_OF_TRUTH)
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
        data.add_spell(PaladinLevel3Spells.DISPEL_MAGIC)
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
        data.add_feature(PaladinDevotionFeatures.PurityOfSpirit())
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
class DevotionPaladinLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_devotion: PaladinDevotionFeatures.AuraOfDevotion = (
            data.get_features_by_type(PaladinDevotionFeatures.AuraOfDevotion)[0]
        )
        aura_of_devotion.extend_feature(PaladinDevotionFeatures.AuraOfDevotionExpansion())
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
            subclass=PaladinSubclass2014.DEVOTION.value,
            skills=skills,
        )


class PaladinDevotionMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.DEVOTION.value,
            replace_spells=replace_spells,
        )
