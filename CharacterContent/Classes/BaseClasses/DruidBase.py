from typing import Optional, Type, TypeAlias

import attr

import Core.Definitions as Definitions
from Model.Creatures.Combatants import ExtendedCombatantData
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Model.Character import Character, SpellSource
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Druid import DruidFeatures
from CharacterContent.Spells.SpellLists import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    DruidLevel6Spells,
    DruidLevel7Spells,
    DruidLevel8Spells,
    DruidLevel9Spells,
)
from Model.Grants import Grants
from Model.FeatureGrants import IfParentMissing

DruidSpellsUpTo2: TypeAlias = DruidLevel1Spells | DruidLevel2Spells

DruidSpellsUpTo3: TypeAlias = DruidSpellsUpTo2 | DruidLevel3Spells

DruidSpellsUpTo4: TypeAlias = DruidSpellsUpTo3 | DruidLevel4Spells

DruidSpellsUpTo5: TypeAlias = DruidSpellsUpTo4 | DruidLevel5Spells

DruidSpellsUpTo6: TypeAlias = DruidSpellsUpTo5 | DruidLevel6Spells

DruidSpellsUpTo7: TypeAlias = DruidSpellsUpTo6 | DruidLevel7Spells

DruidSpellsUpTo8: TypeAlias = DruidSpellsUpTo7 | DruidLevel8Spells

DruidSpellsUpTo9: TypeAlias = DruidSpellsUpTo8 | DruidLevel9Spells


@attr.dataclass
class PotentSpellcastingChoice:
    pass


@attr.dataclass
class PrimalStrikeChoice:
    pass


@attr.dataclass
class DruidLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: DruidLevel0Spells
    cantrip_2: DruidLevel0Spells
    spell_1: DruidLevel1Spells
    spell_2: DruidLevel1Spells
    spell_3: DruidLevel1Spells
    spell_4: DruidLevel1Spells
    primal_order: DruidFeatures.PrimalOrderType = DruidFeatures.PrimalOrderType.MAGICIAN

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(DruidFeatures.Spellcasting())
        data.add_feature(DruidFeatures.Druidic())
        data.add_spell(
            DruidLevel1Spells.SPEAK_WITH_ANIMALS,
            additional_ruling="Always prepared",
            source="Druidic",
        )
        data.add_feature(DruidFeatures.PrimalOrder(order=self.primal_order))
        data.add_cantrip(self.cantrip_1, source=SpellSource.CHOSEN)
        data.add_cantrip(self.cantrip_2, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_1, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_2, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_3, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_4, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel2(ClassBuilder.BaseClassLevel2):
    spell: DruidLevel1Spells
    known_forms: list

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(DruidFeatures.WildShape(known_forms=self.known_forms))
        data.add_feature(DruidFeatures.WildCompanion())
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel3(ClassBuilder.BaseClassLevel3):
    spell: DruidSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: DruidLevel0Spells
    spell: DruidSpellsUpTo2

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip, source=SpellSource.CHOSEN)
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: DruidSpellsUpTo3
    spell_2: DruidSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            DruidFeatures.WildResurgence(), extends=DruidFeatures.WildShape
        )
        data.add_spell(self.spell_1, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_2, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel6(ClassBuilder.BaseClassLevel6):
    spell: DruidSpellsUpTo3

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel7(ClassBuilder.BaseClassLevel7):
    spell: DruidSpellsUpTo4
    elemental_fury: PotentSpellcastingChoice | PrimalStrikeChoice

    def add_features(
        self,
        data: Grants,
    ) -> None:
        if isinstance(self.elemental_fury, PrimalStrikeChoice):
            data.add_feature(DruidFeatures.PrimalStrike())
        else:
            data.add_feature(DruidFeatures.PotentSpellcasting())
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: DruidSpellsUpTo4

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: DruidSpellsUpTo5
    spell_2: DruidSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell_1, source=SpellSource.CHOSEN)
        data.add_spell(self.spell_2, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: DruidLevel0Spells
    spell: DruidSpellsUpTo5

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_cantrip(self.cantrip, source=SpellSource.CHOSEN)
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel11(ClassBuilder.BaseClassLevel11):
    spell: DruidSpellsUpTo6

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class DruidLevel13(ClassBuilder.BaseClassLevel13):
    spell: DruidSpellsUpTo7

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        pass


@attr.dataclass
class DruidLevel15(ClassBuilder.BaseClassLevel15):
    spell: DruidSpellsUpTo8

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Upgrades whichever Elemental Fury option level 7 granted.
        data.add_feature(
            DruidFeatures.ImprovedPotentSpellcasting(),
            extends=DruidFeatures.PotentSpellcasting,
            if_missing=IfParentMissing.DROP,
        )
        data.add_feature(
            DruidFeatures.ImprovedPrimalStrike(),
            extends=DruidFeatures.PrimalStrike,
            if_missing=IfParentMissing.DROP,
        )
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class DruidLevel17(ClassBuilder.BaseClassLevel17):
    spell: DruidSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel18(ClassBuilder.BaseClassLevel18):
    spell: DruidSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(DruidFeatures.BeastSpells(), extends=DruidFeatures.WildShape)
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: DruidSpellsUpTo9

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


@attr.dataclass
class DruidLevel20(ClassBuilder.BaseClassLevel20):
    spell: DruidSpellsUpTo9

    def add_features(self, data: Grants) -> None:
        data.add_feature(DruidFeatures.Archdruid(), extends=DruidFeatures.WildShape)
        data.add_spell(self.spell, source=SpellSource.CHOSEN)


class DruidCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
    ):
        super().__init__(
            base_class=CharacterClass.DRUID,
            subclass=subclass,
            default_equipment=[
                Armor.LeatherArmor(),
                Armor.ShieldArmor(),
                Weapons.Sickle(),
                Weapons.Quarterstaff(),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.SHIELD,
            ],
            weapon_proficiencies=[Weapons.WeaponProficiency.SIMPLE],
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
            default_pack=Packs.ExplorersPack(),
        )


class DruidMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.DRUID,
            base_class_level_features=druid_level_features,
            base_class_level=druid_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
