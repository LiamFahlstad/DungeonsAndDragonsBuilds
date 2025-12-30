from typing import Optional


from CharacterConfigs.BaseClasses.import ClassBuilder
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import SpellSlots
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import PaladinSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


class PaladinStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        paladin_skills: PaladinSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Armor.ChainMailArmor(),
            Armor.ShieldArmor(),
            Weapons.Longsword(player_is_proficient=True),
            Weapons.Javelin(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.PALADIN,
            base_class_level_features=paladin_level_features,
            base_class_level=paladin_level,
            subclass=subclass,
            abilities=abilities,
            skills=paladin_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=PaladinSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )


class PaladinMulticlassBuilder(ClassBuilder.ClassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.PALADIN,
            base_class_level_features=paladin_level_features,
            base_class_level=paladin_level,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.CHARISMA,
            caster_type=SpellSlots.CasterType.HALF_CASTER,
        )
