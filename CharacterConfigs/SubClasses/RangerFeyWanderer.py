from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RangerSubclass
from Features.ClassFeatures.Ranger import RangerFeyWandererFeatures
from Spells.SpellLists import (
    BardLevel4Spells,
    ClericLevel4Spells,
    ConjurationLevel2Spells,
    ConjurationLevel3Spells,
    ConjurationLevel4Spells,
    EnchantmentLevel1Spells,
    IllusionLevel5Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class FeyWandererRangerLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeyWandererFeatures.DreadfulStrikes())
        data.add_feature(RangerFeyWandererFeatures.FeyWandererSpells())
        data.add_feature(RangerFeyWandererFeatures.OtherworldlyGlamour())
        data.add_spell(EnchantmentLevel1Spells.CHARM_PERSON)
        return data


@attr.dataclass
class FeyWandererRangerLevel5(ClassBuilder.SubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel2Spells.MISTY_STEP)
        return data


@attr.dataclass
class FeyWandererRangerLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeyWandererFeatures.BeguilingTwist())
        return data


@attr.dataclass
class FeyWandererRangerLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel3Spells.SUMMON_FEY)
        return data


@attr.dataclass
class FeyWandererRangerLevel11(ClassBuilder.SubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeyWandererFeatures.FeyReinforcements())
        return data


@attr.dataclass
class FeyWandererRangerLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel4Spells.DIMENSION_DOOR)
        return data


@attr.dataclass
class FeyWandererRangerLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerFeyWandererFeatures.MistyWanderer())
        return data


@attr.dataclass
class FeyWandererRangerLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(IllusionLevel5Spells.MISLEAD)
        return data



class RangerFeyWandererCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass.FEY_WANDERER.value,
            skills=skills,
        )


class FeyWandererRangerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.FEY_WANDERER.value,
            replace_spells=replace_spells,
        )
