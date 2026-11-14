from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import PaladinSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Paladin import PaladinEbonBladeFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    ClericLevel4Spells,
    PaladinLevel5Spells,
    WizardLevel3Spells,
)

# Oath of the Ebon Blade Spells: only the Spells (All) column is granted. The
# rune columns depend on the rune inscribed on the weapon, which can change
# at every level; the Oath of the Ebon Blade Spells card lists them.


@attr.dataclass
class PaladinEbonBladeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Death Coil (source level 1) and Runic Smite (source level 2) come
        # with the level-3 subclass grant.
        data.add_feature(PaladinEbonBladeFeatures.DeathCoil())
        data.add_feature(PaladinEbonBladeFeatures.RunicSmite())
        data.add_feature(PaladinEbonBladeFeatures.EbonBladeSpells())
        data.add_feature(PaladinEbonBladeFeatures.Runeforging())
        data.add_feature(
            PaladinEbonBladeFeatures.RunicPower(),
            extends=PaladinFeatures.ChannelDivinity,
        )
        # Death Grip is not in the spell data yet.


@attr.dataclass
class PaladinEbonBladeLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinEbonBladeFeatures.UndeadSteed(),
            extends=PaladinFeatures.FaithfulSteed,
        )
        # Death and Decay is not in the spell data yet.


@attr.dataclass
class PaladinEbonBladeLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinEbonBladeFeatures.AuraOfDeathlyEndurance(),
            extends=PaladinFeatures.AuraOfProtection,
        )


@attr.dataclass
class PaladinEbonBladeLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel3Spells.SUMMON_UNDEAD)


@attr.dataclass
class PaladinEbonBladeLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinEbonBladeFeatures.RunicStrikes())


@attr.dataclass
class PaladinEbonBladeLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)


@attr.dataclass
class PaladinEbonBladeLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinEbonBladeFeatures.ImprovedDeathCoil(),
            extends=PaladinEbonBladeFeatures.DeathCoil,
        )


@attr.dataclass
class PaladinEbonBladeLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinEbonBladeFeatures.RunicMastery())


@attr.dataclass
class PaladinEbonBladeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(PaladinLevel5Spells.CIRCLE_OF_POWER)


@attr.dataclass
class PaladinEbonBladeLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinEbonBladeFeatures.AspectOfTheHorsemen())


class PaladinEbonBladeCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_THE_EBON_BLADE.value,
            skills=skills,
        )


class PaladinEbonBladeMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_THE_EBON_BLADE.value,
            replace_spells=replace_spells,
        )
