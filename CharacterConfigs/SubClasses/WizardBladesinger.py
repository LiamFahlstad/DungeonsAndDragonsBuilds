from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardNonGenericStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import Skill, WizardSubclass
from Features.ClassFeatures import WizardFeatures
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


@attr.dataclass
class WizardBladesingerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        if data.armors:
            raise ValueError("Bladesong cannot be used while wearing armor.")
        data.add_feature(WizardFeatures.BladesongText())
        data.add_feature(WizardFeatures.TrainingInWarAndSong(Skill.ATHLETICS))
        return data


@attr.dataclass
class WizardBladesingerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.ExtraAttack())
        return data


@attr.dataclass
class WizardBladesingerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SongOfDefense())
        return data


@attr.dataclass
class WizardBladesingerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SongOfVictory())
        return data


class WizardBladeSingerNonGenericStarterClassArgs(WizardNonGenericStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass.BLADESINGER.value,
            skills=skills,
        )


class WizardBladesingerMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.BLADESINGER.value,
            replace_spells=replace_spells,
        )
