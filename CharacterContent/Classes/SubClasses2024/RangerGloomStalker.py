from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import RangerSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Ranger import RangerGloomStalkerFeatures
from CharacterContent.Spells.SpellLists import (
    BardLevel4Spells,
    ClericLevel4Spells,
    IllusionLevel1Spells,
    IllusionLevel3Spells,
    IllusionLevel4Spells,
    IllusionLevel5Spells,
    TransmutationLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class RangerGloomStalkerLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RangerGloomStalkerFeatures.DreadAmbusher())
        data.add_feature(RangerGloomStalkerFeatures.UmbralSight())
        data.add_feature(RangerGloomStalkerFeatures.GloomStalkerSpells())
        data.add_spell(IllusionLevel1Spells.DISGUISE_SELF)


@attr.dataclass
class RangerGloomStalkerLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(TransmutationLevel2Spells.ROPE_TRICK)


@attr.dataclass
class RangerGloomStalkerLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RangerGloomStalkerFeatures.IronMind())


@attr.dataclass
class RangerGloomStalkerLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(IllusionLevel3Spells.FEAR)


@attr.dataclass
class RangerGloomStalkerLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RangerGloomStalkerFeatures.StalkersFlurry(),
            extends=RangerGloomStalkerFeatures.DreadAmbusher,
        )


@attr.dataclass
class RangerGloomStalkerLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(IllusionLevel4Spells.GREATER_INVISIBILITY)


@attr.dataclass
class RangerGloomStalkerLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RangerGloomStalkerFeatures.ShadowyDodge())


@attr.dataclass
class RangerGloomStalkerLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(IllusionLevel5Spells.SEEMING)


class RangerGloomStalkerCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=RangerSubclass.GLOOM_STALKER.value,
            skills=skills,
        )


class RangerGloomStalkerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.GLOOM_STALKER.value,
            replace_spells=replace_spells,
        )
