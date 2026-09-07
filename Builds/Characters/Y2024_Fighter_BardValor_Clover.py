"""
Comparison build for Klover's Bard: what if the character level currently
spent on Bard 3 (see Y2024_Bard_Valor_Clover.py) were instead a 1-level
Fighter dip, with the remaining levels taken as Valor Bard? A STARTING class
grants its full proficiencies (all armor, all weapons, 3 weapon masteries,
a Fighting Style), unlike multiclassing into Fighter later, which grants
none of that - so Fighter has to be the starting class for this comparison
to be meaningful. This is a sandbox for evaluating the trade-off, not a
character anyone is actually playing - not tracked in Players.py.

Deliberately kept identical to Y2024_Bard_Valor_Clover.py wherever the class
swap doesn't force a difference: same ability scores/background/species/
spells/cantrips/subclass. The differences, all consequences of Fighter
being the starting class instead of Bard:
- Armor: Fighter grants Heavy armor proficiency, so this swaps the Breastplate
  for Ring Mail (Heavy, no Strength requirement - her Strength is only 8, so
  Chain Mail/Splint/Plate would all impose the -10ft speed penalty for not
  meeting their Strength requirement). NOTE this is NOT actually an upgrade:
  Ring Mail is flat AC 14, while Breastplate (medium, Dex-based) gives her
  AC 14 + her +3 Dex mod capped at +2 = 16, since Fighter doesn't fix her
  poor Strength. Heavy armor access mostly matters for Str-based builds.
- Weapons: same Rapier + 2x Scimitar, all auto-proficient now (no more
  player_is_proficient overrides - Fighter's Martial proficiency covers them
  natively, unlike Valor's Martial Training which isn't wired into
  weapon_proficiencies in this codebase). Added a Longsword purely so all 3
  of Fighter's weapon-mastery slots (Bards/Paladins/Rogues only get 2) have a
  distinct owned weapon type to apply to.
- Fighting Style: Dueling (+2 damage with a one-handed melee weapon and
  nothing in the other hand - fits Rapier + Shield).
- Skills: Fighter's class-skill list doesn't include Nature or Performance,
  so those are gone; Persuasion survives (on both lists) alongside Athletics
  picked from Fighter's list instead. BardLevel2's Expertise picks moved
  from Persuasion/Performance to Persuasion/Athletics accordingly (Expertise
  requires the skill proficiency to already exist).
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterCustomStarterClassArgs,
    FighterLevel1,
)
from CharacterContent.Classes.SubClasses2024.BardValor import (
    BardValorLevel3,
    BardValorMulticlassBuilder,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
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
from Core.Definitions import Ability, FighterSubclass, Skill
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock

# Tactics: same as the pure-Bard version (Y2024_Bard_Valor_Clover.py) -
# control/support spells first, weapon attacks (now with Dueling's +2)
# otherwise. This build exists to compare AC/weapon proficiency/mastery
# access, not to explore different tactics.


def get_fighter_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterCustomStarterClassArgs(
            # Fighter subclass (chosen at Fighter level 3) is never actually
            # reached here - this placeholder is immediately overwritten by
            # BardValorMulticlassBuilder's "Valor" subclass once the sheets
            # are merged (see CharacterBuilder.build()/merge_with()).
            subclass=FighterSubclass.CHAMPION.value,
            # Nature and Performance aren't on Fighter's skill list, unlike
            # Bard's - see module docstring. Persuasion survives; Athletics
            # fills the second slot instead of Performance.
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.PERSUASION: True,
                    Skill.ATHLETICS: True,
                }
            ),
        ),
        base_class_level=1,
        abilities=PointBuyAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=15,
        ),
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
        origin_feat=OriginFeats.Skilled(
            skills=[
                Skill.SLEIGHT_OF_HAND,
                Skill.INVESTIGATION,
                Skill.ACROBATICS,
            ]
        ),
        # Heavy armor now that Fighter grants it - see module docstring for
        # why Ring Mail (not Chain Mail/Splint) is the only heavy option
        # that doesn't hurt her with only 8 Strength.
        armor=[
            Armor.RingMailArmor(),
            Armor.ShieldArmor(),
        ],
        weapons=[
            Weapons.Rapier(),
            Weapons.Scimitar(),
            Weapons.Scimitar(),
            Weapons.Longsword(),
        ],
        items=[
            (Items.Backpack(), 1),
            (Items.Bell(), 1),
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
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Rapier(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    weapon_mastery_3=Weapons.Longsword(),
                    fighting_style=FightingStyles.Dueling(),
                ),
            },
            subclass_features_by_level={},
        ),
    )


def get_bard_valor_multiclass_builder():
    return BardValorMulticlassBuilder(
        bard_level_features=ClassBuilder.BaseClassLevelFeatures(
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
                    spell=BardLevel1Spells.DISSONANT_WHISPERS,
                    # Moved from Persuasion/Performance - see module
                    # docstring (Performance isn't a proficiency here).
                    skill_expertise_1=Skill.PERSUASION,
                    skill_expertise_2=Skill.ATHLETICS,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.HOLD_PERSON,
                ),
            },
            subclass_features_by_level={
                3: BardValorLevel3(),
            },
        ),
        bard_level=3,
    )


class Y2024FighterBardValorCloverCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Clover (Fighter 1 / Bard Valor 3 comparison)",
            starter_class_builder=get_fighter_starter_class_builder(),
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
            multiclass_builders=[
                get_bard_valor_multiclass_builder(),
            ],
        )
