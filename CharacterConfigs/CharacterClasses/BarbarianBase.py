from typing import Optional

from CharacterConfigs.CharacterClasses import ClassBuilder
from Definitions import CharacterClass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import BarbarianSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


class BarbarianStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        barbarian_skills: BarbarianSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Greataxe(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.BARBARIAN,
            base_class_level_features=barbarian_level_features,
            base_class_level=barbarian_level,
            subclass=subclass,
            abilities=abilities,
            skills=barbarian_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=BarbarianSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class BarbarianMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.BARBARIAN,
            base_class_level_features=barbarian_level_features,
            base_class_level=barbarian_level,
            subclass=subclass,
            replace_spells=replace_spells,
        )
