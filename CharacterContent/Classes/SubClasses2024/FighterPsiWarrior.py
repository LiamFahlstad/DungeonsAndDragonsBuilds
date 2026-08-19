from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, FighterSubclass
from CharacterContent.Features.SubClassFeatures.Fighter import FighterPsiWarriorFeatures
from CharacterContent.Spells.SpellLists import WizardLevel5Spells
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterPsiWarriorLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.PsionicPower())
        return data


@attr.dataclass
class FighterPsiWarriorLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        psionic_power: FighterPsiWarriorFeatures.PsionicPower = (
            data.get_features_by_type(FighterPsiWarriorFeatures.PsionicPower)[0]
        )
        psionic_power.extend_feature(FighterPsiWarriorFeatures.TelekineticAdept())
        return data


@attr.dataclass
class FighterPsiWarriorLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.GuardedMind())
        return data


@attr.dataclass
class FighterPsiWarriorLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.BulwarkOfForce())
        return data


@attr.dataclass
class FighterPsiWarriorLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterPsiWarriorFeatures.TelekineticMaster())
        data.add_spell(
            WizardLevel5Spells.TELEKINESIS,
            Ability.INTELLIGENCE,
            additional_ruling="Always prepared; cast without a spell slot or components",
        )
        return data


class FighterPsiWarriorCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: FighterSkillsStatBlock,
    ):
        super().__init__(
            subclass=FighterSubclass.PSI_WARRIOR.value,
            skills=skills,
        )


class FighterPsiWarriorMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.PSI_WARRIOR.value,
            replace_spells=replace_spells,
        )
