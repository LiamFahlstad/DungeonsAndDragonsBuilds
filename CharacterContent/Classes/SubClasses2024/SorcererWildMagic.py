from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.SorcererBase import (
    SorcererMulticlassBuilder,
    SorcererCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import SorcererSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Sorcerer import (
    SorcererWildMagicFeatures,
)


@attr.dataclass
class SorcererWildMagicLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(SorcererWildMagicFeatures.WildMagicSurge())
        data.add_feature(
            SorcererWildMagicFeatures.WildMagicSurgeTable(),
            extends=SorcererWildMagicFeatures.WildMagicSurge,
        )
        data.add_feature(SorcererWildMagicFeatures.TidesOfChaos())
        return data


@attr.dataclass
class SorcererWildMagicLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(SorcererWildMagicFeatures.BendLuck())
        return data


@attr.dataclass
class SorcererWildMagicLevel14(ClassBuilder.SubclassLevel14):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            SorcererWildMagicFeatures.ControlledChaos(),
            extends=SorcererWildMagicFeatures.WildMagicSurge,
        )
        return data


@attr.dataclass
class SorcererWildMagicLevel18(ClassBuilder.SubclassLevel18):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            SorcererWildMagicFeatures.TamedSurge(),
            extends=SorcererWildMagicFeatures.WildMagicSurge,
        )
        return data


class SorcererWildMagicCustomStarterClassArgs(SorcererCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=SorcererSubclass.WILD_MAGIC.value,
            skills=skills,
        )


class SorcererWildMagicMulticlassBuilder(SorcererMulticlassBuilder):

    def __init__(
        self,
        sorcerer_level_features: ClassBuilder.BaseClassLevelFeatures,
        sorcerer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            sorcerer_level_features=sorcerer_level_features,
            sorcerer_level=sorcerer_level,
            subclass=SorcererSubclass.WILD_MAGIC.value,
            replace_spells=replace_spells,
        )
