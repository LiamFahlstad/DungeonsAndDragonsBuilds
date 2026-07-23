from typing import Optional, TypeAlias, cast

import attr

import Core.Definitions as Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import Ability, CharacterClass
from Features.CharacterFeats import EpicBoon, GeneralFeats
from Features.Equipment import Armor, Weapons
from Features.ClassFeatures import SpellSlots
from Features.ClassFeatures.Warlock import WarlockFeatures
from Invocations.Definitions import (
    InvocationsLevel0,
    InvocationsLevel2,
    InvocationsLevel5,
    InvocationsLevel7,
    InvocationsLevel9,
    InvocationsLevel12,
    InvocationsLevel15,
)
from Spells.SpellLists import (
    WarlockLevel0Spells,
    WarlockLevel1Spells,
    WarlockLevel2Spells,
    WarlockLevel3Spells,
    WarlockLevel4Spells,
    WarlockLevel5Spells,
    WarlockLevel6Spells,
    WarlockLevel7Spells,
    WarlockLevel8Spells,
    WarlockLevel9Spells,
)
from StatBlocks.SavingThrowsStatBlock import WarlockSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock

WarlockSpellsUpTo2: TypeAlias = WarlockLevel1Spells | WarlockLevel2Spells

WarlockSpellsUpTo3: TypeAlias = WarlockSpellsUpTo2 | WarlockLevel3Spells

WarlockSpellsUpTo4: TypeAlias = WarlockSpellsUpTo3 | WarlockLevel4Spells

WarlockSpellsUpTo5: TypeAlias = WarlockSpellsUpTo4 | WarlockLevel5Spells

WarlockSpellsUpTo6: TypeAlias = WarlockSpellsUpTo5 | WarlockLevel6Spells

WarlockSpellsUpTo7: TypeAlias = WarlockSpellsUpTo6 | WarlockLevel7Spells

WarlockSpellsUpTo8: TypeAlias = WarlockSpellsUpTo7 | WarlockLevel8Spells

WarlockSpellsUpTo9: TypeAlias = WarlockSpellsUpTo8 | WarlockLevel9Spells

EldritchInvocationsLevel0: TypeAlias = InvocationsLevel0
EldritchInvocationsUpto2: TypeAlias = EldritchInvocationsLevel0 | InvocationsLevel2
EldritchInvocationsUpto5: TypeAlias = EldritchInvocationsUpto2 | InvocationsLevel5
EldritchInvocationsUpto7: TypeAlias = EldritchInvocationsUpto5 | InvocationsLevel7
EldritchInvocationsUpto9: TypeAlias = EldritchInvocationsUpto7 | InvocationsLevel9
EldritchInvocationsUpto12: TypeAlias = EldritchInvocationsUpto9 | InvocationsLevel12
EldritchInvocationsUpto15: TypeAlias = EldritchInvocationsUpto12 | InvocationsLevel15
EldritchInvocationsUpto18: TypeAlias = EldritchInvocationsUpto15


@attr.dataclass
class WarlockLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: WarlockLevel0Spells
    cantrip_2: WarlockLevel0Spells
    spell_1: WarlockLevel1Spells
    spell_2: WarlockLevel1Spells
    eldritch_invocation: InvocationsLevel0

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.ReplacingEldritchInvocations())
        data.add_feature(WarlockFeatures.ReplacingCantripsAndSpells())
        data.add_feature(WarlockFeatures.RegainingSpellSlots())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_invocation(self.eldritch_invocation)
        return data


@attr.dataclass
class WarlockLevel2(ClassBuilder.BaseClassLevel2):
    spell: WarlockLevel1Spells
    eldritch_invocation_1: EldritchInvocationsUpto2
    eldritch_invocation_2: EldritchInvocationsUpto2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.MagicalCunning())
        data.add_spell(self.spell)
        data.add_invocation(self.eldritch_invocation_1)
        data.add_invocation(self.eldritch_invocation_2)
        return data


