from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, FighterSubclass
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.SubClassFeatures.Fighter import FighterBanneretFeatures
from CharacterContent.Spells.SpellLists import DivinationLevel1Spells
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterBanneretLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterBanneretFeatures.KnightlyEnvoy())
        data.add_feature(FighterBanneretFeatures.GroupRecovery())
        data.add_spell(
            DivinationLevel1Spells.COMPREHEND_LANGUAGES,
            Ability.CHARISMA,
            additional_ruling="Ritual only",
        )
        return data


@attr.dataclass
class FighterBanneretLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        group_recovery: FighterBanneretFeatures.GroupRecovery = data.get_features_by_type(
            FighterBanneretFeatures.GroupRecovery
        )[0]
        group_recovery.extend_feature(FighterBanneretFeatures.TeamTactics())
        return data


@attr.dataclass
class FighterBanneretLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        action_surge: FighterFeatures.ActionSurge = data.get_features_by_type(
            FighterFeatures.ActionSurge
        )[0]
        action_surge.extend_feature(FighterBanneretFeatures.RallyingSurge())
        return data


@attr.dataclass
class FighterBanneretLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        indomitable: FighterFeatures.Indomitable = data.get_features_by_type(
            FighterFeatures.Indomitable
        )[0]
        indomitable.extend_feature(FighterBanneretFeatures.SharedResilience())
        return data


@attr.dataclass
class FighterBanneretLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterBanneretFeatures.InspiringCommander())
        return data


class FighterBanneretCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
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
