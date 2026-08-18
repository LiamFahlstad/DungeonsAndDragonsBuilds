"""
Build for Klover's Bard (level 3, College of Valor), based on the
2026-08-18 planning chat with the player.

Two picks weren't answered in that chat and are assumed here (flagged
inline) - confirm with Klover's player and adjust if wrong:
- Background ability bonus/skills/tool: the chat gave rich personality
  detail (raised in a rural commune, moved to Stonehill 3 years ago, overly
  trusting/naive) but no mechanical picks. Kept the previous Entertainer
  ability bonus (+2 Cha/+1 Dex), but swapped its 2 skills to Insight and
  Animal Handling (fits the backstory) since Acrobatics/Performance are now
  covered by the origin feat and class skills instead. Tool proficiency
  trimmed to just Lute, since Musician (which granted 3 instruments) was
  replaced by Skilled this round.
- Level 2 prepared spell: the chat left this blank, and the old pick (Charm
  Person) is now taken at level 1 instead, so Dissonant Whispers is used as
  a placeholder.
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
from CharacterContent.ToolProficiencies.Proficiencies import Lute
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
                    Skill.NATURE: True,
                    Skill.PERFORMANCE: True,
                    Skill.PERSUASION: True,
                }
            ),
        ),
        base_class_level=3,
        abilities=PointBuyAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=15,
        ),
        # Background ability bonus/skills/tool: see module docstring - not
        # mechanically specified in chat, kept/adapted from the prior version.
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.ANIMAL_HANDLING,
            ]
        ),
        add_default_equipment=False,
        # Skilled: proficiency in 3 skills of choice.
        origin_feat=OriginFeats.Skilled(
            skills=[
                Skill.SLEIGHT_OF_HAND,
                Skill.INVESTIGATION,
                Skill.ACROBATICS,
            ]
        ),
        # Half Plate + Shield once Valor grants medium armor/shield proficiency.
        armor=[
            Armor.ChainShirtArmor(),
            Armor.ShieldArmor(),
        ],
        weapons=[
            Weapons.Shortsword(player_is_proficient=True),
        ],
        # Trimmed to 12 items total carried (was 36) - kept one of each type,
        # with Rations bumped to a few days' worth.
        items=[
            (Items.Lute(), 1),
            (Items.Backpack(), 1),
            (Items.Bell(), 1),
            (Items.BullseyeLantern(), 1),
            (Items.Costume(), 1),
            (Items.Mirror(), 1),
            (Items.FlasksOfOil(), 1),
            (Items.Rations(), 3),
            (Items.Tinderbox(), 1),
            (Items.Waterskin(), 1),
        ],
        tool_proficiencies=[
            Lute(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.PRESTIDIGITATION,
                    cantrip_2=BardLevel0Spells.VICIOUS_MOCKERY,
                    spell_1=BardLevel1Spells.CHARM_PERSON,
                    spell_2=BardLevel1Spells.HEALING_WORD,
                    spell_3=BardLevel1Spells.DISGUISE_SELF,
                    spell_4=BardLevel1Spells.COMPREHEND_LANGUAGES,
                ),
                2: BardLevel2(
                    # See module docstring: not specified in chat, using
                    # Dissonant Whispers as a placeholder.
                    spell=BardLevel1Spells.DISSONANT_WHISPERS,
                    skill_expertise_1=Skill.PERSUASION,
                    skill_expertise_2=Skill.PERFORMANCE,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.HOLD_PERSON,
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
                    cantrip_1=WizardLevel0Spells.GREEN_FLAME_BLADE,
                    cantrip_2=WizardLevel0Spells.BOOMING_BLADE,
                    spell=WizardLevel1Spells.SHIELD,
                    spell_casting_ability=Ability.CHARISMA,
                ),
            ),
        )
