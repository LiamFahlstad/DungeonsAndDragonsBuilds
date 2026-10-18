"""The tracked party for Grim's Castle."""


def get_players_group() -> list:
    """The 'Players' combatant group tracked via --player-log. Grim's Castle has
    no character sheets yet: its placeholder players (Encounters.get_players)
    are added to each scenario as allies instead."""
    return []


COMBATANT_GROUPS = {
    "Players": get_players_group,
}
