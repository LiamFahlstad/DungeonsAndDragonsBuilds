"""Named, reusable combatant groups that persist across sessions."""

from Builds.Characters.Y2024_Artificer_Cartographer_ObmarStalskagg import (
    Y2024ArtificerCartographerObmarStalskaggCharacterBuilder,
)
from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder,
)
from Builds.Characters.Y2024_Cleric_Light_GabrielGreybeard import (
    Y2024ClericLightGabrielGreybeardCharacterBuilder,
)
from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder,
)
from Builds.Characters.Y2024_Rogue_ArcaneTrickster_ThumSchtock import (
    Y2024RogueArcaneTricksterThumSchtockCharacterBuilder,
)


def get_players_group() -> list:
    """The 'Players' combatant group: six character sheets tracked across sessions via --player-log."""
    return [
        Y2024ArtificerCartographerObmarStalskaggCharacterBuilder().build(),
        Y2024PaladinDevotionEdmundCharacterBuilder().build(),
        Y2024BardValorCloverCharacterBuilder().build(),
        Y2024ClericLightGabrielGreybeardCharacterBuilder().build(),
        Y2024RogueArcaneTricksterThumSchtockCharacterBuilder().build(),
        Y2024MonkElementsKiviJattiCharacterBuilder().build(),
    ]


def get_players_group_not_obmar() -> list:
    """The 'Players' combatant group: six character sheets tracked across sessions via --player-log."""
    return [
        Y2024PaladinDevotionEdmundCharacterBuilder().build(),
        Y2024BardValorCloverCharacterBuilder().build(),
        Y2024ClericLightGabrielGreybeardCharacterBuilder().build(),
        Y2024RogueArcaneTricksterThumSchtockCharacterBuilder().build(),
        Y2024MonkElementsKiviJattiCharacterBuilder().build(),
    ]


COMBATANT_GROUPS = {
    "Players": get_players_group,
    "Players (not Obmar)": get_players_group_not_obmar,
}
