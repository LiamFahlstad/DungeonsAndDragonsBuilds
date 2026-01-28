from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional

import Definitions


class SorcererLevel0Spells(str, Enum):
    ACID_SPLASH = "Acid Splash"
    BLADE_WARD = "Blade Ward"
    CHILL_TOUCH = "Chill Touch"
    DANCING_LIGHTS = "Dancing Lights"
    ELEMENTALISM = "Elementalism"
    FIRE_BOLT = "Fire Bolt"
    FRIENDS = "Friends"
    LIGHT = "Light"
    MAGE_HAND = "Mage Hand"
    MENDING = "Mending"
    MESSAGE = "Message"
    MIND_SLIVER = "Mind Sliver"
    MINOR_ILLUSION = "Minor Illusion"
    POISON_SPRAY = "Poison Spray"
    PRESTIDIGITATION = "Prestidigitation"
    RAY_OF_FROST = "Ray of Frost"
    SHOCKING_GRASP = "Shocking Grasp"
    SORCEROUS_BURST = "Sorcerous Burst"
    THUNDERCLAP = "Thunderclap"
    TRUE_STRIKE = "True Strike"


class SorcererLevel1Spells(str, Enum):
    BURNING_HANDS = "Burning Hands"
    CHARM_PERSON = "Charm Person"
    CHROMATIC_ORB = "Chromatic Orb"
    COLOR_SPRAY = "Color Spray"
    COMPREHEND_LANGUAGES = "Comprehend Languages"
    DETECT_MAGIC = "Detect Magic"
    DISGUISE_SELF = "Disguise Self"
    EXPEDITIOUS_RETREAT = "Expeditious Retreat"
    FALSE_LIFE = "False Life"
    FEATHER_FALL = "Feather Fall"
    FOG_CLOUD = "Fog Cloud"
    GREASE = "Grease"
    ICE_KNIFE = "Ice Knife"
    JUMP = "Jump"
    MAGE_ARMOR = "Mage Armor"
    MAGIC_MISSILE = "Magic Missile"
    RAY_OF_SICKNESS = "Ray of Sickness"
    SHIELD = "Shield"
    SILENT_IMAGE = "Silent Image"
    SLEEP = "Sleep"
    SPELLFIRE_FLARE = "Spellfire Flare"
    THUNDERWAVE = "Thunderwave"
    WITCH_BOLT = "Witch Bolt"


class SorcererLevel2Spells(str, Enum):
    ALTER_SELF = "Alter Self"
    ARCANE_VIGOR = "Arcane Vigor"
    BLINDNESS_DEAFNESS = "Blindness/Deafness"
    BLUR = "Blur"
    CLOUD_OF_DAGGERS = "Cloud of Daggers"
    CROWN_OF_MADNESS = "Crown of Madness"
    DARKNESS = "Darkness"
    DARKVISION = "Darkvision"
    DEATH_ARMOR = "Death Armor"
    DETECT_THOUGHTS = "Detect Thoughts"
    DRAGONS_BREATH = "Dragon's Breath"
    ENHANCE_ABILITY = "Enhance Ability"
    ENLARGE_REDUCE = "Enlarge/Reduce"
    FLAME_BLADE = "Flame Blade"
    FLAMING_SPHERE = "Flaming Sphere"
    GUST_OF_WIND = "Gust of Wind"
    HOLD_PERSON = "Hold Person"
    INVISIBILITY = "Invisibility"
    KNOCK = "Knock"
    LEVITATE = "Levitate"
    MAGIC_WEAPON = "Magic Weapon"
    MIND_SPIKE = "Mind Spike"
    MIRROR_IMAGE = "Mirror Image"
    MISTY_STEP = "Misty Step"
    PHANTASMAL_FORCE = "Phantasmal Force"
    SCORCHING_RAY = "Scorching Ray"
    SEE_INVISIBILITY = "See Invisibility"
    SHATTER = "Shatter"
    SPIDER_CLIMB = "Spider Climb"
    SUGGESTION = "Suggestion"
    WEB = "Web"


class SorcererLevel3Spells(str, Enum):
    BLINK = "Blink"
    CACOPHONIC_SHIELD = "Cacophonic Shield"
    CLAIRVOYANCE = "Clairvoyance"
    COUNTERSPELL = "Counterspell"
    DAYLIGHT = "Daylight"
    DISPEL_MAGIC = "Dispel Magic"
    FEAR = "Fear"
    FIREBALL = "Fireball"
    FLY = "Fly"
    GASEOUS_FORM = "Gaseous Form"
    HASTE = "Haste"
    HYPNOTIC_PATTERN = "Hypnotic Pattern"
    LAERALS_SILVER_LANCE = "Laeral's Silver Lance"
    LIGHTNING_BOLT = "Lightning Bolt"
    MAJOR_IMAGE = "Major Image"
    PROTECTION_FROM_ENERGY = "Protection from Energy"
    SLEET_STORM = "Sleet Storm"
    SLOW = "Slow"
    STINKING_CLOUD = "Stinking Cloud"
    TONGUES = "Tongues"
    VAMPIRIC_TOUCH = "Vampiric Touch"
    WATER_BREATHING = "Water Breathing"
    WATER_WALK = "Water Walk"


class SorcererLevel4Spells(str, Enum):
    BACKLASH = "Backlash"
    BANISHMENT = "Banishment"
    BLIGHT = "Blight"
    CHARM_MONSTER = "Charm Monster"
    CONFUSION = "Confusion"
    DIMENSION_DOOR = "Dimension Door"
    DOMINATE_BEAST = "Dominate Beast"
    FIRE_SHIELD = "Fire Shield"
    GREATER_INVISIBILITY = "Greater Invisibility"
    ICE_STORM = "Ice Storm"
    POLYMORPH = "Polymorph"
    SPELLFIRE_STORM = "Spellfire Storm"
    STONESKIN = "Stoneskin"
    VITRIOLIC_SPHERE = "Vitriolic Sphere"
    WALL_OF_FIRE = "Wall of Fire"


class SorcererLevel5Spells(str, Enum):
    ANIMATE_OBJECTS = "Animate Objects"
    BIGBYS_HAND = "Bigby's Hand"
    CLOUDKILL = "Cloudkill"
    CONE_OF_COLD = "Cone of Cold"
    CREATION = "Creation"
    DOMINATE_PERSON = "Dominate Person"
    HOLD_MONSTER = "Hold Monster"
    INSECT_PLAGUE = "Insect Plague"
    SEEMING = "Seeming"
    SONGALS_ELEMENTAL_SUFFUSION = "Songal's Elemental Suffusion"
    SYNAPTIC_STATIC = "Synaptic Static"
    TELEKINESIS = "Telekinesis"
    TELEPORTATION_CIRCLE = "Teleportation Circle"
    WALL_OF_STONE = "Wall of Stone"


class SorcererLevel6Spells(str, Enum):
    ARCANE_GATE = "Arcane Gate"
    CHAIN_LIGHTNING = "Chain Lightning"
    CIRCLE_OF_DEATH = "Circle of Death"
    DISINTEGRATE = "Disintegrate"
    ELMINSTERS_EFFULGENT_SPHERES = "Elminster's Effulgent Spheres"
    EYEBITE = "Eyebite"
    FLESH_TO_STONE = "Flesh to Stone"
    GLOBE_OF_INVULNERABILITY = "Globe of Invulnerability"
    MASS_SUGGESTION = "Mass Suggestion"
    MOVE_EARTH = "Move Earth"
    OTILUKES_FREEZING_SPHERE = "Otiluke's Freezing Sphere"
    SUNBEAM = "Sunbeam"
    TRUE_SEEING = "True Seeing"


class SorcererLevel7Spells(str, Enum):
    DELAYED_BLAST_FIREBALL = "Delayed Blast Fireball"
    ETHEREALNESS = "Etherealness"
    FINGER_OF_DEATH = "Finger of Death"
    FIRE_STORM = "Fire Storm"
    PLANE_SHIFT = "Plane Shift"
    PRISMATIC_SPRAY = "Prismatic Spray"
    REVERSE_GRAVITY = "Reverse Gravity"
    SIMBULS_SYNOSTODWEOMER = "Simbul's Synostodweomer"
    TELEPORT = "Teleport"


class SorcererLevel8Spells(str, Enum):
    DEMIPLANE = "Demiplane"
    DOMINATE_MONSTER = "Dominate Monster"
    EARTHQUAKE = "Earthquake"
    INCENDIARY_CLOUD = "Incendiary Cloud"
    POWER_WORD_STUN = "Power Word Stun"
    SUNBURST = "Sunburst"


class SorcererLevel9Spells(str, Enum):
    BLADE_OF_DISASTER = "Blade of Disaster"
    GATE = "Gate"
    METEOR_SWARM = "Meteor Swarm"
    POWER_WORD_KILL = "Power Word Kill"
    TIME_STOP = "Time Stop"
    WISH = "Wish"


class WizardLevel0Spells(str, Enum):
    ACID_SPLASH = "Acid Splash"
    BLADE_WARD = "Blade Ward"
    CHILL_TOUCH = "Chill Touch"
    DANCING_LIGHTS = "Dancing Lights"
    ELEMENTALISM = "Elementalism"
    FIRE_BOLT = "Fire Bolt"
    FRIENDS = "Friends"
    LIGHT = "Light"
    MAGE_HAND = "Mage Hand"
    MENDING = "Mending"
    MESSAGE = "Message"
    MIND_SLIVER = "Mind Sliver"
    MINOR_ILLUSION = "Minor Illusion"
    POISON_SPRAY = "Poison Spray"
    PRESTIDIGITATION = "Prestidigitation"
    RAY_OF_FROST = "Ray of Frost"
    SHOCKING_GRASP = "Shocking Grasp"
    THUNDERCLAP = "Thunderclap"
    TOLL_THE_DEAD = "Toll the Dead"
    TRUE_STRIKE = "True Strike"


class WizardLevel1Spells(str, Enum):
    ALARM = "Alarm"
    BURNING_HANDS = "Burning Hands"
    CHARM_PERSON = "Charm Person"
    CHROMATIC_ORB = "Chromatic Orb"
    COLOR_SPRAY = "Color Spray"
    COMPREHEND_LANGUAGES = "Comprehend Languages"
    DETECT_MAGIC = "Detect Magic"
    DISGUISE_SELF = "Disguise Self"
    EXPEDITIOUS_RETREAT = "Expeditious Retreat"
    FALSE_LIFE = "False Life"
    FEATHER_FALL = "Feather Fall"
    FIND_FAMILIAR = "Find Familiar"
    FOG_CLOUD = "Fog Cloud"
    GREASE = "Grease"
    ICE_KNIFE = "Ice Knife"
    IDENTIFY = "Identify"
    ILLUSORY_SCRIPT = "Illusory Script"
    JUMP = "Jump"
    LONGSTRIDER = "Longstrider"
    MAGE_ARMOR = "Mage Armor"
    MAGIC_MISSILE = "Magic Missile"
    PROTECTION_FROM_EVIL_AND_GOOD = "Protection from Evil and Good"
    RAY_OF_SICKNESS = "Ray of Sickness"
    SHIELD = "Shield"
    SILENT_IMAGE = "Silent Image"
    SLEEP = "Sleep"
    SPELLFIRE_FLARE = "Spellfire Flare"
    TASHAS_HIDEOUS_LAUGHTER = "Tasha's Hideous Laughter"
    TENSERS_FLOATING_DISK = "Tenser's Floating Disk"
    THUNDERWAVE = "Thunderwave"
    UNSEEN_SERVANT = "Unseen Servant"
    WARDAWAY = "Wardaway"
    WITCH_BOLT = "Witch Bolt"


