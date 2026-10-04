from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.DruidBase import (
    DruidLevel1,
    DruidLevel2,
    DruidLevel3,
)
from CharacterContent.Classes.SubClasses2024.DruidMoon import (
    DruidMoonCustomStarterClassArgs,
    DruidMoonLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Species import Halfling
from CharacterContent.Spells.SpellLists import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import CartographersTools
from Combat.Monsters.CR_0.monsters import GiantBadger
from Combat.Monsters.CR_1.monsters import BrownBear, DireWolf, GiantSpider
from Core.Definitions import Ability, Skill
from Model.AbilityScores import PointBuyAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=DruidMoonCustomStarterClassArgs(
            skills=[
                Skill.PERCEPTION,
                Skill.ARCANA,
            ],
        ),
        base_class_level=3,
        # Point buy 27: STR 8, DEX 14, CON 15, INT 10, WIS 15, CHA 8.
        # Guide background: +2 WIS, +1 CON -> final 8 / 14 / 16 / 10 / 17 / 8.
        abilities=PointBuyAbilityScores(
            strength=8,
            dexterity=14,
            constitution=15,
            intelligence=10,
            wisdom=15,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.STEALTH,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        tool_proficiencies=[CartographersTools()],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: DruidLevel1(
                    cantrip_1=DruidLevel0Spells.GUIDANCE,
                    cantrip_2=DruidLevel0Spells.PRODUCE_FLAME,
                    spell_1=DruidLevel1Spells.ENTANGLE,
                    spell_2=DruidLevel1Spells.FAERIE_FIRE,
                    spell_3=DruidLevel1Spells.HEALING_WORD,
                    spell_4=DruidLevel1Spells.THUNDERWAVE,
                ),
                2: DruidLevel2(
                    # Placeholder 1st-level pick (level 2 slot only allows 1st
                    # level); swapped for Pass without Trace via replace_spells.
                    spell=DruidLevel1Spells.FOG_CLOUD,
                    known_forms=[BrownBear, DireWolf, GiantSpider, GiantBadger],
                ),
                3: DruidLevel3(
                    spell=DruidLevel2Spells.SPIKE_GROWTH,
                ),
            },
            subclass_features_by_level={
                3: DruidMoonLevel3(),
            },
        ),
    )


class Y2024DruidMoonMaggieCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Maggie",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Halfling.HalflingSpeciesBuilder(),
        )
