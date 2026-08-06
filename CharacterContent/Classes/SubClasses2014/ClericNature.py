from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericNatureFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericNatureLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericNatureFeatures.AcolyteOfNature())
        data.add_feature(ClericNatureFeatures.BonusProficiency())
        data.add_feature(ClericNatureFeatures.NatureDomainSpells())
        data.add_feature(ClericNatureFeatures.CharmAnimalsAndPlantsChannelDivinity())
        return data


@attr.dataclass
class ClericNatureLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericNatureFeatures.DampenElements())
        return data


@attr.dataclass
class ClericNatureLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericNatureFeatures.DivineStrike())
        return data


@attr.dataclass
class ClericNatureLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        charm_animals_and_plants: ClericNatureFeatures.CharmAnimalsAndPlantsChannelDivinity = (
            data.get_features_by_type(
                ClericNatureFeatures.CharmAnimalsAndPlantsChannelDivinity
            )[0]
        )
        charm_animals_and_plants.extend_feature(ClericNatureFeatures.MasterOfNature())
        return data


class ClericNatureCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.NATURE.value,
            skills=skills,
        )


class ClericNatureMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.NATURE.value,
            replace_spells=replace_spells,
        )
