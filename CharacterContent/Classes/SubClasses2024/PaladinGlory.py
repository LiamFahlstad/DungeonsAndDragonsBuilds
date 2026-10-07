from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import PaladinSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Paladin import PaladinGloryFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    BardLevel4Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel4Spells,
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class PaladinGloryLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinGloryFeatures.InspiringSmite(),
            extends=PaladinFeatures.ChannelDivinity,
        )
        data.add_feature(
            PaladinGloryFeatures.PeerlessAthlete(),
            extends=PaladinFeatures.ChannelDivinity,
        )
        data.add_spell(ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(PaladinLevel1Spells.HEROISM)


@attr.dataclass
class PaladinGloryLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)


@attr.dataclass
class PaladinGloryLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinGloryFeatures.AuraOfAlacrity(),
            extends=PaladinFeatures.AuraOfProtection,
        )


@attr.dataclass
class PaladinGloryLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)


@attr.dataclass
class PaladinGloryLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)


@attr.dataclass
class PaladinGloryLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinGloryFeatures.GloriousDefense())


@attr.dataclass
class PaladinGloryLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)


@attr.dataclass
class PaladinGloryLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinGloryFeatures.LivingLegend())


class PaladinGloryCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_GLORY.value,
            skills=skills,
        )


class PaladinGloryMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_GLORY.value,
            replace_spells=replace_spells,
        )
