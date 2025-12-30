from typing import Optional

from CharacterConfigs.CharacterClasses import ClassBuilder
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import SpellSlots
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import WizardSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


class WizardStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        wizard_skills: WizardSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Dagger(player_is_proficient=True),
            Weapons.Quarterstaff(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.WIZARD,
            base_class_level_features=wizard_level_features,
            base_class_level=wizard_level,
            subclass=subclass,
            abilities=abilities,
            skills=wizard_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=WizardSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )


class WizardMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.WIZARD,
            base_class_level_features=wizard_level_features,
            base_class_level=wizard_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.INTELLIGENCE,
            caster_type=SpellSlots.CasterType.FULL_CASTER,
        )
