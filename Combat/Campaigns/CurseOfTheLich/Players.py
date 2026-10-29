"""Curse of the Lich's party, from its encounters.json, for scripts that
build the characters themselves (RunBuildGroups.py)."""

from Combat.Campaigns.CurseOfTheLich.Campaign import CAMPAIGN


def get_players_group() -> list:
    """The tracked party's character sheets."""
    return CAMPAIGN.players()


def get_players_group_not_obmar() -> list:
    """The party without Obmar."""
    return [
        cs for cs in CAMPAIGN.players() if not cs.character_name.startswith("Obmar")
    ]
