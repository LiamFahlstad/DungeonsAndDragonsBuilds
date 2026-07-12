from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import FighterSubclass
from Features.ClassFeatures import FighterFeatures, SpellSlots
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterEldritchKnightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterFeatures.EldritchKnightSpellcasting())
        data.add_feature(FighterFeatures.WarBond())
        return data


@attr.dataclass
class FighterEldritchKnightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterFeatures.WarMagic())
        return data


@attr.dataclass
class FighterEldritchKnightLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterFeatures.EldritchStrike())
        return data


@attr.dataclass
class FighterEldritchKnightLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterFeatures.ArcaneCharge())
        return data


@attr.dataclass
class FighterEldritchKnightLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        war_magic: FighterFeatures.WarMagic = data.get_features_by_type(
            FighterFeatures.WarMagic
        )[0]
        war_magic.extend_feature(FighterFeatures.ImprovedWarMagic())
        return data


class FighterEldritchKnightCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass.ELDRITCH_KNIGHT.value,
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
            subclass=FighterSubclass.ELDRITCH_KNIGHT.value,
            replace_spells=replace_spells,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )
