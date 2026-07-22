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
from Core.Definitions import Ability


class TheCrownWithoutAKing(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Crown Without a King",
            hp=90,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 4,
                Ability.DEXTERITY.short_name: 18,
                Ability.CONSTITUTION.short_name: 14,
                Ability.INTELLIGENCE.short_name: 14,
                Ability.WISDOM.short_name: 12,
                Ability.CHARISMA.short_name: 20,
            },
            saving_throws={},
            spell_slots={},
            cr="7",
            size=Size.TINY,
            monster_type="Undead",
            alignment=Alignment.LAWFUL_EVIL,
            ac_note="natural armor",
            hp_formula="20d4+40",
            speed_ground_ft=0,
            speed_fly_ft=30,
            speed_climb_ft=None,
            speed_special_rules="hover",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
                DamageTypeEntry(damage_types=[DamageType.PSYCHIC], note=""),
            ],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[
                Condition.CHARMED,
                Condition.FRIGHTENED,
                Condition.PARALYZED,
                Condition.PETRIFIED,
                Condition.POISONED,
                Condition.PRONE,
                Condition.RESTRAINED,
            ],
            senses="Truesight 30 ft., Passive Perception 11",
            languages="telepathy 60 ft., understands all languages known by its current or most recent host",
            traits=[
                MonsterAbility(
                    name="Legendary Resistance (1/Day)",
                    description="If the crown fails a saving throw, it can choose to succeed instead.",
                ),
                MonsterAbility(
                    name="Discorporate",
                    description="If the crown is reduced to 0 Hit Points while worn, it is instead knocked from its host's head and rendered inert for 1 minute, reverting to its dormant floating form when that time expires with all Hit Points restored.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Crown Spike",
                    description="Melee Attack Roll: +7, reach 5 ft. Hit: 9 (2d6 + 2) Piercing damage.",
                ),
                MonsterAbility(
                    name="Coronation (Recharge 5-6)",
                    description="The crown flings itself at a creature it can see within 5 feet, attempting to seize their head. The target must succeed on a DC 16 Charisma saving throw or become the crown's Host: for the next 24 hours, the target is Charmed by the crown and treats the crown's telepathic commands as though they came from a trusted ally, and the crown can take control of the Host's actions on the crown's turn. If the saving throw fails by 5 or more, the Host's own personality is suppressed entirely and it becomes a loyal servant of the Cult of the Curse until the crown is forcibly removed (requires a successful DC 16 Strength check as an action, dealing 10 Force damage to the crown to knock it free).",
                ),
                MonsterAbility(
                    name="Command the Accursed",
                    description="The crown issues a telepathic command to all Undead creatures within 120 feet that are loyal to the Cult of the Curse, granting them advantage on their next attack roll before the end of their next turn.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )


class TheRoadChoir(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Road Choir",
            hp=168,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 20,
                Ability.DEXTERITY.short_name: 6,
                Ability.CONSTITUTION.short_name: 18,
                Ability.INTELLIGENCE.short_name: 4,
                Ability.WISDOM.short_name: 12,
                Ability.CHARISMA.short_name: 20,
            },
            saving_throws={
                Ability.CONSTITUTION.short_name: 7,
                Ability.WISDOM.short_name: 4,
            },
            spell_slots={},
            cr="7",
            monster_type="Undead",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.HUGE,
            ac_note="matted, overlapping husks of flesh, bone, and scavenged plates of armor",
            hp_formula="16d12 + 64",
            speed_ground_ft=20,
            speed_fly_ft=None,
            speed_climb_ft=20,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 4,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
                DamageTypeEntry(damage_types=[DamageType.BLUDGEONING], note=""),
                DamageTypeEntry(damage_types=[DamageType.PIERCING], note=""),
                DamageTypeEntry(damage_types=[DamageType.SLASHING], note=""),
            ],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[
                Condition.EXHAUSTION,
                Condition.POISONED,
                Condition.PRONE,
            ],
            senses="darkvision 60 ft., tremorsense 30 ft., Passive Perception 14",
            languages="understands Common and Undercommon but speaks only in the overlapping, mismatched voices of the dozens fused within it",
            traits=[
                MonsterAbility(
                    name="Legendary Resistance (1/Day)",
                    description="If the Road Choir fails a saving throw, it can choose to succeed instead, the fragments of a hundred stubborn wills refusing to let this body fall to a single failure.",
                ),
                MonsterAbility(
                    name="A Hundred Anchors",
                    description="The Road Choir was once a hunter who broke the law of the list, and Noc'tra twisted that punishment into monstrous scale rather than a single death. The Road Choir has Advantage on saving throws against being Frightened and against any effect that would move it against its will, its dozens of fused bodies far too heavy and far too numerous to easily be turned aside or overwhelmed.",
                ),
                MonsterAbility(
                    name="Endless Reknitting",
                    description="The Road Choir regains 15 Hit Points at the start of its turn if it has at least 1 Hit Point, its many corpses shifting and knitting fresh wounds shut with borrowed flesh. If the Road Choir takes Radiant damage or damage from a Critical Hit, this trait doesn't function at the start of the Road Choir's next turn.",
                ),
                MonsterAbility(
                    name="The Long List",
                    description="The Road Choir remembers scraps of a hundred lives fused into its flesh: half-true directions to safehouses, the names of the dead, and roads Noc'tra has not yet claimed. A creature that spends an action to question the Road Choir, or that remains within 40 feet of it and can hear it without attacking it or moving away for a full turn, hears an answer that may or may not be true. At the end of that creature's turn, it must succeed on a DC 16 Wisdom saving throw or gain 1 stack of Corrupted Hope (maximum 5 stacks). While a creature has 3 or more stacks of Corrupted Hope, it has Disadvantage on Wisdom and Charisma saving throws; while it has 5 stacks, it also has the Frightened condition against every creature except the Road Choir, having learned to trust nothing but the voices that lied to it so sweetly. A creature loses 1 stack of Corrupted Hope whenever it finishes a Long Rest away from the Road Choir's presence.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="The Road Choir makes three Grasping Limb attacks. It can replace one of these attacks with a use of Swallowed Into the Mass.",
                ),
                MonsterAbility(
                    name="Grasping Limb",
                    description="Melee Attack Roll: +8, reach 10 ft. Hit: 12 (2d6 + 5) Bludgeoning damage plus 5 (1d8) Necrotic damage.",
                ),
                MonsterAbility(
                    name="Swallowed Into the Mass",
                    description="Strength Saving Throw: DC 16, one Large or smaller creature within 10 feet. Failure: The target is dragged into the writhing mass of bodies and has the Grappled condition (escape DC 16). Until the grapple ends, the target has the Restrained condition and takes 9 (2d8) Necrotic damage at the start of each of its turns as dozens of dead hands claw at it from every side. The Road Choir can have up to two creatures Grappled by this action at a time.",
                ),
                MonsterAbility(
                    name="Directions to Salvation (Recharge 5-6)",
                    description="The Road Choir calls out in a chorus of overlapping voices, offering true-sounding directions to shelter, safety, or someone the target lost long ago. One creature the Road Choir can see within 90 feet that can hear it must succeed on a DC 16 Wisdom saving throw or have the Charmed condition until the end of its next turn. While Charmed in this way, the target must use its movement on its turn to move as close to the Road Choir as it can by the safest route available to it, and it can't willingly move away from the Road Choir. A creature that succeeds on this saving throw is immune to this Road Choir's Directions to Salvation for the next 24 hours, having caught the lie beneath the layered voices.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )
