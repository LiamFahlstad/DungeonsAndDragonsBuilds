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
from Combat.Monsters.CR_0.monsters_homebrew import DwarfLifeCleric, ElfDruidOfTheLand
from Combat.Monsters.CR_1.monsters import BugbearWarrior, Pirate, Tiger
from Combat.Monsters.CR_1.monsters_homebrew import GoliathPaladinOfDevotion, OrcAssassin
from Combat.Monsters.CR_2.monsters import Priest, Rhinoceros, SabertoothedTiger
from Combat.Monsters.CR_6.monsters import Vrock

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
            description="A tavern brawl: two bugbears, a pirate and a tiger.",
            difficulty="Low: 800 XP (just under Moderate's 900).",
            monsters=[
                CombatantSpec(BugbearWarrior, "Bo"),
                CombatantSpec(BugbearWarrior, "Jax"),
                CombatantSpec(Pirate, "Crock"),
                CombatantSpec(Tiger, "Tiger"),
            ],
        ),
        EncounterSpec(
            id="time_loop_pr_square",
            title="The Square",
            description="Mirelle the vrock and the guards of the square.",
            difficulty="3650 XP, about 2.3x the High budget of 1600.",
            monsters=[
                CombatantSpec(Vrock, "Mirelle"),
                CombatantSpec(Priest, "Guard Priest"),
                CombatantSpec(Rhinoceros, "Guard Rhinoceros"),
                CombatantSpec(SabertoothedTiger, "Guard Saber-Toothed Tiger"),
            ],
        ),
    ],
)
