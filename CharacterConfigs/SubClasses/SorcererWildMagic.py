from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import SorcererSubclass
from Features.ClassFeatures import SorcererFeatures
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererWildMagicLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.WildMagicSurge())
        data.add_feature(SorcererFeatures.WildMagicSurgeTable())
        data.add_feature(SorcererFeatures.TidesOfChaos())
        return data


@attr.dataclass
class SorcererWildMagicLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.BendLuck())
        return data


@attr.dataclass
class SorcererWildMagicLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.ControlledChaos())
        return data


@attr.dataclass
class SorcererWildMagicLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererFeatures.TamedSurge())
        return data


class SorcererWildMagicCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.WILD_MAGIC.value,
            skills=skills,
        )


class SorcererWildMagicMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.WILD_MAGIC.value,
            replace_spells=replace_spells,
        )
