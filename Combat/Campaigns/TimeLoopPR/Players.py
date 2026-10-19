"""Named, reusable combatant groups for the TimeLoopPR oneshot."""

from Builds.Characters.Y2024_Artificer_Reanimator_Dessie import (
    Y2024ArtificerReanimatorDessieCharacterBuilder,
)
from Builds.Characters.Y2024_Bard_Valor_Thomas import (
    Y2024BardValorThomasCharacterBuilder,
)
from Builds.Characters.Y2024_Druid_Moon_Maggie import (
    Y2024DruidMoonMaggieCharacterBuilder,
)
from Builds.Characters.Y2024_Ranger_Drakewarden_Hanna import (
    Y2024RangerDrakewardenHannaCharacterBuilder,
)


def get_players_group() -> list:
    """The 'Players' combatant group: the four oneshot character sheets tracked via --player-log."""
    return [
        Y2024ArtificerReanimatorDessieCharacterBuilder().build(),
        Y2024RangerDrakewardenHannaCharacterBuilder().build(),
        Y2024DruidMoonMaggieCharacterBuilder().build(),
        Y2024BardValorThomasCharacterBuilder().build(),
    ]


COMBATANT_GROUPS = {
    "Players": get_players_group,
}
