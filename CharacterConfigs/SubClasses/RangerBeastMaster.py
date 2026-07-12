from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import DamageType, RangerSubclass
from Features.ClassFeatures import RangerBeastMasterFeatures
from Features.ClassFeatures.PrimalCompanions import CompanionType
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerBeastMasterLevel3(ClassBuilder.SubclassLevel3):
    companion_type: CompanionType
    damage_type: Optional[DamageType] = None
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(
            RangerBeastMasterFeatures.PrimalCompanion(
                companion_type=self.companion_type,
                damage_type=self.damage_type,
            )
        )
        return data


@attr.dataclass
class RangerBeastMasterLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerBeastMasterFeatures.ExceptionalTraining())
        return data


@attr.dataclass
class RangerBeastMasterLevel11(ClassBuilder.SubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerBeastMasterFeatures.BestialFury())
        return data


@attr.dataclass
class RangerBeastMasterLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerBeastMasterFeatures.ShareSpells())
        return data


class RangerBeastMasterCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass.BEAST_MASTER.value,
            skills=skills,
        )


class RangerBeastMasterMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.BEAST_MASTER.value,
            replace_spells=replace_spells,
        )