class WizardLevel2Spells(str, Enum):
    ALTER_SELF = "Alter Self"
    ARCANE_LOCK = "Arcane Lock"
    ARCANE_VIGOR = "Arcane Vigor"
    AUGURY = "Augury"
    BLINDNESS_DEAFNESS = "Blindness/Deafness"
    BLUR = "Blur"
    CLOUD_OF_DAGGERS = "Cloud of Daggers"
    CONTINUAL_FLAME = "Continual Flame"
    CROWN_OF_MADNESS = "Crown of Madness"
    DARKNESS = "Darkness"
    DARKVISION = "Darkvision"
    DEATH_ARMOR = "Death Armor"
    DERYANS_HELPFUL_HOMUNCULI = "Deryan's Helpful Homunculi"
    DETECT_THOUGHTS = "Detect Thoughts"
    DRAGONS_BREATH = "Dragon's Breath"
    ELMINSTERS_ELUSION = "Elminster's Elusion"
    ENHANCE_ABILITY = "Enhance Ability"
    ENLARGE_REDUCE = "Enlarge/Reduce"
    FLAMING_SPHERE = "Flaming Sphere"
    GENTLE_REPOSE = "Gentle Repose"
    GUST_OF_WIND = "Gust of Wind"
    HOLD_PERSON = "Hold Person"
    INVISIBILITY = "Invisibility"
    KNOCK = "Knock"
    LEVITATE = "Levitate"
    LOCATE_OBJECT = "Locate Object"
    MAGIC_MOUTH = "Magic Mouth"
    MAGIC_WEAPON = "Magic Weapon"
    MELFS_ACID_ARROW = "Melf's Acid Arrow"
    MIND_SPIKE = "Mind Spike"
    MIRROR_IMAGE = "Mirror Image"
    MISTY_STEP = "Misty Step"
    NYSTULS_MAGIC_AURA = "Nystul's Magic Aura"
    PHANTASMAL_FORCE = "Phantasmal Force"
    RAY_OF_ENFEEBLEMENT = "Ray of Enfeeblement"
    ROPE_TRICK = "Rope Trick"
    SCORCHING_RAY = "Scorching Ray"
    SEE_INVISIBILITY = "See Invisibility"
    SHATTER = "Shatter"
    SPIDER_CLIMB = "Spider Climb"
    SUGGESTION = "Suggestion"
    WEB = "Web"


class WizardLevel3Spells(str, Enum):
    ANIMATE_DEAD = "Animate Dead"
    BESTOW_CURSE = "Bestow Curse"
    BLINK = "Blink"
    CACOPHONIC_SHIELD = "Cacophonic Shield"
    CLAIRVOYANCE = "Clairvoyance"
    CONJURE_CONSTRUCTS = "Conjure Constructs"
    COUNTERSPELL = "Counterspell"
    DISPEL_MAGIC = "Dispel Magic"
    FEAR = "Fear"
    FEIGN_DEATH = "Feign Death"
    FIREBALL = "Fireball"
    FLY = "Fly"
    GASEOUS_FORM = "Gaseous Form"
    GLYPH_OF_WARDING = "Glyph of Warding"
    HASTE = "Haste"
    HYPNOTIC_PATTERN = "Hypnotic Pattern"
    LAERALS_SILVER_LANCE = "Laeral's Silver Lance"
    LEOMUNDS_TINY_HUT = "Leomund's Tiny Hut"
    LIGHTNING_BOLT = "Lightning Bolt"
    MAGIC_CIRCLE = "Magic Circle"
    MAJOR_IMAGE = "Major Image"
    NONDETECTION = "Nondetection"
    PHANTOM_STEED = "Phantom Steed"
    PROTECTION_FROM_ENERGY = "Protection from Energy"
    REMOVE_CURSE = "Remove Curse"
    SENDING = "Sending"
    SLEET_STORM = "Sleet Storm"
    SLOW = "Slow"
    SPEAK_WITH_DEAD = "Speak with Dead"
    STINKING_CLOUD = "Stinking Cloud"
    SUMMON_FEY = "Summon Fey"
    SUMMON_UNDEAD = "Summon Undead"
    SYLUNÉS_VIPER = "Syluné's Viper"
    TONGUES = "Tongues"
    VAMPIRIC_TOUCH = "Vampiric Touch"
    WATER_BREATHING = "Water Breathing"


class WizardLevel4Spells(str, Enum):
    ARCANE_EYE = "Arcane Eye"
    BACKLASH = "Backlash"
    BANISHMENT = "Banishment"
    BLIGHT = "Blight"
    CHARM_MONSTER = "Charm Monster"
    CONFUSION = "Confusion"
    CONJURE_MINOR_ELEMENTALS = "Conjure Minor Elementals"
    CONTROL_WATER = "Control Water"
    DIMENSION_DOOR = "Dimension Door"
    DIVINATION = "Divination"
    EVARDS_BLACK_TENTACLES = "Evard's Black Tentacles"
    FABRICATE = "Fabricate"
    FIRE_SHIELD = "Fire Shield"
    GREATER_INVISIBILITY = "Greater Invisibility"
    HALLUCINATORY_TERRAIN = "Hallucinatory Terrain"
    ICE_STORM = "Ice Storm"
    LEOMUNDS_SECRET_CHEST = "Leomund's Secret Chest"
    LOCATE_CREATURE = "Locate Creature"
    MORDENKAINENS_FAITHFUL_HOUND = "Mordenkainen's Faithful Hound"
    MORDENKAINENS_PRIVATE_SANCTUM = "Mordenkainen's Private Sanctum"
    OTILUKES_RESILIENT_SPHERE = "Otiluke's Resilient Sphere"
    PHANTASMAL_KILLER = "Phantasmal Killer"
    POLYMORPH = "Polymorph"
    SPELLFIRE_STORM = "Spellfire Storm"
    STONE_SHAPE = "Stone Shape"
    STONESKIN = "Stoneskin"
    SUMMON_ABERRATION = "Summon Aberration"
    SUMMON_CONSTRUCT = "Summon Construct"
    SUMMON_ELEMENTAL = "Summon Elemental"
    VITRIOLIC_SPHERE = "Vitriolic Sphere"
    WALL_OF_FIRE = "Wall of Fire"


class WizardLevel5Spells(str, Enum):
    ALUSTRIELS_MOONCLOAK = "Alustriel's Mooncloak"
    ANIMATE_OBJECTS = "Animate Objects"
    BIGBYS_HAND = "Bigby's Hand"
    CIRCLE_OF_POWER = "Circle of Power"
    CLOUDKILL = "Cloudkill"
    CONE_OF_COLD = "Cone of Cold"
    CONJURE_ELEMENTAL = "Conjure Elemental"
    CONTACT_OTHER_PLANE = "Contact Other Plane"
    CREATION = "Creation"
    DOMINATE_PERSON = "Dominate Person"
    DREAM = "Dream"
    GEAS = "Geas"
    HOLD_MONSTER = "Hold Monster"
    JALLARZIS_STORM_OF_RADIANCE = "Jallarzi's Storm of Radiance"
    LEGEND_LORE = "Legend Lore"
    MISLEAD = "Mislead"
    MODIFY_MEMORY = "Modify Memory"
    PASSWALL = "Passwall"
    PLANAR_BINDING = "Planar Binding"
    RARYS_TELEPATHIC_BOND = "Rary's Telepathic Bond"
    SCRYING = "Scrying"
    SEEMING = "Seeming"
    SONGALS_ELEMENTAL_SUFFUSION = "Songal's Elemental Suffusion"
    STEEL_WIND_STRIKE = "Steel Wind Strike"
    SUMMON_DRAGON = "Summon Dragon"
    SYNAPTIC_STATIC = "Synaptic Static"
    TELEKINESIS = "Telekinesis"
    TELEPORTATION_CIRCLE = "Teleportation Circle"
    WALL_OF_FORCE = "Wall of Force"
    WALL_OF_STONE = "Wall of Stone"
    YOLANDES_REGAL_PRESENCE = "Yolande's Regal Presence"


class WizardLevel6Spells(str, Enum):
    ARCANE_GATE = "Arcane Gate"
    CHAIN_LIGHTNING = "Chain Lightning"
    CIRCLE_OF_DEATH = "Circle of Death"
    CONTINGENCY = "Contingency"
    CREATE_UNDEAD = "Create Undead"
    DISINTEGRATE = "Disintegrate"
    DRAWMIJS_INSTANT_SUMMONS = "Drawmij's Instant Summons"
    ELMINSTERS_EFFULGENT_SPHERES = "Elminster's Effulgent Spheres"
    EYEBITE = "Eyebite"
    FLESH_TO_STONE = "Flesh to Stone"
    GLOBE_OF_INVULNERABILITY = "Globe of Invulnerability"
    GUARDS_AND_WARDS = "Guards and Wards"
    MAGIC_JAR = "Magic Jar"
    MASS_SUGGESTION = "Mass Suggestion"
    MOVE_EARTH = "Move Earth"
    OTILUKES_FREEZING_SPHERE = "Otiluke's Freezing Sphere"
    OTTOS_IRRESISTIBLE_DANCE = "Otto's Irresistible Dance"
    PROGRAMMED_ILLUSION = "Programmed Illusion"
    SUMMON_FIEND = "Summon Fiend"
    SUNBEAM = "Sunbeam"
    TASHAS_BUBBLING_CAULDRON = "Tasha's Bubbling Cauldron"
    TRUE_SEEING = "True Seeing"
    WALL_OF_ICE = "Wall of Ice"


class WizardLevel7Spells(str, Enum):
    DELAYED_BLAST_FIREBALL = "Delayed Blast Fireball"
    ETHEREALNESS = "Etherealness"
    FINGER_OF_DEATH = "Finger of Death"
    FORCECAGE = "Forcecage"
    MIRAGE_ARCANE = "Mirage Arcane"
    MORDENKAINENS_MAGNIFICENT_MANSION = "Mordenkainen's Magnificent Mansion"
    MORDENKAINENS_SWORD = "Mordenkainen's Sword"
    PLANE_SHIFT = "Plane Shift"
    PRISMATIC_SPRAY = "Prismatic Spray"
    PROJECT_IMAGE = "Project Image"
    REVERSE_GRAVITY = "Reverse Gravity"
    SEQUESTER = "Sequester"
    SIMBULS_SYNOSTODWEOMER = "Simbul's Synostodweomer"
    SIMULACRUM = "Simulacrum"
    SYMBOL = "Symbol"
    TELEPORT = "Teleport"


