from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RangerSubclass
from Features.ClassFeatures.Ranger import RangerGloomStalkerFeatures
from Spells.SpellLists import (
    BardLevel4Spells,
    ClericLevel4Spells,
    IllusionLevel1Spells,
    IllusionLevel3Spells,
    IllusionLevel4Spells,
    IllusionLevel5Spells,
    TransmutationLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerGloomStalkerLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.DreadAmbusher())
        data.add_feature(RangerGloomStalkerFeatures.UmbralSight())
        data.add_feature(RangerGloomStalkerFeatures.GloomStalkerSpells())
        data.add_spell(IllusionLevel1Spells.DISGUISE_SELF)
        return data


@attr.dataclass
class RangerGloomStalkerLevel5(ClassBuilder.SubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(TransmutationLevel2Spells.ROPE_TRICK)
        return data


@attr.dataclass
class RangerGloomStalkerLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.IronMind())
        return data


@attr.dataclass
class RangerGloomStalkerLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(IllusionLevel3Spells.FEAR)
        return data


@attr.dataclass
class RangerGloomStalkerLevel11(ClassBuilder.SubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.StalkersFlurry())
        return data


@attr.dataclass
class RangerGloomStalkerLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(IllusionLevel4Spells.GREATER_INVISIBILITY)
        return data


@attr.dataclass
class RangerGloomStalkerLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerGloomStalkerFeatures.ShadowyDodge())
        return data


@attr.dataclass
class RangerGloomStalkerLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(IllusionLevel5Spells.SEEMING)
        return data


class RangerGloomStalkerCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass.GLOOM_STALKER.value,
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
            subclass=RangerSubclass.GLOOM_STALKER.value,
            replace_spells=replace_spells,
        )
