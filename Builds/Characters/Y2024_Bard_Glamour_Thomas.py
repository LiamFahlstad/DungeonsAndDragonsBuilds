"""Build for Thomas, a level 3 College of Glamour Bard (Human, Entertainer)."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.BardGlamour import (
    BardGlamourCustomStarterClassArgs,
    BardGlamourLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Items
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import Lute
from Core.Definitions import Ability, Skill
from Model.AbilityScores import PointBuyAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardGlamourCustomStarterClassArgs(
            skills=[
                Skill.PERSUASION,
                Skill.DECEPTION,
                Skill.INSIGHT,
            ],
        ),
        base_class_level=3,
        # Final: STR 8 / DEX 16 / CON 14 / INT 8 / WIS 10 / CHA 17
        # after the Entertainer bonuses (+2 CHA, +1 DEX).
        abilities=PointBuyAbilityScores(
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
        # Entertainer: Acrobatics + Performance.
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ACROBATICS,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Musician(),
        armor=[Armor.StuddedLeatherArmor()],
        weapons=[],
        items=[(Items.Lute(), 1)],  # spellcasting focus
        tool_proficiencies=[Lute()],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.MINOR_ILLUSION,
                    spell_1=BardLevel1Spells.DISSONANT_WHISPERS,
                    spell_2=BardLevel1Spells.HEALING_WORD,
                    spell_3=BardLevel1Spells.FAERIE_FIRE,
                    spell_4=BardLevel1Spells.LONGSTRIDER,
                ),
                2: BardLevel2(
                    # Only 1st-level slots at Bard 2: Sleep is a placeholder
                    # swapped for Shatter at level 3 (replace_spells).
                    spell=BardLevel1Spells.SLEEP,
                    skill_expertise_1=Skill.PERSUASION,
                    skill_expertise_2=Skill.PERCEPTION,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.SUGGESTION,
                ),
            },
            subclass_features_by_level={
                3: BardGlamourLevel3(),
            },
        ),
        replace_spells={
            BardLevel1Spells.SLEEP: BardLevel2Spells.SHATTER,
        },
    )


class Y2024BardGlamourThomasCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Thomas",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
