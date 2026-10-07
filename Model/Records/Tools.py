"""ToolProficiency: training with a tool. A plain record - it imports
nothing from the rest of the Model - so the Ledger's EquipmentTraining part
can record it."""

from typing import Optional

from Core.Definitions import Ability


class ToolProficiency:
    """Training with a tool, not the tool itself (that's the same-named item,
    see CharacterContent/ToolProficiencies/Proficiencies.TOOL_ITEMS). It adds
    the proficiency bonus to ability checks made with the tool, lists what
    the tool lets you do with the Utilize action (each with its DC) and,
    where listed, the items you can craft with it during downtime."""

    def __init__(
        self,
        name: str,
        category: str,
        ability: Ability,
        utilize: list[tuple[str, int]],
        craftables: Optional[list[str]] = None,
    ):
        self.name = name
        self.category = category
        self.ability = ability
        # (what you can do, DC) pairs - one of these per Utilize action.
        self.utilize = utilize
        # The names of the items you can craft with it.
        self.craftables = craftables if craftables is not None else []

    def utilize_text(self) -> str:
        options = [f"{action} (DC {dc})" for action, dc in self.utilize]
        # Each option is stored capitalized; lower-case all but the first so
        # they read as one sentence ("Pick a lock (DC 15), or disarm a trap").
        options[1:] = [option[0].lower() + option[1:] for option in options[1:]]
        return ", or ".join(options)

    def craft_text(self) -> str:
        return ", ".join(self.craftables)
