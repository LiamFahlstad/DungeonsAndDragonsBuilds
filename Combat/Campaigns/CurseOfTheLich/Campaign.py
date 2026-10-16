"""Curse of the Lich: its party, scenarios and log folders. See CHEATSHEET.md
next to this file for the commands to run each scenario."""

from pathlib import Path

import Combat.Campaigns.CurseOfTheLich.Encounters as Encounters
import Combat.Campaigns.CurseOfTheLich.Players as Players
from Combat.Campaign import Campaign
from Combat.Scenario import CombatScenario

CAMPAIGN = Campaign(
    name="curse_of_the_lich",
    folder=Path(__file__).resolve().parent,
    players=Players.get_players_group,
    scenarios=[
        CombatScenario(
            name="ashelm_church",
            combatants=lambda: Encounters.get_accursed_ambush_combatants(),
        ),
        CombatScenario(
            name="goblin_scouting_party",
            combatants=lambda: Encounters.get_goblin_scouting_party_combatants(),
            allies=lambda: Encounters.get_stonehill_allies(),
            combatants_per_column=5,
        ),
        CombatScenario(
            name="goblin_warband_ambush",
            combatants=lambda: Encounters.get_goblin_warband_ambush_combatants(),
            allies=lambda: Encounters.get_stonehill_allies(),
            combatants_per_column=5,
        ),
        CombatScenario(
            name="wrath_of_durmor",
            combatants=lambda: Encounters.get_wrath_of_durmor_combatants(),
            allies=lambda: Encounters.get_stonehill_allies(),
            combatants_per_column=5,
        ),
    ],
)
