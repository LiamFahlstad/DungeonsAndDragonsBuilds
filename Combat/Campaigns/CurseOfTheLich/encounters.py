"""Curse of the Lich: the party and every encounter it can run (format:
Combat/Campaigns/ENCOUNTERS.md). After changing it, prepare the logs:
python -m Combat.Tools.prepare_encounters"""

import Combat.Combatants as Combatants
from Builds.Characters.Y2024_Artificer_Cartographer_ObmarStalskagg import (
    Y2024ArtificerCartographerObmarStalskaggCharacterBuilder,
)
from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder,
)
from Builds.Characters.Y2024_Cleric_Light_GabrielGreybeard import (
    Y2024ClericLightGabrielGreybeardCharacterBuilder,
)
from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder,
)
from Builds.Characters.Y2024_Rogue_ArcaneTrickster_ThumSchtock import (
    Y2024RogueArcaneTricksterThumSchtockCharacterBuilder,
)
from Combat.EncounterConfig import CampaignSpec, CombatantSpec, EncounterSpec
from Combat.Monsters.CR_0.monsters import GoblinMinion, GoblinWarrior, Worg
from Combat.Monsters.CR_0.monsters_homebrew import (
    Accursed,
    ArmoredAccursed,
    PhysicalAccursed,
)
from Combat.Monsters.CR_1.monsters import GoblinBoss
from Combat.Monsters.CR_1.monsters_homebrew import (
    AccursedGroupOf3,
    CommonCultist,
    GreypawCR1,
)
from Combat.Monsters.CR_2.monsters_homebrew import (
    AccursedGroupOf5,
    PriestOfTheBlackTongues,
)
from Combat.Monsters.CR_3.monsters import GoblinHexer
from Combat.Monsters.CR_3.monsters_homebrew import (
    CantorOfTheBlackChoir,
    GarronTheKindly,
    GoblinKingCR3,
    SerCaldusTheVowOfSilence,
)
from Combat.Monsters.CR_4.monsters_homebrew import ManifestationOfDurmor, MarshalVirel
from Combat.Monsters.CR_6.monsters_homebrew import TheMouthThatWalks

