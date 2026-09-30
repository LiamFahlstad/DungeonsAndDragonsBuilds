"""Alias kept so the existing `from StatBlocks.CharacterStatBlock import
CharacterStatBlock` imports keep working: the stat block and the sheet data
are one object now, Character (StatBlocks/Character.py). Step 10 of the
character-model plan renames every use and removes this module."""

from StatBlocks.Character import Character

CharacterStatBlock = Character
