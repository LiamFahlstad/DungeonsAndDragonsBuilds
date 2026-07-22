from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import WizardSubclass2014
from Features.SubClassFeatures2014.Wizard import WizardEvocationFeatures
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


@attr.dataclass
class EvocationWizardLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvocationFeatures.EvocationSavant())
        data.add_feature(WizardEvocationFeatures.SculptSpells())
        return data


@attr.dataclass
class EvocationWizardLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvocationFeatures.PotentCantrip())
        return data


@attr.dataclass
class EvocationWizardLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvocationFeatures.EmpoweredEvocation())
        return data


@attr.dataclass
class EvocationWizardLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardEvocationFeatures.Overchannel())
        return data


class WizardEvocationCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass2014.EVOCATION.value,
            skills=skills,
        )


class EvocationWizardMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.EVOCATION.value,
            replace_spells=replace_spells,
        )
