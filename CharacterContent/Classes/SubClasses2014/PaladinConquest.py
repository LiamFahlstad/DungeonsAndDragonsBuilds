from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import PaladinSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Paladin import PaladinConquestFeatures
from CharacterContent.Spells.SpellLists import (
    WarlockLevel1Spells,
    PaladinLevel1Spells,
    ClericLevel2Spells,
    WizardLevel3Spells,
    DruidLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class PaladinConquestLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinConquestFeatures.ConquestSpells())
        data.add_feature(PaladinConquestFeatures.ConqueringPresence())
        data.add_feature(PaladinConquestFeatures.GuidedStrike())
        data.add_spell(WarlockLevel1Spells.ARMOR_OF_AGATHYS)
        data.add_spell(PaladinLevel1Spells.COMMAND)
        return data


@attr.dataclass
class PaladinConquestLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.HOLD_PERSON)
        data.add_spell(ClericLevel2Spells.SPIRITUAL_WEAPON)
        return data


@attr.dataclass
class PaladinConquestLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinConquestFeatures.AuraOfConquest())
        return data


@attr.dataclass
class PaladinConquestLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.BESTOW_CURSE)
        data.add_spell(WizardLevel3Spells.FEAR)
        return data


@attr.dataclass
class PaladinConquestLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.DOMINATE_BEAST)
        data.add_spell(DruidLevel4Spells.STONESKIN)
        return data


@attr.dataclass
class PaladinConquestLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinConquestFeatures.ScornfulRebuke())
        return data


@attr.dataclass
class PaladinConquestLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.CLOUDKILL)
        data.add_spell(WizardLevel5Spells.DOMINATE_PERSON)
        return data


@attr.dataclass
class PaladinConquestLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_conquest: PaladinConquestFeatures.AuraOfConquest = (
            data.get_features_by_type(PaladinConquestFeatures.AuraOfConquest)[0]
        )
        aura_of_conquest.extend_feature(PaladinConquestFeatures.AuraOfConquestExpansion())
        return data


@attr.dataclass
class PaladinConquestLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinConquestFeatures.InvincibleConqueror())
        return data


class PaladinConquestCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass2014.CONQUEST.value,
            skills=skills,
        )


class PaladinConquestMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.CONQUEST.value,
            replace_spells=replace_spells,
        )
