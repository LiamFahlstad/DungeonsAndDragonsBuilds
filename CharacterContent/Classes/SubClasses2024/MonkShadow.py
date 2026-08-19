from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, MonkSubclass
from CharacterContent.Features.SubClassFeatures.Monk import MonkShadowFeatures
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Spells.SpellLists import EvocationLevel2Spells, IllusionLevel0Spells
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkShadowLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.extend_feature(MonkShadowFeatures.ShadowArts())
        data.add_spell(
            EvocationLevel2Spells.DARKNESS,
            Ability.WISDOM,
            additional_ruling="Cast by expending 1 Focus Point instead of a spell slot",
        )
        data.add_cantrip(IllusionLevel0Spells.MINOR_ILLUSION, Ability.WISDOM)
        return data


@attr.dataclass
class MonkShadowLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkShadowFeatures.ShadowStep())
        return data


@attr.dataclass
class MonkShadowLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        shadow_step: MonkShadowFeatures.ShadowStep = data.get_features_by_type(
            MonkShadowFeatures.ShadowStep
        )[0]
        shadow_step.extend_feature(MonkShadowFeatures.ImprovedShadowStep())
        return data


@attr.dataclass
class MonkShadowLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.extend_feature(MonkShadowFeatures.CloakOfShadows())
        return data


class MonkShadowCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: MonkSkillsStatBlock,
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.SHADOW.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkShadowMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.SHADOW.value,
            replace_spells=replace_spells,
        )
