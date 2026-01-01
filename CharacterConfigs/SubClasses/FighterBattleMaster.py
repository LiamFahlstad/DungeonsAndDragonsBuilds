from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterMulticlassBuilder,
    FighterStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import FighterSubclass
from Features import Armor, Backgrounds, Maneuvers, OriginFeats, Weapons
from Features.ClassFeatures import FighterFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class BattleMasterFighterLevel3(ClassBuilder.SubclassLevel3):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver
    maneuver_3: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice = FighterFeatures.SuperiorityDice()
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        superiority_dice.add_feature(self.maneuver_3)
        data.add_feature(superiority_dice)
        data.add_feature(FighterFeatures.StudentOfWar())
        return data


@attr.dataclass
class BattleMasterFighterLevel7(ClassBuilder.SubclassLevel7):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice: FighterFeatures.SuperiorityDice = data.get_features_by_type(
            FighterFeatures.SuperiorityDice
        )[0]
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        data.add_feature(FighterFeatures.KnowYourEnemy())
        return data


@attr.dataclass
class BattleMasterFighterLevel10(ClassBuilder.SubclassLevel10):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice: FighterFeatures.SuperiorityDice = data.get_features_by_type(
            FighterFeatures.SuperiorityDice
        )[0]
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        return data


@attr.dataclass
class BattleMasterFighterLevel15(ClassBuilder.SubclassLevel15):
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        superiority_dice: FighterFeatures.SuperiorityDice = data.get_features_by_type(
            FighterFeatures.SuperiorityDice
        )[0]
        superiority_dice.add_feature(self.maneuver_1)
        superiority_dice.add_feature(self.maneuver_2)
        superiority_dice.add_feature(FighterFeatures.Relentless())
        return data


@attr.dataclass
class BattleMasterFighterLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


class BattleMasterFighterStarterClassBuilder(FighterStarterClassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        abilities: AbilitiesStatBlock,
        fighter_skills: FighterSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.BATTLE_MASTER.value,
            abilities=abilities,
            fighter_skills=fighter_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class BattleMasterFighterMulticlassBuilder(FighterMulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            fighter_level_features=fighter_level_features,
            fighter_level=fighter_level,
            subclass=FighterSubclass.BATTLE_MASTER.value,
            replace_spells=replace_spells,
        )
