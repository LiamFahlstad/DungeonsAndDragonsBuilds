from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import FighterSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Fighter import (
    FighterRuneKnightFeatures,
)


@attr.dataclass
class FighterRuneKnightLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterRuneKnightFeatures.BonusProficiencies())
        data.add_feature(FighterRuneKnightFeatures.RuneCarver())
        data.add_feature(FighterRuneKnightFeatures.GiantsMight())


@attr.dataclass
class FighterRuneKnightLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterRuneKnightFeatures.RunicShield())


@attr.dataclass
class FighterRuneKnightLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterRuneKnightFeatures.GreatStature(),
            extends=FighterRuneKnightFeatures.GiantsMight,
        )


@attr.dataclass
class FighterRuneKnightLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterRuneKnightFeatures.MasterOfRunes(),
            extends=FighterRuneKnightFeatures.RuneCarver,
        )


@attr.dataclass
class FighterRuneKnightLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterRuneKnightFeatures.RunicJuggernaut(),
            extends=FighterRuneKnightFeatures.GiantsMight,
        )


class FighterRuneKnightCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=FighterSubclass2014.RUNE_KNIGHT.value,
            skills=skills,
        )


class FighterRuneKnightMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass2014.RUNE_KNIGHT.value,
            replace_spells=replace_spells,
        )
