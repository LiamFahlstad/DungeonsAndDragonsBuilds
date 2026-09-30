"""Alias kept so the existing `from Builds.CharacterSheetAccumulator import
CharacterSheetData` imports keep working: the sheet data and the stat block
are one object now, Character (StatBlocks/Character.py). Step 10 of the
character-model plan renames every use and removes this module."""

from StatBlocks.Character import MAX_ATTUNED_ITEMS, Character

CharacterSheetData = Character

__all__ = ["CharacterSheetData", "MAX_ATTUNED_ITEMS"]
