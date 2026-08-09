"""
Generates player-facing HTML handouts summarizing each 2024-rules class and its
subclasses: flavor text (from SourceTexts), a hand-written mechanical summary,
and every class/subclass feature (pulled live from the Feature classes so it
never drifts from the actual character-sheet code).

Run: python Scrapers/GenerateClassHandouts.py
Output: Output/ClassHandouts/index.html + one file per class.
"""

import importlib
import inspect
import io
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from CharacterContent.Features.Core.BaseFeatures import FEATURE_CARD_CSS, Feature
from Core.Definitions import Ability, CharacterClass, CreatureSize, Skill
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from Utils import Html

CLASS_TEXT_DIR = REPO / "SourceTexts" / "ClassTexts"
SUBCLASS_TEXT_DIR_2024 = REPO / "SourceTexts" / "SubclassTexts2024"
SUBCLASS_TEXT_DIR_2014 = REPO / "SourceTexts" / "SubclassTexts2014"
OUTPUT_DIR = REPO / "Output" / "ClassHandouts"


# ===========================================================================
# Hand-written mechanical summaries (not from source text) — what each class
# actually *does* at the table, mechanically, beyond its flavor.
# ===========================================================================

CLASS_SUMMARIES: dict[str, str] = {
    "Artificer": (
        "A construct-and-invention themed half-caster (Intelligence). Its signature resource is "
        "Infusions — a handful of semi-permanent magic items you build into your gear between "
        "long rests — layered on top of an unusually early spellcasting progression (it gets "
        "spells at level 1, a level ahead of every other half-caster). Magical Tinkering and Right "
        "Tool for the Job add small utility tricks. The subclass, chosen at level 3, mostly decides "
        "which infused item or construct becomes your signature combat tool: a suit of armor for the "
        "Armorer, a cannon for the Artillerist, a companion construct for the Battle Smith, and so on."
    ),
    "Barbarian": (
        "A melee tank whose entire kit revolves around Rage: a limited-use resource (recharges on a "
        "long rest) that grants resistance to bludgeoning/piercing/slashing damage and a flat bonus to "
        "weapon damage while active. Reckless Attack lets you trade away your own defense for guaranteed "
        "advantage on your attacks, and Unarmored Defense (Constitution-based AC) means you're built to "
        "fight without armor. Nearly every subclass feature only triggers or improves while you're "
        "raging, so the subclass mostly reshapes what Rage does rather than giving you a separate "
        "resource of its own."
    ),
    "Bard": (
        "A full spellcaster (Charisma) whose real signature is Bardic Inspiration — a pool of dice, "
        "refreshed on a rest, that you hand out to allies (or yourself) to boost a roll or reduce "
        "damage taken. Expertise and Jack of All Trades make it the best all-round skill class in the "
        "game, and it has one of the widest spell lists of any class. Subclasses mostly change what "
        "Bardic Inspiration dice can additionally be spent on, so the class plays as a flexible "
        "support/skill hybrid rather than a pure blaster or healer."
    ),
    "Cleric": (
        "A full spellcaster (Wisdom) built around Channel Divinity — a small, short-rest-refreshing "
        "pool used for Turn Undead and one or two domain-specific effects. Divine Order lets you pick "
        "between Protector (extra weapon/armor proficiency, a fighting-adjacent kit) or Thaumaturge "
        "(more caster utility) at level 1, so even the 'base' Cleric can lean martial. The Domain "
        "subclass, chosen at level 1, front-loads extra always-prepared spells and defines what Channel "
        "Divinity does, so it shapes the Cleric's table role (healer, striker, support) more than any "
        "other single choice."
    ),
    "Druid": (
        "A full spellcaster (Wisdom) running two resource tracks at once: normal spell slots, and a "
        "limited number of Wild Shape uses that let you transform into a beast with its own separate "
        "HP pool for a set duration. Primal Order (Magician vs. Warden) is a small level-1 choice about "
        "whether you lean more caster or more melee-capable. The Circle subclass, taken at level 2, "
        "mostly expands what Wild Shape can turn into and adds spells that don't count against what you "
        "have prepared — making Druid the class best able to flex between 'squishy caster' and "
        "'melee beast' turn to turn."
    ),
    "Fighter": (
        "A non-caster (except Eldritch Knight) whose whole identity is action economy: more weapon "
        "attacks per round than any other class (up to three extra attacks by level 20), plus Action "
        "Surge for a bonus full turn and Second Wind/Indomitable for self-sustain. Weapon Mastery adds "
        "free rider effects to certain weapons. Because the base class has no resource-management "
        "gimmick the way a caster does, essentially all of the Fighter's build variety comes from its "
        "level-3 subclass — maneuvers for Battle Master, spells for Eldritch Knight, psionics for "
        "Psi Warrior, and so on."
    ),
    "Monk": (
        "A non-caster built around a shared Focus Point pool (2024's replacement for Ki) spent on "
        "bonus-action techniques — Flurry of Blows, Step of the Wind, Patient Defense — layered "
        "on an Unarmored Defense (Dex+Wis) and a scaling Martial Arts damage die. Deflect Attacks and "
        "eventually a second reaction let it punch above its weight defensively despite light armor. The "
        "subclass, picked at level 3, adds new ways to spend Focus Points rather than replacing the "
        "core loop, so every Monk plays similarly turn-to-turn regardless of subclass."
    ),
    "Paladin": (
        "A half-caster (Charisma) that's durable in melee and converts spell slots directly into burst "
        "damage via Divine Smite, rather than casting many spells in a fight. Lay on Hands is a separate "
        "flat HP pool usable for out-of-combat healing or curing conditions, and Channel Divinity plus "
        "(from level 7) an Aura give the party passive buffs just by standing near you. The Oath "
        "subclass, chosen at level 3, supplies its own Channel Divinity options and a short thematic "
        "spell list, but the smite-for-burst-damage engine is the same across every Oath."
    ),
    "Ranger": (
        "A half-caster (Wisdom) that attacks like a Fighter (full Extra Attack progression) with a "
        "smaller spell list layered on top, plus Deft Explorer for skill/utility bonuses instead of a "
        "big combat resource. The level-3 subclass is where the real variety comes in: Beast Master "
        "gives you a second combat unit (a companion with its own turn), while the others (Hunter, "
        "Gloom Stalker, Fey Wanderer, etc.) instead bolt spells or combat tricks onto your own turn."
    ),
    "Rogue": (
        "A non-caster (except Arcane Trickster) whose damage is gated behind Sneak Attack — one "
        "extra damage roll per turn, only when you have advantage or an ally is adjacent to your target "
        "— rather than multiple attacks. It compensates with the best action-economy toolkit for "
        "skills and mobility in the game: Cunning Action (bonus-action Dash/Disengage/Hide), Expertise, "
        "and later Evasion/Uncanny Dodge for survivability. The level-3 subclass mostly adds a new way "
        "to guarantee that once-per-turn advantage, or a side utility track (illusion/enchantment "
        "spells for Arcane Trickster, poison for Assassin, psionics for Soul Knife)."
    ),
    "Sorcerer": (
        "A full spellcaster (Charisma) with a shorter, fixed spells-known list compared to Wizard or "
        "Cleric, but with Sorcery Points — a resource pool that fuels Metamagic (modifying how a "
        "spell works: Twinned, Quickened, etc.) and can be converted to and from spell slots via Font of "
        "Magic. That slot/point flexibility, not spell-list size, is the Sorcerer's core mechanical "
        "identity. The subclass, chosen at level 1, mostly adds its own bonus spells and an extra "
        "Sorcery Point sink rather than changing the core Metamagic engine."
    ),
    "Warlock": (
        "A full-caster-shaped class that actually runs on very few spell slots — but those slots "
        "recharge on a Short Rest and are always cast at your highest available level, which plays very "
        "differently from every other caster's long-rest economy. Most of a Warlock's build identity "
        "comes from Eldritch Invocations, an always-growing a-la-carte list of always-on tricks and "
        "spell-like abilities, plus a Pact Boon (Blade/Chain/Tome/Talisman) chosen at level 3. The "
        "Patron subclass, chosen at level 1, mostly gates which Invocations and bonus spells you can "
        "pick, rather than granting a separate resource of its own."
    ),
    "Wizard": (
        "A full spellcaster (Intelligence) whose power budget lives almost entirely in 'which spells do "
        "I have prepared today' — it has one of the largest spell lists of any class and can "
        "permanently expand it by copying spells into its spellbook from scrolls or other wizards' "
        "books. Arcane Recovery lets it regain some spent spell slots on a Short Rest once per day, "
        "softening the usual long-rest-only slot economy other full casters are stuck with. The Arcane "
        "Tradition subclass, chosen at level 3, grants one signature ability at 3rd level and minor "
        "perks after, but doesn't change this fundamental 'prepared spell selection is the whole game' "
        "identity."
    ),
}