class WizardLevel8Spells(str, Enum):
    ANTIMAGIC_FIELD = "Antimagic Field"
    ANTIPATHY_SYMPATHY = "Antipathy/Sympathy"
    BEFUDDLEMENT = "Befuddlement"
    CLONE = "Clone"
    CONTROL_WEATHER = "Control Weather"
    DEMIPLANE = "Demiplane"
    DOMINATE_MONSTER = "Dominate Monster"
    HOLY_STAR_OF_MYSTRA = "Holy Star of Mystra"
    INCENDIARY_CLOUD = "Incendiary Cloud"
    MAZE = "Maze"
    MIND_BLANK = "Mind Blank"
    POWER_WORD_STUN = "Power Word Stun"
    SUNBURST = "Sunburst"
    TELEPATHY = "Telepathy"


class WizardLevel9Spells(str, Enum):
    ASTRAL_PROJECTION = "Astral Projection"
    BLADE_OF_DISASTER = "Blade of Disaster"
    FORESIGHT = "Foresight"
    GATE = "Gate"
    IMPRISONMENT = "Imprisonment"
    METEOR_SWARM = "Meteor Swarm"
    POWER_WORD_KILL = "Power Word Kill"
    PRISMATIC_WALL = "Prismatic Wall"
    SHAPECHANGE = "Shapechange"
    TIME_STOP = "Time Stop"
    TRUE_POLYMORPH = "True Polymorph"
    WEIRD = "Weird"
    WISH = "Wish"


class BardLevel0Spells(str, Enum):
    BLADE_WARD = "Blade Ward"
    DANCING_LIGHTS = "Dancing Lights"
    FRIENDS = "Friends"
    LIGHT = "Light"
    MAGE_HAND = "Mage Hand"
    MENDING = "Mending"
    MESSAGE = "Message"
    MINOR_ILLUSION = "Minor Illusion"
    PRESTIDIGITATION = "Prestidigitation"
    STARRY_WISP = "Starry Wisp"
    THUNDERCLAP = "Thunderclap"
    TRUE_STRIKE = "True Strike"
    VICIOUS_MOCKERY = "Vicious Mockery"


class BardLevel1Spells(str, Enum):
    ANIMAL_FRIENDSHIP = "Animal Friendship"
    BANE = "Bane"
    CHARM_PERSON = "Charm Person"
    COLOR_SPRAY = "Color Spray"
    COMMAND = "Command"
    COMPREHEND_LANGUAGES = "Comprehend Languages"
    CURE_WOUNDS = "Cure Wounds"
    DETECT_MAGIC = "Detect Magic"
    DISGUISE_SELF = "Disguise Self"
    DISSONANT_WHISPERS = "Dissonant Whispers"
    FAERIE_FIRE = "Faerie Fire"
    FEATHER_FALL = "Feather Fall"
    HEALING_WORD = "Healing Word"
    HEROISM = "Heroism"
    IDENTIFY = "Identify"
    ILLUSORY_SCRIPT = "Illusory Script"
    LONGSTRIDER = "Longstrider"
    SILENT_IMAGE = "Silent Image"
    SLEEP = "Sleep"
    SPEAK_WITH_ANIMALS = "Speak with Animals"
    TASHAS_HIDEOUS_LAUGHTER = "Tasha's Hideous Laughter"
    THUNDERWAVE = "Thunderwave"
    UNSEEN_SERVANT = "Unseen Servant"
    WARDAWAY = "Wardaway"


class BardLevel2Spells(str, Enum):
    AID = "Aid"
    ANIMAL_MESSENGER = "Animal Messenger"
    BLINDNESS_DEAFNESS = "Blindness/Deafness"
    CALM_EMOTIONS = "Calm Emotions"
    CLOUD_OF_DAGGERS = "Cloud of Daggers"
    CROWN_OF_MADNESS = "Crown of Madness"
    DETECT_THOUGHTS = "Detect Thoughts"
    ENHANCE_ABILITY = "Enhance Ability"
    ENLARGE_REDUCE = "Enlarge/Reduce"
    ENTHRALL = "Enthrall"
    HEAT_METAL = "Heat Metal"
    HOLD_PERSON = "Hold Person"
    INVISIBILITY = "Invisibility"
    KNOCK = "Knock"
    LESSER_RESTORATION = "Lesser Restoration"
    LOCATE_ANIMALS_OR_PLANTS = "Locate Animals or Plants"
    LOCATE_OBJECT = "Locate Object"
    MAGIC_MOUTH = "Magic Mouth"
    MIRROR_IMAGE = "Mirror Image"
    PHANTASMAL_FORCE = "Phantasmal Force"
    SEE_INVISIBILITY = "See Invisibility"
    SHATTER = "Shatter"
    SILENCE = "Silence"
    SUGGESTION = "Suggestion"
    ZONE_OF_TRUTH = "Zone of Truth"


class BardLevel3Spells(str, Enum):
    BESTOW_CURSE = "Bestow Curse"
    CACOPHONIC_SHIELD = "Cacophonic Shield"
    CLAIRVOYANCE = "Clairvoyance"
    DISPEL_MAGIC = "Dispel Magic"
    FEAR = "Fear"
    FEIGN_DEATH = "Feign Death"
    GLYPH_OF_WARDING = "Glyph of Warding"
    HYPNOTIC_PATTERN = "Hypnotic Pattern"
    LEOMUNDS_TINY_HUT = "Leomund's Tiny Hut"
    MAJOR_IMAGE = "Major Image"
    MASS_HEALING_WORD = "Mass Healing Word"
    NONDETECTION = "Nondetection"
    PLANT_GROWTH = "Plant Growth"
    SENDING = "Sending"
    SLOW = "Slow"
    SPEAK_WITH_DEAD = "Speak with Dead"
    SPEAK_WITH_PLANTS = "Speak with Plants"
    STINKING_CLOUD = "Stinking Cloud"
    TONGUES = "Tongues"


class BardLevel4Spells(str, Enum):
    BACKLASH = "Backlash"
    CHARM_MONSTER = "Charm Monster"
    COMPULSION = "Compulsion"
    CONFUSION = "Confusion"
    DIMENSION_DOOR = "Dimension Door"
    DOOMTIDE = "Doomtide"
    FOUNT_OF_MOONLIGHT = "Fount of Moonlight"
    FREEDOM_OF_MOVEMENT = "Freedom of Movement"
    GREATER_INVISIBILITY = "Greater Invisibility"
    HALLUCINATORY_TERRAIN = "Hallucinatory Terrain"
    LOCATE_CREATURE = "Locate Creature"
    PHANTASMAL_KILLER = "Phantasmal Killer"
    POLYMORPH = "Polymorph"


class BardLevel5Spells(str, Enum):
    ALUSTRIELS_MOONCLOAK = "Alustriel's Mooncloak"
    ANIMATE_OBJECTS = "Animate Objects"
    AWAKEN = "Awaken"
    DOMINATE_PERSON = "Dominate Person"
    DREAM = "Dream"
    GEAS = "Geas"
    GREATER_RESTORATION = "Greater Restoration"
    HOLD_MONSTER = "Hold Monster"
    LEGEND_LORE = "Legend Lore"
    MASS_CURE_WOUNDS = "Mass Cure Wounds"
    MISLEAD = "Mislead"
    MODIFY_MEMORY = "Modify Memory"
    PLANAR_BINDING = "Planar Binding"
    RAISE_DEAD = "Raise Dead"
    RARYS_TELEPATHIC_BOND = "Rary's Telepathic Bond"
    SCRYING = "Scrying"
    SEEMING = "Seeming"
    SYNAPTIC_STATIC = "Synaptic Static"
    TELEPORTATION_CIRCLE = "Teleportation Circle"
    YOLANDES_REGAL_PRESENCE = "Yolande's Regal Presence"


class BardLevel6Spells(str, Enum):
    DIRGE = "Dirge"
    EYEBITE = "Eyebite"
    FIND_THE_PATH = "Find the Path"
    GUARDS_AND_WARDS = "Guards and Wards"
    HEROES__FEAST = "Heroes' Feast"
    MASS_SUGGESTION = "Mass Suggestion"
    OTTOS_IRRESISTIBLE_DANCE = "Otto's Irresistible Dance"
    PROGRAMMED_ILLUSION = "Programmed Illusion"
    TRUE_SEEING = "True Seeing"


class BardLevel7Spells(str, Enum):
    ETHEREALNESS = "Etherealness"
    FORCECAGE = "Forcecage"
    MIRAGE_ARCANE = "Mirage Arcane"
    MORDENKAINENS_MAGNIFICENT_MANSION = "Mordenkainen's Magnificent Mansion"
    MORDENKAINENS_SWORD = "Mordenkainen's Sword"
    POWER_WORD_FORTIFY = "Power Word Fortify"
    PRISMATIC_SPRAY = "Prismatic Spray"
    PROJECT_IMAGE = "Project Image"
    REGENERATE = "Regenerate"
    RESURRECTION = "Resurrection"
    SYMBOL = "Symbol"
    TELEPORT = "Teleport"


class BardLevel8Spells(str, Enum):
    ANTIPATHY_SYMPATHY = "Antipathy/Sympathy"
    BEFUDDLEMENT = "Befuddlement"
    DOMINATE_MONSTER = "Dominate Monster"
    GLIBNESS = "Glibness"
    MIND_BLANK = "Mind Blank"
    POWER_WORD_STUN = "Power Word Stun"


class BardLevel9Spells(str, Enum):
    FORESIGHT = "Foresight"
    POWER_WORD_HEAL = "Power Word Heal"
    POWER_WORD_KILL = "Power Word Kill"
    PRISMATIC_WALL = "Prismatic Wall"
    TRUE_POLYMORPH = "True Polymorph"


class ClericLevel0Spells(str, Enum):
    GUIDANCE = "Guidance"
    LIGHT = "Light"
    MENDING = "Mending"
    RESISTANCE = "Resistance"
    SACRED_FLAME = "Sacred Flame"
    SPARE_THE_DYING = "Spare the Dying"
    THAUMATURGY = "Thaumaturgy"
    TOLL_THE_DEAD = "Toll the Dead"
    WORD_OF_RADIANCE = "Word of Radiance"


class ClericLevel1Spells(str, Enum):
    BANE = "Bane"
    BLESS = "Bless"
    COMMAND = "Command"
    CREATE_OR_DESTROY_WATER = "Create or Destroy Water"
    CURE_WOUNDS = "Cure Wounds"
    DETECT_EVIL_AND_GOOD = "Detect Evil and Good"
    DETECT_MAGIC = "Detect Magic"
    DETECT_POISON_AND_DISEASE = "Detect Poison and Disease"
    GUIDING_BOLT = "Guiding Bolt"
    HEALING_WORD = "Healing Word"
    INFLICT_WOUNDS = "Inflict Wounds"
    PROTECTION_FROM_EVIL_AND_GOOD = "Protection from Evil and Good"
    PURIFY_FOOD_AND_DRINK = "Purify Food and Drink"
    SANCTUARY = "Sanctuary"
    SHIELD_OF_FAITH = "Shield of Faith"
    WARDAWAY = "Wardaway"


