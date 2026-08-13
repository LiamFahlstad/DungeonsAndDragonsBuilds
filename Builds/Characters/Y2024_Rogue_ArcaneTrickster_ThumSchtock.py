from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueLevel1,
    RogueLevel2,
    RogueLevel3,
)
from CharacterContent.Classes.SubClasses2024.RogueArcaneTrickster import (
    RogueArcaneTricksterCustomStarterClassArgs,
    RogueArcaneTricksterLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Items
from CharacterContent.Items.Weapons.MartialMelee import Shortsword
from CharacterContent.Items.Weapons.SimpleMelee import Dagger
from CharacterContent.Species import Dwarf
from CharacterContent.Spells.SpellLists import (
    EvocationLevel0Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from Core.Definitions import Ability, Skill
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueArcaneTricksterCustomStarterClassArgs(
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: False,
                    Skill.ATHLETICS: False,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: True,
                    Skill.INVESTIGATION: True,
                    Skill.PERCEPTION: False,
                    Skill.PERSUASION: False,
                    Skill.SLEIGHT_OF_HAND: True,
                    Skill.STEALTH: True,
                }
            ),
        ),
        base_class_level=3,
        # Point buy: scores 8-15, total cost must equal 27.
        abilities=PointBuyAbilitiesStatBlock(
            strength=11,
            dexterity=15,
            constitution=12,
            intelligence=15,
            wisdom=10,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.INTELLIGENCE, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.HISTORY,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Skilled(
            skills=[Skill.INSIGHT, Skill.NATURE, Skill.MEDICINE]
        ),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Dagger(),
            Shortsword(),
        ],
        items=[
            (Items.Backpack(), 1),
            (Items.Map(), 1),
            (Items.Rations(), 1),
            (Items.Gold(), 38),
            (Items.Silver(), 5),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_expertise_1=Skill.INVESTIGATION,
                    skill_expertise_2=Skill.SLEIGHT_OF_HAND,
                    weapon_mastery_1=Dagger(),
                    weapon_mastery_2=Shortsword(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
            },
            subclass_features_by_level={
                3: RogueArcaneTricksterLevel3(
                    cantrip_2=WizardLevel0Spells.MINOR_ILLUSION,
                    cantrip_3=EvocationLevel0Spells.BOOMING_BLADE,
                    spell_1=WizardLevel1Spells.SLEEP,
                    spell_2=WizardLevel1Spells.SILENT_IMAGE,
                    spell_3=WizardLevel1Spells.FOG_CLOUD,
                ),
            },
        ),
    )


class Y2024RogueArcaneTricksterThumSchtockCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Thum Schtock",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
