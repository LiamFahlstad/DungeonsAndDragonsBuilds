import CharacterSheetCreator
import Definitions
from Features import HumanFeatures
from Features import OriginFeats

DATA = CharacterSheetCreator.CharacterSheetData()


DATA.speed = HumanFeatures.SPEED  # Given by your species
DATA.size = HumanFeatures.SIZE  # Given by your species

DATA.add_feature(HumanFeatures.Resourceful())
DATA.add_feature(HumanFeatures.Skillful(Definitions.Skill.SURVIVAL))
DATA.add_feature(HumanFeatures.Versatile())

# DATA.add_feature(OriginFeats.Skilled(Definitions.Skill.PERSUASION))
