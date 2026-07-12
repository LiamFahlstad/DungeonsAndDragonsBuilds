from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, MonkSubclass
from Features.ClassFeatures import MonkFeatures
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkMysticArtsLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.MysticArtsSpellcasting())
        return data


@attr.dataclass
class MonkMysticArtsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.MysticFightingStyle())
        data.add_feature(MonkFeatures.MysticFocus())
        return data


@attr.dataclass
class MonkMysticArtsLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.FocusedStrike())
        return data


@attr.dataclass
class MonkMysticArtsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        mystic_fighting_style: MonkFeatures.MysticFightingStyle = (
            data.get_features_by_type(MonkFeatures.MysticFightingStyle)[0]
        )
        mystic_fighting_style.extend_feature(MonkFeatures.ImprovedMysticFightingStyle())
        return data


class MonkMysticArtsCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: MonkSkillsStatBlock,
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.MYSTIC_ARTS.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkMysticArtsMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.MYSTIC_ARTS.value,
            replace_spells=replace_spells,
        )
