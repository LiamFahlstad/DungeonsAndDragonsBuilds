"""Grim's Castle: the party and every encounter it can run (format:
Combat/Campaigns/ENCOUNTERS.md). After changing it, prepare the logs:
python -m Combat.Tools.prepare_encounters --campaign grims_castle"""

from Combat.Combatants import Bull, Player1
from Combat.EncounterConfig import CampaignSpec, CombatantSpec, EncounterSpec

CONFIG = CampaignSpec(
    name="grims_castle",
    title="Grim's Castle",
    description="No character sheets yet, so there is no tracked party: four placeholder players join each encounter as allies. Every encounter below is played from its log, CombatLogs/<id>.json, prepared with: python -m Combat.Tools.prepare_encounters --campaign grims_castle",
    party=[],
    encounters=[
        EncounterSpec(
            id="grims_castle_bull",
            title="The Bull",
            description="A bull, against the four placeholder players.",
            monsters=[
                CombatantSpec(Bull),
            ],
            allies=[
                CombatantSpec(Player1, "Player", count=4),
            ],
        ),
    ],
)
