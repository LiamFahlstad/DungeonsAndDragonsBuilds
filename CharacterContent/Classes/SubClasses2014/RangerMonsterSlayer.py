from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RangerSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Ranger import RangerMonsterSlayerFeatures
from CharacterContent.Spells.SpellLists import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerMonsterSlayerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerMonsterSlayerFeatures.MonsterSlayerMagic())
        data.add_feature(RangerMonsterSlayerFeatures.HuntersSense())
        data.add_feature(RangerMonsterSlayerFeatures.SlayersPrey())
        data.add_spell(PaladinLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        return data


@attr.dataclass
class RangerMonsterSlayerLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel2Spells.ZONE_OF_TRUTH)
        return data


@attr.dataclass
class RangerMonsterSlayerLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerMonsterSlayerFeatures.SupernaturalDefense())
        return data


@attr.dataclass
class RangerMonsterSlayerLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel3Spells.MAGIC_CIRCLE)
        return data


@attr.dataclass
class RangerMonsterSlayerLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerMonsterSlayerFeatures.MagicUsersNemesis())
        return data


@attr.dataclass
class RangerMonsterSlayerLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel4Spells.BANISHMENT)
        return data


@attr.dataclass
class RangerMonsterSlayerLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerMonsterSlayerFeatures.SlayersCounter())
        return data


@attr.dataclass
class RangerMonsterSlayerLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.HOLD_MONSTER)
        return data


class RangerMonsterSlayerCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass2014.MONSTER_SLAYER.value,
            skills=skills,
        )


class RangerMonsterSlayerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass2014.MONSTER_SLAYER.value,
            replace_spells=replace_spells,
        )
