"""This campaign, as its encounters.py describes it: the party and every
encounter it can run (format: Combat/Campaigns/ENCOUNTERS.md). See
CHEATSHEET.md next to this file for the commands."""

from pathlib import Path

from Combat.Campaign import Campaign
from Combat.Campaigns.CurseOfTheLich.encounters import CONFIG

CAMPAIGN = Campaign.from_config(CONFIG, Path(__file__).resolve().parent)
