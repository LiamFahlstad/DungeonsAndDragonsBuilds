from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import RogueSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Rogue import RogueThiefFeatures
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures


@attr.dataclass
class RogueThiefLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RogueThiefFeatures.FastHands())
        data.add_feature(RogueThiefFeatures.SecondStoryWork())


@attr.dataclass
class RogueThiefLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RogueThiefFeatures.SupremeSneak(), extends=RogueFeatures.SneakAttack
        )


@attr.dataclass
class RogueThiefLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RogueThiefFeatures.UseMagicDevice())


@attr.dataclass
class RogueThiefLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RogueThiefFeatures.ThiefsReflexes())


class RogueThiefCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=RogueSubclass.THIEF.value,
            skills=skills,
        )


class RogueThiefMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.THIEF.value,
            replace_spells=replace_spells,
        )
