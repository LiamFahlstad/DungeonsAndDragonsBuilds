"""Example build: Paladin Oath of Genies."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
)
from CharacterConfigs.SubClasses.PaladinGenies import (
    GeniesPaladinLevel3,
    PaladinGeniesCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Dragonborn
from Features.SpeciesFeatures.DragonbornFeatures import DragonColor
from Spells.SpellLists import PaladinLevel1Spells, WizardLevel0Spells, WizardLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinGeniesCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.CHARISMA, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERSUASION,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.MagicInitiateWizard(
            cantrip_1=WizardLevel0Spells.FIRE_BOLT,
            cantrip_2=WizardLevel0Spells.MAGE_HAND,
            spell=WizardLevel1Spells.SHIELD,
            spell_casting_ability=Ability.CHARISMA,
        ),
        armor=[],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.STRENGTH),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Dagger(),
                    spell_1=PaladinLevel1Spells.COMPELLED_DUEL,
                    spell_2=PaladinLevel1Spells.SEARING_SMITE,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.BLESS,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
            },
            subclass_features_by_level={
                3: GeniesPaladinLevel3(),
            },
        ),
        replace_spells={},
    )


class ExamplePaladinGeniesCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Paladin Genies",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dragonborn.DragonbornSpeciesBuilder(
                dragon_ancestry_color=DragonColor.GOLD,
            ),
        )
