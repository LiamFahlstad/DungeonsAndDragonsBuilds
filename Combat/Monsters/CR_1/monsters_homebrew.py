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


class CommonCultist(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Common Cultist",
            hp=22,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 11,
                Ability.DEXTERITY: 14,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 9,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 12,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Cultist",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="scavenged padding",
            hp_formula="4d8+4",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.RELIGION: 1,
                Skill.INTIMIDATION: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Passive Perception 10",
            languages="Common",
            traits=[
                MonsterAbility(
                    name="Zealous Communion",
                    description="While a Priest of the Black Tongues or a Cantor of the Black Choir is within 30 feet of the cultist, the cultist fights with the reckless fervor of the newly converted and has Advantage on attack rolls.",
                ),
                MonsterAbility(
                    name="Strength of the Faithful Mob",
                    description="The cultist has Advantage on an attack roll against a creature if at least one of the cultist's allies is within 5 feet of that creature and the ally doesn't have the Incapacitated condition.",
                ),
                MonsterAbility(
                    name="Marked for the Choir",
                    description="Ritual scarring rings the cultist's throat, and its vestments are stitched shut at the collar in imitation of the silence to come. The sight unsettles the faithless, and the cultist has Advantage on Charisma (Intimidation) checks against any creature that can see these markings.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Scavenged Sickle",
                    description="Melee Attack Roll: +4, reach 5 ft. Hit: 5 (1d6 + 2) Slashing damage.",
                ),
                MonsterAbility(
                    name="Scavenged Sling",
                    description="Ranged Attack Roll: +4, range 30/120 ft. Hit: 4 (1d4 + 2) Bludgeoning damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class AccursedGroupOf3(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Accursed Group (3)",
            hp=30,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 14,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 6,
                Ability.WISDOM: 11,
                Ability.CHARISMA: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.LARGE,
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
                    description="30-21: 3 attacks, 20-11: 2 attacks, 10-1: 1 attack. An attack can be either a Smash or a Grab.",
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
                MonsterAbility(
                    name="Grab",
                    description="reach 5 ft. If the target is a Medium or smaller creature, it has the Grappled condition (escape DC 12).",
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


class CurseCracked(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Curse Cracked",
            hp=22,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 8,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 10,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 12,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="unnaturally cracked hide",
            hp_formula="5d8",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[
                DamageTypeEntry(
                    damage_types=[
                        DamageType.BLUDGEONING,
                        DamageType.PIERCING,
                        DamageType.SLASHING,
                    ],
                    note="",
                ),
            ],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.FORCE], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[],
            senses="darkvision 60 ft., Passive Perception 10",
            languages="understands Common but can barely speak, its jaw held together by glowing cracks",
            traits=[
                MonsterAbility(
                    name="Unstable Vessel",
                    description="Whenever the Curse Cracked takes 5 or more Bludgeoning, Piercing, or Slashing damage from a single attack, the fractures spread across its body flare and destabilize. Until the end of its next turn, its Curse Bolt attack has Disadvantage and deals only half damage.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Curse Bolt",
                    description="Ranged Attack Roll: +5, range 60 ft. Hit: 9 (2d6 + 2) Force damage.",
                ),
                MonsterAbility(
                    name="Cracking Surge (Recharge 5-6)",
                    description="The cracks across the Curse Cracked's body flare with searing light. Each creature within 10 feet of it must make a DC 12 Dexterity saving throw, taking 10 (3d6) Force damage on a failed save, or half as much damage on a successful one.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Fractured Step",
                    description="The Curse Cracked dissolves into a spray of glowing cracks and reforms in an unoccupied space it can see within 15 feet. This movement doesn't provoke Opportunity Attacks.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class CurseBodyBroken(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Curse Body Broken",
            hp=32,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 16,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 14,
                Ability.INTELLIGENCE: 6,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 6,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="grotesquely warped bone and hide",
            hp_formula="5d8+10",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[
                DamageTypeEntry(damage_types=[DamageType.PSYCHIC], note=""),
            ],
            damage_resistances=[
                DamageTypeEntry(
                    damage_types=[
                        DamageType.BLUDGEONING,
                        DamageType.PIERCING,
                        DamageType.SLASHING,
                    ],
                    note="",
                ),
            ],
            damage_immunities=[],
            condition_immunities=[],
            senses="darkvision 60 ft., Passive Perception 10",
            languages="understands Common and can speak, though only through Scream of the Trapped",
            traits=[
                MonsterAbility(
                    name="Impossible Anatomy",
                    description="The curse has broken the victim's body into an eldritch shape with no fixed physiology: bones jut at wrong angles and pieces of flesh float apart from one another. Blows that would fell an ordinary creature glance from its disjointed form, granting it Resistance to Bludgeoning, Piercing, and Slashing damage.",
                ),
                MonsterAbility(
                    name="Still Me",
                    description="Whenever the Curse Body Broken takes Psychic damage or fails a saving throw against an effect that would Frighten, Charm, or Stun it, the trapped victim's own will claws its way to the surface for an instant, wrestling control from the curse. It loses its next action and reaction.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Multiattack",
                    description="The Curse Body Broken makes two Eldritch Strike attacks.",
                ),
                MonsterAbility(
                    name="Eldritch Strike",
                    description="Melee Attack Roll: +5, reach 10 ft. Hit: 7 (1d8 + 3) Bludgeoning damage, and the target must succeed on a DC 12 Strength saving throw or have the Prone condition as the impossibly bent limb wrenches it off balance.",
                ),
                MonsterAbility(
                    name="Scream of the Trapped (Recharge 5-6)",
                    description="For one horrible instant, the victim's own voice tears free from the curse's grip in a scream of agony. Each creature within 20 feet that can hear the Curse Body Broken must succeed on a DC 12 Wisdom saving throw or have the Frightened condition until the end of the Curse Body Broken's next turn.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Grasping Mutation",
                    description="Melee Attack Roll: +5, reach 15 ft. Hit: 5 (1d6 + 3) Bludgeoning damage, and the target has the Grappled condition (escape DC 13) if the Curse Body Broken doesn't have another creature grappled with this action.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class CurseMindBroken(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Curse Mind Broken",
            hp=27,
            ac=12,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 11,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 3,
                Ability.CHARISMA: 14,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=Size.MEDIUM,
            ac_note="curse-flesh where a face should be",
            hp_formula="5d8+5",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[
                DamageTypeEntry(damage_types=[DamageType.FORCE], note=""),
            ],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.PSYCHIC], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[Condition.CHARMED, Condition.FRIGHTENED],
            senses="darkvision 60 ft., Passive Perception 6",
            languages="none, save for a ceaseless overlapping whisper of borrowed voices",
            traits=[
                MonsterAbility(
                    name="Leaking Curse",
                    description="Immediately after a creature hits the Curse Mind Broken with a melee attack, raw curse-energy lashes out from the wound. That creature takes 3 (1d6) Psychic damage.",
                ),
                MonsterAbility(
                    name="Broken Mind",
                    description="There is no longer a mind here to break. The Curse Mind Broken can't be Charmed or Frightened, and it has Advantage on saving throws against any other effect that targets the mind.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Mind Lash",
                    description="Ranged Attack Roll: +4, range 30 ft. Hit: 9 (2d6 + 2) Psychic damage.",
                ),
                MonsterAbility(
                    name="Memory Shatter (Recharge 5-6)",
                    description="One creature the Curse Mind Broken can see within 30 feet must succeed on a DC 12 Wisdom saving throw or have the Stunned condition until the end of its next turn, as fragments of stolen memory overwhelm its mind.",
                ),
                MonsterAbility(
                    name="Whispering Madness",
                    description="Each creature within 15 feet of the Curse Mind Broken that can hear its ceaseless whispering has Disadvantage on Concentration saving throws and can't speak or cast spells with a Verbal component clearly enough to be understood.",
                ),
                MonsterAbility(
                    name="Curse Discharge (Recharge 5-6)",
                    description="Raw curse-magic bursts outward in a wave. Each creature within 15 feet of the Curse Mind Broken must make a DC 12 Dexterity saving throw, taking 16 (3d10) Force damage on a failed save, or half as much damage on a successful one.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
