import CharacterSheetCreator
import Definitions
from Features.SpeciesFeatures import HumanFeatures
from Features import OriginFeats


def human_character_data(
    skill_proficiency: Definitions.Skill,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = HumanFeatures.SPEED  # Given by your species
    data.size = HumanFeatures.SIZE  # Given by your species

    data.add_feature(HumanFeatures.Resourceful())
    data.add_feature(HumanFeatures.Skillful(skill_proficiency))
    data.add_feature(HumanFeatures.Versatile())

    data.add_feature(origin_feat)
    return data
