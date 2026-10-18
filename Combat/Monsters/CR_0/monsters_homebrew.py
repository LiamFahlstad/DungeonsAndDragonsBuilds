from Core.Definitions import Condition, CreatureSize, DamageType
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import (
    DcMonsterAbility,
    DiceType,
    MeleeAttack,
    MonsterAbility,
    Multiattack,
    RangedAttack,
    SavingThrowEffect,
)
from Core.Definitions import Ability, Skill


class Accursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed",
            description="A creature that has been turned byt a curse, driven by a malevolent force.",
            hp=10,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 12,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 5,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1/8",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="",
            hp_formula="2d8+2",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.EXHAUSTION],
            senses="Passive Perception 10",
            languages="Maybe understands the language it knew in life but can't speak",
            traits=[],
            actions=[
                MeleeAttack(
                    name="Smash",
                    attack_bonus=3,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=1,
                    damage_type=DamageType.BLUDGEONING,
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class FreshAccursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Fresh Accursed",
            description="A newly risen Accursed, still reeling from the trauma of its death and the curse that binds it to this world.",
            hp=15,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 12,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 6,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 8,
            },
            saving_throws={},
            spell_slots={},
            cr="1/4",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="",
            hp_formula="4d6",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.EXHAUSTION],
            senses="Passive Perception 10",
            languages="Understands the language it knew in life but can't speak",
            traits=[],
            actions=[
                DcMonsterAbility(
                    name="1 x Mumbling the Curse",
                    description="Wisdom Save (DC 11): 11 (4d4+1) on failed. The Accursed is Prone after.",
                ),
                MeleeAttack(
                    name="Feeble Grasp",
                    attack_bonus=2,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D4,
                    damage_bonus=1,
                    damage_type=DamageType.BLUDGEONING,
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class PhysicalAccursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Physical Accursed",
            description="A more physically imposing Accursed, with a stronger body.",
            hp=13,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 12,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 6,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 8,
            },
            saving_throws={},
            spell_slots={},
            cr="1/4",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="",
            hp_formula="3d8+3",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.EXHAUSTION],
            senses="Passive Perception 10",
            languages="Understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Accursed Brute has Advantage on saving throws against being frightened or charmed.",
                ),
            ],
            actions=[
                MeleeAttack(
                    name="Smash",
                    attack_bonus=4,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=1,
                    damage_type=DamageType.BLUDGEONING,
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class ArmoredAccursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Armored Accursed",
            description="A more physically imposing Accursed, with a stronger body and some crude armor.",
            hp=22,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 13,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 6,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 7,
            },
            saving_throws={},
            spell_slots={},
            cr="1/2",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="",
            hp_formula="5d8+5",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.EXHAUSTION, Condition.POISONED],
            senses="Passive Perception 10",
            languages="Maybe understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Accursed Brute has Advantage on saving throws against being frightened and against effects that would move it against its will.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="Accursed Warden",
                    attacks_text="two Rusted Halberd attacks",
                ),
                MeleeAttack(
                    name="Rusted Halberd",
                    attack_bonus=4,
                    reach_ft=10,
                    dice_count=1,
                    dice_type=DiceType.D10,
                    damage_bonus=0,
                    damage_type=DamageType.SLASHING,
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class BrainBloatedAccursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Brain-Bloated Accursed",
            description="A grotesquely swollen Accursed whose enlarged brain has become a vessel for the Curse. It moves slowly, but seems disturbingly aware of its surroundings.",
            hp=18,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 8,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 15,
                Ability.WISDOM: 14,
                Ability.CHARISMA: 8,
            },
            saving_throws={
                Ability.INTELLIGENCE: 4,
                Ability.WISDOM: 4,
            },
            spell_slots={},
            cr="1/2",
            monster_type=MonsterType.CONSTRUCT,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="",
            hp_formula="4d8+2",
            speed_ground_ft=10,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[
                Condition.EXHAUSTION,
                Condition.POISONED,
            ],
            senses="Passive Perception 12",
            languages="Maybe understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Horde Retaliation",
                    description="When a creature attacks the Brain-Bloated Accursed, each other living Accursed within 5 feet of the attacker can use its reaction to make one melee attack against that creature.",
                ),
                DcMonsterAbility(
                    name="Curse-Feeding Mind",
                    description="A creature that starts its turn within 10 feet of the Brain-Bloated Accursed must succeed on a DC 12 Intelligence saving throw or take 3 (1d6) Psychic damage and have Disadvantage on its next attack roll before the end of its turn.",
                ),
            ],
            actions=[
                RangedAttack(
                    name="Mind Shatter",
                    attack_bonus=4,
                    range_ft=30,
                    dice_count=1,
                    dice_type=DiceType.D8,
                    damage_bonus=1,
                    damage_type=DamageType.PSYCHIC,
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class CurseHighAccursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Curse-High Accursed",
            description="An Accursed intoxicated by the immense vastness of the Curse. It experiences the Curse as overwhelming euphoria, laughing, smiling, and wandering through battle with manic delight.",
            hp=18,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 15,
            },
            saving_throws={
                Ability.CHARISMA: 4,
            },
            spell_slots={},
            cr="1/2",
            monster_type=MonsterType.FEY,
            monster_type_note="",
            alignment=Alignment.CHAOTIC_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="",
            hp_formula="4d8",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERFORMANCE: 2,
                Skill.PERSUASION: 2,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[
                Condition.EXHAUSTION,
                Condition.CHARMED,
            ],
            senses="Passive Perception 10",
            languages="Maybe understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Curse-Drunk Euphoria",
                    description="The Curse-High Accursed has Advantage on saving throws against being frightened. Whenever it succeeds on such a saving throw, it laughs manically and can immediately move up to 10 feet without provoking opportunity attacks.",
                ),
            ],
            actions=[
                MeleeAttack(
                    name="Manic Strike",
                    attack_bonus=3,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=1,
                    damage_type=DamageType.BLUDGEONING,
                ),
                MeleeAttack(
                    name="Clinging Euphoria",
                    attack_bonus=4,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=1,
                    damage_type=DamageType.SLASHING,
                    additional_ruling="The target must succeed on a DC 11 Strength or Dexterity saving throw or the Curse-High Accursed attaches to its back. While attached, it moves with the target, cannot be targeted separately, and the target's speed is halved. At the start of the Accursed's turn, the target takes 3 (1d6) Psychic damage. The target can use its action to make a DC 11 Strength (Athletics) or Dexterity (Acrobatics) check to detach it; an adjacent creature can instead make a DC 8 Strength (Athletics) check.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class HaratCR1_2(ExtendedCombatantData):
    """Young dwarf warrior of Stonehill, son of Clan Leader Harald. Built on the
    official Tough (CR 1/2) -- a single sturdy melee attack, no multiattack --
    with dwarven resilience and a stubbornness trait. Wields Thunder
    (CharacterContent/Items/Weapons/Magic.py): +1 to attack and damage,
    Bludgeoning or Thunder per hit. Thunder's Storm Charges only come from
    hits with its twin, Lightning, so they're left off the stat block.
    First of three tiers that level up with the party: grows into
    HaratCR1 (CR 1) and HaratCR2 (CR 2)."""

    def __init__(self):
        super().__init__(
            combatant_type="Harat, Son of Harald",
            description="Young, headstrong heir of Harald, Clan Leader of the Stonehill dwarves. Too stubborn to retreat, too proud to ask for help.",
            hp=32,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 14,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 9,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 11,
            },
            saving_throws={},
            spell_slots={},
            cr="1/2",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Dwarf",
            alignment=Alignment.LAWFUL_GOOD,
            size=CreatureSize.MEDIUM,
            ac_note="scale mail",
            hp_formula="5d8 + 10",
            speed_ground_ft=25,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={Skill.ATHLETICS: 4},
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 60 ft., Passive Perception 10",
            languages="Common, Dwarvish",
            traits=[
                MonsterAbility(
                    name="Dwarven Resilience",
                    description="Harat has Advantage on saving throws he makes to avoid or end the Poisoned condition.",
                ),
                MonsterAbility(
                    name="Stubborn as Stone",
                    description="Harat has Advantage on saving throws against the Charmed and Frightened conditions, and on Strength checks and saving throws made to resist being shoved, moved, or knocked Prone.",
                ),
            ],
            actions=[
                MeleeAttack(
                    name="Thunder",
                    attack_bonus=5,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=3,
                    damage_type=DamageType.BLUDGEONING,
                    additional_ruling="Harat can choose to deal Thunder damage instead of Bludgeoning damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class DwarfLifeCleric(ExtendedCombatantData):
    """Healer: a simplified level 3 Life Domain Cleric (Dwarf). Its healing
    numbers already include Disciple of Life (+3 Hit Points per heal)."""

    def __init__(self):
        super().__init__(
            combatant_type="Dwarf Life Cleric",
            hp=18,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 8,
                Ability.CONSTITUTION: 10,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 8,
            },
            saving_throws={},
            spell_slots={},
            cr="1/2",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Dwarf, Cleric",
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=CreatureSize.MEDIUM,
            ac_note="scale mail",
            hp_formula="4d8",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.INSIGHT: 3,
                Skill.MEDICINE: 3,
                Skill.RELIGION: 1,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 120 ft., Passive Perception 11",
            languages="Common, Dwarvish",
            traits=[
                MonsterAbility(
                    name="Dwarven Resilience",
                    description="The cleric has Advantage on saving throws it makes to avoid or end the Poisoned condition.",
                ),
            ],
            actions=[
                SavingThrowEffect(
                    name="Sacred Flame",
                    ability=Ability.DEXTERITY,
                    dc=11,
                    target="one creature the cleric can see within 60 feet",
                    dice_count=1,
                    dice_type=DiceType.D8,
                    damage_type=DamageType.RADIANT,
                    success_effect="No damage.",
                ),
                MonsterAbility(
                    name="Life Domain Magic",
                    description="The cleric uses one of the following, each once per day. Cure Wounds: it touches a creature, which regains 13 (2d8 + 4) Hit Points. Bless: up to three creatures it can see within 30 feet add 1d4 to their attack rolls and saving throws for 1 minute (Concentration). Preserve Life: it presents its holy symbol and restores 15 Hit Points, divided as it chooses among any number of Bloodied creatures within 30 feet of it (which can include itself); a creature can't be restored to more than half its Hit Point maximum this way.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Healing Word (2/Day)",
                    description="One creature the cleric can see within 60 feet regains 9 (2d4 + 4) Hit Points.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class ElfDruidOfTheLand(ExtendedCombatantData):
    """Control: a simplified level 3 Circle of the Land Druid (Elf, Polar
    land). Locks targets down with Hold Person and Entangle, slows with Ray of
    Frost, and spends Wild Shape on Land's Aid."""

    def __init__(self):
        super().__init__(
            combatant_type="Elf Druid of the Land",
            hp=18,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 10,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 8,
            },
            saving_throws={},
            spell_slots={},
            cr="1/2",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Elf, Druid",
            alignment=Alignment.NEUTRAL,
            size=CreatureSize.MEDIUM,
            ac_note="leather armor",
            hp_formula="4d8",
            speed_ground_ft=35,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.NATURE: 1,
                Skill.PERCEPTION: 3,
                Skill.SURVIVAL: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 60 ft., Passive Perception 13",
            languages="Common, Druidic, Elvish",
            traits=[
                MonsterAbility(
                    name="Fey Ancestry",
                    description="The druid has Advantage on saving throws it makes to avoid or end the Charmed condition.",
                ),
            ],
            actions=[
                RangedAttack(
                    name="Ray of Frost",
                    attack_bonus=3,
                    range_ft=60,
                    dice_count=1,
                    dice_type=DiceType.D8,
                    damage_type=DamageType.COLD,
                    additional_ruling="The target's Speed is reduced by 10 feet until the start of the druid's next turn.",
                ),
                DcMonsterAbility(
                    name="Circle of the Land Magic",
                    description="The druid uses one of the following. Hold Person (1/Day): one Humanoid it can see within 60 feet must succeed on a DC 11 Wisdom saving throw or have the Paralyzed condition for 1 minute (Concentration), repeating the save at the end of each of its turns and ending the effect on itself on a success. Entangle (1/Day): each creature in a 20-foot square of ground within 90 feet must succeed on a DC 11 Strength saving throw or have the Restrained condition for 1 minute (Concentration); a Restrained creature can take an action to make a DC 11 Strength (Athletics) check, ending the condition on itself on a success, and the area is Difficult Terrain for the duration. Land's Aid (2/Day): each creature of its choice in a 10-foot-radius Sphere centered on a point within 60 feet makes a DC 11 Constitution saving throw, taking 7 (2d6) Necrotic damage on a failure or half as much on a success, and one creature of its choice in the area regains 7 (2d6) Hit Points.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
