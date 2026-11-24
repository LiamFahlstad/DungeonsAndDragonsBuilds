"""Curse of the Lich's party, from its encounters.py, for scripts that
build the characters themselves (RunBuildGroups.py)."""

from Combat.Campaigns.CurseOfTheLich.campaign import CAMPAIGN


def get_players_group_not_obmar() -> list:
    """The party without Obmar."""
    return [
        cs for cs in CAMPAIGN.players() if not cs.character_name.startswith("Obmar")
    ]
