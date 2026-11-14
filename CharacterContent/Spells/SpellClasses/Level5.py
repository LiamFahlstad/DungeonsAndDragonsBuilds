"""Level 5 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import (
    ClassSpell,
    RecordStamp,
    SpellRules,
)
from CharacterContent.Spells.SpellFactory.Enums import (
    CastingTimeType,
    DurationType,
    RangeType,
    School,
)
from CharacterContent.Spells.SpellFactory.SpellFields import (
    CastingTime,
    Components,
    Duration,
    Range,
)
from Core.Definitions import CharacterClass
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class AlustrielsMooncloak(ClassSpell):
    rules = SpellRules(
        name="Alustriel's Mooncloak",
        level=5,
        school=School.ABJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.DRUID,
            CharacterClass.RANGER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a moonstone worth 50+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "For the duration, moonlight fills a 20-foot Emanation originating from you with Dim Light. While in that area, you and your allies have Half Cover and Resistance to Cold, Lightning, and Radiant damage.\n"
            "While the spell lasts, you can use one of the following options, ending the spell immediately:\n"
            "Liberation. When you fail a saving throw to avoid or end the Frightened, Grappled, or Restrained condition, you can take a Reaction to succeed on the save instead.\n"
            "Respite. As a Magic action, you or an ally within the area regains Hit Points equal to 4d10 plus your spellcasting ability modifier."
        ),
        usage_tags=("buff", "heal"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5891c78a7fd1780a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "20-foot Emanation originating from you, filled with Dim Light by moonlight for the duration",
                    ),
                    (
                        "In the area",
                        "You and your allies have Half Cover and Resistance to Cold, Lightning, and Radiant damage",
                    ),
                    (
                        "Options",
                        "While the spell lasts, you can use one of the following options, ending the spell immediately",
                    ),
                )
            ),
            Table(
                ("Option", "Effect"),
                (
                    (
                        "Liberation",
                        "When you fail a saving throw to avoid or end the Frightened, Grappled, or Restrained condition, you can take a Reaction to succeed on the save instead",
                    ),
                    (
                        "Respite",
                        "As a Magic action, you or an ally within the area regains Hit Points equal to 4d10 plus your spellcasting ability modifier",
                    ),
                ),
            ),
        ]


class AnimateObjects(ClassSpell):
    rules = SpellRules(
        name="Animate Objects",
        level=5,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Objects animate at your command. Choose a number of nonmagical objects within range that aren’t being worn or carried, aren’t fixed to a surface, and aren’t Gargantuan. The maximum number of objects is equal to your spellcasting ability modifier; for this number, a Medium or smaller target counts as one object, a Large target counts as two, and a Huge target counts as three.\n"
            "Each target animates, sprouts legs, and becomes a Construct that uses the Animated Object stat block; this creature is under your control until the spell ends or until it is reduced to 0 Hit Points. Each creature you make with this spell is an ally to you and your allies. In combat, it shares your Initiative count and takes its turn immediately after yours.\n"
            "Until the spell ends, you can take a Bonus Action to mentally command any creature you made with this spell if the creature is within 500 feet of you (if you control multiple creatures, you can command any of them at the same time, issuing the same command to each one). If you issue no commands, the creature takes the Dodge action and moves only to avoid harm. When the creature drops to 0 Hit Points, it reverts to its object form, and any remaining damage carries over to that form.\n"
            "Using a Higher-Level Spell Slot. The creature’s Slam damage increases by 1d4 (Medium or smaller), 1d6 (Large), or 1d12 (Huge) for each spell slot level above 5."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f327fd185f762d72")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "A number of nonmagical objects within range that aren't being worn or carried, aren't fixed to a surface, and aren't Gargantuan",
                    ),
                    (
                        "Maximum",
                        "The maximum number of objects is equal to your spellcasting ability modifier; for this number, a Medium or smaller target counts as one object, a Large target counts as two, and a Huge target counts as three",
                    ),
                    (
                        "Result",
                        "Each target animates, sprouts legs, and becomes a Construct that uses the Animated Object stat block (below)",
                    ),
                    (
                        "Control",
                        "This creature is under your control until the spell ends or until it is reduced to 0 Hit Points",
                    ),
                    (
                        "At 0 Hit Points",
                        "The creature reverts to its object form, and any remaining damage carries over to that form",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            (
                                "Allegiance",
                                "Each creature you make with this spell is an ally to you and your allies",
                            ),
                            (
                                "Initiative",
                                "In combat, it shares your Initiative count and takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "Until the spell ends, you can take a Bonus Action to mentally command any creature you made with this spell if the creature is within 500 feet of you (if you control multiple creatures, you can command any of them at the same time, issuing the same command to each one)",
                            ),
                            (
                                "No command",
                                "If you issue no commands, the creature takes the Dodge action and moves only to avoid harm",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Animated Object",
                (
                    Facts(
                        (
                            ("Type", "Construct (Medium or smaller, Large, or Huge)"),
                            ("AC", "15"),
                            (
                                "Hit Points",
                                "10 (Medium or smaller); the Large and Huge values aren't included in this spell's data",
                            ),
                            ("Speed", "30 ft."),
                            (
                                "Abilities",
                                "Str 16, Dex 10, Con 10, Int 3, Wis 3, Cha 1",
                            ),
                            (
                                "Immunities",
                                "Poison, Psychic; Charmed, Exhaustion, Frightened, Paralyzed, Poisoned",
                            ),
                            ("Senses", "Blindsight 30 ft., Passive Perception 6"),
                            ("Languages", "Understands the languages you know"),
                            (
                                "Slam",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: Force damage equal to 1d4 + 3 (Medium or smaller), 2d6 + 3 + your spellcasting ability modifier (Large), or 2d12 + 3 + your spellcasting ability modifier (Huge)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Slam damage",
                                "The creature's Slam damage increases by 1d4 (Medium or smaller), 1d6 (Large), or 1d12 (Huge) for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class AntilifeShell(ClassSpell):
    rules = SpellRules(
        name="Antilife Shell",
        level=5,
        school=School.ABJURATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "An aura extends from you in a 10-foot Emanation for the duration. The aura prevents creatures other than Constructs and Undead from passing or reaching through it. An affected creature can cast spells or make attacks with Ranged or Reach weapons through the barrier.\n"
            "If you move so that an affected creature is forced to pass through the barrier, the spell ends."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c8baf4c782d59407")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "An aura extends from you in a 10-foot Emanation for the duration",
                    ),
                    (
                        "Barrier",
                        "The aura prevents creatures other than Constructs and Undead from passing or reaching through it",
                    ),
                    (
                        "Exception",
                        "An affected creature can cast spells or make attacks with Ranged or Reach weapons through the barrier",
                    ),
                    (
                        "Ends early",
                        "If you move so that an affected creature is forced to pass through the barrier, the spell ends",
                    ),
                )
            )
        ]


class Awaken(ClassSpell):
    rules = SpellRules(
        name="Awaken",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.BARD, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.HOUR, 8),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="an agate worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You spend the casting time tracing magical pathways within a precious gemstone, and then touch the target. The target must be either a Beast or Plant creature with an Intelligence of 3 or less or a natural plant that isn’t a creature. The target gains an Intelligence of 10 and the ability to speak one language you know. If the target is a natural plant, it becomes a Plant creature and gains the ability to move its limbs, roots, vines, creepers, and so forth, and it gains senses similar to a human’s. The DM chooses statistics appropriate for the awakened Plant, such as the statistics for the Awakened Shrub or Awakened Tree in the Monster Manual.\n"
            "The awakened target has the Charmed condition for 30 days or until you or your allies deal damage to it. When that condition ends, the awakened creature chooses its attitude toward you."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c30aa050d92ab5d0")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Casting",
                        "You spend the casting time tracing magical pathways within a precious gemstone, and then touch the target",
                    ),
                    (
                        "Target",
                        "Either a Beast or Plant creature with an Intelligence of 3 or less or a natural plant that isn't a creature",
                    ),
                    (
                        "Effect",
                        "The target gains an Intelligence of 10 and the ability to speak one language you know",
                    ),
                    (
                        "Natural plant",
                        "If the target is a natural plant, it becomes a Plant creature and gains the ability to move its limbs, roots, vines, creepers, and so forth, and it gains senses similar to a human's",
                    ),
                    (
                        "Statistics",
                        "The DM chooses statistics appropriate for the awakened Plant, such as the statistics for the Awakened Shrub or Awakened Tree in the Monster Manual",
                    ),
                    (
                        "Charmed",
                        "The awakened target has the Charmed condition for 30 days or until you or your allies deal damage to it",
                    ),
                    (
                        "Attitude",
                        "When that condition ends, the awakened creature chooses its attitude toward you",
                    ),
                )
            )
        ]


class BanishingSmite(ClassSpell):
    rules = SpellRules(
        name="Banishing Smite",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(
            CastingTimeType.BONUS_ACTION,
            trigger="which you take immediately after hitting a creature with a Melee weapon or an Unarmed Strike",
        ),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="The target hit by the attack roll takes an extra 5d10 Force damage from the attack. If the attack reduces the target to 50 Hit Points or fewer, the target must succeed on a Charisma saving throw or be transported to a harmless demiplane for the duration. While there, the target has the Incapacitated condition. When the spell ends, the target reappears in the space it left or in the nearest unoccupied space if that space is occupied.",
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6bd618d7ddb717ae")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "Immediately after hitting a creature with a Melee weapon or an Unarmed Strike",
                    ),
                    (
                        "Damage",
                        "The target hit by the attack roll takes an extra 5d10 Force damage from the attack",
                    ),
                    (
                        "Threshold",
                        "If the attack reduces the target to 50 Hit Points or fewer, it must make the save below",
                    ),
                    ("Save", "Charisma"),
                    (
                        "Failed save",
                        "Transported to a harmless demiplane for the duration; while there, the target has the Incapacitated condition",
                    ),
                    ("Successful save", "Not transported to the demiplane"),
                    (
                        "Spell ends",
                        "The target reappears in the space it left or in the nearest unoccupied space if that space is occupied",
                    ),
                )
            )
        ]


class BigbysHand(ClassSpell):
    rules = SpellRules(
        name="Bigby's Hand",
        level=5,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="an eggshell and a glove"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a Large hand of shimmering magical energy in an unoccupied space that you can see within range. The hand lasts for the duration, and it moves at your command, mimicking the movements of your own hand.\n"
            "The hand is an object that has AC 20 and Hit Points equal to your Hit Point maximum. If it drops to 0 Hit Points, the spell ends. The hand doesn’t occupy its space.\n"
            "When you cast the spell and as a Bonus Action on your later turns, you can move the hand up to 60 feet and then cause one of the following effects:\n"
            "Clenched Fist. The hand strikes a target within 5 feet of it. Make a melee spell attack. On a hit, the target takes 5d8 Force damage.\n"
            "Forceful Hand. The hand attempts to push a Huge or smaller creature within 5 feet of it. The target must succeed on a Strength saving throw, or the hand pushes the target up to 5 feet plus a number of feet equal to five times your spellcasting ability modifier. The hand moves with the target, remaining within 5 feet of it.\n"
            "Grasping Hand. The hand attempts to grapple a Huge or smaller creature within 5 feet of it. The target must succeed on a Dexterity saving throw, or the target has the Grappled condition, with an escape DC equal to your spell save DC. While the hand grapples the target, you can take a Bonus Action to cause the hand to crush it, dealing Bludgeoning damage to the target equal to 4d6 plus your spellcasting ability modifier.\n"
            "Interposing Hand. The hand grants you Half Cover against attacks and other effects that originate from its space or that pass through it. In addition, its space counts as Difficult Terrain for your enemies.\n"
            "Using a Higher-Level Spell Slot. The damage of the Clenched Fist increases by 2d8 and the damage of the Grasping Hand increases by 2d6 for each spell slot level above 5."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a9c84cd36e017181")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You create a Large hand of shimmering magical energy in an unoccupied space that you can see within range.",
                    ),
                    ("Size", "Large"),
                    (
                        "Appears",
                        "In an unoccupied space that you can see within range; the hand lasts for the duration, and it moves at your command, mimicking the movements of your own hand",
                    ),
                    (
                        "The hand",
                        "An object that has AC 20 and Hit Points equal to your Hit Point maximum; it doesn't occupy its space",
                    ),
                    ("Ends early", "If it drops to 0 Hit Points, the spell ends"),
                    (
                        "Moving",
                        "When you cast the spell and as a Bonus Action on your later turns, you can move the hand up to 60 feet and then cause one of the following effects",
                    ),
                )
            ),
            Option(
                "Clenched Fist",
                (
                    Facts(
                        (
                            ("Target", "A target within 5 feet of the hand"),
                            ("Attack", "Melee spell attack"),
                            ("On a hit", "5d8 Force damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Forceful Hand",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "A Huge or smaller creature within 5 feet of the hand; the hand attempts to push it",
                            ),
                            ("Save", "Strength"),
                            (
                                "Failed save",
                                "The hand pushes the target up to 5 feet plus a number of feet equal to five times your spellcasting ability modifier; the hand moves with the target, remaining within 5 feet of it",
                            ),
                            ("Successful save", "No effect"),
                        )
                    ),
                ),
            ),
            Option(
                "Grasping Hand",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "A Huge or smaller creature within 5 feet of the hand; the hand attempts to grapple it",
                            ),
                            ("Save", "Dexterity"),
                            (
                                "Failed save",
                                "The target has the Grappled condition, with an escape DC equal to your spell save DC",
                            ),
                            ("Successful save", "No effect"),
                            (
                                "Crush",
                                "While the hand grapples the target, you can take a Bonus Action to cause the hand to crush it, dealing Bludgeoning damage to the target equal to 4d6 plus your spellcasting ability modifier",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Interposing Hand",
                (
                    Facts(
                        (
                            (
                                "Cover",
                                "The hand grants you Half Cover against attacks and other effects that originate from its space or that pass through it",
                            ),
                            (
                                "Terrain",
                                "In addition, its space counts as Difficult Terrain for your enemies",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Clenched Fist",
                                "Damage increases by 2d8 for each spell slot level above 5",
                            ),
                            (
                                "Grasping Hand",
                                "Damage increases by 2d6 for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class CircleOfPower(ClassSpell):
    rules = SpellRules(
        name="Circle of Power",
        level=5,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.PALADIN,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description="An aura radiates from you in a 30-foot Emanation for the duration. While in the aura, you and your allies have Advantage on saving throws against spells and other magical effects. When an affected creature makes a saving throw against a spell or magical effect that allows a save to take only half damage, it takes no damage if it succeeds on the save.",
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f38a2720c00e15ef")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "An aura radiates from you in a 30-foot Emanation for the duration",
                    ),
                    (
                        "Advantage",
                        "While in the aura, you and your allies have Advantage on saving throws against spells and other magical effects",
                    ),
                    (
                        "No damage",
                        "When an affected creature makes a saving throw against a spell or magical effect that allows a save to take only half damage, it takes no damage if it succeeds on the save",
                    ),
                )
            )
        ]


class Cloudkill(ClassSpell):
    rules = SpellRules(
        name="Cloudkill",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You create a 20-foot-radius Sphere of yellow-green fog centered on a point within range. The fog lasts for the duration or until strong wind (such as the one created by Gust of Wind) disperses it, ending the spell. Its area is Heavily Obscured.\n"
            "Each creature in the Sphere makes a Constitution saving throw, taking 5d8 Poison damage on a failed save or half as much damage on a successful one. A creature must also make this save when the Sphere moves into its space and when it enters the Sphere or ends its turn there. A creature makes this save only once per turn.\n"
            "The Sphere moves 10 feet away from you at the start of each of your turns.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 5."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0ac70055d6bd3530")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "20-foot-radius Sphere of yellow-green fog centered on a point within range",
                    ),
                    ("Visibility", "The Sphere's area is Heavily Obscured"),
                    (
                        "Ends early",
                        "Strong wind (such as the one created by Gust of Wind) disperses the fog, ending the spell",
                    ),
                    (
                        "Moving",
                        "The Sphere moves 10 feet away from you at the start of each of your turns",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in the Sphere, and also when the Sphere moves into a creature's space and when a creature enters the Sphere or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("5d8 Poison damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 5"),)),),
            ),
        ]


class Commune(ClassSpell):
    rules = SpellRules(
        name="Commune",
        level=5,
        school=School.DIVINATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="incense"),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "You contact a deity or a divine proxy and ask up to three questions that can be answered with yes or no. You must ask your questions before the spell ends. You receive a correct answer for each question.\n"
            "Divine beings aren't necessarily omniscient, so you might receive “unclear” as an answer if a question pertains to information that lies beyond the deity’s knowledge. In a case where a one-word answer could be misleading or contrary to the deity’s interests, the DM might offer a short phrase as an answer instead.\n"
            "If you cast the spell more than once before finishing a Long Rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a84630d6c1130581")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Contact", "You contact a deity or a divine proxy"),
                    (
                        "Questions",
                        "Up to three questions that can be answered with yes or no; you must ask your questions before the spell ends",
                    ),
                    ("Answers", "You receive a correct answer for each question"),
                    (
                        "Unclear",
                        "Divine beings aren't necessarily omniscient, so you might receive \"unclear\" as an answer if a question pertains to information that lies beyond the deity's knowledge",
                    ),
                    (
                        "Short phrase",
                        "In a case where a one-word answer could be misleading or contrary to the deity's interests, the DM might offer a short phrase as an answer instead",
                    ),
                    (
                        "Recasting",
                        "If you cast the spell more than once before finishing a Long Rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer",
                    ),
                )
            )
        ]


class CommuneWithNature(ClassSpell):
    rules = SpellRules(
        name="Commune with Nature",
        level=5,
        school=School.DIVINATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You commune with nature spirits and gain knowledge of the surrounding area. In the outdoors, the spell gives you knowledge of the area within 3 miles of you. In caves and other natural underground settings, the radius is limited to 300 feet. The spell doesn't function where nature has been replaced by construction, such as in castles and settlements.\n"
            "Choose three of the following facts; you learn those facts as they pertain to the spell's area:\n"
            "Locations of settlements\n"
            "Locations of portals to other planes of existence\n"
            "Location of one Challenge Rating 10+ creature (DM’s choice) that is a Celestial, an Elemental, a Fey, a Fiend, or an Undead\n"
            "The most prevalent kind of plant, mineral, or Beast (you choose which to learn)\n"
            "Locations of bodies of water\n"
            "For example, you could determine the location of a powerful monster in the area, the locations of bodies of water, and the locations of any towns."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "51cc53c5e132cc30")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Effect",
                        "You commune with nature spirits and gain knowledge of the surrounding area",
                    ),
                    (
                        "Outdoors",
                        "The spell gives you knowledge of the area within 3 miles of you",
                    ),
                    (
                        "Underground",
                        "In caves and other natural underground settings, the radius is limited to 300 feet",
                    ),
                    (
                        "Doesn't function",
                        "Where nature has been replaced by construction, such as in castles and settlements",
                    ),
                    (
                        "Choose",
                        "Choose three of the following facts; you learn those facts as they pertain to the spell's area",
                    ),
                )
            ),
            Table(
                ("Facts",),
                (
                    ("Locations of settlements",),
                    ("Locations of portals to other planes of existence",),
                    (
                        "Location of one Challenge Rating 10+ creature (DM's choice) that is a Celestial, an Elemental, a Fey, a Fiend, or an Undead",
                    ),
                    (
                        "The most prevalent kind of plant, mineral, or Beast (you choose which to learn)",
                    ),
                    ("Locations of bodies of water",),
                ),
            ),
            Facts(
                (
                    (
                        "Example",
                        "You could determine the location of a powerful monster in the area, the locations of bodies of water, and the locations of any towns",
                    ),
                )
            ),
        ]


class ConeOfCold(ClassSpell):
    rules = SpellRules(
        name="Cone of Cold",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a small crystal or glass cone"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You unleash a blast of cold air. Each creature in a 60-foot Cone originating from you makes a Constitution saving throw, taking 8d8 Cold damage on a failed save or half as much damage on a successful one. A creature killed by this spell becomes a frozen statue until it thaws.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 5."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d8c4a73b64cdc730")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You unleash a blast of cold air."),
                    ("Area", "60-foot Cone originating from you"),
                    ("Save", "Constitution, made by each creature in the Cone"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d8 Cold damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Killed",
                        "A creature killed by this spell becomes a frozen statue until it thaws",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 5"),)),),
            ),
        ]


class ConjureElemental(ClassSpell):
    rules = SpellRules(
        name="Conjure Elemental",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You conjure a Large, intangible spirit from the Elemental Planes that appears in an unoccupied space within range. Choose the spirit’s element, which determines its damage type: air (Lightning), earth (Thunder), fire (Fire), or water (Cold). The spirit lasts for the duration.\n"
            "Whenever a creature you can see enters the spirit’s space or starts its turn within 5 feet of the spirit, you can force that creature to make a Dexterity saving throw if the spirit has no creature Restrained. On failed save, the target takes 8d8 damage of the spirit’s type, and the target has the Restrained condition until the spell ends. At the start of each of its turns, the Restrained target repeats the save. On a failed save, the target takes 4d8 damage of the spirit’s type. On a successful save, the target isn’t Restrained by the spirit.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 5."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "08b95d49e98b822b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You conjure a Large, intangible spirit from the Elemental Planes."
            ),
            Facts(
                (
                    ("Appears", "In an unoccupied space within range"),
                    (
                        "Element",
                        "Choose the spirit's element, which determines its damage type",
                    ),
                )
            ),
            Table(
                ("Element", "Damage type"),
                (
                    ("Air", "Lightning"),
                    ("Earth", "Thunder"),
                    ("Fire", "Fire"),
                    ("Water", "Cold"),
                ),
            ),
            Facts(
                (
                    (
                        "Trigger",
                        "Whenever a creature you can see enters the spirit's space or starts its turn within 5 feet of the spirit, you can force that creature to make a Dexterity saving throw if the spirit has no creature Restrained",
                    ),
                    ("Save", "Dexterity"),
                    (
                        "Failed save",
                        "The target takes 8d8 damage of the spirit's type, and the target has the Restrained condition until the spell ends",
                    ),
                    ("Successful save", "No effect"),
                )
            ),
            Option(
                "Restrained Target",
                (
                    Facts(
                        (
                            (
                                "Repeat save",
                                "At the start of each of its turns, the Restrained target repeats the save",
                            ),
                            (
                                "Failed save",
                                "The target takes 4d8 damage of the spirit's type",
                            ),
                            (
                                "Successful save",
                                "The target isn't Restrained by the spirit",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d8 for each spell slot level above 5"),)),),
            ),
        ]


class ConjureVolley(ClassSpell):
    rules = SpellRules(
        name="Conjure Volley",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 150),
        components=Components(
            verbal=True,
            somatic=True,
            material="a Melee or Ranged weapon worth at least 1 CP",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="You brandish the weapon used to cast the spell and choose a point within range. Hundreds of similar spectral weapons (or ammunition appropriate to the weapon) fall in a volley and then disappear. Each creature of your choice that you can see in a 40-foot-radius, 20-foot-high Cylinder centered on that point makes a Dexterity saving throw. A creature takes 8d8 Force damage on a failed save or half as much damage on a successful one.",
        usage_tags=("damage",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0c33887bd163d0b7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Hundreds of similar spectral weapons (or ammunition appropriate to the weapon) fall in a volley and then disappear.",
                    ),
                    (
                        "Casting",
                        "You brandish the weapon used to cast the spell and choose a point within range",
                    ),
                    (
                        "Area",
                        "40-foot-radius, 20-foot-high Cylinder centered on that point",
                    ),
                    (
                        "Targets",
                        "Each creature of your choice that you can see in the Cylinder",
                    ),
                    ("Save", "Dexterity"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d8 Force damage", "Half as much damage"),),
            ),
        ]


class ContactOtherPlane(ClassSpell):
    rules = SpellRules(
        name="Contact Other Plane",
        level=5,
        school=School.DIVINATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1, ritual=True),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1),
        source="Player's Handbook",
        description=(
            "You mentally contact a demigod, the spirit of a long-dead sage, or some other knowledgeable entity from another plane. Contacting this otherworldly intelligence can break your mind. When you cast this spell, make a DC 15 Intelligence saving throw. On a successful save, you can ask the entity up to five questions. You must ask your questions before the spell ends. The DM answers each question with one word, such as “yes,” “no,” “maybe,” “never,” “irrelevant,” or “unclear” (if the entity doesn’t know the answer to the question). If a one-word answer would be misleading, the DM might instead offer a short phrase as an answer.\n"
            "On a failed save, you take 6d6 Psychic damage and have the Incapacitated condition until you finish a Long Rest. A Greater Restoration spell cast on you ends this effect."
        ),
        usage_tags=("control",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "89d5ca113373e3c9")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Contact",
                        "You mentally contact a demigod, the spirit of a long-dead sage, or some other knowledgeable entity from another plane",
                    ),
                    (
                        "Risk",
                        "Contacting this otherworldly intelligence can break your mind",
                    ),
                    (
                        "Save",
                        "Intelligence (DC 15), made by you when you cast this spell",
                    ),
                )
            ),
            Option(
                "Successful Save",
                (
                    Facts(
                        (
                            (
                                "Questions",
                                "You can ask the entity up to five questions; you must ask your questions before the spell ends",
                            ),
                            (
                                "Answers",
                                'The DM answers each question with one word, such as "yes," "no," "maybe," "never," "irrelevant," or "unclear" (if the entity doesn\'t know the answer to the question)',
                            ),
                            (
                                "Short phrase",
                                "If a one-word answer would be misleading, the DM might instead offer a short phrase as an answer",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Failed Save",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "You take 6d6 Psychic damage and have the Incapacitated condition until you finish a Long Rest",
                            ),
                            (
                                "Ends early",
                                "A Greater Restoration spell cast on you ends this effect",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Contagion(ClassSpell):
    rules = SpellRules(
        name="Contagion",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.DAY, 7),
        source="Player's Handbook",
        description=(
            "Your touch inflicts a magical contagion. The target must succeed on a Constitution saving throw or take 11d8 Necrotic damage and have the Poisoned condition. Also, choose one ability when you cast the spell. While Poisoned, the target has Disadvantage on saving throws made with the chosen ability.\n"
            "The target must repeat the saving throw at the end of each of its turns until it gets three successes or failures. If the target succeeds on three of these saves, the spell ends on the target. If the target fails three of the saves, the spell lasts for 7 days on it.\n"
            "Whenever the Poisoned target receives an effect that would end the Poisoned condition, the target must succeed on a Constitution saving throw, or the Poisoned condition doesn’t end on it."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "571594f4c50cddd4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Your touch inflicts a magical contagion."),
            Facts(
                (
                    ("Target", "A creature you touch"),
                    ("Save", "Constitution"),
                    (
                        "Failed save",
                        "The target takes 11d8 Necrotic damage and has the Poisoned condition",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Ability",
                        "Also, choose one ability when you cast the spell; while Poisoned, the target has Disadvantage on saving throws made with the chosen ability",
                    ),
                    (
                        "Repeat save",
                        "The target must repeat the saving throw at the end of each of its turns until it gets three successes or failures",
                    ),
                    ("Three successes", "The spell ends on the target"),
                    ("Three failures", "The spell lasts for 7 days on it"),
                    (
                        "Curing",
                        "Whenever the Poisoned target receives an effect that would end the Poisoned condition, the target must succeed on a Constitution saving throw, or the Poisoned condition doesn't end on it",
                    ),
                )
            ),
        ]


class ControlWinds(ClassSpell):
    rules = SpellRules(
        name="Control Winds",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You take control of the air in a 100-foot cube that you can see within range. Choose one of the following effects when you cast the spell. The effect lasts for the spell's duration, unless you use your action on a later turn to switch to a different effect. You can also use your action to temporarily halt the effect or to restart one you've halted.\n"
            "Gusts. A wind picks up within the cube, continually blowing in a horizontal direction that you choose. You choose the intensity of the wind: calm, moderate, or strong. If the wind is moderate or strong, ranged weapon attacks that pass through it or that are made against targets within the cube have disadvantage on their attack rolls. If the wind is strong, any creature moving against the wind must spend 1 extra foot of movement for each foot moved.\n"
            "Downdraft. You cause a sustained blast of strong wind to blow downward from the top of the cube. Ranged weapon attacks that pass through the cube or that are made against targets within it have disadvantage on their attack rolls. A creature must make a Strength saving throw if it flies into the cube for the first time on a turn or starts its turn there flying. On a failed save, the creature is knocked prone.\n"
            "Updraft. You cause a sustained updraft within the cube, rising upward from the cube's bottom edge. Creatures that end a fall within the cube take only half damage from the fall. When a creature in the cube makes a vertical jump, the creature can jump up to 10 feet higher than normal."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "9ea4ee838dc44728")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Area", "A 100-foot cube of air that you can see within range"),
                    (
                        "Effect",
                        "Choose one of the following effects when you cast the spell",
                    ),
                    (
                        "Lasts",
                        "The effect lasts for the spell's duration, unless you use your action on a later turn to switch to a different effect",
                    ),
                    (
                        "Halting",
                        "You can also use your action to temporarily halt the effect or to restart one you've halted",
                    ),
                )
            ),
            Option(
                "Gusts",
                (
                    Facts(
                        (
                            (
                                "Wind",
                                "A wind picks up within the cube, continually blowing in a horizontal direction that you choose",
                            ),
                            (
                                "Intensity",
                                "You choose the intensity of the wind: calm, moderate, or strong",
                            ),
                            (
                                "Ranged attacks",
                                "If the wind is moderate or strong, ranged weapon attacks that pass through it or that are made against targets within the cube have Disadvantage on their attack rolls",
                            ),
                            (
                                "Strong wind",
                                "If the wind is strong, any creature moving against the wind must spend 1 extra foot of movement for each foot moved",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Downdraft",
                (
                    Facts(
                        (
                            (
                                "Wind",
                                "A sustained blast of strong wind blows downward from the top of the cube",
                            ),
                            (
                                "Ranged attacks",
                                "Ranged weapon attacks that pass through the cube or that are made against targets within it have Disadvantage on their attack rolls",
                            ),
                            (
                                "Save",
                                "Strength, made by a creature if it flies into the cube for the first time on a turn or starts its turn there flying",
                            ),
                            ("Failed save", "The creature is knocked Prone"),
                            ("Successful save", "No effect"),
                        )
                    ),
                ),
            ),
            Option(
                "Updraft",
                (
                    Facts(
                        (
                            (
                                "Wind",
                                "A sustained updraft within the cube, rising upward from the cube's bottom edge",
                            ),
                            (
                                "Falling",
                                "Creatures that end a fall within the cube take only half damage from the fall",
                            ),
                            (
                                "Jumping",
                                "When a creature in the cube makes a vertical jump, the creature can jump up to 10 feet higher than normal",
                            ),
                        )
                    ),
                ),
            ),
        ]


class CreateSpelljammingHelm(ClassSpell):
    rules = SpellRules(
        name="Create Spelljamming Helm",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.ARTIFICER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a crystal rod worth at least 5000 gp, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Spelljammer: Adventures in Space - Astral Adventurer's Guide",
        description="Holding the rod used in the casting of the spell, you touch a Large or smaller chair that is unoccupied. The rod disappears, and the chair is transformed into a Spelljamming Helm .",
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "abccf5a4df5aaa28")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "A Large or smaller chair that is unoccupied, which you touch while holding the rod used in the casting of the spell",
                    ),
                    (
                        "Effect",
                        "The rod disappears, and the chair is transformed into a Spelljamming Helm",
                    ),
                )
            )
        ]


class Creation(ClassSpell):
    rules = SpellRules(
        name="Creation",
        level=5,
        school=School.ILLUSION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="a paintbrush"),
        duration=Duration(DurationType.SPECIAL),
        source="Player's Handbook",
        description=(
            "You pull wisps of shadow material from the Shadowfell to create an object within range. It is either an object of vegetable matter (soft goods, rope, wood, and the like) or mineral matter (stone, crystal, metal, and the like). The object must be no larger than a 5-foot Cube, and the object must be of a form and material that you have seen.\n"
            "The spell’s duration depends on the object’s material, as shown in the Materials table. If the object is composed of multiple materials, use the shortest duration. Using any object created by this spell as another spell’s Material component causes the other spell to fail.\n"
            "Using a Higher-Level Spell Slot. The Cube increases by 5 feet for each spell slot level above 5."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "a72d00cff174f7e1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You pull wisps of shadow material from the Shadowfell to create an object within range.",
                    ),
                    (
                        "Object",
                        "An object within range: either an object of vegetable matter (soft goods, rope, wood, and the like) or mineral matter (stone, crystal, metal, and the like)",
                    ),
                    (
                        "Size",
                        "No larger than a 5-foot Cube, and of a form and material that you have seen",
                    ),
                    (
                        "Duration",
                        "Depends on the object's material, as shown in the Materials table; if the object is composed of multiple materials, use the shortest duration",
                    ),
                )
            ),
            Table(
                ("Material", "Duration"),
                (
                    ("Vegetable matter", "24 hours"),
                    ("Stone or crystal", "12 hours"),
                    ("Precious metals", "1 hour"),
                    ("Gems", "10 minutes"),
                    ("Adamantine or mithral", "1 minute"),
                ),
            ),
            Facts(
                (
                    (
                        "Material component",
                        "Using any object created by this spell as another spell's Material component causes the other spell to fail",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Cube",
                                "Increases by 5 feet for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DanseMacabre(ClassSpell):
    rules = SpellRules(
        name="Danse Macabre",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Threads of dark power leap from your fingers to pierce up to five Small or Medium corpses you can see within range. Each corpse immediately stands up and becomes undead. You decide whether it is a zombie or a skeleton (the statistics for zombies and skeletons are in the Monster Manual), and it gains a bonus to its attack and damage rolls equal to your spellcasting ability modifier. You can use a bonus action to mentally command the creatures you make with this spell, issuing the same command to all of them. To receive the command, a creature must be within 60 feet of you. You decide what action the creatures will take and where they will move during their next turn, or you can issue a general command, such as to guard a chamber or passageway against your foes. If you issue no commands, the creatures do nothing except defend themselves against hostile creatures. Once given an order, the creatures continue to follow it until their task is complete.\n"
            "The creatures are under your control until the spell ends, after which they become inanimate once more.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 6th level or higher, you animate up to two additional corpses for each slot level above 5th."
        ),
        usage_tags=("buff", "control", "utility", "summon"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "411f373efae7ef81")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Threads of dark power leap from your fingers to pierce up to five Small or Medium corpses you can see within range.",
                    ),
                    (
                        "Targets",
                        "Up to five Small or Medium corpses you can see within range",
                    ),
                    ("Rising", "Each corpse immediately stands up and becomes undead"),
                    (
                        "Kind",
                        "You decide whether it is a zombie or a skeleton (the statistics for zombies and skeletons are in the Monster Manual), and it gains a bonus to its attack and damage rolls equal to your spellcasting ability modifier",
                    ),
                    (
                        "Control",
                        "The creatures are under your control until the spell ends, after which they become inanimate once more",
                    ),
                )
            ),
            Option(
                "Commanding",
                (
                    Facts(
                        (
                            (
                                "Command",
                                "You can use a bonus action to mentally command the creatures you make with this spell, issuing the same command to all of them",
                            ),
                            (
                                "Range",
                                "To receive the command, a creature must be within 60 feet of you",
                            ),
                            (
                                "Orders",
                                "You decide what action the creatures will take and where they will move during their next turn, or you can issue a general command, such as to guard a chamber or passageway against your foes",
                            ),
                            (
                                "No command",
                                "If you issue no commands, the creatures do nothing except defend themselves against hostile creatures",
                            ),
                            (
                                "Following",
                                "Once given an order, the creatures continue to follow it until their task is complete",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Corpses",
                                "You animate up to two additional corpses for each slot level above 5th",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Dawn(ClassSpell):
    rules = SpellRules(
        name="Dawn",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a sunburst pendant worth at least 100 gp",
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="The light of dawn shines down on a location you specify within range. Until the spell ends, a 30-foot-radius, 40-foot-high cylinder of bright light glimmers there. This light is sunlight. When the cylinder appears, each creature in it must make a Constitution saving throw, taking 4d10 radiant damage on a failed save, or half as much damage on a successful one. A creature must also make this saving throw whenever it ends its turn in the cylinder. If you're within 60 feet of the cylinder, you can move it up to 60 feet as a bonus action on your turn.",
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "7445f107e7850ede")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "The light of dawn shines down on a location you specify within range.",
                    ),
                    ("Location", "A location you specify within range"),
                    (
                        "Area",
                        "A 30-foot-radius, 40-foot-high cylinder of bright light glimmers there until the spell ends",
                    ),
                    ("Light", "This light is sunlight"),
                    (
                        "Save",
                        "Constitution, made by each creature in the cylinder when it appears, and whenever a creature ends its turn in the cylinder",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("4d10 Radiant damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Moving",
                        "If you're within 60 feet of the cylinder, you can move it up to 60 feet as a bonus action on your turn",
                    ),
                )
            ),
        ]


class DestructiveWave(ClassSpell):
    rules = SpellRules(
        name="Destructive Wave",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.PALADIN,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description="Destructive energy ripples outward from you in a 30-foot Emanation. Each creature you choose in the Emanation makes a Constitution saving throw. On a failed save, a target takes 5d6 Thunder damage and 5d6 Radiant or Necrotic damage (your choice) and has the Prone condition. On a successful save, a target takes half as much damage only.",
        usage_tags=("control", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8cded48cee015ab1")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Destructive energy ripples outward from you in a 30-foot Emanation.",
                    ),
                    ("Area", "30-foot Emanation"),
                    ("Targets", "Each creature you choose in the Emanation"),
                    ("Save", "Constitution"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "5d6 Thunder damage and 5d6 Radiant or Necrotic damage (your choice), and the Prone condition",
                        "Half as much damage only",
                    ),
                ),
            ),
        ]


class DispelEvilAndGood(ClassSpell):
    rules = SpellRules(
        name="Dispel Evil and Good",
        level=5,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="powdered silver and iron"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "For the duration, Celestials, Elementals, Fey, Fiends, and Undead have Disadvantage on attack rolls against you. You can end the spell early by using either of the following special functions.\n"
            "Break Enchantment. As a Magic action, you touch a creature that is possessed by or has the Charmed or Frightened condition from one or more creatures of the types above. The target is no longer possessed, Charmed, or Frightened by such creatures.\n"
            "Dismissal. As a Magic action, you target one creature you can see within 5 feet of you that has one of the creature types above. The target must succeed on a Charisma saving throw or be sent back to its home plane if it isn’t there already. If they aren’t on their home plane, Undead are sent to the Shadowfell, and Fey are sent to the Feywild."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "f8f9f23b6a56c758")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Effect",
                        "Celestials, Elementals, Fey, Fiends, and Undead have Disadvantage on attack rolls against you",
                    ),
                    (
                        "Ends early",
                        "You can end the spell early by using either of the following special functions",
                    ),
                )
            ),
            Option(
                "Break Enchantment",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            (
                                "Target",
                                "A creature you touch that is possessed by or has the Charmed or Frightened condition from one or more creatures of the types above",
                            ),
                            (
                                "Effect",
                                "The target is no longer possessed, Charmed, or Frightened by such creatures",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Dismissal",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            (
                                "Target",
                                "One creature you can see within 5 feet of you that has one of the creature types above",
                            ),
                            ("Save", "Charisma"),
                            (
                                "Failed save",
                                "The target is sent back to its home plane if it isn't there already",
                            ),
                            ("Successful save", "No effect"),
                            (
                                "Not on home plane",
                                "If they aren't on their home plane, Undead are sent to the Shadowfell, and Fey are sent to the Feywild",
                            ),
                        )
                    ),
                ),
            ),
        ]


class DominatePerson(ClassSpell):
    rules = SpellRules(
        name="Dominate Person",
        level=5,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "One Humanoid you can see within range must succeed on a Wisdom saving throw or have the Charmed condition for the duration. The target has Advantage on the save if you or your allies are fighting it. Whenever the target takes damage, it repeats the save, ending the spell on itself on a success.\n"
            "You have a telepathic link with the Charmed target while the two of you are on the same plane of existence. On your turn, you can use this link to issue commands to the target (no action required), such as “Attack that creature,” “Move over there,” or “Fetch that object.” The target does its best to obey on its turn. If it completes an order and doesn’t receive further direction from you, it acts and moves as it likes, focusing on protecting itself.\n"
            "You can command the target to take a Reaction but must take your own Reaction to do so.\n"
            "Using a Higher-Level Spell Slot. Your Concentration can last longer with a spell slot of level 6 (up to 10 minutes), 7 (up to 1 hour), or 8+ (up to 8 hours)."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "305c3ca75173a5c4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You take control of a Humanoid."),
            Facts(
                (
                    ("Target", "One Humanoid you can see within range"),
                    (
                        "Save",
                        "Wisdom, with Advantage if you or your allies are fighting it",
                    ),
                    ("Failed save", "Charmed for the duration"),
                    ("Successful save", "No effect"),
                    (
                        "Repeat save",
                        "Whenever the target takes damage, it repeats the save, ending the spell on itself on a success",
                    ),
                )
            ),
            Option(
                "Control",
                (
                    Facts(
                        (
                            (
                                "Telepathic link",
                                "You have a telepathic link with the Charmed target while the two of you are on the same plane of existence",
                            ),
                            (
                                "Commands",
                                'On your turn, you can use this link to issue commands to the target (no action required), such as "Attack that creature," "Move over there," or "Fetch that object"',
                            ),
                            (
                                "Obeying",
                                "The target does its best to obey on its turn; if it completes an order and doesn't receive further direction from you, it acts and moves as it likes, focusing on protecting itself",
                            ),
                            (
                                "Reactions",
                                "You can command the target to take a Reaction but must take your own Reaction to do so",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Concentration lasts up to"),
                        (("6", "10 minutes"), ("7", "1 hour"), ("8+", "8 hours")),
                    ),
                ),
            ),
        ]


class Dream(ClassSpell):
    rules = SpellRules(
        name="Dream",
        level=5,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.SPECIAL),
        components=Components(verbal=True, somatic=True, material="a handful of sand"),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You target a creature you know on the same plane of existence. You or a willing creature you touch enters a trance state to act as a dream messenger. While in the trance, the messenger is Incapacitated and has a Speed of 0.\n"
            "If the target is asleep, the messenger appears in the target’s dreams and can converse with the target as long as it remains asleep, through the spell’s duration. The messenger can also shape the dream’s environment, creating landscapes, objects, and other images. The messenger can emerge from the trance at any time, ending the spell. The target recalls the dream perfectly upon waking.\n"
            "If the target is awake when you cast the spell, the messenger knows it and can either end the trance (and the spell) or wait for the target to sleep, at which point the messenger enters its dreams.\n"
            "You can make the messenger terrifying to the target. If you do so, the messenger can deliver a message of no more than ten words, and then the target makes a Wisdom saving throw. On a failed save, the target gains no benefit from its rest, and it takes 3d6 Psychic damage when it wakes up."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ffbb297d449ea90d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature you know on the same plane of existence"),
                    (
                        "Messenger",
                        "You or a willing creature you touch enters a trance state to act as a dream messenger",
                    ),
                    (
                        "In the trance",
                        "The messenger is Incapacitated and has a Speed of 0",
                    ),
                )
            ),
            Option(
                "If the Target Is Asleep",
                (
                    Facts(
                        (
                            (
                                "Dreams",
                                "The messenger appears in the target's dreams and can converse with the target as long as it remains asleep, through the spell's duration",
                            ),
                            (
                                "Environment",
                                "The messenger can also shape the dream's environment, creating landscapes, objects, and other images",
                            ),
                            (
                                "Emerging",
                                "The messenger can emerge from the trance at any time, ending the spell",
                            ),
                            (
                                "Waking",
                                "The target recalls the dream perfectly upon waking",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "If the Target Is Awake",
                (
                    Facts(
                        (
                            (
                                "Choice",
                                "The messenger knows it and can either end the trance (and the spell) or wait for the target to sleep, at which point the messenger enters its dreams",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Terrifying Messenger",
                (
                    Facts(
                        (
                            (
                                "Option",
                                "You can make the messenger terrifying to the target",
                            ),
                            (
                                "Message",
                                "If you do so, the messenger can deliver a message of no more than ten words, and then the target makes a Wisdom saving throw",
                            ),
                            (
                                "Failed save",
                                "The target gains no benefit from its rest, and it takes 3d6 Psychic damage when it wakes up",
                            ),
                            ("Successful save", "No effect"),
                        )
                    ),
                ),
            ),
        ]


class Enervation(ClassSpell):
    rules = SpellRules(
        name="Enervation",
        level=5,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "A tendril of inky darkness reaches out from you to drain life from a creature you can see within range.\n"
            "The target makes a Dexterity saving throw. On a failed save, the target takes 6d8 Necrotic damage. On each of your subsequent turns, you can take a Bonus Action to deal 2d8 Necrotic damage to the target automatically. The spell ends if the target is ever outside the spell’s range or it has Total Cover from you.\n"
            "On a successful save, the target takes half the initial damage only, and the spell ends.\n"
            "Whenever this spell deals damage to a target, you regain Hit Points equal to half the amount of Necrotic damage dealt.\n"
            "Using a Higher-Level Spell Slot. The initial damage increases by 1d8 for each spell slot level above 5."
        ),
        usage_tags=("damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "893361968b4095db")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A tendril of inky darkness reaches out from you to drain life from a creature you can see within range.",
                    ),
                    ("Target", "A creature you can see within range"),
                    ("Save", "Dexterity"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "6d8 Necrotic damage",
                        "Half the initial damage only, and the spell ends",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Later turns",
                        "On each of your subsequent turns, you can take a Bonus Action to deal 2d8 Necrotic damage to the target automatically",
                    ),
                    (
                        "Ends early",
                        "The spell ends if the target is ever outside the spell’s range or it has Total Cover from you",
                    ),
                    (
                        "Healing",
                        "Whenever this spell deals damage to a target, you regain Hit Points equal to half the amount of Necrotic damage dealt",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The initial damage increases by 1d8 for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class FarStep(ClassSpell):
    rules = SpellRules(
        name="Far Step",
        level=5,
        school=School.CONJURATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="You teleport up to 60 feet to an unoccupied space you can see. On each of your turns before the spell ends, you can use a bonus action to teleport in this way again.",
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "3f49df045799450a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Teleport",
                        "You teleport up to 60 feet to an unoccupied space you can see",
                    ),
                    (
                        "Again",
                        "On each of your turns before the spell ends, you can use a bonus action to teleport in this way again",
                    ),
                )
            )
        ]


class FlameStrike(ClassSpell):
    rules = SpellRules(
        name="Flame Strike",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True, material="a pinch of sulfur"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A vertical column of brilliant fire roars down from above. Each creature in a 10-foot-radius, 40-foot-high Cylinder centered on a point within range makes a Dexterity saving throw, taking 5d6 Fire damage and 5d6 Radiant damage on a failed save or half as much damage on a successful one.\n"
            "Using a Higher-Level Spell Slot. The Fire damage and the Radiant damage increase by 1d6 for each spell slot level above 5."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "2521210fd9adf82d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A vertical column of brilliant fire roars down from above.",
                    ),
                    (
                        "Area",
                        "10-foot-radius, 40-foot-high Cylinder centered on a point within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the Cylinder"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("5d6 Fire damage and 5d6 Radiant damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The Fire damage and the Radiant damage increase by 1d6 for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Geas(ClassSpell):
    rules = SpellRules(
        name="Geas",
        level=5,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True),
        duration=Duration(DurationType.DAY, 30),
        source="Player's Handbook",
        description=(
            "You give a verbal command to a creature that you can see within range, ordering it to carry out some service or refrain from an action or a course of activity as you decide. The target must succeed on a Wisdom saving throw or have the Charmed condition for the duration. The target automatically succeeds if it can’t understand your command.\n"
            "While Charmed, the creature takes 5d10 Psychic damage if it acts in a manner directly counter to your command. It takes this damage no more than once each day.\n"
            "You can issue any command you choose, short of an activity that would result in certain death. Should you issue a suicidal command, the spell ends.\n"
            "A Remove Curse , Greater Restoration , or Wish spell ends this spell.\n"
            "Using a Higher-Level Spell Slot. If you use a level 7 or 8 spell slot, the duration is 365 days. If you use a level 9 spell slot, the spell lasts until it is ended by one of the spells mentioned above."
        ),
        usage_tags=("control", "damage", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "d74575d17c309ecf")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature that you can see within range"),
                    (
                        "Command",
                        "You give a verbal command to the creature, ordering it to carry out some service or refrain from an action or a course of activity as you decide",
                    ),
                    ("Save", "Wisdom"),
                    ("Failed save", "Charmed for the duration"),
                    ("Successful save", "No effect"),
                    (
                        "Automatic success",
                        "The target automatically succeeds if it can't understand your command",
                    ),
                    (
                        "While Charmed",
                        "The creature takes 5d10 Psychic damage if it acts in a manner directly counter to your command; it takes this damage no more than once each day",
                    ),
                    (
                        "Limit",
                        "You can issue any command you choose, short of an activity that would result in certain death; should you issue a suicidal command, the spell ends",
                    ),
                    (
                        "Ends early",
                        "A Remove Curse, Greater Restoration, or Wish spell ends this spell",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Duration"),
                        (
                            ("7-8", "365 days"),
                            (
                                "9",
                                "Until it is ended by one of the spells mentioned above",
                            ),
                        ),
                    ),
                ),
            ),
        ]


class GraveGround(ClassSpell):
    rules = SpellRules(
        name="Grave Ground",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a handful of grave dirt"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "Skeletal hands burst from an area on the ground within range. The area consists of up to four 10-foot squares, which you arrange as you like. Each square must be contiguous with at least one other square. That area is Difficult Terrain for your enemies.\n"
            "Any enemy in that area when the skeletal hands appear makes a Strength saving throw. On a failed save, a creature takes 6d6 Necrotic damage, and until the end of its next turn, the creature subtracts 1d6 from all its damage rolls. An enemy also makes this save if it enters the area or ends its turn there. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 5."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e9b297ac46444c5a")


class GreaterRestoration(ClassSpell):
    rules = SpellRules(
        name="Greater Restoration",
        level=5,
        school=School.ABJURATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.PALADIN,
            CharacterClass.RANGER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="diamond dust worth 100+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You touch a creature and magically remove one of the following effects from it:\n"
            "1 Exhaustion level\n"
            "The Charmed or Petrified condition\n"
            "A curse, including the target’s Attunement to a cursed magic item\n"
            "Any reduction to one of the target’s ability scores\n"
            "Any reduction to the target’s Hit Point maximum"
        ),
        usage_tags=("control",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1c2cdbc0ac270b21")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature you touch"),
                    (
                        "Effect",
                        "You magically remove one of the following effects from it",
                    ),
                )
            ),
            Table(
                ("Effect removed",),
                (
                    ("1 Exhaustion level",),
                    ("The Charmed or Petrified condition",),
                    (
                        "A curse, including the target's Attunement to a cursed magic item",
                    ),
                    ("Any reduction to one of the target's ability scores",),
                    ("Any reduction to the target's Hit Point maximum",),
                ),
            ),
        ]


class Hallow(ClassSpell):
    rules = SpellRules(
        name="Hallow",
        level=5,
        school=School.ABJURATION,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.HOUR, 24),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="incense worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Player's Handbook",
        description=(
            "You touch a point and infuse an area around it with holy or unholy power. The area can have a radius up to 60 feet, and the spell fails if the radius includes an area already under the effect of Hallow . The affected area has the following effects.\n"
            "Hallowed Ward. Choose any of these creature types: Aberration, Celestial, Elemental, Fey, Fiend, or Undead. Creatures of the chosen types can’t willingly enter the area, and any creature that is possessed by or that has the Charmed or Frightened condition from such creatures isn’t possessed, Charmed, or Frightened by them while in the area.\n"
            "Extra Effect. You bind an extra effect to the area from the list below:\n"
            "Courage. Creatures of any types you choose can’t gain the Frightened condition while in the area.\n"
            "Darkness. Darkness fills the area. Normal light, as well as magical light created by spells of a level lower than this spell, can’t illuminate the area.\n"
            "Daylight. Bright light fills the area. Magical Darkness created by spells of a level lower than this spell can’t extinguish the light.\n"
            "Peaceful Rest. Dead bodies interred in the area can’t be turned into Undead.\n"
            "Extradimensional Interference. Creatures of any types you choose can’t enter or exit the area using teleportation or interplanar travel.\n"
            "Fear. Creatures of any types you choose have the Frightened condition while in the area.\n"
            "Resistance. Creatures of any types you choose have Resistance to one damage type of your choice while in the area.\n"
            "Silence. No sound can emanate from within the area, and no sound can reach into it.\n"
            "Tongues. Creatures of any types you choose can communicate with any other creature in the area even if they don’t share a common language.\n"
            "Vulnerability. Creatures of any types you choose have Vulnerability to one damage type of your choice while in the area."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3a208a4b88f13b9a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "A point you touch and an area around it, infused with holy or unholy power; the area can have a radius up to 60 feet",
                    ),
                    (
                        "Fails",
                        "The spell fails if the radius includes an area already under the effect of Hallow",
                    ),
                )
            ),
            Option(
                "Hallowed Ward",
                (
                    Facts(
                        (
                            (
                                "Creature types",
                                "Choose any of these creature types: Aberration, Celestial, Elemental, Fey, Fiend, or Undead",
                            ),
                            (
                                "Entering",
                                "Creatures of the chosen types can't willingly enter the area",
                            ),
                            (
                                "Protection",
                                "Any creature that is possessed by or that has the Charmed or Frightened condition from such creatures isn't possessed, Charmed, or Frightened by them while in the area",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Extra Effect",
                        "You bind an extra effect to the area from the list below",
                    ),
                )
            ),
            Table(
                ("Effect", "Description"),
                (
                    (
                        "Courage",
                        "Creatures of any types you choose can't gain the Frightened condition while in the area",
                    ),
                    (
                        "Darkness",
                        "Darkness fills the area. Normal light, as well as magical light created by spells of a level lower than this spell, can't illuminate the area",
                    ),
                    (
                        "Daylight",
                        "Bright light fills the area. Magical Darkness created by spells of a level lower than this spell can't extinguish the light",
                    ),
                    (
                        "Peaceful Rest",
                        "Dead bodies interred in the area can't be turned into Undead",
                    ),
                    (
                        "Extradimensional Interference",
                        "Creatures of any types you choose can't enter or exit the area using teleportation or interplanar travel",
                    ),
                    (
                        "Fear",
                        "Creatures of any types you choose have the Frightened condition while in the area",
                    ),
                    (
                        "Resistance",
                        "Creatures of any types you choose have Resistance to one damage type of your choice while in the area",
                    ),
                    (
                        "Silence",
                        "No sound can emanate from within the area, and no sound can reach into it",
                    ),
                    (
                        "Tongues",
                        "Creatures of any types you choose can communicate with any other creature in the area even if they don't share a common language",
                    ),
                    (
                        "Vulnerability",
                        "Creatures of any types you choose have Vulnerability to one damage type of your choice while in the area",
                    ),
                ),
            ),
        ]


class HoldMonster(ClassSpell):
    rules = SpellRules(
        name="Hold Monster",
        level=5,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a straight piece of iron"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "Choose a creature that you can see within range. The target must succeed on a Wisdom saving throw or have the Paralyzed condition for the duration. At the end of each of its turns, the target repeats the save, ending the spell on itself on a success.\n"
            "Using a Higher-Level Spell Slot. You can target one additional creature for each spell slot level above 5."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "68bc91147f89f04c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A creature that you can see within range"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target has the Paralyzed condition for the duration",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Repeat save",
                        "At the end of each of its turns, the target repeats the save, ending the spell on itself on a success",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Targets",
                                "You can target one additional creature for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class HolyWeapon(ClassSpell):
    rules = SpellRules(
        name="Holy Weapon",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="You imbue a weapon you touch with holy power. Until the spell ends, the weapon emits bright light in a 30-foot radius and dim light for an additional 30 feet. In addition, weapon attacks made with it deal an extra 2d8 radiant damage on a hit. If the weapon isn't already a magic weapon, it becomes one for the duration. As a bonus action on your turn, you can dismiss this spell and cause the weapon to emit a burst of radiance. Each creature of your choice that you can see within 30 feet of the weapon must make a Constitution saving throw. On a failed save, a creature takes 4d8 radiant damage, and it is blinded for 1 minute. On a successful save, a creature takes half as much damage and isn't blinded. At the end of each of its turns, a blinded creature can make a Constitution saving throw, ending the effect on itself on a success.",
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "c1c756c942b894b3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "You imbue a weapon you touch with holy power."),
                    ("Weapon", "A weapon you touch"),
                    (
                        "Light",
                        "Until the spell ends, the weapon emits bright light in a 30-foot radius and dim light for an additional 30 feet",
                    ),
                    (
                        "Extra damage",
                        "Weapon attacks made with it deal an extra 2d8 Radiant damage on a hit",
                    ),
                    (
                        "Magic",
                        "If the weapon isn't already a magic weapon, it becomes one for the duration",
                    ),
                )
            ),
            Option(
                "Dismissing the Spell",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "As a bonus action on your turn, you can dismiss this spell and cause the weapon to emit a burst of radiance",
                            ),
                            (
                                "Targets",
                                "Each creature of your choice that you can see within 30 feet of the weapon",
                            ),
                            ("Save", "Constitution"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (
                            (
                                "4d8 Radiant damage, and it is Blinded for 1 minute",
                                "Half as much damage and isn't Blinded",
                            ),
                        ),
                    ),
                    Facts(
                        (
                            (
                                "Repeat save",
                                "At the end of each of its turns, a Blinded creature can make a Constitution saving throw, ending the effect on itself on a success",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Immolation(ClassSpell):
    rules = SpellRules(
        name="Immolation",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Flames wreathe one creature you can see within range. The target must make a Dexterity saving throw. It takes 8d6 fire damage on a failed save, or half as much damage on a successful one. On a failed save, the target also burns for the spell's duration. The burning target sheds bright light in a 30-foot radius and dim light for an additional 30 feet. At the end of each of its turns, the target repeats the saving throw. It takes 4d6 fire damage on a failed save, and the spell ends on a successful one. These magical flames can't be extinguished by nonmagical means.\n"
            "If damage from this spell kills a target, the target is turned to ash."
        ),
        usage_tags=("buff", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "b58308f8f5c07ea2")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Flavor", "Flames wreathe one creature you can see within range."),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Dexterity"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "8d6 Fire damage, and the target also burns for the spell's duration",
                        "Half as much damage",
                    ),
                ),
            ),
            Option(
                "Burning Target",
                (
                    Facts(
                        (
                            (
                                "Light",
                                "The burning target sheds bright light in a 30-foot radius and dim light for an additional 30 feet",
                            ),
                            (
                                "Repeat save",
                                "Dexterity, at the end of each of its turns",
                            ),
                            ("Failed save", "4d6 Fire damage"),
                            ("Successful save", "The spell ends"),
                            (
                                "Flames",
                                "These magical flames can't be extinguished by nonmagical means",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Ash",
                        "If damage from this spell kills a target, the target is turned to ash",
                    ),
                )
            ),
        ]


class InfernalCalling(ClassSpell):
    rules = SpellRules(
        name="Infernal Calling",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a ruby worth at least 999 gp"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Uttering a dark incantation, you summon a devil from the Nine Hells. You choose the devil's type, which must be one of challenge rating 6 or lower, such as a barbed devil or a bearded devil. The devil appears in an unoccupied space that you can see within range. The devil disappears when it drops to 0 hit points or when the spell ends.\n"
            "The devil is unfriendly toward you and your companions. Roll initiative for the devil, which has its own turns. It is under the Dungeon Master's control and acts according to its nature on each of its turns, which might result in its attacking you if it thinks it can prevail, or trying to tempt you to undertake an evil act in exchange for limited service. The DM has the creature's statistics.\n"
            'On each of your turns, you can try to issue a verbal command to the devil (no action required by you). It obeys the command if the likely outcome is in accordance with its desires, especially if the result would draw you toward evil. Otherwise, you must make a Charisma (Deception, Intimidation, or Persuasion) check contested by its Wisdom (Insight) check. You make the check with advantage if you say the devil\'s true name. If your check fails, the devil becomes immune to your verbal commands for the duration of the spell, though it can still carry out your commands if it chooses. If your check succeeds, the devil carries out your command— such as "attack my enemies," "explore the room ahead," or "bear this message to the queen"—until it completes the activity, at which point it returns to you to report having done so.\n'
            "If your concentration ends before the spell reaches its full duration, the devil doesn't disappear if it has become immune to your verbal commands. Instead, it acts in whatever manner it chooses for 3d6 minutes, and then it disappears.\n"
            "If you possess an individual devil's talisman, you can summon that devil if it is of the appropriate challenge rating plus 1, and it obeys all your commands, with no Charisma checks required.\n"
            "At Higher Levels When you cast this spell using a spell slot of 6th level or higher, the challenge rating increases by 1 for each slot level above 5th."
        ),
        usage_tags=("control", "utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "89f15b7711508c64")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Uttering a dark incantation, you summon a devil from the Nine Hells.",
                    ),
                    (
                        "Devil",
                        "You choose the devil's type, which must be one of challenge rating 6 or lower, such as a barbed devil or a bearded devil",
                    ),
                    ("Appears", "In an unoccupied space that you can see within range"),
                    (
                        "Disappears",
                        "When it drops to 0 hit points or when the spell ends",
                    ),
                    (
                        "Attitude",
                        "The devil is unfriendly toward you and your companions",
                    ),
                    (
                        "Initiative",
                        "Roll initiative for the devil, which has its own turns",
                    ),
                    (
                        "Control",
                        "It is under the Dungeon Master's control and acts according to its nature on each of its turns, which might result in its attacking you if it thinks it can prevail, or trying to tempt you to undertake an evil act in exchange for limited service",
                    ),
                    ("Statistics", "The DM has the creature's statistics"),
                )
            ),
            Option(
                "Commanding the Devil",
                (
                    Facts(
                        (
                            (
                                "Command",
                                "On each of your turns, you can try to issue a verbal command to the devil (no action required by you)",
                            ),
                            (
                                "Obeys",
                                "It obeys the command if the likely outcome is in accordance with its desires, especially if the result would draw you toward evil",
                            ),
                            (
                                "Otherwise",
                                "You must make a Charisma (Deception, Intimidation, or Persuasion) check contested by its Wisdom (Insight) check",
                            ),
                            (
                                "True name",
                                "You make the check with Advantage if you say the devil's true name",
                            ),
                            (
                                "Check fails",
                                "The devil becomes immune to your verbal commands for the duration of the spell, though it can still carry out your commands if it chooses",
                            ),
                            (
                                "Check succeeds",
                                'The devil carries out your command - such as "attack my enemies," "explore the room ahead," or "bear this message to the queen" - until it completes the activity, at which point it returns to you to report having done so',
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "If Your Concentration Ends",
                (
                    Facts(
                        (
                            (
                                "Immune devil",
                                "If your concentration ends before the spell reaches its full duration, the devil doesn't disappear if it has become immune to your verbal commands",
                            ),
                            (
                                "Instead",
                                "It acts in whatever manner it chooses for 3d6 minutes, and then it disappears",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Devil's Talisman",
                (
                    Facts(
                        (
                            (
                                "Talisman",
                                "If you possess an individual devil's talisman, you can summon that devil if it is of the appropriate challenge rating plus 1, and it obeys all your commands, with no Charisma checks required",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Challenge rating", "+1 for each slot level above 5th"),)),),
            ),
        ]


class InsectPlague(ClassSpell):
    rules = SpellRules(
        name="Insect Plague",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.SORCERER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 300),
        components=Components(verbal=True, somatic=True, material="a locust"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "Swarming locusts fill a 20-foot-radius Sphere centered on a point you choose within range. The Sphere remains for the duration, and its area is Lightly Obscured and Difficult Terrain.\n"
            "When the swarm appears, each creature in it makes a Constitution saving throw, taking 4d10 Piercing damage on a failed save or half as much damage on a successful one. A creature also makes this save when it enters the spell’s area for the first time on a turn or ends its turn there. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 5."
        ),
        usage_tags=("control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "76081d23a0970aa3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Swarming locusts fill a 20-foot-radius Sphere centered on a point you choose within range.",
                    ),
                    (
                        "Area",
                        "20-foot-radius Sphere centered on a point you choose within range; it remains for the duration, and its area is Lightly Obscured and Difficult Terrain",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in the Sphere when the swarm appears, and also when a creature enters the spell's area for the first time on a turn or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("4d10 Piercing damage", "Half as much damage"),),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d10 for each spell slot level above 5"),)),),
            ),
        ]


class JallarzisStormOfRadiance(ClassSpell):
    rules = SpellRules(
        name="Jallarzi's Storm of Radiance",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="a pinch of phosphorus"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You unleash a storm of flashing light and raging thunder in a 10-foot-radius, 40-foot-high Cylinder centered on a point you can see within range. While in this area, creatures have the Blinded and Deafened conditions, and they can’t cast spells with a Verbal component.\n"
            "When the storm appears, each creature in it makes a Constitution saving throw, taking 2d10 Radiant damage and 2d10 Thunder damage on a failed save or half as much damage on a successful one. A creature also makes this save when it enters the spell’s area for the first time on a turn or ends its turn there. A creature makes this save only once per turn.\n"
            "Using a Higher-Level Spell Slot. The Radiant and Thunder damage increase by 1d10 for each spell slot level above 5."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "1a4504f5d60bb069")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You unleash a storm of flashing light and raging thunder in a 10-foot-radius, 40-foot-high Cylinder centered on a point you can see within range.",
                    ),
                    (
                        "Area",
                        "10-foot-radius, 40-foot-high Cylinder centered on a point you can see within range",
                    ),
                    (
                        "In the area",
                        "Creatures have the Blinded and Deafened conditions, and they can't cast spells with a Verbal component",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in the Cylinder when the storm appears, and also when a creature enters the spell's area for the first time on a turn or ends its turn there; a creature makes this save only once per turn",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d10 Radiant damage and 2d10 Thunder damage",
                        "Half as much damage",
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The Radiant and Thunder damage increase by 1d10 for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class LegendLore(ClassSpell):
    rules = SpellRules(
        name="Legend Lore",
        level=5,
        school=School.DIVINATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="incense worth 250+ GP, which the spell consumes, and four ivory strips worth 50+ GP each",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "Name or describe a famous person, place, or object. The spell brings to your mind a brief summary of the significant lore about that famous thing, as described by the DM.\n"
            "The lore might consist of important details, amusing revelations, or even secret lore that has never been widely known. The more information you already know about the thing, the more precise and detailed the information you receive is. That information is accurate but might be couched in figurative language or poetry, as determined by the DM.\n"
            "If the famous thing you chose isn’t actually famous, you hear sad musical notes played on a trombone, and the spell fails."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "b7de08d7138d98a4")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "A famous person, place, or object that you name or describe",
                    ),
                    (
                        "Lore",
                        "The spell brings to your mind a brief summary of the significant lore about that famous thing, as described by the DM",
                    ),
                    (
                        "Contents",
                        "The lore might consist of important details, amusing revelations, or even secret lore that has never been widely known",
                    ),
                    (
                        "Detail",
                        "The more information you already know about the thing, the more precise and detailed the information you receive is",
                    ),
                    (
                        "Accuracy",
                        "That information is accurate but might be couched in figurative language or poetry, as determined by the DM",
                    ),
                    (
                        "Not famous",
                        "If the famous thing you chose isn't actually famous, you hear sad musical notes played on a trombone, and the spell fails",
                    ),
                )
            )
        ]


class Maelstrom(ClassSpell):
    rules = SpellRules(
        name="Maelstrom",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(
            verbal=True, somatic=True, material="paper or leaf in the shape of a funnel"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description="A mass of 5-foot-deep water appears and swirls in a 30-foot radius centered on a point you can see within range. The point must be on ground or in a body of water. Until the spell ends, that area is difficult terrain, and any creature that starts its turn there must succeed on a Strength saving throw or take 6d6 bludgeoning damage and be pulled 10 feet toward the center.",
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "72fdef494c2ea26e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "A mass of 5-foot-deep water appears and swirls in a 30-foot radius centered on a point you can see within range; the point must be on ground or in a body of water",
                    ),
                    ("Terrain", "Until the spell ends, that area is Difficult Terrain"),
                    (
                        "Save",
                        "Strength, made by any creature that starts its turn there",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "6d6 Bludgeoning damage, and the creature is pulled 10 feet toward the center",
                        "No effect",
                    ),
                ),
            ),
        ]


class MassCureWounds(ClassSpell):
    rules = SpellRules(
        name="Mass Cure Wounds",
        level=5,
        school=School.ABJURATION,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "A wave of healing energy washes out from a point you can see within range. Choose up to six creatures in a 30-foot-radius Sphere centered on that point. Each target regains Hit Points equal to 5d8 plus your spellcasting ability modifier.\n"
            "Using a Higher-Level Spell Slot. The healing increases by 1d8 for each spell slot level above 5."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "256c4d654aaa718d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A wave of healing energy washes out from a point you can see within range.",
                    ),
                    ("Point", "A point you can see within range"),
                    (
                        "Targets",
                        "Choose up to six creatures in a 30-foot-radius Sphere centered on that point",
                    ),
                    (
                        "Healing",
                        "Each target regains Hit Points equal to 5d8 plus your spellcasting ability modifier",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Healing", "+1d8 for each spell slot level above 5"),)),),
            ),
        ]


class Mislead(ClassSpell):
    rules = SpellRules(
        name="Mislead",
        level=5,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You gain the Invisible condition at the same time that an illusory double of you appears where you are standing. The double lasts for the duration, but the invisibility ends immediately after you make an attack roll, deal damage, or cast a spell.\n"
            "As a Magic action, you can move the illusory double up to twice your Speed and make it gesture, speak, and behave in whatever way you choose. It is intangible and invulnerable.\n"
            "You can see through its eyes and hear through its ears as if you were located where it is."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7dc31a846aebfd46")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Effect",
                        "You gain the Invisible condition at the same time that an illusory double of you appears where you are standing",
                    ),
                    (
                        "The double",
                        "Lasts for the duration; it is intangible and invulnerable",
                    ),
                    (
                        "Invisibility ends",
                        "Immediately after you make an attack roll, deal damage, or cast a spell",
                    ),
                    (
                        "Moving",
                        "As a Magic action, you can move the illusory double up to twice your Speed and make it gesture, speak, and behave in whatever way you choose",
                    ),
                    (
                        "Senses",
                        "You can see through its eyes and hear through its ears as if you were located where it is",
                    ),
                )
            )
        ]


class ModifyMemory(ClassSpell):
    rules = SpellRules(
        name="Modify Memory",
        level=5,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You attempt to reshape another creature’s memories. One creature that you can see within range makes a Wisdom saving throw. If you are fighting the creature, it has Advantage on the save. On a failed save, the target has the Charmed condition for the duration. While Charmed in this way, the target also has the Incapacitated condition and is unaware of its surroundings, though it can hear you. If it takes any damage or is targeted by another spell, this spell ends, and no memories are modified.\n"
            "While this charm lasts, you can affect the target’s memory of an event that it experienced within the last 24 hours and that lasted no more than 10 minutes. You can permanently eliminate all memory of the event, allow the target to recall the event with perfect clarity, change its memory of the event’s details, or create a memory of some other event.\n"
            "You must speak to the target to describe how its memories are affected, and it must be able to understand your language for the modified memories to take root. Its mind fills in any gaps in the details of your description. If the spell ends before you finish describing the modified memories, the creature’s memory isn’t altered. Otherwise, the modified memories take hold when the spell ends.\n"
            "A modified memory doesn’t necessarily affect how a creature behaves, particularly if the memory contradicts the creature’s natural inclinations, alignment, or beliefs. An illogical modified memory, such as a false memory of how much the creature enjoyed swimming in acid, is dismissed as a bad dream. The DM might deem a modified memory too nonsensical to affect a creature.\n"
            "A Remove Curse or Greater Restoration spell cast on the target restores the creature’s true memory.\n"
            "Using a Higher-Level Spell Slot. You can alter the target’s memories of an event that took place up to 7 days ago (level 6 spell slot), 30 days ago (level 7 spell slot), 365 days ago (level 8 spell slot), or any time in the creature’s past (level 9 spell slot)."
        ),
        usage_tags=("buff", "control", "heal"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8c7f4da2bf0aed08")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You attempt to reshape another creature's memories."),
            Facts(
                (
                    ("Target", "One creature that you can see within range"),
                    ("Save", "Wisdom, with Advantage if you are fighting the creature"),
                    (
                        "Failed save",
                        "The target has the Charmed condition for the duration; while Charmed in this way, the target also has the Incapacitated condition and is unaware of its surroundings, though it can hear you",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Ends early",
                        "If it takes any damage or is targeted by another spell, this spell ends, and no memories are modified",
                    ),
                )
            ),
            Option(
                "Changing Memories",
                (
                    Facts(
                        (
                            (
                                "Event",
                                "While this charm lasts, you can affect the target's memory of an event that it experienced within the last 24 hours and that lasted no more than 10 minutes",
                            ),
                            (
                                "Choices",
                                "You can permanently eliminate all memory of the event, allow the target to recall the event with perfect clarity, change its memory of the event's details, or create a memory of some other event",
                            ),
                            (
                                "Describing",
                                "You must speak to the target to describe how its memories are affected, and it must be able to understand your language for the modified memories to take root; its mind fills in any gaps in the details of your description",
                            ),
                            (
                                "Interrupted",
                                "If the spell ends before you finish describing the modified memories, the creature's memory isn't altered",
                            ),
                            (
                                "Taking hold",
                                "Otherwise, the modified memories take hold when the spell ends",
                            ),
                            (
                                "Behavior",
                                "A modified memory doesn't necessarily affect how a creature behaves, particularly if the memory contradicts the creature's natural inclinations, alignment, or beliefs",
                            ),
                            (
                                "Illogical",
                                "An illogical modified memory, such as a false memory of how much the creature enjoyed swimming in acid, is dismissed as a bad dream; the DM might deem a modified memory too nonsensical to affect a creature",
                            ),
                            (
                                "Restoring",
                                "A Remove Curse or Greater Restoration spell cast on the target restores the creature's true memory",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Older events",
                                "You can alter the target's memories of an event that took place up to the time shown below",
                            ),
                        )
                    ),
                    Table(
                        ("Slot level", "Event took place up to"),
                        (
                            ("6", "7 days ago"),
                            ("7", "30 days ago"),
                            ("8", "365 days ago"),
                            ("9", "Any time in the creature's past"),
                        ),
                    ),
                ),
            ),
        ]


class MordenkainensLucubration(ClassSpell):
    rules = SpellRules(
        name="Mordenkainen's Lucubration",
        level=5,
        school=School.DIVINATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description=(
            "You recover up to two expended spell slots of level 2 or lower.\n"
            "Using a Higher-Level Spell Slot. The maximum level of spell slots you can recover increases to level 3 (if cast with a level 6–7 spell slot) or level 4 (if cast with a level 8+ spell slot)."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4d385db11b6d343d")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Recover",
                        "You recover up to two expended spell slots of level 2 or lower",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Spell slot used", "Maximum level you can recover"),
                        (("Level 6-7", "Level 3"), ("Level 8+", "Level 4")),
                    ),
                ),
            ),
        ]


class NegativeEnergyFlood(ClassSpell):
    rules = SpellRules(
        name="Negative Energy Flood",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.WARLOCK, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True, material="a broken bone and a square of black silk"
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Arcana Unleashed",
        description=(
            "You send ribbons of negative energy at one creature you can see within range. If the target isn’t Undead, it makes a Constitution saving throw, taking 3d10 + 25 Necrotic damage on a failed save or half as much damage on a successful one. A Humanoid killed by this spell rises at the start of your next turn as a Zombie that follows your verbal orders for 24 hours, after which it acts according to its nature.\n"
            "If the target is Undead, it gains 3d10 Temporary Hit Points.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d10 for each spell slot level above 5."
        ),
        usage_tags=("damage", "heal", "summon"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3f8dd0e59772a04b")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You send ribbons of negative energy at one creature you can see within range.",
                    ),
                    ("Target", "One creature you can see within range"),
                    ("Save", "Constitution, if the target isn’t Undead"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("3d10 + 25 Necrotic damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Undead target",
                        "If the target is Undead, it gains 3d10 Temporary Hit Points",
                    ),
                    (
                        "Killed Humanoid",
                        "A Humanoid killed by this spell rises at the start of your next turn as a Zombie",
                    ),
                    (
                        "Zombie",
                        "It follows your verbal orders for 24 hours, after which it acts according to its nature",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The damage increases by 1d10 for each spell slot level above 5",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Passwall(ClassSpell):
    rules = SpellRules(
        name="Passwall",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(
            verbal=True, somatic=True, material="a pinch of sesame seeds"
        ),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "A passage appears at a point that you can see on a wooden, plaster, or stone surface (such as a wall, ceiling, or floor) within range and lasts for the duration. You choose the opening’s dimensions: up to 5 feet wide, 8 feet tall, and 20 feet deep. The passage creates no instability in a structure surrounding it.\n"
            "When the opening disappears, any creatures or objects still in the passage created by the spell are safely ejected to an unoccupied space nearest to the surface on which you cast the spell."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "19795f4012def0d3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Passage",
                        "A passage appears at a point that you can see on a wooden, plaster, or stone surface (such as a wall, ceiling, or floor) within range and lasts for the duration",
                    ),
                    (
                        "Size",
                        "You choose the opening's dimensions: up to 5 feet wide, 8 feet tall, and 20 feet deep",
                    ),
                    (
                        "Stability",
                        "The passage creates no instability in a structure surrounding it",
                    ),
                    (
                        "Ending",
                        "When the opening disappears, any creatures or objects still in the passage created by the spell are safely ejected to an unoccupied space nearest to the surface on which you cast the spell",
                    ),
                )
            )
        ]


class PlanarBinding(ClassSpell):
    rules = SpellRules(
        name="Planar Binding",
        level=5,
        school=School.ABJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="a jewel worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.HOUR, 24),
        source="Player's Handbook",
        description=(
            "You attempt to bind a Celestial, an Elemental, a Fey, or a Fiend to your service. The creature must be within range for the entire casting of the spell. (Typically, the creature is first summoned into the center of the inverted version of the Magic Circle spell to trap it while this spell is cast.) At the completion of the casting, the target must succeed on a Charisma saving throw or be bound to serve you for the duration. If the creature was summoned or created by another spell, that spell’s duration is extended to match the duration of this spell.\n"
            "A bound creature must follow your commands to the best of its ability. You might command the creature to accompany you on an adventure, to guard a location, or to deliver a message. If the creature is Hostile, it strives to twist your commands to achieve its own objectives. If the creature carries out your commands completely before the spell ends, it travels to you to report this fact if you are on the same plane of existence. If you are on a different plane, it returns to the place where you bound it and remains there until the spell ends.\n"
            "Using a Higher-Level Spell Slot. The duration increases with a spell slot of level 6 (10 days), 7 (30 days), 8 (180 days), and 9 (366 days)."
        ),
        usage_tags=("control", "summon"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7a67f71b4ea5d5bb")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "A Celestial, an Elemental, a Fey, or a Fiend that you attempt to bind to your service; the creature must be within range for the entire casting of the spell",
                    ),
                    (
                        "Typically",
                        "The creature is first summoned into the center of the inverted version of the Magic Circle spell to trap it while this spell is cast",
                    ),
                    ("Save", "Charisma, at the completion of the casting"),
                    (
                        "Failed save",
                        "The target is bound to serve you for the duration",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Other spells",
                        "If the creature was summoned or created by another spell, that spell's duration is extended to match the duration of this spell",
                    ),
                )
            ),
            Option(
                "Bound Creature",
                (
                    Facts(
                        (
                            (
                                "Commands",
                                "A bound creature must follow your commands to the best of its ability",
                            ),
                            (
                                "Examples",
                                "You might command the creature to accompany you on an adventure, to guard a location, or to deliver a message",
                            ),
                            (
                                "Hostile",
                                "If the creature is Hostile, it strives to twist your commands to achieve its own objectives",
                            ),
                            (
                                "Task done",
                                "If the creature carries out your commands completely before the spell ends, it travels to you to report this fact if you are on the same plane of existence",
                            ),
                            (
                                "Different plane",
                                "If you are on a different plane, it returns to the place where you bound it and remains there until the spell ends",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Table(
                        ("Slot level", "Duration"),
                        (
                            ("6", "10 days"),
                            ("7", "30 days"),
                            ("8", "180 days"),
                            ("9", "366 days"),
                        ),
                    ),
                ),
            ),
        ]


class RaiseDead(ClassSpell):
    rules = SpellRules(
        name="Raise Dead",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="a diamond worth 500+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "With a touch, you revive a dead creature if it has been dead no longer than 10 days and it wasn’t Undead when it died.\n"
            "The creature returns to life with 1 Hit Point. This spell also neutralizes any poisons that affected the creature at the time of death.\n"
            "This spell closes all mortal wounds, but it doesn’t restore missing body parts. If the creature is lacking body parts or organs integral for its survival - its head, for instance - the spell automatically fails.\n"
            "Coming back from the dead is an ordeal. The target takes a −4 penalty to D20 Tests. Every time the target finishes a Long Rest, the penalty is reduced by 1 until it becomes 0."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3a671e9687238819")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "A dead creature you touch, if it has been dead no longer than 10 days and it wasn't Undead when it died",
                    ),
                    ("Effect", "The creature returns to life with 1 Hit Point"),
                    (
                        "Poisons",
                        "This spell also neutralizes any poisons that affected the creature at the time of death",
                    ),
                    (
                        "Wounds",
                        "This spell closes all mortal wounds, but it doesn't restore missing body parts",
                    ),
                    (
                        "Fails",
                        "If the creature is lacking body parts or organs integral for its survival - its head, for instance - the spell automatically fails",
                    ),
                    (
                        "Penalty",
                        "Coming back from the dead is an ordeal; the target takes a −4 penalty to D20 Tests",
                    ),
                    (
                        "Recovery",
                        "Every time the target finishes a Long Rest, the penalty is reduced by 1 until it becomes 0",
                    ),
                )
            )
        ]


class RarysTelepathicBond(ClassSpell):
    rules = SpellRules(
        name="Rary's Telepathic Bond",
        level=5,
        school=School.DIVINATION,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION, ritual=True),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True, material="two eggs"),
        duration=Duration(DurationType.HOUR, 1),
        source="Player's Handbook",
        description=(
            "You forge a telepathic link among up to eight willing creatures of your choice within range, psychically linking each creature to all the others for the duration. Creatures that can’t communicate in any languages aren’t affected by this spell.\n"
            "Until the spell ends, the targets can communicate telepathically through the bond whether or not they share a language. The communication is possible over any distance, though it can’t extend to other planes of existence."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "6768a14555b6249e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "Up to eight willing creatures of your choice within range",
                    ),
                    (
                        "Link",
                        "You forge a telepathic link among them, psychically linking each creature to all the others for the duration",
                    ),
                    (
                        "Not affected",
                        "Creatures that can't communicate in any languages aren't affected by this spell",
                    ),
                    (
                        "Communication",
                        "Until the spell ends, the targets can communicate telepathically through the bond whether or not they share a language",
                    ),
                    (
                        "Distance",
                        "The communication is possible over any distance, though it can't extend to other planes of existence",
                    ),
                )
            )
        ]


class Reincarnate(ClassSpell):
    rules = SpellRules(
        name="Reincarnate",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.HOUR, 1),
        range=Range(RangeType.TOUCH),
        components=Components(
            verbal=True,
            somatic=True,
            material="rare oils worth 1,000+ GP, which the spell consumes",
        ),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You touch a dead Humanoid or a piece of one. If the creature has been dead no longer than 10 days, the spell forms a new body for it and calls the soul to enter that body. Roll 1d10 and consult the table below to determine the body’s species, or the DM chooses another playable species.\n"
            "The reincarnated creature makes any choices that a species’ description offers, and the creature recalls its former life. It retains the capabilities it had in its original form, except it loses the traits of its previous species and gains the traits of its new one."
        ),
        usage_tags=("heal",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "c6197393d6e382b3")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    ("Target", "A dead Humanoid or a piece of one that you touch"),
                    (
                        "Requirement",
                        "The creature has been dead no longer than 10 days",
                    ),
                    (
                        "Effect",
                        "The spell forms a new body for it and calls the soul to enter that body",
                    ),
                    (
                        "Species",
                        "Roll 1d10 and consult the table below to determine the body's species, or the DM chooses another playable species",
                    ),
                )
            ),
            Table(
                ("1d10", "Species"),
                (
                    ("1", "Aasimar"),
                    ("2", "Dragonborn"),
                    ("3", "Dwarf"),
                    ("4", "Elf"),
                    ("5", "Gnome"),
                    ("6", "Goliath"),
                    ("7", "Halfling"),
                    ("8", "Human"),
                    ("9", "Orc"),
                    ("10", "Tiefling"),
                ),
            ),
            Facts(
                (
                    (
                        "Choices",
                        "The reincarnated creature makes any choices that a species' description offers, and the creature recalls its former life",
                    ),
                    (
                        "Capabilities",
                        "It retains the capabilities it had in its original form, except it loses the traits of its previous species and gains the traits of its new one",
                    ),
                )
            ),
        ]


class Scrying(ClassSpell):
    rules = SpellRules(
        name="Scrying",
        level=5,
        school=School.DIVINATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 10),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True,
            somatic=True,
            material="a focus worth 1,000+ GP, such as a crystal ball, mirror, or water-filled font",
        ),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You can see and hear a creature you choose that is on the same plane of existence as you. The target makes a Wisdom saving throw, which is modified (see the tables below) by how well you know the target and the sort of physical connection you have to it. The target doesn’t know what it is making the save against, only that it feels uneasy.\n"
            "On a successful save, the target isn’t affected, and you can’t use this spell on it again for 24 hours.\n"
            "On a failed save, the spell creates an Invisible, intangible sensor within 10 feet of the target. You can see and hear through the sensor as if you were there. The sensor moves with the target, remaining within 10 feet of it for the duration. If something can see the sensor, it appears as a luminous orb about the size of your fist.\n"
            "Instead of targeting a creature, you can target a location you have seen. When you do so, the sensor appears at that location and doesn’t move."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "bab79f6494e87311")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Target",
                        "A creature you choose that is on the same plane of existence as you; you can see and hear it",
                    ),
                    (
                        "Save",
                        "Wisdom, modified (see the tables below) by how well you know the target and the sort of physical connection you have to it",
                    ),
                    (
                        "Unaware",
                        "The target doesn't know what it is making the save against, only that it feels uneasy",
                    ),
                )
            ),
            Table(
                ("Your knowledge of the target is...", "Save modifier"),
                (
                    ("Secondhand (heard of the target)", "+5"),
                    ("Firsthand (met the target)", "+0"),
                    ("Extensive (know the target well)", "−5"),
                ),
            ),
            Table(
                ("You have the target's...", "Save modifier"),
                (
                    ("Picture or other likeness", "−2"),
                    ("Garment or other possession", "−4"),
                    ("Body part, lock of hair, or bit of nail", "−10"),
                ),
            ),
            Facts(
                (
                    (
                        "Successful save",
                        "The target isn't affected, and you can't use this spell on it again for 24 hours",
                    ),
                    (
                        "Failed save",
                        "The spell creates an Invisible, intangible sensor within 10 feet of the target",
                    ),
                )
            ),
            Option(
                "The Sensor",
                (
                    Facts(
                        (
                            (
                                "Senses",
                                "You can see and hear through the sensor as if you were there",
                            ),
                            (
                                "Moving",
                                "The sensor moves with the target, remaining within 10 feet of it for the duration",
                            ),
                            (
                                "Seen",
                                "If something can see the sensor, it appears as a luminous orb about the size of your fist",
                            ),
                            (
                                "Location",
                                "Instead of targeting a creature, you can target a location you have seen; when you do so, the sensor appears at that location and doesn't move",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Seeming(ClassSpell):
    rules = SpellRules(
        name="Seeming",
        level=5,
        school=School.ILLUSION,
        classes=(CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 8),
        source="Player's Handbook",
        description=(
            "You give an illusory appearance to each creature of your choice that you can see within range. An unwilling target can make a Charisma saving throw, and if it succeeds, it is unaffected by this spell.\n"
            "You can give the same appearance or different ones to the targets. The spell can change the appearance of the targets’ bodies and equipment. You can make each creature seem 1 foot shorter or taller and appear heavier or lighter. A target’s new appearance must have the same basic arrangement of limbs as the target, but the extent of the illusion is otherwise up to you. The spell lasts for the duration.\n"
            "The changes wrought by this spell fail to hold up to physical inspection. For example, if you use this spell to add a hat to a creature’s outfit, objects pass through the hat.\n"
            "A creature that takes the Study action to examine a target can make an Intelligence (Investigation) check against your spell save DC. If it succeeds, it becomes aware that the target is disguised."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "80bf19feacede81f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Targets",
                        "Each creature of your choice that you can see within range; you give each an illusory appearance",
                    ),
                    (
                        "Save",
                        "Charisma, which an unwilling target can make; if it succeeds, it is unaffected by this spell",
                    ),
                    (
                        "Appearances",
                        "You can give the same appearance or different ones to the targets",
                    ),
                    (
                        "Changes",
                        "The spell can change the appearance of the targets' bodies and equipment; you can make each creature seem 1 foot shorter or taller and appear heavier or lighter",
                    ),
                    (
                        "Limit",
                        "A target's new appearance must have the same basic arrangement of limbs as the target, but the extent of the illusion is otherwise up to you",
                    ),
                    (
                        "Inspection",
                        "The changes wrought by this spell fail to hold up to physical inspection; for example, if you use this spell to add a hat to a creature's outfit, objects pass through the hat",
                    ),
                    (
                        "Study",
                        "A creature that takes the Study action to examine a target can make an Intelligence (Investigation) check against your spell save DC; if it succeeds, it becomes aware that the target is disguised",
                    ),
                )
            )
        ]


class SkillEmpowerment(ClassSpell):
    rules = SpellRules(
        name="Skill Empowerment",
        level=5,
        school=School.TRANSMUTATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
            CharacterClass.ARTIFICER,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.TOUCH),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "Your magic deepens a creature's understanding of its own talent. You touch one willing creature and give it expertise in one skill of your choice; until the spell ends, the creature doubles its proficiency bonus for ability checks it makes that use the chosen skill.\n"
            "You must choose a skill in which the target is proficient and that isn't already benefiting from an effect, such as Expertise, that doubles its proficiency bonus."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "1c2e372ccf52d7b8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "Your magic deepens a creature's understanding of its own talent.",
                    ),
                    ("Target", "One willing creature you touch"),
                    (
                        "Effect",
                        "You give it expertise in one skill of your choice; until the spell ends, the creature doubles its proficiency bonus for ability checks it makes that use the chosen skill",
                    ),
                    (
                        "Requirement",
                        "You must choose a skill in which the target is proficient and that isn't already benefiting from an effect, such as Expertise, that doubles its proficiency bonus",
                    ),
                )
            )
        ]


class SongalsElementalSuffusion(ClassSpell):
    rules = SpellRules(
        name="Songal's Elemental Suffusion",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a pearl worth 100+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Forgotten Realms - Heroes of Faerun",
        description=(
            "You imbue yourself with the elemental power of genies. You gain the following benefits until the spell ends:\n"
            "Elemental Immunity. When you cast this spell, choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. You have Resistance to the chosen damage type.\n"
            "Elemental Pulse. When you cast this spell and at the start of each of your subsequent turns, you release a burst of elemental energy in a 15-foot Emanation originating from yourself. Each creature of your choice in that area makes a Dexterity saving throw. On a failed save, a creature takes 2d6 Acid, Cold, Fire, Lightning, or Thunder damage (your choice) and has the Prone condition. On a successful save, a creature takes half as much damage only.\n"
            "Flight. You gain a Fly Speed of 30 feet and can hover.\n"
            "Casting as a Circle Spell. If the spell is cast as a Circle spell, its casting time increases to 1 minute, and its duration increases to Concentration, up to 10 minutes. For each secondary caster who participates in the casting, you can choose one additional creature, to a maximum of nine additional creatures. The chosen creatures also gain the benefits of the spell for its duration.\n"
            "When the spell is cast, each secondary caster must expend a level 2+ spell slot; otherwise, the spell fails."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ed5c5db86f76dd2f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You imbue yourself with the elemental power of genies.",
                    ),
                    (
                        "Benefits",
                        "You gain the following benefits until the spell ends",
                    ),
                )
            ),
            Option(
                "Elemental Immunity",
                (
                    Facts(
                        (
                            (
                                "Choice",
                                "When you cast this spell, choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder",
                            ),
                            ("Effect", "You have Resistance to the chosen damage type"),
                        )
                    ),
                ),
            ),
            Option(
                "Elemental Pulse",
                (
                    Facts(
                        (
                            (
                                "When",
                                "When you cast this spell and at the start of each of your subsequent turns, you release a burst of elemental energy in a 15-foot Emanation originating from yourself",
                            ),
                            ("Targets", "Each creature of your choice in that area"),
                            ("Save", "Dexterity"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (
                            (
                                "2d6 Acid, Cold, Fire, Lightning, or Thunder damage (your choice) and the Prone condition",
                                "Half as much damage only",
                            ),
                        ),
                    ),
                ),
            ),
            Option(
                "Flight",
                (
                    Facts(
                        (("Effect", "You gain a Fly Speed of 30 feet and can hover"),)
                    ),
                ),
            ),
            Option(
                "Casting as a Circle Spell",
                (
                    Facts(
                        (
                            (
                                "Time",
                                "If the spell is cast as a Circle spell, its casting time increases to 1 minute, and its duration increases to Concentration, up to 10 minutes",
                            ),
                            (
                                "Extra creatures",
                                "For each secondary caster who participates in the casting, you can choose one additional creature, to a maximum of nine additional creatures; the chosen creatures also gain the benefits of the spell for its duration",
                            ),
                            (
                                "Spell slots",
                                "When the spell is cast, each secondary caster must expend a level 2+ spell slot; otherwise, the spell fails",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SpiritLantern(ClassSpell):
    rules = SpellRules(
        name="Spirit Lantern",
        level=5,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.CLERIC,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a black lantern"),
        duration=Duration(DurationType.MINUTE, 10),
        source="Arcana Unleashed",
        description=(
            "You conjure a floating, ghostly black lantern that hovers above you and sheds Dim Light in a 60-foot radius. When an enemy dies within this Dim Light, a fragment of the creature’s soul flies into the lantern. The lantern can hold a number of soul fragments equal to your spellcasting ability modifier, and those fragments dissipate when the spell ends.\n"
            "As a Bonus Action, you can expend a soul fragment to create one of the following effects.\n"
            "Drain Life. The soul fragment darts at a creature of your choice that you can see within 60 feet of yourself. The target makes a Constitution saving throw, taking Necrotic damage equal to 4d8 plus your spellcasting ability modifier on a failed save or half as much damage on a successful one.\n"
            "Repair Undead. The soul fragment flies into an Undead creature of your choice that you can see within 60 feet of yourself. That creature regains Hit Points equal to 4d8 plus your spellcasting ability modifier.\n"
            "Ward Ally. The soul fragment darts around a creature of your choice that you can see within 60 feet of yourself. Other creatures have Disadvantage on attack rolls against the chosen creature until the start of your next turn."
        ),
        usage_tags=("control", "damage", "heal"),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8793b81bb2b400c6")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You conjure a floating, ghostly black lantern that hovers above you and sheds Dim Light in a 60-foot radius.",
                    ),
                    ("Light", "Dim Light in a 60-foot radius"),
                    (
                        "Soul fragments",
                        "When an enemy dies within this Dim Light, a fragment of the creature's soul flies into the lantern",
                    ),
                    (
                        "Capacity",
                        "The lantern can hold a number of soul fragments equal to your spellcasting ability modifier, and those fragments dissipate when the spell ends",
                    ),
                    (
                        "Using",
                        "As a Bonus Action, you can expend a soul fragment to create one of the following effects",
                    ),
                )
            ),
            Option(
                "Drain Life",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "A creature of your choice that you can see within 60 feet of yourself; the soul fragment darts at it",
                            ),
                            ("Save", "Constitution"),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (
                            (
                                "Necrotic damage equal to 4d8 plus your spellcasting ability modifier",
                                "Half as much damage",
                            ),
                        ),
                    ),
                ),
            ),
            Option(
                "Repair Undead",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "An Undead creature of your choice that you can see within 60 feet of yourself; the soul fragment flies into it",
                            ),
                            (
                                "Healing",
                                "That creature regains Hit Points equal to 4d8 plus your spellcasting ability modifier",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Ward Ally",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "A creature of your choice that you can see within 60 feet of yourself; the soul fragment darts around it",
                            ),
                            (
                                "Effect",
                                "Other creatures have Disadvantage on attack rolls against the chosen creature until the start of your next turn",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SteelWindStrike(ClassSpell):
    rules = SpellRules(
        name="Steel Wind Strike",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.RANGER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(somatic=True, material="a Melee weapon worth 1+ SP"),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You flourish the weapon used in the casting and then vanish to strike like the wind. Choose up to five creatures you can see within range. Make a melee spell attack against each target. On a hit, a target takes 6d10 Force damage.\n"
            "You then teleport to an unoccupied space you can see within 5 feet of one of the targets."
        ),
        usage_tags=("buff", "damage"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "9bc5cf5ab40fe233")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You flourish the weapon used in the casting and then vanish to strike like the wind.",
                    ),
                    ("Targets", "Up to five creatures you can see within range"),
                    ("Attack", "Melee spell attack against each target"),
                    ("On a hit", "6d10 Force damage"),
                    (
                        "Teleport",
                        "You then teleport to an unoccupied space you can see within 5 feet of one of the targets",
                    ),
                )
            )
        ]


class SummonCelestial(ClassSpell):
    rules = SpellRules(
        name="Summon Celestial",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.CLERIC, CharacterClass.PALADIN),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="a reliquary worth 500+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth a Celestial spirit. It manifests in an angelic form in an unoccupied space that you can see within range and uses the Celestial Spirit stat block. When you cast the spell, choose Avenger or Defender. Your choice determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "207f65350e267189")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a Celestial spirit."),
            Facts(
                (
                    (
                        "Appears",
                        "In an unoccupied space that you can see within range, manifesting in an angelic form",
                    ),
                    (
                        "Kind",
                        "Avenger or Defender, chosen when you cast the spell; your choice determines certain details in its stat block",
                    ),
                    ("Stat block", "Celestial Spirit (below)"),
                    (
                        "Disappears",
                        "When it drops to 0 Hit Points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            (
                                "Initiative",
                                "It shares your Initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Celestial Spirit",
                (
                    Facts(
                        (
                            ("Type", "Large Celestial"),
                            ("AC", "11 + the spell's level"),
                            ("Hit Points", "40 + 10 for each spell level above 5"),
                            ("Speed", "30 ft., Fly 40 ft."),
                            (
                                "Abilities",
                                "Str 16, Dex 14, Con 16, Int 10, Wis 14, Cha 16",
                            ),
                            ("Resistances", "Radiant"),
                            ("Immunities", "Charmed, Frightened"),
                            ("Senses", "Darkvision 60 ft., Passive Perception 12"),
                            (
                                "Languages",
                                "Celestial, understands the languages you know",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of attacks equal to half this spell's level (round down)",
                            ),
                            (
                                "Radiant Bow",
                                "Avenger only. Ranged Attack Roll: Bonus equals your spell attack modifier, range 600 ft. Hit: 2d6 + 2 + the spell's level Radiant damage",
                            ),
                            (
                                "Radiant Mace",
                                "Defender only. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d10 + 3 + the spell's level Radiant damage, and the spirit can choose itself or another creature it can see within 10 feet of the target. The chosen creature gains 1d10 Temporary Hit Points",
                            ),
                            (
                                "Healing Touch",
                                "1/Day. The spirit touches another creature. The target regains Hit Points equal to 2d8 + the spell's level",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the spell slot's level for the spell's level in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonDraconicSpirit(ClassSpell):
    rules = SpellRules(
        name="Summon Draconic Spirit",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="an object with the image of a dragon engraved on it, worth at least 500 gp",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Fizban's Treasury of Dragons",
        description=(
            "You call forth a draconic spirit. It manifests in an unoccupied space that you can see within range. This corporeal form uses the Draconic Spirit stat block. When you cast this spell, choose a family of dragon: chromatic, gem, or metallic. The creature resembles a dragon of the chosen family, which determines certain traits in its stat block. The creature disappears when it drops to 0 hit points or when the spell ends.\n"
            "The creature is an ally to you and your companions. In combat, the creature shares your initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don't issue any, it takes the Dodge action and uses its move to avoid danger.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 6th level or higher, use the higher level wherever the spell's level appears in the stat block."
        ),
        usage_tags=("utility", "summon"),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "9d80e4c3d0306d5a")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a draconic spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    ("Form", "This corporeal form uses the Draconic Spirit stat block"),
                    (
                        "Family",
                        "Chromatic, gem, or metallic, chosen when you cast this spell; the creature resembles a dragon of the chosen family, which determines certain traits in its stat block",
                    ),
                    (
                        "Stat block",
                        "Draconic Spirit (not included in this spell's data)",
                    ),
                    (
                        "Disappears",
                        "When it drops to 0 hit points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your companions"),
                            (
                                "Initiative",
                                "In combat, the creature shares your initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its move to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the higher level wherever the spell's level appears in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonDragon(ClassSpell):
    rules = SpellRules(
        name="Summon Dragon",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(
            verbal=True,
            somatic=True,
            material="an object with the image of a dragon engraved on it worth 500+ GP",
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You call forth a Dragon spirit. It manifests in an unoccupied space that you can see within range and uses the Draconic Spirit stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "30688c0c977c4d7e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("You call forth a Dragon spirit."),
            Facts(
                (
                    ("Appears", "In an unoccupied space that you can see within range"),
                    ("Stat block", "Draconic Spirit (below)"),
                    (
                        "Disappears",
                        "When it drops to 0 Hit Points or when the spell ends",
                    ),
                )
            ),
            Option(
                "Combat",
                (
                    Facts(
                        (
                            ("Allegiance", "An ally to you and your allies"),
                            (
                                "Initiative",
                                "It shares your Initiative count, but it takes its turn immediately after yours",
                            ),
                            (
                                "Commands",
                                "It obeys your verbal commands (no action required by you); if you don't issue any, it takes the Dodge action and uses its movement to avoid danger",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Draconic Spirit",
                (
                    Facts(
                        (
                            ("Type", "Large Dragon"),
                            ("AC", "14 + the spell's level"),
                            ("Hit Points", "50 + 10 for each spell level above 5"),
                            ("Speed", "30 ft., Fly 60 ft., Swim 30 ft."),
                            (
                                "Abilities",
                                "Str 19, Dex 14, Con 17, Int 10, Wis 14, Cha 14",
                            ),
                            ("Resistances", "Acid, Cold, Fire, Lightning, Poison"),
                            ("Immunities", "Charmed, Frightened, Poisoned"),
                            (
                                "Senses",
                                "Blindsight 30 ft., Darkvision 60 ft., Passive Perception 12",
                            ),
                            (
                                "Languages",
                                "Draconic, understands the languages you know",
                            ),
                            (
                                "Shared Resistances",
                                "When you summon the spirit, choose one of its Resistances. You have Resistance to the chosen damage type until the spell ends",
                            ),
                            (
                                "Multiattack",
                                "The spirit makes a number of Rend attacks equal to half the spell's level (round down), and it uses Breath Weapon",
                            ),
                            (
                                "Rend",
                                "Melee Attack Roll: Bonus equals your spell attack modifier, reach 10 ft. Hit: 1d6 + 4 + the spell's level Piercing damage",
                            ),
                            (
                                "Breath Weapon",
                                "Dexterity saving throw against your spell save DC, each creature in a 30-foot Cone. Failure: 2d6 damage of a type this spirit has Resistance to (your choice when you cast the spell). Success: Half damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Stat block",
                                "Use the spell slot's level for the spell's level in the stat block",
                            ),
                        )
                    ),
                ),
            ),
        ]


class SummonPlant(ClassSpell):
    rules = SpellRules(
        name="Summon Plant",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(
            verbal=True, somatic=True, material="herbs worth 500+ GP"
        ),
        duration=Duration(DurationType.HOUR, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "You call forth the spirit of an animated plant. It manifests in an unoccupied space that you can see within range and uses the Plant Spirit stat block. When you cast the spell, choose Fungus, Tree, or Vine. The creature resembles a plant of the chosen type, which determines certain details in its stat block. The creature disappears when it drops to 0 Hit Points or when the spell ends.\n"
            "The creature is an ally to you and your allies. In combat, the creature shares your Initiative count, but it takes its turn immediately after yours. It obeys your verbal commands (no action required by you). If you don’t issue any, it takes the Dodge action and uses its movement to avoid danger.\n"
            "Using a Higher-Level Spell Slot. Use the spell slot’s level for the spell’s level in the stat block."
        ),
        usage_tags=("summon",),
        target=FeatureTarget.ALLY,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0ee23992a1a29d97")


class SwiftQuiver(ClassSpell):
    rules = SpellRules(
        name="Swift Quiver",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a Quiver worth 1+ GP"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="When you cast the spell and as a Bonus Action until it ends, you can make two attacks with a weapon that fires Arrows or Bolts, such as a Longbow or a Light Crossbow. The spell magically creates the ammunition needed for each attack. Each Arrow or Bolt created by the spell deals damage like a nonmagical piece of ammunition of its kind and disintegrates immediately after it hits or misses.",
        usage_tags=("buff",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "21ffd640d8d49e9e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Attacks",
                        "When you cast the spell and as a Bonus Action until it ends, you can make two attacks with a weapon that fires Arrows or Bolts, such as a Longbow or a Light Crossbow",
                    ),
                    (
                        "Ammunition",
                        "The spell magically creates the ammunition needed for each attack",
                    ),
                    (
                        "Damage",
                        "Each Arrow or Bolt created by the spell deals damage like a nonmagical piece of ammunition of its kind and disintegrates immediately after it hits or misses",
                    ),
                )
            )
        ]


class SynapticStatic(ClassSpell):
    rules = SpellRules(
        name="Synaptic Static",
        level=5,
        school=School.ENCHANTMENT,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="Player's Handbook",
        description=(
            "You cause psychic energy to erupt at a point within range. Each creature in a 20-foot-radius Sphere centered on that point makes an Intelligence saving throw, taking 8d6 Psychic damage on a failed save or half as much damage on a successful one.\n"
            "On a failed save, a target also has muddled thoughts for 1 minute. During that time, it subtracts 1d6 from all its attack rolls and ability checks, as well as any Constitution saving throws to maintain Concentration. The target makes an Intelligence saving throw at the end of each of its turns, ending the effect on itself on a success."
        ),
        usage_tags=("buff", "control", "damage"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "403f6a47542ff256")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You cause psychic energy to erupt at a point within range.",
                    ),
                    ("Point", "A point within range"),
                    ("Area", "20-foot-radius Sphere centered on that point"),
                    ("Save", "Intelligence, made by each creature in the Sphere"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d6 Psychic damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Muddled thoughts",
                        "On a failed save, a target also has muddled thoughts for 1 minute",
                    ),
                    (
                        "Penalty",
                        "During that time, it subtracts 1d6 from all its attack rolls and ability checks, as well as any Constitution saving throws to maintain Concentration",
                    ),
                    (
                        "Repeat save",
                        "Intelligence, made by the target at the end of each of its turns, ending the effect on itself on a success",
                    ),
                )
            ),
        ]


class Telekinesis(ClassSpell):
    rules = SpellRules(
        name="Telekinesis",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "You gain the ability to move or manipulate creatures or objects by thought. When you cast the spell and as a Magic action on your later turns before the spell ends, you can exert your will on one creature or object that you can see within range, causing the appropriate effect below. You can affect the same target round after round or choose a new one at any time. If you switch targets, the prior target is no longer affected by the spell.\n"
            "Creature. You can try to move a Huge or smaller creature. The target must succeed on a Strength saving throw, or you move it up to 30 feet in any direction within the spell’s range. Until the end of your next turn, the creature has the Restrained condition, and if you lift it into the air, it is suspended there. It falls at the end of your next turn unless you use this option on it again and it fails the save.\n"
            "Object. You can try to move a Huge or smaller object. If the object isn’t being worn or carried, you automatically move it up to 30 feet in any direction within the spell’s range.\n"
            "If the object is worn or carried by a creature, that creature must succeed on a Strength saving throw, or you pull the object away and move it up to 30 feet in any direction within the spell’s range.\n"
            "You can exert fine control on objects with your telekinetic grip, such as manipulating a simple tool, opening a door or a container, stowing or retrieving an item from an open container, or pouring the contents from a vial."
        ),
        usage_tags=("control",),
        target=FeatureTarget.CREATURE,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "8c2a75d92c49f38f")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph(
                "You gain the ability to move or manipulate creatures or objects by thought."
            ),
            Facts(
                (
                    (
                        "Using",
                        "When you cast the spell and as a Magic action on your later turns before the spell ends, you can exert your will on one creature or object that you can see within range, causing the appropriate effect below",
                    ),
                    (
                        "Targets",
                        "You can affect the same target round after round or choose a new one at any time; if you switch targets, the prior target is no longer affected by the spell",
                    ),
                )
            ),
            Option(
                "Creature",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "A Huge or smaller creature; you can try to move it",
                            ),
                            ("Save", "Strength"),
                            (
                                "Failed save",
                                "You move it up to 30 feet in any direction within the spell's range",
                            ),
                            ("Successful save", "No effect"),
                            (
                                "Restrained",
                                "Until the end of your next turn, the creature has the Restrained condition, and if you lift it into the air, it is suspended there",
                            ),
                            (
                                "Falls",
                                "It falls at the end of your next turn unless you use this option on it again and it fails the save",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Object",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "A Huge or smaller object; you can try to move it",
                            ),
                            (
                                "Unattended",
                                "If the object isn't being worn or carried, you automatically move it up to 30 feet in any direction within the spell's range",
                            ),
                            (
                                "Worn or carried",
                                "If the object is worn or carried by a creature, that creature must succeed on a Strength saving throw, or you pull the object away and move it up to 30 feet in any direction within the spell's range",
                            ),
                            (
                                "Fine control",
                                "You can exert fine control on objects with your telekinetic grip, such as manipulating a simple tool, opening a door or a container, stowing or retrieving an item from an open container, or pouring the contents from a vial",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TeleportationCircle(ClassSpell):
    rules = SpellRules(
        name="Teleportation Circle",
        level=5,
        school=School.CONJURATION,
        classes=(
            CharacterClass.BARD,
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.MINUTE, 1),
        range=Range(RangeType.FOOT, 10),
        components=Components(
            verbal=True, material="rare inks worth 50+ GP, which the spell consumes"
        ),
        duration=Duration(DurationType.ROUND, 1),
        source="Player's Handbook",
        description=(
            "As you cast the spell, you draw a 5-foot-radius circle on the ground inscribed with sigils that link your location to a permanent teleportation circle of your choice whose sigil sequence you know and that is on the same plane of existence as you. A shimmering portal opens within the circle you drew and remains open until the end of your next turn. Any creature that enters the portal instantly appears within 5 feet of the destination circle or in the nearest unoccupied space if that space is occupied.\n"
            "Many major temples, guildhalls, and other important places have permanent teleportation circles. Each circle includes a unique sigil sequence—a string of runes arranged in a particular pattern.\n"
            "When you first gain the ability to cast this spell, you learn the sigil sequences for two destinations on the Material Plane, determined by the DM. You might learn additional sigil sequences during your adventures. You can commit a new sigil sequence to memory after studying it for 1 minute.\n"
            "You can create a permanent teleportation circle by casting this spell in the same location every day for 365 days."
        ),
        usage_tags=("buff",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e9ad6dd84ecc50ef")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Circle",
                        "As you cast the spell, you draw a 5-foot-radius circle on the ground inscribed with sigils that link your location to a permanent teleportation circle of your choice whose sigil sequence you know and that is on the same plane of existence as you",
                    ),
                    (
                        "Portal",
                        "A shimmering portal opens within the circle you drew and remains open until the end of your next turn",
                    ),
                    (
                        "Travel",
                        "Any creature that enters the portal instantly appears within 5 feet of the destination circle or in the nearest unoccupied space if that space is occupied",
                    ),
                )
            ),
            Option(
                "Sigil Sequences",
                (
                    Facts(
                        (
                            (
                                "Permanent circles",
                                "Many major temples, guildhalls, and other important places have permanent teleportation circles; each circle includes a unique sigil sequence - a string of runes arranged in a particular pattern",
                            ),
                            (
                                "Known",
                                "When you first gain the ability to cast this spell, you learn the sigil sequences for two destinations on the Material Plane, determined by the DM; you might learn additional sigil sequences during your adventures",
                            ),
                            (
                                "Learning",
                                "You can commit a new sigil sequence to memory after studying it for 1 minute",
                            ),
                            (
                                "Creating",
                                "You can create a permanent teleportation circle by casting this spell in the same location every day for 365 days",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TransmuteRock(ClassSpell):
    rules = SpellRules(
        name="Transmute Rock",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID, CharacterClass.WIZARD, CharacterClass.ARTIFICER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="clay and water"),
        duration=Duration(DurationType.UNTIL_DISPELLED),
        source="Xanathar's Guide to Everything",
        description=(
            "You choose an area of stone or mud that you can see that fits within a 40-foot cube and that is within range, and choose one of the following effects.\n"
            "Transmute Rock to Mud. Nonmagical rock of any sort in the area becomes an equal volume of thick and flowing mud that remains for the spell's duration. If you cast the spell on an area of ground, it becomes muddy enough that creatures can sink into it. Each foot that a creature moves through the mud costs 4 feet of movement, and any creature on the ground when you cast the spell must make a Strength saving throw. A creature must also make this save the first time it enters the area on a turn or ends its turn there. On a failed save, a creature sinks into the mud and is restrained, though it can use an action to end the restrained condition on itself by pulling itself free of the mud. If you cast the spell on a ceiling, the mud falls. Any creature under the mud when it falls must make a Dexterity saving throw. A creature takes 4d8 bludgeoning damage on a failed save, or half as much damage on a successful one.\n"
            "Transmute Mud to Rock. Nonmagical mud or quicksand in the area no more than 10 feet deep transforms into soft stone for the spell's duration. Any creature in the mud when it transforms must make a Dexterity saving throw. On a failed save, a creature becomes restrained by the rock. The restrained creature can use an action to try to break free by succeeding on a Strength check (DC 20) or by dealing 25 damage to the rock around it. On a successful save, a creature is shunted safely to the surface to an unoccupied space."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "fbde1e7640530b4e")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Area",
                        "You choose an area of stone or mud that you can see that fits within a 40-foot cube and that is within range",
                    ),
                    ("Effect", "Choose one of the following effects"),
                )
            ),
            Option(
                "Transmute Rock to Mud",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Nonmagical rock of any sort in the area becomes an equal volume of thick and flowing mud that remains for the spell's duration",
                            ),
                            (
                                "Ground",
                                "If you cast the spell on an area of ground, it becomes muddy enough that creatures can sink into it",
                            ),
                            (
                                "Movement",
                                "Each foot that a creature moves through the mud costs 4 feet of movement",
                            ),
                            (
                                "Save",
                                "Strength, made by any creature on the ground when you cast the spell, and by a creature the first time it enters the area on a turn or ends its turn there",
                            ),
                            (
                                "Failed save",
                                "A creature sinks into the mud and is Restrained, though it can use an action to end the Restrained condition on itself by pulling itself free of the mud",
                            ),
                            ("Successful save", "No effect"),
                            (
                                "Ceiling",
                                "If you cast the spell on a ceiling, the mud falls",
                            ),
                            (
                                "Falling mud",
                                "Any creature under the mud when it falls must make a Dexterity saving throw",
                            ),
                        )
                    ),
                    Table(
                        ("Failed save", "Successful save"),
                        (("4d8 Bludgeoning damage", "Half as much damage"),),
                    ),
                ),
            ),
            Option(
                "Transmute Mud to Rock",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Nonmagical mud or quicksand in the area no more than 10 feet deep transforms into soft stone for the spell's duration",
                            ),
                            (
                                "Save",
                                "Dexterity, made by any creature in the mud when it transforms",
                            ),
                            (
                                "Failed save",
                                "A creature becomes Restrained by the rock; the Restrained creature can use an action to try to break free by succeeding on a Strength check (DC 20) or by dealing 25 damage to the rock around it",
                            ),
                            (
                                "Successful save",
                                "A creature is shunted safely to the surface to an unoccupied space",
                            ),
                        )
                    ),
                ),
            ),
        ]


class TreeStride(ClassSpell):
    rules = SpellRules(
        name="Tree Stride",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description=(
            "You gain the ability to enter a tree and move from inside it to inside another tree of the same kind within 500 feet. Both trees must be living and at least the same size as you. You must use 5 feet of movement to enter a tree. You instantly know the location of all other trees of the same kind within 500 feet and, as part of the move used to enter the tree, can either pass into one of those trees or step out of the tree you’re in. You appear in a spot of your choice within 5 feet of the destination tree, using another 5 feet of movement. If you have no movement left, you appear within 5 feet of the tree you entered.\n"
            "You can use this transportation ability only once on each of your turns. You must end each turn outside a tree."
        ),
        usage_tags=("utility",),
        target=FeatureTarget.SELF,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4bddb34584e049d7")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Ability",
                        "You gain the ability to enter a tree and move from inside it to inside another tree of the same kind within 500 feet",
                    ),
                    (
                        "Trees",
                        "Both trees must be living and at least the same size as you",
                    ),
                    ("Entering", "You must use 5 feet of movement to enter a tree"),
                    (
                        "Knowledge",
                        "You instantly know the location of all other trees of the same kind within 500 feet and, as part of the move used to enter the tree, can either pass into one of those trees or step out of the tree you're in",
                    ),
                    (
                        "Exit",
                        "You appear in a spot of your choice within 5 feet of the destination tree, using another 5 feet of movement; if you have no movement left, you appear within 5 feet of the tree you entered",
                    ),
                    (
                        "Limit",
                        "You can use this transportation ability only once on each of your turns",
                    ),
                    ("Turn end", "You must end each turn outside a tree"),
                )
            )
        ]


class WallOfForce(ClassSpell):
    rules = SpellRules(
        name="Wall of Force",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a shard of glass"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "An Invisible wall of force springs into existence at a point you choose within range. The wall appears in any orientation you choose, as a horizontal or vertical barrier or at an angle. It can be free floating or resting on a solid surface. You can form it into a hemispherical dome or a globe with a radius of up to 10 feet, or you can shape a flat surface made up of ten 10-foot-by-10-foot panels. Each panel must be contiguous with another panel. In any form, the wall is 1/4 inch thick and lasts for the duration. If the wall cuts through a creature’s space when it appears, the creature is pushed to one side of the wall (you choose which side).\n"
            "Nothing can physically pass through the wall. It is immune to all damage and can’t be dispelled by Dispel Magic. A Disintegrate spell destroys the wall instantly, however. The wall also extends into the Ethereal Plane and blocks ethereal travel through the wall."
        ),
        usage_tags=("buff", "control"),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "58e67a44e2bc247c")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "An Invisible wall of force springs into existence at a point you choose within range.",
                    ),
                    (
                        "Appears",
                        "An Invisible wall of force, at a point you choose within range",
                    ),
                    (
                        "Orientation",
                        "The wall appears in any orientation you choose, as a horizontal or vertical barrier or at an angle; it can be free floating or resting on a solid surface",
                    ),
                    (
                        "Shape",
                        "You can form it into a hemispherical dome or a globe with a radius of up to 10 feet, or you can shape a flat surface made up of ten 10-foot-by-10-foot panels",
                    ),
                    ("Panels", "Each panel must be contiguous with another panel"),
                    (
                        "Thickness",
                        "In any form, the wall is 1/4 inch thick and lasts for the duration",
                    ),
                    (
                        "Creatures",
                        "If the wall cuts through a creature's space when it appears, the creature is pushed to one side of the wall (you choose which side)",
                    ),
                    ("Barrier", "Nothing can physically pass through the wall"),
                    (
                        "Durability",
                        "It is immune to all damage and can't be dispelled by Dispel Magic; a Disintegrate spell destroys the wall instantly, however",
                    ),
                    (
                        "Ethereal Plane",
                        "The wall also extends into the Ethereal Plane and blocks ethereal travel through the wall",
                    ),
                )
            )
        ]


class WallOfLight(ClassSpell):
    rules = SpellRules(
        name="Wall of Light",
        level=5,
        school=School.EVOCATION,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a hand mirror"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "A shimmering wall of bright light appears at a point you choose within range. The wall appears in any orientation you choose: horizontally, vertically, or diagonally. It can be free floating, or it can rest on a solid surface. The wall can be up to 60 feet long, 10 feet high, and 5 feet thick. The wall blocks line of sight, but creatures and objects can pass through it. It emits bright light out to 120 feet and dim light for an additional 120 feet.\n"
            "When the wall appears, each creature in its area must make a Constitution saving throw. On a failed save, a creature takes 4d8 radiant damage, and it is blinded for 1 minute. On a successful save, it takes half as much damage and isn't blinded. A blinded creature can make a Constitution saving throw at the end of each of its turns, ending the effect on itself on a success.\n"
            "A creature that ends its turn in the wall's area takes 4d8 radiant damage.\n"
            "Until the spell ends, you can use an action to launch a beam of radiance from the wall at one creature you can see within 60 feet of it. Make a ranged spell attack. On a hit, the target takes 4d8 radiant damage. Whether you hit or miss, reduce the length of the wall by 10 feet. If the wall's length drops to 0 feet, the spell ends.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 6th level or higher, the damage increases by 1d8 for each slot level above 5th."
        ),
        usage_tags=("damage", "utility"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "083dfc548f6f4700")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A shimmering wall of bright light appears at a point you choose within range.",
                    ),
                    ("Appears", "At a point you choose within range"),
                    (
                        "Orientation",
                        "The wall appears in any orientation you choose: horizontally, vertically, or diagonally; it can be free floating, or it can rest on a solid surface",
                    ),
                    (
                        "Size",
                        "The wall can be up to 60 feet long, 10 feet high, and 5 feet thick",
                    ),
                    (
                        "Blocking",
                        "The wall blocks line of sight, but creatures and objects can pass through it",
                    ),
                    (
                        "Light",
                        "It emits bright light out to 120 feet and dim light for an additional 120 feet",
                    ),
                    (
                        "Save",
                        "Constitution, made by each creature in its area when the wall appears",
                    ),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "4d8 Radiant damage, and it is Blinded for 1 minute",
                        "Half as much damage and isn't Blinded",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Repeat save",
                        "A Blinded creature can make a Constitution saving throw at the end of each of its turns, ending the effect on itself on a success",
                    ),
                    (
                        "In the wall",
                        "A creature that ends its turn in the wall's area takes 4d8 Radiant damage",
                    ),
                )
            ),
            Option(
                "Beam of Radiance",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "Until the spell ends, you can use an action to launch a beam of radiance from the wall at one creature you can see within 60 feet of it",
                            ),
                            ("Attack", "Ranged spell attack"),
                            ("On a hit", "The target takes 4d8 Radiant damage"),
                            (
                                "Wall shrinks",
                                "Whether you hit or miss, reduce the length of the wall by 10 feet",
                            ),
                            (
                                "Ends",
                                "If the wall's length drops to 0 feet, the spell ends",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "At Higher Levels",
                (Facts((("Damage", "+1d8 for each slot level above 5th"),)),),
            ),
        ]


class WallOfStone(ClassSpell):
    rules = SpellRules(
        name="Wall of Stone",
        level=5,
        school=School.EVOCATION,
        classes=(
            CharacterClass.ARTIFICER,
            CharacterClass.DRUID,
            CharacterClass.SORCERER,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True, material="a cube of granite"),
        duration=Duration(DurationType.MINUTE, 10, concentration=True),
        source="Player's Handbook",
        description=(
            "A nonmagical wall of solid stone springs into existence at a point you choose within range. The wall is 6 inches thick and is composed of ten 10-foot-by-10-foot panels. Each panel must be contiguous with another panel. Alternatively, you can create 10-foot-by-20-foot panels that are only 3 inches thick.\n"
            "If the wall cuts through a creature’s space when it appears, the creature is pushed to one side of the wall (you choose which side). If a creature would be surrounded on all sides by the wall (or the wall and another solid surface), that creature can make a Dexterity saving throw. On a success, it can use its Reaction to move up to its Speed so that it is no longer enclosed by the wall.\n"
            "The wall can have any shape you desire, though it can’t occupy the same space as a creature or object. The wall doesn’t need to be vertical or rest on a firm foundation. It must, however, merge with and be solidly supported by existing stone. Thus, you can use this spell to bridge a chasm or create a ramp.\n"
            "If you create a span greater than 20 feet in length, you must halve the size of each panel to create supports. You can crudely shape the wall to create battlements and the like.\n"
            "The wall is an object made of stone that can be damaged and thus breached. Each panel has AC 15 and 30 Hit Points per inch of thickness, and it has Immunity to Poison and Psychic damage. Reducing a panel to 0 Hit Points destroys it and might cause connected panels to collapse at the DM’s discretion.\n"
            "If you maintain your Concentration on this spell for its full duration, the wall becomes permanent and can’t be dispelled. Otherwise, the wall disappears when the spell ends."
        ),
        usage_tags=("control",),
        target=FeatureTarget.OBJECT,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "0bdfae87c153ee07")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A nonmagical wall of solid stone springs into existence at a point you choose within range.",
                    ),
                    (
                        "Appears",
                        "A nonmagical wall of solid stone, at a point you choose within range",
                    ),
                    (
                        "Panels",
                        "The wall is 6 inches thick and is composed of ten 10-foot-by-10-foot panels; each panel must be contiguous with another panel",
                    ),
                    (
                        "Alternatively",
                        "You can create 10-foot-by-20-foot panels that are only 3 inches thick",
                    ),
                    (
                        "Creatures",
                        "If the wall cuts through a creature's space when it appears, the creature is pushed to one side of the wall (you choose which side)",
                    ),
                    (
                        "Shape",
                        "The wall can have any shape you desire, though it can't occupy the same space as a creature or object",
                    ),
                    (
                        "Support",
                        "The wall doesn't need to be vertical or rest on a firm foundation; it must, however, merge with and be solidly supported by existing stone, so you can use this spell to bridge a chasm or create a ramp",
                    ),
                    (
                        "Long spans",
                        "If you create a span greater than 20 feet in length, you must halve the size of each panel to create supports; you can crudely shape the wall to create battlements and the like",
                    ),
                    (
                        "Permanent",
                        "If you maintain your Concentration on this spell for its full duration, the wall becomes permanent and can't be dispelled; otherwise, the wall disappears when the spell ends",
                    ),
                )
            ),
            Option(
                "Enclosed Creature",
                (
                    Facts(
                        (
                            (
                                "Who",
                                "A creature that would be surrounded on all sides by the wall (or the wall and another solid surface)",
                            ),
                            ("Save", "That creature can make a Dexterity saving throw"),
                            (
                                "Successful save",
                                "It can use its Reaction to move up to its Speed so that it is no longer enclosed by the wall",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "The Wall as an Object",
                (
                    Facts(
                        (
                            (
                                "Object",
                                "The wall is an object made of stone that can be damaged and thus breached",
                            ),
                            (
                                "Each panel",
                                "AC 15 and 30 Hit Points per inch of thickness, and it has Immunity to Poison and Psychic damage",
                            ),
                            (
                                "Destroyed",
                                "Reducing a panel to 0 Hit Points destroys it and might cause connected panels to collapse at the DM's discretion",
                            ),
                        )
                    ),
                ),
            ),
        ]


class WavesOfExhaustion(ClassSpell):
    rules = SpellRules(
        name="Waves of Exhaustion",
        level=5,
        school=School.NECROMANCY,
        classes=(
            CharacterClass.SORCERER,
            CharacterClass.WARLOCK,
            CharacterClass.WIZARD,
        ),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.SELF),
        components=Components(
            verbal=True, somatic=True, material="a piece of dried meat"
        ),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Arcana Unleashed",
        description=(
            "You evoke a nimbus of flickering gray light around your body. For the duration, you can take a Magic action to emit a wave of gray light in a 60-foot Cone. Creatures in that area must succeed on a Constitution saving throw or gain 1 Exhaustion level. This spell can’t increase a creature’s Exhaustion level above 4.\n"
            "Exhaustion levels gained from this spell are removed when the spell ends."
        ),
        usage_tags=("control",),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "e880d26954686d6d")


class WrathOfNature(ClassSpell):
    rules = SpellRules(
        name="Wrath of Nature",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.RANGER),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Xanathar's Guide to Everything",
        description=(
            "You call out to the spirits of nature to rouse them against your enemies. Choose a point you can see within range. The spirits cause trees, rocks, and grasses in a 60-foot cube centered on that point to become animated until the spell ends.\n"
            "Grasses and Undergrowth. Any area of ground in the cube that is covered by grass or undergrowth is difficult terrain for your enemies.\n"
            "Trees. At the start of each of your turns, each of your enemies within 10 feet of any tree in the cube must succeed on a Dexterity saving throw or take 4d6 slashing damage from whipping branches.\n"
            "Roots and Vines. At the end of each of your turns, one creature of your choice that is on the ground in the cube must succeed on a Strength saving throw or become restrained until the spell ends. A restrained creature can use an action to make a Strength (Athletics) check against your spell save DC, ending the effect on itself on a success.\n"
            "Rocks. As a bonus action on your turn, you can cause a loose rock in the cube to launch at a creature you can see in the cube. Make a ranged spell attack against the target. On a hit, the target takes 3d8 nonmagical bludgeoning damage, and it must succeed on a Strength saving throw or fall prone."
        ),
        usage_tags=("control", "damage", "utility"),
        target=FeatureTarget.ENEMY,
    )
    converted_from = RecordStamp("spells_dnd5e.json", "a56da068c1e41b35")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You call out to the spirits of nature to rouse them against your enemies.",
                    ),
                    (
                        "Area",
                        "A 60-foot cube centered on a point you can see within range",
                    ),
                    (
                        "Effect",
                        "The spirits cause trees, rocks, and grasses in the cube to become animated until the spell ends",
                    ),
                )
            ),
            Option(
                "Grasses and Undergrowth",
                (
                    Facts(
                        (
                            (
                                "Terrain",
                                "Any area of ground in the cube that is covered by grass or undergrowth is Difficult Terrain for your enemies",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Trees",
                (
                    Facts(
                        (
                            (
                                "When",
                                "At the start of each of your turns, each of your enemies within 10 feet of any tree in the cube",
                            ),
                            ("Save", "Dexterity"),
                            (
                                "Failed save",
                                "4d6 Slashing damage from whipping branches",
                            ),
                            ("Successful save", "No damage"),
                        )
                    ),
                ),
            ),
            Option(
                "Roots and Vines",
                (
                    Facts(
                        (
                            (
                                "When",
                                "At the end of each of your turns, one creature of your choice that is on the ground in the cube",
                            ),
                            ("Save", "Strength"),
                            ("Failed save", "Restrained until the spell ends"),
                            ("Successful save", "No effect"),
                            (
                                "Escape",
                                "A Restrained creature can use an action to make a Strength (Athletics) check against your spell save DC, ending the effect on itself on a success",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Rocks",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "As a bonus action on your turn, you can cause a loose rock in the cube to launch at a creature you can see in the cube",
                            ),
                            ("Attack", "Ranged spell attack"),
                            (
                                "On a hit",
                                "3d8 nonmagical Bludgeoning damage, and the target must succeed on a Strength saving throw or fall Prone",
                            ),
                        )
                    ),
                ),
            ),
        ]


class YolandesRegalPresence(ClassSpell):
    rules = SpellRules(
        name="Yolande's Regal Presence",
        level=5,
        school=School.ENCHANTMENT,
        classes=(CharacterClass.BARD, CharacterClass.WIZARD),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True, material="a miniature tiara"),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="Player's Handbook",
        description="You surround yourself with unearthly majesty in a 10-foot Emanation. Whenever the Emanation enters the space of a creature you can see and whenever a creature you can see enters the Emanation or ends its turn there, you can force that creature to make a Wisdom saving throw. On a failed save, the target takes 4d6 Psychic damage and has the Prone condition, and you can push it up to 10 feet away. On a successful save, the target takes half as much damage only. A creature makes this save only once per turn.",
        usage_tags=("control", "damage", "heal"),
        target=FeatureTarget.AREA,
    )
    converted_from = RecordStamp("spells_dnd2024.json", "7df03f6281e18804")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "You surround yourself with unearthly majesty in a 10-foot Emanation.",
                    ),
                    ("Area", "10-foot Emanation"),
                    (
                        "Trigger",
                        "Whenever the Emanation enters the space of a creature you can see and whenever a creature you can see enters the Emanation or ends its turn there, you can force that creature to make a Wisdom saving throw",
                    ),
                    ("Save", "Wisdom; a creature makes this save only once per turn"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "4d6 Psychic damage and the Prone condition, and you can push it up to 10 feet away",
                        "Half as much damage only",
                    ),
                ),
            ),
        ]


class TemporalShunt(ClassSpell):
    rules = SpellRules(
        name="Temporal Shunt",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.WIZARD,),
        casting_time=CastingTime(
            CastingTimeType.REACTION,
            trigger="taken when a creature you see makes an attack roll or starts to cast a spell",
        ),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.ROUND, 1),
        source="Explorer's Guide to Wildemount",
        description=(
            "You target the triggering creature, which must succeed on a Wisdom saving throw or vanish, being thrown to another point in time and causing the attack to miss or the spell to be wasted. At the start of its next turn, the target reappears where it was or in the closest unoccupied space. The target doesn't remember you casting the spell or being affected by it.\n"
            "At Higher Levels. When you cast this spell using a spell slot of 6th level or higher, you can target one additional creature for each slot level above 5th. All targets must be within 30 feet of each other."
        ),
        usage_tags=("control",),
        target=FeatureTarget.ENEMY,
        school_note="Dunamancy:Chronurgy",
    )
    converted_from = RecordStamp("spells_dnd5e.json", "ee0966ad3cdc39d8")

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "A creature you see makes an attack roll or starts to cast a spell",
                    ),
                    ("Target", "The triggering creature"),
                    ("Save", "Wisdom"),
                    (
                        "Failed save",
                        "The target vanishes, being thrown to another point in time and causing the attack to miss or the spell to be wasted",
                    ),
                    ("Successful save", "No effect"),
                    (
                        "Returns",
                        "At the start of its next turn, the target reappears where it was or in the closest unoccupied space",
                    ),
                    (
                        "Memory",
                        "The target doesn't remember you casting the spell or being affected by it",
                    ),
                )
            ),
            Option(
                "At Higher Levels",
                (
                    Facts(
                        (
                            (
                                "Targets",
                                "You can target one additional creature for each slot level above 5th",
                            ),
                            (
                                "Distance",
                                "All targets must be within 30 feet of each other",
                            ),
                        )
                    ),
                ),
            ),
        ]


class Bonestorm(ClassSpell):
    rules = SpellRules(
        name="Bonestorm",
        level=5,
        school=School.ABJURATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description="You conjure a whirl of battering bone and gore around yourself. You regain 4d6 Hit Points, and each creature in a 10-foot Emanation originating from you makes a Constitution saving throw. A target takes 4d8 Necrotic damage on a failed save or half as much damage on a successful one.",
        usage_tags=("damage", "heal"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "92e10b0c9332b688")


class DreamFlight(ClassSpell):
    rules = SpellRules(
        name="Dream Flight",
        level=5,
        school=School.ABJURATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.SELF),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "You draw on the magic of the green dragonflight. For the duration, you gain the following benefits.\n"
            "Healing Presence. When you move within 5 feet of a creature, you can restore 5d4 Hit Points to that creature. A creature can regain these Hit Points only once per turn.\n"
            "Wings. You sprout spectral wings from your back if you don’t already have wings. You have a Fly Speed of 60 feet and can hover. In addition, your movement doesn’t provoke Opportunity Attacks."
        ),
        usage_tags=("buff", "heal"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "4c1ddaa8dfcad7b9")


class ExplosiveTrap(ClassSpell):
    rules = SpellRules(
        name="Explosive Trap",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.RANGER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 60),
        components=Components(somatic=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description="An Invisible, intangible trap appears on the ground at a point you choose within range. The first time a creature comes within 5 feet of the trap, the trap explodes in a fiery burst that fills a 20-foot-radius Sphere centered on the trap. The spell ends, and each creature within the Sphere makes a Dexterity saving throw. On a failed save, a creature takes 8d6 Fire damage and, if it is Huge or smaller, is pushed 20 feet straight away from the trap’s location.",
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "5c30e2ee8617ab02")


class Innervate(ClassSpell):
    rules = SpellRules(
        name="Innervate",
        level=5,
        school=School.TRANSMUTATION,
        classes=(CharacterClass.DRUID,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 30),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "A creature of your choice within range gains a level 4 spell slot. The spell slot vanishes after it is expended or the target finishes a Long Rest. It can use this spell slot to cast any spell it has prepared.\n"
            "In addition, you regain one expended use of Wild Shape."
        ),
        usage_tags=("buff",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "ffe482af7d05a25e")


class Rescue(ClassSpell):
    rules = SpellRules(
        name="Rescue",
        level=5,
        school=School.CONJURATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description="You teleport to an unoccupied space you can see within range. One willing creature within 60 feet of the space you left also teleports to an unoccupied space within 5 feet of your destination space.",
        usage_tags=("buff",),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "176ea4bef164b12f")


class ShatteringStar(ClassSpell):
    rules = SpellRules(
        name="Shattering Star",
        level=5,
        school=School.EVOCATION,
        classes=(CharacterClass.SORCERER,),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True, somatic=True),
        duration=Duration(DurationType.INSTANTANEOUS),
        source="World of Warcraft",
        description=(
            "You exhale a bolt of concentrated power at a creature within range. Make a ranged spell attack against the target. On a hit, the target takes 10d8 Force damage, and it takes a –2 penalty to AC until the start of your next turn as clinging frost makes the target’s exterior brittle.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d8 for each spell slot level above 5."
        ),
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "37ecd7df504ee8e0")


class SigilOfChains(ClassSpell):
    rules = SpellRules(
        name="Sigil of Chains",
        level=5,
        school=School.CONJURATION,
        classes=(),
        casting_time=CastingTime(CastingTimeType.ACTION),
        range=Range(RangeType.FOOT, 90),
        components=Components(verbal=True),
        duration=Duration(DurationType.ROUND, 1),
        source="World of Warcraft",
        description="A sigil appears at a point on the ground you can see within range, then erupts in a 20-foot-radius Sphere. Each creature in the Sphere makes a Dexterity saving throw. On a failed save, a creature takes 5d6 Force damage, is pulled up to 10 feet straight toward the sigil, and has the Restrained condition until the end of your next turn. On a successful save, the creature takes half as much damage, and its Speed is reduced by 10 feet until the end of your next turn.",
        usage_tags=("control", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "3c11a0cea518e1e5")


class VoidEruption(ClassSpell):
    rules = SpellRules(
        name="Void Eruption",
        level=5,
        school=School.NECROMANCY,
        classes=(CharacterClass.CLERIC,),
        casting_time=CastingTime(CastingTimeType.BONUS_ACTION),
        range=Range(RangeType.FOOT, 120),
        components=Components(verbal=True),
        duration=Duration(DurationType.MINUTE, 1, concentration=True),
        source="World of Warcraft",
        description=(
            "Shadowy Void energy erupts in a 20-foot-radius Sphere centered on a point you choose within range. Each creature in the Sphere makes a Constitution saving throw, taking 5d6 Necrotic damage on a failed save or half as much damage on a successful one. At the same time, you take on a form of Void that grants you the following benefits for the duration.\n"
            "Void Bolt. As a Bonus Action on your turn, you can hurl a bolt of Void energy at a creature within 60 feet of yourself. Make a ranged spell attack; on a hit, the target takes Necrotic damage equal to 2d6 plus your spellcasting ability modifier.\n"
            "Void Stealth. While you are in an area of Dim Light or Darkness, you have the Invisible condition."
        ),
        usage_tags=("buff", "damage"),
    )
    converted_from = RecordStamp("spells_dnd2024.json", "52dad98edc37fc1c")


SPELLS = [
    AlustrielsMooncloak,
    AnimateObjects,
    AntilifeShell,
    Awaken,
    BanishingSmite,
    BigbysHand,
    Bonestorm,
    CircleOfPower,
    Cloudkill,
    Commune,
    CommuneWithNature,
    ConeOfCold,
    ConjureElemental,
    ConjureVolley,
    ContactOtherPlane,
    Contagion,
    ControlWinds,
    CreateSpelljammingHelm,
    Creation,
    DanseMacabre,
    Dawn,
    DestructiveWave,
    DispelEvilAndGood,
    DominatePerson,
    Dream,
    DreamFlight,
    Enervation,
    ExplosiveTrap,
    FarStep,
    FlameStrike,
    Geas,
    GraveGround,
    GreaterRestoration,
    Hallow,
    HoldMonster,
    HolyWeapon,
    Immolation,
    InfernalCalling,
    Innervate,
    InsectPlague,
    JallarzisStormOfRadiance,
    LegendLore,
    Maelstrom,
    MassCureWounds,
    Mislead,
    ModifyMemory,
    MordenkainensLucubration,
    NegativeEnergyFlood,
    Passwall,
    PlanarBinding,
    RaiseDead,
    RarysTelepathicBond,
    Reincarnate,
    Rescue,
    Scrying,
    Seeming,
    ShatteringStar,
    SigilOfChains,
    SkillEmpowerment,
    SongalsElementalSuffusion,
    SpiritLantern,
    SteelWindStrike,
    SummonCelestial,
    SummonDraconicSpirit,
    SummonDragon,
    SummonPlant,
    SwiftQuiver,
    SynapticStatic,
    Telekinesis,
    TeleportationCircle,
    TemporalShunt,
    TransmuteRock,
    TreeStride,
    VoidEruption,
    WallOfForce,
    WallOfLight,
    WallOfStone,
    WavesOfExhaustion,
    WrathOfNature,
    YolandesRegalPresence,
]
