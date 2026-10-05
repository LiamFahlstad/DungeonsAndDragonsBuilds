from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import PaladinSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Paladin import PaladinGeniesFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    EvocationLevel1Spells,
    PaladinLevel5Spells,
    TransmutationLevel0Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class PaladinGeniesLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            PaladinGeniesFeatures.ElementalSmite(),
            extends=PaladinFeatures.ChannelDivinity,
        )
        data.add_feature(PaladinGeniesFeatures.GeniesSplendor())
        data.add_spell(EvocationLevel1Spells.CHROMATIC_ORB)
        data.add_spell(TransmutationLevel0Spells.ELEMENTALISM)
        data.add_spell(EvocationLevel1Spells.THUNDEROUS_SMITE)
        return data


@attr.dataclass
class PaladinGeniesLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(WizardLevel2Spells.MIRROR_IMAGE)
        data.add_spell(WizardLevel2Spells.PHANTASMAL_FORCE)
        return data


@attr.dataclass
class PaladinGeniesLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            PaladinGeniesFeatures.AuraOfElementalShielding(),
            extends=PaladinFeatures.AuraOfProtection,
        )
        return data


@attr.dataclass
class PaladinGeniesLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(WizardLevel3Spells.FLY)
        data.add_spell(WizardLevel3Spells.GASEOUS_FORM)
        return data


@attr.dataclass
class PaladinGeniesLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(WizardLevel4Spells.CONJURE_MINOR_ELEMENTALS)
        data.add_spell(WizardLevel4Spells.SUMMON_ELEMENTAL)
        return data


@attr.dataclass
class PaladinGeniesLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(PaladinGeniesFeatures.ElementalRebuke())
        return data


@attr.dataclass
class PaladinGeniesLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(PaladinLevel5Spells.BANISHING_SMITE)
        data.add_spell(WizardLevel5Spells.CONTACT_OTHER_PLANE)
        return data


@attr.dataclass
class PaladinGeniesLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(PaladinGeniesFeatures.NobleScion())
        return data


class PaladinGeniesCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_GENIES.value,
            skills=skills,
        )


class PaladinGeniesMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_GENIES.value,
            replace_spells=replace_spells,
        )
