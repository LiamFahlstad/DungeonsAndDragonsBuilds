from typing import Optional, TypeAlias

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import SpellSlots, WarlockFeatures
from Invocations.Definitions import (
    InvocationsLevel0,
    InvocationsLevel2,
    InvocationsLevel5,
    InvocationsLevel7,
    InvocationsLevel9,
    InvocationsLevel12,
    InvocationsLevel15,
)
from Spells.Definitions import (
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
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
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
    general_feat: (
        GeneralFeats.GeneralFeatCharacterFeature | GeneralFeats.GeneralFeatTextFeature
    )
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

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
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
    spell_1: WarlockSpellsUpTo5
    spell_2: WarlockSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WarlockLevel10(ClassBuilder.BaseClassLevel10):
    spell: WarlockSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel11(ClassBuilder.BaseClassLevel11):
    spell: WarlockSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WarlockLevel13(ClassBuilder.BaseClassLevel13):
    spell: WarlockSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel14(ClassBuilder.BaseClassLevel14):
    spell: WarlockSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel15(ClassBuilder.BaseClassLevel15):
    spell: WarlockSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat
    spell_1: WarlockSpellsUpTo8
    spell_2: WarlockSpellsUpTo8

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WarlockLevel17(ClassBuilder.BaseClassLevel17):
    spell: WarlockSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel18(ClassBuilder.BaseClassLevel18):
    spell: WarlockSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.SpellMastery())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel19(ClassBuilder.BaseClassLevel19):
    spell: WarlockSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class WarlockLevel20(ClassBuilder.BaseClassLevel20):
    spell: WarlockSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.SignatureSpells())
        data.add_spell(self.spell)
        return data


class WarlockStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        warlock_skills: WarlockSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Sickle(player_is_proficient=True),
            Weapons.Dagger(player_is_proficient=True),
            Armor.LeatherArmor(),
        ]
        super().__init__(
            base_class=CharacterClass.WARLOCK,
            base_class_level_features=warlock_level_features,
            base_class_level=warlock_level,
            subclass=subclass,
            abilities=abilities,
            skills=warlock_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=WarlockSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor_proficiencies=[Definitions.ArmorType.LIGHT],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
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
