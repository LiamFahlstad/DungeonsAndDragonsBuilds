from enum import Enum


###### HIT DICE ######

ARTIFICER_HIT_DIE = 8
BARBARIAN_HIT_DIE = 12
BARD_HIT_DIE = 8
CLERIC_HIT_DIE = 8
DRUID_HIT_DIE = 8
FIGHTER_HIT_DIE = 10
MONK_HIT_DIE = 8
PALADIN_HIT_DIE = 10
PSION_HIT_DIE = 6
RANGER_HIT_DIE = 10
ROGUE_HIT_DIE = 8
SORCERER_HIT_DIE = 6
WARLOCK_HIT_DIE = 8
WIZARD_HIT_DIE = 6


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

    @property
    def short_name(self) -> str:
        short_names = {
            Ability.STRENGTH: "STR",
            Ability.DEXTERITY: "DEX",
            Ability.CONSTITUTION: "CON",
            Ability.INTELLIGENCE: "INT",
            Ability.WISDOM: "WIS",
            Ability.CHARISMA: "CHA",
        }
        return short_names[self]


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

    @staticmethod
    def list_sorted() -> list["Skill"]:
        return sorted(Skill, key=lambda skill: skill.value)


class HomeBrewSkill(str, Enum):
    ACROBATICS = "Acrobatics"  # Dexterity
    SPIRIT = "Spirit"  # Wisdom
    ARCANA = "Arcana"  # Intelligence
    ATHLETICS = "Athletics"  # Strength
    DECEPTION = "Deception"  # Charisma
    LORE = "Lore"  # Intelligence
    INSIGHT = "Insight"  # Wisdom
    INTIMIDATION = "Intimidation"  # Charisma
    INVESTIGATION = "Investigation"  # Intelligence
    MEDICINE = "Medicine"  # Wisdom
    NATURE = "Nature"  # Intelligence
    PERCEPTION = "Perception"  # Wisdom
    PERFORMANCE = "Performance"  # Charisma
    PERSUASION = "Persuasion"  # Charisma
    SLEIGHT_OF_HAND = "Sleight of Hand"  # Dexterity
    STEALTH = "Stealth"  # Dexterity

    @staticmethod
    def list_sorted() -> list["HomeBrewSkill"]:
        return sorted(HomeBrewSkill, key=lambda skill: skill.value)


class SkillConfig(str, Enum):
    DEFAULT = "Default"
    HOMEBREW = "Homebrew"

    @staticmethod
    def map_homebrew_to_default(skill: HomeBrewSkill) -> list[Skill]:
        default_mapping = {
            HomeBrewSkill.ACROBATICS: [Skill.ACROBATICS],
            HomeBrewSkill.SPIRIT: [Skill.ANIMAL_HANDLING],
            HomeBrewSkill.ARCANA: [Skill.ARCANA],
            HomeBrewSkill.ATHLETICS: [Skill.ATHLETICS],
            HomeBrewSkill.DECEPTION: [Skill.DECEPTION],
            HomeBrewSkill.LORE: [Skill.HISTORY, Skill.RELIGION],
            HomeBrewSkill.INSIGHT: [Skill.INSIGHT],
            HomeBrewSkill.INTIMIDATION: [Skill.INTIMIDATION],
            HomeBrewSkill.INVESTIGATION: [Skill.INVESTIGATION],
            HomeBrewSkill.MEDICINE: [Skill.MEDICINE],
            HomeBrewSkill.NATURE: [Skill.NATURE, Skill.SURVIVAL],
            HomeBrewSkill.PERCEPTION: [Skill.PERCEPTION],
            HomeBrewSkill.PERFORMANCE: [Skill.PERFORMANCE],
            HomeBrewSkill.PERSUASION: [Skill.PERSUASION],
            HomeBrewSkill.SLEIGHT_OF_HAND: [Skill.SLEIGHT_OF_HAND],
            HomeBrewSkill.STEALTH: [Skill.STEALTH],
        }
        return default_mapping[skill]


class DiceRollCondition(str, Enum):
    ADVANTAGE = "Advantage"
    DISADVANTAGE = "Disadvantage"
    NEUTRAL = "Neutral"


class ArtificerSubclass(str, Enum):
    ALCHEMIST = "Alchemist"
    ARMORER = "Armorer"
    ARTILLERIST = "Artillerist"
    BATTLE_SMITH = "Battle Smith"
    CARTOGRAPHER = "Cartographer"
    REANIMATOR = "Reanimator"


