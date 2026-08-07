from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ApplyWhen, RangerSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Ranger import RangerGloomStalkerFeatures
from CharacterContent.Spells.SpellLists import (
    WizardLevel1Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerGloomStalkerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.GloomStalkerMagic())
        data.add_feature(RangerGloomStalkerFeatures.DreadAmbusher(), apply_when=ApplyWhen.LAST)
        data.add_feature(RangerGloomStalkerFeatures.UmbralSight())
        data.add_spell(WizardLevel1Spells.DISGUISE_SELF)
        return data


@attr.dataclass
class RangerGloomStalkerLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel2Spells.ROPE_TRICK)
        return data


@attr.dataclass
class RangerGloomStalkerLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.IronMind())
        return data


@attr.dataclass
class RangerGloomStalkerLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.FEAR)
        return data


@attr.dataclass
class RangerGloomStalkerLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.StalkersFlurry())
        return data


@attr.dataclass
class RangerGloomStalkerLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.GREATER_INVISIBILITY)
        return data


@attr.dataclass
class RangerGloomStalkerLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.ShadowyDodge())
        return data


@attr.dataclass
class RangerGloomStalkerLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.SEEMING)
        return data


class RangerGloomStalkerCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass2014.GLOOM_STALKER.value,
            skills=skills,
        )


class RangerGloomStalkerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass2014.GLOOM_STALKER.value,
            replace_spells=replace_spells,
        )
