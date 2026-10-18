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
    RangedAttack,
    SavingThrowEffect,
)
from Core.Definitions import Ability


class CommonCultist(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Common Cultist",
            hp=28,
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
            size=CreatureSize.MEDIUM,
            ac_note="scavenged padding",
            hp_formula="5d8+5",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.RELIGION: 1,
                Skill.INTIMIDATION: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
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
                MeleeAttack(
                    name="Scavenged Sickle",
                    attack_bonus=4,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=2,
                    damage_type=DamageType.SLASHING,
                ),
                RangedAttack(
                    name="Scavenged Sling",
                    attack_bonus=4,
                    range_ft=30,
                    long_range_ft=120,
                    dice_count=1,
                    dice_type=DiceType.D4,
                    damage_bonus=2,
                    damage_type=DamageType.BLUDGEONING,
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Fanatic's Surge",
                    description="The cultist recites a fragment of the Black Choir's litany, gaining Advantage on its next attack roll before the end of its turn.",
                ),
            ],
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
                DcMonsterAbility(
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
            hp=26,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 12,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 14,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 11,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="unnaturally cracked hide",
            hp_formula="5d8+5",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[
                DamageTypeEntry(
                    damage_types=[DamageType.BLUDGEONING],
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
                RangedAttack(
                    name="Curse Bolt",
                    attack_bonus=5,
                    range_ft=60,
                    dice_count=2,
                    dice_type=DiceType.D6,
                    damage_bonus=2,
                    damage_type=DamageType.FORCE,
                ),
                DcMonsterAbility(
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
                Ability.DEXTERITY: 12,
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
            size=CreatureSize.MEDIUM,
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
                Multiattack(
                    creature_name="Curse Body Broken",
                    attacks_text="two Eldritch Strike attacks",
                ),
                DcMonsterAbility(
                    name="Eldritch Strike",
                    description="Melee Attack Roll: +5, reach 10 ft. Hit: 7 (1d8 + 3) Bludgeoning damage, and the target must succeed on a DC 12 Strength saving throw or have the Prone condition as the impossibly bent limb wrenches it off balance.",
                ),
                DcMonsterAbility(
                    name="Scream of the Trapped (Recharge 5-6)",
                    description="For one horrible instant, the victim's own voice tears free from the curse's grip in a scream of agony. Each creature within 20 feet that can hear the Curse Body Broken must succeed on a DC 12 Wisdom saving throw or have the Frightened condition until the end of the Curse Body Broken's next turn.",
                ),
            ],
            bonus_actions=[
                DcMonsterAbility(
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
                Ability.WISDOM: 12,
                Ability.CHARISMA: 14,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="curse-flesh where a face should be",
            hp_formula="5d8+5",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
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
                RangedAttack(
                    name="Mind Lash",
                    attack_bonus=5,
                    range_ft=30,
                    dice_count=2,
                    dice_type=DiceType.D6,
                    damage_bonus=2,
                    damage_type=DamageType.PSYCHIC,
                ),
                DcMonsterAbility(
                    name="Memory Shatter (Recharge 5-6)",
                    description="One creature the Curse Mind Broken can see within 30 feet must succeed on a DC 12 Wisdom saving throw or have the Stunned condition until the end of its next turn, as fragments of stolen memory overwhelm its mind.",
                ),
                MonsterAbility(
                    name="Whispering Madness",
                    description="Each creature within 15 feet of the Curse Mind Broken that can hear its ceaseless whispering has Disadvantage on Concentration saving throws and can't speak or cast spells with a Verbal component clearly enough to be understood.",
                ),
                DcMonsterAbility(
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


class HaratCR1(ExtendedCombatantData):
    """Harat's second tier (CR 1), between HaratCR1_2 (CR 1/2, built on
    the official Tough) and HaratCR2 (CR 2, built toward the
    official Berserker). New at this tier: a shield, Multiattack with Thunder,
    and the Shield of Stonehill reaction to protect adjacent allies."""

    def __init__(self):
        super().__init__(
            combatant_type="Harat, Shield of Stonehill",
            description="Harald's son has started to earn his place in the clan: still stubborn, but now he plants himself in front of his friends instead of charging ahead.",
            hp=39,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 15,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 15,
                Ability.INTELLIGENCE: 9,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 11,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Dwarf",
            alignment=Alignment.LAWFUL_GOOD,
            size=CreatureSize.MEDIUM,
            ac_note="scale mail, shield",
            hp_formula="6d8 + 12",
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
                Multiattack(
                    creature_name="Harat",
                    attacks_text="two Thunder attacks",
                    use_article=False,
                ),
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


class GreypawCR1(ExtendedCombatantData):
    """Greypaw's first tier (CR 1), built on the official Dire Wolf (CR 1):
    a single prone-free Bite and the tracker's senses. Grows into GreypawCR2
    (CR 2) and then GreypawCR3 (CR 3, CR_3/monsters_homebrew.py)."""

    def __init__(self):
        super().__init__(
            combatant_type="Greypaw (Young)",
            hp=30,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 16,
                Ability.DEXTERITY: 13,
                Ability.CONSTITUTION: 15,
                Ability.INTELLIGENCE: 3,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 5,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.BEAST,
            monster_type_note="Mutated",
            alignment=Alignment.UNALIGNED,
            size=CreatureSize.LARGE,
            ac_note="Thick Hide",
            hp_formula="4d10 + 8",
            speed_ground_ft=40,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 3,
                Skill.SURVIVAL: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="darkvision 60 ft., keen smell, Passive Perception 13",
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
                MeleeAttack(
                    name="Bite",
                    attack_bonus=5,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D10,
                    damage_bonus=3,
                    damage_type=DamageType.PIERCING,
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class GoblinKingCR1(ExtendedCombatantData):
    """The Goblin King's first tier (CR 1), before he grows into GoblinKingCR3.
    The official Goblin Boss (CR 1) stat block -- Scimitar/Shortbow
    Multiattack and Redirect Attack -- with Royal Command (one goblin) in
    place of Nimble Escape."""

    def __init__(self):
        super().__init__(
            combatant_type="Goblin King (Upstart)",
            hp=21,
            ac=17,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 15,
                Ability.CONSTITUTION: 10,
                Ability.INTELLIGENCE: 10,
                Ability.WISDOM: 8,
                Ability.CHARISMA: 12,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.FEY,
            monster_type_note="Goblinoid",
            alignment=Alignment.CHAOTIC_NEUTRAL,
            size=CreatureSize.SMALL,
            ac_note="chain shirt, shield",
            hp_formula="6d6",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={Skill.INTIMIDATION: 3, Skill.STEALTH: 6},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 60 ft., Passive Perception 9",
            languages="Common, Goblin",
            traits=[],
            actions=[
                Multiattack(
                    creature_name="goblin",
                    attacks_text="two attacks, using Scimitar or Shortbow in any combination",
                ),
                MeleeAttack(
                    name="Scimitar",
                    attack_bonus=4,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=2,
                    damage_type=DamageType.SLASHING,
                    additional_ruling="If the attack roll had Advantage, the target takes an extra 2 (1d4) Slashing damage.",
                ),
                RangedAttack(
                    name="Shortbow",
                    attack_bonus=4,
                    range_ft=80,
                    long_range_ft=320,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=2,
                    damage_type=DamageType.PIERCING,
                    additional_ruling="If the attack roll had Advantage, the target takes an extra 2 (1d4) Piercing damage.",
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Royal Command",
                    description="The goblin barks an order at one allied goblin within 30 feet of it that can hear it. That goblin can take a Reaction to move up to half its Speed and make one weapon attack.",
                ),
            ],
            reactions=[
                MonsterAbility(
                    name="Redirect Attack",
                    description="Trigger: A creature the goblin can see makes an attack roll against it. Response: The goblin chooses a Medium or Small ally within 5 feet of itself. The goblin and that ally swap places, and the ally becomes the target of the attack instead.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class GoliathPaladinOfDevotion(ExtendedCombatantData):
    """Tank: a simplified level 3 Oath of Devotion Paladin (Goliath, Stone Giant
    ancestry). Taunts with Compelled Duel, smites with a radiant longsword and
    soaks hits with Stone's Endurance."""

    def __init__(self):
        super().__init__(
            combatant_type="Goliath Paladin of Devotion",
            hp=38,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 14,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 13,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 12,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Goliath, Paladin",
            alignment=Alignment.LAWFUL_GOOD,
            size=CreatureSize.MEDIUM,
            ac_note="scale mail, shield",
            hp_formula="7d8 + 7",
            speed_ground_ft=35,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.ATHLETICS: 4,
                Skill.INTIMIDATION: 3,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Passive Perception 10",
            languages="Common, Giant",
            traits=[
                MonsterAbility(
                    name="Divine Smite (2/Day)",
                    description="Immediately after the paladin hits a creature with a melee weapon, the target takes an extra 9 (2d8) Radiant damage.",
                ),
            ],
            actions=[
                MeleeAttack(
                    name="Sacred Longsword",
                    attack_bonus=4,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D8,
                    damage_bonus=2,
                    damage_type=DamageType.RADIANT,
                ),
                DcMonsterAbility(
                    name="Compelled Duel (1/Day)",
                    description="The paladin challenges one creature it can see within 30 feet. The target must succeed on a DC 11 Wisdom saving throw or, for 1 minute (Concentration), have Disadvantage on attack rolls against creatures other than the paladin, and must succeed on a DC 11 Wisdom saving throw to willingly move more than 30 feet away from it. The effect ends early if the paladin attacks or casts a spell at another creature.",
                ),
            ],
            bonus_actions=[],
            reactions=[
                MonsterAbility(
                    name="Stone's Endurance (2/Day)",
                    description="When the paladin takes damage, it reduces the damage by 7 (1d12 + 1).",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class OrcAssassin(ExtendedCombatantData):
    """DPS: a simplified level 3 Assassin Rogue (Orc). Strikes first with
    Assassinate, darts in and out with Cunning Action, and shrugs off its
    first killing blow with Relentless Endurance."""

    def __init__(self):
        super().__init__(
            combatant_type="Orc Assassin",
            hp=22,
            ac=14,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 12,
                Ability.INTELLIGENCE: 8,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 10,
            },
            saving_throws={},
            spell_slots={},
            cr="1",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Orc, Rogue",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="leather armor",
            hp_formula="4d8 + 4",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.ACROBATICS: 5,
                Skill.PERCEPTION: 2,
                Skill.STEALTH: 7,
            },
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[],
            condition_immunities=[],
            senses="Darkvision 120 ft., Passive Perception 12",
            languages="Common, Orc, Thieves' Cant",
            traits=[
                MonsterAbility(
                    name="Assassinate and Sneak Attack",
                    description="The assassin has Advantage on Initiative rolls, and during the first round of combat it has Advantage on attack rolls against any creature that hasn't taken a turn yet. Once per turn, it deals an extra 7 (2d6) damage when it hits with a weapon attack that has Advantage, or when the target is within 5 feet of one of its allies that doesn't have the Incapacitated condition.",
                ),
                MonsterAbility(
                    name="Relentless Endurance (1/Day)",
                    description="When the assassin is reduced to 0 Hit Points but not killed outright, it drops to 1 Hit Point instead.",
                ),
            ],
            actions=[
                MeleeAttack(
                    name="Shortsword",
                    attack_bonus=5,
                    reach_ft=5,
                    dice_count=1,
                    dice_type=DiceType.D6,
                    damage_bonus=3,
                    damage_type=DamageType.PIERCING,
                ),
            ],
            bonus_actions=[
                MonsterAbility(
                    name="Cunning Action",
                    description="The assassin takes the Dash, Disengage, or Hide action.",
                ),
            ],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