class ArtificerSubclass2014(str, Enum):
    ALCHEMIST = "Alchemist"
    ARMORER = "Armorer"
    ARTILLERIST = "Artillerist"
    BATTLE_SMITH = "Battle Smith"


class PaladinSubclass(str, Enum):
    OATH_OF_DEVOTION = "Oath of Devotion"
    OATH_OF_THE_ANCIENTS = "Oath of the Ancients"
    OATH_OF_GLORY = "Oath of Glory"
    OATH_OF_VENGEANCE = "Oath of Vengeance"
    OATH_OF_CONQUEST = "Oath of Conquest"
    OATH_OF_REDEMPTION = "Oath of Redemption"
    OATH_OF_GENIES = "Oath of Genies"


class PaladinSubclass2014(str, Enum):
    OATHBREAKER = "Oathbreaker"
    DEVOTION = "Oath of Devotion"
    VENGEANCE = "Oath of Vengeance"
    REDEMPTION = "Oath of Redemption"
    CONQUEST = "Oath of Conquest"
    CROWN = "Oath of the Crown"
    WATCHERS = "Oath of the Watchers"


class ClericSubclass(str, Enum):
    LIGHT = "Light"
    LIFE = "Life"
    WAR = "War"
    KNOWLEDGE = "Knowledge"
    NATURE = "Nature"
    TEMPEST = "Tempest"
    TRICKERY = "Trickery"
    DEATH = "Death"
    GRAVE = "Grave"


class ClericSubclass2014(str, Enum):
    ARCANA = "Arcana"
    FORGE = "Forge"
    LIFE = "Life"
    DEATH = "Death"
    NATURE = "Nature"
    ORDER = "Order"
    PEACE = "Peace"
    TEMPEST = "Tempest"
    TWILIGHT = "Twilight"


class RogueSubclass(str, Enum):
    THIEF = "Thief"
    ASSASSIN = "Assassin"
    ARCANE_TRICKSTER = "Arcane Trickster"
    SOUL_KNIFE = "Soul Knife"
    SCION_OF_THE_THREE = "Scion of the Three"
    PHANTOM = "Phantom"


class RogueSubclass2014(str, Enum):
    SWASHBUCKLER = "Swashbuckler"
    THIEF = "Thief"
    MASTERMIND = "Mastermind"
    SCOUT = "Scout"
    ASSASSIN = "Assassin"


class BardSubclass(str, Enum):
    LORE = "College of Lore"
    VALOR = "College of Valor"
    GLAMOUR = "College of Glamour"
    SWORD = "College of Swords"
    WHISPERS = "College of Whispers"
    MOON = "College of the Moon"
    DANCE = "College of Dance"
    SPIRITS = "College of Spirits"


class BardSubclass2014(str, Enum):
    ELOQUENCE = "College of Eloquence"
    LORE = "College of Lore"
    WHISPERS = "College of Whispers"
    SWORD = "College of Swords"
    CREATION = "College of Creation"


class DruidSubclass(str, Enum):
    MOON = "Circle of the Moon"
    LAND = "Circle of the Land"
    DREAMS = "Circle of Dreams"
    SHELL = "Circle of the Shell"
    SEA = "Circle of the Sea"
    STARS = "Circle of the Stars"


class DruidSubclass2014(str, Enum):
    SPORES = "Circle of Spores"
    DREAMS = "Circle of Dreams"
    SHEPHERD = "Circle of the Shepherd"
    WILDFIRE = "Circle of Wildfire"


class DruidLandType(str, Enum):
    ARID = "Arid"
    POLAR = "Polar"
    TEMPERATE = "Temperate"
    TROPICAL = "Tropical"


class WizardSubclass(str, Enum):
    ABJURER = "Abjurer"
    DIVINER = "Diviner"
    EVOKER = "Evoker"
    ILLUSIONIST = "Illusionist"
    BLADESINGER = "Bladesinger"
    TRANSMUTER = "Transmuter"


