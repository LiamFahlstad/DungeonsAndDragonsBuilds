from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    regained_on_from_uses,
)
from Model.Content.Improvements import (
    DamageResistance,
    GrantLanguage,
    GrantSense,
    HitPointsPerLevelBonus,
    InitiativeProficiency,
    SkillProficiency,
    SkillProficiencyChoice,
    SpeedBonus,
    WeaponMinimumDamageDie,
)
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    ClericLevel0Spells,
    ClericLevel1Spells,
    ConjurationLevel1Spells,
    DivinationLevel0Spells,
    DivinationLevel1Spells,
    DruidLevel0Spells,
    DruidLevel1Spells,
    EnchantmentLevel0Spells,
    EvocationLevel0Spells,
    NecromancyLevel0Spells,
    SorcererLevel0Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    WarlockLevel1Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
)
from Core.Definitions import Ability, CharacterClass, DamageType, Language, Sense, Skill
from Core.Weapons import WeaponDamageRolls
from Model.Grants import Grants
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import PROFICIENCY_BONUS_GAINED_AT, MAX_PROFICIENCY_BONUS
from Model.View import CharacterView
from Model.CharacterSources import SpellSource
from Model.Spells import FeatureSpell
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    Table,
    dc_formula,
)


class OriginFeat(Feature):
    # A feat can be taken once, unless it says it's Repeatable (see
    # Character._validate_feats_taken_once).
    repeatable = False

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return regained_on_from_uses(self.uses)

    def grant_to(self, data: Grants) -> None:
        """Grant this feat; its granted_spells() are listed under it."""
        data.for_origin_feat(self).add_feature(self)


class Skilled(OriginFeat):
    """Also add proficiency in any combination of three skills or tools of your choice."""

    # 2024 PHB: Repeatable.
    repeatable = True

    def __init__(self, skills: list[Skill]):
        self._choice = SkillProficiencyChoice(
            skills, list(Skill), count=3, error_prefix="Skilled"
        )
        super().__init__(name="Skilled", origin="Origin Feat", passive=True)

    def apply(self, ledger_writer: LedgerWriter):
        self._choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Skill Proficiency",
                        "Any combination of three skills of your choice",
                    ),
                    ("Chosen", ", ".join(skill.value for skill in self._choice.skills)),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        choices = ", ".join(skill.value for skill in self._choice.skills)
        return (
            "You gain proficiency in any combination of three skills of your choice.\n"
            f"Choices: {choices}"
        )


