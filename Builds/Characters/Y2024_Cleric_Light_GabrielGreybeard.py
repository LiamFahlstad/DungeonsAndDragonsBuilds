"""
Gabriel Gråskägg - Dwarf Cleric (level 3, Light Domain).

Mål: Hitta tillbaka till sin tro i den mörka tiden efter lichen! Vill få nog
kraft att göra sin egen ward så han kan lämna Stonehill.

Hemlis: Född Gabriel Gryningsljus, egentligen en high priest men som har
tappat delar av sin kraft för många år sedan när han började tvivla på sin
gud efter att han blev utkastad hemifrån.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericLevel1,
    ClericLevel2,
    ClericLevel3,
    DivineOrderProtectorChoice,
)
from CharacterContent.Classes.SubClasses2024.ClericLight import (
    ClericLightCustomStarterClassArgs,
    ClericLightLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Dwarf
from CharacterContent.Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import CooksUtensils
from Core.Definitions import Ability, Skill
from Model.AbilityScores import PointBuyAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ClericLightCustomStarterClassArgs(
            skills=[
                Skill.INSIGHT,
                Skill.PERSUASION,
            ],
        ),
        base_class_level=3,
        # Point buy (27 pts): WIS 15 (9) + CON 14 (7) + CHA 13 (5) + DEX 12 (4)
        # + INT 10 (2) + STR 8 (0) = 27. These are the pre-background scores;
        # the Sage background bonuses below bring WIS/CON to 16/16.
        abilities=PointBuyAbilityScores(
            strength=13,
            dexterity=10,
            constitution=14,
            intelligence=8,
            wisdom=15,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ARCANA,
                Skill.HISTORY,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        # RAW Sage's tool proficiency is Calligrapher's Supplies, but the
        # answers explicitly asked for Cook's Utensils, so that's what's used.
        tool_proficiencies=[CooksUtensils()],
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ClericLevel1(
                    cantrip_1=ClericLevel0Spells.GUIDANCE,
                    cantrip_2=ClericLevel0Spells.SACRED_FLAME,
                    cantrip_3=ClericLevel0Spells.THAUMATURGY,
                    spell_1=ClericLevel1Spells.BLESS,
                    spell_2=ClericLevel1Spells.CURE_WOUNDS,
                    spell_3=ClericLevel1Spells.GUIDING_BOLT,
                    spell_4=ClericLevel1Spells.SHIELD_OF_FAITH,
                    divine_order=DivineOrderProtectorChoice(),
                ),
                2: ClericLevel2(
                    spell=ClericLevel2Spells.SILENCE,
                ),
                3: ClericLevel3(
                    spell=ClericLevel2Spells.ZONE_OF_TRUTH,
                ),
            },
            subclass_features_by_level={
                3: ClericLightLevel3(),
            },
        ),
    )


class Y2024ClericLightGabrielGreybeardCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Gabriel Greybeard",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
        self.drop_item(Armor.ChainShirtArmor)
        self.add_adventuring_gear(
            "Stonehill Armory Upgrade",
            armor=[Armor.SplintArmor()],
            weapons=[Weapons.Battleaxe(), Weapons.LightCrossbow()],
        )
        self.add_adventuring_gear(
            "Adventure to Ashelm",
            weapons=[Weapons.ModarinsWrath()],
        )
