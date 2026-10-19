from CharacterContent.Spells.SpellLists import (
    AbjurationLevel2Spells,
    AbjurationLevel3Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    ConjurationLevel4Spells,
    ConjurationLevel5Spells,
    DivinationLevel4Spells,
    DivinationLevel5Spells,
    EnchantmentLevel1Spells,
    EnchantmentLevel4Spells,
    EnchantmentLevel5Spells,
    EvocationLevel1Spells,
    EvocationLevel2Spells,
    EvocationLevel3Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    IllusionLevel1Spells,
    IllusionLevel2Spells,
    IllusionLevel3Spells,
    SorcererLevel2Spells,
    TransmutationLevel2Spells,
)
from Core.Definitions import (
    Ability,
    CharacterClass,
    Condition,
    CreatureSize,
    DamageType,
    WarlockVestigeDomain,
    WarlockVestigeType,
)
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import MonsterAbility
from Model.View import CharacterView
from Presentation.CreatureStatBlocks import format_creature_stat_block
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    StatBlock,
    Table,
)

# The Domain Spells of the Cleric domains Vestige Spells can draw on, keyed by
# the Warlock level (equal to the Cleric level) they're prepared from.
VESTIGE_DOMAIN_SPELLS: dict[WarlockVestigeDomain, dict[int, list[str]]] = {
    WarlockVestigeDomain.LIFE: {
        3: [
            ClericLevel2Spells.AID,
            ClericLevel1Spells.BLESS,
            ClericLevel1Spells.CURE_WOUNDS,
            ClericLevel2Spells.LESSER_RESTORATION,
        ],
        5: [ClericLevel3Spells.MASS_HEALING_WORD, ClericLevel3Spells.REVIVIFY],
        7: [ClericLevel4Spells.AURA_OF_LIFE, ClericLevel4Spells.DEATH_WARD],
        9: [
            ClericLevel5Spells.GREATER_RESTORATION,
            ClericLevel5Spells.MASS_CURE_WOUNDS,
        ],
    },
    WarlockVestigeDomain.LIGHT: {
        3: [
            EvocationLevel1Spells.BURNING_HANDS,
            EvocationLevel1Spells.FAERIE_FIRE,
            EvocationLevel2Spells.SCORCHING_RAY,
            SorcererLevel2Spells.SEE_INVISIBILITY,
        ],
        5: [EvocationLevel3Spells.DAYLIGHT, EvocationLevel3Spells.FIREBALL],
        7: [DivinationLevel4Spells.ARCANE_EYE, EvocationLevel4Spells.WALL_OF_FIRE],
        9: [EvocationLevel5Spells.FLAME_STRIKE, DivinationLevel5Spells.SCRYING],
    },
    WarlockVestigeDomain.TRICKERY: {
        3: [
            EnchantmentLevel1Spells.CHARM_PERSON,
            IllusionLevel1Spells.DISGUISE_SELF,
            IllusionLevel2Spells.INVISIBILITY,
            AbjurationLevel2Spells.PASS_WITHOUT_TRACE,
        ],
        5: [IllusionLevel3Spells.HYPNOTIC_PATTERN, AbjurationLevel3Spells.NONDETECTION],
        7: [EnchantmentLevel4Spells.CONFUSION, ConjurationLevel4Spells.DIMENSION_DOOR],
        9: [
            EnchantmentLevel5Spells.DOMINATE_PERSON,
            EnchantmentLevel5Spells.MODIFY_MEMORY,
        ],
    },
    WarlockVestigeDomain.WAR: {
        3: [
            ClericLevel1Spells.GUIDING_BOLT,
            TransmutationLevel2Spells.MAGIC_WEAPON,
            ClericLevel1Spells.SHIELD_OF_FAITH,
            ClericLevel2Spells.SPIRITUAL_WEAPON,
        ],
        5: [
            EvocationLevel3Spells.CRUSADERS_MANTLE,
            ClericLevel3Spells.SPIRIT_GUARDIANS,
        ],
        7: [EvocationLevel4Spells.FIRE_SHIELD, ClericLevel4Spells.FREEDOM_OF_MOVEMENT],
        9: [
            EnchantmentLevel5Spells.HOLD_MONSTER,
            ConjurationLevel5Spells.STEEL_WIND_STRIKE,
        ],
    },
}

