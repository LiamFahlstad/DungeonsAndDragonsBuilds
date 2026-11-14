from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import PaladinEbonBladeRune, PaladinSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Paladin import PaladinEbonBladeFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    AbjurationLevel1Spells,
    AbjurationLevel5Spells,
    ClericLevel4Spells,
    ConjurationLevel4Spells,
    EvocationLevel1Spells,
    EvocationLevel2Spells,
    EvocationLevel3Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    NecromancyLevel1Spells,
    NecromancyLevel2Spells,
    NecromancyLevel3Spells,
    NecromancyLevel4Spells,
    NecromancyLevel5Spells,
    PaladinLevel5Spells,
    WizardLevel3Spells,
)

# Oath of the Ebon Blade Spells table, rune columns: (rune, Paladin level) ->
# spell. Each level builder takes the rune inscribed with Runeforging at that
# level and grants that column's spell.
_RUNE_SPELLS: dict[PaladinEbonBladeRune, dict[int, str]] = {
    PaladinEbonBladeRune.BLOOD: {
        3: NecromancyLevel1Spells.VAMPIRIC_BLOOD,
        5: EvocationLevel2Spells.SPIRITUAL_WEAPON,
        9: NecromancyLevel3Spells.LEECHING_STRIKE,
        13: ConjurationLevel4Spells.EVARDS_BLACK_TENTACLES,
        17: AbjurationLevel5Spells.BONESTORM,
    },
    PaladinEbonBladeRune.FROST: {
        3: EvocationLevel1Spells.CHAINS_OF_ICE,
        5: EvocationLevel2Spells.FROSTSCYTHE,
        9: EvocationLevel3Spells.REMORSELESS_WINTER,
        13: EvocationLevel4Spells.ICE_STORM,
        17: EvocationLevel5Spells.CONE_OF_COLD,
    },
    PaladinEbonBladeRune.UNHOLY: {
        3: NecromancyLevel1Spells.SCOURGE_STRIKE,
        5: NecromancyLevel2Spells.RAY_OF_ENFEEBLEMENT,
        9: NecromancyLevel3Spells.BESTOW_CURSE,
        13: NecromancyLevel4Spells.BLIGHT,
        17: NecromancyLevel5Spells.CONTAGION,
    },
}


@attr.dataclass
class PaladinEbonBladeLevel3(ClassBuilder.SubclassLevel3):
    rune: PaladinEbonBladeRune

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
        data.add_spell(AbjurationLevel1Spells.DEATH_GRIP)
        data.add_spell(_RUNE_SPELLS[self.rune][3])


@attr.dataclass
class PaladinEbonBladeLevel5(ClassBuilder.SubclassLevel5):
    rune: PaladinEbonBladeRune

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinEbonBladeFeatures.UndeadSteed(),
            extends=PaladinFeatures.FaithfulSteed,
        )
        data.add_spell(NecromancyLevel2Spells.DEATH_AND_DECAY)
        data.add_spell(_RUNE_SPELLS[self.rune][5])


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
    rune: PaladinEbonBladeRune

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel3Spells.SUMMON_UNDEAD)
        data.add_spell(_RUNE_SPELLS[self.rune][9])


@attr.dataclass
class PaladinEbonBladeLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinEbonBladeFeatures.RunicStrikes())


@attr.dataclass
class PaladinEbonBladeLevel13(ClassBuilder.SubclassLevel13):
    rune: PaladinEbonBladeRune

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        data.add_spell(_RUNE_SPELLS[self.rune][13])


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
    rune: PaladinEbonBladeRune

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(PaladinLevel5Spells.CIRCLE_OF_POWER)
        data.add_spell(_RUNE_SPELLS[self.rune][17])


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
