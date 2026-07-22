from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import WarlockSubclass
from Features.SubClassFeatures.Warlock import WarlockFiendFeatures
from Spells.SpellLists import (
    BardLevel1Spells,
    BardLevel5Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    WarlockLevel2Spells,
)
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class FiendWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFiendFeatures.FiendSpells())
        data.add_feature(WarlockFiendFeatures.DarkOnesBlessing())
        data.add_spell(SorcererLevel1Spells.BURNING_HANDS)
        data.add_spell(BardLevel1Spells.COMMAND)
        data.add_spell(SorcererLevel2Spells.SCORCHING_RAY)
        data.add_spell(WarlockLevel2Spells.SUGGESTION)
        return data


@attr.dataclass
class FiendWarlockLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.FIREBALL)
        data.add_spell(SorcererLevel3Spells.STINKING_CLOUD)
        return data


@attr.dataclass
class FiendWarlockLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFiendFeatures.DarkOnesOwnLuck())
        return data


@attr.dataclass
class FiendWarlockLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel4Spells.FIRE_SHIELD)
        data.add_spell(SorcererLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class FiendWarlockLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel5Spells.GEAS)
        data.add_spell(SorcererLevel5Spells.INSECT_PLAGUE)
        return data


@attr.dataclass
class FiendWarlockLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFiendFeatures.FiendishResilience())
        return data


@attr.dataclass
class FiendWarlockLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFiendFeatures.HurlThroughHell())
        return data


class WarlockFiendCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_FIEND.value,
            skills=skills,
        )


class FiendWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_FIEND.value,
            replace_spells=replace_spells,
        )
