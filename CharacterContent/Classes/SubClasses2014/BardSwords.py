from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import BardSubclass2014, Skill
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Features.SubClassFeatures2014.Bard import BardSwordsFeatures


@attr.dataclass
class BardSwordsLevel3(ClassBuilder.SubclassLevel3):
    fighting_style: FightingStyles.FightingStyle

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BardSwordsFeatures.BonusProficiencies())
        data.add_feature(BardSwordsFeatures.BladeFlourish())
        data.add_fighting_style(self.fighting_style)
        return data


@attr.dataclass
class BardSwordsLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BardSwordsFeatures.ExtraAttack())
        return data


@attr.dataclass
class BardSwordsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            BardSwordsFeatures.MastersFlourish(),
            extends=BardSwordsFeatures.BladeFlourish,
        )
        return data


class BardSwordsCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BardSubclass2014.SWORD.value,
            skills=skills,
        )


class BardSwordsMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.SWORD.value,
            replace_spells=replace_spells,
        )