class ClericLevel2Spells(str, Enum):
    AID = "Aid"
    AUGURY = "Augury"
    BLINDNESS_DEAFNESS = "Blindness/Deafness"
    CALM_EMOTIONS = "Calm Emotions"
    CONTINUAL_FLAME = "Continual Flame"
    DERYANS_HELPFUL_HOMUNCULI = "Deryan's Helpful Homunculi"
    ENHANCE_ABILITY = "Enhance Ability"
    FIND_TRAPS = "Find Traps"
    GENTLE_REPOSE = "Gentle Repose"
    HOLD_PERSON = "Hold Person"
    LESSER_RESTORATION = "Lesser Restoration"
    LOCATE_OBJECT = "Locate Object"
    PRAYER_OF_HEALING = "Prayer of Healing"
    PROTECTION_FROM_POISON = "Protection from Poison"
    SILENCE = "Silence"
    SPIRITUAL_WEAPON = "Spiritual Weapon"
    WARDING_BOND = "Warding Bond"
    ZONE_OF_TRUTH = "Zone of Truth"


class ClericLevel3Spells(str, Enum):
    ANIMATE_DEAD = "Animate Dead"
    AURA_OF_VITALITY = "Aura of Vitality"
    BEACON_OF_HOPE = "Beacon of Hope"
    BESTOW_CURSE = "Bestow Curse"
    CLAIRVOYANCE = "Clairvoyance"
    CREATE_FOOD_AND_WATER = "Create Food and Water"
    DAYLIGHT = "Daylight"
    DISPEL_MAGIC = "Dispel Magic"
    FEIGN_DEATH = "Feign Death"
    GLYPH_OF_WARDING = "Glyph of Warding"
    LAERALS_SILVER_LANCE = "Laeral's Silver Lance"
    MAGIC_CIRCLE = "Magic Circle"
    MASS_HEALING_WORD = "Mass Healing Word"
    MELD_INTO_STONE = "Meld into Stone"
    PROTECTION_FROM_ENERGY = "Protection from Energy"
    REMOVE_CURSE = "Remove Curse"
    REVIVIFY = "Revivify"
    SENDING = "Sending"
    SPEAK_WITH_DEAD = "Speak with Dead"
    SPIRIT_GUARDIANS = "Spirit Guardians"
    TONGUES = "Tongues"
    WATER_WALK = "Water Walk"


class ClericLevel4Spells(str, Enum):
    AURA_OF_LIFE = "Aura of Life"
    AURA_OF_PURITY = "Aura of Purity"
    BANISHMENT = "Banishment"
    CONTROL_WATER = "Control Water"
    DEATH_WARD = "Death Ward"
    DIVINATION = "Divination"
    DOOMTIDE = "Doomtide"
    FREEDOM_OF_MOVEMENT = "Freedom of Movement"
    GUARDIAN_OF_FAITH = "Guardian of Faith"
    LOCATE_CREATURE = "Locate Creature"
    STONE_SHAPE = "Stone Shape"


class ClericLevel5Spells(str, Enum):
    CIRCLE_OF_POWER = "Circle Of Power"
    COMMUNE = "Commune"
    CONTAGION = "Contagion"
    DISPEL_EVIL_AND_GOOD = "Dispel Evil and Good"
    FLAME_STRIKE = "Flame Strike"
    GEAS = "Geas"
    GREATER_RESTORATION = "Greater Restoration"
    HALLOW = "Hallow"
    INSECT_PLAGUE = "Insect Plague"
    LEGEND_LORE = "Legend Lore"
    MASS_CURE_WOUNDS = "Mass Cure Wounds"
    PLANAR_BINDING = "Planar Binding"
    RAISE_DEAD = "Raise Dead"
    SCRYING = "Scrying"
    SUMMON_CELESTIAL = "Summon Celestial"


class ClericLevel6Spells(str, Enum):
    BLADE_BARRIER = "Blade Barrier"
    CREATE_UNDEAD = "Create Undead"
    DIRGE = "Dirge"
    FIND_THE_PATH = "Find the Path"
    FORBIDDANCE = "Forbiddance"
    HARM = "Harm"
    HEAL = "Heal"
    HEROES__FEAST = "Heroes' Feast"
    PLANAR_ALLY = "Planar Ally"
    SUNBEAM = "Sunbeam"
    TRUE_SEEING = "True Seeing"
    WORD_OF_RECALL = "Word of Recall"


class ClericLevel7Spells(str, Enum):
    CONJURE_CELESTIAL = "Conjure Celestial"
    DIVINE_WORD = "Divine Word"
    ETHEREALNESS = "Etherealness"
    FIRE_STORM = "Fire Storm"
    PLANE_SHIFT = "Plane Shift"
    POWER_WORD_FORTIFY = "Power Word Fortify"
    REGENERATE = "Regenerate"
    RESURRECTION = "Resurrection"
    SYMBOL = "Symbol"


class ClericLevel8Spells(str, Enum):
    ANTIMAGIC_FIELD = "Antimagic Field"
    CONTROL_WEATHER = "Control Weather"
    EARTHQUAKE = "Earthquake"
    HOLY_AURA = "Holy Aura"
    HOLY_STAR_OF_MYSTRA = "Holy Star of Mystra"
    SUNBURST = "Sunburst"


class ClericLevel9Spells(str, Enum):
    ASTRAL_PROJECTION = "Astral Projection"
    GATE = "Gate"
    MASS_HEAL = "Mass Heal"
    POWER_WORD_HEAL = "Power Word Heal"
    TRUE_RESURRECTION = "True Resurrection"


class DruidLevel0Spells(str, Enum):
    DRUIDCRAFT = "Druidcraft"
    ELEMENTALISM = "Elementalism"
    GUIDANCE = "Guidance"
    MENDING = "Mending"
    MESSAGE = "Message"
    POISON_SPRAY = "Poison Spray"
    PRODUCE_FLAME = "Produce Flame"
    RESISTANCE = "Resistance"
    SHILLELAGH = "Shillelagh"
    SPARE_THE_DYING = "Spare the Dying"
    STARRY_WISP = "Starry Wisp"
    THORN_WHIP = "Thorn Whip"
    THUNDERCLAP = "Thunderclap"


class DruidLevel1Spells(str, Enum):
    ANIMAL_FRIENDSHIP = "Animal Friendship"
    CHARM_PERSON = "Charm Person"
    CREATE_OR_DESTROY_WATER = "Create or Destroy Water"
    CURE_WOUNDS = "Cure Wounds"
    DETECT_MAGIC = "Detect Magic"
    DETECT_POISON_AND_DISEASE = "Detect Poison and Disease"
    ENTANGLE = "Entangle"
    FAERIE_FIRE = "Faerie Fire"
    FOG_CLOUD = "Fog Cloud"
    GOODBERRY = "Goodberry"
    HEALING_WORD = "Healing Word"
    ICE_KNIFE = "Ice Knife"
    JUMP = "Jump"
    LONGSTRIDER = "Longstrider"
    PROTECTION_FROM_EVIL_AND_GOOD = "Protection from Evil and Good"
    PURIFY_FOOD_AND_DRINK = "Purify Food and Drink"
    SPEAK_WITH_ANIMALS = "Speak with Animals"
    THUNDERWAVE = "Thunderwave"


class DruidLevel2Spells(str, Enum):
    AID = "Aid"
    ANIMAL_MESSENGER = "Animal Messenger"
    AUGURY = "Augury"
    BARKSKIN = "Barkskin"
    BEAST_SENSE = "Beast Sense"
    CONTINUAL_FLAME = "Continual Flame"
    DARKVISION = "Darkvision"
    ENHANCE_ABILITY = "Enhance Ability"
    ENLARGE_REDUCE = "Enlarge/Reduce"
    FIND_TRAPS = "Find Traps"
    FLAME_BLADE = "Flame Blade"
    FLAMING_SPHERE = "Flaming Sphere"
    GUST_OF_WIND = "Gust of Wind"
    HEAT_METAL = "Heat Metal"
    HOLD_PERSON = "Hold Person"
    LESSER_RESTORATION = "Lesser Restoration"
    LOCATE_ANIMALS_OR_PLANTS = "Locate Animals or Plants"
    LOCATE_OBJECT = "Locate Object"
    MOONBEAM = "Moonbeam"
    PASS_WITHOUT_TRACE = "Pass without Trace"
    PROTECTION_FROM_POISON = "Protection from Poison"
    SPIKE_GROWTH = "Spike Growth"
    SUMMON_BEAST = "Summon Beast"


class DruidLevel3Spells(str, Enum):
    AURA_OF_VITALITY = "Aura of Vitality"
    CALL_LIGHTNING = "Call Lightning"
    CONJURE_ANIMALS = "Conjure Animals"
    DAYLIGHT = "Daylight"
    DISPEL_MAGIC = "Dispel Magic"
    ELEMENTAL_WEAPON = "Elemental Weapon"
    FEIGN_DEATH = "Feign Death"
    MELD_INTO_STONE = "Meld into Stone"
    PLANT_GROWTH = "Plant Growth"
    PROTECTION_FROM_ENERGY = "Protection from Energy"
    REVIVIFY = "Revivify"
    SLEET_STORM = "Sleet Storm"
    SPEAK_WITH_PLANTS = "Speak with Plants"
    SUMMON_FEY = "Summon Fey"
    SYLUNÉS_VIPER = "Syluné's Viper"
    WATER_BREATHING = "Water Breathing"
    WATER_WALK = "Water Walk"
    WIND_WALL = "Wind Wall"


class DruidLevel4Spells(str, Enum):
    BLIGHT = "Blight"
    CHARM_MONSTER = "Charm Monster"
    CONFUSION = "Confusion"
    CONJURE_MINOR_ELEMENTALS = "Conjure Minor Elementals"
    CONJURE_WOODLAND_BEINGS = "Conjure Woodland Beings"
    CONTROL_WATER = "Control Water"
    DIVINATION = "Divination"
    DOMINATE_BEAST = "Dominate Beast"
    FIRE_SHIELD = "Fire Shield"
    FOUNT_OF_MOONLIGHT = "Fount of Moonlight"
    FREEDOM_OF_MOVEMENT = "Freedom of Movement"
    GIANT_INSECT = "Giant Insect"
    GRASPING_VINE = "Grasping Vine"
    HALLUCINATORY_TERRAIN = "Hallucinatory Terrain"
    ICE_STORM = "Ice Storm"
    LOCATE_CREATURE = "Locate Creature"
    POLYMORPH = "Polymorph"
    STONE_SHAPE = "Stone Shape"
    STONESKIN = "Stoneskin"
    SUMMON_ELEMENTAL = "Summon Elemental"
    WALL_OF_FIRE = "Wall of Fire"


class DruidLevel5Spells(str, Enum):
    ALUSTRIELS_MOONCLOAK = "Alustriel's Mooncloak"
    ANTILIFE_SHELL = "Antilife Shell"
    AWAKEN = "Awaken"
    COMMUNE_WITH_NATURE = "Commune with Nature"
    CONE_OF_COLD = "Cone of Cold"
    CONJURE_ELEMENTAL = "Conjure Elemental"
    CONTAGION = "Contagion"
    GEAS = "Geas"
    GREATER_RESTORATION = "Greater Restoration"
    INSECT_PLAGUE = "Insect Plague"
    MASS_CURE_WOUNDS = "Mass Cure Wounds"
    PLANAR_BINDING = "Planar Binding"
    REINCARNATE = "Reincarnate"
    SCRYING = "Scrying"
    SONGALS_ELEMENTAL_SUFFUSION = "Songal's Elemental Suffusion"
    TREE_STRIDE = "Tree Stride"
    WALL_OF_STONE = "Wall of Stone"


class DruidLevel6Spells(str, Enum):
    CONJURE_FEY = "Conjure Fey"
    ELMINSTERS_EFFULGENT_SPHERES = "Elminster's Effulgent Spheres"
    FIND_THE_PATH = "Find the Path"
    FLESH_TO_STONE = "Flesh to Stone"
    HEAL = "Heal"
    HEROES__FEAST = "Heroes' Feast"
    MOVE_EARTH = "Move Earth"
    SUNBEAM = "Sunbeam"
    TRANSPORT_VIA_PLANTS = "Transport via Plants"
    WALL_OF_THORNS = "Wall of Thorns"
    WIND_WALK = "Wind Walk"


class DruidLevel7Spells(str, Enum):
    FIRE_STORM = "Fire Storm"
    MIRAGE_ARCANE = "Mirage Arcane"
    PLANE_SHIFT = "Plane Shift"
    REGENERATE = "Regenerate"
    REVERSE_GRAVITY = "Reverse Gravity"
    SYMBOL = "Symbol"


class DruidLevel8Spells(str, Enum):
    ANIMAL_SHAPES = "Animal Shapes"
    ANTIPATHY_SYMPATHY = "Antipathy/Sympathy"
    BEFUDDLEMENT = "Befuddlement"
    CONTROL_WEATHER = "Control Weather"
    EARTHQUAKE = "Earthquake"
    INCENDIARY_CLOUD = "Incendiary Cloud"
    SUNBURST = "Sunburst"
    TSUNAMI = "Tsunami"


class DruidLevel9Spells(str, Enum):
    FORESIGHT = "Foresight"
    SHAPECHANGE = "Shapechange"
    STORM_OF_VENGEANCE = "Storm of Vengeance"
    TRUE_RESURRECTION = "True Resurrection"


class PaladinLevel1Spells(str, Enum):
    BLESS = "Bless"
    COMMAND = "Command"
    COMPELLED_DUEL = "Compelled Duel"
    CURE_WOUNDS = "Cure Wounds"
    DETECT_EVIL_AND_GOOD = "Detect Evil and Good"
    DETECT_MAGIC = "Detect Magic"
    DETECT_POISON_AND_DISEASE = "Detect Poison and Disease"
    DIVINE_FAVOR = "Divine Favor"
    DIVINE_SMITE = "Divine Smite"
    HEROISM = "Heroism"
    PROTECTION_FROM_EVIL_AND_GOOD = "Protection from Evil and Good"
    PURIFY_FOOD_AND_DRINK = "Purify Food and Drink"
    SEARING_SMITE = "Searing Smite"
    SHIELD_OF_FAITH = "Shield of Faith"
    THUNDEROUS_SMITE = "Thunderous Smite"
    WARDAWAY = "Wardaway"
    WRATHFUL_SMITE = "Wrathful Smite"


class PaladinLevel2Spells(str, Enum):
    AID = "Aid"
    FIND_STEED = "Find Steed"
    GENTLE_REPOSE = "Gentle Repose"
    LESSER_RESTORATION = "Lesser Restoration"
    LOCATE_OBJECT = "Locate Object"
    MAGIC_WEAPON = "Magic Weapon"
    PRAYER_OF_HEALING = "Prayer of Healing"
    PROTECTION_FROM_POISON = "Protection from Poison"
    SHINING_SMITE = "Shining Smite"
    WARDING_BOND = "Warding Bond"
    ZONE_OF_TRUTH = "Zone of Truth"


class PaladinLevel3Spells(str, Enum):
    AURA_OF_VITALITY = "Aura of Vitality"
    BLINDING_SMITE = "Blinding Smite"
    CREATE_FOOD_AND_WATER = "Create Food and Water"
    CRUSADERS_MANTLE = "Crusader's Mantle"
    DAYLIGHT = "Daylight"
    DISPEL_MAGIC = "Dispel Magic"
    ELEMENTAL_WEAPON = "Elemental Weapon"
    MAGIC_CIRCLE = "Magic Circle"
    REMOVE_CURSE = "Remove Curse"
    REVIVIFY = "Revivify"


class PaladinLevel4Spells(str, Enum):
    AURA_OF_LIFE = "Aura of Life"
    AURA_OF_PURITY = "Aura of Purity"
    BANISHMENT = "Banishment"
    DEATH_WARD = "Death Ward"
    LOCATE_CREATURE = "Locate Creature"
    STAGGERING_SMITE = "Staggering Smite"


class PaladinLevel5Spells(str, Enum):
    BANISHING_SMITE = "Banishing Smite"
    CIRCLE_OF_POWER = "Circle Of Power"
    DESTRUCTIVE_WAVE = "Destructive Wave"
    DISPEL_EVIL_AND_GOOD = "Dispel Evil and Good"
    GEAS = "Geas"
    GREATER_RESTORATION = "Greater Restoration"
    RAISE_DEAD = "Raise Dead"
    SUMMON_CELESTIAL = "Summon Celestial"


class RangerLevel1Spells(str, Enum):
    ALARM = "Alarm"
    ANIMAL_FRIENDSHIP = "Animal Friendship"
    CURE_WOUNDS = "Cure Wounds"
    DETECT_MAGIC = "Detect Magic"
    DETECT_POISON_AND_DISEASE = "Detect Poison and Disease"
    ENSNARING_STRIKE = "Ensnaring Strike"
    ENTANGLE = "Entangle"
    FOG_CLOUD = "Fog Cloud"
    GOODBERRY = "Goodberry"
    HAIL_OF_THORNS = "Hail of Thorns"
    HUNTERS_MARK = "Hunter's Mark"
    JUMP = "Jump"
    LONGSTRIDER = "Longstrider"
    SPEAK_WITH_ANIMALS = "Speak with Animals"


class RangerLevel2Spells(str, Enum):
    AID = "Aid"
    ANIMAL_MESSENGER = "Animal Messenger"
    BARKSKIN = "Barkskin"
    BEAST_SENSE = "Beast Sense"
    CORDON_OF_ARROWS = "Cordon of Arrows"
    DARKVISION = "Darkvision"
    ENHANCE_ABILITY = "Enhance Ability"
    FIND_TRAPS = "Find Traps"
    GUST_OF_WIND = "Gust of Wind"
    LESSER_RESTORATION = "Lesser Restoration"
    LOCATE_ANIMALS_OR_PLANTS = "Locate Animals or Plants"
    LOCATE_OBJECT = "Locate Object"
    MAGIC_WEAPON = "Magic Weapon"
    PASS_WITHOUT_TRACE = "Pass without Trace"
    PROTECTION_FROM_POISON = "Protection from Poison"
    SILENCE = "Silence"
    SPIKE_GROWTH = "Spike Growth"
    SUMMON_BEAST = "Summon Beast"


class RangerLevel3Spells(str, Enum):
    CONJURE_ANIMALS = "Conjure Animals"
    CONJURE_BARRAGE = "Conjure Barrage"
    DAYLIGHT = "Daylight"
    DISPEL_MAGIC = "Dispel Magic"
    ELEMENTAL_WEAPON = "Elemental Weapon"
    LIGHTNING_ARROW = "Lightning Arrow"
    MELD_INTO_STONE = "Meld into Stone"
    NONDETECTION = "Nondetection"
    PLANT_GROWTH = "Plant Growth"
    PROTECTION_FROM_ENERGY = "Protection from Energy"
    REVIVIFY = "Revivify"
    SPEAK_WITH_PLANTS = "Speak with Plants"
    SUMMON_FEY = "Summon Fey"
    WATER_BREATHING = "Water Breathing"
    WATER_WALK = "Water Walk"
    WIND_WALL = "Wind Wall"


class RangerLevel4Spells(str, Enum):
    CONJURE_WOODLAND_BEINGS = "Conjure Woodland Beings"
    DOMINATE_BEAST = "Dominate Beast"
    FREEDOM_OF_MOVEMENT = "Freedom of Movement"
    GRASPING_VINE = "Grasping Vine"
    LOCATE_CREATURE = "Locate Creature"
    STONESKIN = "Stoneskin"
    SUMMON_ELEMENTAL = "Summon Elemental"


class RangerLevel5Spells(str, Enum):
    ALUSTRIELS_MOONCLOAK = "Alustriel's Mooncloak"
    COMMUNE_WITH_NATURE = "Commune with Nature"
    CONJURE_VOLLEY = "Conjure Volley"
    GREATER_RESTORATION = "Greater Restoration"
    STEEL_WIND_STRIKE = "Steel Wind Strike"
    SWIFT_QUIVER = "Swift Quiver"
    TREE_STRIDE = "Tree Stride"


class WarlockLevel0Spells(str, Enum):
    BLADE_WARD = "Blade Ward"
    CHILL_TOUCH = "Chill Touch"
    ELDRITCH_BLAST = "Eldritch Blast"
    FRIENDS = "Friends"
    MAGE_HAND = "Mage Hand"
    MIND_SLIVER = "Mind Sliver"
    MINOR_ILLUSION = "Minor Illusion"
    POISON_SPRAY = "Poison Spray"
    PRESTIDIGITATION = "Prestidigitation"
    THUNDERCLAP = "Thunderclap"
    TOLL_THE_DEAD = "Toll the Dead"
    TRUE_STRIKE = "True Strike"


class WarlockLevel1Spells(str, Enum):
    ARMOR_OF_AGATHYS = "Armor of Agathys"
    ARMS_OF_HADAR = "Arms of Hadar"
    BANE = "Bane"
    CHARM_PERSON = "Charm Person"
    COMPREHEND_LANGUAGES = "Comprehend Languages"
    DETECT_MAGIC = "Detect Magic"
    EXPEDITIOUS_RETREAT = "Expeditious Retreat"
    HELLISH_REBUKE = "Hellish Rebuke"
    HEX = "Hex"
    ILLUSORY_SCRIPT = "Illusory Script"
    PROTECTION_FROM_EVIL_AND_GOOD = "Protection from Evil and Good"
    SPEAK_WITH_ANIMALS = "Speak with Animals"
    TASHAS_HIDEOUS_LAUGHTER = "Tasha's Hideous Laughter"
    UNSEEN_SERVANT = "Unseen Servant"
    WITCH_BOLT = "Witch Bolt"


class WarlockLevel2Spells(str, Enum):
    CLOUD_OF_DAGGERS = "Cloud of Daggers"
    CROWN_OF_MADNESS = "Crown of Madness"
    DARKNESS = "Darkness"
    ENTHRALL = "Enthrall"
    HOLD_PERSON = "Hold Person"
    INVISIBILITY = "Invisibility"
    MIND_SPIKE = "Mind Spike"
    MIRROR_IMAGE = "Mirror Image"
    MISTY_STEP = "Misty Step"
    RAY_OF_ENFEEBLEMENT = "Ray of Enfeeblement"
    SPIDER_CLIMB = "Spider Climb"
    SUGGESTION = "Suggestion"


class WarlockLevel3Spells(str, Enum):
    COUNTERSPELL = "Counterspell"
    DISPEL_MAGIC = "Dispel Magic"
    FEAR = "Fear"
    FLY = "Fly"
    GASEOUS_FORM = "Gaseous Form"
    HUNGER_OF_HADAR = "Hunger of Hadar"
    HYPNOTIC_PATTERN = "Hypnotic Pattern"
    MAGIC_CIRCLE = "Magic Circle"
    MAJOR_IMAGE = "Major Image"
    REMOVE_CURSE = "Remove Curse"
    SUMMON_FEY = "Summon Fey"
    SUMMON_UNDEAD = "Summon Undead"
    TONGUES = "Tongues"
    VAMPIRIC_TOUCH = "Vampiric Touch"


class WarlockLevel4Spells(str, Enum):
    BACKLASH = "Backlash"
    BANISHMENT = "Banishment"
    BLIGHT = "Blight"
    CHARM_MONSTER = "Charm Monster"
    DIMENSION_DOOR = "Dimension Door"
    DOOMTIDE = "Doomtide"
    HALLUCINATORY_TERRAIN = "Hallucinatory Terrain"
    SUMMON_ABERRATION = "Summon Aberration"


class WarlockLevel5Spells(str, Enum):
    CONTACT_OTHER_PLANE = "Contact Other Plane"
    DREAM = "Dream"
    HOLD_MONSTER = "Hold Monster"
    JALLARZIS_STORM_OF_RADIANCE = "Jallarzi's Storm of Radiance"
    MISLEAD = "Mislead"
    PLANAR_BINDING = "Planar Binding"
    SCRYING = "Scrying"
    SYNAPTIC_STATIC = "Synaptic Static"
    TELEPORTATION_CIRCLE = "Teleportation Circle"


class WarlockLevel6Spells(str, Enum):
    ARCANE_GATE = "Arcane Gate"
    CIRCLE_OF_DEATH = "Circle of Death"
    CREATE_UNDEAD = "Create Undead"
    EYEBITE = "Eyebite"
    SUMMON_FIEND = "Summon Fiend"
    TASHAS_BUBBLING_CAULDRON = "Tasha's Bubbling Cauldron"
    TRUE_SEEING = "True Seeing"


class WarlockLevel7Spells(str, Enum):
    ETHEREALNESS = "Etherealness"
    FINGER_OF_DEATH = "Finger of Death"
    FORCECAGE = "Forcecage"
    PLANE_SHIFT = "Plane Shift"


class WarlockLevel8Spells(str, Enum):
    BEFUDDLEMENT = "Befuddlement"
    DEMIPLANE = "Demiplane"
    DOMINATE_MONSTER = "Dominate Monster"
    GLIBNESS = "Glibness"
    POWER_WORD_STUN = "Power Word Stun"


class WarlockLevel9Spells(str, Enum):
    ASTRAL_PROJECTION = "Astral Projection"
    BLADE_OF_DISASTER = "Blade of Disaster"
    FORESIGHT = "Foresight"
    GATE = "Gate"
    IMPRISONMENT = "Imprisonment"
    POWER_WORD_KILL = "Power Word Kill"
    TRUE_POLYMORPH = "True Polymorph"
    WEIRD = "Weird"


class AbjurationLevel0Spells(str, Enum):
    BLADE_WARD = "Blade Ward"
    RESISTANCE = "Resistance"


class AbjurationLevel1Spells(str, Enum):
    ALARM = "Alarm"
    ARMOR_OF_AGATHYS = "Armor of Agathys"
    CURE_WOUNDS = "Cure Wounds"
    HEALING_WORD = "Healing Word"
    MAGE_ARMOR = "Mage Armor"
    PROTECTION_FROM_EVIL_AND_GOOD = "Protection from Evil and Good"
    SANCTUARY = "Sanctuary"
    SHIELD = "Shield"
    SHIELD_OF_FAITH = "Shield of Faith"
    WARDAWAY = "Wardaway"


class AbjurationLevel2Spells(str, Enum):
    AID = "Aid"
    ARCANE_LOCK = "Arcane Lock"
    ARCANE_VIGOR = "Arcane Vigor"
    ELMINSTERS_ELUSION = "Elminster's Elusion"
    LESSER_RESTORATION = "Lesser Restoration"
    PASS_WITHOUT_TRACE = "Pass without Trace"
    PRAYER_OF_HEALING = "Prayer of Healing"
    PROTECTION_FROM_POISON = "Protection from Poison"
    WARDING_BOND = "Warding Bond"


class AbjurationLevel3Spells(str, Enum):
    AURA_OF_VITALITY = "Aura of Vitality"
    BEACON_OF_HOPE = "Beacon of Hope"
    COUNTERSPELL = "Counterspell"
    DISPEL_MAGIC = "Dispel Magic"
    GLYPH_OF_WARDING = "Glyph of Warding"
    MAGIC_CIRCLE = "Magic Circle"
    MASS_HEALING_WORD = "Mass Healing Word"
    NONDETECTION = "Nondetection"
    PROTECTION_FROM_ENERGY = "Protection from Energy"
    REMOVE_CURSE = "Remove Curse"


class AbjurationLevel4Spells(str, Enum):
    AURA_OF_LIFE = "Aura of Life"
    AURA_OF_PURITY = "Aura of Purity"
    BACKLASH = "Backlash"
    BANISHMENT = "Banishment"
    DEATH_WARD = "Death Ward"
    FREEDOM_OF_MOVEMENT = "Freedom of Movement"
    MORDENKAINENS_PRIVATE_SANCTUM = "Mordenkainen's Private Sanctum"


class AbjurationLevel5Spells(str, Enum):
    ALUSTRIELS_MOONCLOAK = "Alustriel's Mooncloak"
    ANTILIFE_SHELL = "Antilife Shell"
    CIRCLE_OF_POWER = "Circle of Power"
    DISPEL_EVIL_AND_GOOD = "Dispel Evil and Good"
    GREATER_RESTORATION = "Greater Restoration"
    HALLOW = "Hallow"
    MASS_CURE_WOUNDS = "Mass Cure Wounds"
    PLANAR_BINDING = "Planar Binding"


class AbjurationLevel6Spells(str, Enum):
    CONTINGENCY = "Contingency"
    FORBIDDANCE = "Forbiddance"
    GLOBE_OF_INVULNERABILITY = "Globe of Invulnerability"
    GUARDS_AND_WARDS = "Guards and Wards"
    HEAL = "Heal"


class AbjurationLevel7Spells(str, Enum):
    SYMBOL = "Symbol"


class AbjurationLevel8Spells(str, Enum):
    ANTIMAGIC_FIELD = "Antimagic Field"
    HOLY_AURA = "Holy Aura"
    MIND_BLANK = "Mind Blank"


class AbjurationLevel9Spells(str, Enum):
    IMPRISONMENT = "Imprisonment"
    MASS_HEAL = "Mass Heal"
    PRISMATIC_WALL = "Prismatic Wall"


class ConjurationLevel0Spells(str, Enum):
    MAGE_HAND = "Mage Hand"
    PRODUCE_FLAME = "Produce Flame"


class ConjurationLevel1Spells(str, Enum):
    ARMS_OF_HADAR = "Arms of Hadar"
    ENSNARING_STRIKE = "Ensnaring Strike"
    ENTANGLE = "Entangle"
    FIND_FAMILIAR = "Find Familiar"
    FOG_CLOUD = "Fog Cloud"
    GOODBERRY = "Goodberry"
    GREASE = "Grease"
    HAIL_OF_THORNS = "Hail of Thorns"
    ICE_KNIFE = "Ice Knife"
    TENSERS_FLOATING_DISK = "Tenser's Floating Disk"
    UNSEEN_SERVANT = "Unseen Servant"


class ConjurationLevel2Spells(str, Enum):
    CLOUD_OF_DAGGERS = "Cloud of Daggers"
    DERYANS_HELPFUL_HOMUNCULI = "Deryan's Helpful Homunculi"
    FIND_STEED = "Find Steed"
    FLAMING_SPHERE = "Flaming Sphere"
    MISTY_STEP = "Misty Step"
    SUMMON_BEAST = "Summon Beast"
    WEB = "Web"


class ConjurationLevel3Spells(str, Enum):
    CALL_LIGHTNING = "Call Lightning"
    CONJURE_ANIMALS = "Conjure Animals"
    CONJURE_BARRAGE = "Conjure Barrage"
    CONJURE_CONSTRUCTS = "Conjure Constructs"
    CREATE_FOOD_AND_WATER = "Create Food and Water"
    HUNGER_OF_HADAR = "Hunger of Hadar"
    SLEET_STORM = "Sleet Storm"
    SPIRIT_GUARDIANS = "Spirit Guardians"
    STINKING_CLOUD = "Stinking Cloud"
    SUMMON_FEY = "Summon Fey"
    SYLUNS_VIPER = "Syluné's Viper"


class ConjurationLevel4Spells(str, Enum):
    CONJURE_MINOR_ELEMENTALS = "Conjure Minor Elementals"
    CONJURE_WOODLAND_BEINGS = "Conjure Woodland Beings"
    DIMENSION_DOOR = "Dimension Door"
    DOOMTIDE = "Doomtide"
    EVARDS_BLACK_TENTACLES = "Evard's Black Tentacles"
    GIANT_INSECT = "Giant Insect"
    GRASPING_VINE = "Grasping Vine"
    GUARDIAN_OF_FAITH = "Guardian of Faith"
    LEOMUNDS_SECRET_CHEST = "Leomund's Secret Chest"
    MORDENKAINENS_FAITHFUL_HOUND = "Mordenkainen's Faithful Hound"
    SUMMON_ABERRATION = "Summon Aberration"
    SUMMON_CONSTRUCT = "Summon Construct"
    SUMMON_ELEMENTAL = "Summon Elemental"


class ConjurationLevel5Spells(str, Enum):
    BANISHING_SMITE = "Banishing Smite"
    CLOUDKILL = "Cloudkill"
    CONJURE_ELEMENTAL = "Conjure Elemental"
    CONJURE_VOLLEY = "Conjure Volley"
    INSECT_PLAGUE = "Insect Plague"
    STEEL_WIND_STRIKE = "Steel Wind Strike"
    SUMMON_CELESTIAL = "Summon Celestial"
    SUMMON_DRAGON = "Summon Dragon"
    TELEPORTATION_CIRCLE = "Teleportation Circle"
    TREE_STRIDE = "Tree Stride"


class ConjurationLevel6Spells(str, Enum):
    ARCANE_GATE = "Arcane Gate"
    CONJURE_FEY = "Conjure Fey"
    DRAWMIJS_INSTANT_SUMMONS = "Drawmij's Instant Summons"
    HEROES_FEAST = "Heroes' Feast"
    PLANAR_ALLY = "Planar Ally"
    SUMMON_FIEND = "Summon Fiend"
    TASHAS_BUBBLING_CAULDRON = "Tasha's Bubbling Cauldron"
    TRANSPORT_VIA_PLANTS = "Transport via Plants"
    WALL_OF_THORNS = "Wall of Thorns"
    WORD_OF_RECALL = "Word of Recall"


