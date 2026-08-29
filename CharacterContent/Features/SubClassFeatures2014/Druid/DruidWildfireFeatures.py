from Combat.Definitions import Alignment, Condition, DamageTypeEntry, ExtendedCombatantData, MonsterAbility, MonsterType, Size
from Core.Definitions import Ability, CharacterClass, DamageType, MAX_PROFICIENCY_BONUS
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils
from Utils.CreatureStatBlocks import format_creature_stat_block


def _build_wildfire_spirit(druid_level: int, proficiency_bonus: int, spell_attack_modifier: int) -> ExtendedCombatantData:
    flame_seed_description = (
        f"Ranged Weapon Attack: {spell_attack_modifier:+} to hit, range 60 ft., one target you can see. "
        f"Hit: 1d6 + {proficiency_bonus} Fire damage."
    )
    fiery_teleportation_description = (
        "The spirit and each willing creature of your choice within 5 feet of it teleport up to 15 feet to "
        "unoccupied spaces you can see. Then each creature within 5 feet of the space that the spirit left must "
        f"succeed on a Dexterity saving throw against your spell save DC or take 1d6 + {proficiency_bonus} Fire damage."
    )

    return ExtendedCombatantData(
        combatant_type="Wildfire Spirit",
        hp=5 + (5 * druid_level),
        ac=13,
        temp_hp=0,
        conditions=[],
        ability_scores={"Str": 10, "Dex": 14, "Con": 14, "Int": 13, "Wis": 15, "Cha": 11},
        saving_throws={},
        spell_slots={},
        cr="—",
        monster_type=MonsterType.ELEMENTAL,
        alignment=Alignment.UNALIGNED,
        size=Size.SMALL,
        ac_note="natural armor",
        hp_formula=f"5 + five times your druid level ({druid_level})",
        speed_ground_ft=30,
        speed_fly_ft=30,
        speed_special_rules="hover",
        damage_immunities=[DamageTypeEntry(damage_types=[DamageType.FIRE])],
        condition_immunities=[
            Condition.CHARMED,
            Condition.FRIGHTENED,
            Condition.GRAPPLED,
            Condition.PRONE,
            Condition.RESTRAINED,
        ],
        senses="Darkvision 60 ft., Passive Perception 12",
        languages="Understands the languages you speak",
        traits=[],
        actions=[
            MonsterAbility(name="Flame Seed", description=flame_seed_description),
            MonsterAbility(name="Fiery Teleportation", description=fiery_teleportation_description),
        ],
        bonus_actions=[],
        reactions=[],
        legendary_actions=[],
        legendary_resistances=0,
        lair_actions=[],
        mythic_actions=[],
    )


def format_wildfire_spirit(character_stat_block: CharacterStatBlock) -> str:
    druid_level = character_stat_block.get_class_level(CharacterClass.DRUID)
    proficiency_bonus = character_stat_block.get_proficiency_bonus()
    wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
    spell_attack_modifier = proficiency_bonus + wisdom_modifier
    spirit = _build_wildfire_spirit(druid_level, proficiency_bonus, spell_attack_modifier)
    return format_creature_stat_block(spirit, character_stat_block, retain_mental_abilities=False)


class CircleSpells(Feature):
    def __init__(self):
        super().__init__(name="Circle Spells", origin="Circle of Wildfire Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 2nd level, you have formed a bond with a wildfire spirit, a primal being of creation and destruction. Your link with this spirit grants you access to some spells when you reach certain levels in this class, as shown on the Circle of Wildfire Spells table.\n"
            "\n"
            "Once you gain access to one of these spells, you always have it prepared, and it doesn't count against the number of spells you can prepare each day. If you gain access to a spell that doesn't appear on the Druid Spell List, the spell is nonetheless a druid spell for you.\n"
            "Circle of Wildfire Spells\n"
            "Druid Level\tSpells\n"
            "2nd\tBurning Hands, Cure Wounds\n"
            "3rd\tFlaming Sphere, Scorching Ray\n"
            "5th\tPlant Growth, Revivify\n"
            "7th\tAura of Life, Fire Shield\n"
            "9th\tFlame Strike, Mass Cure Wounds"
        )
        return description


class SummonWildfireSpirit(Feature):
    def __init__(self):
        super().__init__(name="Summon Wildfire Spirit", origin="Circle of Wildfire Druid Level 3", action_type="action", duration="1 Hour", range="30 Feet", usage_tags=["damage", "utility", "summon"], uses=FeatureUses(max_uses=1, regain_all_on="Wild Shape use"))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can summon the primal spirit bound to your soul. As an action, you can expend one use of your Wild Shape feature to summon your wildfire spirit, rather than assuming a beast form.\n"
            "\n"
            "The spirit appears in an unoccupied space of your choice that you can see within 30 feet of you. Each creature within 10 feet of the spirit (other than you) when it appears must succeed on a Dexterity saving throw against your spell save DC or take 2d6 fire damage.\n"
            "\n"
            "The spirit is friendly to you and your companions and obeys your commands. See this creature's game statistics in the Wildfire Spirit stat block, which uses your proficiency bonus (PB) in several places. You determine the spirit's appearance. Some spirits take the form of a humanoid figure made of gnarled branches covered in flame, while others look like beasts wreathed in fire.\n"
            "\n"
            "In combat, the spirit shares your initiative count, but it takes its turn immediately after yours. The only action it takes on its turn is the Dodge action, unless you take a bonus action on your turn to command it to take another action. That action can be one in its stat block or some other action. If you are incapacitated, the spirit can take any action of its choice, not just Dodge.\n"
            "\n"
            "The spirit manifests for 1 hour, until it is reduced to 0 hit points, until you use this feature to summon the spirit again, or until you die.\n"
            "\n"
            + format_wildfire_spirit(character_stat_block)
        )
        return description