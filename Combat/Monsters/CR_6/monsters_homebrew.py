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
    LegendaryResistance,
    MeleeOrRangedAttack,
    MonsterAbility,
    Multiattack,
    NamedAttackAction,
    SavingThrowEffect,
)
from Core.Definitions import Ability
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    EffectRoll,
)
from Model.Content.CombatModifiers import AttackKind
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent


class TheMouthThatWalks(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Mouth That Walks",
            hp=124,
            ac=13,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 19,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 18,
                Ability.INTELLIGENCE: 7,
                Ability.WISDOM: 11,
                Ability.CHARISMA: 18,
            },
            saving_throws={
                Ability.CONSTITUTION: 7,
            },
            spell_slots={},
            cr="6",
            monster_type=MonsterType.ABERRATION,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.LARGE,
            ac_note="scarred, wound-thick flesh and rusted ritual chains",
            hp_formula="13d10 + 52",
            speed_ground_ft=5,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="The Mouth is bound in ancient chains anchored to the sanctum floor and cannot move more than 10 feet from its anchor point unless the chains are destroyed (AC 20, 30 Hit Points, Immune to Poison and Psychic damage).",
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
                Condition.EXHAUSTION,
                Condition.FRIGHTENED,
                Condition.POISONED,
            ],
            senses="blindsight 60 ft. (blind beyond this radius), Passive Perception 10",
            languages="understands Common and Undercommon but can speak only in broken, overlapping fragments of Noc'tra",
            traits=[
                LegendaryResistance(
                    creature_name="Mouth",
                    uses=1,
                    flavor_note="its ruined mind refusing the concept of a true, final death",
                ),
                MonsterAbility(
                    name="The Ceaseless Litany",
                    description="The wound that was once the Mouth's face and chest never stops speaking splintered fragments of Noc'tra, filling a 20-foot Emanation with a droning, layered horror. A creature that ends its turn within the Emanation begins accumulating the toll of Noc'tra: at the start of each of its turns thereafter, it takes 1d6 Psychic damage for every consecutive round it has ended its turn within the Emanation (maximum 6d6), as the broken litany claws deeper into its mind with every passing moment of exposure. A creature that ends its turn outside the Emanation loses all accumulated rounds, the grip fading once it is out of earshot. A creature that is Deafened is immune to this damage.",
                ),
                MonsterAbility(
                    name="Verge of Unmaking",
                    description="While Bloodied, the wound the Curse tore into the Mouth strains to finish what it started: the Emanation of the Ceaseless Litany increases to 30 feet, and the Mouth's Devouring Maw attack deals an extra 7 (2d6) Necrotic damage.",
                ),
            ],
            actions=[
                DcMonsterAbility(
                    name="Devouring Maw",
                    description="Melee Attack Roll: +7, reach 10 ft. Hit: 26 (4d10 + 4) Piercing damage plus 7 (2d6) Necrotic damage. If the target is Medium or smaller and isn't already grappled by the Mouth, the target is also grappled (escape DC 15) and drawn into the wound: while grappled this way, the target is Restrained, and at the start of each of its turns it takes 7 (2d6) Necrotic damage as the wound convulses around it.",
                ),
                DcMonsterAbility(
                    name="Chain-Wracked Lash (Recharge 5-6)",
                    description="One of the Mouth's anchoring chains tears free of the sanctum floor and lashes out. Melee Attack Roll: +7, reach 15 ft. Hit: 14 (2d10 + 4) Bludgeoning damage, and if the target is Large or smaller, it must succeed on a DC 15 Strength saving throw or be pulled up to 10 feet toward the Mouth.",
                ),
                DcMonsterAbility(
                    name="Noc'tra's Wail (Recharge 5-6)",
                    description="The wound shudders and screams a fragment of Noc'tra outward in a 15-foot Cone. Each creature in the area must succeed on a DC 15 Wisdom saving throw, taking 14 (4d6) Psychic damage and gaining the Frightened condition until the end of the Mouth's next turn on a failed save, or half as much damage only on a successful one.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=1,
            lair_actions=[],
            mythic_actions=[],
        )


class TheHunter(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="The Hunter",
            hp=110,
            ac=15,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 16,
                Ability.DEXTERITY: 16,
                Ability.CONSTITUTION: 16,
                Ability.INTELLIGENCE: 12,
                Ability.WISDOM: 13,
                Ability.CHARISMA: 14,
            },
            saving_throws={
                Ability.CONSTITUTION: 4,
                Ability.WISDOM: 3,
            },
            spell_slots={},
            cr="6",
            monster_type=MonsterType.HUMANOID,
            monster_type_note="Cursebound",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="worn leathers and curse-hardened grey skin",
            hp_formula="13d10 + 39",
            speed_ground_ft=35,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={
                Skill.PERCEPTION: 5,
                Skill.STEALTH: 7,
                Skill.INTIMIDATION: 5,
            },
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
            ],
            damage_immunities=[],
            condition_immunities=[
                Condition.FRIGHTENED,
            ],
            senses="darkvision 60 ft., Passive Perception 15",
            languages="Common, plus a fragment of the old tongue the Curse left behind, which it rarely speaks",
            traits=[
                MonsterAbility(
                    name="Cursebound",
                    description="The Hunter has absorbed the essence of an Accursed creature into its own flesh, marking it with grey skin, blackened teeth, and eyes like dying embers. It has Resistance to Necrotic damage, and it is immune to being Frightened.",
                ),
                DcMonsterAbility(
                    name="Unnerving Calm",
                    description="The Hunter never raises its voice or its guard. It has Advantage on Charisma (Intimidation) checks. In addition, at the start of each of its turns, the Hunter can choose one creature within 10 feet of it that can see it; that creature must succeed on a DC 15 Wisdom saving throw or have Disadvantage on attack rolls against the Hunter until the start of the Hunter's next turn, unnerved by its stillness.",
                ),
                MonsterAbility(
                    name="Curse Sense",
                    description="The Hunter always knows the direction and distance to any Accursed or cursed creature within 60 feet of it, even if that creature is hidden, invisible, or behind total cover, and the Hunter has Advantage on attack rolls against such creatures.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Cursed Kris",
                    description="Melee Attack Roll: +7, reach 5 ft. Hit: 11 (2d6 + 4) Piercing damage plus 7 (2d6) Necrotic damage as the bound curse feeds through the blade.",
                ),
            ],
            bonus_actions=[
                DcMonsterAbility(
                    name="Marked for the Hunt (Recharge 5-6)",
                    description="The Hunter fixes its gaze on one creature it can see within 30 feet. Constitution Saving Throw: DC 15, the target. Failure: The target is Marked until the start of the Hunter's next turn. While a creature is Marked this way, the Hunter's attack rolls against it score a Critical Hit on a roll of 19 or 20, and the Marked creature can't benefit from Invisible or Heavily Obscured against the Hunter.",
                ),
            ],
            reactions=[
                MonsterAbility(
                    name="Predator's Reflexes",
                    description="Trigger: A creature the Hunter can see moves within 5 feet of the Hunter. Response: The Hunter makes one Cursed Kris attack against that creature.",
                ),
            ],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )


