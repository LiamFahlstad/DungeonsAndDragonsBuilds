"""Grim's Castle: its party, scenarios and log folders. See CHEATSHEET.md next
to this file for the commands to run each scenario."""

from pathlib import Path

import Combat.Campaigns.GrimsCastle.Encounters as Encounters
import Combat.Campaigns.GrimsCastle.Players as Players
from Combat.Campaign import Campaign
from Combat.Scenario import CombatScenario

CAMPAIGN = Campaign(
    name="grims_castle",
    title="Grim's Castle",
    folder=Path(__file__).resolve().parent,
    players=Players.get_players_group,
    scenarios=[
        CombatScenario(
            name="grims_castle_bull",
            combatants=lambda: Encounters.get_bull(),
            allies=lambda: Encounters.get_players(),
        ),
    ],
)
