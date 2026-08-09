"""Named, reusable combatant groups that persist across sessions."""

from Builds.Characters.Y2024_Paladin_Vengeance_NadiaIronvow import (
    Y2024PaladinVengeanceNadiaIronvowCharacterBuilder,
)
from Builds.Characters.Y2024_Wizard_Bladesinger_IlyanaBladesong import (
    Y2024WizardBladesingerIlyanaBladesongCharacterBuilder,
)
from Builds.Characters.Y2024_Cleric_Light_SolenneBrightward import (
    Y2024ClericLightSolenneBrightwardCharacterBuilder,
)
from Builds.Characters.Y2024_Rogue_Assassin_LysandraNightblade import (
    Y2024RogueAssassinLysandraNightbladeCharacterBuilder,
)
from Builds.Characters.Y2024_Ranger_GloomStalker_NyxShadowtracker import (
    Y2024RangerGloomStalkerNyxShadowtrackerCharacterBuilder,
)
from Builds.Characters.Y2024_Bard_Lore_TobiasGreyquill import (
    Y2024BardLoreTobiasGreyquillCharacterBuilder,
)


def get_players_group() -> list:
    """The 'Players' combatant group: six character sheets tracked across sessions via --player-log."""
    return [
        Y2024PaladinVengeanceNadiaIronvowCharacterBuilder().build(),
        Y2024WizardBladesingerIlyanaBladesongCharacterBuilder().build(),
        Y2024ClericLightSolenneBrightwardCharacterBuilder().build(),
        Y2024RogueAssassinLysandraNightbladeCharacterBuilder().build(),
        Y2024RangerGloomStalkerNyxShadowtrackerCharacterBuilder().build(),
        Y2024BardLoreTobiasGreyquillCharacterBuilder().build(),
    ]


COMBATANT_GROUPS = {"Players": get_players_group}
