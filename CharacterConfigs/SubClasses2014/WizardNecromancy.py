from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import WizardSubclass2014
from Features.SubClassFeatures2014.Wizard import WizardNecromancyFeatures
from Spells.SpellLists import NecromancyLevel3Spells
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


@attr.dataclass
class NecromancyWizardLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardNecromancyFeatures.NecromancySavant())
        data.add_feature(WizardNecromancyFeatures.GrimHarvest())
        return data


@attr.dataclass
class NecromancyWizardLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardNecromancyFeatures.UndeadThralls())
        data.add_spell(NecromancyLevel3Spells.ANIMATE_DEAD)
        return data


@attr.dataclass
class NecromancyWizardLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardNecromancyFeatures.InuredToUndeath())
        return data


@attr.dataclass
class NecromancyWizardLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardNecromancyFeatures.CommandUndead())
        return data


class WizardNecromancyCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass2014.NECROMANCY.value,
            skills=skills,
        )


class NecromancyWizardMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.NECROMANCY.value,
            replace_spells=replace_spells,
        )
