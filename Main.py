import CharacterSheetCreator
from Definitions import WarlockSubclass, PaladinSubclass, FighterSubclass, Species

DATA = CharacterSheetCreator.CharacterSheetData()

##########################################
# ================ CHANGE ============== #
##########################################

# ================ GENERAL ============= #
SUBCLASS = FighterSubclass.BATTLE_MASTER
SPECIES = Species.HUMAN
DATA.character_name = "Sten"


##########################################
# ============ LEAVE AS IS ============= #
##########################################

if SUBCLASS == WarlockSubclass.THE_ARCHFEY:
    from CharacterConfigs import Warlock

    CHARACTER_CLASS_DATA = Warlock.DATA

elif SUBCLASS == PaladinSubclass.OATH_OF_VENGEANCE:
    from CharacterConfigs import PaladinOathOfVengeance

    CHARACTER_CLASS_DATA = PaladinOathOfVengeance.DATA

elif SUBCLASS == PaladinSubclass.OATH_OF_DEVOTION:
    from CharacterConfigs import PaladinOathOfDevotion

    CHARACTER_CLASS_DATA = PaladinOathOfDevotion.DATA

elif SUBCLASS == FighterSubclass.BATTLE_MASTER:
    from CharacterConfigs import BattleMasterFighter

    CHARACTER_CLASS_DATA = BattleMasterFighter.DATA


if SPECIES == Species.HUMAN:
    from SpeciesConfigs import Human

    SPECIES_DATA = Human.DATA


def merge_character_data(
    base_data: CharacterSheetCreator.CharacterSheetData,
    additional_data: CharacterSheetCreator.CharacterSheetData,
) -> CharacterSheetCreator.CharacterSheetData:
    """Merge two CharacterSheetData objects, with additional_data taking precedence."""
    merged_data = CharacterSheetCreator.CharacterSheetData()

    # Merge basic attributes
    for attr in vars(base_data):
        base_value = getattr(base_data, attr)
        additional_value = getattr(additional_data, attr)

        if additional_value not in (None, [], {}, ""):
            setattr(merged_data, attr, additional_value)
        else:
            setattr(merged_data, attr, base_value)

    return merged_data


if __name__ == "__main__":
    merged_data = merge_character_data(DATA, CHARACTER_CLASS_DATA)
    merged_data = merge_character_data(merged_data, SPECIES_DATA)
    merged_data.create_character_sheet()
