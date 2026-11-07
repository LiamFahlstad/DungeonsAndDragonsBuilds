"""Time Loop PR: the party and every encounter it can run (format:
Combat/Campaigns/ENCOUNTERS.md). Each encounter's log is an empty {} until the
encounter is opened, which sets it up from its EncounterSpec. Check this with:
python -m Combat.Tools.prepare_encounters --campaign time_loop_pr"""

from Builds.Characters.Y2024_Artificer_Reanimator_Dessie import (
    Y2024ArtificerReanimatorDessieCharacterBuilder,
)
from Builds.Characters.Y2024_Bard_Valor_Thomas import (
    Y2024BardValorThomasCharacterBuilder,
)
from Builds.Characters.Y2024_Druid_Moon_Maggie import (
    Y2024DruidMoonMaggieCharacterBuilder,
)
from Builds.Characters.Y2024_Ranger_Drakewarden_Hanna import (
    Y2024RangerDrakewardenHannaCharacterBuilder,
)
from Combat.EncounterConfig import CampaignSpec, CombatantSpec, EncounterSpec, PartySpec
from Combat.Monsters.CR_0.monsters import Cat, Wolf
from Combat.Monsters.CR_0.monsters_homebrew import Child, DwarfLifeCleric
from Combat.Monsters.CR_1.monsters import (
    AnimatedArmor,
    BugbearWarrior,
    DireWolf,
    Pirate,
    Spy,
    Tiger,
)
from Combat.Monsters.CR_1.monsters_homebrew import HumanPaladinOfDevotion, OrcAssassin
from Combat.Monsters.CR_3.monsters_homebrew import MirelleTheGildedKnight
from Combat.Monsters.CR_5.monsters_homebrew import MiraPrincessOfTheLoop

CONFIG = CampaignSpec(
    name="time_loop_pr",
    title="Time Loop PR",
    description="A oneshot for four level 3 players. Every encounter below is logged in CombatLogs/<id>.json, empty until it's opened, then set up from its encounter below.",
    party=PartySpec(
        id="main_party",
        members=[
            Y2024ArtificerReanimatorDessieCharacterBuilder,
            Y2024RangerDrakewardenHannaCharacterBuilder,
            Y2024DruidMoonMaggieCharacterBuilder,
            Y2024BardValorThomasCharacterBuilder,
        ],
        # Mira travels with the party as a child until the last encounter,
        # where she turns out to be the villain; the final fight's `players`
        # leaves both allies out.
        allies=[
            CombatantSpec(Child, "Mira"),
            CombatantSpec(Cat, "The Cat"),
        ],
    ),
    encounters=[
        EncounterSpec(
            id="time_loop_pr_outside_the_gates",
            title="Outside the Gates",
            description="An easy fight against a rival adventuring party: a human paladin tank, a dwarf healer, an elf druid wild-shaped into a dire wolf, and an orc assassin.",
            difficulty="Low: 700 XP against the four level 3 players (Low 600, Moderate 900); 680 net of Mira and the Cat.",
            monsters=[
                CombatantSpec(
                    HumanPaladinOfDevotion, "Cedric", hidden_from_players=True
                ),
                CombatantSpec(DwarfLifeCleric, "Brenna"),
                # Sylvaris is an elf druid, fighting wild-shaped as a dire wolf.
                CombatantSpec(DireWolf, "Sylvaris"),
                CombatantSpec(OrcAssassin, "Durgash"),
            ],
        ),
        EncounterSpec(
            id="time_loop_pr_drunk_oxe",
            title="The Drunk Oxe",
            description="A tavern brawl: a bugbear, a pirate and a tiger.",
            difficulty="Low: 600 XP against the four level 3 players (the Low budget).",
            monsters=[
                CombatantSpec(BugbearWarrior, "Bo"),
                CombatantSpec(Pirate, "Crock"),
                CombatantSpec(Tiger, "Tiger"),
            ],
        ),
        EncounterSpec(
            id="time_loop_pr_square",
            title="The Square",
            description="Mirelle, a princess cursed into a Large golden knight, and the guards of the square: two gilded sentinels, two watch officers and two guard dogs, each pair acting together.",
            difficulty="High: 1600 XP (the High budget). The guards alone are Moderate: 900 XP; Mirelle adds 700.",
            monsters=[
                CombatantSpec(
                    MirelleTheGildedKnight, "Mirelle", hidden_from_players=True
                ),
                CombatantSpec(
                    AnimatedArmor, "Gilded Sentinel", count=2, group="Gilded Sentinels"
                ),
                CombatantSpec(Spy, "Watch Officer", count=2, group="Watch Officers"),
                CombatantSpec(Wolf, "Guard Dog", count=2, group="Guard Dogs"),
            ],
        ),
        EncounterSpec(
            id="time_loop_pr_mira",
            title="Mira",
            description="The final fight: Mira, the princess whose magic trapped the kingdom in the time loop, and her Warrior (Mirelle's stat block). Mira marks targets for the Warrior's greatsword, teleports it into reach and rewinds the blows it takes, recharging its Golden Arc. The first time she's Bloodied, two duplicates of her join in.",
            difficulty="Above High: 2500 XP, about 1.5x the High budget (1600). Mira adds 1800, the Warrior 700.",
            # The party's allies (Mira the child and the Cat) stay out: Mira
            # is the villain here. She goes by her stat block's name, "Mira,
            # Princess of the Loop", because "Mira" is the party ally's name.
            players=["Dessie", "Hanna", "Maggie", "Thomas"],
            monsters=[
                CombatantSpec(MiraPrincessOfTheLoop),
                CombatantSpec(MirelleTheGildedKnight, "Warrior"),
            ],
        ),
    ],
)
