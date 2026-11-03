"""Time Loop PR: the party and every encounter it can run (format:
Combat/Campaigns/ENCOUNTERS.md). After changing it, prepare the logs:
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
from Combat.EncounterConfig import CampaignSpec, CombatantSpec, EncounterSpec
from Combat.Monsters.CR_0.monsters import Wolf
from Combat.Monsters.CR_0.monsters_homebrew import DwarfLifeCleric, ElfDruidOfTheLand
from Combat.Monsters.CR_1.monsters import (
    AnimatedArmor,
    BugbearWarrior,
    Pirate,
    Spy,
    Tiger,
)
from Combat.Monsters.CR_1.monsters_homebrew import GoliathPaladinOfDevotion, OrcAssassin
from Combat.Monsters.CR_3.monsters_homebrew import MirelleTheGildedKnight
from Combat.Monsters.CR_5.monsters_homebrew import MiraPrincessOfTheLoop

CONFIG = CampaignSpec(
    name="time_loop_pr",
    title="Time Loop PR",
    description="A oneshot for four level 3 players. Every encounter below is played from its log, CombatLogs/<id>.json, prepared with: python -m Combat.Tools.prepare_encounters --campaign time_loop_pr",
    party=[
        Y2024ArtificerReanimatorDessieCharacterBuilder,
        Y2024RangerDrakewardenHannaCharacterBuilder,
        Y2024DruidMoonMaggieCharacterBuilder,
        Y2024BardValorThomasCharacterBuilder,
    ],
    encounters=[
        EncounterSpec(
            id="time_loop_pr_outside_the_gates",
            title="Outside the Gates",
            description="An easy fight against a rival adventuring party: one tank, one healer, one control, one DPS.",
            difficulty="Low: 600 XP against the four level 3 players (Low starts at 600).",
            monsters=[
                CombatantSpec(GoliathPaladinOfDevotion, "Paladin"),
                CombatantSpec(DwarfLifeCleric, "Cleric"),
                CombatantSpec(ElfDruidOfTheLand, "Druid"),
                CombatantSpec(OrcAssassin, "Assassin"),
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
            monsters=[
                CombatantSpec(MiraPrincessOfTheLoop, "Mira"),
                CombatantSpec(MirelleTheGildedKnight, "Warrior"),
            ],
        ),
    ],
)