class ManifestationOfDurmor(ExtendedCombatantData):
    """Molten avatar of the mountain Durmor: a Huge figure rooted in the
    mountainside that doesn't move, striking with a 15-foot reach and hurling
    lava instead. Built on the official Earth Elemental -- tremorsense, a
    Slam -- scaled to Huge and CR 6 and given the Fire Elemental's fire
    immunity and water weakness, with a Molten Body retaliation trait and an
    Eruption recharge in place of the Fire Elemental's always-on Fiery Aura.

    Fights alongside GoblinKingCR4 (Wrath of Durmor), the two of them alone.
    It makes two Molten Strikes a turn; the King's Royal Command spends its
    Reaction on a third. Its Slams knock foes Prone for the King's Durmor's
    Chosen bonus damage, and its Lava Lobs and Eruption leave lava the King
    walks on unharmed and fights from behind a heat shimmer. Its three
    legendary actions a round go to itself (a Molten Strike, costing all 3)
    or to the King (Lava Path moves him and puts lava under him; Rally the
    King gives him Temporary Hit Points and an attack).

    Tuned as a pair against official CR 6 + CR 4 pairings (the same 3400 XP):
    its stats sit a little under a plain CR 6 so that the synergy (the
    commanded Strike, legendary actions, Prone for the King) brings the
    fight to the hard end of High instead of beyond it."""

    def __init__(self):
        super().__init__(
            combatant_type="Manifestation of Durmor",
            hp=105,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 18,
                Ability.DEXTERITY: 8,
                Ability.CONSTITUTION: 20,
                Ability.INTELLIGENCE: 5,
                Ability.WISDOM: 12,
                Ability.CHARISMA: 8,
            },
            saving_throws={
                Ability.STRENGTH: 7,
                Ability.CONSTITUTION: 8,
                Ability.WISDOM: 4,
            },
            spell_slots={},
            cr="6",
            monster_type=MonsterType.ELEMENTAL,
            monster_type_note="",
            alignment=Alignment.NEUTRAL,
            size=CreatureSize.HUGE,
            ac_note="cooling stone crust",
            hp_formula="10d12 + 40",
            speed_ground_ft=0,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="rooted in the mountainside; it can't move or be moved",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.FIRE], note=""),
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[
                Condition.EXHAUSTION,
                Condition.GRAPPLED,
                Condition.PARALYZED,
                Condition.PETRIFIED,
                Condition.POISONED,
                Condition.PRONE,
                Condition.RESTRAINED,
                Condition.UNCONSCIOUS,
            ],
            senses="Darkvision 60 ft., Tremorsense 60 ft., Passive Perception 11",
            languages="Primordial (Ignan, Terran)",
            traits=[
                MonsterAbility(
                    name="Molten Body",
                    description="A creature that touches the manifestation or hits it with a melee attack while within 5 feet of it takes 3 (1d6) Fire damage. The lava the manifestation leaves is Difficult Terrain, and a creature takes 5 (1d10) Fire damage when it enters lava for the first time on a turn or ends its turn there. Water cracks its crust: for every gallon splashed on it, the manifestation takes 3 (1d6) Cold damage and its AC drops by 2 until the end of its next turn.",
                    combat_effects=(
                        CombatEffect(
                            name="Molten Body",
                            damage=(CombatDamage("1d6", DamageType.FIRE),),
                            trigger=CombatTrigger(
                                TriggerEvent.HIT_BY,
                                optional=False,
                                attacks=AttackKind.MELEE,
                                when="the attacker is within 5 feet of the manifestation",
                            ),
                            notes=("To the creature that hit it in melee.",),
                        ),
                        CombatEffect(
                            name="Lava",
                            damage=(CombatDamage("1d10", DamageType.FIRE),),
                            notes=(
                                "A creature that enters lava for the first time on"
                                " a turn or ends its turn there.",
                                "The Goblin King walks on lava unharmed.",
                            ),
                        ),
                    ),
                ),
            ],
            actions=[
                Multiattack(
                    creature_name="manifestation",
                    attacks_text="two Molten Strike attacks",
                ),
                MeleeOrRangedAttack(
                    name="Molten Strike",
                    attack_bonus=7,
                    reach_ft=15,
                    range_ft=120,
                    dice_count=2,
                    dice_type=DiceType.D6,
                    damage_bonus=4,
                    damage_type=DamageType.BLUDGEONING,
                    additional_ruling="The target also takes 3 (1d6) Fire damage. Slam (melee): if the target is a Large or smaller creature, it has the Prone condition. Lava Lob (ranged): hit or miss, the ground within 5 feet of the target becomes lava until the end of the manifestation's next turn.",
                    combat_effects=(
                        CombatEffect(
                            name="Molten Strike: Slam",
                            roll=EffectRoll.ATTACK,
                            attack_bonus=7,
                            damage=(
                                CombatDamage("2d6 + 4", DamageType.BLUDGEONING),
                                CombatDamage("1d6", DamageType.FIRE),
                            ),
                            conditions=(CombatCondition(Condition.PRONE),),
                            notes=(
                                "Melee, reach 15 ft. Prone only if the target is"
                                " Large or smaller.",
                            ),
                        ),
                        CombatEffect(
                            name="Molten Strike: Lava Lob",
                            roll=EffectRoll.ATTACK,
                            attack_bonus=7,
                            damage=(
                                CombatDamage("2d6 + 4", DamageType.BLUDGEONING),
                                CombatDamage("1d6", DamageType.FIRE),
                            ),
                            notes=(
                                "Ranged, 120 ft. Hit or miss, the ground within 5"
                                " feet of the target becomes lava until the end of"
                                " the manifestation's next turn.",
                            ),
                        ),
                    ),
                ),
                SavingThrowEffect(
                    name="Eruption (Recharge 6)",
                    ability=Ability.DEXTERITY,
                    dc=16,
                    target="each creature in a 20-foot Emanation originating from the manifestation, except Goblins",
                    dice_count=5,
                    dice_type=DiceType.D10,
                    damage_type=DamageType.FIRE,
                    success_effect="Half damage.",
                    extra_ruling="The ground in the Emanation becomes lava until the end of the manifestation's next turn.",
                    combat_effects=(
                        CombatEffect(
                            name="Eruption",
                            roll=EffectRoll.SAVE,
                            save_ability=Ability.DEXTERITY,
                            dc=16,
                            half_on_success=True,
                            damage=(CombatDamage("5d10", DamageType.FIRE),),
                            notes=(
                                "Each creature in a 20-foot Emanation except Goblins.",
                                "The ground there becomes lava until the end of"
                                " the manifestation's next turn.",
                            ),
                        ),
                    ),
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[
                MonsterAbility(
                    name="Lava Path (Costs 1 Action)",
                    description="Lava wells up from the ground in a 10-foot-radius circle centered on a point the manifestation can see within 60 feet of it, and lasts until the end of the manifestation's next turn. If the Goblin King is within 60 feet of the manifestation, he can then move up to half his Speed without provoking Opportunity Attacks.",
                ),
                NamedAttackAction(
                    name="Molten Strike (Costs 3 Actions)",
                    creature_name="manifestation",
                    attack_name="Molten Strike",
                ),
                MonsterAbility(
                    name="Rally the King (Costs 2 Actions)",
                    description="Molten rock armors the Goblin King if he is within 60 feet of the manifestation: he gains 10 Temporary Hit Points and can make one Scimitar attack.",
                    combat_effects=(
                        CombatEffect(
                            name="Rally the King",
                            temp_hp=CombatHitPoints("10"),
                            notes=(
                                "On the Goblin King. He then makes one Scimitar"
                                " attack: roll it from his Scimitar row.",
                            ),
                        ),
                    ),
                ),
            ],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
