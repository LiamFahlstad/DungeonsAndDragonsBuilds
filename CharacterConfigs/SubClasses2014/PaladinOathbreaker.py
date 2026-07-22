from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import PaladinSubclass2014
from Features.SubClassFeatures2014.Paladin import PaladinOathbreakerFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel3Spells,
    ClericLevel5Spells,
    WarlockLevel1Spells,
    WarlockLevel2Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class OathbreakerPaladinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinOathbreakerFeatures.OathbreakerSpells())
        data.add_feature(PaladinOathbreakerFeatures.ControlUndead())
        data.add_feature(PaladinOathbreakerFeatures.DreadfulAspect())
        data.add_spell(WarlockLevel1Spells.HELLISH_REBUKE)
        data.add_spell(ClericLevel1Spells.INFLICT_WOUNDS)
        return data


@attr.dataclass
class OathbreakerPaladinLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WarlockLevel2Spells.CROWN_OF_MADNESS)
        data.add_spell(WarlockLevel2Spells.DARKNESS)
        return data


@attr.dataclass
class OathbreakerPaladinLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinOathbreakerFeatures.AuraOfHate())
        return data


@attr.dataclass
class OathbreakerPaladinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel3Spells.ANIMATE_DEAD)
        data.add_spell(ClericLevel3Spells.BESTOW_CURSE)
        return data


@attr.dataclass
class OathbreakerPaladinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.BLIGHT)
        data.add_spell(WizardLevel4Spells.CONFUSION)
        return data


@attr.dataclass
class OathbreakerPaladinLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinOathbreakerFeatures.SupernaturalResistance())
        return data


@attr.dataclass
class OathbreakerPaladinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel5Spells.CONTAGION)
        data.add_spell(WizardLevel5Spells.DOMINATE_PERSON)
        return data


@attr.dataclass
class OathbreakerPaladinLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_hate: PaladinOathbreakerFeatures.AuraOfHate = (
            data.get_features_by_type(PaladinOathbreakerFeatures.AuraOfHate)[0]
        )
        aura_of_hate.extend_feature(PaladinOathbreakerFeatures.AuraOfHateExpansion())
        return data


@attr.dataclass
class OathbreakerPaladinLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinOathbreakerFeatures.DreadLord())
        return data


class PaladinOathbreakerCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass2014.OATHBREAKER.value,
            skills=skills,
        )


class PaladinOathbreakerMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.OATHBREAKER.value,
            replace_spells=replace_spells,
        )
