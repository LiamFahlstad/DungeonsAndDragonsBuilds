from CharacterContent.Items.Weapons import WeaponProficiency
from Core.Definitions import (
    Ability,
    CharacterClass,
    Condition,
    CreatureSize,
    DamageType,
)
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    FeatureDice,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import GrantWeaponProficiency
from Model.Creatures.Combatants import (
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import MonsterAbility
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    StatBlock,
)


class ToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade",
            origin="Battle Smith Artificer Level 3",
            usage_tags=["utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Smith's Tools. If you already have this proficiency, you gain proficiency with one other type of Artisan's Tools of your choice.\n"
            "Weapon Crafting. When you craft a nonmagical or magic weapon, the amount of time required to craft it is halved."
        )
        return description


class Spells(Feature):
    def __init__(self):
        super().__init__(
            name="Battle Smith spells", origin="Battle Smith Artificer Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach an Artificer level specified in the Battle Smith Spells table, you thereafter always have the listed spells prepared.\n"
            "Battle Smith Spells\n"
            "Artificer Level	Spells\n"
            "3	Heroism, Shield\n"
            "5	Shining Smite, Warding Bond\n"
            "9	Aura of Vitality, Conjure Barrage\n"
            "13	Aura of Purity, Fire Shield\n"
            "17	Banishing Smite, Mass Cure Wounds"
        )
        return description


class BattleReady(Feature):
    def __init__(self):
        super().__init__(name="Battle Ready", origin="Battle Smith Artificer Level 3")

    def apply(self, ledger_writer: LedgerWriter):
        # "Weapon Knowledge. You gain proficiency with Martial weapons."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your combat training and your experiments with magic have paid off in two ways.\n"
            "Arcane Empowerment. When you attack with a magic weapon, you can use your Intelligence modifier, instead of your Strength or Dexterity modifier, for the attack and damage rolls.\n"
            "Weapon Knowledge. You gain proficiency with Martial weapons. You can use a weapon with which you have proficiency as a Spellcasting Focus for your Artificer spells."
        )
        return description


def _build_steel_defender(character: CharacterView) -> ExtendedCombatantData:
    artificer_level = character.get_class_level(CharacterClass.ARTIFICER)
    intelligence_modifier = character.get_intelligence_modifier()
    spell_attack = character.calculate_attack_bonus_for_ability(Ability.INTELLIGENCE)
    proficiency_bonus = character.get_proficiency_bonus()

    deflect = (
        "Trigger: A creature the defender can see within 5 feet of it makes an attack roll targeting a different creature. "
        "Response: The triggering creature makes the attack roll with Disadvantage."
    )
    if character.has_feature(ImprovedDefender):
        deflect += (
            f" The attacker takes 1d4 + {intelligence_modifier} Force damage "
            "(Improved Deflection: 1d4 plus your Intelligence modifier)."
        )
    return ExtendedCombatantData(
        combatant_type="Steel Defender",
        hp=5 + 5 * artificer_level,
        ac=12 + intelligence_modifier,
        temp_hp=0,
        conditions=[],
        ability_scores={
            Ability.STRENGTH: 14,
            Ability.DEXTERITY: 12,
            Ability.CONSTITUTION: 14,
            Ability.INTELLIGENCE: 4,
            Ability.WISDOM: 10,
            Ability.CHARISMA: 6,
        },
        saving_throws={
            Ability.STRENGTH: 2,
            Ability.DEXTERITY: 1,
            Ability.CONSTITUTION: 2,
            Ability.INTELLIGENCE: -3,
            Ability.WISDOM: 0,
            Ability.CHARISMA: -2,
        },
        spell_slots={},
        cr="None",
        monster_type=MonsterType.CONSTRUCT,
        size=CreatureSize.MEDIUM,
        description=f"XP 0; PB equals your Proficiency Bonus (currently +{proficiency_bonus}).",
        hp_formula=f"5 + five times your Artificer level; {artificer_level}d8 Hit Dice",
        speed_ground_ft=40,
        damage_immunities=[DamageTypeEntry(damage_types=[DamageType.POISON])],
        condition_immunities=[
            Condition.CHARMED,
            Condition.EXHAUSTION,
            Condition.POISONED,
        ],
        senses="Darkvision 60 ft., Passive Perception 10",
        languages="Understands the languages you know",
        traits=[
            MonsterAbility(
                name="Steel Bond",
                description=f"Add your Proficiency Bonus (+{proficiency_bonus}) to any ability check or saving throw the Steel Defender makes.",
            )
        ],
        actions=[
            MonsterAbility(
                name="Force-Empowered Rend",
                description=(
                    f"Melee Attack Roll: {spell_attack:+}, reach 5 ft. "
                    f"Hit: 1d8 + {2 + intelligence_modifier} Force damage (1d8 + 2 plus your Intelligence modifier)."
                ),
            ),
            MonsterAbility(
                name="Repair (3/Day)",
                description=(
                    "The defender, or one Construct or object it can see within 5 feet of it, regains Hit Points "
                    f"equal to 2d8 + {intelligence_modifier} (2d8 plus your Intelligence modifier)."
                ),
            ),
        ],
        bonus_actions=[],
        reactions=[MonsterAbility(name="Deflect Attack", description=deflect)],
        legendary_actions=[],
        legendary_resistances=0,
        lair_actions=[],
        mythic_actions=[],
    )


