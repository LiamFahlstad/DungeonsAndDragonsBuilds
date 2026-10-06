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
from CharacterContent.Features.SubClassFeatures2014.Bard import BardWhispersFeatures
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures


@attr.dataclass
class BardWhispersLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            BardWhispersFeatures.PsychicBlades(), extends=BardFeatures.BardicInspiration
        )
        data.add_feature(BardWhispersFeatures.WordsOfTerror())


@attr.dataclass
class BardWhispersLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BardWhispersFeatures.MantleOfWhispers())


@attr.dataclass
class BardWhispersLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(BardWhispersFeatures.ShadowLore())


class BardWhispersCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BardSubclass2014.WHISPERS.value,
            skills=skills,
        )


class BardWhispersMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.WHISPERS.value,
            replace_spells=replace_spells,
        )
