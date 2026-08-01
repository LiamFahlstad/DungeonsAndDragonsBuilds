"""Example build: Fighter Champion outfitted with one of every ArmorImprovement demo
armor (see Features/Equipment/Armor.py), plus a few magic armors that modify the
wearer rather than the armor itself (via `improvements=`), so all of it is visible
together on one character sheet."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
)
from CharacterConfigs.SubClasses2024.FighterChampion import (
    FighterChampionCustomStarterClassArgs,
    FighterChampionLevel3,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Items import Armor, Weapons
from SpeciesConfigs import Dwarf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterChampionCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ANIMAL_HANDLING: True,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=4,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
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
            # -- ArmorImprovement showcase: one of each improvement --
            Armor.ReinforcedBulwark(),  # SetArmorClassBase (worn)
            Armor.WardensBuckler(),  # AddArmorClassBonus (worn shield)
            Armor.GiantkinPlate(is_wearing=False),  # SetStrengthRequirement
            Armor.ShadowplateMail(is_wearing=False),  # SetStealthDisadvantage(False)
            Armor.VeteransChainShirt(is_wearing=False),  # AddArmorDescription
            Armor.DragonscalePlate(is_wearing=False),  # Standalone magical armor
            # -- Character-affecting improvement showcase: magic armor that
            # modifies the wearer (via `improvements=`), not the armor itself --
            Armor.SentinelsWatchArmor(is_wearing=False),  # SkillBonus
            Armor.StalwartsAegis(is_wearing=False),  # SavingThrowAdvantage
        ],
        weapons=[
            Weapons.Longsword(player_is_proficient=True),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Longsword(),
                    weapon_mastery_3=Weapons.Longsword(),
                    fighting_style=FightingStyles.Dueling(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Longsword(),
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


class ExampleArmorShowcaseCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Armor Showcase",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
