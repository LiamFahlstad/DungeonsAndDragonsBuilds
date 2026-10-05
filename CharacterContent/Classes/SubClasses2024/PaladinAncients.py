from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import PaladinSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Paladin import PaladinAncientsFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    ConjurationLevel1Spells,
    ConjurationLevel2Spells,
    DivinationLevel1Spells,
    DruidLevel2Spells,
    RangerLevel3Spells,
    RangerLevel5Spells,
    WizardLevel4Spells,
)


@attr.dataclass
class PaladinAncientsLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            PaladinAncientsFeatures.NaturesWrath(),
            extends=PaladinFeatures.ChannelDivinity,
        )
        data.add_spell(ConjurationLevel1Spells.ENSNARING_STRIKE)
        data.add_spell(DivinationLevel1Spells.SPEAK_WITH_ANIMALS)
        return data


@attr.dataclass
class PaladinAncientsLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(ConjurationLevel2Spells.MISTY_STEP)
        data.add_spell(DruidLevel2Spells.MOONBEAM)
        return data


@attr.dataclass
class PaladinAncientsLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            PaladinAncientsFeatures.AuraOfWarding(),
            extends=PaladinFeatures.AuraOfProtection,
        )
        return data


@attr.dataclass
class PaladinAncientsLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(RangerLevel3Spells.PLANT_GROWTH)
        data.add_spell(RangerLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class PaladinAncientsLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(WizardLevel4Spells.ICE_STORM)
        data.add_spell(WizardLevel4Spells.STONESKIN)
        return data


@attr.dataclass
class PaladinAncientsLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(PaladinAncientsFeatures.UndyingSentinel())
        return data


@attr.dataclass
class PaladinAncientsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(RangerLevel5Spells.COMMUNE_WITH_NATURE)
        data.add_spell(RangerLevel5Spells.TREE_STRIDE)
        return data


@attr.dataclass
class PaladinAncientsLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            PaladinAncientsFeatures.ElderChampion(),
            extends=PaladinFeatures.AuraOfProtection,
        )
        return data


class PaladinAncientsCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_THE_ANCIENTS.value,
            skills=skills,
        )


class PaladinAncientsMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_THE_ANCIENTS.value,
            replace_spells=replace_spells,
        )
