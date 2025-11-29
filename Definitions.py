from enum import Enum

from abc import ABC, abstractmethod

import attr


class CharacterClass(Enum):
    BARBARIAN = "Barbarian"
    BARD = "Bard"
    CLERIC = "Cleric"
    DRUID = "Druid"
    FIGHTER = "Fighter"
    MONK = "Monk"
    PALADIN = "Paladin"
    RANGER = "Ranger"
    ROGUE = "Rogue"
    SORCERER = "Sorcerer"
    WARLOCK = "Warlock"
    WIZARD = "Wizard"


class Species(Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    HALFLING = "Halfling"
    ORC = "Orc"
    GNOME = "Gnome"
    TIEFLING = "Tiefling"
    DRAGONBORN = "Dragonborn"


###### ABILITIES AND SKILLS ######


class Ability(Enum):
    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"
    INTELLIGENCE = "Intelligence"
    WISDOM = "Wisdom"
    CHARISMA = "Charisma"


class Skill(Enum):
    ACROBATICS = "Acrobatics"  # Dexterity
    ANIMAL_HANDLING = "Animal Handling"  # Wisdom
    ARCANA = "Arcana"  # Intelligence
    ATHLETICS = "Athletics"  # Strength
    DECEPTION = "Deception"  # Charisma
    HISTORY = "History"  # Intelligence
    INSIGHT = "Insight"  # Wisdom
    INTIMIDATION = "Intimidation"  # Charisma
    INVESTIGATION = "Investigation"  # Intelligence
    MEDICINE = "Medicine"  # Wisdom
    NATURE = "Nature"  # Intelligence
    PERCEPTION = "Perception"  # Wisdom
    PERFORMANCE = "Performance"  # Charisma
    PERSUASION = "Persuasion"  # Charisma
    RELIGION = "Religion"  # Intelligence
    SLEIGHT_OF_HAND = "Sleight of Hand"  # Dexterity
    STEALTH = "Stealth"  # Dexterity
    SURVIVAL = "Survival"  # Wisdom


class DiceRollCondition(Enum):
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"
    NEUTRAL = "Neutral"


class PaladinSubclass(Enum):
    OATH_OF_DEVOTION = "Oath of Devotion"
    OATH_OF_THE_ANCIENTS = "Oath of the Ancients"
    OATH_OF_VENGEANCE = "Oath of Vengeance"
    OATH_OF_CONQUEST = "Oath of Conquest"
    OATH_OF_REDEMPTION = "Oath of Redemption"


class WarlockSubclass(Enum):
    THE_FIEND = "The Fiend"
    THE_ARCHFEY = "The Archfey"
    THE_GREAT_OLD_ONE = "The Great Old One"
    THE_UNDEAD = "The Undead"


class FighterSubclass(Enum):
    BATTLE_MASTER = "Battle Master"


class RangerSubclass(Enum):
    BEAST_MASTER = "Beast Master"


class CreatureSize(Enum):
    TINY = "Tiny"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    HUGE = "Huge"
    GARGANTUAN = "Gargantuan"
