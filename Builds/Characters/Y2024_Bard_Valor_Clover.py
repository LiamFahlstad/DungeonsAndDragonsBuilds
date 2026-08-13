"""
Skeleton build for Clover's Bard (level 3, College of Valor).

This is a minimal starting point, not a finished build. Every line marked
TODO is a placeholder value you should replace with your own choice. See
Y2024_Bard_Lore_TobiasGreyquill.py in this same folder for a fully worked
out, higher-level example of a Bard build.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.BardValor import (
    BardValorCustomStarterClassArgs,
    BardValorLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import Drum, Flute, Lute
from Core.Definitions import Ability, Skill
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock

# Tactics:
# - Prioritize control and support spells over weapon attacks when they can swing the encounter.
# - Use Faerie Fire against groups to give the party advantage on attacks.
# - Use Dissonant Whispers to damage and force an enemy to flee, potentially triggering allies' opportunity attacks.
# - Use Healing Word to revive fallen allies without sacrificing your action.
# - When no important spell is needed, attack with your rapier and True Strike.
# - Stay at medium range when possible


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardValorCustomStarterClassArgs(
            skills=BardSkillsStatBlock(
                proficiencies={
                    Skill.PERSUASION: True,
                    Skill.PERCEPTION: True,
                    Skill.INSIGHT: True,
                }
            ),
        ),
        base_class_level=3,
        # Point Buy - 27 points: STR 8 (0), DEX 14 (7), CON 15 (9), INT 8 (0),
        # WIS 10 (2), CHA 15 (9). Background then bumps DEX to 15 and CHA to 17.
        abilities=PointBuyAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=15,
            intelligence=8,
            wisdom=10,
            charisma=15,
        ),
        # Entertainer background.
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ACROBATICS,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=False,
        # Background feat: Musician (also grants proficiency with 3 musical
        # instruments of choice - modeled below via tool_proficiencies).
        origin_feat=OriginFeats.Musician(),
        # Half Plate + Shield once Valor grants medium armor/shield proficiency.
        armor=[
            Armor.HalfPlateArmor(),
            Armor.ShieldArmor(),
        ],
        weapons=[
            Weapons.Rapier(player_is_proficient=True, ability=Ability.DEXTERITY),
        ],
        items=[
            (Items.Lute(), 1),
            (Items.Drum(), 1),
            (Items.Flute(), 1),
        ],
        tool_proficiencies=[
            Lute(),
            Drum(),
            Flute(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.TRUE_STRIKE,
                    cantrip_2=BardLevel0Spells.VICIOUS_MOCKERY,
                    spell_1=BardLevel1Spells.HEALING_WORD,
                    spell_2=BardLevel1Spells.DISSONANT_WHISPERS,
                    spell_3=BardLevel1Spells.FAERIE_FIRE,
                    spell_4=BardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                2: BardLevel2(
                    # Aid is a 2nd-level spell, only learnable once 2nd-level
                    # slots open up at Bard level 3 - see below.
                    spell=BardLevel1Spells.CHARM_PERSON,
                    skill_expertise_1=Skill.PERSUASION,
                    skill_expertise_2=Skill.PERCEPTION,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.AID,
                ),
            },
            subclass_features_by_level={
                3: BardValorLevel3(),
            },
        ),
    )


class Y2024BardValorCloverCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Clover",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.STEALTH,
                # Human bonus feat: Magic Initiate (Wizard) for True Strike,
                # Blade Ward, and the Shield reaction spell.
                origin_feat=OriginFeats.MagicInitiateWizard(
                    cantrip_1=WizardLevel0Spells.TRUE_STRIKE,
                    cantrip_2=WizardLevel0Spells.BLADE_WARD,
                    spell=WizardLevel1Spells.SHIELD,
                    spell_casting_ability=Ability.CHARISMA,
                ),
            ),
        )
