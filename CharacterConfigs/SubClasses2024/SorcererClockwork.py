from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import SorcererSubclass
from Features.SubClassFeatures.Sorcerer import SorcererClockworkFeatures
from Spells.SpellLists import (
    AbjurationLevel1Spells,
    AbjurationLevel2Spells,
    AbjurationLevel4Spells,
    AbjurationLevel5Spells,
    ConjurationLevel4Spells,
    EvocationLevel5Spells,
    SorcererLevel3Spells,
)
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererClockworkLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererClockworkFeatures.ClockworkSpells())
        data.add_spell(AbjurationLevel2Spells.AID)
        data.add_spell(AbjurationLevel1Spells.ALARM)
        data.add_spell(AbjurationLevel2Spells.LESSER_RESTORATION)
        data.add_spell(AbjurationLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        data.add_feature(SorcererClockworkFeatures.RestoreBalance())
        return data


@attr.dataclass
class SorcererClockworkLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.DISPEL_MAGIC)
        data.add_spell(SorcererLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class SorcererClockworkLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererClockworkFeatures.BastionOfLaw())
        return data


@attr.dataclass
class SorcererClockworkLevel7(ClassBuilder.SubclassLevel7):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(AbjurationLevel4Spells.FREEDOM_OF_MOVEMENT)
        data.add_spell(ConjurationLevel4Spells.SUMMON_CONSTRUCT)
        return data


@attr.dataclass
class SorcererClockworkLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(AbjurationLevel5Spells.GREATER_RESTORATION)
        data.add_spell(EvocationLevel5Spells.WALL_OF_FORCE)
        return data


@attr.dataclass
class SorcererClockworkLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererClockworkFeatures.TranceOfOrder())
        return data


@attr.dataclass
class SorcererClockworkLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererClockworkFeatures.ClockworkCavalcade())
        return data


class SorcererClockworkCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.CLOCKWORK.value,
            skills=skills,
        )


class SorcererClockworkMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.CLOCKWORK.value,
            replace_spells=replace_spells,
        )
