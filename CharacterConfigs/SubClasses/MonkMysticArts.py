from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, MonkSubclass
from Features.ClassFeatures import SpellSlots
from Features.ClassFeatures.Monk import MonkMysticArtsFeatures
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkMysticArtsLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkMysticArtsFeatures.MysticArtsSpellcasting())
        return data


@attr.dataclass
class MonkMysticArtsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkMysticArtsFeatures.MysticFightingStyle())
        data.add_feature(MonkMysticArtsFeatures.MysticFocus())
        return data


@attr.dataclass
class MonkMysticArtsLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkMysticArtsFeatures.FocusedStrike())
        return data


@attr.dataclass
class MonkMysticArtsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        mystic_fighting_style: MonkMysticArtsFeatures.MysticFightingStyle = (
            data.get_features_by_type(MonkMysticArtsFeatures.MysticFightingStyle)[0]
        )
        mystic_fighting_style.extend_feature(MonkMysticArtsFeatures.ImprovedMysticFightingStyle())
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
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
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
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )
