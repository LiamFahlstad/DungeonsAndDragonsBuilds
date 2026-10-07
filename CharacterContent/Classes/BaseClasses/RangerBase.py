from typing import Optional

import attr

import Core.Definitions as Definitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Model.Grants import Grants
from Core.Definitions import Ability, CharacterClass, Skill
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Ranger import RangerFeatures
from CharacterContent.Spells.SpellLists import (
    RangerLevel1Spells,
    RangerLevel2Spells,
    RangerLevel3Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
)


@attr.dataclass
class RangerLevel1(ClassBuilder.BaseClassLevel1):
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    spell_1: RangerLevel1Spells
    spell_2: RangerLevel1Spells

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(RangerFeatures.Spellcasting())
        data.add_feature(RangerFeatures.ReplacingWeaponMasteries())
        data.add_feature(RangerFeatures.FavoredEnemy())

        # Add/Change prepared spells:
        data.add_spell(RangerLevel1Spells.HUNTERS_MARK)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)


@attr.dataclass
class RangerLevel2(ClassBuilder.BaseClassLevel2):
    skill_expertise: Skill
    fighting_style: FightingStyles.FightingStyle
    spell: RangerLevel1Spells

    def add_features(self, data: Grants) -> None:
        data.add_feature(RangerFeatures.DeftExplorerLanguages())
        data.add_feature(RangerFeatures.DeftExplorerExpertise(self.skill_expertise))
        data.add_fighting_style(self.fighting_style)
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel3(ClassBuilder.BaseClassLevel3):
    spell: RangerLevel1Spells

    def add_features(self, data: Grants) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    spell: RangerLevel1Spells

    def add_features(self, data: Grants) -> None:

        data.add_feature(self.general_feat)
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel5(ClassBuilder.BaseClassLevel5):
    spell: RangerLevel1Spells | RangerLevel2Spells

    def add_features(self, data: Grants) -> None:
        data.add_feature(RangerFeatures.ExtraAttack())
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: Grants) -> None:
        data.add_feature(RangerFeatures.Roving())


@attr.dataclass
class RangerLevel7(ClassBuilder.BaseClassLevel7):
    spell: RangerLevel1Spells | RangerLevel2Spells

    def add_features(self, data: Grants) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class RangerLevel9(ClassBuilder.BaseClassLevel9):
    skill_expertise_1: Skill
    skill_expertise_2: Skill
    spell_1: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells
    spell_2: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            RangerFeatures.Expertise(self.skill_expertise_1, self.skill_expertise_2)
        )
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)


@attr.dataclass
class RangerLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RangerFeatures.Tireless())


@attr.dataclass
class RangerLevel11(ClassBuilder.BaseClassLevel11):
    spell: RangerLevel1Spells | RangerLevel2Spells | RangerLevel3Spells

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class RangerLevel13(ClassBuilder.BaseClassLevel13):
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
    )

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            RangerFeatures.RelentlessHunter(), extends=RangerFeatures.FavoredEnemy
        )
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RangerFeatures.NaturesVeil())


@attr.dataclass
class RangerLevel15(ClassBuilder.BaseClassLevel15):
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
    )

    def add_features(self, data: Grants) -> None:
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.general_feat)


@attr.dataclass
class RangerLevel17(ClassBuilder.BaseClassLevel17):
    spell_1: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )
    spell_2: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )

    def add_features(self, data: Grants) -> None:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_feature(
            RangerFeatures.PreciseHunter(), extends=RangerFeatures.FavoredEnemy
        )


@attr.dataclass
class RangerLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(RangerFeatures.FeralSenses())


@attr.dataclass
class RangerLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon
    spell: (
        RangerLevel1Spells
        | RangerLevel2Spells
        | RangerLevel3Spells
        | RangerLevel4Spells
        | RangerLevel5Spells
    )

    def add_features(self, data: Grants) -> None:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell)


@attr.dataclass
class RangerLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: Grants) -> None:
        data.add_feature(
            RangerFeatures.FoeSlayer(), extends=RangerFeatures.FavoredEnemy
        )


class RangerCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: list[Skill],
    ):
        super().__init__(
            base_class=CharacterClass.RANGER,
            subclass=subclass,
            default_equipment=[
                Armor.StuddedLeatherArmor(),
                Weapons.Scimitar(),
                Weapons.Shortsword(),
                Weapons.Longbow(),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.SHIELD,
            ],
            weapon_proficiencies=[
                Weapons.WeaponProficiency.SIMPLE,
                Weapons.WeaponProficiency.MARTIAL,
            ],
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
            default_pack=Packs.ExplorersPack(),
        )


class RangerMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.RANGER,
            base_class_level_features=ranger_level_features,
            base_class_level=ranger_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