class WizardSubclass2014(str, Enum):
    NECROMANCY = "Necromancy"
    EVOCATION = "Evocation"
    ABJURATION = "Abjuration"
    ILLUSION = "Illusion"
    CONJURATION = "Conjuration"
    ENCHANTMENT = "Enchantment"
    ORDER_OF_SCRIBES = "Order of Scribes"
    CHRONURGY = "Chronurgy"
    GRAVITURGY = "Graviturgy"
    DIVINATION = "Divination"


class SorcererSubclass(str, Enum):
    ABERRANT = "Aberrant Sorcery"
    CLOCKWORK = "Clockwork Sorcery"
    DRACONIC = "Draconic Sorcery"
    SHADOW = "Shadow Sorcery"
    SPELLFIRE = "Spellfire Sorcery"
    WILD_MAGIC = "Wild Magic Sorcery"


class SorcererSubclass2014(str, Enum):
    STORM = "Storm"
    DRACONIC = "Draconic"
    DIVINE_SOUL = "Divine Soul"
    LUNAR_SORCERY = "Lunar Sorcery"
    ABERRANT_MIND = "Aberrant Mind"


class WarlockSubclass(str, Enum):
    THE_FIEND = "The Fiend"
    THE_ARCHFEY = "The Archfey"
    THE_GREAT_OLD_ONE = "The Great Old One"
    THE_UNDEAD = "The Undead"
    THE_CELESTIAL = "The Celestial"


class WarlockSubclass2014(str, Enum):
    HEXBLADE = "Hexblade"
    FIEND = "Fiend"
    THE_ARCHFEY = "The Archfey"
    THE_GREAT_OLD_ONE = "The Great Old One"
    THE_FATHOMLESS = "The Fathomless"
    THE_GENIE = "The Genie"
    THE_UNDYING = "The Undying"
    THE_CELESTIAL = "The Celestial"


class WarlockGenieKind(str, Enum):
    DAO = "Dao"
    DJINNI = "Djinni"
    EFREETI = "Efreeti"
    MARID = "Marid"


class FighterSubclass(str, Enum):
    BANNERET = "Banneret"
    BATTLE_MASTER = "Battle Master"
    CHAMPION = "Champion"
    ELDRITCH_KNIGHT = "Eldritch Knight"
    PSI_WARRIOR = "Psi Warrior"


class FighterSubclass2014(str, Enum):
    RUNE_KNIGHT = "Rune Knight"
    CHAMPION = "Champion"
    BATTLE_MASTER = "Battle Master"
    ELDRITCH_KNIGHT = "Eldritch Knight"
    CAVALIER = "Cavalier"
    ARCANE_ARCHER = "Arcane Archer"
    ECHO_KNIGHT = "Echo Knight"
    SAMURAI = "Samurai"


class RangerSubclass(str, Enum):
    BEAST_MASTER = "Beast Master"
    HUNTER = "Hunter"
    FEY_WANDERER = "Fey Wanderer"
    GLOOM_STALKER = "Gloom Stalker"
    HOLLOW_WARDEN = "Hollow Warden"
    WINTER_WALKER = "Winter Walker"


class RangerSubclass2014(str, Enum):
    HORIZON_WALKER = "Horizon Walker"
    HUNTER = "Hunter"
    SWARMKEEPER = "Swarmkeeper"
    MONSTER_SLAYER = "Monster Slayer"
    DRAKEWARDEN = "Drakewarden"
    GLOOM_STALKER = "Gloom Stalker"


class MonkSubclass(str, Enum):
    SHADOW = "Shadow"
    MYSTIC_ARTS = "Mystic Arts"
    MERCY = "Mercy"
    ELEMENTS = "the Elements"
    OPEN_HAND = "Open Hand"


class MonkSubclass2014(str, Enum):
    KENSEI = "Kensei"
    SUN_SOUL = "Sun Soul"
    ASTRAL_SELF = "Astral Self"
    DRUNKEN_MASTER = "Drunken Master"
    LONG_DEATH = "Long Death"
    OPEN_HAND = "Open Hand"


class BarbarianSubclass(str, Enum):
    PATH_OF_THE_BERSERKER = "Path of the Berserker"
    PATH_OF_THE_ZEALOT = "Path of the Zealot"
    PATH_OF_THE_WORLD_TREE = "Path of the World Tree"
    PATH_OF_THE_WILD_HEART = "Path of the Wild Heart"


