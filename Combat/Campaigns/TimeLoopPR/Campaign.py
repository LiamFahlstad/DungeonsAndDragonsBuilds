"""Time Loop PR (oneshot): its party, scenarios and log folders. See
CHEATSHEET.md next to this file for the commands to run each scenario."""

from pathlib import Path

import Combat.Campaigns.TimeLoopPR.Encounters as Encounters
import Combat.Campaigns.TimeLoopPR.Players as Players
from Combat.Campaign import Campaign
from Combat.Scenario import CombatScenario

CAMPAIGN = Campaign(
    name="time_loop_pr",
    folder=Path(__file__).resolve().parent,
    players=Players.get_players_group,
    scenarios=[
        CombatScenario(
            name="time_loop_pr_drunk_oxe",
            combatants=lambda: Encounters.get_drunk_oxe_combatants(),
        ),
        CombatScenario(
            name="time_loop_pr_square",
            combatants=lambda: Encounters.get_square_combatants(),
        ),
    ],
)
