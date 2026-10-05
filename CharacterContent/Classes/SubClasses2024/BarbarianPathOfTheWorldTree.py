from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import BarbarianSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Barbarian import (
    BarbarianPathOfTheWorldTreeFeatures,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianWorldTreeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            BarbarianPathOfTheWorldTreeFeatures.VitalityOfTheTree(),
            extends=BarbarianFeatures.Rage,
        )
        return data


@attr.dataclass
class BarbarianWorldTreeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            BarbarianPathOfTheWorldTreeFeatures.BranchesOfTheTree(),
            extends=BarbarianFeatures.Rage,
        )
        return data


@attr.dataclass
class BarbarianWorldTreeLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(BarbarianPathOfTheWorldTreeFeatures.BatteringRoots())
        return data


@attr.dataclass
class BarbarianWorldTreeLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            BarbarianPathOfTheWorldTreeFeatures.TravelAlongTheTree(),
            extends=BarbarianFeatures.Rage,
        )
        return data


class BarbarianWorldTreeCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_WORLD_TREE.value,
            skills=skills,
        )


class BarbarianWorldTreeMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_WORLD_TREE.value,
            replace_spells=replace_spells,
        )
