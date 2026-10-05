from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import PaladinSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Paladin import (
    PaladinRedemptionFeatures,
)
from CharacterContent.Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel2Spells,
    WizardLevel1Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class PaladinRedemptionLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(PaladinRedemptionFeatures.RedemptionSpells())
        data.add_feature(PaladinRedemptionFeatures.EmissaryOfPeace())
        data.add_feature(PaladinRedemptionFeatures.RebukeTheViolent())
        data.add_spell(ClericLevel1Spells.SANCTUARY)
        data.add_spell(WizardLevel1Spells.SLEEP)
        return data


@attr.dataclass
class PaladinRedemptionLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(ClericLevel2Spells.CALM_EMOTIONS)
        data.add_spell(ClericLevel2Spells.HOLD_PERSON)
        return data


@attr.dataclass
class PaladinRedemptionLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(PaladinRedemptionFeatures.AuraOfTheGuardian())
        return data


@attr.dataclass
class PaladinRedemptionLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(WizardLevel3Spells.COUNTERSPELL)
        data.add_spell(WizardLevel3Spells.HYPNOTIC_PATTERN)
        return data


@attr.dataclass
class PaladinRedemptionLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(WizardLevel4Spells.OTILUKES_RESILIENT_SPHERE)
        data.add_spell(WizardLevel4Spells.STONESKIN)
        return data


@attr.dataclass
class PaladinRedemptionLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(PaladinRedemptionFeatures.ProtectiveSpirit())
        return data


@attr.dataclass
class PaladinRedemptionLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(WizardLevel5Spells.HOLD_MONSTER)
        data.add_spell(WizardLevel5Spells.WALL_OF_FORCE)
        return data


@attr.dataclass
class PaladinRedemptionLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            PaladinRedemptionFeatures.AuraOfTheGuardianExpansion(),
            extends=PaladinRedemptionFeatures.AuraOfTheGuardian,
        )
        return data


@attr.dataclass
class PaladinRedemptionLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(PaladinRedemptionFeatures.EmissaryOfRedemption())
        return data


class PaladinRedemptionCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass2014.REDEMPTION.value,
            skills=skills,
        )


class PaladinRedemptionMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.REDEMPTION.value,
            replace_spells=replace_spells,
        )
