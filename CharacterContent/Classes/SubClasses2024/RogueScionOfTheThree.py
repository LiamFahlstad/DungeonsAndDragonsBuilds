from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import RogueSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Rogue import (
    RogueScionOfTheThreeFeatures,
)
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures


@attr.dataclass
class RogueScionOfTheThreeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RogueScionOfTheThreeFeatures.Bloodthirst())
        data.add_feature(RogueScionOfTheThreeFeatures.DreadAllegiance())


@attr.dataclass
class RogueScionOfTheThreeLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RogueScionOfTheThreeFeatures.StrikeFear(), extends=RogueFeatures.SneakAttack
        )


@attr.dataclass
class RogueScionOfTheThreeLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RogueScionOfTheThreeFeatures.AuraOfMalevolence(),
            extends=RogueScionOfTheThreeFeatures.Bloodthirst,
        )


@attr.dataclass
class RogueScionOfTheThreeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RogueScionOfTheThreeFeatures.DreadIncarnate())


class RogueScionOfTheThreeCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=RogueSubclass.SCION_OF_THE_THREE.value,
            skills=skills,
        )


class RogueScionOfTheThreeMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.SCION_OF_THE_THREE.value,
            replace_spells=replace_spells,
        )
