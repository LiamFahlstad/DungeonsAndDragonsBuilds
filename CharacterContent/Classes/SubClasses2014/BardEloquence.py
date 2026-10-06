from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import BardSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Bard import BardEloquenceFeatures
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures


@attr.dataclass
class BardEloquenceLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BardEloquenceFeatures.SilverTongue())
        data.add_feature(
            BardEloquenceFeatures.UnsettlingWords(),
            extends=BardFeatures.BardicInspiration,
        )


@attr.dataclass
class BardEloquenceLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BardEloquenceFeatures.UnfailingInspiration(),
            extends=BardFeatures.BardicInspiration,
        )
        data.add_feature(BardEloquenceFeatures.UniversalSpeech())


@attr.dataclass
class BardEloquenceLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BardEloquenceFeatures.InfectiousInspiration(),
            extends=BardFeatures.BardicInspiration,
        )


class BardEloquenceCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BardSubclass2014.ELOQUENCE.value,
            skills=skills,
        )


class BardEloquenceMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.ELOQUENCE.value,
            replace_spells=replace_spells,
        )
