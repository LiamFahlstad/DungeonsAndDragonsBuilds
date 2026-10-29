"""This campaign, as its encounters.json describes it: the party and every
encounter it can run (format: Combat/Campaigns/ENCOUNTERS.md). See
CHEATSHEET.md next to this file for the commands."""

from pathlib import Path

from Combat.Campaign import Campaign

CAMPAIGN = Campaign.from_config(Path(__file__).resolve().parent)
