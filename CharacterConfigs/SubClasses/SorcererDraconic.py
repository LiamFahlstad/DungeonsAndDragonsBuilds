from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import SorcererSubclass
from Features.ClassFeatures import SorcererDraconicFeatures
from Spells.Definitions import (
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    BardLevel1Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererDraconicLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDraconicFeatures.DraconicResilience())
        data.add_spell(SorcererLevel1Spells.CHROMATIC_ORB)
        data.add_spell(SorcererLevel2Spells.ALTER_SELF)
        data.add_spell(BardLevel1Spells.COMMAND)
        data.add_spell(SorcererLevel2Spells.DRAGONS_BREATH)
        return data


@attr.dataclass
class SorcererDraconicLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.FEAR)
        data.add_spell(SorcererLevel3Spells.FLY)
        return data


@attr.dataclass
class SorcererDraconicLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDraconicFeatures.ElementalAffinity())
        return data


@attr.dataclass
class SorcererDraconicLevel7(ClassBuilder.SubclassLevel7):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.ARCANE_EYE)
        data.add_spell(SorcererLevel4Spells.CHARM_MONSTER)
        return data


@attr.dataclass
class SorcererDraconicLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.SUMMON_DRAGON)
        return data


@attr.dataclass
class SorcererDraconicLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDraconicFeatures.DragonWings())
        return data


@attr.dataclass
class SorcererDraconicLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDraconicFeatures.DragonCompanion())
        return data


class SorcererDraconicCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass.DRACONIC.value,
            skills=skills,
        )


class SorcererDraconicMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.DRACONIC.value,
            replace_spells=replace_spells,
        )
