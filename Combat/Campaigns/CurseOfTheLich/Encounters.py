from Builds.CharacterBuilder import CharacterSheetData
from Builds.Characters.OptimizedClericLight import OptimizedClericLightCharacterBuilder
from Builds.Characters.OptimizedPaladinVengeance import OptimizedPaladinVengeanceCharacterBuilder
from Builds.Characters.OptimizedRogueAssassin import OptimizedRogueAssassinCharacterBuilder
from Builds.Characters.OptimizedWizardBladesinger import OptimizedWizardBladesingerCharacterBuilder
from Combat import Combatants
from Combat.Monsters.CR_0.monsters_homebrew import (
    Accursed,
    AccursedBrute,
    AccursedWarden,
)
from Combat.Monsters.CR_1.monsters_homebrew import CommonCultist, SisterAshNumberSeven
from Combat.Monsters.CR_2.monsters_homebrew import (
    AccursedGroupLarge,
    PriestOfTheBlackTongues,
)
from Combat.Monsters.CR_3.monsters_homebrew import (
    CantorOfTheBlackChoir,
    GarronTheKindly,
    SerCaldusTheVowOfSilence,
)
from Combat.Monsters.CR_4.monsters_homebrew import MarshalVirel
from Combat.Monsters.CR_6.monsters_homebrew import TheMouthThatWalks


def get_players() -> list[CharacterSheetData]:
    return [
        OptimizedPaladinVengeanceCharacterBuilder().build(),
        OptimizedWizardBladesingerCharacterBuilder().build(),
        OptimizedClericLightCharacterBuilder().build(),
        OptimizedRogueAssassinCharacterBuilder().build(),
    ]


def get_black_tongues_skirmish_combatants() -> list[Combatants.BasicCombatantData]:
    cultist1 = CommonCultist()
    cultist1.set_name("Common Cultist 1")

    cultist2 = CommonCultist()
    cultist2.set_name("Common Cultist 2")

    accursed1 = Accursed()
    accursed1.set_name("Accursed 1")

    accursed2 = Accursed()
    accursed2.set_name("Accursed 2")

    sister_ash = SisterAshNumberSeven()
    sister_ash.set_name("Sister Ash - Number Seven")

    return [cultist1, cultist2, accursed1, accursed2, sister_ash]


def get_yellow_capes_patrol_combatants() -> list[Combatants.BasicCombatantData]:
    marshal = MarshalVirel()
    marshal.set_name("Marshal Virel")

    enforcer1 = Combatants.Priest()
    enforcer1.set_name("Yellow Cape Enforcer 1")

    enforcer2 = Combatants.Priest()
    enforcer2.set_name("Yellow Cape Enforcer 2")

    return [marshal, enforcer1, enforcer2]


def get_black_tongues_ritual_combatants() -> list[Combatants.BasicCombatantData]:
    priest = PriestOfTheBlackTongues()
    priest.set_name("Priest of the Black Tongues")

    brute = AccursedBrute()
    brute.set_name("Accursed Brute")

    warden = AccursedWarden()
    warden.set_name("Accursed Warden")

    accursed_group = AccursedGroupLarge()
    accursed_group.set_name("Accursed Group")

    return [priest, brute, warden, accursed_group]


def get_yellow_capes_last_stand_combatants() -> list[Combatants.BasicCombatantData]:
    garron = GarronTheKindly()
    garron.set_name("Garron the Kindly")

    ser_caldus = SerCaldusTheVowOfSilence()
    ser_caldus.set_name("Ser Caldus - The Vow of Silence")

    return [garron, ser_caldus]


def get_mouth_that_walks_combatants() -> list[Combatants.BasicCombatantData]:
    mouth = TheMouthThatWalks()
    mouth.set_name("The Mouth That Walks")

    cantor = CantorOfTheBlackChoir()
    cantor.set_name("Cantor of the Black Choir")

    accursed1 = Accursed()
    accursed1.set_name("Accursed 1")

    accursed2 = Accursed()
    accursed2.set_name("Accursed 2")

    return [mouth, cantor, accursed1, accursed2]
