from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from Combat.Scenario import CombatScenario


@dataclass
class Campaign:
    """A self-contained campaign living in Combat/Campaigns/<Campaign>/: its
    tracked party, its scenarios, and the folders holding its logs.

    `name` is the key used on the command line (--campaign). `players` builds
    the 'Players' group tracked by --player-log. Player logs live in
    `<folder>/PlayerLogs/`, encounter logs in `<folder>/CombatLogs/`."""

    name: str
    folder: Path
    players: Callable[[], list]
    scenarios: list[CombatScenario] = field(default_factory=list)
    # How the statistics report names it, e.g. "Curse of the Lich"; defaults to
    # `name` title-cased.
    title: str = ""

    @property
    def display_title(self) -> str:
        return self.title or self.name.replace("_", " ").title()

    @property
    def player_log_dir(self) -> Path:
        return self.folder / "PlayerLogs"

    @property
    def combat_log_dir(self) -> Path:
        return self.folder / "CombatLogs"

    @property
    def default_player_log(self) -> Path:
        return self.player_log_dir / "main_party.json"
