from typing import Optional, TypeAlias

import attr

import Core.Definitions as Definitions
from Model.Character import Character
from Model.Grants import Grants
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    EpicBoon,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Artificer import ArtificerFeatures
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items, Packs
from CharacterContent.Spells.SpellLists import (
    ArtificerLevel0Spells,
    ArtificerLevel1Spells,
    ArtificerLevel2Spells,
    ArtificerLevel3Spells,
    ArtificerLevel4Spells,
    ArtificerLevel5Spells,
)

# Artificer is a half-caster whose spell slots never exceed 5th level.
ArtificerSpellsUpTo2: TypeAlias = ArtificerLevel1Spells | ArtificerLevel2Spells

ArtificerSpellsUpTo3: TypeAlias = ArtificerSpellsUpTo2 | ArtificerLevel3Spells

ArtificerSpellsUpTo4: TypeAlias = ArtificerSpellsUpTo3 | ArtificerLevel4Spells

ArtificerSpellsUpTo5: TypeAlias = ArtificerSpellsUpTo4 | ArtificerLevel5Spells


@attr.dataclass
class ArtificerLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: ArtificerLevel0Spells
    cantrip_2: ArtificerLevel0Spells
    spell_1: ArtificerLevel1Spells
    spell_2: ArtificerLevel1Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ArtificerFeatures.Spellcasting())
        data.add_feature(ArtificerFeatures.TinkersMagic())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel2(ClassBuilder.BaseClassLevel2):
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ArtificerFeatures.ReplicateMagicItem())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel3(ClassBuilder.BaseClassLevel3):
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    spell: ArtificerLevel1Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel5(ClassBuilder.BaseClassLevel5):
    spell: ArtificerSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            ArtificerFeatures.MagicItemTinker(),
            extends=ArtificerFeatures.ReplicateMagicItem,
        )
        return data


@attr.dataclass
class ArtificerLevel7(ClassBuilder.BaseClassLevel7):
    spell: ArtificerSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ArtificerFeatures.FlashofGenius())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ArtificerLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: ArtificerSpellsUpTo3
    spell_2: ArtificerSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: ArtificerLevel0Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ArtificerFeatures.MagicItemAdept())
        data.add_cantrip(self.cantrip)
        return data


@attr.dataclass
class ArtificerLevel11(ClassBuilder.BaseClassLevel11):
    spell: ArtificerSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ArtificerFeatures.SpellStoringItem())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ArtificerLevel13(ClassBuilder.BaseClassLevel13):
    spell: ArtificerSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel14(ClassBuilder.BaseClassLevel14):
    cantrip: ArtificerLevel0Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            ArtificerFeatures.AdvancedArtifice(),
            extends=ArtificerFeatures.FlashofGenius,
        )
        data.add_cantrip(self.cantrip)
        return data


@attr.dataclass
class ArtificerLevel15(ClassBuilder.BaseClassLevel15):
    spell: ArtificerSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class ArtificerLevel17(ClassBuilder.BaseClassLevel17):
    spell_1: ArtificerSpellsUpTo5
    spell_2: ArtificerSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class ArtificerLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(ArtificerFeatures.MagicItemMaster())
        return data


@attr.dataclass
class ArtificerLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: ArtificerSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class ArtificerLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(
            ArtificerFeatures.SoulOfArtifice(), extends=ArtificerFeatures.FlashofGenius
        )
        return data


class ArtificerCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
    ):
        super().__init__(
            base_class=CharacterClass.ARTIFICER,
            subclass=subclass,
            default_equipment=[
                Armor.StuddedLeatherArmor(),
                Weapons.Dagger(),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.SHIELD,
            ],
            weapon_proficiencies=[Weapons.WeaponProficiency.SIMPLE],
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
            default_pack=Packs.DungeoneersPack(),
        )


class ArtificerMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.ARTIFICER,
            base_class_level_features=artificer_level_features,
            base_class_level=artificer_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