# Hand-written mechanical summaries per 2024 subclass — how it plays, in short.
# Keyed by py_stem (unique across all classes).
SUBCLASS_SUMMARIES: dict[str, str] = {
    # --- Artificer ---
    "ArtificerAlchemist": (
        "Turns your Infusions into a mobile alchemy lab: Experimental Elixir gives you a pool of "
        "temporary random-effect potions, and Alchemical Savant adds your Intelligence modifier to "
        "the healing or damage of spells cast through your tools. A support/utility caster who "
        "patches up the party with on-demand elixirs."
    ),
    "ArtificerArmorer": (
        "Turns your own armor into the subclass's resource: Arcane Armor becomes a wearable focus "
        "with two interchangeable models (Guardian for tanking/melee, Infiltrator for ranged/"
        "skirmishing), each granting its own attack and defensive rider. Plays like an integrated "
        "melee/ranged combatant who is also a full support caster underneath the armor."
    ),
    "ArtificerArtillerist": (
        "Gets a portable turret (Eldritch Cannon) you can plant and command as a bonus action for "
        "ranged damage, healing, or a defensive barrier, plus Arcane Firearm to boost your own "
        "spell damage. A ranged-focused controller who fights through a semi-autonomous companion "
        "instead of melee."
    ),
    "ArtificerBattleSmith": (
        "Gets Steel Defender, a combat-capable construct companion that fights on your turn and "
        "shares your proficiency bonus on its attacks, plus Battle Ready to let you use "
        "Intelligence for weapon attacks. Plays like a pet class hybridized with a melee-competent "
        "caster."
    ),
    "ArtificerCartographer": (
        "Focuses on exploration and battlefield-control magic — extra-dimensional maps, "
        "terrain-shaping and teleportation-style tricks — trading direct damage for movement and "
        "information control for the party."
    ),
    "ArtificerReanimator": (
        "A necromancy-flavored Artificer that builds and commands undead-construct minions, "
        "similar in spirit to Battle Smith's Steel Defender but built around a growing minion "
        "roster instead of one companion."
    ),
    # --- Barbarian ---
    "BarbarianPathOfTheBerserker": (
        "The straightforward damage path: Frenzy lets you make a bonus-action attack every turn "
        "you rage (at the cost of Exhaustion afterward), and later features let you shrug off "
        "being frightened or charmed. Highest single-target damage path, lowest utility."
    ),
    "BarbarianPathOfTheWildHeart": (
        "A totem-animal path that grants a menu of passive animal-spirit benefits (Bear for extra "
        "resistance, Eagle for mobility, Wolf for pack tactics, etc.) chosen and swapped as you "
        "rage, plus a late-game beast-companion-style feature. Flexible buff/utility path layered "
        "onto the base Rage kit."
    ),
    "BarbarianPathOfTheWorldTree": (
        "A support-leaning path: Vitality of the Tree gives temporary HP you can share with "
        "allies, and Branches of the Tree lets you teleport short distances during Rage. Turns the "
        "Barbarian into a mobile, ally-protecting anchor rather than a pure striker."
    ),
    "BarbarianPathOfTheZealot": (
        "A divine-fury path built for surviving death and punishing enemies: Rage bonus damage "
        "becomes Necrotic or Radiant, Warrior of the Gods makes you hard to permanently kill, and "
        "later features let you ignore death saves and deal extra damage on crits. Best pick for a "
        "Barbarian that wants to be the party's unkillable front line."
    ),
    # --- Bard ---
    "BardDance": (
        "Trades some spellcasting for a martial-adjacent bonus-action dance stance (Dazzling/Tempo "
        "Footwork) that grants mobility, extra unarmed-strike-style attacks, or defensive bonuses "
        "— the Bard subclass built to stay in melee."
    ),
    "BardGlamour": (
        "A charm/control-focused caster: Mantle of Inspiration grants temporary HP and free "
        "movement to allies who get Bardic Inspiration, and later features add powerful charm and "
        "command effects. Plays as a battlefield-repositioning support/controller."
    ),
    "BardLore": (
        "The generalist's generalist: Bonus Proficiencies and Cutting Words (spend a Bardic "
        "Inspiration die to weaken an enemy's roll after the fact) plus eventually a boost to your "
        "own checks. Best pick for a skill-monkey/utility Bard rather than a combat specialist."
    ),
    "BardMoon": (
        "A druidic-flavored Bard who can also Wild Shape into a limited beast form by spending "
        "Bardic Inspiration, blending normal Bard support magic with light shapeshifting utility "
        "and mobility."
    ),
    "BardSpirits": (
        "A fortune-telling caster whose Bardic Inspiration dice trigger random buff/debuff effects "
        "off a 'Spirit Tales' table, adding a gambling/random-swing element on top of the normal "
        "support kit."
    ),
    "BardValor": (
        "The martial Bard: bonus armor/shield/weapon proficiency, Extra Attack, and the ability to "
        "grant allies extra attacks or damage via Bardic Inspiration. Plays as a support character "
        "who can also stand in the front line."
    ),
    # --- Cleric ---
    "ClericGrave": (
        "A death-and-undead-focused Domain: guarantees maximum healing to creatures at 0 HP, "
        "detects undead, and later punishes enemies who land killing blows near you. Plays as a "
        "battlefield-medic/anti-undead specialist."
    ),
    "ClericKnowledge": (
        "A skill/utility Domain: bonus skill proficiencies with automatic expertise, and Visions "
        "of the Past for free divination-style information gathering. The least combat-focused "
        "Domain, built for out-of-combat problem solving."
    ),
    "ClericLife": (
        "The dedicated healer Domain: Disciple of Life adds flat extra healing to every healing "
        "spell you cast, plus heavy armor proficiency and a Channel Divinity that heals the party "
        "in a burst. Best pick for a Cleric whose main job is keeping the party alive."
    ),
    "ClericLight": (
        "A damage-Domain built around radiant/fire cantrip scaling (Warding Flare imposes "
        "disadvantage on an attacker; later features add AoE radiant bursts). Plays as the closest "
        "thing Cleric has to a blaster caster."
    ),
    "ClericTrickery": (
        "A stealth/illusion Domain: Blessing of the Trickster grants advantage on Stealth, and "
        "Invoke Duplicity conjures an illusory duplicate of yourself for feints and ranged spell "
        "relay. Plays as a support caster who leans into misdirection rather than direct healing "
        "or damage."
    ),
    "ClericWar": (
        "A melee-Domain: War Priest lets you make a bonus-action weapon attack a few times per "
        "rest, and Channel Divinity grants a big attack-roll bonus. Best pick for a Cleric who "
        "wants to fight in melee with a weapon rather than lean on spells alone."
    ),
    # --- Druid ---
    "DruidLand": (
        "A pure-caster Circle: gains extra always-prepared spells tied to a chosen terrain (arid, "
        "polar, temperate, or tropical) plus Natural Recovery (regain spell slots on a short "
        "rest) and terrain-based resistance. The Circle for a Druid who wants to stay a "
        "spellcaster rather than lean on Wild Shape."
    ),
    "DruidMoon": (
        "The combat-shapeshifter Circle: Wild Shape becomes usable as a bonus action, can turn "
        "into higher-CR combat beasts, and lets you spend spell slots to heal while shape-shifted. "
        "The default pick for a Druid who wants to fight primarily in beast form."
    ),
    "DruidSea": (
        "A Wild-Shape-boosted Circle themed around the ocean: while shape-shifted you gain a "
        "radiant/cold rider on your attacks and later a party-wide protective aura. Blends "
        "melee-beast play with a support buff for allies."
    ),
    "DruidStars": (
        "A ranged/support Circle: Starry Form lets you assume a glowing constellation shape "
        "(Archer, Chalice, or Dragon) granting ranged spell attacks, healing, or a movement/reach "
        "buff instead of a physical Beast form. The Circle for a Druid who wants Wild-Shape-like "
        "resource spending without becoming a melee beast."
    ),
    # --- Fighter ---
    "FighterBanneret": (
        "A leadership subclass: Rallying Cry lets your Second Wind heal nearby allies too, and "
        "later features boost your and your allies' social/leadership rolls. A support-flavored "
        "Fighter that buffs the party rather than adding more personal damage."
    ),
    "FighterBattleMaster": (
        "The tactics subclass: a pool of Superiority Dice spent on Maneuvers (Trip Attack, "
        "Riposte, Precision Attack, etc.) that add riders to your existing attacks. The most "
        "build-flexible Fighter subclass — same action economy as base Fighter, but every attack "
        "can do something extra."
    ),
    "FighterChampion": (
        "The simplest subclass: wider crit range (19-20, later 18-20) and passive bonuses "
        "(advantage on Initiative/Athletics, free movement after a crit, better death saves). No "
        "new resource to manage — just raw, low-complexity power."
    ),
    "FighterEldritchKnight": (
        "Fighter's caster hybrid: a limited Wizard-style spell list (mostly Abjuration/Evocation) "
        "cast with Intelligence, plus War Magic to combine a cantrip with a weapon attack in the "
        "same turn. Adds spellcasting utility on top of the normal Fighter attack routine."
    ),
    "FighterPsiWarrior": (
        "A psionics-flavored subclass: a pool of Psionic Energy dice spent on telekinetic attacks, "
        "damage reduction, and a controlled-fall/shove effect, plus eventually short-range "
        "teleportation. Adds a scaling resource-based toolkit without needing spell slots."
    ),
    # --- Monk ---
    "MonkElements": (
        "Formerly Four Elements: spend Focus Points to cast elemental-themed effects (fire, "
        "water, air, earth) as if they were spells — the Monk subclass that behaves most like a "
        "caster, trading some martial-arts uptime for elemental blasts and utility."
    ),
    "MonkMercy": (
        "A healer/debuffer subclass: Hands of Harm and Hands of Healing let your unarmed strikes "
        "deal extra necrotic damage or heal on demand by spending Focus Points, plus later "
        "features let you resist death yourself. The support-focused Monk."
    ),
    "MonkMysticArts": (
        "Formerly Astral Self: manifests glowing spectral arms and visage that extend your "
        "unarmed strike reach and let you use Wisdom for attacks, plus later features add flight "
        "and radiant/necrotic damage riders. A Focus-Point-fueled boost to your own melee output."
    ),
    "MonkOpenHand": (
        "The default combat subclass: Open Hand Technique adds a rider (knock prone, push, or "
        "deny reactions) to your Flurry of Blows hits, plus later defensive and mobility bonuses. "
        "Straightforward striker/control Monk with no extra resource beyond Focus Points."
    ),
    "MonkShadow": (
        "A stealth/teleport subclass: spend Focus Points to cast darkness and "
        "teleport-between-shadows effects, plus a summonable shadow duplicate at higher levels. "
        "Plays as a mobile skirmisher/assassin-style Monk."
    ),
    # --- Paladin ---
    "PaladinAncients": (
        "A nature-and-light Oath built for endurance: Channel Divinity gives a big temporary "
        "AC/resistance-to-spells buff and a fear effect, and Aura of Warding grants resistance to "
        "spell damage. Best pick for a Paladin standing against heavy magical threats."
    ),
    "PaladinDevotion": (
        "The classic Oath: Channel Divinity adds a big single-attack accuracy boost or a frighten "
        "effect, and Aura of Devotion grants charm/fear immunity to you and nearby allies. "
        "Straightforward, reliable melee/support Paladin with no unusual mechanics."
    ),
    "PaladinGenies": (
        "A wish-granting-patron Oath: Channel Divinity lets you banish a creature briefly or "
        "teleport yourself, and later features grant an elemental damage rider and a genie-themed "
        "vessel item. Adds battlefield removal/mobility on top of the standard Smite engine."
    ),
    "PaladinGlory": (
        "A competitive/heroic Oath: Channel Divinity boosts your speed and jump distance, and "
        "later features let you grant Heroic Inspiration and reroll ability checks for the party. "
        "Leans into athletic/heroic utility alongside normal Smite damage."
    ),
    "PaladinVengeance": (
        "A single-target hunter Oath: Channel Divinity marks a foe with advantage-granting, "
        "movement-denying effects, and Relentless Avenger lets you move after an opportunity "
        "attack. Best pick for a Paladin focused on shutting down one priority target rather than "
        "supporting the group."
    ),
    # --- Ranger ---
    "RangerBeastMaster": (
        "Gets Primal Companion, a full second combat unit (a beast that acts on your turn) whose "
        "attacks scale with your proficiency bonus. Plays like a pet class — most of the "
        "subclass's power sits in the companion, not in extra features for you."
    ),
    "RangerFeyWanderer": (
        "A charm/illusion-flavored half-caster: bonus Enchantment/Illusion spells, a "
        "fear-inducing Otherworldly Glamour, and Beguiling Twist to resist and punish charm/fear "
        "effects. Adds social/control magic on top of standard Ranger attacks."
    ),
    "RangerGloomStalker": (
        "The ambush subclass: bonus initiative and a free extra attack (with bonus damage) on "
        "your first turn, plus darkvision and see-in-magical-darkness utility. Built to front-load "
        "huge burst damage on the opening round of combat."
    ),
    "RangerHollowWarden": (
        "A necrotic/undead-hunting subclass built around withering, life-draining melee riders and "
        "resistance-granting party support against death magic. Plays as a Ranger who trades some "
        "mobility tricks for sustain and anti-undead utility."
    ),
    "RangerHunter": (
        "The build-your-own-toolkit subclass: pick from a menu of combat features at each tier "
        "(e.g. extra damage vs. a chosen target, an AoE reaction attack, or multi-target attacks) "
        "to shape the Ranger into an AoE farmer, a single-target duelist, or a defensive "
        "skirmisher."
    ),
    "RangerWinterWalker": (
        "A cold-themed subclass: bonus cold-damage riders, resistance to cold, and "
        "battlefield-control effects like ice terrain or a cold aura. Plays as a control/damage "
        "hybrid suited to attrition fights."
    ),
    # --- Rogue ---
    "RogueArcaneTrickster": (
        "Rogue's caster hybrid: a limited Wizard-style spell list (mostly Enchantment/Illusion) "
        "cast with Intelligence, plus Mage Hand Legerdemain to use an invisible spectral hand for "
        "sleight-of-hand tricks mid-combat. Adds utility/control spellcasting on top of Sneak "
        "Attack."
    ),
    "RogueAssassin": (
        "The burst-damage subclass: advantage against any creature that hasn't acted yet in "
        "combat (a near-guaranteed Sneak Attack on a surprised or slower target), and Assassinate "
        "later adds automatic-crit-style bonus damage. Built to end a fight in the first round."
    ),
    "RoguePhantom": (
        "A death-and-soul-themed subclass: gain a free skill/tool proficiency each rest, deal "
        "bonus necrotic damage alongside Sneak Attack to a second target, and collect 'soul "
        "trinkets' from nearby deaths for minor magical bonuses. Adds consistent extra damage and "
        "utility."
    ),
    "RogueScionOfTheThree": (
        "A patron-bound subclass granting a small at-will spell-like boon and a scaling combat "
        "rider tied to your chosen patron (fiend, fey, etc.), functioning like a mini-Warlock "
        "bolted onto Sneak Attack."
    ),
    "RogueSoulKnife": (
        "A psionics-flavored subclass: manifests psychic dice used for ranged 'psychic blade' "
        "attacks (no weapon needed) and telepathy, plus a short-range teleport at higher levels. "
        "Best for a Rogue who wants ranged, weapon-less Sneak Attack delivery."
    ),
    "RogueThief": (
        "The generalist subclass: Fast Hands lets you use Cunning Action for extra item "
        "interactions (like drinking a potion or using a scroll as a bonus action), and "
        "Second-Story Work adds climbing speed and better jumps. Utility/mobility focused rather "
        "than adding damage."
    ),
    # --- Sorcerer ---
    "SorcererAberrant": (
        "A psionics-flavored Sorcery: bonus telepathy and psychic-damage spells, and Sorcery "
        "Points can fuel telekinetic and mind-altering effects instead of only Metamagic. Adds a "
        "control/utility layer on top of the normal Sorcerer nova engine."
    ),
    "SorcererClockwork": (
        "An order-and-protection themed Sorcery: can restore a creature's HP or undo a bad "
        "outcome (reroll or negate a triggered effect) by spending Sorcery Points, functioning as "
        "a reactive defensive/support tool for the party."
    ),
    "SorcererDraconic": (
        "The tanky Sorcery: bonus HP per level, natural armor (better AC without armor), and a "
        "damage-type-matched resistance plus a breath-weapon-style spell rider. Best pick for a "
        "Sorcerer that wants to survive being hit rather than avoid it."
    ),
    "SorcererShadow": (
        "A necrotic/darkvision themed Sorcery: can see in magical darkness, gains a fear effect, "
        "and later can briefly become incorporeal to avoid damage. Leans into stealth and "
        "resilience over raw blasting."
    ),
    "SorcererSpellfire": (
        "A fire-and-healing themed Sorcery: converts Sorcery Points into bonus fire damage or "
        "healing on your spells, functioning as a flexible damage/support toggle depending on "
        "what the fight needs."
    ),
    "SorcererWildMagic": (
        "The chaos Sorcery: casting spells can trigger random Wild Magic Surge effects, and "
        "Sorcery Points can be spent to force advantage/disadvantage on a roll (Bend Luck) or "
        "deliberately trigger a surge for a chance at a big effect. Highest ceiling, least "
        "predictable Sorcerer."
    ),
    # --- Warlock ---
    "WarlockArchfey": (
        "A charm/mobility Patron: Fey Presence forces a fear or charm effect on nearby enemies, "
        "and Misty Escape lets you teleport away and turn invisible when hit. Best for a Warlock "
        "who wants to control the battlefield and then vanish."
    ),
    "WarlockCelestial": (
        "The healer Patron: bonus Radiant/healing spells and a Channel Divinity-style HP "
        "restoration or bonus fire/radiant damage on your cantrips. The best Patron for a Warlock "
        "filling a support role."
    ),
    "WarlockFiend": (
        "The nova-damage Patron: Dark One's Blessing grants temporary HP whenever you drop a "
        "creature to 0 HP, keeping you topped up mid-fight, alongside bonus fire/dark-themed "
        "spells. Best for an aggressive, front-line-adjacent Warlock."
    ),
    "WarlockGreatOldOne": (
        "A telepathy/mind-control Patron: bonus telepathy, an Awakened Mind for silent "
        "communication, and later a frighten-and-incapacitate reaction. Leans into psychic "
        "control effects over direct damage."
    ),
    "WarlockUndead": (
        "A resilience Patron: Form of Dread lets you take on a frightening undead-like form "
        "granting resistance and a fear aura, plus later features let you ignore Exhaustion and "
        "stabilize automatically. Best for a Warlock built to keep fighting through punishment."
    ),
    # --- Wizard ---
    "WizardAbjurer": (
        "The defensive School: Arcane Ward is a temporary-HP-style shield that recharges whenever "
        "you cast an Abjuration spell, letting you tank hits by keeping your ward topped up. Best "
        "for a Wizard who wants to stand closer to the front line."
    ),
    "WizardBladesinger": (
        "A melee-caster School: Bladesong grants bonus AC, speed, and Acrobatics while lightly "
        "armed and armored, letting you cast spells and fight in melee at the same time without "
        "penalty. The Wizard subclass built to skip the 'stay at range' assumption entirely."
    ),
    "WizardDiviner": (
        "The battlefield-prediction School: Portent lets you replace any attack roll, save, or "
        "check — yours or an enemy's — with a pre-rolled die a couple of times per rest, turning "
        "bad luck into good on demand."
    ),
    "WizardEvoker": (
        "The blaster School: Sculpt Spells lets you carve allies out of your own damaging spell's "
        "area, and Overchannel lets you cast an evocation spell at maximum damage (at a personal "
        "HP cost on repeated use). Built for a Wizard who wants to safely drop AoE damage into "
        "mixed fights."
    ),
    "WizardIllusionist": (
        "The trickery School: Improved Minor Illusion adds sound and image together, and later "
        "features let you alter illusions after casting or even make part of one briefly real. "
        "Built for control and misdirection rather than direct damage."
    ),
    "WizardTransmuter": (
        "The utility/transformation School: can temporarily change nonmagical objects between "
        "materials and later create a Transmuter's Stone granting a party member a chosen minor "
        "benefit (darkvision, speed, save proficiency, or resistance). Broad out-of-combat and "
        "support utility."
    ),
}


