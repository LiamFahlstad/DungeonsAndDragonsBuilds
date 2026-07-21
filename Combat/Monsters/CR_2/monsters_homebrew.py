from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    Size,
    Skill,
)
from Definitions import Ability


class PriestOfTheBlackTongues(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Priest of the Black Tongues",
            hp=44,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 10,
                Ability.DEXTERITY.short_name: 14,
                Ability.CONSTITUTION.short_name: 12,
                Ability.INTELLIGENCE.short_name: 11,
                Ability.WISDOM.short_name: 16,
                Ability.CHARISMA.short_name: 13,
            },
            saving_throws={Ability.WISDOM.short_name: 5},
            spell_slots={},
            cr="2",
            monster_type="Humanoid (Cultist)",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
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
                MonsterAbility(
                    name="Curse-Throat Wail (Recharge 5-6)",
                    description="The priest looses a rasping shout amplified by the brass throat-tube lashed across its ruined mouth. Each creature in a 15-foot cone must make a DC 13 Wisdom saving throw, taking 10 (3d6) Psychic damage and gaining the Frightened condition until the end of the priest's next turn on a failed save, or half as much damage only on a successful one.",
                ),
                MonsterAbility(
                    name="Spellcasting",
                    description="The priest casts one of the following spells, using Wisdom as the spellcasting ability (spell save DC 13, +5 to hit with spell attacks): At will: Thaumaturgy, Toll the Dead. 2/Day each: Hold Person, Silence. 1/Day: Bestow Curse.",
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
                Ability.STRENGTH.short_name: 10,
                Ability.DEXTERITY.short_name: 16,
                Ability.CONSTITUTION.short_name: 12,
                Ability.INTELLIGENCE.short_name: 12,
                Ability.WISDOM.short_name: 16,
                Ability.CHARISMA.short_name: 11,
            },
            saving_throws={
                Ability.WISDOM.short_name: 5,
                Ability.CONSTITUTION.short_name: 3,
            },
            spell_slots={},
            cr="2",
            monster_type="Humanoid (Yellow Cape)",
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=Size.MEDIUM,
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
                MonsterAbility(
                    name="Chime-Rod",
                    description="Melee Attack Roll: +5, reach 5 ft. Hit: 6 (1d6 + 3) Bludgeoning damage to the throat. The target must succeed on a DC 13 Constitution saving throw or be unable to speak or make sound, including casting spells with a Verbal component, until the end of its next turn.",
                ),
                MonsterAbility(
                    name="Peal of Still Choirs (Recharge 5-6)",
                    description="Sister Lumen rings her cluster of harmonic bells. Each creature of her choice within 20 feet of her must make a DC 13 Wisdom saving throw. On a failed save, a creature takes 7 (2d6) Thunder damage, can't speak or cast spells with a Verbal component until the end of Sister Lumen's next turn, and a creature that was Concentrating on a spell must succeed on a Concentration saving throw or lose Concentration on that spell. On a successful save, a creature takes half as much damage only and suffers no other effect.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Sign of the Covered Mouth",
                    description="Sister Lumen directs up to three willing Yellow Cape allies she can see within 30 feet of her using silent hand signs. Each of them can immediately move up to their Speed or make one weapon attack, without provoking Opportunity Attacks for the movement.",
                ),
            ],
            reactions=[
                MonsterAbility(
                    name="Interrupting Chime (1/Day)",
                    description="When a creature Sister Lumen can see within 30 feet of her begins casting a spell with a Verbal component, she can ring a warning bell. The creature must succeed on a DC 13 Wisdom saving throw or its spell fails and has no effect.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class AccursedGroupLarge(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed Group (Large)",
            hp=80,
            ac=9,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 12,
                Ability.DEXTERITY.short_name: 8,
                Ability.CONSTITUTION.short_name: 12,
                Ability.INTELLIGENCE.short_name: 3,
                Ability.WISDOM.short_name: 6,
                Ability.CHARISMA.short_name: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="2",
            monster_type="Undead",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.HUGE,
            ac_note="",
            hp_formula="16d8+8",
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
            condition_immunities=[Condition.EXHAUSTION, Condition.POISONED],
            senses="darkvision 60 ft., Passive Perception 8",
            languages="Understands the languages its bodies knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Thinning Ranks",
                    description="The Large Group represents a cluster of roughly 6 to 8 Accursed shambling and grasping as a single combatant. The number of Rotten Grasp attacks it can make with Multiattack falls as its bodies are destroyed: 8 attacks while it has 61 or more Hit Points, 6 attacks at 41-60 Hit Points, 4 attacks at 21-40 Hit Points, and 2 attacks at 20 Hit Points or fewer.",
                ),
                MonsterAbility(
                    name="Noc'tra's Failed Bargain",
                    description="If damage reduces the Large Group to 0 Hit Points, it must make a Constitution saving throw (DC 5 plus the damage taken) unless the damage is Radiant or from a Critical Hit. On a successful save, its last husks still standing hold together and the Large Group drops to 1 Hit Point instead.",
                ),
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Large Group has Advantage on saving throws against being frightened and against effects that would move it against its will, as the press of its fellow husks holds the line.",
                ),
                MonsterAbility(
                    name="Directed by the Faithful",
                    description="A priest of Noc'tra within 30 feet of the Large Group can take a Bonus Action to command it, causing the Large Group to immediately take the Attack action or to move up to its Speed toward a point the priest designates. Without such direction, the Large Group can only shamble toward the nearest creature it can sense and attack that creature.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="The Large Group makes a number of Rotten Grasp attacks determined by its Thinning Ranks trait (up to 8).",
                ),
                MonsterAbility(
                    name="Rotten Grasp",
                    description="Melee Attack Roll: +2, reach 5 ft. Hit: 3 (1d6) Bludgeoning damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
