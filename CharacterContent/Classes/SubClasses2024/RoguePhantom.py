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
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures
from CharacterContent.Features.SubClassFeatures.Rogue import RoguePhantomFeatures


@attr.dataclass
class RoguePhantomLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            RoguePhantomFeatures.WailsFromTheGrave(), extends=RogueFeatures.SneakAttack
        )
        data.add_feature(RoguePhantomFeatures.WhispersOfTheDead())
        return data


@attr.dataclass
class RoguePhantomLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(RoguePhantomFeatures.TokensOfTheDeparted())
        data.add_feature(RoguePhantomFeatures.VoiceOfDeath())
        return data


@attr.dataclass
class RoguePhantomLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(RoguePhantomFeatures.GhostWalk())
        return data


@attr.dataclass
class RoguePhantomLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(RoguePhantomFeatures.DeathsFriend())
        return data


class RoguePhantomCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=RogueSubclass.PHANTOM.value,
            skills=skills,
        )


class RoguePhantomMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.PHANTOM.value,
            replace_spells=replace_spells,
        )
