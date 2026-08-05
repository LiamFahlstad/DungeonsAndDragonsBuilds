from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WizardSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Wizard import WizardDivinationFeatures
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


@attr.dataclass
class WizardDivinationLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardDivinationFeatures.DivinationSavant())
        data.add_feature(WizardDivinationFeatures.Portent())
        return data


@attr.dataclass
class WizardDivinationLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardDivinationFeatures.ExpertDivination())
        return data


@attr.dataclass
class WizardDivinationLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardDivinationFeatures.TheThirdEye())
        return data


@attr.dataclass
class WizardDivinationLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardDivinationFeatures.GreaterPortent())
        return data


class WizardDivinationCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass2014.DIVINATION.value,
            skills=skills,
        )


class WizardDivinationMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.DIVINATION.value,
            replace_spells=replace_spells,
        )
