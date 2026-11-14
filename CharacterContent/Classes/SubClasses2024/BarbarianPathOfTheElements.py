from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import BarbarianSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Barbarian import (
    BarbarianPathOfTheElementsFeatures,
)


@attr.dataclass
class BarbarianElementsLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Granted top-level (not as a Rage extension) so Elemental Overload
        # at level 14 can extend it.
        data.add_feature(BarbarianPathOfTheElementsFeatures.RagingElements())


@attr.dataclass
class BarbarianElementsLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BarbarianPathOfTheElementsFeatures.EchoOfTheElements())


@attr.dataclass
class BarbarianElementsLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BarbarianPathOfTheElementsFeatures.PrimordialBond())


@attr.dataclass
class BarbarianElementsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BarbarianPathOfTheElementsFeatures.ElementalOverload(),
            extends=BarbarianPathOfTheElementsFeatures.RagingElements,
        )


class BarbarianElementsCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_ELEMENTS.value,
            skills=skills,
        )


class BarbarianElementsMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_ELEMENTS.value,
            replace_spells=replace_spells,
        )
