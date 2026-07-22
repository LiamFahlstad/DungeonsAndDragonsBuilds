from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import RangerSubclass2014
from Features.SubClassFeatures2014.Ranger import RangerHorizonWalkerFeatures
from Spells.SpellLists import (
    WizardLevel1Spells,
    SorcererLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerHorizonWalkerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHorizonWalkerFeatures.HorizonWalkerSpells())
        data.add_feature(RangerHorizonWalkerFeatures.DetectPortal())
        data.add_feature(RangerHorizonWalkerFeatures.PlanarWarrior())
        data.add_spell(WizardLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        return data


@attr.dataclass
class RangerHorizonWalkerLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel2Spells.MISTY_STEP)
        return data


@attr.dataclass
class RangerHorizonWalkerLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHorizonWalkerFeatures.EtherealStep())
        return data


@attr.dataclass
class RangerHorizonWalkerLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        return data


@attr.dataclass
class RangerHorizonWalkerLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHorizonWalkerFeatures.DistantStrike())
        return data


@attr.dataclass
class RangerHorizonWalkerLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.BANISHMENT)
        return data


@attr.dataclass
class RangerHorizonWalkerLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerHorizonWalkerFeatures.SpectralDefense())
        return data


@attr.dataclass
class RangerHorizonWalkerLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.TELEPORTATION_CIRCLE)
        return data


class RangerHorizonWalkerCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass2014.HORIZON_WALKER.value,
            skills=skills,
        )


class HorizonWalkerRangerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass2014.HORIZON_WALKER.value,
            replace_spells=replace_spells,
        )
