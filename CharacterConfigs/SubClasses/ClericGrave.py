from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass
from Features.ClassFeatures.Cleric import ClericGraveFeatures, ClericFeatures
from Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    NecromancyLevel1Spells,
    NecromancyLevel2Spells,
    NecromancyLevel3Spells,
    NecromancyLevel4Spells,
)
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericGraveLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel1Spells.DETECT_EVIL_AND_GOOD)
        data.add_spell(NecromancyLevel1Spells.FALSE_LIFE)
        data.add_spell(ClericLevel2Spells.GENTLE_REPOSE)
        data.add_spell(NecromancyLevel2Spells.RAY_OF_ENFEEBLEMENT)
        data.add_spell(ClericLevel0Spells.SPARE_THE_DYING)
        channel_divinity: ClericFeatures.ChannelDivinity = data.get_features_by_type(
            ClericFeatures.ChannelDivinity
        )[0]
        channel_divinity.extend_feature(ClericGraveFeatures.PathToTheGrave())
        data.add_feature(ClericGraveFeatures.CircleOfMortality())
        return data


@attr.dataclass
class ClericGraveLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel3Spells.REVIVIFY)
        data.add_spell(NecromancyLevel3Spells.VAMPIRIC_TOUCH)
        return data


@attr.dataclass
class ClericGraveLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericGraveFeatures.SentinelAtDeathsDoor())
        return data


@attr.dataclass
class ClericGraveLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(NecromancyLevel4Spells.BLIGHT)
        data.add_spell(ClericLevel4Spells.DEATH_WARD)
        return data


@attr.dataclass
class ClericGraveLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel5Spells.DISPEL_EVIL_AND_GOOD)
        data.add_spell(ClericLevel5Spells.RAISE_DEAD)
        return data


@attr.dataclass
class ClericGraveLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericGraveFeatures.DivineReaper())
        return data


class ClericGraveCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass.GRAVE.value,
            skills=skills,
        )


class ClericGraveMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.GRAVE.value,
            replace_spells=replace_spells,
        )