# Hand-written mechanical summaries for 2014-rules legacy subclasses.
SUBCLASS_SUMMARIES_2014: dict[str, str] = {
    # --- Barbarian ---
    "BarbarianPathOfTheAncestralGuardian": (
        "Turns Rage into a protective aura: nearby enemies have disadvantage on attack rolls against "
        "allies, and you can use Reaction to protect an ally by interposing your Rage resistance. "
        "A guardian/tank-focused Path trading damage for party defense."
    ),
    "BarbarianPathOfTheBattlerager": (
        "A dex-based Barbarian using light armor and spiked armor: Reckless Assault lets you make "
        "bonus-action unarmed strikes during Rage, and Spiked Retribution triggers automatic damage "
        "on enemies who damage you. Built for aggressive, close-quarters mobile combat."
    ),
    "BarbarianPathOfTheStormHerald": (
        "Rage manifests as a tempestuous aura: you emit a damage aura while raging (thunder or "
        "lightning), and can spend bonus actions to move the aura or deal extra damage. A blaster-style "
        "Path combining Rage durability with AoE rider damage."
    ),
    "BarbarianPathOfTheTotemWarrior": (
        "Gains animal-spirit totems (Bear, Eagle, Wolf) chosen at level 3, each granting passive "
        "bonuses (extra resistance, bonus speed, pack-tactics benefits) swappable when finishing a "
        "long rest. A flexible buff/utility Path with minor animal-themed features."
    ),
    "BarbarianPathOfWildMagic": (
        "Casting spells near you during Rage triggers random Wild Magic Surge effects (damage, teleport, "
        "forced movement, etc.), and you can spend rage to trigger surges deliberately. A chaotic, "
        "high-variance Path for Barbarians who want magical unpredictability mid-combat."
    ),
    # --- Bard ---
    "BardCreation": (
        "Bardic Inspiration grants temporary HP in addition to the bonus action die, and Mote of "
        "Potential lets an inspired ally gain a bonus to ability checks, attack rolls, or damage. A "
        "support Path built around boosting allies' own rolls rather than controlling the battlefield."
    ),
    "BardEloquence": (
        "Unsettling Words lets you spend a Bardic Inspiration die after someone in range makes an "
        "ability check, ability save, or attack roll, immediately imposing disadvantage. A counter/denial "
        "Path for disrupting enemy actions and saving throws mid-turn."
    ),
    "BardSwords": (
        "Bonus armor/weapon proficiency and a Blade Flourish rider (bonus damage or forced movement) "
        "on weapon attacks triggered by Bardic Inspiration. A melee-focused Bard subclass trading spells "
        "for combat maneuvers."
    ),
    "BardWhispers": (
        "Psychic Scream lets an inspired creature deal psychic damage to a nearby target when they gain "
        "inspiration, plus later you can use Inspiration to amplify a creature's damage or create a "
        "magic ally. A subtle control/damage Path emphasizing illicit whispers and obfuscation."
    ),
    # --- Cleric ---
    "ClericArcana": (
        "Bonus Wizard cantrips and spells, plus the ability to cast an Abjuration or Evocation spell "
        "as a bonus action by spending Channel Divinity. A spellcasting-centric Domain adding versatility "
        "and extra arcane options."
    ),
    "ClericDeath": (
        "Reaper of the Dead adds a second melee attack to your Toll the Dead cantrip against undead/fiends, "
        "and Channel Divinity forces undead/fiends to make a save or be turned. An anti-undead-focused Domain "
        "with heavy crowd control."
    ),
    "ClericForge": (
        "Bonus heavy armor proficiency and advantage on saving throws against magical effects, plus "
        "Channel Divinity to temporarily boost AC or damage rolls for an ally. A protection-themed Domain "
        "emphasizing durability and ally defense."
    ),
    "ClericNature": (
        "Bonus Druid cantrips and heavy nature spells, plus the ability to command beasts with Channel "
        "Divinity and eventually shapeshift into beasts like a Druid. An outdoors/druidic Domain for a "
        "Divine caster who wants Wild Shape access."
    ),
    "ClericOrder": (
        "Emboldening Bond lets you create a link between you and nearby creatures granting temp HP and "
        "advantage on saves, plus Channel Divinity to add extra damage to an ally's attack. A support Domain "
        "focused on empowering others in a coordinated formation."
    ),
    "ClericPeace": (
        "Embody the Peace is the signature feature: you and nearby allies gain temporary HP at the start "
        "of their turn, and Channel Divinity grants advantage on ability checks/saves. An exceptionally "
        "strong support/defensive Domain with consistent HP and advantage provisioning."
    ),
    "ClericTempest": (
        "Bonus martial weapon proficiency and the ability to add thunder/lightning damage to your weapon "
        "attacks, plus Channel Divinity for a devastating AoE knockdown. A martial/damage Domain trading "
        "support for burst damage and forced movement."
    ),
    "ClericTwilight": (
        "Channel Divinity grants 300 feet of dim light and allies in it gain temporary HP at the start "
        "of turns, plus you can spend uses to grant temp HP reactively. An exceptionally strong defensive/"
        "support Domain providing near-permanent party HP top-ups and darkvision."
    ),
    # --- Druid ---
    "DruidDreams": (
        "Serenity allows you to cause fatigue and grant advantage on saves to creatures in your radius, "
        "plus Waking Suggestion lets you implant a compulsion in a sleeping creature. A subtle control Domain "
        "emphasizing sleep, dreams, and mind-affecting magic."
    ),
    "DruidShepherd": (
        "Unicorn Guide grants temp HP to nearby creatures when you Wild Shape or use healing magic, and "
        "later you can summon spectral animals as companions. A support-focused Circle providing consistent "
        "ally buffing through summons."
    ),
    "DruidSpores": (
        "Symbiotic Entity gives you temporary HP and benefits when you anger spores or take damage, and "
        "Fungal Infestation lets you animate dead humanoids as zombies. A melee/necromancy-flavored Circle "
        "that plays like a hybrid melee combatant."
    ),
    "DruidWildfire": (
        "Wildfire Spirit summons a fire elemental companion that acts on your turn and can teleport to "
        "spread damage AoE, plus you can teleport through the spirit. A pet-companion Circle built around "
        "commanding a semi-autonomous fire elemental."
    ),
    # --- Fighter ---
    "FighterArcaneArcher": (
        "Arcane Shot lets you spend Superiority Dice to fire magical arrows (force damage, knockback, "
        "invisibility, etc.), adding spellcaster-style versatility to weapon attacks. A control/utility "
        "subclass turning you into a magical archer."
    ),
    "FighterCavalier": (
        "Bonus proficiency with mounted combat plus Unwavering Mark to force enemies who damage your allies "
        "to make a save against your retaliation. A tank/leadership Fighter focused on mounted charge damage "
        "and protecting others."
    ),
    "FighterEchoKnight": (
        "Echo Avatar creates a spectral duplicate that acts as an extension of yourself, letting you make "
        "attacks from its location and teleport to it. A mobility/positioning subclass emphasizing flanking "
        "and tactical placement."
    ),
    "FighterRuneKnight": (
        "Giant's Might lets you grow large and gain bonus damage, strength, and reach, with Rune features "
        "granting saves, advantage, or forced movement. A size-shifting, rune-magic subclass built for "
        "adaptable battlefield control."
    ),
    "FighterSamurai": (
        "Fighting Spirit grants advantage on your first attack each round and let you heal as a bonus action "
        "while active, plus Elegant Courtier boosts social rolls. A focus-fueled precision striker subclass "
        "emphasizing poise and self-healing."
    ),
    # --- Monk ---
    "MonkDrunkenMaster": (
        "Intoxicated Frenzy lets your unarmed strikes knock creatures prone or push them away during "
        "Flurry of Blows, plus Drunkard's Luck adds evasion-like saves. A mobile, control-focused Monastery "
        "trading direct damage for forced movement and positioning."
    ),
    "MonkKensei": (
        "Kensei Weapons expands your martial arts to use a chosen weapon alongside unarmed strikes with "
        "the same damage die, plus ranged weapon attacks gain a bonus die. A versatile weapon-using Monastery "
        "for a Monk who wants to wield implements."
    ),
    "MonkLongDeath": (
        "Mastery of Death lets you spend ki points to avoid falling unconscious when you would reach 0 HP, "
        "plus later you resist necrotic damage and can animate corpses. A survival/undeath-themed Monastery "
        "built for grim durability."
    ),
    "MonkSunSoul": (
        "Radiant Sun Bolt is an unarmed strike alternative that deals radiant damage and scales with your "
        "martial arts die, plus you gain bonus radiant-damage spells. A radiant-damage Monastery combining "
        "unarmed strikes with radiant spell synergy."
    ),
    # --- Paladin ---
    "PaladinConquest": (
        "Guided Strike adds advantage to a weapon attack, and Conquering Presence frightens enemies who "
        "fail a save, locking them down so they can't move. A conquest/control Oath emphasizing fear and "
        "forced immobility."
    ),
    "PaladinCrown": (
        "Champion of Order adds proficiency to initiative and persuasion, plus Divine Purpose lets you "
        "make a bonus attack when an ally scores a hit nearby. A leadership/order-themed Oath focused on "
        "bolstering allies."
    ),
    "PaladinOathbreaker": (
        "A dark-themed Oath that channels necrotic/dark power: Aura of Hate lets undead/fiends nearby gain "
        "bonus damage, and Spiteful Rebuke forces attackers to make a save or take necrotic damage. A "
        "necromancy-flavored subclass for evil Paladins."
    ),
    "PaladinRedemption": (
        "Emissary of Peace adds proficiency to social checks and grants temp HP to nearby allies, while "
        "Protective Bond lets you redirect damage a nearby creature takes to yourself. A pacifist/"
        "redemption-themed Oath for a Paladin focused on protection and healing."
    ),
    "PaladinWatchers": (
        "Bonus spells and language proficiencies, plus Aura of the Sentinels grants nearby allies advantage "
        "on initiative and reaction attacks. A planar-warden Oath for a Paladin who stands watch against "
        "extraplanar threats."
    ),
    # --- Ranger ---
    "RangerDrakewarden": (
        "Drake Companion summons a drake that acts on your turn and grows with you, dealing bonus fire/poison "
        "damage on its attacks. A pet-companion Conclave trading some martial prowess for a scaled familiar."
    ),
    "RangerHorizonWalker": (
        "Horizon Walker grants advantage on initiative and lets you cast Teleportation Circle at will, plus "
        "you add extra damage to attacks against creatures from other planes. A planar-exploration Conclave "
        "built for mobility and otherworldly threats."
    ),
    "RangerMonsterSlayer": (
        "Slayer's Prey marks a creature, and each turn you add extra damage against it plus advantage on "
        "saves against its spells and abilities. A single-target-hunter Conclave focusing on marked-prey bonuses."
    ),
    "RangerSwarmkeeper": (
        "Gathered Swarm conjures visible insects that deal bonus damage on your attacks and let you move a "
        "creature or trigger an AoE reaction. A swarm-companion Conclave that functions like a semi-autonomous "
        "entity."
    ),
    # --- Rogue ---
    "RogueMastermind": (
        "Master of Intrigue adds bonus intelligence-gathering and language proficiencies, plus Soul of "
        "Deceit lets you disengage/hide as a bonus action reliably and lie convincingly. An espionage/"
        "intrigue Archetype for a cunning infiltrator."
    ),
    "RogueScout": (
        "Skirmisher grants extra Cunning Action uses and lets you move half your speed when you take a "
        "reaction, plus Ambush lets you roll initiative with advantage in a surprise round. A mobile "
        "skirmisher Archetype excelling in tactical positioning."
    ),
    "RogueSwashbuckler": (
        "Fancy Footwork lets you move away from enemies without triggering opportunity attacks when you hit "
        "them, plus Rakish Audacity adds Charisma to initiative. A duelist/acrobat Archetype for a Rogue who "
        "wants to swagger and swashbuckle."
    ),
    # --- Sorcerer ---
    "SorcererAberrantMind": (
        "Psionic Sorcery lets you cast divination/enchantment spells with Sorcery Points instead of spells "
        "known, plus telepathy and psychic damage rider spells. An intrigue/telepathy Sorcery built around "
        "subtle mind-affecting effects."
    ),
    "SorcererDivineSoul": (
        "Bonus cleric-flavored spells and Channel Divinity options (healing burst, turning undead), plus "
        "Unerring Spell lets you reroll damage dice. A divine-flavored Sorcery that blends cleric and sorcerer "
        "mechanics."
    ),
    "SorcererLunarSorcery": (
        "Moon Forms grant variable bonuses based on lunar phase (Waxing for temp HP/advantage, Full for extra "
        "damage, Waning for rerolls), and Lunar Embodiment adds lunar-themed spell options. A phase-dependent "
        "Sorcery that changes abilities based on active moon."
    ),
    "SorcererStormSorcery": (
        "Storm Guide lets you choose who thunderstorm benefits (wind, lightning damage) apply to, plus "
        "Thunderbolt Strike allows bonus movement after lightning-damage hits. A storm/air-themed Sorcery "
        "emphasizing thunderstorm manipulation."
    ),
    # --- Warlock ---
    "WarlockFathomless": (
        "Tentacle of the Deep conjures an invisible tentacle you can command as a bonus action for attacks/"
        "movement, plus you gain swimming speed and water-breathing. A sea-tentacle Patron that functions "
        "like a semi-autonomous limb."
    ),
    "WarlockHexblade": (
        "Hexblade's Curse marks a creature, letting you add bonus damage and force rerolls, plus bonus "
        "melee-weapon spells and the ability to use Charisma for weapon attacks. A cursed-blade Patron "
        "for a Warlock who wants to fight in melee."
    ),
    "WarlockTheGenie": (
        "Genie's Vessel is a magic item that grants proficiency bonuses and reaction-based AC boosts, plus "
        "you can cast spells from inside it and eventually plane-shift. A djinn-themed Patron centered around "
        "a magical vessel-sanctuary."
    ),
    "WarlockTheUndying": (
        "Form of Dread manifests a frightening aura granting you resistance and fear effects, plus Undying "
        "Nature prevents you from aging and lets you regain HP if you finish a short rest. A lichdom/immortality "
        "Patron that trades resources for extreme durability."
    ),
    # --- Wizard ---
    "WizardChronurgy": (
        "Arcane Abeyance lets you store spells to cast later with Delayed spell effects, and Convergent "
        "Future grants advantage on a roll (once per short rest). A time-manipulation Tradition for a Wizard "
        "who bends causality."
    ),
    "WizardConjuration": (
        "Conjuration Savant makes your summoned creatures more durable and grants them temp HP, plus "
        "Benign Transposition lets you swap positions with a summoned creature. A summoning-focused Tradition "
        "emphasizing minion control and battlefield positioning."
    ),
    "WizardEnchantment": (
        "Enchantment Savant adds your Int to charm save DCs and lets you use a reaction to cause an "
        "enchanted creature to use disadvantage on saves. A charm/mind-control Tradition for a Wizard who "
        "dominates through subtle magic."
    ),
    "WizardGraviturgy": (
        "Gravity Well lets you pull/push creatures short distances after casting a spell, and you can "
        "calculate precise gravitational effects (damage, fall height). A gravity-manipulation Tradition "
        "for force-and-fall themed spellcasting."
    ),
    "WizardNecromancy": (
        "Undead Thralls turn some of your spell slots into undead minions (skeletons/zombies) with "
        "bonus HP, and Grim Harvest lets you regain HP when undead die. A necromancy/summoning Tradition "
        "emphasizing undead companion control."
    ),
    "WizardOrderOfScribes": (
        "Awakened Spellbook is your spellbook familiar, giving it AC and HP, plus Manifest Mind lets the "
        "book scribe spells you learn and grant you temp HP. A scholarly Tradition that treats your spellbook "
        "as a semi-autonomous companion."
    ),
}


