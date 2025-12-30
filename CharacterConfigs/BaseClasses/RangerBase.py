from typing import Optional

from CharacterConfigs.BaseClasses.import ClassBuilder
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import SpellSlots
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import RangerSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


class RangerStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        ranger_skills: RangerSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Armor.StuddedLeatherArmor(),
            Weapons.Scimitar(player_is_proficient=True),
            Weapons.Shortsword(player_is_proficient=True),
            Weapons.Shortbow(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.RANGER,
            base_class_level_features=ranger_level_features,
            base_class_level=ranger_level,
            subclass=subclass,
            abilities=abilities,
            skills=ranger_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=RangerSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )


class RangerMulticlassBuilder(ClassBuilder.ClassBuilder):

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
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
