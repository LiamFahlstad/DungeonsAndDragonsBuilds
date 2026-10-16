from Core.Definitions import Condition, CreatureSize, DamageType, Skill
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
    SavingThrowEffect,
)
from Core.Definitions import Ability


class PriestOfTheBlackTongues(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Priest of the Black Tongues",
            hp=44,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 13,
                Ability.CHARISMA: 9,
            },
            saving_throws={Ability.WISDOM: 3},
            spell_slots={},
            cr="2",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Cultist",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="leather vestments",
            hp_formula="8d8+8",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.RELIGION: 2,
                Skill.INTIMIDATION: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(
                    damage_types=[DamageType.NECROTIC],
                    note="from the curse's lingering touch",
                ),
            ],
            damage_immunities=[],
            condition_immunities=[Condition.FRIGHTENED],
            senses="darkvision 60 ft., Passive Perception 13",
            languages="Common, Deep Speech",
            traits=[
                MonsterAbility(
                    name="Black Tongue",
                    description="The priest's tongue and teeth were charred black the moment it spoke Noc'tra aloud during the Utterance Ritual and lived. Its voice now cracks and rasps like grinding stone, and it has Advantage on Charisma (Intimidation) checks against any creature that can hear it speak.",
                ),
                MonsterAbility(
                    name="Curse-Marked",
                    description="Having survived a taste of the Great Lich's whisper, the priest's nerves are already broken to the sound of oblivion. It has Resistance to Necrotic damage and cannot be Frightened.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Curse-Etched Stave",
                    description="Melee Attack Roll: +4, reach 5 ft. Hit: 5 (1d6 + 2) Bludgeoning damage plus 7 (2d6) Necrotic damage as curse-fire crawls from the wood into the wound.",
                ),
                DcMonsterAbility(
                    name="Curse-Throat Wail (Recharge 5-6)",
                    description="The priest looses a rasping shout amplified by the brass throat-tube lashed across its ruined mouth. Each creature in a 15-foot cone must make a DC 12 Wisdom saving throw, taking 10 (3d6) Psychic damage and gaining the Frightened condition until the end of the priest's next turn on a failed save, or half as much damage only on a successful one.",
                ),
                DcMonsterAbility(
                    name="Spellcasting",
                    description="The priest casts one of the following spells, using Wisdom as the spellcasting ability (spell save DC 12, +3 to hit with spell attacks): At will: Thaumaturgy, Toll the Dead. 2/Day each: Hold Person, Silence. 1/Day: Bestow Curse.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Command the Accursed",
                    description="The priest chooses any number of Accursed it can see within 30 feet of it. Each chosen Accursed can immediately take the Attack action or move up to its Speed toward a point the priest designates, per the Accursed's Directed by the Faithful trait.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class SisterLumenBellWardenOfStillChoirs(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Sister Lumen, Bell-Warden of Still Choirs",
            hp=44,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 9,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 9,
            },
            saving_throws={
                Ability.WISDOM: 3,
                Ability.CONSTITUTION: 2,
            },
            spell_slots={},
            cr="2",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Yellow Cape",
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=CreatureSize.MEDIUM,
            ac_note="muffling wraps and leather vestments",
            hp_formula="8d8+8",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.STEALTH: 5,
                Skill.PERCEPTION: 5,
                Skill.INSIGHT: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Passive Perception 15",
            languages="Common (cannot speak; communicates only through hand signs)",
            traits=[
                MonsterAbility(
                    name="Vow of the Cut Tongue",
                    description="Sister Lumen's tongue was cut in her own order's rite and she cannot speak. She is immune to any effect that requires her to speak, such as a spell with a Verbal component she must recite aloud or a compulsion that demands she answer.",
                ),
                MonsterAbility(
                    name="Attuned to the Choir",
                    description="Sister Lumen has Advantage on Wisdom (Perception) checks that rely on hearing, and she can pinpoint the location of any creature within 60 feet of her that has spoken, chanted, or cast a spell with a Verbal component within the last minute.",
                ),
            ],
            actions=[
                DcMonsterAbility(
                    name="Chime-Rod",
                    description="Melee Attack Roll: +5, reach 5 ft. Hit: 6 (1d6 + 3) Bludgeoning damage to the throat. The target must succeed on a DC 12 Constitution saving throw or be unable to speak or make sound, including casting spells with a Verbal component, until the end of its next turn.",
                ),
                DcMonsterAbility(
                    name="Peal of Still Choirs (Recharge 5-6)",
                    description="Sister Lumen rings her cluster of harmonic bells. Each creature of her choice within 20 feet of her must make a DC 12 Wisdom saving throw. On a failed save, a creature takes 7 (2d6) Thunder damage, can't speak or cast spells with a Verbal component until the end of Sister Lumen's next turn, and a creature that was Concentrating on a spell must succeed on a Concentration saving throw or lose Concentration on that spell. On a successful save, a creature takes half as much damage only and suffers no other effect.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Sign of the Covered Mouth",
                    description="Sister Lumen directs up to three willing Yellow Cape allies she can see within 30 feet of her using silent hand signs. Each of them can immediately move up to their Speed or make one weapon attack, without provoking Opportunity Attacks for the movement.",
                ),
            ],
            reactions=[
                DcMonsterAbility(
                    name="Interrupting Chime (1/Day)",
                    description="When a creature Sister Lumen can see within 30 feet of her begins casting a spell with a Verbal component, she can ring a warning bell. The creature must succeed on a DC 12 Wisdom saving throw or its spell fails and has no effect.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class AccursedGroupOf5(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed Group (5)",
            hp=50,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 15,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 7,
                Ability.WISDOM: 11,
                Ability.CHARISMA: 7,
            },
            saving_throws={},
            spell_slots={},
            cr="2",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.LARGE,
            ac_note="",
            hp_formula="8d6+4",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[Condition.GRAPPLED, Condition.RESTRAINED],
            senses="darkvision 60 ft., Passive Perception 10",
            languages="Understands the languages its bodies knew in life but can't speak",
            traits=[],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="50-41: 5 attacks, 40-31: 4 attacks, 30-21: 3 attacks, 20-11: 2 attacks, 10-1: 1 attack. An attack can be either a Smash or a Grab.",
                ),
                MeleeAttack(
                    name="Smash",
                    attack_bonus=4,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=1,
                    damage_type=DamageType.BLUDGEONING,
                ),
                DcMonsterAbility(
                    name="Grab",
                    description="reach 5 ft. If the target is a Medium or smaller creature, it has the Grappled condition (escape DC 13).",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Rush",
                    description="The Accursed Group of 3 can dash as a bonus action on it's first turn of combat.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class HaratCR2(ExtendedCombatantData):
    """Harat's third tier (CR 2), built toward the official Berserker (CR 2)'s
    durability while keeping his shield. Keeps everything from
    HaratCR1 (CR 1) and adds Thunderclap (a recharge area
    shove that finally taps Thunder's namesake damage) and Too Stubborn to
    Fall."""

    def __init__(self):
        super().__init__(
            combatant_type="Harat, Thunder of Stonehill",
            description="Harat has grown into the hammer his father entrusted him with. When Thunder strikes the ground, the whole battle line hears it.",
            hp=45,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 16,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 16,
                Ability.INTELLIGENCE: 9,
                Ability.WISDOM: 11,
                Ability.CHARISMA: 11,
            },
            saving_throws={},
            spell_slots={},
            cr="2",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Dwarf",
            alignment=Alignment.LAWFUL_GOOD,
            size=CreatureSize.MEDIUM,
            ac_note="scale mail, shield",
            hp_formula="6d8 + 18",
            speed_ground_ft=25,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={Skill.ATHLETICS: 5},
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
                MonsterAbility(
                    name="Too Stubborn to Fall (1/Day)",
                    description="If Harat would be reduced to 0 Hit Points but not killed outright, he drops to 1 Hit Point instead.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="Harat",
                    attacks_text="two Thunder attacks",
                    use_article=False,
                ),
                MeleeAttack(
                    name="Thunder",
                    attack_bonus=6,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=4,
                    damage_type=DamageType.BLUDGEONING,
                    additional_ruling="Harat can choose to deal Thunder damage instead of Bludgeoning damage.",
                ),
                SavingThrowEffect(
                    name="Thunderclap (Recharge 5-6)",
                    ability=Ability.CONSTITUTION,
                    dc=13,
                    target="each creature of Harat's choice in a 10-foot Emanation originating from him",
                    dice_count=2,
                    dice_type=DiceType.D8,
                    damage_type=DamageType.THUNDER,
                    failure_effect="and the target is pushed 10 feet straight away from Harat and has the Prone condition",
                    success_effect="Half damage only.",
                ),
            ],
            bonus_actions=[],
            reactions=[
                MonsterAbility(
                    name="Shield of Stonehill",
                    description="Trigger: A creature Harat can see makes an attack roll against an ally within 5 feet of him. Response: Harat interposes his shield, imposing Disadvantage on the attack roll.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class GreypawCR2(ExtendedCombatantData):
    """Greypaw's second tier (CR 2), between GreypawCR1 (CR 1, built on the
    official Dire Wolf) and GreypawCR3 (CR 3). New at this tier: Multiattack
    (two Bites) and the Bite's knock-Prone rider. Bloodied Frenzy and the
    heavier 2d8 Bite come at CR 3."""

    def __init__(self):
        super().__init__(
            combatant_type="Greypaw (Grown)",
            hp=52,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 17,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 16,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 13,
                Ability.CHARISMA: 5,
            },
            saving_throws={
                Ability.STRENGTH: 5,
            },
            spell_slots={},
            cr="2",
            monster_type=MonsterType.BEAST,
            monster_type_note="Mutated",
            alignment=Alignment.UNALIGNED,
            size=CreatureSize.LARGE,
            ac_note="Thick Hide",
            hp_formula="7d10 + 14",
            speed_ground_ft=40,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 5,
                Skill.SURVIVAL: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="darkvision 60 ft., keen smell, Passive Perception 15",
            languages="None",
            traits=[
                MonsterAbility(
                    name="Keen Hearing and Smell",
                    description="Greypaw has advantage on Wisdom (Perception) checks that rely on hearing or smell.",
                ),
                MonsterAbility(
                    name="Relentless Tracker",
                    description="Greypaw has advantage on Wisdom (Survival) checks made to track creatures. It can identify a creature by scent after smelling something it touched or wore.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="Greypaw",
                    attacks_text="two Bite attacks",
                    use_article=False,
                ),
                MeleeAttack(
                    name="Bite",
                    attack_bonus=5,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D8,
                    damage_bonus=3,
                    damage_type=DamageType.PIERCING,
                    additional_ruling="If the target is a Medium or smaller creature, it must succeed on a DC 12 Strength saving throw or be knocked Prone.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