# ===========================================================================
# Class / subclass tables
# ===========================================================================


@dataclass
class ClassInfo:
    name: str
    character_class: CharacterClass
    spell_ability: Ability
    text_file: str


@dataclass
class SubclassInfo:
    py_stem: str
    display_name: str
    text_dir: Path
    text_stem: str
    flavor_edition: str  # "2024" or "2014" (2014 used as a flavor-only fallback)
    is_legacy_2014: bool = False


CLASSES: list[ClassInfo] = [
    ClassInfo(
        "Artificer", CharacterClass.ARTIFICER, Ability.INTELLIGENCE, "artificer.txt"
    ),
    ClassInfo(
        "Barbarian", CharacterClass.BARBARIAN, Ability.INTELLIGENCE, "barbarian.txt"
    ),
    ClassInfo("Bard", CharacterClass.BARD, Ability.CHARISMA, "bard.txt"),
    ClassInfo("Cleric", CharacterClass.CLERIC, Ability.WISDOM, "cleric.txt"),
    ClassInfo("Druid", CharacterClass.DRUID, Ability.WISDOM, "druid.txt"),
    ClassInfo("Fighter", CharacterClass.FIGHTER, Ability.INTELLIGENCE, "fighter.txt"),
    ClassInfo("Monk", CharacterClass.MONK, Ability.INTELLIGENCE, "monk.txt"),
    ClassInfo("Paladin", CharacterClass.PALADIN, Ability.CHARISMA, "paladin.txt"),
    ClassInfo("Ranger", CharacterClass.RANGER, Ability.WISDOM, "ranger.txt"),
    ClassInfo("Rogue", CharacterClass.ROGUE, Ability.INTELLIGENCE, "rogue.txt"),
    ClassInfo("Sorcerer", CharacterClass.SORCERER, Ability.CHARISMA, "sorcerer.txt"),
    ClassInfo("Warlock", CharacterClass.WARLOCK, Ability.CHARISMA, "warlock.txt"),
    ClassInfo("Wizard", CharacterClass.WIZARD, Ability.INTELLIGENCE, "wizard.txt"),
]


