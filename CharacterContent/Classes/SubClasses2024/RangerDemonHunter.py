from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import RangerSubclass, Skill
from CharacterContent.Features.ClassFeatures.Ranger import RangerFeatures
from CharacterContent.Features.SubClassFeatures.Ranger import RangerDemonHunterFeatures
from CharacterContent.Features.SubClassFeatures.Ranger.RangerDemonHunterFeatures import (
    DemonHunterSpecialization,
)
from CharacterContent.Spells.SpellLists import (
    AbjurationLevel4Spells,
    ConjurationLevel2Spells,
    ConjurationLevel5Spells,
    EvocationLevel1Spells,
    EvocationLevel2Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    NecromancyLevel1Spells,
    NecromancyLevel3Spells,
    TransmutationLevel1Spells,
    TransmutationLevel3Spells,
)

# Demon Hunter Spells table, the specialization columns: (column, Ranger
# level) -> spell.
_SPECIALIZATION_SPELLS: dict[DemonHunterSpecialization, dict[int, str]] = {
    DemonHunterSpecialization.DEVOURER: {
        3: NecromancyLevel1Spells.CONSUME_SOUL,
        5: ConjurationLevel2Spells.MISTY_STEP,
        9: NecromancyLevel3Spells.SOUL_REAP,
        13: EvocationLevel4Spells.COLLAPSING_STAR,
        17: ConjurationLevel5Spells.STEEL_WIND_STRIKE,
    },
    DemonHunterSpecialization.HAVOC: {
        3: TransmutationLevel1Spells.FEL_RUSH,
        5: EvocationLevel2Spells.EYE_BEAM,
        9: TransmutationLevel3Spells.BLINK,
        13: EvocationLevel4Spells.FIRE_SHIELD,
        17: ConjurationLevel5Spells.CONJURE_VOLLEY,
    },
    DemonHunterSpecialization.VENGEANCE: {
        3: EvocationLevel1Spells.INFERNAL_STRIKE,
        5: EvocationLevel2Spells.FIERY_BRAND,
        9: TransmutationLevel3Spells.DEMON_SPIKES,
        13: AbjurationLevel4Spells.BANISHMENT,
        17: ConjurationLevel5Spells.SIGIL_OF_CHAINS,
    },
}


def _add_specialization_spell(
    data: Grants, specialization: DemonHunterSpecialization, ranger_level: int
) -> None:
    data.add_spell(_SPECIALIZATION_SPELLS[specialization][ranger_level])


@attr.dataclass
class RangerDemonHunterLevel3(ClassBuilder.SubclassLevel3):
    specialization: DemonHunterSpecialization

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # The source's Level 1 (Spellcasting) and Level 2 (Deft Explorer,
        # Fighting Style) notes are folded into the subclass's level 3 grant.
        data.add_feature(
            RangerDemonHunterFeatures.DemonHunterSpellcasting(),
            extends=RangerFeatures.Spellcasting,
        )
        data.add_feature(
            RangerDemonHunterFeatures.DemonHunterLanguages(),
            extends=RangerFeatures.DeftExplorerLanguages,
        )
        data.add_feature(RangerDemonHunterFeatures.VoidWarrior())
        data.add_feature(
            RangerDemonHunterFeatures.DemonHunterSpells(
                specialization=self.specialization
            )
        )
        data.add_feature(RangerDemonHunterFeatures.SoulFragments())
        data.add_feature(RangerDemonHunterFeatures.SpectralSight())
        data.add_spell(EvocationLevel1Spells.THROW_GLAIVE)
        _add_specialization_spell(data, self.specialization, 3)


@attr.dataclass
class RangerDemonHunterLevel5(ClassBuilder.SubclassLevel5):
    specialization: DemonHunterSpecialization

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(EvocationLevel2Spells.SIGIL_OF_FLAME)
        _add_specialization_spell(data, self.specialization, 5)


@attr.dataclass
class RangerDemonHunterLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RangerDemonHunterFeatures.Torment(), extends=RangerFeatures.FavoredEnemy
        )


@attr.dataclass
class RangerDemonHunterLevel9(ClassBuilder.SubclassLevel9):
    specialization: DemonHunterSpecialization

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(TransmutationLevel3Spells.METAMORPHOSIS)
        _add_specialization_spell(data, self.specialization, 9)


@attr.dataclass
class RangerDemonHunterLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RangerDemonHunterFeatures.IllidariKnowledge(),
            extends=RangerDemonHunterFeatures.SoulFragments,
        )


@attr.dataclass
class RangerDemonHunterLevel13(ClassBuilder.SubclassLevel13):
    specialization: DemonHunterSpecialization

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(EvocationLevel4Spells.CHAOS_NOVA)
        _add_specialization_spell(data, self.specialization, 13)


@attr.dataclass
class RangerDemonHunterLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            RangerDemonHunterFeatures.SoulShatter(),
            extends=RangerDemonHunterFeatures.SoulFragments,
        )


@attr.dataclass
class RangerDemonHunterLevel17(ClassBuilder.SubclassLevel17):
    specialization: DemonHunterSpecialization

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(EvocationLevel5Spells.DESTRUCTIVE_WAVE)
        _add_specialization_spell(data, self.specialization, 17)


@attr.dataclass
class RangerDemonHunterLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Replaces Feral Senses, which the base Ranger level 18 still grants:
        # a subclass can't remove a base-class feature yet.
        data.add_feature(RangerDemonHunterFeatures.ImprovedSpectralSight())


class RangerDemonHunterCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=RangerSubclass.DEMON_HUNTER.value,
            skills=skills,
        )


class RangerDemonHunterMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.DEMON_HUNTER.value,
            replace_spells=replace_spells,
        )
