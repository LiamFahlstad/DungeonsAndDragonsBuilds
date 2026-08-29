from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    MonsterType,
    Size,
)
from Core.Definitions import Ability, Skill


class Accursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed",
            description="A creature that has been turned byt a curse, driven by a malevolent force.",
            hp=11,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 12,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1/8",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
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
                MonsterAbility(
                    name="Shambling Strike",
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


class FreshAccursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Fresh Accursed",
            description="A newly risen Accursed, still reeling from the trauma of its death and the curse that binds it to this world.",
            hp=11,
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
            size=Size.MEDIUM,
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
            languages="Understands the language it knew in life but can't speak",
            traits=[],
            actions=[
                MonsterAbility(
                    name="1 x Mumbling the Curse",
                    description="Wisdom Save (DC 10): 11 (4d4+1) on failed. The Accursed is Prone after.",
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
            hp=16,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 13,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1/4",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="",
            hp_formula="3d8+3",
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
            languages="Understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Accursed Brute has Advantage on saving throws against being frightened or charmed.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Crushing strike",
                    description="Melee Attack Roll: +3, reach 5 ft. Hit: 5 (1d8 + 1) Bludgeoning damage.",
                ),
                MonsterAbility(
                    name="Grab",
                    description="Melee Attack Roll: +2, reach 5 ft. Hit: 3 (1d4 + 1) Bludgeoning damage. If the target is a Medium or smaller creature, it has the Grappled condition (escape DC 10).",
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
                Ability.STRENGTH: 14,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 15,
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
            size=Size.MEDIUM,
            ac_note="",
            hp_formula="5d8+5",
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
            senses="Passive Perception 10",
            languages="Maybe understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Accursed Brute has Advantage on saving throws against being frightened and against effects that would move it against its will.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="The Accursed Warden makes two Rusted Halberd attacks.",
                ),
                MonsterAbility(
                    name="Rusted Halberd",
                    description="Melee Attack Roll: +4, reach 10 ft. Hit: 5 (1d10) Slashing damage.",
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
            size=Size.MEDIUM,
            ac_note="",
            hp_formula="4d8+2",
            speed_ground_ft=10,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
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
                MonsterAbility(
                    name="Curse-Feeding Mind",
                    description="A creature that starts its turn within 10 feet of the Brain-Bloated Accursed must succeed on a DC 12 Intelligence saving throw or take 3 (1d6) Psychic damage and have Disadvantage on its next attack roll before the end of its turn.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Mind Shatter",
                    description="Ranged Attack Roll: +4, range 30 ft. Hit: 5 (1d8 + 1) Psychic damage.",
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
            size=Size.MEDIUM,
            ac_note="",
            hp_formula="4d8",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERFORMANCE: 4,
                Skill.PERSUASION: 4,
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
                MonsterAbility(
                    name="Manic Strike",
                    description="Melee Attack Roll: +3, reach 5 ft. Hit: 4 (1d6 + 1) Bludgeoning damage.",
                ),
                MonsterAbility(
                    name="Clinging Euphoria",
                    description="Melee Attack Roll: +4, reach 5 ft. Hit: 4 (1d6 + 1) Slashing damage. The target must succeed on a DC 16 Strength or Dexterity saving throw or the Curse-High Accursed attaches to its back. While attached, it moves with the target, cannot be targeted separately, and the target's speed is halved. At the start of the Accursed's turn, the target takes 3 (1d6) Psychic damage. The target can use its action to make a DC 16 Strength (Athletics) or Dexterity (Acrobatics) check to detach it; an adjacent creature can instead make a DC 8 Strength (Athletics) check.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
