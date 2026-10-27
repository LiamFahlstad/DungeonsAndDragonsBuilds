from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import FighterSubclass, Skill
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.SubClassFeatures.Fighter import (
    FighterSorrowKnightFeatures,
)


@attr.dataclass
class FighterSorrowKnightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterSorrowKnightFeatures.DespairingStrikes())
        data.add_feature(FighterSorrowKnightFeatures.SolemnGaze())


@attr.dataclass
class FighterSorrowKnightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # A rider on Tactical Shift, which is itself an extension of Second
        # Wind (FighterBase level 5). Extensions only match top-level
        # features, so this rides on Second Wind's card beside Tactical Shift.
        data.add_feature(
            FighterSorrowKnightFeatures.DreadedAppearance(),
            extends=FighterFeatures.SecondWind,
        )


@attr.dataclass
class FighterSorrowKnightLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterSorrowKnightFeatures.UnsettledStrikes(),
            extends=FighterSorrowKnightFeatures.DespairingStrikes,
        )


@attr.dataclass
class FighterSorrowKnightLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterSorrowKnightFeatures.GrimConstitution())


@attr.dataclass
class FighterSorrowKnightLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterSorrowKnightFeatures.GrievingMantle(),
            extends=FighterFeatures.ActionSurge,
        )


class FighterSorrowKnightCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=FighterSubclass.SORROW_KNIGHT.value,
            skills=skills,
        )


class FighterSorrowKnightMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.SORROW_KNIGHT.value,
            replace_spells=replace_spells,
        )
