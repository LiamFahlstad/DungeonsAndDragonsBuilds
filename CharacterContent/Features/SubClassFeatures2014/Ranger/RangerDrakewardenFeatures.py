from typing import Optional

from Combat.Definitions import Alignment, DamageTypeEntry, ExtendedCombatantData, MonsterAbility, Size
from Core.Definitions import Ability, CharacterClass, DamageType
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils
from Utils.CreatureStatBlocks import format_creature_stat_block


def _build_drake(
    ranger_level: int,
    proficiency_bonus: int,
    damage_type: Optional[DamageType],
) -> ExtendedCombatantData:
    chosen_type = damage_type if damage_type is not None else DamageType.FIRE
    has_wings = ranger_level >= 7
    is_large = ranger_level >= 15
    size = Size.LARGE if is_large else (Size.MEDIUM if has_wings else Size.SMALL)

    bite_extra_dice = "1d6"
    if is_large:
        bite_extra_dice = "2d6"
    elif has_wings:
        bite_extra_dice = "1d6"

    bite_description = (
        f"Melee Attack Roll: {3 + proficiency_bonus:+}, reach 5 ft. "
        f"Hit: 1d6 + {proficiency_bonus} Piercing damage"
    )
    if has_wings:
        bite_description += f", plus {bite_extra_dice} {chosen_type.value} damage (Magic Fang/Empowered Bite)"

    traits = [
        MonsterAbility(
            name="Draconic Essence",
            description=(
                "When you summon the drake, choose a damage type: Acid, Cold, Fire, Lightning, or Poison. "
                "The chosen type determines the drake's damage immunity and the damage of its Infused Strikes trait."
            ),
        )
    ]

    reactions = [
        MonsterAbility(
            name="Infused Strikes",
            description=(
                "When another creature within 30 feet of the drake that it can see hits a target with a weapon "
                f"attack, the drake infuses the strike with its essence, causing the target to take an extra 1d6 "
                f"{chosen_type.value} damage."
            ),
        )
    ]

    return ExtendedCombatantData(
        combatant_type="Drake Companion",
        hp=5 + (5 * ranger_level),
        ac=14 + proficiency_bonus,
        temp_hp=0,
        conditions=[],
        ability_scores={"Str": 16, "Dex": 12, "Con": 15, "Int": 8, "Wis": 14, "Cha": 8},
        saving_throws={"Dex": 1 + proficiency_bonus, "Wis": 2 + proficiency_bonus},
        spell_slots={},
        cr=str(proficiency_bonus),
        monster_type="Dragon",
        alignment=Alignment.NEUTRAL,
        size=size,
        ac_note="natural armor",
        hp_formula=f"5 + five times your Ranger level ({ranger_level} d10 Hit Dice)",
        speed_ground_ft=40,
        speed_fly_ft=40 if has_wings else None,
        damage_immunities=[DamageTypeEntry(damage_types=[chosen_type])],
        senses="Darkvision 60 ft., Passive Perception 12",
        languages="Draconic",
        traits=traits,
        actions=[MonsterAbility(name="Bite", description=bite_description)],
        bonus_actions=[],
        reactions=reactions,
        legendary_actions=[],
        legendary_resistances=0,
        lair_actions=[],
        mythic_actions=[],
    )


def format_drake(
    character_stat_block: CharacterStatBlock,
    damage_type: Optional[DamageType] = None,
) -> str:
    ranger_level = character_stat_block.get_class_level(CharacterClass.RANGER)
    proficiency_bonus = character_stat_block.get_proficiency_bonus()
    drake = _build_drake(ranger_level, proficiency_bonus, damage_type)
    return format_creature_stat_block(drake, character_stat_block, retain_mental_abilities=False)


class DraconicGift(Feature):
    def __init__(self, language: Optional[str] = None):
        super().__init__(name="Draconic Gift", origin="Drakewarden Ranger Level 3")
        self._language = language

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The bond you share with your drake creates a connection to dragonkind, granting you understanding and empowering your presence. You gain the following benefits:\n"
            "    * Thaumaturgy. You learn the Thaumaturgy cantrip, which is a ranger spell for you.\n"
            "    * Tongue of Dragons. You learn to speak, read, and write Draconic or one other language of your choice."
        )
        if self._language is not None:
            description += f"\nYou chose {self._language}."
        return description


