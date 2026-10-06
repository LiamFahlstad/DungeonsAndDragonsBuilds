from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Ability, FighterSubclass, Skill
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.SubClassFeatures.Fighter import FighterBanneretFeatures
from CharacterContent.Spells.SpellLists import DivinationLevel1Spells


@attr.dataclass
class FighterBanneretLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterBanneretFeatures.KnightlyEnvoy())
        data.add_feature(FighterBanneretFeatures.GroupRecovery())
        data.add_spell(
            DivinationLevel1Spells.COMPREHEND_LANGUAGES,
            Ability.CHARISMA,
            additional_ruling="Ritual only",
        )


@attr.dataclass
class FighterBanneretLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterBanneretFeatures.TeamTactics(),
            extends=FighterBanneretFeatures.GroupRecovery,
        )


@attr.dataclass
class FighterBanneretLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterBanneretFeatures.RallyingSurge(), extends=FighterFeatures.ActionSurge
        )


@attr.dataclass
class FighterBanneretLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterBanneretFeatures.SharedResilience(),
            extends=FighterFeatures.Indomitable,
        )


@attr.dataclass
class FighterBanneretLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(FighterBanneretFeatures.InspiringCommander())


class FighterBanneretCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=FighterSubclass.BANNERET.value,
            skills=skills,
        )


class FighterBanneretMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.BANNERET.value,
            replace_spells=replace_spells,
        )
