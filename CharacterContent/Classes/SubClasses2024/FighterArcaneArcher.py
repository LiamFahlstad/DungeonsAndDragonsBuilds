from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterCustomStarterClassArgs,
)
from Model.Grants import Grants
from CharacterContent.Spells.SpellLists import TransmutationLevel0Spells
from Core.Definitions import FighterSubclass, Skill
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.SubClassFeatures.Fighter import (
    FighterArcaneArcherFeatures,
)
from CharacterContent.Features.SubClassFeatures.Fighter.FighterArcaneArcherFeatures import (
    ARCANE_ARCHER_LORE_CANTRIPS,
    ArcaneShotOption,
)


@attr.dataclass
class FighterArcaneArcherLevel3(ClassBuilder.SubclassLevel3):
    cantrip: TransmutationLevel0Spells
    arcane_shot_option_1: ArcaneShotOption
    arcane_shot_option_2: ArcaneShotOption
    # Arcana and Nature, or a Fighter skill in place of each one you already have.
    skill_1: Skill = Skill.ARCANA
    skill_2: Skill = Skill.NATURE

    def __attrs_post_init__(self):
        if self.cantrip not in ARCANE_ARCHER_LORE_CANTRIPS:
            raise ValueError(
                f"Arcane Archer Lore: {self.cantrip} must be Druidcraft or Prestidigitation."
            )

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            FighterArcaneArcherFeatures.ArcaneArcherLore(
                self.cantrip, self.skill_1, self.skill_2
            )
        )
        arcane_shot = FighterArcaneArcherFeatures.ArcaneShot()
        data.add_feature(self.arcane_shot_option_1, extends=arcane_shot)
        data.add_feature(self.arcane_shot_option_2, extends=arcane_shot)
        data.add_feature(arcane_shot)


@attr.dataclass
class FighterArcaneArcherLevel7(ClassBuilder.SubclassLevel7):
    arcane_shot_option: ArcaneShotOption

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.arcane_shot_option, extends=FighterArcaneArcherFeatures.ArcaneShot
        )
        data.add_feature(FighterArcaneArcherFeatures.CurvingShot())
        data.add_feature(FighterArcaneArcherFeatures.MagicalAmmunition())


@attr.dataclass
class FighterArcaneArcherLevel10(ClassBuilder.SubclassLevel10):
    arcane_shot_option: ArcaneShotOption

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.arcane_shot_option, extends=FighterArcaneArcherFeatures.ArcaneShot
        )
        data.add_feature(
            FighterArcaneArcherFeatures.EverReadyShot(),
            extends=FighterArcaneArcherFeatures.ArcaneShot,
        )


@attr.dataclass
class FighterArcaneArcherLevel15(ClassBuilder.SubclassLevel15):
    arcane_shot_option: ArcaneShotOption

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.arcane_shot_option, extends=FighterArcaneArcherFeatures.ArcaneShot
        )
        data.add_feature(
            FighterArcaneArcherFeatures.IndomitableTeleport(),
            extends=FighterFeatures.Indomitable,
        )


@attr.dataclass
class FighterArcaneArcherLevel18(ClassBuilder.SubclassLevel18):
    arcane_shot_option: ArcaneShotOption

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            self.arcane_shot_option, extends=FighterArcaneArcherFeatures.ArcaneShot
        )
        data.add_feature(FighterArcaneArcherFeatures.MasterfulShots())


class FighterArcaneArcherCustomStarterClassArgs(FighterCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=FighterSubclass.ARCANE_ARCHER.value,
            skills=skills,
        )


class FighterArcaneArcherMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.ARCANE_ARCHER.value,
            replace_spells=replace_spells,
        )