def _s2024(stem: str) -> tuple[Path, str, str]:
    return (SUBCLASS_TEXT_DIR_2024, stem, "2024")


def _s2014(stem: str) -> tuple[Path, str, str]:
    return (SUBCLASS_TEXT_DIR_2014, stem, "2014")


# (py_stem, display_name, (text_dir, text_stem, edition))
_SUBCLASS_RAW: dict[str, list[tuple[str, str, tuple[Path, str, str]]]] = {
    "Artificer": [
        ("ArtificerAlchemist", "Alchemist", _s2024("alchemist")),
        ("ArtificerArmorer", "Armorer", _s2024("armorer")),
        ("ArtificerArtillerist", "Artillerist", _s2024("artillerist")),
        ("ArtificerBattleSmith", "Battle Smith", _s2024("battle_smith")),
        ("ArtificerCartographer", "Cartographer", _s2024("cartographer")),
        ("ArtificerReanimator", "Reanimator", _s2024("reanimator")),
    ],
    "Barbarian": [
        (
            "BarbarianPathOfTheBerserker",
            "Path of the Berserker",
            _s2024("path_of_the_berserker"),
        ),
        (
            "BarbarianPathOfTheWildHeart",
            "Path of the Wild Heart",
            _s2024("path_of_the_wild_heart"),
        ),
        (
            "BarbarianPathOfTheWorldTree",
            "Path of the World Tree",
            _s2024("path_of_the_world_tree"),
        ),
        (
            "BarbarianPathOfTheZealot",
            "Path of the Zealot",
            _s2024("path_of_the_zealot"),
        ),
    ],
    "Bard": [
        ("BardDance", "College of Dance", _s2024("college_of_dance")),
        ("BardGlamour", "College of Glamour", _s2024("college_of_glamour")),
        ("BardLore", "College of Lore", _s2024("college_of_lore")),
        ("BardMoon", "College of the Moon", _s2024("college_of_the_moon")),
        ("BardSpirits", "College of Spirits", _s2014("spirits")),
        ("BardValor", "College of Valor", _s2024("college_of_valor")),
    ],
    "Cleric": [
        ("ClericGrave", "Grave Domain", _s2014("grave")),
        ("ClericKnowledge", "Knowledge Domain", _s2024("knowledge_domain")),
        ("ClericLife", "Life Domain", _s2024("life_domain")),
        ("ClericLight", "Light Domain", _s2024("light_domain")),
        ("ClericTrickery", "Trickery Domain", _s2024("trickery_domain")),
        ("ClericWar", "War Domain", _s2024("war_domain")),
    ],
    "Druid": [
        ("DruidLand", "Circle of the Land", _s2024("circle_of_the_land")),
        ("DruidMoon", "Circle of the Moon", _s2024("circle_of_the_moon")),
        ("DruidSea", "Circle of the Sea", _s2024("circle_of_the_sea")),
        ("DruidStars", "Circle of the Stars", _s2024("circle_of_the_stars")),
    ],
    "Fighter": [
        ("FighterBanneret", "Banneret", _s2014("banneret")),
        ("FighterBattleMaster", "Battle Master", _s2024("battle_master")),
        ("FighterChampion", "Champion", _s2024("champion")),
        ("FighterEldritchKnight", "Eldritch Knight", _s2024("eldritch_knight")),
        ("FighterPsiWarrior", "Psi Warrior", _s2024("psi_warrior")),
    ],
    "Monk": [
        ("MonkElements", "Warrior of the Elements", _s2024("warrior_of_the_elements")),
        ("MonkMercy", "Warrior of Mercy", _s2024("warrior_of_mercy")),
        (
            "MonkMysticArts",
            "Warrior of the Mystic Arts",
            _s2024("warrior_of_the_mystic_arts"),
        ),
        (
            "MonkOpenHand",
            "Warrior of the Open Hand",
            _s2024("warrior_of_the_open_hand"),
        ),
        ("MonkShadow", "Warrior of Shadow", _s2024("warrior_of_shadow")),
    ],
    "Paladin": [
        ("PaladinAncients", "Oath of the Ancients", _s2024("oath_of_the_ancients")),
        ("PaladinDevotion", "Oath of Devotion", _s2024("oath_of_devotion")),
        (
            "PaladinGenies",
            "Oath of the Noble Genie",
            _s2024("oath_of_the_noble_genies"),
        ),
        ("PaladinGlory", "Oath of Glory", _s2024("oath_of_glory")),
        ("PaladinVengeance", "Oath of Vengeance", _s2024("oath_of_vengeance")),
    ],
    "Ranger": [
        ("RangerBeastMaster", "Beast Master", _s2024("beast_master")),
        ("RangerFeyWanderer", "Fey Wanderer", _s2024("fey_wanderer")),
        ("RangerGloomStalker", "Gloom Stalker", _s2024("gloom_stalker")),
        ("RangerHollowWarden", "Hollow Warden", _s2024("hollow_warden")),
        ("RangerHunter", "Hunter", _s2024("hunter")),
        ("RangerWinterWalker", "Winter Walker", _s2024("winter_walker")),
    ],
    "Rogue": [
        ("RogueArcaneTrickster", "Arcane Trickster", _s2024("arcane_trickster")),
        ("RogueAssassin", "Assassin", _s2024("assassin")),
        ("RoguePhantom", "Phantom", _s2014("phantom")),
        ("RogueScionOfTheThree", "Scion of the Three", _s2024("scion_of_the_three")),
        ("RogueSoulKnife", "Soul Knife", _s2024("soulknife")),
        ("RogueThief", "Thief", _s2024("thief")),
    ],
    "Sorcerer": [
        ("SorcererAberrant", "Aberrant Sorcery", _s2024("aberrant_sorcery")),
        ("SorcererClockwork", "Clockwork Sorcery", _s2024("clockwork_sorcery")),
        ("SorcererDraconic", "Draconic Sorcery", _s2024("draconic_sorcery")),
        ("SorcererShadow", "Shadow Sorcery", _s2024("shadow_sorcery")),
        ("SorcererSpellfire", "Spellfire Sorcery", _s2024("spellfire_sorcery")),
        ("SorcererWildMagic", "Wild Magic Sorcery", _s2024("wild_magic_sorcery")),
    ],
    "Warlock": [
        ("WarlockArchfey", "The Archfey", _s2024("archfey_patron")),
        ("WarlockCelestial", "The Celestial", _s2024("celestial_patron")),
        ("WarlockFiend", "The Fiend", _s2024("fiend_patron")),
        ("WarlockGreatOldOne", "The Great Old One", _s2024("great_old_one_patron")),
        ("WarlockUndead", "The Undead", _s2024("undead_patron")),
    ],
    "Wizard": [
        ("WizardAbjurer", "Abjurer", _s2024("abjurer")),
        ("WizardBladesinger", "Bladesinger", _s2024("bladesinger")),
        ("WizardDiviner", "Diviner", _s2024("diviner")),
        ("WizardEvoker", "Evoker", _s2024("evoker")),
        ("WizardIllusionist", "Illusionist", _s2024("illusionist")),
        ("WizardTransmuter", "Transmuter", _s2014("transmutation")),
    ],
}

