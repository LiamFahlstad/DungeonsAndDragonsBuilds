from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import WarlockSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Warlock import WarlockArchfeyFeatures
from CharacterContent.Spells.SpellLists import (
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    DruidLevel4Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    WarlockLevel2Spells,
)


@attr.dataclass
class WarlockArchfeyLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WarlockArchfeyFeatures.ArchfeySpells())
        data.add_feature(WarlockArchfeyFeatures.StepsOfTheFey())
        data.add_spell(BardLevel1Spells.FAERIE_FIRE)
        data.add_spell(BardLevel2Spells.CALM_EMOTIONS)
        data.add_spell(WarlockLevel2Spells.MISTY_STEP)
        data.add_spell(BardLevel2Spells.PHANTASMAL_FORCE)
        data.add_spell(BardLevel1Spells.SLEEP)
        return data


@attr.dataclass
class WarlockArchfeyLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SorcererLevel3Spells.BLINK)
        data.add_spell(BardLevel3Spells.PLANT_GROWTH)
        return data


@attr.dataclass
class WarlockArchfeyLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            WarlockArchfeyFeatures.MistyEscape(),
            extends=WarlockArchfeyFeatures.StepsOfTheFey,
        )
        return data


@attr.dataclass
class WarlockArchfeyLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(DruidLevel4Spells.DOMINATE_BEAST)
        data.add_spell(SorcererLevel4Spells.GREATER_INVISIBILITY)
        return data


@attr.dataclass
class WarlockArchfeyLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SorcererLevel5Spells.DOMINATE_PERSON)
        data.add_spell(SorcererLevel5Spells.SEEMING)
        return data


@attr.dataclass
class WarlockArchfeyLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WarlockArchfeyFeatures.BeguilingDefenses())
        return data


@attr.dataclass
class WarlockArchfeyLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(WarlockArchfeyFeatures.BewitchingMagic())
        return data


class WarlockArchfeyCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_ARCHFEY.value,
            skills=skills,
        )


class WarlockArchfeyMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_ARCHFEY.value,
            replace_spells=replace_spells,
        )
