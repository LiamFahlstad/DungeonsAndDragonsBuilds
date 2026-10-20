from typing import Optional
from Core.Rules import MAX_PROFICIENCY_BONUS, levels_gained, proficiency_bonus

from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    FeatureDice,
)
from Core.Definitions import CreatureSize
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import MonsterAbility
from Core.Definitions import Ability, CharacterClass, DamageType
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, StatBlock, dc_formula


def _build_drake(
    ranger_level: int,
    proficiency_bonus: int,
    damage_type: Optional[DamageType],
) -> ExtendedCombatantData:
    chosen_type = damage_type if damage_type is not None else DamageType.FIRE
    has_wings = ranger_level >= 7
    is_large = ranger_level >= 15
    size = (
        CreatureSize.LARGE
        if is_large
        else (CreatureSize.MEDIUM if has_wings else CreatureSize.SMALL)
    )

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
        fang_label = "Magic Fang + Empowered Bite" if is_large else "Magic Fang"
        bite_description += (
            f", plus {bite_extra_dice} {chosen_type.value} damage ({fang_label})"
        )

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
        ability_scores={
            Ability.STRENGTH: 16,
            Ability.DEXTERITY: 12,
            Ability.CONSTITUTION: 15,
            Ability.INTELLIGENCE: 8,
            Ability.WISDOM: 14,
            Ability.CHARISMA: 8,
        },
        saving_throws={
            Ability.DEXTERITY: 1 + proficiency_bonus,
            Ability.WISDOM: 2 + proficiency_bonus,
        },
        spell_slots={},
        cr=str(proficiency_bonus),
        monster_type=MonsterType.DRAGON,
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
    character: CharacterView,
    damage_type: Optional[DamageType] = None,
) -> str:
    ranger_level = character.get_class_level(CharacterClass.RANGER)
    proficiency_bonus = character.get_proficiency_bonus()
    drake = _build_drake(ranger_level, proficiency_bonus, damage_type)
    return format_creature_stat_block(drake, retain_mental_abilities=False)