# What the vestige's type decides: its creature type, the damage its strike
# deals (and it and you, from level 6, resist), and its Divine Power.
_VESTIGE_MONSTER_TYPE = {
    WarlockVestigeType.CELESTIAL: MonsterType.CELESTIAL,
    WarlockVestigeType.FIEND: MonsterType.FIEND,
    WarlockVestigeType.UNDEAD: MonsterType.UNDEAD,
}
VESTIGE_DAMAGE_TYPE = {
    WarlockVestigeType.CELESTIAL: DamageType.RADIANT,
    WarlockVestigeType.FIEND: DamageType.FIRE,
    WarlockVestigeType.UNDEAD: DamageType.NECROTIC,
}
_DIVINE_POWER = {
    WarlockVestigeType.CELESTIAL: (
        "Healing Touch",
        "The vestige touches another creature. The target regains Hit Points equal to 2d8 plus your Charisma modifier and ends one condition on it: Blinded, Deafened, or Poisoned.",
    ),
    WarlockVestigeType.FIEND: (
        "Fiendish Swap",
        "If you and the vestige are within 60 feet of each other, you both teleport, swapping places.",
    ),
    WarlockVestigeType.UNDEAD: (
        "Cursed Invocation",
        "The vestige places a curse on a creature you can see within 30 feet of the vestige for 1 minute. While cursed, the target has Disadvantage on attack rolls against you and the vestige.",
    ),
}
_SEMBLANCE_SPIRITS = {
    WarlockVestigeType.CELESTIAL: ("Celestial Spirit", "Summon Celestial"),
    WarlockVestigeType.FIEND: ("Fiendish Spirit", "Summon Fiend"),
    WarlockVestigeType.UNDEAD: ("Undead Spirit", "Summon Undead"),
}


def _build_vestige(
    character: CharacterView, vestige_type: WarlockVestigeType
) -> ExtendedCombatantData:
    warlock_level = character.get_class_level(CharacterClass.WARLOCK)
    charisma_modifier = character.get_charisma_modifier()
    spell_attack = character.calculate_attack_bonus_for_ability(Ability.CHARISMA)
    proficiency_bonus = character.get_proficiency_bonus()
    damage_type = VESTIGE_DAMAGE_TYPE[vestige_type]
    divine_power_name, divine_power_text = _DIVINE_POWER[vestige_type]
    regains = "Once per Long Rest"
    if character.has_feature(VestigePower):
        regains = "Regains its use when you finish a Short or Long Rest or use Magical Cunning"
    return ExtendedCombatantData(
        combatant_type="Vestige Companion",
        hp=4 + 4 * warlock_level,
        ac=13 + charisma_modifier,
        temp_hp=0,
        conditions=[],
        ability_scores={
            Ability.STRENGTH: 1,
            Ability.DEXTERITY: 14,
            Ability.CONSTITUTION: 10,
            Ability.INTELLIGENCE: 15,
            Ability.WISDOM: 15,
            Ability.CHARISMA: 16,
        },
        saving_throws={
            Ability.STRENGTH: -5,
            Ability.DEXTERITY: 2,
            Ability.CONSTITUTION: 0,
            Ability.INTELLIGENCE: 2,
            Ability.WISDOM: 2,
            Ability.CHARISMA: 3,
        },
        spell_slots={},
        cr="None",
        monster_type=_VESTIGE_MONSTER_TYPE[vestige_type],
        alignment=Alignment.NEUTRAL,
        size=CreatureSize.SMALL,
        description=f"XP 0; PB equals your Proficiency Bonus (currently +{proficiency_bonus}).",
        ac_note="13 plus your Charisma modifier",
        hp_formula=f"4 + four times your Warlock level; {warlock_level}d6 Hit Dice",
        initiative_bonus=2,
        speed_ground_ft=5,
        speed_fly_ft=30,
        speed_special_rules="hover",
        damage_resistances=[DamageTypeEntry(damage_types=[damage_type])],
        condition_immunities=[
            Condition.CHARMED,
            Condition.FRIGHTENED,
            Condition.PRONE,
        ],
        senses="Passive Perception 12",
        languages="Speaks the languages you know",
        traits=[
            MonsterAbility(
                name="Pact Bond",
                description=f"Add your Proficiency Bonus (+{proficiency_bonus}) to any ability check or saving throw the vestige makes.",
            )
        ],
        actions=[
            MonsterAbility(
                name="Vestige's Strike",
                description=(
                    f"Melee or Ranged Attack Roll: {spell_attack:+} (your spell attack modifier), reach 5 ft. or range 60 ft. "
                    f"Hit: 1d6 + {3 + charisma_modifier} {damage_type.value} damage (1d6 + 3 plus your Charisma modifier)."
                ),
            ),
        ],
        bonus_actions=[
            MonsterAbility(
                name=f"Divine Power: {divine_power_name}",
                description=f"{divine_power_text} {regains}.",
            ),
        ],
        reactions=[],
        legendary_actions=[],
        legendary_resistances=0,
        lair_actions=[],
        mythic_actions=[],
    )


