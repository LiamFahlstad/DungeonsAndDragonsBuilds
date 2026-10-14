from Core.Definitions import (
    ARTIFICER_HIT_DIE,
    Ability,
    CharacterClass,
    Condition,
    CreatureSize,
    DamageType,
)
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import MonsterAbility
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
)
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    dc_formula,
    StatBlock,
)


class ReanimatorSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Reanimator Spells", origin="Reanimator Artificer Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach an Artificer level specified in the Reanimator Spells table, you thereafter always have the listed spells prepared.\n"
            "Reanimator Spells\n"
            "Artificer Level	Spells\n"
            "3	False Life, Spare the Dying, Witch Bolt\n"
            "5	Blindness/Deafness, Enhance Ability\n"
            "9	Animate Dead, Lightning Bolt\n"
            "13	Blight, Death Ward\n"
            "17	Antilife Shell, Raise Dead"
        )
        return description


class ReanimatorSkillSet(Feature):
    def __init__(self):
        super().__init__(
            name="Reanimator's Skill Set",
            origin="Reanimator Artificer Level 3",
            activation=FeatureActivation(range="10-Foot Emanation"),
            usage_tags=["heal", "damage", "utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Jolt to Life's uses are in the panel below.
        return [
            Option(
                "Jolt to Life",
                (
                    Facts(
                        (
                            ("Trigger", "You cast Spare the Dying"),
                            (
                                "Heal",
                                "The target regains Hit Points equal to your Artificer level",
                            ),
                            (
                                "Area",
                                "Each creature of your choice in a 10-foot Emanation from the target",
                            ),
                            (
                                "Save",
                                f"Dexterity save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)}): 2d4 Lightning damage (3d4 from Artificer level 11, 4d4 from 17); half on a success",
                            ),
                            (
                                "Uses",
                                "Intelligence modifier (minimum once) per Long Rest",
                            ),
                        )
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Reanimator's Tools",
                        "Proficiency with Alchemist's Supplies, or another Artisan's Tools if you already have it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Jolt to Life. When you cast Spare the Dying, you can modify the spell so that it sends a jolt of electricity through the target, reviving it. The target regains a number of Hit Points equal to your Artificer level, and each creature of your choice in a 10-foot Emanation originating from the target makes a Dexterity saving throw against your spell save DC, taking 2d4 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "You can modify the spell this way a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest. The Lightning damage of this feature increases by 1d4 when you reach Artificer levels 11 (3d4) and 17 (4d4).\n"
            "Reanimator's Tools. You gain proficiency with Alchemist's Supplies. If you already have this proficiency, you gain proficiency with one other type of Artisan's Tools of your choice."
        )
        return description


def _build_reanimated_companion(character: CharacterView) -> ExtendedCombatantData:
    artificer_level = character.get_class_level(CharacterClass.ARTIFICER)
    intelligence_modifier = character.get_intelligence_modifier()
    spell_attack = character.calculate_attack_bonus_for_ability(Ability.INTELLIGENCE)
    spell_save_dc = character.calculate_difficulty_class_for_ability(
        Ability.INTELLIGENCE
    )
    proficiency_bonus = character.get_proficiency_bonus()
    death_burst_dice = "4d4" if character.has_feature(ImprovedReanimation) else "2d4"

    return ExtendedCombatantData(
        combatant_type="Reanimated Companion",
        hp=5 + 5 * artificer_level,
        ac=10 + intelligence_modifier,
        temp_hp=0,
        conditions=[],
        ability_scores={
            Ability.STRENGTH: 11,
            Ability.DEXTERITY: 10,
            Ability.CONSTITUTION: 16,
            Ability.INTELLIGENCE: 4,
            Ability.WISDOM: 10,
            Ability.CHARISMA: 6,
        },
        saving_throws={
            Ability.STRENGTH: 0,
            Ability.DEXTERITY: 0,
            Ability.CONSTITUTION: 3,
            Ability.INTELLIGENCE: -3,
            Ability.WISDOM: 0,
            Ability.CHARISMA: -2,
        },
        spell_slots={},
        cr="None",
        monster_type=MonsterType.UNDEAD,
        alignment=Alignment.NEUTRAL,
        size=CreatureSize.MEDIUM,
        description=(
            f"XP 0; PB equals your Proficiency Bonus (currently +{proficiency_bonus}). "
            "Your Strange Modifications choices (Ferocity, Bloated, Gaunt, Moist) change this card as described in those features."
        ),
        hp_formula=f"5 + five times your Artificer level; {artificer_level}d8 Hit Dice",
        speed_ground_ft=30,
        damage_resistances=[
            DamageTypeEntry(damage_types=[DamageType.NECROTIC, DamageType.POISON])
        ],
        damage_immunities=[DamageTypeEntry(damage_types=[DamageType.LIGHTNING])],
        condition_immunities=[
            Condition.CHARMED,
            Condition.EXHAUSTION,
            Condition.POISONED,
        ],
        senses="Blindsight 60 ft.; Passive Perception 10",
        languages="Understands the languages you know",
        traits=[
            MonsterAbility(
                name="Death Burst",
                description=(
                    "The companion explodes when it dies. Dexterity Saving Throw: "
                    f"DC {spell_save_dc}, each creature in a 10-foot Emanation originating from the companion. "
                    f"Failure: {death_burst_dice} Necrotic damage. Success: Half damage."
                ),
            ),
            MonsterAbility(
                name="Lightning Absorption",
                description="Whenever the companion is subjected to Lightning damage, it regains a number of Hit Points equal to the Lightning damage dealt.",
            ),
        ],
        actions=[
            MonsterAbility(
                name="Dreadful Swipe",
                description=(
                    f"Melee Attack Roll: {spell_attack:+}, reach 5 ft. "
                    f"Hit: 1d4 + {intelligence_modifier} Necrotic damage (1d4 plus your Intelligence modifier), "
                    "and the target can't take Opportunity Attacks until the start of its next turn."
                ),
            )
        ],
        bonus_actions=[],
        reactions=[],
        legendary_actions=[],
        legendary_resistances=0,
        lair_actions=[],
        mythic_actions=[],
    )


def format_reanimated_companion(character: CharacterView) -> str:
    return format_creature_stat_block(
        _build_reanimated_companion(character), retain_mental_abilities=False
    )


class ReanimatedCompanion(Feature):
    def __init__(self):
        super().__init__(
            name="Reanimated Companion",
            origin="Reanimator Artificer Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until Long Rest",
                range="5 Feet",
            ),
            usage_tags=["summon"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Create a companion through necromancy and science. You choose its look; that doesn't change its statistics."
            ),
            Facts(
                (
                    (
                        "Action",
                        "Magic action, using Tinker's Tools or other Artisan's Tools you're proficient with",
                    ),
                    ("Range", "An unoccupied space within 5 feet"),
                    (
                        "Lasts",
                        "Until you finish a Long Rest or dismiss it (Magic action). If you die, it drops to 0 Hit Points and dies, triggering its Death Burst.",
                    ),
                    (
                        "Limit",
                        "Once per Long Rest, or expend a spell slot to create it again. Only one at a time, and not while yours is present.",
                    ),
                    ("Loyalty", "Friendly to you and your allies, and obeys you"),
                    (
                        "In combat",
                        "Acts on your turn. It moves and uses its Reaction on its own, but its only action is Dodge unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, it acts on its own and isn't limited to Dodge.",
                    ),
                )
            ),
            StatBlock(format_reanimated_companion(character)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Using Tinker's Tools or another type of Artisan's Tools with which you have proficiency, you can take a Magic action to create a Reanimated Companion (see the stat block) through the power of necromancy and science. The companion manifests in an unoccupied space within 5 feet of you. You determine the companion's appearance; your choices don't affect the companion's game statistics.\n"
            "The companion is Friendly to you and your allies and obeys you. It lasts until you finish a Long Rest or until you take a Magic action to dismiss it early, at which point it harmlessly collapses into a pile of viscera. It immediately drops to 0 Hit Points and dies (triggering its Death Burst trait) if you die.\n"
            "Once you create a companion, you can't do so again until you finish a Long Rest or expend a spell slot to create one. You can have only one companion at a time and can't create one while your companion is present.\n"
            "The Companion in Combat. In combat, the companion acts during your turn. It can move and take its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, the companion acts on its own and isn't limited to the Dodge action.\n"
            + format_reanimated_companion(character)
        )
        return description


class StrangeModifications(Feature):
    def __init__(self):
        super().__init__(
            name="Strange Modifications",
            origin="Reanimator Artificer Level 5",
            activation=FeatureActivation(range="120 Feet"),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Each time you create a Reanimated Companion, choose one:"),
            Option(
                "Arcane Conduit",
                (
                    Facts(
                        (
                            (
                                "Casting",
                                "Cast spells as if from the companion's space, using your own senses",
                            ),
                            (
                                "Damage",
                                "Once per turn, when an Artificer Evocation or Necromancy spell deals damage while the companion is within 120 feet, add your Intelligence modifier to one damage roll",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Ferocity",
                (Facts((("Dreadful Swipe", "Its damage die becomes 1d6"),)),),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you create a Reanimated Companion, it gains one of the following options of your choice; choose when you create the companion.\n"
            "Arcane Conduit. You can cast spells as though you were in the companion's space, but you must use your own senses. Once per turn, when you cast an Artificer spell from the Evocation or Necromancy school and deal damage while your companion is within 120 feet of you, you can add your Intelligence modifier to one damage roll of that spell.\n"
            "Ferocity. The damage die of the companion's Dreadful Swipe increases to 1d6."
        )
        return description


class ImprovedReanimation(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Reanimation",
            origin="Reanimator Artificer Level 9",
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "The damage of your Reanimated Companion's Death Burst increases to 4d4. Necrotic damage dealt by your companion ignores Resistance."
        return description


class MacabreModifications(Feature):
    def __init__(self):
        super().__init__(
            name="Macabre Modifications",
            origin="Reanimator Artificer Level 9",
            usage_tags=["control", "damage", "utility"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Your Reanimated Companion gains two Strange Modifications instead of one, and you can also pick these options."
            ),
            Option(
                "New modifications",
                (
                    Facts(
                        (
                            (
                                "Bloated",
                                "It becomes Large. A Large or smaller creature it hits with Dreadful Swipe is pushed up to 10 feet away. Add your Intelligence modifier to its Death Burst damage.",
                            ),
                            (
                                "Gaunt",
                                f"Speed 45 feet and a Climb Speed equal to its Speed, climbing any surface without a check. A creature of your choice that starts its turn within 10 feet of it makes a Wisdom save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)}) or is Frightened until the start of its next turn.",
                            ),
                            (
                                "Moist",
                                "A Swim Speed equal to its Speed, and it can squeeze through 1-inch spaces. An attacker within 10 feet that hits it with an attack roll takes Acid damage equal to your Intelligence modifier.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You experiment and alter your companion further. Whenever you create a Reanimated Companion, the companion now gains two options for Strange Modifications, instead of one. Additionally, when picking options for Strange Modifications, you can also choose from the following options.\n"
            "Bloated. The companion becomes Large. Whenever it hits a Large or smaller creature with its Dreadful Swipe action, that creature is pushed up to 10 feet away from the companion. Additionally, you can add your Intelligence modifier to the damage dealt by the companion's Death Burst.\n"
            "Gaunt. The companion's Speed increases to 45 feet, and it gains a Climb Speed equal to its Speed. It can climb difficult surfaces, including along ceilings, without needing to make an ability check. In addition, whenever a creature of your choice starts its turn within a 10-foot Emanation originating from your companion, the creature must succeed on a Wisdom saving throw against your spell save DC or have the Frightened condition until the start of its next turn.\n"
            "Moist. The companion gains a Swim Speed equal to its Speed, and it can move through a space as narrow as 1 inch without expending extra movement to do so. In addition, whenever the companion is hit by an attack roll from a creature within 10 feet of itself, the attacker takes Acid damage equal to your Intelligence modifier."
        )
        return description


class RefinedReanimation(Feature):
    def __init__(self):
        super().__init__(
            name="Refined Reanimation",
            origin="Reanimator Artificer Level 15",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["heal", "utility"],
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="long rest",
                current_formula="Used by Facilitated Revival.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Facilitated Revival's once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    (
                        "Facilitated Revival",
                        "Cast Raise Dead without a spell slot or Material components, using artisan's tools you're proficient with as the focus. Once per Long Rest.",
                    ),
                    (
                        "Life Transfer",
                        "Reaction when you or your companion takes damage: regain Hit Points equal to the companion's current Hit Points; it then drops to 0 and dies (triggering Death Burst)",
                    ),
                    (
                        "Superior Modifications",
                        "Your companion gains three Strange Modifications",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have mastered the science of revivification, granting you the following benefits.\n"
            "Facilitated Revival. You can cast Raise Dead once without expending a spell slot and without Material components, provided you use Tinker's Tools or another type of Artisan's Tools with which you have proficiency as the Spellcasting Focus. Once you use this feature, you can't use it again until you finish a Long Rest.\n"
            "Life Transfer. You can siphon the animating magic of your Reanimated Companion to bolster yourself. When you or your companion takes damage, you can take a Reaction to gain a number of Hit Points equal to your companion's current Hit Points. The companion then immediately drops to 0 Hit Points and dies (triggering its Death Burst trait).\n"
            "Superior Modifications. Whenever you create a Reanimated Companion, the companion now gains three options for Strange Modifications."
        )
        return description