class Alert(OriginFeat):
    def __init__(self):
        super().__init__(name="Alert", origin="Origin Feat")
        self._proficiency = InitiativeProficiency()

    def apply(self, ledger_writer: LedgerWriter):
        self._proficiency.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Initiative Proficiency",
                        "Add your Proficiency Bonus to Initiative rolls",
                    ),
                    (
                        "Initiative Swap",
                        "Immediately after you roll Initiative, swap Initiative with one willing ally in the same combat (not if either of you is Incapacitated)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Initiative Proficiency. When you roll Initiative, you can add your Proficiency Bonus to the roll.\n"
            "Initiative Swap. Immediately after you roll Initiative, you can swap your Initiative with the Initiative of one willing ally in the same combat. You can't make this swap if you or the ally has the Incapacitated condition.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class Crafter(OriginFeat):
    def __init__(self, artisans_tools: list[str]):
        self.artisans_tools = artisans_tools
        super().__init__(name="Crafter", origin="Origin Feat", usage_tags=["utility"])

    def get_tool_choices(self) -> str:
        tool_map = {
            "Artisan": "Artisan's Tools\tCrafted Gear",
            "Carpenter": "Carpenter's Tools\tLadder, Torch",
            "Leatherworker": "Leatherworker's Tools\tCase, Pouch",
            "Mason": "Mason's Tools\tBlock and Tackle",
            "Potter": "Potter's Tools\tJug, Lamp",
            "Smith": "Smith's Tools\tBall Bearings, Bucket, Caltrops, Grappling Hook, Iron Pot",
            "Tinker": "Tinker's Tools\tBell, Shovel, Tinder Box",
            "Weaver": "Weaver's Tools\tBasket, Rope, Net, Tent",
            "Woodcarver": "Woodcarver's Tools\tClub, Greatclub, Quarterstaff",
        }

        unknown = [t for t in self.artisans_tools if t not in tool_map]
        if unknown:
            raise ValueError(
                f"Unknown artisan tool(s): {', '.join(unknown)}. "
                f"Valid choices are: {', '.join(tool_map.keys())}."
            )

        return "\n".join(f"    * {tool_map[t]}" for t in self.artisans_tools)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        rows = tuple(
            tuple(line.strip(" *").split("\t"))
            for line in self.get_tool_choices().splitlines()
        )
        return [
            Facts(
                (
                    (
                        "Tool Proficiency",
                        "Three different Artisan's Tools of your choice from the Fast Crafting table",
                    ),
                    ("Discount", "20 percent off every nonmagical item you buy"),
                    (
                        "Fast Crafting",
                        "When you finish a Long Rest, craft one piece of gear from the table with tools you're proficient with. It falls apart when you finish another Long Rest.",
                    ),
                )
            ),
            Table(("Artisan's Tools", "Crafted gear"), rows),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Tool Proficiency. You gain proficiency with three different Artisan's Tools of your choice from the Fast Crafting table.\n"
            "Discount. Whenever you buy a nonmagical item, you receive a 20 percent discount on it.\n"
            "Fast Crafting:\n"
            "When you finish a Long Rest, you can craft one piece of gear from the Fast Crafting table,\n"
            "provided you have the Artisan's Tools associated with that item and have proficiency with those tools. \n"
            "The item lasts until you finish another Long Rest, at which point the item falls apart.\n"
            f"{self.get_tool_choices()}"
        )


class Healer(OriginFeat):
    def __init__(self):
        super().__init__(name="Healer", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Option(
                "Battle Medic",
                (
                    Facts(
                        (
                            (
                                "Action",
                                "Utilize action, expending one use of a Healer's Kit",
                            ),
                            ("Range", "5 feet"),
                            ("Target", "A creature you tend"),
                            (
                                "Effect",
                                "The creature can expend one Hit Point Die; you roll it, and it regains the roll + your Proficiency Bonus Hit Points",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Healing Rerolls",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Reroll a 1 on a die that restores Hit Points with a spell or Battle Medic; you must use the new roll",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Battle Medic:\n"
            "  If you have a Healer's Kit, you can expend one use of it and tend to a creature within 5 feet of yourself as a Utilize action.\n"
            "  That creature can expend one of its Hit Point Dice, and you then roll that die. The creature regains a number of Hit Points equal to the roll plus your Proficiency Bonus.\n"
            "Healing Rerolls.\n"
            "  Whenever you roll a die to determine the number of Hit Points you restore with a spell or with this feat's Battle Medic benefit,\n"
            "  you can reroll the die if it rolls a 1, and you must use the new roll.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class Lucky(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Lucky",
            origin="Origin Feat",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Luck Points", "Proficiency Bonus per Long Rest"),
                    (
                        "Advantage",
                        "When you roll a d20 for a D20 Test, spend 1 to give yourself Advantage",
                    ),
                    (
                        "Disadvantage",
                        "When a creature rolls a d20 for an attack roll against you, spend 1 to give it Disadvantage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Luck Points. You have a number of Luck Points equal to your Proficiency Bonus and can spend the points on the benefits below. You regain your expended Luck Points when you finish a Long Rest.\n"
            "Advantage. When you roll a d20 for a D20 Test, you can spend 1 Luck Point to give yourself Advantage on the roll.\n"
            "Disadvantage. When a creature rolls a d20 for an attack roll against you, you can spend 1 Luck Point to impose Disadvantage on that roll."
        )
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MagicInitiate(OriginFeat):
    # 2024 PHB: Repeatable.
    repeatable = True

    def __init__(
        self,
        cantrip_1: str,
        cantrip_2: str,
        spell: str,
        spell_casting_ability: Ability,
        character_class: CharacterClass,
    ):
        if character_class not in [
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.WIZARD,
        ]:
            raise ValueError("Character class must be Cleric, Druid, or Wizard.")

        cantrips_map = {
            CharacterClass.CLERIC: ClericLevel0Spells,
            CharacterClass.DRUID: DruidLevel0Spells,
            CharacterClass.WIZARD: WizardLevel0Spells,
        }
        spells_map = {
            CharacterClass.CLERIC: ClericLevel1Spells,
            CharacterClass.DRUID: DruidLevel1Spells,
            CharacterClass.WIZARD: WizardLevel1Spells,
        }

        if cantrip_1 not in list(cantrips_map[character_class]):
            raise ValueError(
                f"Cantrip 1 must be a valid {character_class.name.title()} cantrip. ({cantrip_1})"
            )
        if cantrip_2 not in list(cantrips_map[character_class]):
            raise ValueError(
                f"Cantrip 2 must be a valid {character_class.name.title()} cantrip. ({cantrip_2})"
            )
        if spell not in list(spells_map[character_class]):
            raise ValueError(
                f"Spell must be a valid {character_class.name.title()} level 1 spell. ({spell})"
            )

        self.character_class = character_class
        self.cantrip_1 = cantrip_1
        self.cantrip_2 = cantrip_2
        self.spell = spell
        self.spell_casting_ability = spell_casting_ability
        super().__init__(
            name=f"Magic Initiate ({self.character_class.value})",
            origin="Origin Feat",
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(spell, self.spell_casting_ability, source=SpellSource.CHOSEN)
            for spell in (self.cantrip_1, self.cantrip_2, self.spell)
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        spell_list = self.character_class.name.title()
        return [
            Facts(
                (
                    (
                        "Cantrips",
                        f"{self.cantrip_1} and {self.cantrip_2} ({spell_list} list)",
                    ),
                    (
                        "Level 1 spell",
                        f"{self.spell}; cast it once per Long Rest without a spell slot",
                    ),
                    ("Prepared", "All three are always prepared"),
                    ("Spellcasting ability", self.spell_casting_ability.value),
                    (
                        "Spell Change",
                        f"Whenever you gain a level, replace one with another spell of the same level from the {spell_list} list",
                    ),
                    (
                        "Repeatable",
                        "You can take this feat again, choosing a different spell list",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        spells = (
            f"Cantrip 1: {self.cantrip_1}, Cantrip 2: {self.cantrip_2}, "
            f"Level 1 Spell: {self.spell} (Cast once per long rest without a spell slot)"
        )
        return (
            f"Magic Initiate {self.character_class.name.title()} Spellcasting\n"
            f"Spell List (always prepared): {spells}\n"
            "Spell Change. Whenever you gain a new level, you can replace one of the spells you chose for this feat with a different spell of the same level from the chosen spell list.\n\n"
            "Repeatable. You can take this feat more than once, but you must choose a different spell list each time."
        )


def _resolve_spell_enum(value, enum_type: type) -> str:
    if isinstance(value, enum_type):
        return value.value
    return value


class MagicInitiateCleric(MagicInitiate):
    def __init__(
        self,
        cantrip_1: str,
        cantrip_2: str,
        spell: str,
        spell_casting_ability: Ability,
    ):
        super().__init__(
            _resolve_spell_enum(cantrip_1, ClericLevel0Spells),
            _resolve_spell_enum(cantrip_2, ClericLevel0Spells),
            _resolve_spell_enum(spell, ClericLevel1Spells),
            spell_casting_ability,
            character_class=CharacterClass.CLERIC,
        )


class MagicInitiateDruid(MagicInitiate):
    def __init__(
        self,
        cantrip_1: str,
        cantrip_2: str,
        spell: str,
        spell_casting_ability: Ability,
    ):
        super().__init__(
            _resolve_spell_enum(cantrip_1, DruidLevel0Spells),
            _resolve_spell_enum(cantrip_2, DruidLevel0Spells),
            _resolve_spell_enum(spell, DruidLevel1Spells),
            spell_casting_ability,
            character_class=CharacterClass.DRUID,
        )


class MagicInitiateWizard(MagicInitiate):
    def __init__(
        self,
        cantrip_1: str,
        cantrip_2: str,
        spell: str,
        spell_casting_ability: Ability,
    ):
        super().__init__(
            _resolve_spell_enum(cantrip_1, WizardLevel0Spells),
            _resolve_spell_enum(cantrip_2, WizardLevel0Spells),
            _resolve_spell_enum(spell, WizardLevel1Spells),
            spell_casting_ability,
            character_class=CharacterClass.WIZARD,
        )


class Musician(OriginFeat):
    def __init__(self):
        super().__init__(name="Musician", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Instrument Training",
                        "Proficiency with three Musical Instruments of your choice",
                    ),
                    (
                        "Encouraging Song",
                        "As you finish a Short or Long Rest, play an instrument you're proficient with: up to Proficiency Bonus allies who hear it gain Heroic Inspiration",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Instrument Training: You gain proficiency with three Musical Instruments of your choice.\n"
            "\n"
            "Encouraging Song: As you finish a Short or Long Rest, you can play a song on a Musical Instrument with which you have proficiency and give Heroic Inspiration to allies who hear the song. The number of allies you can affect in this way equals your Proficiency Bonus.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SavageAttacker(OriginFeat):
    def __init__(self):
        super().__init__(name="Savage Attacker", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "Once per turn, you hit a target with a weapon"),
                    (
                        "Effect",
                        "Roll the weapon's damage dice twice and use either roll",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You've trained to deal particularly damaging strikes.\n"
            "Once per turn when you hit a target with a weapon, you can roll the weapon's damage dice twice and use either roll against the target.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class TavernBrawler(OriginFeat):
    def __init__(self):
        super().__init__(name="Tavern Brawler", origin="Origin Feat")
        # Enhanced Unarmed Strike: 1d4 + Strength instead of the normal
        # damage. Shown only where it beats the strike's own die (the default
        # 1, not a Monk's Martial Arts die).
        self._enhanced_unarmed_strike = WeaponMinimumDamageDie(
            lambda weapon: weapon.is_unarmed_strike,
            WeaponDamageRolls.D4,
            Ability.STRENGTH,
            "Tavern Brawler",
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._enhanced_unarmed_strike.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Enhanced Unarmed Strike",
                        "When it hits and deals damage, can deal 1d4 + Strength modifier Bludgeoning damage instead of the normal damage",
                    ),
                    (
                        "Damage Rerolls",
                        "Reroll a 1 on an Unarmed Strike damage die; you must use the new roll",
                    ),
                    ("Improvised Weaponry", "Proficiency with improvised weapons"),
                    (
                        "Push",
                        "Once per turn, when you hit with an Unarmed Strike as part of the Attack action on your turn, can deal damage and also push the target 5 feet away",
                    ),
                    (
                        "On this sheet",
                        "The Unarmed Strike damage shown uses 1d4 + Strength modifier unless its own die is better (e.g. a Martial Arts die)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Enhanced Unarmed Strike. When you hit with your Unarmed Strike and deal damage, you can deal Bludgeoning damage equal to 1d4 plus your Strength modifier instead of the normal damage of an Unarmed Strike.\n"
            "\n"
            "Damage Rerolls. Whenever you roll a damage die for your Unarmed Strike, you can reroll the die if it rolls a 1, and you must use the new roll.\n"
            "\n"
            "Improvised Weaponry. You have proficiency with improvised weapons.\n"
            "\n"
            "Push. When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can deal damage to the target and also push it 5 feet away from you. You can use this benefit only once per turn.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Tough(OriginFeat):
    def __init__(self):
        self._hp = HitPointsPerLevelBonus(2)
        super().__init__(name="Tough", origin="Origin Feat", passive=True)

    def apply(self, ledger_writer: LedgerWriter):
        self._hp.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Hit Point maximum",
                        "+2 per character level, now and whenever you gain a level",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "Resilience. You gain 2 additional Hit Points for each level you have. "
            "Whenever you gain a new level, you gain 2 additional Hit Points."
        )


class CultOfTheDragonInitiate(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Cult of the Dragon Initiate",
            origin="Origin Feat",
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="short or long rest",
                current_formula="Used by Inspired by Fear.",
            ),
        )

    def apply(self, ledger_writer: LedgerWriter):
        # Dragon's Tongue. (A character who already knows Draconic picks
        # another language instead; that choice isn't tracked.)
        GrantLanguage(Language.DRACONIC).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Inspired by Fear's once-per-rest box is in the panel below.
        return [
            Facts(
                (
                    (
                        "Dragon's Tongue",
                        "You know Draconic (or, if you already do, another language of your choice)",
                    ),
                )
            ),
            Option(
                "Dragon's Terror",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            ("Range", "30 feet"),
                            ("Target", "One creature you can see"),
                            ("Save", f"Wisdom, DC {dc_formula(Ability.WISDOM)}"),
                            ("Failed", "Frightened until the end of your next turn"),
                            (
                                "Afterwards",
                                "A target that succeeds, or whose fear ends, is immune for 24 hours",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Inspired by Fear",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "You cause a creature to be Frightened, with you as the source of its fear",
                            ),
                            ("Effect", "Gain Heroic Inspiration if you lack it"),
                            ("Limit", "Once per Short or Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Dragon’s Tongue. You know Draconic. If you already know Draconic when you select this feat, you instead learn one language of your choice from the language tables in the Player’s Handbook or chapter 2 of this book.\n"
            "Dragon’s Terror. You can take a Magic action to instill terror in a creature you can see within 30 feet of yourself. The target must succeed on a Wisdom saving throw (DC 8 plus your Wisdom modifier and Proficiency Bonus) or have the Frightened condition until the end of your next turn. If the target succeeds on the save or when the effect ends for a target, the target is immune to this effect for 24 hours.\n"
            "Inspired by Fear. When you cause a creature to have the Frightened condition and you are the source of its fear, you can gain Heroic Inspiration if you lack it. Once you use this benefit, you can’t use it again until you finish a Short or Long Rest.\n"
        )

    def calculate_dc(self, character: CharacterView) -> int:
        wisdom_modifier = character.get_wisdom_modifier()
        proficiency_bonus = character.get_proficiency_bonus()
        return 8 + wisdom_modifier + proficiency_bonus

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class EmeraldEnclaveFledgling(OriginFeat):
    def __init__(self, spell_casting_ability: Ability):
        if spell_casting_ability not in (
            Ability.INTELLIGENCE,
            Ability.WISDOM,
            Ability.CHARISMA,
        ):
            raise ValueError(
                "Emerald Enclave Fledgling spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        self.spell_casting_ability = spell_casting_ability
        super().__init__(name="Emerald Enclave Fledgling", origin="Origin Feat")

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                DruidLevel1Spells.SPEAK_WITH_ANIMALS, self.spell_casting_ability
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Speak with Animals",
                        f"Always prepared; cast it with your spell slots. {self.spell_casting_ability.value} is its spellcasting ability. Cast as a Ritual, it lasts 8 hours.",
                    ),
                    (
                        "Tag Team",
                        "When you take the Help action, swap places with a willing, non-Incapacitated ally within 5 feet; this doesn't provoke Opportunity Attacks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Speak with Animals. You always have the Speak with Animals spell prepared and can cast it with any spell slots you have. "
            f"{self.spell_casting_ability.value} is your spellcasting ability for this spell. When you cast this spell as a Ritual, its duration is 8 hours.\n"
            "\n"
            "Tag Team. When you take the Help action, you can switch places with a willing ally within 5 feet of yourself as part of that same action. This movement doesn’t provoke Opportunity Attacks. You can’t use this benefit if the ally has the Incapacitated condition.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class FamiliarFriend(OriginFeat):
    def __init__(self, spell_casting_ability: Ability):
        if spell_casting_ability not in (
            Ability.INTELLIGENCE,
            Ability.WISDOM,
            Ability.CHARISMA,
        ):
            raise ValueError(
                "Familiar Friend spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        self.spell_casting_ability = spell_casting_ability
        super().__init__(
            name="Familiar Friend",
            origin="Origin Feat",
            # One free casting of Find Familiar per Long Rest.
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                ConjurationLevel1Spells.FIND_FAMILIAR, self.spell_casting_ability
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Faithful Companion",
                        f"Find Familiar is always prepared; cast it once per Long Rest without a slot or Material components, or with your spell slots. {self.spell_casting_ability.value} is its spellcasting ability.",
                    ),
                    (
                        "Fortified Familiar",
                        "When you cast Find Familiar, the familiar's Hit Point maximum and current Hit Points rise by 2 x your character level",
                    ),
                    (
                        "Helpful Friend",
                        "Advantage on ability checks with skills you're proficient in while your familiar is within 5 feet of you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Faithful Companion. You always have the Find Familiar spell prepared. "
            f"{self.spell_casting_ability.value} is your spellcasting ability for this spell. "
            "You can cast it once without a spell slot or Material components, and you regain the ability to cast it in this way when you finish a Long Rest. You can also cast the spell using any spell slots you have.\n"
            "Fortified Familiar. When you cast the Find Familiar spell, your familiar’s Hit Point maximum and current Hit Points are increased by an amount equal to twice your character level "
            f"(currently {2 * character.character_level}).\n"
            "Helpful Friend. When you make an ability check using a skill in which you have proficiency while your familiar is within 5 feet of you, you gain Advantage on the check."
        )
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return 1


class HarperAgent(OriginFeat):
    def __init__(self):
        super().__init__(name="Harper Agent", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Language", "Thieves' Cant"),
                    (
                        "Instrument Training",
                        "Proficiency with a Musical Instrument of your choice",
                    ),
                    (
                        "Distracting Melody",
                        "When you Help an ally's attack roll, the enemy you distract can be within 30 feet of you instead of 5, if it can see or hear you",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Thieves’ Cant. You know Thieves’ Cant.\n"
            "Instrument Training. You gain proficiency with a Musical Instrument of your choice.\n"
            "Distracting Melody. When you take the Help action to assist an ally’s attack roll, the enemy you’re distracting can be within 30 feet of you, rather than within 5 feet of you, provided the enemy can see or hear you.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class LordsAllianceAgent(OriginFeat):
    def __init__(self):
        super().__init__(name="Lords' Alliance Agent", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Inspiring Strike",
                        "Once per turn, when you score a Critical Hit, an ally within 30 feet who can see or hear you and lacks Heroic Inspiration gains it",
                    ),
                    (
                        "Reassert Honor",
                        "When an enemy you can see damages an ally within 5 feet of you, you have Advantage on your next attack roll against it before the end of your next turn",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Inspiring Strike. Once per turn when you score a Critical Hit against a creature, you can choose an ally within 30 feet of yourself who can see or hear you and who lacks Heroic Inspiration. That ally gains Heroic Inspiration.\n"
            "Reassert Honor. When an enemy you can see deals damage to an ally of yours that is within 5 feet of you, you have Advantage on your next attack roll against that enemy before the end of your next turn.\n"
        )


class PurpleDragonRook(OriginFeat):
    VALID_SKILLS = [Skill.INSIGHT, Skill.PERFORMANCE, Skill.PERSUASION]

    def __init__(self, entreat_skill: Skill):
        self._choice = SkillProficiencyChoice(
            [entreat_skill],
            self.VALID_SKILLS,
            count=1,
            error_prefix="Purple Dragon Rook",
        )
        super().__init__(
            name="Purple Dragon Rook",
            origin="Origin Feat",
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="long rest",
                current_formula="Used by Rallying Cry.",
            ),
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        skill_name = self._choice.skills[0].value if self._choice.skills else "Insight"
        return [
            Facts(
                (
                    ("Entreat", f"Proficiency in {skill_name}"),
                    (
                        "Rallying Cry",
                        "When you roll Initiative and aren't Incapacitated, Proficiency Bonus creatures you can see within 30 feet gain Heroic Inspiration. Once per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        skill_name = self._choice.skills[0].value if self._choice.skills else "Insight"
        return (
            "You gain the following benefits.\n"
            f"Entreat. You gain proficiency in {skill_name}.\n"
            "Rallying Cry. When you roll Initiative and don’t have the Incapacitated condition, you can choose a number of creatures equal to your Proficiency Bonus that you can see within 30 feet of yourself. Those creatures gain Heroic Inspiration.\n"
            "Once you use this benefit, you can’t do so again until you finish a Long Rest.\n"
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SpellfireSpark(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Spellfire Spark",
            origin="Origin Feat",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Magic Absorption",
                        "Once per turn, when a spell or magical effect damages you, reduce the damage by 1d4 (not while Incapacitated)",
                    ),
                    (
                        "Spellfire Flame",
                        "You learn Sacred Flame; Intelligence, Wisdom or Charisma (chosen with the feat) is its spellcasting ability. Cast it as a Bonus Action Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Magic Absorption. Once per turn, when you take damage from a spell or magical effect, you reduce the total damage taken by 1d4. You can’t use this benefit if you have the Incapacitated condition.\n"
            "Spellfire Flame. You learn the Sacred Flame cantrip. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat). You can also cast this cantrip as a Bonus Action a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TyroOfTheGauntlet(OriginFeat):
    def __init__(self):
        super().__init__(name="Tyro of the Gauntlet", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Stand as One",
                        "Reaction when an ally within 5 feet (not Incapacitated) would be pushed or pulled: it isn't",
                    ),
                    (
                        "Vigilant",
                        "When you take the Ready action, the next attack roll against you before the start of your next turn has Disadvantage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Stand as One. When an ally within 5 feet of you is subjected to an effect that would push or pull it, you can take a Reaction to prevent that ally from being pushed or pulled. To receive this benefit, the ally can’t have the Incapacitated condition.\n"
            "Vigilant. When you take the Ready action, the next attack roll made against you has Disadvantage before the start of your next turn.\n"
        )


class ZhentarimRuffian(OriginFeat):
    def __init__(self):
        super().__init__(name="Zhentarim Ruffian", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Exploit Opening",
                        "When you roll damage for an Opportunity Attack, roll the damage dice twice and use either roll",
                    ),
                    (
                        "Family First",
                        "When you roll Initiative with Heroic Inspiration, expend it to give yourself and your allies Advantage on that Initiative roll",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Exploit Opening. When you roll damage for an Opportunity Attack, you can roll the damage dice twice and use either roll against the target.\n"
            "Family First. If you have Heroic Inspiration when you roll Initiative, you can expend it to give yourself and your allies Advantage on that Initiative roll.\n"
        )


class SharpEye(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Sharp Eye",
            origin="Origin Feat",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You take the Search or Study action"),
                    (
                        "Effect",
                        "Advantage on any ability check made as part of that action",
                    ),
                    ("Still fails", "The use isn't expended"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you take the Search or Study action, you can give yourself Advantage on any ability check made as part of that action. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest. If the check fails, the use of this feature isn't expended."
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class Survivor(OriginFeat):
    def __init__(self):
        super().__init__(name="Survivor", origin="Origin Feat")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Hypervigilance",
                        "When you roll Initiative, reroll a d20 of 9 or lower; use the new roll",
                    ),
                    (
                        "Steel Yourself",
                        "Reaction when you fail a save to avoid or end Charmed or Frightened: add your Proficiency Bonus to it. Once per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Hypervigilance. Whenever you roll Initiative, you can reroll the d20 if the number rolled is 9 or lower. You must use the new roll.\n"
            "Steel Yourself. When you fail a saving throw to avoid or end the Charmed or Frightened condition, you can take a Reaction to add a bonus to the roll potentially causing it to succeed. The bonus is equal to your Proficiency Bonus.\n"
            "Once you take this Reaction, you can't do so again until you finish a Long Rest.\n"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


_MENTAL_ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)


def _uses_per_proficiency_bonus(regain_all_on: str) -> FeatureUses:
    """Uses for a benefit usable "a number of times equal to your Proficiency
    Bonus"; pair it with a number_of_uses() that returns the proficiency bonus."""
    return FeatureUses(
        max_uses=MAX_PROFICIENCY_BONUS,
        regain_all_on=regain_all_on,
        current_formula="Current amount: equal to your proficiency bonus.",
        gained_at=PROFICIENCY_BONUS_GAINED_AT,
    )


class _SpellcastingOriginFeat(OriginFeat):
    """Base class for origin feats that teach a spell whose spellcasting
    ability (Intelligence, Wisdom, or Charisma) is chosen with the feat.

    Subclasses declare:
        _NAME   – feat display name
        _SPELL  – the spell the feat teaches
        _USES   – optional FeatureUses for a limited-use benefit

    They only need to implement get_description().
    """

    _NAME: str
    _SPELL: str
    _USES: FeatureUses | None = None

    def __init__(self, spell_casting_ability: Ability):
        if spell_casting_ability not in _MENTAL_ABILITIES:
            raise ValueError(
                f"{self._NAME} spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        self.spell_casting_ability = spell_casting_ability
        super().__init__(name=self._NAME, origin="Origin Feat", uses=self._USES)

    def granted_spells(self) -> list[FeatureSpell]:
        return [FeatureSpell(self._SPELL, self.spell_casting_ability)]


class ArcaneArtist(_SpellcastingOriginFeat):
    _NAME = "Arcane Artist"
    _SPELL = BardLevel0Spells.MINOR_ILLUSION
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"Minor Illusion; {self.spell_casting_ability.value} is its spellcasting ability",
                    ),
                    (
                        "Inspiring Magic",
                        "When you cast an Illusion spell, an ally within 30 feet who can see you gains Heroic Inspiration. Once per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the Minor Illusion cantrip. {self.spell_casting_ability.value} is your spellcasting ability for this spell.\n"
            "Inspiring Magic. When you cast a spell from the Illusion school, you can choose one ally within 30 feet of yourself who can see you. That ally gains Heroic Inspiration. Once you use this benefit, you can't use it again until you finish a Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ArcaneEloquence(_SpellcastingOriginFeat):
    _NAME = "Arcane Eloquence"
    _SPELL = BardLevel0Spells.VICIOUS_MOCKERY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"Vicious Mockery; {self.spell_casting_ability.value} is your spellcasting ability for it",
                    ),
                    (
                        "Smooth Talker",
                        "Add 1d4 to Charisma (Deception, Intimidation or Persuasion) checks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the Vicious Mockery cantrip. {self.spell_casting_ability.value} is your spellcasting ability for this spell.\n"
            "Smooth Talker. When you make a Charisma (Deception, Intimidation, or Persuasion) check, you can roll 1d4 and add the number rolled to the ability check."
        )


class ArcaneInfiltrator(_SpellcastingOriginFeat):
    _NAME = "Arcane Infiltrator"
    _SPELL = BardLevel0Spells.FRIENDS
    _USES = _uses_per_proficiency_bonus("long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"Friends; {self.spell_casting_ability.value} is its spellcasting ability",
                    ),
                    (
                        "Cunning Diversion",
                        "Take the Dodge action as a Bonus Action, Proficiency Bonus times per Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the Friends cantrip. {self.spell_casting_ability.value} is your spellcasting ability for this spell.\n"
            "Cunning Diversion. You can take the Dodge action as a Bonus Action. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ArcaneOmens(_SpellcastingOriginFeat):
    _NAME = "Arcane Omens"
    _SPELL = ClericLevel0Spells.GUIDANCE
    _USES = _uses_per_proficiency_bonus("long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"Guidance; {self.spell_casting_ability.value} is its spellcasting ability",
                    ),
                    (
                        "Helpful Premonition",
                        "Reaction when you or a creature you can see within 30 feet fails a save: add 1d4 to it. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the Guidance cantrip. {self.spell_casting_ability.value} is your spellcasting ability for this spell.\n"
            "Helpful Premonition. When you or a creature you can see within 30 feet of yourself fails a saving throw, you can take a Reaction to roll 1d4 and add the number rolled to the save's total, potentially turning the failure into a success. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ArcaneOverload(_SpellcastingOriginFeat):
    _NAME = "Arcane Overload"
    _SPELL = EvocationLevel0Spells.FIRE_BOLT
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"Fire Bolt; {self.spell_casting_ability.value} is its spellcasting ability",
                    ),
                    (
                        "Power Surge",
                        "When an Evocation spell you cast deals damage, add your Proficiency Bonus to one of its damage rolls. Once per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the Fire Bolt cantrip. {self.spell_casting_ability.value} is your spellcasting ability for this spell.\n"
            "Power Surge. When you cast an Evocation spell and deal damage with it, you can add your Proficiency Bonus to one damage roll of that spell. Once you use this benefit, you can't do so again until you finish a Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ArcaneSafeguard(_SpellcastingOriginFeat):
    _NAME = "Arcane Safeguard"
    _SPELL = ClericLevel0Spells.RESISTANCE
    _USES = _uses_per_proficiency_bonus("long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"Resistance; {self.spell_casting_ability.value} is its spellcasting ability. Cast it as a Bonus Action Proficiency Bonus times per Long Rest.",
                    ),
                    (
                        "Sheltering Aid",
                        "When you take the Help action for an ally's ability check, the ally gains Temporary Hit Points equal to your Proficiency Bonus",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the Resistance cantrip. {self.spell_casting_ability.value} is your spellcasting ability for this spell. "
            "You can cast the Resistance cantrip as a Bonus Action. You can do so a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Sheltering Aid. When you take the Help action to assist with an ally's ability check, that ally gains a number of Temporary Hit Points equal to your Proficiency Bonus."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ArcaneUndertaker(_SpellcastingOriginFeat):
    _NAME = "Arcane Undertaker"
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def __init__(
        self,
        necromancy_cantrip: NecromancyLevel0Spells,
        spell_casting_ability: Ability,
    ):
        self.necromancy_cantrip = necromancy_cantrip
        super().__init__(spell_casting_ability)

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(
                self.necromancy_cantrip,
                self.spell_casting_ability,
                source=SpellSource.CHOSEN,
            )
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cantrip",
                        f"{self.necromancy_cantrip.value}; {self.spell_casting_ability.value} is its spellcasting ability",
                    ),
                    (
                        "Knowledge from the Dead",
                        "Add 1d4 to Intelligence (History) and Wisdom (Medicine) checks",
                    ),
                    (
                        "Understanding of Death",
                        "When you take the Help action to stabilize a creature at 0 Hit Points, gain Heroic Inspiration; once per Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Cantrip. You learn the {self.necromancy_cantrip.value} cantrip (a Cleric or Wizard cantrip from the Necromancy school). {self.spell_casting_ability.value} is your spellcasting ability for this spell.\n"
            "Knowledge from the Dead. When you make an Intelligence (History) or Wisdom (Medicine) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Understanding of Death. When you take the Help action to stabilize a creature with 0 Hit Points, you gain Heroic Inspiration. Once you use this benefit, you can't use it again until you finish a Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class PortalJumper(OriginFeat):
    VALID_DAMAGE_TYPES = (DamageType.NECROTIC, DamageType.PSYCHIC, DamageType.RADIANT)

    def __init__(self, damage_type: DamageType):
        if damage_type not in self.VALID_DAMAGE_TYPES:
            allowed = ", ".join(dt.value for dt in self.VALID_DAMAGE_TYPES)
            raise ValueError(f"Portal Jumper damage type must be one of: {allowed}.")
        self.damage_type = damage_type
        self._resistance = DamageResistance(damage_type)
        super().__init__(
            name="Portal Jumper",
            origin="Origin Feat",
            uses=_uses_per_proficiency_bonus("long rest"),
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Otherworldly Resilience",
                        f"Resistance to {self.damage_type.value} damage",
                    ),
                    (
                        "Portal Step",
                        "Spend 15 feet of movement to teleport to an unoccupied space you can see within 15 feet. Once per turn, Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Otherworldly Resilience. You have Resistance to {self.damage_type.value} damage.\n"
            "Portal Step. You can spend 15 feet of movement to teleport to an unoccupied space you can see within 15 feet of yourself. You can use this benefit a number of times equal to your Proficiency Bonus but only once per turn, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TransmutedAnatomy(OriginFeat):
    def __init__(self):
        self._speed = SpeedBonus(5)
        super().__init__(
            name="Transmuted Anatomy",
            origin="Origin Feat",
            uses=_uses_per_proficiency_bonus("long rest"),
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._speed.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Lengthened Stride", "Speed +5 feet"),
                    (
                        "Resilient Anatomy",
                        "Advantage on saves against being shape-shifted against your will",
                    ),
                    (
                        "Resilience",
                        "Reaction when you fail a Constitution save: add 1d4 to it. Proficiency Bonus times per Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Lengthened Stride. Your Speed increases by 5 feet.\n"
            "Resilient Anatomy. You have Advantage on saving throws against effects that would compel you to shape-shift against your will. "
            "Additionally, when you fail a Constitution saving throw, you can take a Reaction to roll 1d4 and add the number rolled to the save, potentially turning the failure into a success. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ChildOfTheSun(_SpellcastingOriginFeat):
    _NAME = "Child of the Sun"
    _SPELL = BardLevel1Spells.FAERIE_FIRE
    # One free cast of Faerie Fire per Long Rest.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Eyes of Eirdu",
                        "You and allies within 10 feet have Advantage on saves to avoid or end Blinded",
                    ),
                    (
                        "Faerie Fire",
                        f"You learn it; {self.spell_casting_ability.value} is its spellcasting ability. Cast it once per Long Rest without a slot (then damage can't break your Concentration on it), or with your spell slots.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Eyes of Eirdu. You and allies within 10 feet of you have Advantage on saving throws made to avoid or end the Blinded condition.\n"
            f"Faerie Fire. You learn the Faerie Fire spell. {self.spell_casting_ability.value} is your spellcasting ability for this spell. "
            "You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast the spell using any spell slots you have. "
            "When you cast Faerie Fire without a spell slot using this benefit, taking damage can't break your Concentration on the spell."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ShadowmoorHexer(_SpellcastingOriginFeat):
    _NAME = "Shadowmoor Hexer"
    _SPELL = WarlockLevel1Spells.HEX
    # One free cast of Hex per Long Rest.
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Hex",
                        f"Always prepared; cast it once per Long Rest without a slot, or with your spell slots. {self.spell_casting_ability.value} is its spellcasting ability.",
                    ),
                    (
                        "Curse Magic",
                        "When a creature cursed by your Hex hits you with an attack roll, it takes Psychic damage equal to your Proficiency Bonus (once per turn)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            f"Hex. You always have the Hex spell prepared. {self.spell_casting_ability.value} is your spellcasting ability for this spell. "
            "You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast the spell using any spell slots you have.\n"
            "Curse Magic. When a creature that you've cursed with Hex hits you with an attack roll, the creature takes Psychic damage equal to your Proficiency Bonus. A creature takes this damage only once per turn."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class TirelessReveler(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Tireless Reveler",
            origin="Origin Feat",
            uses=_uses_per_proficiency_bonus("short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "An ally you can see within 60 feet expends Heroic Inspiration",
                    ),
                    ("Effect", "Gain Heroic Inspiration if you lack it"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "When an ally you can see within 60 feet of yourself expends Heroic Inspiration, you can gain Heroic Inspiration if you lack it. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Short or Long Rest."

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class VampireHunter(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Vampire Hunter",
            origin="Origin Feat",
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Adroit Escape",
                        "Advantage on checks to escape nonmagical restraints or the Grappled condition",
                    ),
                    (
                        "Vitality Ward",
                        "Reaction when you take Necrotic damage: reduce it by Proficiency Bonus d6s. Once per Short or Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Adroit Escape. You have Advantage on checks to escape from nonmagical restraints or the Grappled condition.\n"
            "Vitality Ward. When you take Necrotic damage, you can take a Reaction to mitigate the damage. Roll a number of d6s equal to your Proficiency Bonus, and add them together. Reduce the Necrotic damage you take by this total. Once you use this benefit, you can't use it again until you finish a Short or Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class VampiresPlaything(OriginFeat):
    def __init__(self):
        super().__init__(
            name="Vampire's Plaything",
            origin="Origin Feat",
            uses=_uses_per_proficiency_bonus("long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Timely Retreat's uses are in the panel below.
        return [
            Facts(
                (
                    (
                        "Decanting",
                        "When you finish a Long Rest with an empty vial or flask, create a Potion of Healing or an Antitoxin. It evaporates when you finish another Long Rest.",
                    ),
                    (
                        "Timely Retreat",
                        "Bonus Action: take the Dash or Disengage action. Proficiency Bonus times per Long Rest.",
                    ),
                    (
                        "Vampiric Connection",
                        "While on the same plane, your former vampire master (its fate is up to the DM) can talk to you telepathically, and you can let it perceive through your senses",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Decanting. When you finish a Long Rest, you can create one Potion of Healing or an Antitoxin, as long as you have an empty vial or flask. These liquids evaporate when you finish another Long Rest.\n"
            "Timely Retreat. You can take a Bonus Action to take the Dash action or the Disengage action. You can use this benefit a number of times equal to your Proficiency Bonus, and you recover all expended uses when you finish a Long Rest.\n"
            "Vampiric Connection. The DM determines the fate of your former vampire master. While you and your former vampire master are on the same plane of existence, the vampire can communicate with you telepathically, and you can choose to allow the vampire to perceive through your senses."
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


# ---------------------------------------------------------------------------
# Dragonmark Feats
# ---------------------------------------------------------------------------

_DRAGONMARK_PREREQUISITE = "Dragonmark Feat (Prerequisite: Eberron Campaign, Can't Have Another Dragonmark Feat)\n"
_DRAGONMARK_FREE_CAST = "Always prepared. Cast it once without a spell slot (regained on a Long Rest), or with your spell slots."


def _dragonmark_spell_names(spells: tuple) -> str:
    names = [str(spell) for spell in spells]
    if len(names) <= 1:
        return "".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


class _DragonmarkFeat(OriginFeat):
    """Base class for the twelve house Dragonmark feats (Eberron: Forge of the
    Artificer). Each adds 1d4 to some ability checks, teaches cantrips and
    always-prepared spells it can cast once per Long Rest without a spell
    slot (more at character level 3), with a chosen Intelligence, Wisdom or
    Charisma spellcasting ability, and has a Spells of the Mark list.

    Subclasses declare:
        _NAME            - feat name
        _INTUITION       - (benefit name, the checks it adds 1d4 to)
        _MAGIC           - the spell benefit's name, e.g. "Healing Touch"
        _CANTRIPS        - cantrips the feat teaches
        _SPELLS          - spells always prepared from the start
        _LEVEL_3_SPELLS  - spells added the same way at character level 3
        _MARK_SPELLS     - the Spells of the Mark table, spell levels 1-5
        _USES            - optional FeatureUses for a limited-use benefit

    pass their own usage_tags (and activation) to __init__, add any other
    benefit in _extra_facts(), and write get_description() from the feat's
    own text, ending with _spells_of_the_mark_text().

    Spells of the Mark is shown on the card only: the engine can't add
    spells to a class's spell list.
    """

    _NAME: str
    _INTUITION: tuple[str, str]
    _MAGIC: str
    _CANTRIPS: tuple[str, ...] = ()
    _SPELLS: tuple[str, ...] = ()
    _LEVEL_3_SPELLS: tuple[str, ...] = ()
    _MARK_SPELLS: tuple[str, str, str, str, str]
    _USES: FeatureUses | None = None

    def __init__(
        self,
        character_level: int,
        spell_casting_ability: Ability,
        usage_tags=None,
        activation: FeatureActivation | None = None,
    ):
        if character_level < 1:
            raise ValueError(f"{self._NAME} requires character level 1 or higher.")
        if spell_casting_ability not in _MENTAL_ABILITIES:
            raise ValueError(
                f"{self._NAME} spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        self.character_level = character_level
        self.spell_casting_ability = spell_casting_ability
        super().__init__(
            name=self._NAME,
            origin="Dragonmark Feat",
            usage_tags=usage_tags,
            activation=activation,
            uses=self._USES,
        )

    def granted_spells(self) -> list[FeatureSpell]:
        """The cantrips, and the always-prepared spells castable once per
        Long Rest without a slot at this feat's character level."""
        free_cast = list(self._SPELLS)
        if self.character_level >= 3:
            free_cast += list(self._LEVEL_3_SPELLS)
        return [
            FeatureSpell(cantrip, self.spell_casting_ability)
            for cantrip in self._CANTRIPS
        ] + [
            FeatureSpell(spell, self.spell_casting_ability, _DRAGONMARK_FREE_CAST)
            for spell in free_cast
        ]

    def _extra_facts(self) -> tuple:
        """(label, text) rows for this mark's benefits beyond the shared ones."""
        return ()

    def _magic_text(self) -> str:
        parts = []
        if self._CANTRIPS:
            parts.append(
                f"You know the {_dragonmark_spell_names(self._CANTRIPS)} cantrip"
            )
        if self._SPELLS:
            each = "each" if len(self._SPELLS) > 1 else "it"
            parts.append(
                f"{_dragonmark_spell_names(self._SPELLS)} always prepared; cast {each} once per Long Rest without a spell slot, or with your spell slots"
            )
        return ". ".join(parts)

    def _level_3_text(self) -> str:
        spells = _dragonmark_spell_names(self._LEVEL_3_SPELLS)
        if self._SPELLS:
            return f"{spells} also always prepared, cast the same way"
        return f"{spells} always prepared; cast it once per Long Rest without a spell slot, or with your spell slots"

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        intuition, checks = self._INTUITION
        rows = [
            (intuition, f"Add 1d4 to {checks}"),
            (self._MAGIC, self._magic_text()),
        ]
        if self._LEVEL_3_SPELLS:
            rows.append(("Character Level 3", self._level_3_text()))
        rows.append(
            (
                "Spellcasting Ability",
                f"{self.spell_casting_ability.value} (chosen with this feat)",
            )
        )
        rows.extend(self._extra_facts())
        return [
            Facts(tuple(rows)),
            Option(
                "Spells of the Mark",
                (
                    Paragraph(
                        "If you have the Spellcasting or Pact Magic feature, these spells are added to its spell list."
                    ),
                    Table(
                        ("Spell Level", "Spells"),
                        tuple(
                            (str(level), spells)
                            for level, spells in enumerate(self._MARK_SPELLS, 1)
                        ),
                    ),
                ),
            ),
        ]

    def _spells_of_the_mark_text(self) -> str:
        return f"{self._NAME} Spells\n" + "\n".join(
            f"Level {level}: {spells}"
            for level, spells in enumerate(self._MARK_SPELLS, 1)
        )


class AberrantDragonmark(OriginFeat):
    """Unlike the house marks: a chosen Sorcerer cantrip and level 1 spell,
    Constitution as their spellcasting ability, a free cast regained on a
    Short or Long Rest, and no Spells of the Mark."""

    def __init__(
        self,
        cantrip: SorcererLevel0Spells | str,
        spell: SorcererLevel1Spells | str,
    ):
        cantrip = _resolve_spell_enum(cantrip, SorcererLevel0Spells)
        spell = _resolve_spell_enum(spell, SorcererLevel1Spells)
        if cantrip not in [s.value for s in SorcererLevel0Spells]:
            raise ValueError(
                f"Aberrant Dragonmark cantrip must be a Sorcerer cantrip. ({cantrip})"
            )
        if spell not in [s.value for s in SorcererLevel1Spells]:
            raise ValueError(
                f"Aberrant Dragonmark spell must be a level 1 Sorcerer spell. ({spell})"
            )
        self.cantrip = cantrip
        self.spell = spell
        super().__init__(
            name="Aberrant Dragonmark",
            origin="Dragonmark Feat",
            usage_tags=["buff", "heal", "damage"],
            activation=FeatureActivation(action_type=ActionType.REACTION),
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(self.cantrip, Ability.CONSTITUTION, source=SpellSource.CHOSEN),
            FeatureSpell(
                self.spell,
                Ability.CONSTITUTION,
                "Always prepared. Cast it once without a spell slot (regained on a Short or Long Rest), or with your spell slots.",
                source=SpellSource.CHOSEN,
            ),
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Aberrant Fortitude's use is in the panel below.
        return [
            Facts(
                (
                    (
                        "Aberrant Fortitude",
                        "Reaction when you fail a Constitution saving throw: add 1d4 to the save, possibly turning it into a success. Once per Long Rest.",
                    ),
                    (
                        "Aberrant Magic",
                        f"You know {self.cantrip} (Sorcerer cantrip). {self.spell} (level 1 Sorcerer spell) is always prepared; cast it once without a spell slot, regained on a Short or Long Rest, or with your spell slots.",
                    ),
                    ("Spellcasting Ability", "Constitution, for both spells"),
                )
            ),
            Option(
                "Aberrant Surge: when you cast the level 1 spell from this feat",
                (
                    Paragraph("You can expend one of your Hit Point Dice and roll it."),
                    Table(
                        ("Roll", "Effect"),
                        (
                            (
                                "Even",
                                "You gain Temporary Hit Points equal to the number rolled",
                            ),
                            (
                                "Odd",
                                "One creature within 30 feet of you (not you) takes Force damage equal to the number rolled; if no other creature is in range, you take it",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Aberrant Fortitude. When you fail a Constitution saving throw, you can take a Reaction to roll 1d4 and add the number rolled to the save, potentially turning the failure into a success. Once you've used this benefit, you can't use it again until you finish a Long Rest.\n"
            f"Aberrant Magic. You know one cantrip of your choice from the Sorcerer spell list ({self.cantrip}). Also, choose a level 1 spell from that spell list ({self.spell}). You always have that spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Short or Long Rest. You can also cast this spell using any spell slots you have. Constitution is your spellcasting ability for this spell.\n"
            "Aberrant Surge. When you cast the level 1 spell from this feat, you can expend one of your Hit Point Dice and roll it. If you roll an even number, you gain a number of Temporary Hit Points equal to the number rolled. If you roll an odd number, one creature within 30 feet of you (not including you) takes Force damage equal to the number rolled. If no other creatures are in range, you take the damage."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MarkOfDetection(_DragonmarkFeat):
    _NAME = "Mark of Detection"
    _INTUITION = (
        "Deductive Intuition",
        "Intelligence (Investigation) and Wisdom (Insight) checks",
    )
    _MAGIC = "Magical Detection"
    _SPELLS = (
        BardLevel1Spells.DETECT_MAGIC,
        DruidLevel1Spells.DETECT_POISON_AND_DISEASE,
    )
    _LEVEL_3_SPELLS = (SorcererLevel2Spells.SEE_INVISIBILITY,)
    _MARK_SPELLS = (
        "Detect Evil and Good, Identify",
        "Detect Thoughts, Find Traps",
        "Clairvoyance, Nondetection",
        "Arcane Eye, Divination",
        "Legend Lore",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Deductive Intuition. When you make an Intelligence (Investigation) or Wisdom (Insight) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Magical Detection. You always have the Detect Magic and Detect Poison and Disease spells prepared. You can cast each spell once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast these spells using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "When you reach character level 3, you also always have the See Invisibility spell prepared and can cast it the same way.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Detection Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfFinding(_DragonmarkFeat):
    _NAME = "Mark of Finding"
    _INTUITION = ("Hunter's Intuition", "Wisdom (Perception or Survival) checks")
    _MAGIC = "Finder's Magic"
    _SPELLS = (DivinationLevel1Spells.HUNTERS_MARK,)
    _LEVEL_3_SPELLS = (BardLevel2Spells.LOCATE_OBJECT,)
    _MARK_SPELLS = (
        "Faerie Fire, Longstrider",
        "Locate Animals or Plants, Mind Spike",
        "Clairvoyance, Speak with Plants",
        "Divination, Locate Creature",
        "Commune with Nature",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Hunter's Intuition. When you make a Wisdom (Perception or Survival) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Finder's Magic. You always have the Hunter's Mark spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "When you reach character level 3, you also always have the Locate Object spell prepared and can cast it the same way.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Finding Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfHandling(_DragonmarkFeat):
    _NAME = "Mark of Handling"
    _INTUITION = (
        "Wild Intuition",
        "Intelligence (Nature) and Wisdom (Animal Handling) checks",
    )
    _MAGIC = "Primal Connection"
    _SPELLS = (
        BardLevel1Spells.ANIMAL_FRIENDSHIP,
        BardLevel1Spells.SPEAK_WITH_ANIMALS,
    )
    _MARK_SPELLS = (
        "Command, Find Familiar",
        "Beast Sense, Calm Emotions",
        "Beacon of Hope, Conjure Animals",
        "Aura of Life, Dominate Beast",
        "Awaken",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def _extra_facts(self) -> tuple:
        return (
            (
                "Monstrous Connections",
                "From character level 3, Animal Friendship and Speak with Animals can also target a Monstrosity with an Intelligence of 3 or lower",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Wild Intuition. When you make an Intelligence (Nature) or Wisdom (Animal Handling) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Primal Connection. You always have the Animal Friendship and Speak with Animals spells prepared. You can cast each spell once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast these spells using any spell slots you have. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "Monstrous Connections. When you reach character level 3, you can target a Monstrosity when you cast Animal Friendship or Speak with Animals if the creature's Intelligence score is 3 or lower.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Handling Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfHealing(_DragonmarkFeat):
    _NAME = "Mark of Healing"
    _INTUITION = (
        "Medical Intuition",
        "Wisdom (Medicine) checks and ability checks using a Herbalism Kit",
    )
    _MAGIC = "Healing Touch"
    _SPELLS = (BardLevel1Spells.CURE_WOUNDS,)
    _LEVEL_3_SPELLS = (BardLevel2Spells.LESSER_RESTORATION,)
    _MARK_SPELLS = (
        "False Life, Healing Word",
        "Arcane Vigor, Prayer of Healing",
        "Aura of Vitality, Mass Healing Word",
        "Aura of Life, Aura of Purity",
        "Greater Restoration",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Medical Intuition. When you make a Wisdom (Medicine) check or an ability check using a Herbalism Kit, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Healing Touch. You always have the Cure Wounds spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "When you reach character level 3, you also always have the Lesser Restoration spell prepared and can cast it the same way.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Healing Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfHospitality(_DragonmarkFeat):
    _NAME = "Mark of Hospitality"
    _INTUITION = (
        "Ever Hospitable",
        "Charisma (Persuasion) checks and ability checks using Brewer's Supplies or Cook's Utensils",
    )
    _MAGIC = "Innkeeper's Magic"
    _SPELLS = (
        DruidLevel1Spells.PURIFY_FOOD_AND_DRINK,
        BardLevel1Spells.UNSEEN_SERVANT,
    )
    _LEVEL_3_SPELLS = (BardLevel2Spells.CALM_EMOTIONS,)
    _MARK_SPELLS = (
        "Goodberry, Sleep",
        "Aid, Enhance Ability",
        "Create Food and Water, Leomund's Tiny Hut",
        "Aura of Purity, Mordenkainen's Private Sanctum",
        "Hallow",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Ever Hospitable. When you make a Charisma (Persuasion) check or an ability check using Brewer's Supplies or Cook's Utensils, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Innkeeper's Magic. You always have the Purify Food and Drink and Unseen Servant spells prepared. You can cast each spell once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast these spells using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "When you reach character level 3, you also always have the Calm Emotions spell prepared and can cast it the same way.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Hospitality Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfMaking(_DragonmarkFeat):
    _NAME = "Mark of Making"
    _INTUITION = (
        "Artisan's Intuition",
        "Intelligence (Arcana) checks and ability checks using Artisan's Tools",
    )
    _MAGIC = "Spellsmith"
    _CANTRIPS = (SorcererLevel0Spells.MENDING,)
    _SPELLS = (SorcererLevel2Spells.MAGIC_WEAPON,)
    _MARK_SPELLS = (
        "Identify, Tenser's Floating Disk",
        "Continual Flame, Spiritual Weapon",
        "Conjure Barrage, Elemental Weapon",
        "Fabricate, Stone Shape",
        "Creation",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Artisan's Intuition. When you make an Intelligence (Arcana) check or an ability check using Artisan's Tools, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Spellsmith. You know the Mending cantrip. You also always have the Magic Weapon spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic class feature, the spells on the Mark of Making Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfPassage(_DragonmarkFeat):
    _NAME = "Mark of Passage"
    _INTUITION = (
        "Intuitive Motion",
        "Strength (Athletics) and Dexterity (Acrobatics) checks",
    )
    _MAGIC = "Magical Passage"
    _SPELLS = (SorcererLevel2Spells.MISTY_STEP,)
    _MARK_SPELLS = (
        "Expeditious Retreat, Jump",
        "Find Steed, Pass without Trace",
        "Blink, Phantom Steed",
        "Dimension Door, Freedom of Movement",
        "Teleportation Circle",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])
        self._speed = SpeedBonus(5)

    def apply(self, ledger_writer: LedgerWriter):
        self._speed.apply(ledger_writer)

    def _extra_facts(self) -> tuple:
        return (("Courier's Speed", "Your Speed increases by 5 feet"),)

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Courier's Speed. Your Speed increases by 5 feet.\n"
            "Intuitive Motion. When you make a Strength (Athletics) or Dexterity (Acrobatics) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Magical Passage. You always have the Misty Step spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Passage Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfScribing(_DragonmarkFeat):
    _NAME = "Mark of Scribing"
    _INTUITION = (
        "Gifted Scribe",
        "Intelligence (History) checks and ability checks using Calligrapher's Supplies",
    )
    _MAGIC = "Scribe's Insight"
    _CANTRIPS = (SorcererLevel0Spells.MESSAGE,)
    _SPELLS = (BardLevel1Spells.COMPREHEND_LANGUAGES,)
    _LEVEL_3_SPELLS = (BardLevel2Spells.MAGIC_MOUTH,)
    _MARK_SPELLS = (
        "Command, Illusory Script",
        "Animal Messenger, Silence",
        "Sending, Tongues",
        "Arcane Eye, Confusion",
        "Dream",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Gifted Scribe. When you make an Intelligence (History) check or an ability check using Calligrapher's Supplies, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Scribe's Insight. You know the Message cantrip. You also always have the Comprehend Languages spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "When you reach character level 3, you also always have the Magic Mouth spell prepared and can cast it the same way.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic class feature, the spells on the Mark of Scribing Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfSentinel(_DragonmarkFeat):
    _NAME = "Mark of Sentinel"
    _INTUITION = ("Sentinel's Intuition", "Wisdom (Insight or Perception) checks")
    _MAGIC = "Guardian's Shield"
    _SPELLS = (WizardLevel1Spells.SHIELD,)
    _MARK_SPELLS = (
        "Compelled Duel, Shield of Faith",
        "Warding Bond, Zone of Truth",
        "Counterspell, Protection from Energy",
        "Death Ward, Guardian of Faith",
        "Bigby's Hand",
    )
    _USES = _uses_per_proficiency_bonus("long rest")

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(
            character_level,
            spell_casting_ability,
            usage_tags=["buff"],
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
        )

    def _extra_facts(self) -> tuple:
        # Vigilant Guardian's uses are in the panel below.
        return (
            (
                "Vigilant Guardian",
                "Reaction when a creature you can see within 5 feet of you is hit by an attack roll: swap places with it, and you are hit by the attack instead. Proficiency Bonus times per Long Rest.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE
            + "Sentinel's Intuition. When you make a Wisdom (Insight or Perception) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Guardian's Shield. You always have the Shield spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "Vigilant Guardian. When a creature you can see within 5 feet of you is hit by an attack roll, you can take a Reaction to swap places with that creature, and you are hit by the attack instead. You can use this feature a number of times equal to your Proficiency Bonus and regain all expended uses when you finish a Long Rest.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic class feature, the spells on the Mark of Sentinel Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MarkOfShadow(_DragonmarkFeat):
    _NAME = "Mark of Shadow"
    _INTUITION = (
        "Cunning Intuition",
        "Dexterity (Stealth) and Charisma (Performance) checks",
    )
    _MAGIC = "Shape Shadows"
    _CANTRIPS = (SorcererLevel0Spells.MINOR_ILLUSION,)
    _SPELLS = (SorcererLevel2Spells.INVISIBILITY,)
    _MARK_SPELLS = (
        "Disguise Self, Silent Image",
        "Darkness, Pass without Trace",
        "Clairvoyance, Major Image",
        "Greater Invisibility, Hallucinatory Terrain",
        "Mislead",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Cunning Intuition. When you make a Dexterity (Stealth) or Charisma (Performance) check, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Shape Shadows. You know the Minor Illusion cantrip. You also always have the Invisibility spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Shadow Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfStorm(_DragonmarkFeat):
    _NAME = "Mark of Storm"
    _INTUITION = (
        "Windwright's Intuition",
        "Dexterity (Acrobatics) checks and ability checks using Navigator's Tools",
    )
    _MAGIC = "Storm Magic"
    _CANTRIPS = (SorcererLevel0Spells.THUNDERCLAP,)
    _LEVEL_3_SPELLS = (SorcererLevel2Spells.GUST_OF_WIND,)
    _MARK_SPELLS = (
        "Feather Fall, Fog Cloud",
        "Levitate, Shatter",
        "Sleet Storm, Wind Wall",
        "Conjure Minor Elementals, Control Water",
        "Conjure Elemental",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])
        self._resistance = DamageResistance(DamageType.LIGHTNING)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def _extra_facts(self) -> tuple:
        return (("Storm's Boon", "Resistance to Lightning damage"),)

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Windwright's Intuition. When you make a Dexterity (Acrobatics) check or an ability check using Navigator's Tools, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Storm's Boon. You have Resistance to Lightning damage.\n"
            "Storm Magic. You know the Thunderclap cantrip. When you reach character level 3, you also always have the Gust of Wind spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast it using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Storm Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


class MarkOfWarding(_DragonmarkFeat):
    _NAME = "Mark of Warding"
    _INTUITION = (
        "Warder's Intuition",
        "Intelligence (Investigation) checks and ability checks using Thieves' Tools",
    )
    _MAGIC = "Wards and Seals"
    _SPELLS = (WizardLevel1Spells.ALARM, WizardLevel1Spells.MAGE_ARMOR)
    _LEVEL_3_SPELLS = (WizardLevel2Spells.ARCANE_LOCK,)
    _MARK_SPELLS = (
        "Armor of Agathys, Sanctuary",
        "Knock, Nystul's Magic Aura",
        "Glyph of Warding, Magic Circle",
        "Leomund's Secret Chest, Mordenkainen's Faithful Hound",
        "Antilife Shell",
    )

    def __init__(self, character_level: int, spell_casting_ability: Ability):
        super().__init__(character_level, spell_casting_ability, usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return (
            _DRAGONMARK_PREREQUISITE + "You gain the following benefits.\n"
            "Warder's Intuition. When you make an Intelligence (Investigation) check or an ability check using Thieves' Tools, you can roll 1d4 and add the number rolled to the ability check.\n"
            "Wards and Seals. You always have the Alarm and Mage Armor spells prepared. You can cast each spell once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. You can also cast these spells using any spell slots you have of the appropriate level. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "When you reach character level 3, you also always have the Arcane Lock spell prepared and can cast it the same way.\n"
            "Spells of the Mark. If you have the Spellcasting or Pact Magic feature, the spells on the Mark of Warding Spells table are added to that feature's spell list.\n"
            + self._spells_of_the_mark_text()
        )


# ---------------------------------------------------------------------------
# Planar Pact Feats
# ---------------------------------------------------------------------------
# D&D Beyond Drops: Fey and Infernal Pact (May 2026), Shadow Pact (October
# 2026). Prerequisite: can't have another Planar Pact feat. Not enforced: no
# feat checks another feat as a prerequisite.

_PLANAR_PACT_ORIGIN = "Planar Pact Feat"
_PLANAR_PACT_PREREQUISITE = (
    "Planar Pact Feat (Prerequisite: Can't Have Another Planar Pact Feat)\n"
)


class FeyPact(OriginFeat):
    VALID_CANTRIPS = tuple(DivinationLevel0Spells) + tuple(EnchantmentLevel0Spells)
    # "One language of your choice from the language tables in the Player's
    # Handbook" - the secret languages aren't on them.
    VALID_LANGUAGES = tuple(
        language
        for language in Language
        if language not in (Language.DRUIDIC, Language.THIEVES_CANT)
    )

    def __init__(
        self,
        cantrip: DivinationLevel0Spells | EnchantmentLevel0Spells,
        spell_casting_ability: Ability,
        language: Language = Language.SYLVAN,
    ):
        if cantrip not in self.VALID_CANTRIPS:
            raise ValueError(
                f"Fey Pact cantrip must be a Divination or Enchantment cantrip. ({cantrip})"
            )
        if spell_casting_ability not in _MENTAL_ABILITIES:
            raise ValueError(
                "Fey Pact spellcasting ability must be Intelligence, Wisdom, or Charisma."
            )
        if language not in self.VALID_LANGUAGES:
            raise ValueError(
                f"Fey Pact language must be Sylvan or one from the Player's Handbook language tables. ({language})"
            )
        self.cantrip = cantrip
        self.spell_casting_ability = spell_casting_ability
        self.language = language
        self._language = GrantLanguage(language)
        self._nature = SkillProficiency([Skill.NATURE])
        super().__init__(
            name="Fey Pact",
            origin=_PLANAR_PACT_ORIGIN,
            usage_tags=["buff"],
            # Honeyed Words, once it turns a failure into a success.
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._language.apply(ledger_writer)
        self._nature.apply(ledger_writer)

    def granted_spells(self) -> list[FeatureSpell]:
        return [
            FeatureSpell(DruidLevel0Spells.DRUIDCRAFT, self.spell_casting_ability),
            FeatureSpell(
                self.cantrip, self.spell_casting_ability, source=SpellSource.CHOSEN
            ),
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        language = (
            "Sylvan"
            if self.language == Language.SYLVAN
            else f"{self.language.value} (you already knew Sylvan)"
        )
        return [
            Facts(
                (
                    ("Fey Bond", f"You know {language}; proficiency in Nature"),
                    (
                        "Fey Cantrips",
                        f"Druidcraft and {self.cantrip}; {self.spell_casting_ability.value} is their spellcasting ability",
                    ),
                    (
                        "Honeyed Words",
                        "When you fail a Charisma (Deception or Persuasion) check, reroll it and use the new roll. Once the reroll turns a failure into a success, you can't use this again until you finish a Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            _PLANAR_PACT_PREREQUISITE + "You gain the following benefits.\n"
            "Fey Bond. You know Sylvan. If you already know Sylvan when you select this feat, you instead learn one language of your choice from the language tables in the Player's Handbook. You also gain Proficiency in the Nature skill.\n"
            "Fey Cantrips. You know the Druidcraft cantrip and learn one other cantrip of your choice from the Divination or Enchantment school of magic. Intelligence, Wisdom, or Charisma is your spellcasting ability for these spells (choose when you select this feat).\n"
            "Honeyed Words. When you fail a Charisma (Deception or Persuasion) check, you can reroll the check, and you must use the new roll. Once this benefit turns a failure into a success, you can't use it again until you finish a Long Rest.\n"
            f"Choices: {self.language.value}, {self.cantrip}, {self.spell_casting_ability.value}"
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class InfernalPact(OriginFeat):
    VALID_DAMAGE_TYPES = (DamageType.FIRE, DamageType.POISON)

    def __init__(self, damage_type: DamageType):
        if damage_type not in self.VALID_DAMAGE_TYPES:
            raise ValueError("Infernal Pact resistance must be Fire or Poison.")
        self.damage_type = damage_type
        self._resistance = DamageResistance(damage_type)
        # "Unimpeded by magical Darkness" is on the card only: a sense has a
        # range and nothing else.
        self._darkvision = GrantSense(Sense.DARKVISION, 30)
        self._deception = SkillProficiency([Skill.DECEPTION])
        super().__init__(
            name="Infernal Pact",
            origin=_PLANAR_PACT_ORIGIN,
            passive=True,
            usage_tags=["buff"],
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)
        self._darkvision.apply(ledger_writer)
        self._deception.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Infernal Resistance",
                        f"Resistance to {self.damage_type.value} damage",
                    ),
                    (
                        "Infernal Sight",
                        "Darkvision 30 feet, unimpeded by magical Darkness",
                    ),
                    ("Silver-Tongued", "Proficiency in Deception"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            _PLANAR_PACT_PREREQUISITE + "You gain the following benefits.\n"
            f"Infernal Resistance. You have Resistance to Fire damage or Poison damage. (Chosen: {self.damage_type.value})\n"
            "Infernal Sight. You gain Darkvision with a range of 30 feet. This Darkvision is unimpeded by magical Darkness.\n"
            "Silver-Tongued. You gain proficiency in the Deception skill."
        )


class ShadowPact(OriginFeat):
    def __init__(self):
        # "Darkvision 60 feet, or +30 feet if you already have it": the ledger
        # can only extend a sense by the range it grants, so this records the
        # plain 60 feet and the card states the +30.
        self._darkvision = GrantSense(Sense.DARKVISION, 60)
        super().__init__(
            name="Shadow Pact",
            origin=_PLANAR_PACT_ORIGIN,
            usage_tags=["heal"],
            # Shroud of Shadows.
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute",
                range="5-Foot Emanation",
            ),
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._darkvision.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Darkvision",
                        "60 feet; if you already have Darkvision, its range increases by 30 feet instead (add it by hand)",
                    ),
                    (
                        "Shadow Blood",
                        "While entirely within Dim Light or Darkness, reroll a 1 on a die that sets how many Hit Points you regain, and use the new roll",
                    ),
                )
            ),
            Option(
                "Shroud of Shadows",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            ("Effect", "A 5-foot Emanation of Dim Light around you"),
                            ("Duration", "1 minute"),
                            (
                                "Ends early",
                                "You dismiss it (no action required) or have the Incapacitated condition",
                            ),
                            ("Recharge", "When you finish a Short or Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            _PLANAR_PACT_PREREQUISITE + "You gain the following benefits.\n"
            "Darkvision. You gain Darkvision with a range of 60 feet. If you already have Darkvision, its range increases by 30 feet.\n"
            "Shadow Blood. Whenever you roll a die to determine the number of Hit Points you regain, you can reroll the die if it rolls a 1 while you're entirely within Dim Light or Darkness, and you must use the new roll.\n"
            "Shroud of Shadows. You can take a Bonus Action to radiate a 5-foot Emanation of Dim Light around you for 1 minute. It ends early if you dismiss it (no action required) or you have the Incapacitated condition. Once you use this benefit, you can't use it again until you finish a Short or Long Rest."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
