from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WizardSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Wizard import WizardOrderOfScribesFeatures
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


@attr.dataclass
class WizardOrderOfScribesLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardOrderOfScribesFeatures.WizardlyQuill())
        data.add_feature(WizardOrderOfScribesFeatures.AwakenedSpellbook())
        return data


@attr.dataclass
class WizardOrderOfScribesLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        awakened_spellbook: WizardOrderOfScribesFeatures.AwakenedSpellbook = (
            data.get_features_by_type(
                WizardOrderOfScribesFeatures.AwakenedSpellbook
            )[0]
        )
        awakened_spellbook.extend_feature(WizardOrderOfScribesFeatures.ManifestMind())
        return data


@attr.dataclass
class WizardOrderOfScribesLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        awakened_spellbook: WizardOrderOfScribesFeatures.AwakenedSpellbook = (
            data.get_features_by_type(
                WizardOrderOfScribesFeatures.AwakenedSpellbook
            )[0]
        )
        awakened_spellbook.extend_feature(WizardOrderOfScribesFeatures.MasterScriviner())
        return data


@attr.dataclass
class WizardOrderOfScribesLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        awakened_spellbook: WizardOrderOfScribesFeatures.AwakenedSpellbook = (
            data.get_features_by_type(
                WizardOrderOfScribesFeatures.AwakenedSpellbook
            )[0]
        )
        awakened_spellbook.extend_feature(WizardOrderOfScribesFeatures.OneWithTheWord())
        return data


class WizardOrderOfScribesCustomStarterClassArgs(WizardCustomStarterClassArgs):
    def __init__(
        self,
        skills: WizardSkillsStatBlock,
    ):
        super().__init__(
            subclass=WizardSubclass2014.ORDER_OF_SCRIBES.value,
            skills=skills,
        )


class WizardOrderOfScribesMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass2014.ORDER_OF_SCRIBES.value,
            replace_spells=replace_spells,
        )
