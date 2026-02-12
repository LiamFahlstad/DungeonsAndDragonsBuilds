from typing import Optional

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import CharacterClass
from Features import Armor, Backgrounds, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import RogueFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import RogueSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueLevel1(ClassBuilder.BaseClassLevel1):
    skill_1: Definitions.Skill
    skill_2: Definitions.Skill
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(RogueFeatures.Expertise(self.skill_1, self.skill_2))
        data.add_feature(RogueFeatures.SneakAttack())
        data.add_feature(RogueFeatures.ThievesCant())
        data.add_feature(RogueFeatures.WeaponMastery())
        return data


@attr.dataclass
class RogueLevel2(ClassBuilder.BaseClassLevel2):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.CunningAction())
        return data


@attr.dataclass
class RogueLevel3(ClassBuilder.BaseClassLevel3):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.SteadyAim())
        return data


@attr.dataclass
class RogueLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.UncannyDodge())
        return data


@attr.dataclass
class RogueLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.ReliableTalent())
        return data


@attr.dataclass
class RogueLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel10(ClassBuilder.BaseClassLevel10):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.ImprovedCunningStrike())
        return data


@attr.dataclass
class RogueLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel13(ClassBuilder.BaseClassLevel13):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.DeviousStrikes())
        return data


@attr.dataclass
class RogueLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.SlipperyMind())
        return data


@attr.dataclass
class RogueLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel17(ClassBuilder.BaseClassLevel17):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.Elusive())
        return data


@attr.dataclass
class RogueLevel19(ClassBuilder.BaseClassLevel19):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class RogueLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.StrokeOfLuck())
        return data


class RogueStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        rogue_skills: RogueSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Shortsword(player_is_proficient=True),
            Weapons.Dagger(player_is_proficient=True),
            Weapons.Scimitar(player_is_proficient=True),
            Armor.LeatherArmor(),
        ]
        super().__init__(
            base_class=CharacterClass.ROGUE,
            base_class_level_features=rogue_level_features,
            base_class_level=rogue_level,
            subclass=subclass,
            abilities=abilities,
            skills=rogue_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=RogueSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor_proficiencies=[Definitions.ArmorType.LIGHT],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class RogueMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.ROGUE,
            base_class_level_features=rogue_level_features,
            base_class_level=rogue_level,
            subclass=subclass,
            replace_spells=replace_spells,
        )
