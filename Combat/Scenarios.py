"""Registry of every campaign and its runnable combat scenarios. Select one with
`python RunCombatSimulator.py --scenario <name>`.

Each campaign lives entirely in Combat/Campaigns/<Campaign>/ and declares its
party and scenarios in that folder's Campaign.py. To add a campaign, create its
folder and add its CAMPAIGN to the tuple below."""

from Combat.Campaign import Campaign
from Combat.Campaigns.CurseOfTheLich.Campaign import CAMPAIGN as CURSE_OF_THE_LICH
from Combat.Campaigns.TimeLoopPR.Campaign import CAMPAIGN as TIME_LOOP_PR
from Combat.Scenario import CombatScenario

CAMPAIGNS: dict[str, Campaign] = {
    campaign.name: campaign for campaign in (CURSE_OF_THE_LICH, TIME_LOOP_PR)
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
