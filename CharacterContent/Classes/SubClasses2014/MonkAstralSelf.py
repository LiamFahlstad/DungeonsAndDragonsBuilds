from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import Ability, MonkSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Monk import MonkAstralSelfFeatures


@attr.dataclass
class MonkAstralSelfLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkAstralSelfFeatures.ArmsOfTheAstralSelf())


@attr.dataclass
class MonkAstralSelfLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            MonkAstralSelfFeatures.VisageOfTheAstralSelf(),
            extends=MonkAstralSelfFeatures.ArmsOfTheAstralSelf,
        )


@attr.dataclass
class MonkAstralSelfLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkAstralSelfFeatures.BodyOfTheAstralSelf())


@attr.dataclass
class MonkAstralSelfLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(MonkAstralSelfFeatures.AwakenedAstralSelf())


class MonkAstralSelfCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass2014.ASTRAL_SELF.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkAstralSelfMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass2014.ASTRAL_SELF.value,
            replace_spells=replace_spells,
        )
