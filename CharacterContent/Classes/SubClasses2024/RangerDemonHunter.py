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
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    TransmutationLevel3Spells,
)

# Demon Hunter Spells table. The World of Warcraft spells (Throw Glaive, Sigil
# of Flame, Metamorphosis, Chaos Nova, Consume Soul, Soul Reap, Collapsing
# Star, Fel Rush, Eye Beam, Infernal Strike, Fiery Brand, Demon Spikes, Sigil
# of Chains) aren't in the spell data yet, so they're left out of the grants
# below; the Demon Hunter Spells feature still lists them.
_SPECIALIZATION_SPELLS: dict[DemonHunterSpecialization, dict[int, str]] = {
    DemonHunterSpecialization.DEVOURER: {
        # 3: Consume Soul, 9: Soul Reap, 13: Collapsing Star - not scraped yet.
        5: ConjurationLevel2Spells.MISTY_STEP,
        17: ConjurationLevel5Spells.STEEL_WIND_STRIKE,
    },
    DemonHunterSpecialization.HAVOC: {
        # 3: Fel Rush, 5: Eye Beam - not scraped yet.
        9: TransmutationLevel3Spells.BLINK,
        13: EvocationLevel4Spells.FIRE_SHIELD,
        17: ConjurationLevel5Spells.CONJURE_VOLLEY,
    },
    DemonHunterSpecialization.VENGEANCE: {
        # 3: Infernal Strike, 5: Fiery Brand, 9: Demon Spikes, 17: Sigil of
        # Chains - not scraped yet.
        13: AbjurationLevel4Spells.BANISHMENT,
    },
}


def _add_specialization_spell(
    data: Grants, specialization: DemonHunterSpecialization, ranger_level: int
) -> None:
    spell = _SPECIALIZATION_SPELLS[specialization].get(ranger_level)
    if spell is not None:
        data.add_spell(spell)


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
        # Spells (All) 3: Throw Glaive - not scraped yet.
        _add_specialization_spell(data, self.specialization, 3)


@attr.dataclass
class RangerDemonHunterLevel5(ClassBuilder.SubclassLevel5):
    specialization: DemonHunterSpecialization

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Spells (All) 5: Sigil of Flame - not scraped yet.
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
        # Spells (All) 9: Metamorphosis - not scraped yet.
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
        # Spells (All) 13: Chaos Nova - not scraped yet.
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
