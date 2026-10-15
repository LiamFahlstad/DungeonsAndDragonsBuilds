from Core.Definitions import Ability, Condition, CreatureSize, DamageType, Skill
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import (
    DcMonsterAbility,
    DiceType,
    Illumination,
    MeleeAttack,
    MonsterAbility,
    Multiattack,
    RangedAttack,
    SavingThrowEffect,
    SiegeMonster,
)


class MarshalVirel(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Marshal Virel",
            hp=78,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 14,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 11,
                Ability.WISDOM: 13,
                Ability.CHARISMA: 11,
            },
            saving_throws={
                Ability.CONSTITUTION: 3,
                Ability.WISDOM: 2,
            },
            spell_slots={},
            cr="4",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Yellow Cape",
            alignment=Alignment.LAWFUL_NEUTRAL,
            size=CreatureSize.MEDIUM,
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
                DcMonsterAbility(
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


class ManifestationOfDurmor(ExtendedCombatantData):
    """Molten avatar of the mountain Durmor. Built on the official Earth
    Elemental (CR 5) -- Earth Glide, Siege Monster, tremorsense, Slam plus a
    ranged rock attack -- scaled down to CR 4 and
    given the Fire Elemental's fire immunity, Illumination and Water
    Susceptibility, with a Molten Body retaliation trait and an Eruption
    recharge in place of the Fire Elemental's always-on Fiery Aura."""

    def __init__(self):
        super().__init__(
            combatant_type="Manifestation of Durmor",
            hp=110,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 19,
                Ability.DEXTERITY: 8,
                Ability.CONSTITUTION: 17,
                Ability.INTELLIGENCE: 5,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 8,
            },
            saving_throws={},
            spell_slots={},
            cr="4",
            monster_type=MonsterType.ELEMENTAL,
            monster_type_note="",
            alignment=Alignment.NEUTRAL,
            size=CreatureSize.LARGE,
            ac_note="cooling stone crust",
            hp_formula="13d10 + 39",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="burrow 20 ft.",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.FIRE], note=""),
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[
                Condition.EXHAUSTION,
                Condition.PARALYZED,
                Condition.PETRIFIED,
                Condition.POISONED,
                Condition.UNCONSCIOUS,
            ],
            senses="Darkvision 60 ft., Tremorsense 60 ft., Passive Perception 10",
            languages="Primordial (Ignan, Terran)",
            traits=[
                MonsterAbility(
                    name="Earth Glide",
                    description="The manifestation can burrow through nonmagical, unworked earth and stone, leaving a glowing seam of cooling rock behind it.",
                ),
                Illumination(
                    creature_name="manifestation", radius_ft=20, dim_radius_ft=20
                ),
                MonsterAbility(
                    name="Molten Body",
                    description="A creature that touches the manifestation or hits it with a melee attack while within 5 feet of it takes 4 (1d8) Fire damage.",
                ),
                SiegeMonster(creature_name="manifestation"),
                MonsterAbility(
                    name="Water Susceptibility",
                    description="The manifestation takes 3 (1d6) Cold damage for every 5 feet it moves in water or for every gallon of water splashed on it, and its AC drops by 2 until the end of its next turn as its crust cracks.",
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="manifestation",
                    attacks_text="two attacks, using Molten Slam or Lava Lob in any combination",
                ),
                MeleeAttack(
                    name="Molten Slam",
                    attack_bonus=6,
                    reach_ft=10,
                    dice_count=2,
                    dice_type=DiceType.D6,
                    damage_bonus=4,
                    damage_type=DamageType.BLUDGEONING,
                    secondary_dice_count=1,
                    secondary_dice_type=DiceType.D6,
                    secondary_damage_type=DamageType.FIRE,
                ),
                RangedAttack(
                    name="Lava Lob",
                    attack_bonus=6,
                    range_ft=60,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=4,
                    damage_type=DamageType.BLUDGEONING,
                    secondary_dice_count=1,
                    secondary_dice_type=DiceType.D6,
                    secondary_damage_type=DamageType.FIRE,
                    additional_ruling="If the target is a Large or smaller creature, it has the Prone condition.",
                ),
                SavingThrowEffect(
                    name="Eruption (Recharge 5-6)",
                    ability=Ability.DEXTERITY,
                    dc=14,
                    target="each creature in a 15-foot Emanation originating from the manifestation",
                    dice_count=3,
                    dice_type=DiceType.D10,
                    damage_type=DamageType.FIRE,
                    success_effect="Half damage.",
                    extra_ruling="The ground in the Emanation becomes Difficult Terrain until the end of the manifestation's next turn.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
