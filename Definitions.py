from enum import Enum

from abc import ABC, abstractmethod

import attr


class CharacterClass(str, Enum):
    ARTIFICER = "Artificer"
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

    @property
    def hit_die(self) -> int:
        hit_dice_mapping = {
            CharacterClass.ARTIFICER: 8,
            CharacterClass.BARBARIAN: 12,
            CharacterClass.BARD: 8,
            CharacterClass.CLERIC: 8,
            CharacterClass.DRUID: 8,
            CharacterClass.FIGHTER: 10,
            CharacterClass.MONK: 8,
            CharacterClass.PALADIN: 10,
            CharacterClass.RANGER: 10,
            CharacterClass.ROGUE: 8,
            CharacterClass.SORCERER: 6,
            CharacterClass.WARLOCK: 8,
            CharacterClass.WIZARD: 6,
        }
        return hit_dice_mapping[self]

    @property
    def average_hit_die(self) -> int:
        return (self.hit_die // 2) + 1


class Species(str, Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    HALFLING = "Halfling"
    ORC = "Orc"
    GNOME = "Gnome"
    TIEFLING = "Tiefling"
    DRAGONBORN = "Dragonborn"


###### ABILITIES AND SKILLS ######


class Ability(str, Enum):
    STRENGTH = "Strength"
    DEXTERITY = "Dexterity"
    CONSTITUTION = "Constitution"
    INTELLIGENCE = "Intelligence"
    WISDOM = "Wisdom"
    CHARISMA = "Charisma"


class Skill(str, Enum):
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


class DiceRollCondition(str, Enum):
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"
    NEUTRAL = "Neutral"


class PaladinSubclass(str, Enum):
    OATH_OF_DEVOTION = "Oath of Devotion"
    OATH_OF_THE_ANCIENTS = "Oath of the Ancients"
    OATH_OF_GLORY = "Oath of Glory"
    OATH_OF_VENGEANCE = "Oath of Vengeance"
    OATH_OF_CONQUEST = "Oath of Conquest"
    OATH_OF_REDEMPTION = "Oath of Redemption"


class RogueSubclass(str, Enum):
    THIEF = "Thief"
    ASSASSIN = "Assassin"
    ARCANE_TRICKSTER = "Arcane Trickster"
    SOUL_KNIFE = "Soul Knife"
    SCION_OF_THE_THREE = "Scion of the Three"


class WizardSubclass(str, Enum):
    ABJURER = "Abjurer"
    DIVINER = "Diviner"
    EVOKER = "Evoker"
    ILLUSIONIST = "Illusionist"
    BLADESINGER = "Bladesinger"


class WarlockSubclass(str, Enum):
    THE_FIEND = "The Fiend"
    THE_ARCHFEY = "The Archfey"
    THE_GREAT_OLD_ONE = "The Great Old One"
    THE_UNDEAD = "The Undead"


class FighterSubclass(str, Enum):
    BATTLE_MASTER = "Battle Master"


class RangerSubclass(str, Enum):
    BEAST_MASTER = "Beast Master"
    HUNTER = "Hunter"


class BarbarianSubclass(str, Enum):
    PATH_OF_THE_BERSERKER = "Path of the Berserker"
    PATH_OF_THE_ZEALOT = "Path of the Zealot"
    PATH_OF_THE_WORLD_TREE = "Path of the World Tree"
    PATH_OF_THE_WILD_HEART = "Path of the Wild Heart"


class CreatureSize(str, Enum):
    TINY = "Tiny"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    HUGE = "Huge"
    GARGANTUAN = "Gargantuan"


class DamageType(str, Enum):
    ACID = "Acid"
    BLUDGEONING = "Bludgeoning"
    COLD = "Cold"
    FIRE = "Fire"
    FORCE = "Force"
    LIGHTNING = "Lightning"
    NECROTIC = "Necrotic"
    PIERCING = "Piercing"
    POISON = "Poison"
    PSYCHIC = "Psychic"
    RADIANT = "Radiant"
    SLASHING = "Slashing"
    THUNDER = "Thunder"
