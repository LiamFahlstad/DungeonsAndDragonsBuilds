from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import FighterSubclass2014
from Features.ClassFeatures import SpellSlots
from Features.SubClassFeatures2014.Fighter import FighterEldritchKnightFeatures
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterEldritchKnightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEldritchKnightFeatures.EldritchKnightSpellcasting())
        data.add_feature(FighterEldritchKnightFeatures.WeaponBond())
        return data


@attr.dataclass
class FighterEldritchKnightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEldritchKnightFeatures.WarMagic())
        return data


@attr.dataclass
class FighterEldritchKnightLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEldritchKnightFeatures.EldritchStrike())
        return data


@attr.dataclass
class FighterEldritchKnightLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterEldritchKnightFeatures.ArcaneCharge())
        return data


@attr.dataclass
class FighterEldritchKnightLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        war_magic: FighterEldritchKnightFeatures.WarMagic = data.get_features_by_type(
            FighterEldritchKnightFeatures.WarMagic
        )[0]
        war_magic.extend_feature(FighterEldritchKnightFeatures.ImprovedWarMagic())
        return data


class FighterEldritchKnightCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass2014.ELDRITCH_KNIGHT.value,
            skills=skills,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )


class FighterEldritchKnightMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.ELDRITCH_KNIGHT.value,
            replace_spells=replace_spells,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )
