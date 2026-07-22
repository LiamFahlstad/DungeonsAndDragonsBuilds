from Combat.Definitions import (
    Alignment,
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    Size,
)
from Core.Definitions import Ability


class Accursed(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed",
            hp=11,
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
            cr="1/8",
            monster_type="Undead",
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
            senses="darkvision 60 ft., Passive Perception 8",
            languages="Understands the language it knew in life but can't speak",
            traits=[],
            actions=[
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


class AccursedBrute(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed Brute",
            hp=16,
            ac=9,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 13,
                Ability.DEXTERITY.short_name: 8,
                Ability.CONSTITUTION.short_name: 13,
                Ability.INTELLIGENCE.short_name: 3,
                Ability.WISDOM.short_name: 6,
                Ability.CHARISMA.short_name: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1/4",
            monster_type="Undead",
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
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[Condition.EXHAUSTION, Condition.POISONED],
            senses="darkvision 60 ft., Passive Perception 8",
            languages="Understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Accursed Brute has Advantage on saving throws against being frightened and against effects that would move it against its will, as the press of its fellow husks holds the line.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Crushing Grasp",
                    description="Melee Attack Roll: +3, reach 5 ft. Hit: 6 (1d8 + 2) Bludgeoning damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class AccursedWarden(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed Warden",
            hp=27,
            ac=11,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 14,
                Ability.DEXTERITY.short_name: 8,
                Ability.CONSTITUTION.short_name: 14,
                Ability.INTELLIGENCE.short_name: 3,
                Ability.WISDOM.short_name: 6,
                Ability.CHARISMA.short_name: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1/2",
            monster_type="Undead",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="remnants of a guard's ring mail, rotted into the flesh",
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
            senses="darkvision 60 ft., Passive Perception 8",
            languages="Understands the language it knew in life but can't speak",
            traits=[
                MonsterAbility(
                    name="Noc'tra's Failed Bargain",
                    description="If damage reduces the Accursed Warden to 0 Hit Points, it must make a Constitution saving throw (DC 5 plus the damage taken) unless the damage is Radiant or from a Critical Hit. On a successful save, the Accursed Warden drops to 1 Hit Point instead.",
                ),
                MonsterAbility(
                    name="Herd-Bound",
                    description="While within 5 feet of at least one other Accursed creature, the Accursed Warden has Advantage on saving throws against being frightened and against effects that would move it against its will, as the press of its fellow husks holds the line.",
                ),
                MonsterAbility(
                    name="Directed by the Faithful",
                    description="A priest of Noc'tra within 30 feet of the Accursed Warden can take a Bonus Action to command it, causing the Accursed Warden to immediately take the Attack action or to move up to its Speed toward a point the priest designates. Without such direction, the Accursed Warden can only shamble toward the nearest creature it can sense and attack that creature.",
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


class TheLivingSymbolOfNoctra(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Living Symbol of Noc'tra",
            hp=4,
            ac=10,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH.short_name: 8,
                Ability.DEXTERITY.short_name: 8,
                Ability.CONSTITUTION.short_name: 10,
                Ability.INTELLIGENCE.short_name: 6,
                Ability.WISDOM.short_name: 6,
                Ability.CHARISMA.short_name: 4,
            },
            saving_throws={},
            spell_slots={},
            cr="1/8",
            monster_type="Humanoid (Cultist)",
            alignment=Alignment.UNALIGNED,
            size=Size.MEDIUM,
            ac_note="",
            hp_formula="1d8",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
            ],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[Condition.FRIGHTENED],
            senses="Passive Perception 8",
            languages="Understands Common but, throat scarred shut by the curse, can't speak",
            traits=[
                MonsterAbility(
                    name="Empty Vessel",
                    description="The Living Symbol has no will of its own. Unless a Priest or Cantor of Noc'tra is puppeting it (see Puppet of the Symbol), it takes no actions on its turn and can only move up to half its Speed toward the nearest creature it can sense, arms slack and eyes unfocused.",
                ),
                MonsterAbility(
                    name="Puppet of the Symbol",
                    description="A Priest or Cantor of Noc'tra within 60 feet of the Living Symbol can take an Action to seize the tattoos etched into its flesh, forcing the Living Symbol to immediately do one of the following: move up to its Speed in any manner the controller chooses, including crawling, contorting, or being dragged limply through the air; make one Warped Strike; or trigger Noc'tra's Detonation.",
                ),
                MonsterAbility(
                    name="Flesh Not Its Own",
                    description="The Living Symbol has Vulnerability to being charmed, frightened, possessed, or otherwise magically compelled, and automatically fails any saving throw against such an effect created by a Priest or Cantor of Noc'tra. It can't resist, and gains no benefit from being unconscious or restrained against, a Puppet of the Symbol attempt.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Warped Strike (Puppeted Only)",
                    description="Usable only when the Living Symbol is puppeted (see Puppet of the Symbol). Melee Attack Roll: +1, reach 5 ft., as a limb bends unnaturally to strike. Hit: 2 (1d4) Bludgeoning damage.",
                ),
                MonsterAbility(
                    name="Noc'tra's Detonation (Puppeted Only)",
                    description="Usable only when the Living Symbol is puppeted (see Puppet of the Symbol). The tattoos carved into the Living Symbol's flesh flare white-hot and its body ruptures in a burst of curse-magic. Each creature within 15 feet of the Living Symbol must succeed on a DC 13 Constitution saving throw or take 14 (4d6) Necrotic damage, or half as much damage on a success. The Living Symbol dies, its body collapsing into ash scored with the afterimage of the Noc'tra symbol.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