SUBCLASSES: dict[str, list[SubclassInfo]] = {
    class_name: [
        SubclassInfo(py_stem, display_name, text_dir, text_stem, edition)
        for py_stem, display_name, (text_dir, text_stem, edition) in entries
    ]
    for class_name, entries in _SUBCLASS_RAW.items()
}


def _legacy2014(
    py_stem: str, display_name: str, text_stem: str
) -> SubclassInfo:
    """Helper to build a legacy 2014 subclass info."""
    return SubclassInfo(
        py_stem, display_name, SUBCLASS_TEXT_DIR_2014, text_stem, "2014", True
    )


# Legacy 2014-rules subclasses not already present in the 2024 list.
LEGACY_2014_SUBCLASSES: dict[str, list[SubclassInfo]] = {
    "Barbarian": [
        _legacy2014(
            "BarbarianPathOfTheAncestralGuardian",
            "Path of the Ancestral Guardian",
            "ancestral_guardian",
        ),
        _legacy2014(
            "BarbarianPathOfTheBattlerager",
            "Path of the Battlerager",
            "battlerager",
        ),
        _legacy2014(
            "BarbarianPathOfTheStormHerald", "Path of the Storm Herald", "storm_herald"
        ),
        _legacy2014(
            "BarbarianPathOfTheTotemWarrior", "Path of the Totem Warrior", "totem_warrior"
        ),
        _legacy2014(
            "BarbarianPathOfWildMagic", "Path of Wild Magic", "barbarian_wild_magic"
        ),
    ],
    "Bard": [
        _legacy2014("BardCreation", "College of Creation", "creation"),
        _legacy2014("BardEloquence", "College of Eloquence", "eloquence"),
        _legacy2014("BardSwords", "College of Swords", "swords"),
        _legacy2014("BardWhispers", "College of Whispers", "whispers"),
    ],
    "Cleric": [
        _legacy2014("ClericArcana", "Arcana Domain", "arcana"),
        _legacy2014("ClericDeath", "Death Domain", "death"),
        _legacy2014("ClericForge", "Forge Domain", "forge"),
        _legacy2014("ClericNature", "Nature Domain", "nature"),
        _legacy2014("ClericOrder", "Order Domain", "order"),
        _legacy2014("ClericPeace", "Peace Domain", "peace"),
        _legacy2014("ClericTempest", "Tempest Domain", "tempest"),
        _legacy2014("ClericTwilight", "Twilight Domain", "twilight"),
    ],
    "Druid": [
        _legacy2014("DruidDreams", "Circle of Dreams", "dreams"),
        _legacy2014("DruidShepherd", "Circle of the Shepherd", "shepherd"),
        _legacy2014("DruidSpores", "Circle of Spores", "spores"),
        _legacy2014("DruidWildfire", "Circle of Wildfire", "wildfire"),
    ],
    "Fighter": [
        _legacy2014("FighterArcaneArcher", "Arcane Archer", "arcane_archer"),
        _legacy2014("FighterCavalier", "Cavalier", "cavalier"),
        _legacy2014("FighterEchoKnight", "Echo Knight", "echo_knight"),
        _legacy2014("FighterRuneKnight", "Rune Knight", "rune_knight"),
        _legacy2014("FighterSamurai", "Samurai", "samurai"),
    ],
    "Monk": [
        _legacy2014("MonkDrunkenMaster", "Way of the Drunken Master", "drunken_master"),
        _legacy2014("MonkKensei", "Way of the Kensei", "kensei"),
        _legacy2014("MonkLongDeath", "Way of the Long Death", "long_death"),
        _legacy2014("MonkSunSoul", "Way of the Sun Soul", "sun_soul"),
    ],
    "Paladin": [
        _legacy2014("PaladinConquest", "Oath of Conquest", "conquest"),
        _legacy2014("PaladinCrown", "Oath of the Crown", "crown"),
        _legacy2014("PaladinOathbreaker", "Oathbreaker", "oathbreaker"),
        _legacy2014("PaladinRedemption", "Oath of Redemption", "redemption"),
        _legacy2014("PaladinWatchers", "Oath of the Watchers", "watchers"),
    ],
    "Ranger": [
        _legacy2014("RangerDrakewarden", "Drakewarden", "drakewarden"),
        _legacy2014("RangerHorizonWalker", "Horizon Walker", "horizon_walker"),
        _legacy2014("RangerMonsterSlayer", "Monster Slayer", "monster_slayer"),
        _legacy2014("RangerSwarmkeeper", "Swarmkeeper", "swarmkeeper"),
    ],
    "Rogue": [
        _legacy2014("RogueMastermind", "Mastermind", "mastermind"),
        _legacy2014("RogueScout", "Scout", "scout"),
        _legacy2014("RogueSwashbuckler", "Swashbuckler", "swashbuckler"),
    ],
    "Sorcerer": [
        _legacy2014("SorcererAberrantMind", "Aberrant Mind", "aberrant_mind"),
        _legacy2014("SorcererDivineSoul", "Divine Soul", "divine_soul"),
        _legacy2014("SorcererLunarSorcery", "Lunar Sorcery", "lunar_sorcery"),
        _legacy2014("SorcererStormSorcery", "Storm Sorcery", "storm_sorcery"),
    ],
    "Warlock": [
        _legacy2014("WarlockFathomless", "The Fathomless", "fathomless"),
        _legacy2014("WarlockHexblade", "The Hexblade", "hexblade"),
        _legacy2014("WarlockTheGenie", "The Genie", "the_genie"),
        _legacy2014("WarlockTheUndying", "The Undying", "undying"),
    ],
    "Wizard": [
        _legacy2014("WizardChronurgy", "Chronurgy Magic", "chronurgy"),
        _legacy2014("WizardConjuration", "School of Conjuration", "conjuration"),
        _legacy2014("WizardEnchantment", "School of Enchantment", "enchantment"),
        _legacy2014("WizardGraviturgy", "Graviturgy Magic", "graviturgy"),
        _legacy2014("WizardNecromancy", "School of Necromancy", "necromancy"),
        _legacy2014("WizardOrderOfScribes", "Order of Scribes", "order_of_scribes"),
    ],
}