class BarbarianSubclass2014(str, Enum):
    PATH_OF_THE_TOTEM_WARRIOR = "Path of the Totem Warrior"
    PATH_OF_THE_BERSERKER = "Path of the Berserker"
    PATH_OF_THE_STORM_HERALD = "Path of the Storm Herald"
    PATH_OF_THE_ANCESTRAL_GUARDIAN = "Path of the Ancestral Guardian"
    PATH_OF_THE_BATTLERAGER = "Path of the Battlerager"
    PATH_OF_WILD_MAGIC = "Path of Wild Magic"


class BarbarianStormEnvironment(str, Enum):
    DESERT = "Desert"
    SEA = "Sea"
    TUNDRA = "Tundra"


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


# Damage type color mapping (mirrors Spell.SCHOOL_COLORS)
DAMAGE_TYPE_COLORS: dict[str, str] = {
    "Acid": "#7CB342",
    "Bludgeoning": "#795548",
    "Cold": "#4FC3F7",
    "Fire": "#FF5722",
    "Force": "#BA68C8",
    "Lightning": "#FFC107",
    "Necrotic": "#4A148C",
    "Piercing": "#9E9E9E",
    "Poison": "#43A047",
    "Psychic": "#EC407A",
    "Radiant": "#FFD54F",
    "Slashing": "#B71C1C",
    "Thunder": "#3F51B5",
}


def get_damage_type_color(damage_type: str) -> str:
    """Return the color hex code for a damage type, or a default gray if unknown."""
    return DAMAGE_TYPE_COLORS.get(damage_type, "#999999")


class ArmorType(str, Enum):
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"
    SHIELD = "Shield"


###### RESISTANCES, SENSES, AND LANGUAGES ######


class Language(str, Enum):
    COMMON = "Common"
    COMMON_SIGN_LANGUAGE = "Common Sign Language"
    DRACONIC = "Draconic"
    DWARVISH = "Dwarvish"
    ELVISH = "Elvish"
    GIANT = "Giant"
    GNOMISH = "Gnomish"
    GOBLIN = "Goblin"
    HALFLING = "Halfling"
    ORC = "Orc"
    ABYSSAL = "Abyssal"
    CELESTIAL = "Celestial"
    DEEP_SPEECH = "Deep Speech"
    INFERNAL = "Infernal"
    PRIMORDIAL = "Primordial"
    SYLVAN = "Sylvan"
    UNDERCOMMON = "Undercommon"
    DRUIDIC = "Druidic"
    THIEVES_CANT = "Thieves' Cant"

    @staticmethod
    def list_sorted() -> list["Language"]:
        return sorted(Language, key=lambda language: language.value)


class Sense(str, Enum):
    DARKVISION = "Darkvision"
    BLINDSIGHT = "Blindsight"
    TREMORSENSE = "Tremorsense"
    TRUESIGHT = "Truesight"


class Condition(str, Enum):
    BLINDED = "Blinded"
    CHARMED = "Charmed"
    DEAFENED = "Deafened"
    EXHAUSTION = "Exhaustion"
    FRIGHTENED = "Frightened"
    GRAPPLED = "Grappled"
    INCAPACITATED = "Incapacitated"
    INVISIBLE = "Invisible"
    PARALYZED = "Paralyzed"
    PETRIFIED = "Petrified"
    POISONED = "Poisoned"
    PRONE = "Prone"
    RESTRAINED = "Restrained"
    STUNNED = "Stunned"
    UNCONSCIOUS = "Unconscious"

    @staticmethod
    def list_sorted() -> list["Condition"]:
        return sorted(Condition, key=lambda condition: condition.value)


class ApplyWhen(str, Enum):
    IMMEDIATE = "immediate"
    LAST = "last"


class Die(int, Enum):
    D1 = 1
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20

    @property
    def average(self) -> float:
        return (self.value + 1) / 2

    @classmethod
    def die_from_value(cls, value: int) -> "Die":
        for die in Die:
            if die.value == value:
                return die
        raise ValueError(f"No Die found with value {value}")

    def average_with_advantage(self) -> float:
        sides = self.value
        return sum(
            k * ((k / sides) ** 2 - ((k - 1) / sides) ** 2) for k in range(1, sides + 1)
        )

    def average_with_disadvantage(self) -> float:
        sides = self.value
        return sum(
            k * (((sides - k + 1) / sides) ** 2 - ((sides - k) / sides) ** 2)
            for k in range(1, sides + 1)
        )
