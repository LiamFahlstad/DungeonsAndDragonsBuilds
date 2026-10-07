from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import FighterSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Fighter import (
    FighterCavalierFeatures,
)


@attr.dataclass
class FighterCavalierLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterCavalierFeatures.BonusProficiency())
        data.add_feature(FighterCavalierFeatures.BornToTheSaddle())
        data.add_feature(FighterCavalierFeatures.UnwaveringMark())


@attr.dataclass
class FighterCavalierLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterCavalierFeatures.WardingManeuver())


@attr.dataclass
class FighterCavalierLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterCavalierFeatures.HoldTheLine())


@attr.dataclass
class FighterCavalierLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterCavalierFeatures.FerociousCharger())


@attr.dataclass
class FighterCavalierLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterCavalierFeatures.VigilantDefender())


class FighterCavalierCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=FighterSubclass2014.CAVALIER.value,
            skills=skills,
        )


class FighterCavalierMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.CAVALIER.value,
            replace_spells=replace_spells,
        )
