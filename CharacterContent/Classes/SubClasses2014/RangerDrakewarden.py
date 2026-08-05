from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import DamageType, RangerSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Ranger import RangerDrakewardenFeatures
from CharacterContent.Spells.SpellLists import ClericLevel0Spells
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerDrakewardenLevel3(ClassBuilder.SubclassLevel3):
    damage_type: Optional[DamageType] = None
    language: Optional[str] = None

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerDrakewardenFeatures.DraconicGift(language=self.language))
        data.add_feature(RangerDrakewardenFeatures.DrakeCompanion(damage_type=self.damage_type))
        data.add_cantrip(ClericLevel0Spells.THAUMATURGY)
        return data


@attr.dataclass
class RangerDrakewardenLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerDrakewardenFeatures.BondOfFangAndScale())
        return data


@attr.dataclass
class RangerDrakewardenLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerDrakewardenFeatures.DrakesBreath())
        return data


@attr.dataclass
class RangerDrakewardenLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerDrakewardenFeatures.PerfectedBond())
        return data


class RangerDrakewardenCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass2014.DRAKEWARDEN.value,
            skills=skills,
        )


class RangerDrakewardenMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass2014.DRAKEWARDEN.value,
            replace_spells=replace_spells,
        )