CONFIG = CampaignSpec(
    name="curse_of_the_lich",
    title="Curse of the Lich",
    description="The tracked six-player campaign. Every encounter below is played from its log, CombatLogs/<id>.json, prepared with: python -m Combat.Tools.prepare_encounters",
    party=[
        Y2024ArtificerCartographerObmarStalskaggCharacterBuilder,
        Y2024PaladinDevotionEdmundCharacterBuilder,
        Y2024BardValorCloverCharacterBuilder,
        Y2024ClericLightGabrielGreybeardCharacterBuilder,
        Y2024RogueArcaneTricksterThumSchtockCharacterBuilder,
        Y2024MonkElementsKiviJattiCharacterBuilder,
    ],
    encounters=[
        EncounterSpec(
            id="ashelm_church",
            title="Ashelm Church",
            description="The accursed ambush at the church: three groups of five Accursed and one group of three.",
            monsters=[
                CombatantSpec(AccursedGroupOf5, "(1) Accursed Group of 5"),
                CombatantSpec(AccursedGroupOf5, "(2) Accursed Group of 5"),
                CombatantSpec(AccursedGroupOf5, "(3) Accursed Group of 5"),
                CombatantSpec(AccursedGroupOf3, "Accursed Group of 3"),
            ],
        ),
        EncounterSpec(
            id="goblin_scouting_party",
            title="Goblin Scouting Party",
            description="A goblin scouting party, with Greypaw fighting alongside the party.",
            difficulty="Balanced for three level 3 players (Edmund, Clover, Kivi).",
            players=["Edmund", "Clover", "Kivi"],
            monsters=[
                CombatantSpec(GoblinBoss, "Goblin Boss", count=2),
                CombatantSpec(GoblinWarrior, "Goblin Warrior", count=4),
                CombatantSpec(GoblinMinion, "Goblin Minion", count=2),
            ],
            allies=[
                CombatantSpec(GreypawCR1, "Greypaw (Ally)"),
            ],
            combatants_per_column=5,
        ),
        EncounterSpec(
            id="goblin_warband_ambush",
            title="Goblin Warband Ambush",
            description="A goblin warband with hexers and worgs ambushes the party; Greypaw fights alongside them.",
            difficulty="Moderate for the full party (6x level 4): 2500 XP, 2300 net of Greypaw.",
            monsters=[
                CombatantSpec(GoblinHexer, "Goblin Hexer", count=2),
                CombatantSpec(GoblinBoss, "Goblin Boss", count=3),
                CombatantSpec(Worg, "Worg", count=2, group="Worgs"),
                CombatantSpec(
                    GoblinWarrior,
                    "Goblin Warrior A",
                    count=3,
                    group="Goblin Warriors A",
                ),
                CombatantSpec(
                    GoblinWarrior,
                    "Goblin Warrior B",
                    count=3,
                    group="Goblin Warriors B",
                ),
            ],
            allies=[
                CombatantSpec(GreypawCR1, "Greypaw (Ally)"),
            ],
            combatants_per_column=5,
        ),
        EncounterSpec(
            id="goblin_warband_ambush_friendly_goblins",
            title="Goblin Warband Ambush (Friendly Goblins)",
            description="The goblin warband ambush, with a band of friendly goblins fighting alongside the party and Greypaw. A fourth goblin boss and three more goblin warriors join the warband to keep the difficulty the same.",
            difficulty="Moderate for the full party (6x level 4): 2850 XP, 2300 net of Greypaw and the friendly goblins.",
            monsters=[
                CombatantSpec(
                    GoblinHexer, "Goblin Hexer", count=2, group="Goblin Hexers"
                ),
                CombatantSpec(
                    GoblinBoss, "Goblin Boss A", count=2, group="Goblin Bosses A"
                ),
                CombatantSpec(
                    GoblinBoss, "Goblin Boss B", count=2, group="Goblin Bosses B"
                ),
                CombatantSpec(Worg, "Worg", count=2, group="Worgs"),
                CombatantSpec(
                    GoblinWarrior,
                    "Goblin Warrior A",
                    count=3,
                    group="Goblin Warriors A",
                ),
                CombatantSpec(
                    GoblinWarrior,
                    "Goblin Warrior B",
                    count=3,
                    group="Goblin Warriors B",
                ),
                CombatantSpec(
                    GoblinWarrior,
                    "Goblin Warrior C",
                    count=3,
                    group="Goblin Warriors C",
                ),
            ],
            allies=[
                CombatantSpec(GreypawCR1, "Greypaw (Ally)"),
                CombatantSpec(GoblinBoss, "Katt"),
                CombatantSpec(GoblinWarrior, "Mask", group="Friendly Goblin Warriors"),
                CombatantSpec(GoblinWarrior, "Bror", group="Friendly Goblin Warriors"),
                CombatantSpec(
                    GoblinWarrior, "Kamrat", group="Friendly Goblin Warriors"
                ),
            ],
            combatants_per_column=5,
        ),
        EncounterSpec(
            id="wrath_of_durmor",
            title="Wrath of Durmor",
            description="The Manifestation of Durmor and the Goblin King with their goblins; Greypaw fights alongside the party.",
            difficulty="High for the full party (6x level 4): 3200 XP, 3000 net of Greypaw.",
            monsters=[
                CombatantSpec(ManifestationOfDurmor, "Manifestation of Durmor"),
                CombatantSpec(GoblinKingCR3, "Goblin King"),
                CombatantSpec(GoblinHexer, "Goblin Hexer"),
                CombatantSpec(GoblinBoss, "Goblin Boss", count=2),
                CombatantSpec(GoblinWarrior, "Goblin Warrior", count=6),
            ],
            allies=[
                CombatantSpec(GreypawCR1, "Greypaw (Ally)"),
            ],
            combatants_per_column=5,
        ),
        EncounterSpec(
            id="black_tongues_skirmish",
            title="Black Tongues Skirmish",
            description="Two Common Cultists with two Accursed.",
            monsters=[
                CombatantSpec(CommonCultist, "Common Cultist", count=2),
                CombatantSpec(Accursed, "Accursed", count=2),
            ],
        ),
        EncounterSpec(
            id="yellow_capes_patrol",
            title="Yellow Capes Patrol",
            description="Marshal Virel with two Yellow Cape Enforcers.",
            monsters=[
                CombatantSpec(MarshalVirel, "Marshal Virel"),
                CombatantSpec(Combatants.Priest, "Yellow Cape Enforcer", count=2),
            ],
        ),
        EncounterSpec(
            id="black_tongues_ritual",
            title="Black Tongues Ritual",
            description="The Priest of the Black Tongues with an Accursed Brute, an Accursed Warden and a group of five Accursed.",
            monsters=[
                CombatantSpec(PriestOfTheBlackTongues, "Priest of the Black Tongues"),
                CombatantSpec(PhysicalAccursed, "Accursed Brute"),
                CombatantSpec(ArmoredAccursed, "Accursed Warden"),
                CombatantSpec(AccursedGroupOf5, "Accursed Group"),
            ],
        ),
        EncounterSpec(
            id="yellow_capes_last_stand",
            title="Yellow Capes' Last Stand",
            description="Garron the Kindly and Ser Caldus, the Vow of Silence.",
            monsters=[
                CombatantSpec(GarronTheKindly, "Garron the Kindly"),
                CombatantSpec(
                    SerCaldusTheVowOfSilence, "Ser Caldus - The Vow of Silence"
                ),
            ],
        ),
        EncounterSpec(
            id="mouth_that_walks",
            title="The Mouth That Walks",
            description="The Mouth That Walks and the Cantor of the Black Choir, with two Accursed.",
            monsters=[
                CombatantSpec(TheMouthThatWalks, "The Mouth That Walks"),
                CombatantSpec(CantorOfTheBlackChoir, "Cantor of the Black Choir"),
                CombatantSpec(Accursed, "Accursed", count=2),
            ],
        ),
    ],
)