# ===========================================================================
# Flavor-text parsing
# ===========================================================================


def _nonempty_paragraphs(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def parse_class_flavor(text_file: str) -> list[str]:
    path = CLASS_TEXT_DIR / text_file
    lines = path.read_text(encoding="utf-8").splitlines()

    source_idx = next((i for i, l in enumerate(lines) if l.startswith("Source:")), -1)
    start = source_idx + 1 if source_idx >= 0 else 0

    end = len(lines)
    for i in range(start, len(lines)):
        if re.match(r"^Core\s+.+\s+Traits\s*$", lines[i].strip()):
            end = i
            break

    return _nonempty_paragraphs(lines[start:end])


def parse_subclass_flavor(info: SubclassInfo) -> list[str]:
    path = info.text_dir / f"{info.text_stem}.txt"
    lines = path.read_text(encoding="utf-8").splitlines()

    if info.flavor_edition == "2024":
        source_idx = next(
            (i for i, l in enumerate(lines) if l.startswith("Source")), -1
        )
        start = source_idx + 1 if source_idx >= 0 else 0
        end = len(lines)
        for i in range(start, len(lines)):
            if re.match(r"^Level\s+\d+:", lines[i].strip()):
                end = i
                break
        return _nonempty_paragraphs(lines[start:end])
    else:
        end = len(lines)
        for i, l in enumerate(lines):
            if re.match(r"^Sources?:", l.strip()):
                end = i
                break
        return _nonempty_paragraphs(lines[:end])


# ===========================================================================
# Feature extraction (imports the real Feature classes so text never drifts
# from the actual character-sheet code)
# ===========================================================================

_GENERIC_SKILLS = [
    Skill.PERCEPTION,
    Skill.INSIGHT,
    Skill.STEALTH,
    Skill.ATHLETICS,
    Skill.ARCANA,
    Skill.SURVIVAL,
    Skill.PERSUASION,
]


def make_dummy_stat_block(
    character_class: CharacterClass, spell_ability: Ability, level: int = 20
) -> CharacterStatBlock:
    return CharacterStatBlock(
        name="Preview Character",
        character_subclass="",
        base_class=character_class,
        level_per_class={character_class: level},
        abilities=AbilitiesStatBlock(16, 14, 14, 14, 14, 12),
        skills=SkillsStatBlock(),
        combat=CombatStatBlock(speed=30, size=CreatureSize.MEDIUM),
        saving_throws=SavingThrowsStatBlock(),
        spell_casting_ability=spell_ability,
        spell_slots={1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
        class_by_character_level={lvl: character_class for lvl in range(1, level + 1)},
    )


def _auto_fill_args(cls: type, skill_overrides: Optional[dict] = None) -> dict:
    sig = inspect.signature(cls.__init__)
    kwargs = {}
    skill_idx = 0
    for pname, param in list(sig.parameters.items())[1:]:
        if param.default is not inspect.Parameter.empty:
            continue
        ann = param.annotation
        if skill_overrides and pname in skill_overrides:
            kwargs[pname] = skill_overrides[pname]
        elif ann is Skill:
            kwargs[pname] = _GENERIC_SKILLS[skill_idx % len(_GENERIC_SKILLS)]
            skill_idx += 1
        elif isinstance(ann, type) and issubclass(ann, Enum):
            kwargs[pname] = list(ann)[0]
        else:
            raise TypeError(
                f"cannot auto-fill required parameter '{pname}' of type {ann!r}"
            )
    return kwargs


def _instantiate_feature(cls: type):
    """Instantiate a Feature, brute-forcing Skill-typed args against every Skill
    if the class rejects our generic guesses (some features restrict skills to a
    class/domain-specific pool)."""
    kwargs = _auto_fill_args(cls)
    try:
        return cls(**kwargs)
    except Exception:
        pass

    sig = inspect.signature(cls.__init__)
    skill_params = [
        pname
        for pname, param in list(sig.parameters.items())[1:]
        if param.default is inspect.Parameter.empty and param.annotation is Skill
    ]
    if not skill_params:
        raise

    from itertools import permutations

    for combo in permutations(list(Skill), len(skill_params)):
        overrides = dict(zip(skill_params, combo))
        try:
            return cls(**_auto_fill_args(cls, overrides))
        except Exception:
            continue
    raise TypeError(f"no valid skill combination found for {cls.__name__}")


# Features whose constructor args can't be meaningfully auto-filled (e.g. Wild
# Shape's known_forms is a list of monster stat block classes) get a hand-written
# card instead of being skipped silently.
MANUAL_FEATURE_HTML: dict[tuple[str, str], str] = {
    (
        "CharacterContent.Features.ClassFeatures.Druid.DruidFeatures",
        "WildShape",
    ): (
        "<div class='feature-card'><div class='feature-header'>"
        "<span class='feature-name'>Wild Shape</span>"
        "<span class='feature-origin'>Druid Level 2</span></div><div class='feature-body'>"
        "<p>As a Bonus Action, you can magically assume the shape of a Beast you know (your Druid "
        "level caps the Beast's Challenge Rating and whether it can fly or swim — see the Wild Shape "
        "table in the rulebook). While shape-shifted you use the Beast's game statistics except mental "
        "ability scores, personality, and Intelligence/Wisdom/Charisma-based skills, which stay your "
        "own; the transformation lasts until you choose to end it, drop to 0 Hit Points in Beast form, "
        "or use this feature again.</p>"
        "<p>You can use this feature twice, gaining a third use at level 6 and a fourth at level 17. "
        "You regain one expended use per Short Rest and all uses on a Long Rest.</p>"
        "</div></div>\n"
    ),
    (
        "CharacterContent.Features.ClassFeatures.Druid.DruidFeatures",
        "AdditionalWildShapeForms",
    ): (
        "<div class='feature-card'><div class='feature-header'>"
        "<span class='feature-name'>Additional Known Forms</span>"
        "<span class='feature-origin'>Druid</span></div><div class='feature-body'>"
        "<p>At higher levels, and through certain Circle subclass features, you learn additional "
        "Beast forms you can assume with Wild Shape.</p></div></div>\n"
    ),
}


def collect_features(
    module_path: str, stat_block: CharacterStatBlock
) -> list[tuple[int, str]]:
    """Returns (sort_level, rendered_html) pairs for every Feature class defined
    directly in the given module."""
    module = importlib.import_module(module_path)
    entries: list[tuple[int, str]] = []
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ != module.__name__:
            continue
        if not issubclass(cls, Feature) or cls is Feature:
            continue

        override_key = (module_path, cls.__name__)
        if override_key in MANUAL_FEATURE_HTML:
            html = MANUAL_FEATURE_HTML[override_key]
            match = re.search(r"Level\s+(\d+)", html)
            entries.append((int(match.group(1)) if match else 999, html))
            continue

        try:
            feature = _instantiate_feature(cls)
        except Exception as exc:
            print(f"    [skip] {module_path}.{cls.__name__}: {exc}")
            continue

        match = re.search(r"Level\s+(\d+)", feature.origin or "")
        level = int(match.group(1)) if match else 999
        entries.append((level, render_feature_card(feature, stat_block)))

    entries.sort(key=lambda pair: pair[0])
    return entries


def render_feature_card(feature: Feature, stat_block: CharacterStatBlock) -> str:
    try:
        buf = io.StringIO()
        feature.write_to_file(stat_block, buf)
        html = buf.getvalue()
        if html:
            return html
    except Exception as exc:
        print(f"    [render-fail] {feature.name}: {exc}")

    return (
        "<div class='feature-card'><div class='feature-header'>"
        f"<span class='feature-name'>{feature.name}</span>"
        f"<span class='feature-origin'>{feature.origin or ''}</span>"
        "</div><div class='feature-body'><p><em>Could not render automatically — "
        "see the full rulebook entry.</em></p></div></div>\n"
    )


# ===========================================================================
# HTML page assembly
# ===========================================================================

PAGE_CSS = """
        .page-nav { margin-bottom: 1rem; }
        .page-nav a { color: #6a4a20; text-decoration: none; font-size: 0.9rem; }
        .page-nav a:hover { text-decoration: underline; }

        .class-flavor p { font-style: italic; color: var(--muted-color); }

        .mechanical-summary {
            background: #f4ede0;
            border-left: 4px solid #9a7040;
            border-radius: 0 4px 4px 0;
            padding: 0.7rem 1rem;
            margin: 0.8rem 0 1.2rem 0;
        }
        .mechanical-summary-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6a4a20;
            margin-bottom: 0.3rem;
        }
        .subclass-mechanical-summary {
            font-size: 0.92rem;
            padding: 0.5rem 0.8rem;
            margin: 0.5rem 0 1rem 0;
        }

        .subclass-section {
            border-top: 3px double #9a7040;
            margin-top: 2rem;
            padding-top: 1rem;
        }
        .subclass-flavor-note {
            font-size: 0.78rem;
            color: var(--muted-color);
            font-style: italic;
        }

        .toc { columns: 2; margin: 1rem 0; }
        .toc a { color: #4a3020; }

        .edition-badge {
            display: inline-block;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            margin-left: 0.5rem;
            vertical-align: middle;
        }
        .edition-2024 {
            background: #e8d4b8;
            color: #6a4a20;
            border: 1px solid #9a7040;
        }
        .edition-2014 {
            background: #d4c5b9;
            color: #5a3a10;
            border: 1px solid #8a6030;
        }

        h1, h2, h3 { color: #4a3020; }
        h2 { border-bottom: 1px solid #b89060; padding-bottom: 0.2rem; }
"""


def _page_shell(title: str, body: str) -> str:
    style = Html.render_style_block(
        Html.BASE_CHARACTER_SHEET_CSS, FEATURE_CARD_CSS, PAGE_CSS
    )
    return (
        "<!doctype html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'/>\n"
        f"<title>{title}</title>\n{style}\n</head>\n<body>\n<div>\n{body}\n</div>\n</body>\n</html>\n"
    )


def _flavor_html(paragraphs: list[str]) -> str:
    return (
        "\n".join(f"<p>{p}</p>" for p in paragraphs)
        or "<p><em>No flavor text on file.</em></p>"
    )


def build_class_page(info: ClassInfo) -> str:
    print(f"  building {info.name}...")
    flavor = parse_class_flavor(info.text_file)
    summary = CLASS_SUMMARIES[info.name]
    stat_block = make_dummy_stat_block(info.character_class, info.spell_ability)

    class_module = (
        f"CharacterContent.Features.ClassFeatures.{info.name}.{info.name}Features"
    )
    class_features = collect_features(class_module, stat_block)
    class_feature_html = "\n".join(html for _, html in class_features)

    subclass_html_parts = []
    toc_parts = []
    for sub in SUBCLASSES.get(info.name, []):
        anchor = re.sub(r"[^a-z0-9]+", "-", sub.display_name.lower()).strip("-")
        toc_parts.append(
            f"<li><a href='#{anchor}'>{sub.display_name} "
            f"<span class='edition-badge edition-2024'>2024</span></a></li>"
        )

        sub_flavor = parse_subclass_flavor(sub)
        edition_note = (
            ""
            if sub.flavor_edition == "2024"
            else "<p class='subclass-flavor-note'>(Flavor text from the 2014 sourcebook — "
            "no 2024-specific write-up exists yet; the features below are the 2024-rules "
            "mechanics.)</p>"
        )

        sub_module = f"CharacterContent.Features.SubClassFeatures.{info.name}.{sub.py_stem}Features"
        sub_features = collect_features(sub_module, stat_block)
        sub_feature_html = "\n".join(html for _, html in sub_features)

        sub_summary = SUBCLASS_SUMMARIES.get(sub.py_stem)
        if sub_summary is None:
            print(f"    [warn] no mechanical summary for {sub.py_stem}")
            sub_summary_html = ""
        else:
            sub_summary_html = (
                "<div class='mechanical-summary subclass-mechanical-summary'>"
                "<span class='mechanical-summary-label'>How it plays, mechanically</span>"
                f"{sub_summary}</div>\n"
            )

        subclass_html_parts.append(
            f"<div class='subclass-section' id='{anchor}'>\n"
            f"<h3>{sub.display_name} <span class='edition-badge edition-2024'>2024</span></h3>\n"
            f"{edition_note}\n"
            f"<div class='class-flavor'>{_flavor_html(sub_flavor)}</div>\n"
            f"{sub_summary_html}"
            f"{sub_feature_html}\n"
            "</div>\n"
        )

    # Legacy 2014 subclasses section
    legacy_subclass_html_parts = []
    legacy_toc_parts = []
    legacy_subclasses = LEGACY_2014_SUBCLASSES.get(info.name, [])
    if legacy_subclasses:
        for sub in legacy_subclasses:
            anchor = re.sub(r"[^a-z0-9]+", "-", sub.display_name.lower()).strip("-")
            legacy_toc_parts.append(
                f"<li><a href='#{anchor}'>{sub.display_name} "
                f"<span class='edition-badge edition-2014'>2014</span></a></li>"
            )

            sub_flavor = parse_subclass_flavor(sub)
            sub_module = f"CharacterContent.Features.SubClassFeatures2014.{info.name}.{sub.py_stem}Features"
            sub_features = collect_features(sub_module, stat_block)
            sub_feature_html = "\n".join(html for _, html in sub_features)

            sub_summary = SUBCLASS_SUMMARIES_2014.get(sub.py_stem)
            if sub_summary is None:
                print(f"    [warn] no mechanical summary for {sub.py_stem}")
                sub_summary_html = ""
            else:
                sub_summary_html = (
                    "<div class='mechanical-summary subclass-mechanical-summary'>"
                    "<span class='mechanical-summary-label'>How it plays, mechanically</span>"
                    f"{sub_summary}</div>\n"
                )

            legacy_subclass_html_parts.append(
                f"<div class='subclass-section' id='{anchor}'>\n"
                f"<h3>{sub.display_name} <span class='edition-badge edition-2014'>2014</span></h3>\n"
                f"<div class='class-flavor'>{_flavor_html(sub_flavor)}</div>\n"
                f"{sub_summary_html}"
                f"{sub_feature_html}\n"
                "</div>\n"
            )

    legacy_section = ""
    if legacy_subclasses:
        legacy_section = (
            f"\n<h2>Legacy Subclasses (2014 Rules)</h2>\n"
            f"<p>These come from the original 2014 ruleset and were not carried forward into the 2024 "
            f"rulebook's subclass lineup above.</p>\n"
            f"<ul class='toc'>{''.join(legacy_toc_parts)}</ul>\n"
            f"{''.join(legacy_subclass_html_parts)}\n"
        )

    body = (
        f"<div class='page-nav'><a href='index.html'>← All Classes</a></div>\n"
        f"<h1>{info.name}</h1>\n"
        f"<div class='class-flavor'>{_flavor_html(flavor)}</div>\n"
        "<div class='mechanical-summary'>"
        "<span class='mechanical-summary-label'>How it plays, mechanically</span>"
        f"{summary}</div>\n"
        f"<h2>{info.name} Class Features</h2>\n"
        f"{class_feature_html}\n"
        f"<h2>Subclasses</h2>\n"
        f"<ul class='toc'>{''.join(toc_parts)}</ul>\n"
        f"{''.join(subclass_html_parts)}\n"
        f"{legacy_section}"
    )
    return _page_shell(f"{info.name} — Class Handout", body)


def build_index_page() -> str:
    items = []
    for info in CLASSES:
        subclass_names = ", ".join(
            s.display_name for s in SUBCLASSES.get(info.name, [])
        )
        items.append(
            f"<li><a href='{info.name.lower()}.html'><strong>{info.name}</strong></a>"
            f"<br/><span class='subclass-flavor-note'>{subclass_names}</span></li>"
        )
    body = (
        "<h1>Class Handouts</h1>\n"
        "<p>Flavor text, full feature text, and a mechanical summary for every class and its "
        "2024-rules subclasses. Click a class to read more.</p>\n"
        f"<ul class='toc'>{''.join(items)}</ul>\n"
    )
    return _page_shell("Class Handouts", body)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating class handouts...")
    for info in CLASSES:
        html = build_class_page(info)
        out_path = OUTPUT_DIR / f"{info.name.lower()}.html"
        out_path.write_text(html, encoding="utf-8")

    (OUTPUT_DIR / "index.html").write_text(build_index_page(), encoding="utf-8")
    print(f"Done. Open {OUTPUT_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