class DrakeCompanion(Feature):
    def __init__(self, damage_type: Optional[DamageType] = None):
        super().__init__(name="Drake Companion", origin="Drakewarden Ranger Level 3")
        self.damage_type = damage_type

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        uses = 1
        description = (
            "As an action, you can magically summon the drake that is bound to you. It appears in an unoccupied space of your choice within 30 feet of you.\n"
            "The drake is friendly to you and your companions, and it obeys your commands. Whenever you summon the drake, choose a damage type listed in its Draconic Essence trait. You can determine the cosmetic characteristics of the drake, such as its color, its scale texture, or any visible effect of its Draconic Essence; your choice has no effect on its game statistics.\n"
            "In combat, the drake shares your initiative count, but it takes its turn immediately after yours. It can move and use its reaction on its own, but the only action it takes on its turn is the Dodge action, unless you take a bonus action on your turn to command it to take another action. That action can be one in its stat block or some other action. If you are incapacitated, the drake can take any action of its choice, not just Dodge.\n"
            "The drake remains until it is reduced to 0 hit points, until you use this feature to summon the drake again, or until you die. Anything the drake was wearing or carrying is left behind when the drake vanishes.\n"
            "Once you summon the drake, you can't do so again until you finish a long rest, unless you expend a spell slot of 1st level or higher to summon it.\n"
            "\nThe drake's stat block grows as you gain levels in this class (Bond of Fang and Scale at 7th level and Perfected Bond at 15th level are reflected below):\n"
            + format_drake(character_stat_block, self.damage_type)
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Summon a friendly drake within 30 feet as an action (choose a damage type for its Draconic Essence). "
            "The drake shares your initiative and acts after you, taking only the Dodge action unless you use a bonus action to command it. "
            "It remains until reduced to 0 HP, resummoned, or you die; recharge with long rest or by expending a 1st-level spell slot."
        )


class BondOfFangAndScale(Feature):
    def __init__(self):
        super().__init__(name="Bond of Fang and Scale", origin="Drakewarden Ranger Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The bond you share with your drake intensifies, protecting you and stoking the drake's fury. When you summon your drake, it grows wings on its back and gains a flying speed equal to its walking speed.\n"
            "In addition, while your drake is summoned, you and the drake gain the following benefits:\n"
            "    * Drake Mount. The drake grows to Medium size. Reflecting your special bond, you can use the drake as a mount if your size is Medium or smaller. While you are riding your drake, it can't use the flying speed of this feature.\n"
            "    * Magic Fang. The drake's Bite attack deals an extra 1d6 damage of the type chosen for the drake's Draconic Essence.\n"
            "    * Resistance. You gain resistance to the damage type chosen for the drake's Draconic Essence."
        )
        return description


class DrakesBreath(Feature):
    def __init__(self):
        super().__init__(name="Drake's Breath", origin="Drakewarden Ranger Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        ranger_level = character_stat_block.get_class_level(CharacterClass.RANGER)
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        spell_save_dc = 8 + proficiency_bonus + wisdom_modifier
        damage = "10d6" if ranger_level >= 15 else "8d6"
        uses = 1
        description = (
            "As an action, you can exhale a 30-foot cone of damaging breath or cause your drake to exhale it. Choose acid, cold, fire, lightning, or poison damage (your choice doesn't have to match your drake's Draconic Essence). "
            f"Each creature in the cone must make a Dexterity saving throw against your spell save DC ({spell_save_dc}), taking {damage} damage on a failed save, or half as much damage on a successful one.\n"
            "This damage increases to 10d6 when you reach 15th level in this class.\n"
            "Once you use this feature, you can't do so again until you finish a long rest, unless you expend a spell slot of 3rd level or higher to use it again."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        ranger_level = character_stat_block.get_class_level(CharacterClass.RANGER)
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        spell_save_dc = 8 + proficiency_bonus + wisdom_modifier
        damage = "10d6" if ranger_level >= 15 else "8d6"
        return [
            ("What", "Exhale a cone of damaging breath"),
            ("Action", "Action"),
            ("Range", "30-foot cone"),
            ("Save", f"Dexterity save vs. spell save DC {spell_save_dc}"),
            ("Damage", f"{damage} on failed save, half on success"),
            ("Recharge", "Long rest (or 3rd+ spell slot)"),
        ]


class PerfectedBond(Feature):
    def __init__(self):
        super().__init__(name="Perfected Bond", origin="Drakewarden Ranger Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "Your bond to your drake reaches the pinnacle of its power. While your drake is summoned, you and the drake gain the following benefits:\n"
            "    * Empowered Bite. The drake's Bite attack deals an extra 1d6 damage of the type chosen for its Draconic Essence (for a total of 2d6 extra damage).\n"
            "    * Large Drake. The drake grows to Large size. When you ride your drake, it is no longer prohibited from using the flying speed of Bond of Fang and Scale.\n"
            f"    * Reflexive Resistance. When either you or the drake takes damage while you're within 30 feet of each other, you can use your reaction to give yourself or the drake resistance to that instance of damage. You can use this reaction a number of times equal to your proficiency bonus ({proficiency_bonus}), and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest")
