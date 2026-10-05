from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import RogueSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Rogue import RogueAssassinFeatures
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures


@attr.dataclass
class RogueAssassinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(RogueAssassinFeatures.Assassinate())
        data.add_feature(RogueAssassinFeatures.AssassinsTools())
        return data


@attr.dataclass
class RogueAssassinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(RogueAssassinFeatures.InfiltrationExpertise())
        return data


@attr.dataclass
class RogueAssassinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            RogueFeatures.CunningStrike(), extends=RogueFeatures.SneakAttack
        )
        data.add_feature(
            RogueAssassinFeatures.EnvenomWeapons(), extends=RogueFeatures.SneakAttack
        )
        return data


@attr.dataclass
class RogueAssassinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            RogueFeatures.CunningStrike(), extends=RogueFeatures.SneakAttack
        )
        data.add_feature(RogueAssassinFeatures.DeathStrike())
        return data


class RogueAssassinCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=RogueSubclass.ASSASSIN.value,
            skills=skills,
        )


class RogueAssassinMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.ASSASSIN.value,
            replace_spells=replace_spells,
        )
