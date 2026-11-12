from Core.Definitions import Ability, CreatureSize, DamageType, Skill
from Model.Creatures.Combatants import (
    Alignment,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import (
    DcMonsterAbility,
    DiceType,
    MeleeAttack,
    MonsterAbility,
    Multiattack,
)
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
)
from Model.Content.CombatModifiers import ArmorClass
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent


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


class GoblinKingCR4(ExtendedCombatantData):
    """The Goblin King's second tier (CR 4), grown from GoblinKingCR1.
    Scaled-up take on the official Goblin Boss (CR 1): Scimitar kit pushed to
    CR 4 with a third attack, more HP, and a Royal Command bonus action (in
    place of Nimble Escape) that spends his allies' Reactions.

    Fights alongside ManifestationOfDurmor (Wrath of Durmor), the two of them
    alone: Durmor's Chosen lets him walk the lava it leaves, shields him in a
    heat shimmer while he stands in it, and punishes the creatures its Slams
    knock Prone; Royal Command spends the manifestation's Reaction on a
    Molten Strike."""

    def __init__(self):
        super().__init__(
            combatant_type="Goblin King",
            hp=71,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 12,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 16,
                Ability.INTELLIGENCE: 11,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 14,
            },
            saving_throws={},
            spell_slots={},
            cr="4",
            monster_type=MonsterType.FEY,
            monster_type_note="Goblinoid",
            alignment=Alignment.CHAOTIC_NEUTRAL,
            size=CreatureSize.SMALL,
            ac_note="leather armor, shield",
            hp_formula="11d6 + 33",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={Skill.INTIMIDATION: 4, Skill.STEALTH: 7},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 60 ft., Passive Perception 10",
            languages="Common, Goblin",
            traits=[
                MonsterAbility(
                    name="Durmor's Chosen",
                    description="Durmor's blessing lets the goblin walk on lava and molten rock as if it were solid ground: it isn't Difficult Terrain for the goblin, and the goblin takes no damage from it. While the goblin stands in lava, its shimmering heat gives the goblin a +2 bonus to AC. Once per turn, when the goblin hits a creature that has the Prone condition, the target takes an extra 7 (2d6) damage of the weapon's type.",
                    combat_effects=(
                        CombatEffect(
                            name="Durmor's Chosen: Strike the Fallen",
                            damage=(CombatDamage("2d6", DamageType.SLASHING),),
                            trigger=CombatTrigger(
                                TriggerEvent.HIT,
                                optional=False,
                                once_per_turn=True,
                                when="the target has the Prone condition",
                            ),
                            notes=(
                                "Once per turn, on a hit against a Prone creature.",
                            ),
                        ),
                        CombatEffect(
                            name="Durmor's Chosen: Heat Shimmer",
                            targets_self=True,
                            conditions=(
                                CombatCondition(
                                    "Heat Shimmer", modifiers=(ArmorClass(2),)
                                ),
                            ),
                            notes=(
                                "While the goblin stands in lava: take the badge"
                                " off when it leaves the lava or the lava cools.",
                            ),
                        ),
                    ),
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="goblin",
                    attacks_text="three Scimitar attacks",
                ),
                MeleeAttack(
                    name="Scimitar",
                    attack_bonus=5,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=3,
                    damage_type=DamageType.SLASHING,
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Royal Command",
                    description="The goblin barks an order at up to two allies within 60 feet of it that can hear it: allied goblins or the Manifestation of Durmor. A goblin can take a Reaction to move up to half its Speed and make one weapon attack. The manifestation can take a Reaction to make one Molten Strike attack, melee or ranged.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