@attr.dataclass
class WarlockLevel3(ClassBuilder.BaseClassLevel3):
    spell: WarlockSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: WarlockLevel0Spells
    spell: WarlockSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel5(ClassBuilder.BaseClassLevel5):
    spell: WarlockSpellsUpTo3
    eldritch_invocation_1: EldritchInvocationsUpto5
    eldritch_invocation_2: EldritchInvocationsUpto5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        data.add_invocation(self.eldritch_invocation_1)
        data.add_invocation(self.eldritch_invocation_2)
        return data


@attr.dataclass
class WarlockLevel6(ClassBuilder.BaseClassLevel6):
    spell: WarlockSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel7(ClassBuilder.BaseClassLevel7):
    spell: WarlockSpellsUpTo4
    eldritch_invocation: EldritchInvocationsUpto7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        data.add_invocation(self.eldritch_invocation)
        return data


@attr.dataclass
class WarlockLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: WarlockSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel9(ClassBuilder.BaseClassLevel9):
    spell: WarlockSpellsUpTo5
    eldritch_invocation: EldritchInvocationsUpto9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.ContactPatron())
        data.add_spell(self.spell)
        data.add_invocation(self.eldritch_invocation)
        return data


@attr.dataclass
class WarlockLevel10(ClassBuilder.BaseClassLevel10):
    cantrip: WarlockLevel0Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_cantrip(self.cantrip)
        return data


@attr.dataclass
class WarlockLevel11(ClassBuilder.BaseClassLevel11):
    spell: WarlockSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.MysticArcanum())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat
    eldritch_invocation: EldritchInvocationsUpto12

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_invocation(self.eldritch_invocation)
        return data


@attr.dataclass
class WarlockLevel13(ClassBuilder.BaseClassLevel13):
    spell: WarlockSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        mystic_arcanum: WarlockFeatures.MysticArcanum = cast(
            WarlockFeatures.MysticArcanum, data.get_features_by_type(
                WarlockFeatures.MysticArcanum
            )[0]
        )
        mystic_arcanum.extend_feature(WarlockFeatures.MysticArcanum())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class WarlockLevel15(ClassBuilder.BaseClassLevel15):
    spell: WarlockSpellsUpTo8
    eldritch_invocation: EldritchInvocationsUpto15

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        mystic_arcanum: WarlockFeatures.MysticArcanum = cast(
            WarlockFeatures.MysticArcanum, data.get_features_by_type(
                WarlockFeatures.MysticArcanum
            )[0]
        )
        mystic_arcanum.extend_feature(WarlockFeatures.MysticArcanum())
        data.add_spell(self.spell)
        data.add_invocation(self.eldritch_invocation)
        return data


@attr.dataclass
class WarlockLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WarlockLevel17(ClassBuilder.BaseClassLevel17):
    spell: WarlockSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        mystic_arcanum: WarlockFeatures.MysticArcanum = cast(
            WarlockFeatures.MysticArcanum, data.get_features_by_type(
                WarlockFeatures.MysticArcanum
            )[0]
        )
        mystic_arcanum.extend_feature(WarlockFeatures.MysticArcanum())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel18(ClassBuilder.BaseClassLevel18):
    eldritch_invocation: EldritchInvocationsUpto18

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_invocation(self.eldritch_invocation)
        return data


@attr.dataclass
class WarlockLevel19(ClassBuilder.BaseClassLevel19):
    spell: WarlockSpellsUpTo9
    epic_boon: EpicBoon.EpicBoon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.epic_boon)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.EldritchMaster())
        return data


class WarlockCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            base_class=CharacterClass.WARLOCK,
            subclass=subclass,
            saving_throws=WarlockSavingThrowsStatBlock(),
            default_equipment=[
                Weapons.Sickle(),
                Weapons.Dagger(),
                Armor.LeatherArmor(),
            ],
            skills=skills,
            armor_proficiencies=[Definitions.ArmorType.LIGHT],
            weapon_proficiencies=[Weapons.WeaponProficiency.SIMPLE],
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.WARLOCK_CASTER,
        )


class WarlockMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.WARLOCK,
            base_class_level_features=warlock_level_features,
            base_class_level=warlock_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.WARLOCK_CASTER,
        )