class ConjurationLevel7Spells(str, Enum):
    CONJURE_CELESTIAL = "Conjure Celestial"
    ETHEREALNESS = "Etherealness"
    MORDENKAINENS_MAGNIFICENT_MANSION = "Mordenkainen's Magnificent Mansion"
    PLANE_SHIFT = "Plane Shift"
    TELEPORT = "Teleport"


class ConjurationLevel8Spells(str, Enum):
    DEMIPLANE = "Demiplane"
    INCENDIARY_CLOUD = "Incendiary Cloud"
    MAZE = "Maze"
    TSUNAMI = "Tsunami"


class ConjurationLevel9Spells(str, Enum):
    BLADE_OF_DISASTER = "Blade of Disaster"
    GATE = "Gate"
    STORM_OF_VENGEANCE = "Storm of Vengeance"
    WISH = "Wish"


class DivinationLevel0Spells(str, Enum):
    GUIDANCE = "Guidance"
    TRUE_STRIKE = "True Strike"


class DivinationLevel1Spells(str, Enum):
    COMPREHEND_LANGUAGES = "Comprehend Languages"
    DETECT_EVIL_AND_GOOD = "Detect Evil and Good"
    DETECT_MAGIC = "Detect Magic"
    DETECT_POISON_AND_DISEASE = "Detect Poison and Disease"
    HUNTERS_MARK = "Hunter's Mark"
    IDENTIFY = "Identify"
    SPEAK_WITH_ANIMALS = "Speak with Animals"


class DivinationLevel2Spells(str, Enum):
    AUGURY = "Augury"
    BEAST_SENSE = "Beast Sense"
    DETECT_THOUGHTS = "Detect Thoughts"
    FIND_TRAPS = "Find Traps"
    LOCATE_ANIMALS_OR_PLANTS = "Locate Animals or Plants"
    LOCATE_OBJECT = "Locate Object"
    MIND_SPIKE = "Mind Spike"
    SEE_INVISIBILITY = "See Invisibility"


class DivinationLevel3Spells(str, Enum):
    CLAIRVOYANCE = "Clairvoyance"
    SENDING = "Sending"
    TONGUES = "Tongues"


class DivinationLevel4Spells(str, Enum):
    ARCANE_EYE = "Arcane Eye"
    DIVINATION = "Divination"
    LOCATE_CREATURE = "Locate Creature"


class DivinationLevel5Spells(str, Enum):
    COMMUNE = "Commune"
    COMMUNE_WITH_NATURE = "Commune with Nature"
    CONTACT_OTHER_PLANE = "Contact Other Plane"
    LEGEND_LORE = "Legend Lore"
    RARYS_TELEPATHIC_BOND = "Rary's Telepathic Bond"
    SCRYING = "Scrying"


class DivinationLevel6Spells(str, Enum):
    FIND_THE_PATH = "Find the Path"
    TRUE_SEEING = "True Seeing"


class DivinationLevel7Spells(str, Enum):
    pass


class DivinationLevel8Spells(str, Enum):
    TELEPATHY = "Telepathy"


class DivinationLevel9Spells(str, Enum):
    FORESIGHT = "Foresight"


class EnchantmentLevel0Spells(str, Enum):
    FRIENDS = "Friends"
    MIND_SLIVER = "Mind Sliver"
    VICIOUS_MOCKERY = "Vicious Mockery"


class EnchantmentLevel1Spells(str, Enum):
    ANIMAL_FRIENDSHIP = "Animal Friendship"
    BANE = "Bane"
    BLESS = "Bless"
    CHARM_PERSON = "Charm Person"
    COMMAND = "Command"
    COMPELLED_DUEL = "Compelled Duel"
    DISSONANT_WHISPERS = "Dissonant Whispers"
    HEROISM = "Heroism"
    HEX = "Hex"
    SLEEP = "Sleep"
    TASHAS_HIDEOUS_LAUGHTER = "Tasha's Hideous Laughter"


class EnchantmentLevel2Spells(str, Enum):
    ANIMAL_MESSENGER = "Animal Messenger"
    CALM_EMOTIONS = "Calm Emotions"
    CROWN_OF_MADNESS = "Crown of Madness"
    ENTHRALL = "Enthrall"
    HOLD_PERSON = "Hold Person"
    SUGGESTION = "Suggestion"
    ZONE_OF_TRUTH = "Zone of Truth"


class EnchantmentLevel4Spells(str, Enum):
    CHARM_MONSTER = "Charm Monster"
    COMPULSION = "Compulsion"
    CONFUSION = "Confusion"
    DOMINATE_BEAST = "Dominate Beast"
    STAGGERING_SMITE = "Staggering Smite"


class EnchantmentLevel5Spells(str, Enum):
    DOMINATE_PERSON = "Dominate Person"
    GEAS = "Geas"
    HOLD_MONSTER = "Hold Monster"
    MODIFY_MEMORY = "Modify Memory"
    SYNAPTIC_STATIC = "Synaptic Static"
    YOLANDES_REGAL_PRESENCE = "Yolande's Regal Presence"


class EnchantmentLevel6Spells(str, Enum):
    DIRGE = "Dirge"
    MASS_SUGGESTION = "Mass Suggestion"
    OTTOS_IRRESISTIBLE_DANCE = "Otto's Irresistible Dance"


class EnchantmentLevel7Spells(str, Enum):
    POWER_WORD_FORTIFY = "Power Word Fortify"


class EnchantmentLevel8Spells(str, Enum):
    ANTIPATHY_SYMPATHY = "Antipathy/Sympathy"
    BEFUDDLEMENT = "Befuddlement"
    DOMINATE_MONSTER = "Dominate Monster"
    GLIBNESS = "Glibness"
    POWER_WORD_STUN = "Power Word Stun"


class EnchantmentLevel9Spells(str, Enum):
    POWER_WORD_HEAL = "Power Word Heal"
    POWER_WORD_KILL = "Power Word Kill"


class EvocationLevel0Spells(str, Enum):
    ACID_SPLASH = "Acid Splash"
    ELDRITCH_BLAST = "Eldritch Blast"
    FIRE_BOLT = "Fire Bolt"
    LIGHT = "Light"
    RAY_OF_FROST = "Ray of Frost"
    SACRED_FLAME = "Sacred Flame"
    SHOCKING_GRASP = "Shocking Grasp"
    SORCEROUS_BURST = "Sorcerous Burst"
    STARRY_WISP = "Starry Wisp"
    THUNDERCLAP = "Thunderclap"
    WORD_OF_RADIANCE = "Word of Radiance"


class EvocationLevel1Spells(str, Enum):
    BURNING_HANDS = "Burning Hands"
    CHROMATIC_ORB = "Chromatic Orb"
    DIVINE_SMITE = "Divine Smite"
    FAERIE_FIRE = "Faerie Fire"
    GUIDING_BOLT = "Guiding Bolt"
    HELLISH_REBUKE = "Hellish Rebuke"
    MAGIC_MISSILE = "Magic Missile"
    SEARING_SMITE = "Searing Smite"
    SPELLFIRE_FLARE = "Spellfire Flare"
    THUNDEROUS_SMITE = "Thunderous Smite"
    THUNDERWAVE = "Thunderwave"
    WITCH_BOLT = "Witch Bolt"


class EvocationLevel2Spells(str, Enum):
    CONTINUAL_FLAME = "Continual Flame"
    DARKNESS = "Darkness"
    FLAME_BLADE = "Flame Blade"
    GUST_OF_WIND = "Gust of Wind"
    MELFS_ACID_ARROW = "Melf's Acid Arrow"
    MOONBEAM = "Moonbeam"
    SCORCHING_RAY = "Scorching Ray"
    SHATTER = "Shatter"
    SPIRITUAL_WEAPON = "Spiritual Weapon"


class EvocationLevel3Spells(str, Enum):
    BLINDING_SMITE = "Blinding Smite"
    CACOPHONIC_SHIELD = "Cacophonic Shield"
    CRUSADERS_MANTLE = "Crusader's Mantle"
    DAYLIGHT = "Daylight"
    FIREBALL = "Fireball"
    LAERALS_SILVER_LANCE = "Laeral's Silver Lance"
    LEOMUNDS_TINY_HUT = "Leomund's Tiny Hut"
    LIGHTNING_BOLT = "Lightning Bolt"
    WIND_WALL = "Wind Wall"


class EvocationLevel4Spells(str, Enum):
    FIRE_SHIELD = "Fire Shield"
    FOUNT_OF_MOONLIGHT = "Fount of Moonlight"
    ICE_STORM = "Ice Storm"
    OTILUKES_RESILIENT_SPHERE = "Otiluke's Resilient Sphere"
    SPELLFIRE_STORM = "Spellfire Storm"
    VITRIOLIC_SPHERE = "Vitriolic Sphere"
    WALL_OF_FIRE = "Wall of Fire"


class EvocationLevel5Spells(str, Enum):
    BIGBYS_HAND = "Bigby's Hand"
    CONE_OF_COLD = "Cone of Cold"
    DESTRUCTIVE_WAVE = "Destructive Wave"
    FLAME_STRIKE = "Flame Strike"
    JALLARZIS_STORM_OF_RADIANCE = "Jallarzi's Storm of Radiance"
    WALL_OF_FORCE = "Wall of Force"
    WALL_OF_STONE = "Wall of Stone"


class EvocationLevel6Spells(str, Enum):
    BLADE_BARRIER = "Blade Barrier"
    CHAIN_LIGHTNING = "Chain Lightning"
    ELMINSTERS_EFFULGENT_SPHERES = "Elminster's Effulgent Spheres"
    OTILUKES_FREEZING_SPHERE = "Otiluke's Freezing Sphere"
    SUNBEAM = "Sunbeam"
    WALL_OF_ICE = "Wall of Ice"


class EvocationLevel7Spells(str, Enum):
    DELAYED_BLAST_FIREBALL = "Delayed Blast Fireball"
    DIVINE_WORD = "Divine Word"
    FIRE_STORM = "Fire Storm"
    FORCECAGE = "Forcecage"
    MORDENKAINENS_SWORD = "Mordenkainen's Sword"
    PRISMATIC_SPRAY = "Prismatic Spray"


class EvocationLevel8Spells(str, Enum):
    HOLY_STAR_OF_MYSTRA = "Holy Star of Mystra"
    SUNBURST = "Sunburst"


class EvocationLevel9Spells(str, Enum):
    METEOR_SWARM = "Meteor Swarm"


class IllusionLevel0Spells(str, Enum):
    DANCING_LIGHTS = "Dancing Lights"
    MINOR_ILLUSION = "Minor Illusion"


class IllusionLevel1Spells(str, Enum):
    COLOR_SPRAY = "Color Spray"
    DISGUISE_SELF = "Disguise Self"
    ILLUSORY_SCRIPT = "Illusory Script"
    SILENT_IMAGE = "Silent Image"


class IllusionLevel2Spells(str, Enum):
    BLUR = "Blur"
    INVISIBILITY = "Invisibility"
    MAGIC_MOUTH = "Magic Mouth"
    MIRROR_IMAGE = "Mirror Image"
    NYSTULS_MAGIC_AURA = "Nystul's Magic Aura"
    PHANTASMAL_FORCE = "Phantasmal Force"
    SILENCE = "Silence"