class DraconicGift(Feature):
    def __init__(self, language: Optional[str] = None):
        super().__init__(
            name="Draconic Gift",
            origin="Drakewarden Ranger Level 3",
            usage_tags=["utility"],
        )
        self._language = language

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        language = (
            self._language
            if self._language is not None
            else "Draconic or one other language of your choice"
        )
        return [
            Paragraph(
                "The bond you share with your drake connects you to dragonkind, granting you understanding and empowering your presence."
            ),
            Facts(
                (
                    (
                        "Thaumaturgy",
                        "You learn the cantrip; it's a Ranger spell for you",
                    ),
                    ("Tongue of Dragons", f"Speak, read and write {language}"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
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
        super().__init__(
            name="Drake Companion",
            origin="Drakewarden Ranger Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="30 Feet"
            ),
            usage_tags=["utility", "summon"],
        )
        self.damage_type = damage_type

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Summon the drake bound to you. Choose a damage type from its Draconic Essence each time; its look is up to you."
            ),
            Facts(
                (
                    ("Action", "Action"),
                    ("Range", "An unoccupied space within 30 feet"),
                    (
                        "Loyalty",
                        "Friendly to you and your companions, and obeys your commands",
                    ),
                    (
                        "In combat",
                        "Shares your initiative count and takes its turn right after yours. It moves and uses its reaction on its own, but its only action is Dodge unless you take a bonus action to command another action (from its stat block or any other). If you're incapacitated, it can take any action.",
                    ),
                    (
                        "Lasts",
                        "Until it drops to 0 hit points, you summon it again, or you die. What it wore or carried is left behind.",
                    ),
                    (
                        "Recharge",
                        "Once per long rest, or expend a spell slot of 1st level or higher",
                    ),
                )
            ),
            StatBlock(format_drake(character, self.damage_type)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As an action, you can magically summon the drake that is bound to you. It appears in an unoccupied space of your choice within 30 feet of you.\n"
            "The drake is friendly to you and your companions, and it obeys your commands. Whenever you summon the drake, choose a damage type listed in its Draconic Essence trait. You can determine the cosmetic characteristics of the drake, such as its color, its scale texture, or any visible effect of its Draconic Essence; your choice has no effect on its game statistics.\n"
            "In combat, the drake shares your initiative count, but it takes its turn immediately after yours. It can move and use its reaction on its own, but the only action it takes on its turn is the Dodge action, unless you take a bonus action on your turn to command it to take another action. That action can be one in its stat block or some other action. If you are incapacitated, the drake can take any action of its choice, not just Dodge.\n"
            "The drake remains until it is reduced to 0 hit points, until you use this feature to summon the drake again, or until you die. Anything the drake was wearing or carrying is left behind when the drake vanishes.\n"
            "Once you summon the drake, you can't do so again until you finish a long rest, unless you expend a spell slot of 1st level or higher to summon it.\n"
            "\nThe drake's stat block grows as you gain levels in this class (Bond of Fang and Scale at 7th level and Perfected Bond at 15th level are reflected below):\n"
            + format_drake(character, self.damage_type)
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class BondOfFangAndScale(Feature):
    def __init__(self):
        super().__init__(
            name="Bond of Fang and Scale",
            origin="Drakewarden Ranger Level 7",
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Your drake grows wings when summoned: a flying speed equal to its walking speed. While it's summoned:"
            ),
            Facts(
                (
                    (
                        "Drake Mount",
                        "It's Medium, and you can ride it if you're Medium or smaller (it can't fly while ridden)",
                    ),
                    (
                        "Magic Fang",
                        "Its Bite deals an extra 1d6 damage of its Draconic Essence type",
                    ),
                    (
                        "Resistance",
                        "You have resistance to its Draconic Essence damage type",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The bond you share with your drake intensifies, protecting you and stoking the drake's fury. When you summon your drake, it grows wings on its back and gains a flying speed equal to its walking speed.\n"
            "In addition, while your drake is summoned, you and the drake gain the following benefits:\n"
            "    * Drake Mount. The drake grows to Medium size. Reflecting your special bond, you can use the drake as a mount if your size is Medium or smaller. While you are riding your drake, it can't use the flying speed of this feature.\n"
            "    * Magic Fang. The drake's Bite attack deals an extra 1d6 damage of the type chosen for the drake's Draconic Essence.\n"
            "    * Resistance. You gain resistance to the damage type chosen for the drake's Draconic Essence."
        )
        return description


DRAKES_BREATH_DICE = FeatureDice(
    "Breath Damage",
    (
        (7, "8d6"),
        (15, "10d6"),
    ),
    CharacterClass.RANGER,
)


class DrakesBreath(Feature):
    def __init__(self):
        super().__init__(
            name="Drake's Breath",
            origin="Drakewarden Ranger Level 11",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="30-Foot Cone"
            ),
            usage_tags=["damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
            dice=DRAKES_BREATH_DICE,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The breath's dice and once-per-long-rest box are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Action"),
                    ("Area", "30-foot cone, from you or your drake"),
                    (
                        "Damage type",
                        "Acid, cold, fire, lightning or poison (needn't match the drake's essence)",
                    ),
                    (
                        "Save",
                        f"Dexterity save against your spell save DC ({dc_formula(Ability.WISDOM)})",
                    ),
                    ("Failed", "Breath Damage dice (see Dice below)"),
                    ("Succeeded", "Half damage"),
                    (
                        "Recharge",
                        "Once per long rest, or expend a spell slot of 3rd level or higher",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As an action, you can exhale a 30-foot cone of damaging breath or cause your drake to exhale it. Choose acid, cold, fire, lightning, or poison damage (your choice doesn't have to match your drake's Draconic Essence). "
            "Each creature in the cone must make a Dexterity saving throw against your spell save DC, taking 8d6 damage on a failed save, or half as much damage on a successful one.\n"
            "This damage increases to 10d6 when you reach 15th level in this class.\n"
            "Once you use this feature, you can't do so again until you finish a long rest, unless you expend a spell slot of 3rd level or higher to use it again."
        )
        return description

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        wisdom_modifier = character.get_wisdom_modifier()
        return 8 + proficiency_bonus + wisdom_modifier

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA


class PerfectedBond(Feature):
    def __init__(self):
        super().__init__(
            name="Perfected Bond",
            origin="Drakewarden Ranger Level 15",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Reflexive Resistance: equal to your proficiency bonus.",
                gained_at=levels_gained(proficiency_bonus, from_level=15),
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Reflexive Resistance's uses are in the panel below.
        return [
            Paragraph("While your drake is summoned:"),
            Facts(
                (
                    (
                        "Empowered Bite",
                        "Its Bite deals another extra 1d6 of its Draconic Essence type (2d6 extra in total)",
                    ),
                    ("Large Drake", "It's Large, and it can fly while you ride it"),
                    (
                        "Reflexive Resistance",
                        "Reaction when you or the drake takes damage while within 30 feet of each other: give yourself or the drake resistance to that damage. Proficiency Bonus times per long rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your bond to your drake reaches the pinnacle of its power. While your drake is summoned, you and the drake gain the following benefits:\n"
            "    * Empowered Bite. The drake's Bite attack deals an extra 1d6 damage of the type chosen for its Draconic Essence (for a total of 2d6 extra damage).\n"
            "    * Large Drake. The drake grows to Large size. When you ride your drake, it is no longer prohibited from using the flying speed of Bond of Fang and Scale.\n"
            "    * Reflexive Resistance. When either you or the drake takes damage while you're within 30 feet of each other, you can use your reaction to give yourself or the drake resistance to that instance of damage. You can use this reaction a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
