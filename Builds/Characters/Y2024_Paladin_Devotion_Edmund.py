"""
Build for Edmund's Paladin (level 3, Oath of Devotion), based on the
2026-08-16 planning chat with the player.

The background's ability bonus is only pinned down as "+1 Strength" in that
chat; the other +2 of the required +3 total is assumed here as +1 Dexterity
/ +1 Wisdom (the Sailor background's ability triad, which also matches the
Navigator's Tools proficiency and the Perception skill pick). Confirm with
Edmund's player and adjust if that's not what they meant.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
)
from CharacterContent.Classes.SubClasses2024.PaladinDevotion import (
    PaladinDevotionCustomStarterClassArgs,
    PaladinDevotionLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species import Tiefling
from CharacterContent.Spells.SpellLists import PaladinLevel1Spells
from CharacterContent.ToolProficiencies.Proficiencies import NavigatorsTools
from Core.Definitions import Ability, Skill
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinDevotionCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: True,
                }
            ),
        ),
        base_class_level=3,
        abilities=PointBuyAbilitiesStatBlock(
            strength=15,
            dexterity=12,
            constitution=13,
            intelligence=8,
            wisdom=10,
            charisma=14,
        ),
        # See module docstring: only the +1 Strength is confirmed from chat.
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        # No default equipment, so armor/weapons are spelled out explicitly.
        armor=[Armor.ChainMailArmor(), Armor.ShieldArmor()],
        weapons=[Weapons.Longsword(), Weapons.Dagger()],
        items=[
            (Items.HolySymbol(), 1),
            (Items.Bedroll(), 1),
            (Items.Tinderbox(), 1),
            (Items.NavigatorsTools(), 1),
            (Items.InkPen(), 1),
            (Items.Paper(), 1),
            (Items.Map(), 1),
            (Items.Rations(), 3),
        ],
        tool_proficiencies=[NavigatorsTools()],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    # Sap and Nick weapon masteries, both on weapons he
                    # actually carries: Longsword (Sap) and Dagger (Nick).
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Dagger(),
                    spell_1=PaladinLevel1Spells.CURE_WOUNDS,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                2: PaladinLevel2(
                    # TODO: choose your Fighting Style (not mentioned in chat).
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.CEREMONY,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.BLESS,
                ),
            },
            subclass_features_by_level={
                3: PaladinDevotionLevel3(),
            },
        ),
    )


class Y2024PaladinDevotionEdmundCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            # Not spoken in-fiction yet (a written/drawn nickname), but this
            # is the name used for the sheet and party-facing purposes.
            name="Edmund",
            starter_class_builder=get_starter_class_builder(),
            # Chthonic Tiefling: resistance to necrotic damage, the
            # Thaumaturgy cantrip (from Otherworldly Presence), plus the
            # Chill Touch cantrip and False Life spell from Fiendish Legacy.
            species_builder=Tiefling.TieflingSpeciesBuilder(
                character_level=3,
                fiendish_lineage=Tiefling.FiendishLineage.CHTHONIC,
            ),
        )
