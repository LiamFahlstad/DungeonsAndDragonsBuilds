"""Registry of every campaign and its runnable combat scenarios. Select one with
`python RunCombatSimulator.py --scenario <name>`.

Each campaign lives entirely in Combat/Campaigns/<Campaign>/: its party and
encounters are in that folder's encounters.py (Combat/Campaigns/ENCOUNTERS.md),
which its Campaign.py loads. To add a campaign, create its folder and add its
CAMPAIGN to the tuple below."""

from pathlib import Path

from Combat.Campaign import Campaign
from Combat.Campaigns.CurseOfTheLich.Campaign import CAMPAIGN as CURSE_OF_THE_LICH
from Combat.Campaigns.GrimsCastle.Campaign import CAMPAIGN as GRIMS_CASTLE
from Combat.Campaigns.TimeLoopPR.Campaign import CAMPAIGN as TIME_LOOP_PR
from Combat.Scenario import CombatScenario

CAMPAIGNS: dict[str, Campaign] = {
    campaign.name: campaign
    for campaign in (CURSE_OF_THE_LICH, TIME_LOOP_PR, GRIMS_CASTLE)
}
DEFAULT_CAMPAIGN = CURSE_OF_THE_LICH.name

# Scenario name -> scenario, and scenario name -> the campaign it belongs to.
SCENARIOS: dict[str, CombatScenario] = {}
SCENARIO_CAMPAIGNS: dict[str, Campaign] = {}
for _campaign in CAMPAIGNS.values():
    for _scenario in _campaign.scenarios:
        if _scenario.name in SCENARIOS:
            raise ValueError(
                f"Scenario '{_scenario.name}' is defined by both "
                f"'{SCENARIO_CAMPAIGNS[_scenario.name].name}' and '{_campaign.name}'"
            )
        SCENARIOS[_scenario.name] = _scenario
        SCENARIO_CAMPAIGNS[_scenario.name] = _campaign


def campaign_of_player_log(path: str | Path) -> Campaign | None:
    """The campaign whose PlayerLogs/ folder holds the player log at `path`,
    or None for a log kept anywhere else."""
    return next((c for c in CAMPAIGNS.values() if c.owns_player_log(path)), None)


def pick_campaign(
    scenario: str | None = None,
    campaign: str | None = None,
    player_log: str | Path | None = None,
) -> Campaign:
    """The campaign RunCombatSimulator.py runs: --scenario's, else
    --campaign, else the one whose PlayerLogs/ holds --player-log, else
    DEFAULT_CAMPAIGN. Raises ValueError when they disagree: a party log
    played with another campaign's party would be replayed onto the wrong
    characters, and point to encounters that campaign doesn't have."""
    if scenario:
        chosen = SCENARIO_CAMPAIGNS[scenario]
        if campaign and campaign != chosen.name:
            raise ValueError(
                f"--scenario {scenario} belongs to campaign '{chosen.name}', "
                f"not '{campaign}'"
            )
    elif campaign:
        chosen = CAMPAIGNS[campaign]
    else:
        chosen = None
    log_campaign = campaign_of_player_log(player_log) if player_log else None
    if chosen is None:
        chosen = log_campaign or CAMPAIGNS[DEFAULT_CAMPAIGN]
    if log_campaign is not None and log_campaign is not chosen:
        raise ValueError(
            f"--player-log {player_log} is campaign '{log_campaign.name}''s party "
            f"log, not '{chosen.name}''s"
        )
    return chosen
