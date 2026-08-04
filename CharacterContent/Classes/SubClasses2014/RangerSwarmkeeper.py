from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RangerSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Ranger import RangerSwarmkeeperFeatures
from CharacterContent.Spells.SpellLists import (
    WizardLevel0Spells,
    DruidLevel1Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    DruidLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class RangerSwarmkeeperLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerSwarmkeeperFeatures.GatheredSwarm())
        data.add_feature(RangerSwarmkeeperFeatures.SwarmkeeperMagic())
        data.add_cantrip(WizardLevel0Spells.MAGE_HAND)
        data.add_spell(DruidLevel1Spells.FAERIE_FIRE)
        return data


@attr.dataclass
class RangerSwarmkeeperLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel2Spells.WEB)
        return data


@attr.dataclass
class RangerSwarmkeeperLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerSwarmkeeperFeatures.WrithingTide())
        return data


@attr.dataclass
class RangerSwarmkeeperLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.GASEOUS_FORM)
        return data


@attr.dataclass
class RangerSwarmkeeperLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerSwarmkeeperFeatures.MightySwarm())
        return data


@attr.dataclass
class RangerSwarmkeeperLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.ARCANE_EYE)
        return data


@attr.dataclass
class RangerSwarmkeeperLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerSwarmkeeperFeatures.SwarmingDispersal())
        return data


@attr.dataclass
class RangerSwarmkeeperLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.INSECT_PLAGUE)
        return data


class RangerSwarmkeeperCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass2014.SWARMKEEPER.value,
            skills=skills,
        )


class RangerSwarmkeeperMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass2014.SWARMKEEPER.value,
            replace_spells=replace_spells,
        )
