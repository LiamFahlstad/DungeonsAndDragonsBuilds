from typing import Optional, TypeAlias

import attr

import Core.Definitions as Definitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
    BardLevel5Spells,
    BardLevel6Spells,
    BardLevel7Spells,
    BardLevel8Spells,
    BardLevel9Spells,
)

BardSpellsUpTo2: TypeAlias = BardLevel1Spells | BardLevel2Spells

BardSpellsUpTo3: TypeAlias = BardSpellsUpTo2 | BardLevel3Spells

BardSpellsUpTo4: TypeAlias = BardSpellsUpTo3 | BardLevel4Spells

BardSpellsUpTo5: TypeAlias = BardSpellsUpTo4 | BardLevel5Spells

BardSpellsUpTo6: TypeAlias = BardSpellsUpTo5 | BardLevel6Spells

BardSpellsUpTo7: TypeAlias = BardSpellsUpTo6 | BardLevel7Spells

BardSpellsUpTo8: TypeAlias = BardSpellsUpTo7 | BardLevel8Spells

BardSpellsUpTo9: TypeAlias = BardSpellsUpTo8 | BardLevel9Spells


@attr.dataclass
class BardLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: BardLevel0Spells
    cantrip_2: BardLevel0Spells
    spell_1: BardLevel1Spells
    spell_2: BardLevel1Spells
    spell_3: BardLevel1Spells
    spell_4: BardLevel1Spells

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(BardFeatures.Spellcasting())
        data.add_feature(BardFeatures.BardicInspiration())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class BardLevel2(ClassBuilder.BaseClassLevel2):
    spell: BardLevel1Spells
    skill_expertise_1: Skill
    skill_expertise_2: Skill

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(BardFeatures.JackOfAllTrades())
        data.add_spell(self.spell)
        data.add_feature(
            BardFeatures.ExpertiseLevel1(
                skill_1=self.skill_expertise_1, skill_2=self.skill_expertise_2
            )
        )
        return data


@attr.dataclass
class BardLevel3(ClassBuilder.BaseClassLevel3):
    spell: BardSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: BardLevel0Spells
    spell: BardSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: BardSpellsUpTo3
    spell_2: BardSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            BardFeatures.FontOfInspiration(), extends=BardFeatures.BardicInspiration
        )
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class BardLevel6(ClassBuilder.BaseClassLevel6):
    spell: BardSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel7(ClassBuilder.BaseClassLevel7):
    spell: BardSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(BardFeatures.Countercharm())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: BardSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: BardSpellsUpTo5
    spell_2: BardSpellsUpTo5
    skill_expertise_1: Skill
    skill_expertise_2: Skill

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_feature(
            BardFeatures.ExpertiseLevel1(
                skill_1=self.skill_expertise_1, skill_2=self.skill_expertise_2
            )
        )
        return data


@attr.dataclass
class BardLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: BardLevel0Spells
    spell: BardSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        data.add_feature(BardFeatures.MagicalSecrets())
        return data


@attr.dataclass
class BardLevel11(ClassBuilder.BaseClassLevel11):
    spell: BardSpellsUpTo6

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BardLevel13(ClassBuilder.BaseClassLevel13):
    spell: BardSpellsUpTo7

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        return data


@attr.dataclass
class BardLevel15(ClassBuilder.BaseClassLevel15):
    spell: BardSpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BardLevel17(ClassBuilder.BaseClassLevel17):
    spell: BardSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel18(ClassBuilder.BaseClassLevel18):
    spell: BardSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(
            BardFeatures.SuperiorInspiration(), extends=BardFeatures.BardicInspiration
        )

        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: BardSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class BardLevel20(ClassBuilder.BaseClassLevel20):
    spell: BardSpellsUpTo9

    def add_features(self, data: Grants) -> Grants:
        data.add_feature(BardFeatures.WordsOfCreation())
        data.add_spell(self.spell)
        data.add_spell(BardLevel9Spells.POWER_WORD_HEAL)
        data.add_spell(BardLevel9Spells.POWER_WORD_KILL)
        return data


class BardCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
    ):
        super().__init__(
            base_class=CharacterClass.BARD,
            subclass=subclass,
            default_equipment=[
                Armor.LeatherArmor(),
                Weapons.Dagger(),
            ],
            skills=skills,
            armor_proficiencies=[Definitions.ArmorType.LIGHT],
            weapon_proficiencies=[Weapons.WeaponProficiency.SIMPLE],
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
            default_pack=Packs.EntertainersPack(),
        )


class BardMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.BARD,
            base_class_level_features=bard_level_features,
            base_class_level=bard_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