def format_steel_defender(character: CharacterView) -> str:
    return format_creature_stat_block(
        _build_steel_defender(character), retain_mental_abilities=False
    )


class SteelDefender(Feature):
    def __init__(self):
        super().__init__(
            name="Steel Defender",
            origin="Battle Smith Artificer Level 3",
            usage_tags=["summon"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Your tinkering has made you a companion. You choose its look and whether it has two legs or four; neither changes its statistics."
            ),
            Facts(
                (
                    (
                        "Loyalty",
                        "Friendly to you and your allies, and obeys you. It vanishes if you die.",
                    ),
                    (
                        "In combat",
                        "Acts on your turn. It moves and uses its Reaction on its own, but its only action is Dodge unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, it acts on its own and isn't limited to Dodge.",
                    ),
                    (
                        "Revive",
                        "Magic action: touch it within 1 hour of its death and expend a spell slot. It returns to life after 1 minute with all its Hit Points.",
                    ),
                    (
                        "Replace",
                        "When you finish a Long Rest with Smith's Tools in hand, create a new one; the old one vanishes",
                    ),
                )
            ),
            StatBlock(format_steel_defender(character)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your tinkering has borne you a companion, a Steel Defender (see the stat block). You determine the defender's appearance and whether it has two legs or four; your choices don't affect the defender's game statistics.\n"
            "The defender is Friendly to you and your allies and obeys you. It vanishes if you die.\n"
            "The Defender in Combat. In combat, the defender acts during your turn. It can move and take its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, the defender acts on its own and isn't limited to the Dodge action.\n"
            "Restoring or Replacing the Defender. If the defender has died within the last hour, you can take a Magic action to touch it and expend a spell slot. The defender returns to life after 1 minute with all its Hit Points restored.\n"
            "Whenever you finish a Long Rest, you can create a new defender if you have Smith's Tools in hand. If you already have a defender from this feature, the first one vanishes.\n"
            + format_steel_defender(character)
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Battle Smith Artificer Level 5")

    def get_description(self, character: CharacterView) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn. You can forgo one of your attacks when you take the Attack action to command your Steel Defender to take the Force-Empowered Rend action."
        return description


ARCANE_JOLT_DICE = FeatureDice(
    "Arcane Jolt",
    (
        (9, "2d6"),
        (15, "4d6"),
    ),
    CharacterClass.ARTIFICER,
    note="Force damage or healing",
)


class ArcaneJolt(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Jolt",
            origin="Battle Smith Artificer Level 9",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["damage", "heal"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
            dice=ARCANE_JOLT_DICE,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses and the jolt dice are in the panel below.
        return [
            Paragraph("Channel magical energy through a strike."),
            Facts(
                (
                    (
                        "Trigger",
                        "You hit with an attack roll using a magic weapon, or your Steel Defender hits",
                    ),
                    ("Limit", "Once per turn"),
                )
            ),
            Option(
                "Destructive Energy",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "The target takes extra Arcane Jolt dice (see Dice below) Force damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Restorative Energy",
                (
                    Facts(
                        (
                            ("Range", "Within 30 feet of the target"),
                            ("Target", "One creature or object you can see"),
                            (
                                "Heal",
                                "It regains Arcane Jolt dice (see Dice below) Hit Points",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When either you hit a target with an attack roll using a magic weapon or your Steel Defender hits a target, you can channel magical energy through the strike to create one of the following effects:\n"
            "Destructive Energy. The target takes an extra 2d6 Force damage.\n"
            "Restorative Energy. Choose one creature or object you can see within 30 feet of the target. Healing energy flows into the chosen recipient, restoring 2d6 Hit Points to it.\n"
            "You can use this energy a number of times equal to your Intelligence modifier (minimum of once), but you can do so no more than once per turn. You regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class ImprovedDefender(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Defender",
            origin="Battle Smith Artificer Level 15",
            usage_tags=["damage", "heal"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Arcane Jolt and Steel Defender have become more powerful, granting these benefits.\n"
            "Improved Jolt. The extra damage and healing of your Arcane Jolt both increase to 4d6.\n"
            "Improved Deflection. Whenever your Steel Defender uses its Deflect Attack, the attacker takes Force damage equal to 1d4 plus your Intelligence modifier."
        )
        return description
