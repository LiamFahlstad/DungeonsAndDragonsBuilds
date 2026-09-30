"""Example build: Fighter Champion outfitted with one of every WeaponImprovement demo
weapon (see Features/Equipment/Weapons.py), a plain weapon with its ability
overridden via SetWeaponAbility, and a couple of magic weapons that modify the
wielder rather than the weapon (via `improvements=`), so all of it is visible
together on one character sheet."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
)
from CharacterContent.Classes.SubClasses2024.FighterChampion import (
    FighterChampionCustomStarterClassArgs,
    FighterChampionLevel3,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Dwarf
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterChampionCustomStarterClassArgs(
            skills=[
                Skill.ACROBATICS,
                Skill.ANIMAL_HANDLING,
            ],
        ),
        base_class_level=4,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.ATHLETICS,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.SavageAttacker(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            # -- WeaponImprovement showcase: one of each improvement --
            Weapons.UnerringBlade(),  # SetAttackRollBonus
            Weapons.MarksmansLongbow(),  # AddAttackRollBonus
            Weapons.Skullcrusher(),  # SetDamageRollBonus
            Weapons.VenomfangDagger(),  # AddDamageRollBonus
            Weapons.Colossustrike(),  # SetDamageDie
            Weapons.FrostbrandBlade(),  # SetDamageType
            Weapons.LungingLongsword(),  # AddWeaponProperty
            Weapons.LoremastersRapier(),  # AddWeaponDescription
            Weapons.StormcallerMace(),  # AddExtraDamage
            # -- SetWeaponAbility showcase: a plain Shortbow using Wisdom instead
            # of Dexterity, e.g. a "guided by instinct" reskin --
            Weapons.Shortbow(ability=Ability.WISDOM),
            # -- Character-affecting improvement showcase: magic weapons that
            # modify the wielder (via `improvements=`), not the weapon itself --
            Weapons.SkirmishersShortsword(),  # SkillBonus
            Weapons.VanguardsSpear(),  # InitiativeRollCondition
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.UnerringBlade(),
                    weapon_mastery_2=Weapons.MarksmansLongbow(),
                    weapon_mastery_3=Weapons.VenomfangDagger(),
                    fighting_style=FightingStyles.Archery(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Skullcrusher(),
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.STRENGTH, 2)]
                    ),
                ),
                5: FighterLevel5(),
            },
            subclass_features_by_level={
                3: FighterChampionLevel3(),
            },
        ),
    )


class Y2024FighterChampionVanceBladewrightCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Vance Bladewright",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
