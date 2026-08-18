"""Named, reusable combatant groups that persist across sessions."""

from Builds.Characters.Y2024_Artificer_Cartographer_ObmarStalskagg import (
    Y2024ArtificerCartographerObmarStalskaggCharacterBuilder,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder,
)
from Builds.Characters.Y2024_Bard_Valor_Clover import (
    Y2024BardValorCloverCharacterBuilder,
)
from Builds.Characters.Y2024_Cleric_Light_Grabriel import (
    Y2024ClericLightGrabrielCharacterBuilder,
)
from Builds.Characters.Y2024_Rogue_ArcaneTrickster_ThumSchtock import (
    Y2024RogueArcaneTricksterThumSchtockCharacterBuilder,
)
from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder,
)


def get_players_group() -> list:
    """The 'Players' combatant group: six character sheets tracked across sessions via --player-log."""
    return [
        Y2024ArtificerCartographerObmarStalskaggCharacterBuilder().build(),
        Y2024PaladinDevotionEdmundCharacterBuilder().build(),
        Y2024BardValorCloverCharacterBuilder().build(),
        Y2024ClericLightGrabrielCharacterBuilder().build(),
        Y2024RogueArcaneTricksterThumSchtockCharacterBuilder().build(),
        Y2024MonkElementsKiviJattiCharacterBuilder().build(),
    ]


COMBATANT_GROUPS = {"Players": get_players_group}
