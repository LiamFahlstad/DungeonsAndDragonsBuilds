from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    DiceType,
    ExtendedCombatantData,
    MeleeAttack,
    MonsterAbility,
    MonsterType,
    Size,
    Skill,
)
from Core.Definitions import Ability


class MarshalVirel(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Marshal Virel",
            hp=78,
            ac=17,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 14,
                Ability.DEXTERITY: 18,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 13,
                Ability.WISDOM: 16,
                Ability.CHARISMA: 11,
            },
            saving_throws={
                Ability.CONSTITUTION: 4,
                Ability.WISDOM: 5,
            },
            spell_slots={},
            cr="4",
            monster_type=MonsterType.HUMANOID, monster_type_note='Yellow Cape',
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=Size.MEDIUM,
            ac_note="breastplate",
            hp_formula="12d8 + 24",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 5,
                Skill.INSIGHT: 5,
                Skill.STEALTH: 6,
                Skill.ATHLETICS: 4,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Passive Perception 15",
            languages="Common (rarely speaks; communicates primarily through hand signs)",
            traits=[
                MonsterAbility(
                    name="Kill the Scream",
                    description="Virel has Advantage on attack rolls against any creature that, since the end of its last turn, has spoken, cast a spell with a Verbal component, or made any vocal sound.",
                ),
                MonsterAbility(
                    name="Wordless Coordination",
                    description="At the start of each of his turns, Virel can silently direct up to two allies within 30 feet of him that can see him. Each of them has Advantage on the next attack roll or saving throw it makes before the start of Virel's next turn.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="Virel makes two Duelist's Rapier attacks.",
                ),
                MonsterAbility(
                    name="Duelist's Rapier",
                    description="Melee Attack Roll: +6, reach 5 ft. Hit: 11 (1d8 + 6) Piercing damage. If this attack is a critical hit, the target must succeed on a DC 13 Constitution saving throw or have the Silenced condition (it can't speak or cast spells that require a Verbal component) until the end of its next turn.",
                ),
                MeleeAttack(
                    name="Throat Strike (Recharge 5-6)",
                    attack_bonus=6,
                    reach_ft=5,
                    dice_count=2,
                    dice_type=DiceType.D8,
                    damage_bonus=9,
                    damage_type=DamageType.PIERCING,
                    additional_ruling="The target must succeed on a DC 13 Constitution saving throw or have the Silenced condition (it can't speak or cast spells that require a Verbal component) and can't take Reactions until the end of its next turn.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Signal to Strike",
                    description="Virel makes a silent hand signal to one ally within 30 feet that can see him. That ally can immediately use its Reaction to make one weapon attack.",
                ),
            ],
            reactions=[
                MonsterAbility(
                    name="Parry",
                    description="Virel adds 2 to his AC against one melee attack that would hit him, potentially causing it to miss, provided he can see the attacker and is wielding a weapon.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
