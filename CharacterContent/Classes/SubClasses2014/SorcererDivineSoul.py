from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import SorcererSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Sorcerer import SorcererDivineSoulFeatures
from CharacterContent.Features.ClassFeatures.Sorcerer import SorcererFeatures
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


@attr.dataclass
class SorcererDivineSoulLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        spellcasting: SorcererFeatures.Spellcasting = data.get_features_by_type(
            SorcererFeatures.Spellcasting
        )[0]
        spellcasting.extend_feature(SorcererDivineSoulFeatures.DivineMagic())
        data.add_feature(SorcererDivineSoulFeatures.FavoredByTheGods())
        return data


@attr.dataclass
class SorcererDivineSoulLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDivineSoulFeatures.EmpoweredHealing())
        return data


@attr.dataclass
class SorcererDivineSoulLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDivineSoulFeatures.AngelicForm())
        return data


@attr.dataclass
class SorcererDivineSoulLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(SorcererDivineSoulFeatures.UnearthlyRecovery())
        return data


class SorcererDivineSoulCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: SorcererSkillsStatBlock,
    ):
        super().__init__(
            subclass=SorcererSubclass2014.DIVINE_SOUL.value,
            skills=skills,
        )


class SorcererDivineSoulMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass2014.DIVINE_SOUL.value,
            replace_spells=replace_spells,
        )
