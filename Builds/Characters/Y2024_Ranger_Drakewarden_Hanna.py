from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
)
from CharacterContent.Classes.SubClasses2014.RangerDrakewarden import (
    RangerDrakewardenCustomStarterClassArgs,
    RangerDrakewardenLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import RangerLevel1Spells
from Core.Definitions import Ability, DamageType, Skill
from Model.AbilityScores import PointBuyAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerDrakewardenCustomStarterClassArgs(
            skills=[
                Skill.NATURE,
                Skill.PERCEPTION,
                Skill.STEALTH,
            ],
        ),
        base_class_level=3,
        # Point buy: scores 8-15, total cost must equal 27.
        abilities=PointBuyAbilityScores(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=14,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.WISDOM, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ATHLETICS,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.PortalJumper(damage_type=DamageType.PSYCHIC),
        armor=[
            Armor.StuddedLeatherArmor(),
        ],
        weapons=[
            Weapons.Longbow(),
            Weapons.Shortsword(),
            Weapons.Shortsword(),
        ],
        # One-shot party role: scout and climber. Only gear that can matter on
        # the adventure; tools are left to Dessie, healing and maps to Maggie.
        # Torches give her a light of her own when scouting away from
        # Dessie's lantern (and something to set things on fire with).
        items=[
            (Items.Arrows(), 2),  # two bundles of 20 arrows
            (Items.DruidicFocus(), 1),
            (Items.Rope(), 1),
            (Items.GrapplingHook(), 1),
            (Items.HuntingTrap(), 1),
            (Items.SignalWhistle(), 1),
            (Items.Torch(), 5),
            (Items.Tinderbox(), 1),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Shortsword(),
                    spell_1=RangerLevel1Spells.ENSNARING_STRIKE,
                    spell_2=RangerLevel1Spells.ABSORB_ELEMENTS,
                ),
                2: RangerLevel2(
                    skill_expertise=Skill.PERCEPTION,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.FOG_CLOUD,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.LONGSTRIDER,
                ),
            },
            subclass_features_by_level={
                3: RangerDrakewardenLevel3(
                    damage_type=DamageType.FIRE,
                    language="Draconic",
                ),
            },
        ),
        replace_spells={},
    )


class Y2024RangerDrakewardenHannaCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Hanna",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.INSIGHT,
                origin_feat=OriginFeats.Alert(),
            ),
        )
        # Kingdom Saving Agency mission issue (the agency that recruited the
        # party): Hanna is the party's eyes. A spyglass for scouting ahead,
        # a Darkvision scroll since none of the three can see in the dark,
        # and manacles for bringing a target back alive.
        self.add_adventuring_gear(
            "Kingdom Saving Agency",
            items=[
                (Items.Spyglass(), 1),
                (Items.Scroll("Darkvision"), 1),
                (Items.Manacles(), 1),
                (Items.PotionOfHealing(), 1),
            ],
            gold=10,  # travel expenses
        )