def format_vestige(character: CharacterView, vestige_type: WarlockVestigeType) -> str:
    return format_creature_stat_block(
        _build_vestige(character, vestige_type), retain_mental_abilities=False
    )


class VestigeCompanion(Feature):
    def __init__(self, vestige_type: WarlockVestigeType):
        super().__init__(
            name="Vestige Companion",
            origin="Vestige Patron Warlock Level 3",
            usage_tags=["summon"],
        )
        self.vestige_type = vestige_type

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                f"A dying god's vestige manifests, drawing strength from your pact. Yours is a {self.vestige_type.value}; you choose its look, which bears signs of its supernatural origin."
            ),
            Facts(
                (
                    (
                        "Loyalty",
                        "Friendly to you and your allies, and obeys you. It vanishes if you die.",
                    ),
                    (
                        "In combat",
                        "Acts on your turn. It moves and uses its Reaction on its own, but its only action is Dodge unless you take a Bonus Action to command it to take an action in its stat block or another action. If you have the Incapacitated condition, it acts on its own and isn't limited to Dodge.",
                    ),
                    (
                        "Attack",
                        "When you take the Attack action, sacrifice one of your attacks to command it to take the Vestige's Strike action",
                    ),
                    (
                        "At 0 Hit Points",
                        "It disappears, leaving behind what it wore or carried. A 1-minute magical ceremony manifests it again with full Hit Points within 5 feet of you.",
                    ),
                    (
                        "Dismiss",
                        "Magic action: send it to a pocket dimension, or call it back to an unoccupied space within 30 feet of you",
                    ),
                    (
                        "New form",
                        "When you finish a Long Rest, summon it within 5 feet of you in a new form, choosing its appearance and whether it's a Celestial, Fiend or Undead",
                    ),
                )
            ),
            StatBlock(format_vestige(character, self.vestige_type)),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The vestige manifests, drawing strength from your pact. It uses the Vestige Companion stat block and is a Celestial, Fiend, or Undead (choose when you gain this feature). You determine what the vestige looks like, but regardless of its form, the vestige bears features indicating its supernatural origin. For example, you might decide your vestige is an oversize floating skull etched with sigils, a circle of glowing runes, or a constantly shifting abstract shape. The vestige is Friendly to you and your allies and obeys your commands. It vanishes if you die.\n"
            "The Vestige in Combat. In combat, the vestige acts during your turn. It can move and use its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action in its stat block or some other action. You can also sacrifice one of your attacks when you take the Attack action to command the vestige to take the Vestige's Strike action. If you have the Incapacitated condition, the vestige acts on its own and isn't limited to the Dodge action.\n"
            "Disappearance of the Vestige. When the vestige drops to 0 Hit Points, it disappears. You can spend 1 minute performing a magical ceremony to manifest the vestige again; it reappears with its maximum Hit Points in an unoccupied space within 5 feet of you. As a Magic action, you can temporarily dismiss the vestige to a pocket dimension. As a Magic action while it is temporarily dismissed, you can cause the vestige to reappear in an unoccupied space within 30 feet of you. Whenever the vestige drops to 0 Hit Points or disappears into the pocket dimension, it leaves behind in its space anything it was wearing or carrying.\n"
            "Whenever you finish a Long Rest, you can summon the vestige in a new form, which appears in an unoccupied space within 5 feet of you. You choose its appearance and whether it is a Celestial, Fiend, or Undead. If the vestige is already manifested from this feature, its form changes to the new one.\n"
            + format_vestige(character, self.vestige_type)
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class VestigeSpells(Feature):
    def __init__(self, domain: WarlockVestigeDomain):
        super().__init__(name="Vestige Spells", origin="Vestige Patron Warlock Level 3")
        self.domain = domain

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                f"You chose the {self.domain.value} Domain: its Domain Spells are Warlock spells for you, and from the Warlock level shown you always have them prepared."
            ),
            Table(
                ("Warlock level", "Spells"),
                tuple(
                    (str(level), ", ".join(spells))
                    for level, spells in VESTIGE_DOMAIN_SPELLS[self.domain].items()
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The magic of your Vestige Companion ensures you always have certain spells ready. Select one of the following Cleric domains: Life, Light, Trickery, or War. The Domain Spells of your chosen domain are Warlock spells for you. When you reach a Warlock level equal to a Cleric level listed on the Domain Spells table for the domain you have chosen, you thereafter always have the listed spells prepared.\n"
            "For example, if you chose the War Domain for this feature, when you reach Warlock level 3, you would have the Guiding Bolt, Magic Weapon, Shield of Faith, and Spiritual Weapon spells prepared.\n"
            f"You chose the {self.domain.value} Domain."
        )
        return description


class VestigePower(Feature):
    def __init__(self, vestige_type: WarlockVestigeType):
        super().__init__(
            name="Vestige Power",
            origin="Vestige Patron Warlock Level 6",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["buff"],
        )
        self.vestige_type = vestige_type

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        damage_type = VESTIGE_DAMAGE_TYPE[self.vestige_type].value
        return [
            Facts(
                (
                    (
                        "Divine Power",
                        "Your vestige regains its use whenever you finish a Short or Long Rest or use Magical Cunning",
                    ),
                    (
                        "Resistance",
                        f"While within 30 feet of your vestige, you have Resistance to the same damage types as it ({damage_type} for a {self.vestige_type.value})",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your Vestige Companion now regains its use of Divine Power whenever you finish a Short or Long Rest or when you use your Magical Cunning feature. In addition, while within 30 feet of your Vestige Companion, you have Resistance to the same damage types as the vestige."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class VestigeRecovery(Feature):
    def __init__(self):
        super().__init__(
            name="Vestige Recovery",
            origin="Vestige Patron Warlock Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["heal"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "Your Vestige Companion would drop to 0 Hit Points"),
                    ("Cost", "Expend a Pact Magic spell slot"),
                    (
                        "Effect",
                        "Its Hit Points change to its Hit Point maximum instead, and it teleports to an unoccupied space you can see within 30 feet of it",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When your Vestige Companion would drop to 0 Hit Points, you can take a Reaction and expend a Pact Magic spell slot to instead change its Hit Points to its Hit Point maximum. The vestige then teleports to an unoccupied space you can see within 30 feet of it. Once you use this feature, you can't do so again until you finish a Long Rest."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SemblanceOfLife(Feature):
    def __init__(self, vestige_type: WarlockVestigeType):
        super().__init__(
            name="Semblance of Life",
            origin="Vestige Patron Warlock Level 14",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Hour", range="90 Feet"
            ),
            usage_tags=["buff", "summon"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )
        self.vestige_type = vestige_type

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        spirit, spell = _SEMBLANCE_SPIRITS[self.vestige_type]
        return [
            Paragraph(
                "Help your Vestige Companion briefly adopt a more powerful form."
            ),
            Facts(
                (
                    ("Action", "Magic action, with the vestige within 90 feet of you"),
                    ("Duration", "1 hour"),
                    (
                        "Form",
                        f"{spirit} (your vestige is a {self.vestige_type.value}; see the {spell} spell in the Player's Handbook)",
                    ),
                    (
                        "Spell level",
                        "Half your Warlock level (round down; maximum level 9)",
                    ),
                    (
                        "Keeps",
                        "Its personality, Divine Power Bonus Action, Hit Points and Hit Point Dice",
                    ),
                    (
                        "Temporary Hit Points",
                        "Equal to the spirit form's Hit Points; any left vanish after 1 hour, and the transformation ends early once it has none left",
                    ),
                )
            ),
            Option(
                "Other forms",
                (
                    Paragraph(
                        "Celestial vestige: Celestial Spirit (Summon Celestial). Fiend vestige: Fiendish Spirit (Summon Fiend). Undead vestige: Undead Spirit (Summon Undead)."
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Vestige Companion continues to grow in strength, and with your assistance, it can briefly adopt a more powerful form. Depending on the vestige's type, you can take a Magic action while the vestige is within 90 feet of you to shape-shift it for 1 hour into one of the following forms: Celestial Spirit (Celestial vestige; see the Summon Celestial spell in the Player's Handbook), Fiendish Spirit (Fiend vestige; see the Summon Fiend spell in the Player's Handbook), or Undead Spirit (Undead vestige; see the Summon Undead spell in the Player's Handbook). The vestige's game statistics are replaced by the spirit's stat block, and the spell's level is equal to half your Warlock level (round down; maximum level 9), but the vestige retains its personality, Divine Power Bonus Action, Hit Points, and Hit Point Dice.\n"
            "The vestige gains a number of Temporary Hit Points equal to the Hit Points of the spirit form. These Temporary Hit Points vanish if any remain after 1 hour, and the transformation ends early if it has no Temporary Hit Points left.\n"
            "Once you use this feature, you can't do so again until you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