class IllusionLevel3Spells(str, Enum):
    FEAR = "Fear"
    HYPNOTIC_PATTERN = "Hypnotic Pattern"
    MAJOR_IMAGE = "Major Image"
    PHANTOM_STEED = "Phantom Steed"


class IllusionLevel4Spells(str, Enum):
    GREATER_INVISIBILITY = "Greater Invisibility"
    HALLUCINATORY_TERRAIN = "Hallucinatory Terrain"
    PHANTASMAL_KILLER = "Phantasmal Killer"


class IllusionLevel5Spells(str, Enum):
    CREATION = "Creation"
    DREAM = "Dream"
    MISLEAD = "Mislead"
    SEEMING = "Seeming"


class IllusionLevel6Spells(str, Enum):
    PROGRAMMED_ILLUSION = "Programmed Illusion"


class IllusionLevel7Spells(str, Enum):
    MIRAGE_ARCANE = "Mirage Arcane"
    PROJECT_IMAGE = "Project Image"
    SIMULACRUM = "Simulacrum"


class IllusionLevel8Spells(str, Enum):
    pass


class IllusionLevel9Spells(str, Enum):
    WEIRD = "Weird"


class NecromancyLevel0Spells(str, Enum):
    CHILL_TOUCH = "Chill Touch"
    POISON_SPRAY = "Poison Spray"
    SPARE_THE_DYING = "Spare the Dying"
    TOLL_THE_DEAD = "Toll the Dead"


class NecromancyLevel1Spells(str, Enum):
    FALSE_LIFE = "False Life"
    INFLICT_WOUNDS = "Inflict Wounds"
    RAY_OF_SICKNESS = "Ray of Sickness"
    WRATHFUL_SMITE = "Wrathful Smite"


class NecromancyLevel2Spells(str, Enum):
    DEATH_ARMOR = "Death Armor"
    GENTLE_REPOSE = "Gentle Repose"
    RAY_OF_ENFEEBLEMENT = "Ray of Enfeeblement"


class NecromancyLevel3Spells(str, Enum):
    ANIMATE_DEAD = "Animate Dead"
    BESTOW_CURSE = "Bestow Curse"
    FEIGN_DEATH = "Feign Death"
    REVIVIFY = "Revivify"
    SPEAK_WITH_DEAD = "Speak with Dead"
    SUMMON_UNDEAD = "Summon Undead"
    VAMPIRIC_TOUCH = "Vampiric Touch"


class NecromancyLevel4Spells(str, Enum):
    BLIGHT = "Blight"


class NecromancyLevel5Spells(str, Enum):
    CONTAGION = "Contagion"
    RAISE_DEAD = "Raise Dead"
    REINCARNATE = "Reincarnate"


class NecromancyLevel6Spells(str, Enum):
    CIRCLE_OF_DEATH = "Circle of Death"
    CREATE_UNDEAD = "Create Undead"
    EYEBITE = "Eyebite"
    HARM = "Harm"
    MAGIC_JAR = "Magic Jar"


class NecromancyLevel7Spells(str, Enum):
    FINGER_OF_DEATH = "Finger of Death"
    RESURRECTION = "Resurrection"


class NecromancyLevel8Spells(str, Enum):
    CLONE = "Clone"


class NecromancyLevel9Spells(str, Enum):
    ASTRAL_PROJECTION = "Astral Projection"
    TRUE_RESURRECTION = "True Resurrection"


class TransmutationLevel0Spells(str, Enum):
    DRUIDCRAFT = "Druidcraft"
    ELEMENTALISM = "Elementalism"
    MENDING = "Mending"
    MESSAGE = "Message"
    PRESTIDIGITATION = "Prestidigitation"
    SHILLELAGH = "Shillelagh"
    THAUMATURGY = "Thaumaturgy"
    THORN_WHIP = "Thorn Whip"


class TransmutationLevel1Spells(str, Enum):
    CREATE_OR_DESTROY_WATER = "Create or Destroy Water"
    DIVINE_FAVOR = "Divine Favor"
    EXPEDITIOUS_RETREAT = "Expeditious Retreat"
    FEATHER_FALL = "Feather Fall"
    JUMP = "Jump"
    LONGSTRIDER = "Longstrider"
    PURIFY_FOOD_AND_DRINK = "Purify Food and Drink"


class TransmutationLevel2Spells(str, Enum):
    ALTER_SELF = "Alter Self"
    BARKSKIN = "Barkskin"
    BLINDNESS_DEAFNESS = "Blindness/Deafness"
    CORDON_OF_ARROWS = "Cordon of Arrows"
    DARKVISION = "Darkvision"
    DRAGONS_BREATH = "Dragon's Breath"
    ENHANCE_ABILITY = "Enhance Ability"
    ENLARGE_REDUCE = "Enlarge/Reduce"
    HEAT_METAL = "Heat Metal"
    KNOCK = "Knock"
    LEVITATE = "Levitate"
    MAGIC_WEAPON = "Magic Weapon"
    ROPE_TRICK = "Rope Trick"
    SHINING_SMITE = "Shining Smite"
    SPIDER_CLIMB = "Spider Climb"
    SPIKE_GROWTH = "Spike Growth"


class TransmutationLevel3Spells(str, Enum):
    BLINK = "Blink"
    ELEMENTAL_WEAPON = "Elemental Weapon"
    FLY = "Fly"
    GASEOUS_FORM = "Gaseous Form"
    HASTE = "Haste"
    LIGHTNING_ARROW = "Lightning Arrow"
    MELD_INTO_STONE = "Meld into Stone"
    PLANT_GROWTH = "Plant Growth"
    SLOW = "Slow"
    SPEAK_WITH_PLANTS = "Speak with Plants"
    WATER_BREATHING = "Water Breathing"
    WATER_WALK = "Water Walk"


class TransmutationLevel4Spells(str, Enum):
    CONTROL_WATER = "Control Water"
    FABRICATE = "Fabricate"
    POLYMORPH = "Polymorph"
    STONE_SHAPE = "Stone Shape"
    STONESKIN = "Stoneskin"


class TransmutationLevel5Spells(str, Enum):
    ANIMATE_OBJECTS = "Animate Objects"
    AWAKEN = "Awaken"
    PASSWALL = "Passwall"
    SONGALS_ELEMENTAL_SUFFUSION = "Songal's Elemental Suffusion"
    SWIFT_QUIVER = "Swift Quiver"
    TELEKINESIS = "Telekinesis"


class TransmutationLevel6Spells(str, Enum):
    DISINTEGRATE = "Disintegrate"
    FLESH_TO_STONE = "Flesh to Stone"
    MOVE_EARTH = "Move Earth"
    WIND_WALK = "Wind Walk"


class TransmutationLevel7Spells(str, Enum):
    REGENERATE = "Regenerate"
    REVERSE_GRAVITY = "Reverse Gravity"
    SEQUESTER = "Sequester"
    SIMBULS_SYNOSTODWEOMER = "Simbul's Synostodweomer"


class TransmutationLevel8Spells(str, Enum):
    ANIMAL_SHAPES = "Animal Shapes"
    CONTROL_WEATHER = "Control Weather"
    EARTHQUAKE = "Earthquake"


class TransmutationLevel9Spells(str, Enum):
    SHAPECHANGE = "Shapechange"
    TIME_STOP = "Time Stop"
    TRUE_POLYMORPH = "True Polymorph"


class Spell(ABC):
    """Abstract base spell interface."""

    def __init__(self, spell_casting_ability: Optional[Definitions.Ability] = None):
        self.spell_casting_ability = spell_casting_ability

    # ---------- Required properties ---------- #

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def level(self) -> int:
        pass

    @property
    @abstractmethod
    def school(self) -> str:
        pass

    @property
    @abstractmethod
    def classes(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def casting_time(self) -> str:
        pass

    @property
    @abstractmethod
    def range(self) -> str:
        pass

    @property
    @abstractmethod
    def components(self) -> str:
        pass

    @property
    @abstractmethod
    def duration(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def source(self) -> str:
        pass

    # ---------- Shared behavior ---------- #

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "school": self.school,
            "classes": self.classes,
            "casting_time": self.casting_time,
            "range": self.range,
            "components": self.components,
            "duration": self.duration,
            "description": self.description,
            "source": self.source,
        }

    def write_to_file(self, file):
        lines = [line.strip() + "." for line in self.description.strip().split(".")]
        lines = lines if len(lines) <= 1 else lines[:-1]
        description = "\n".join(lines)

        file.write(f"Name: {self.name}\n")
        file.write(f"Level: {self.level}\n")
        file.write(f"School: {self.school}\n")
        file.write(f"Classes: {', '.join(self.classes)}\n")
        file.write(f"Casting Time: {self.casting_time}\n")
        file.write(f"Range: {self.range}\n")
        file.write(f"Components: {self.components}\n")
        file.write(f"Duration: {self.duration}\n")
        file.write(f"Description:\n{description}\n")
        file.write(f"Source: {self.source}\n")

        if self.spell_casting_ability:
            file.write(f"Spellcasting Ability: {self.spell_casting_ability.value}\n")

    def __repr__(self):
        return f"<Spell {self.name!r}, level {self.level}>"


class DataSpell(Spell):
    """Spell backed directly by JSON/dict data."""

    def __init__(
        self,
        spell_data: dict[str, Any],
        spell_casting_ability: Optional[Definitions.Ability] = None,
    ):
        super().__init__(spell_casting_ability)
        self._data = spell_data

    @property
    def name(self) -> str:
        return str(self._data.get("name"))

    @property
    def level(self) -> int:
        value = self._data.get("level")
        if not isinstance(value, int):
            raise ValueError(f"Invalid level value: {value}")
        return value

    @property
    def school(self) -> str:
        return str(self._data.get("school"))

    @property
    def classes(self) -> List[str]:
        return self._data.get("classes", [])

    @property
    def casting_time(self) -> str:
        return str(self._data.get("casting_time"))

    @property
    def range(self) -> str:
        return str(self._data.get("range"))

    @property
    def components(self) -> str:
        return str(self._data.get("components"))

    @property
    def duration(self) -> str:
        return str(self._data.get("duration"))

    @property
    def description(self) -> str:
        return str(self._data.get("description"))

    @property
    def source(self) -> str:
        return str(self._data.get("source"))


class ExplicitSpell(Spell):
    """Spell defined entirely by explicit fields."""

    def __init__(
        self,
        *,
        name: str,
        level: int,
        school: str,
        classes: list[str],
        casting_time: str,
        range: str,
        components: str,
        duration: str,
        description: str,
        source: str,
        spell_casting_ability: Optional[Definitions.Ability] = None,
    ):
        super().__init__(spell_casting_ability)

        self._name = name
        self._level = level
        self._school = school
        self._classes = classes
        self._casting_time = casting_time
        self._range = range
        self._components = components
        self._duration = duration
        self._description = description
        self._source = source

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        return self._level

    @property
    def school(self) -> str:
        return self._school

    @property
    def classes(self) -> list[str]:
        return self._classes

    @property
    def casting_time(self) -> str:
        return self._casting_time

    @property
    def range(self) -> str:
        return self._range

    @property
    def components(self) -> str:
        return self._components

    @property
    def duration(self) -> str:
        return self._duration

    @property
    def description(self) -> str:
        return self._description

    @property
    def source(self) -> str:
        return self._source
