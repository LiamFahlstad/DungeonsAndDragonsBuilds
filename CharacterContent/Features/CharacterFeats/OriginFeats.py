from typing import Optional

from Model.Content.Feature import (
    Feature,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    regained_on_from_uses,
)
from Model.Content.Improvements import (
    DamageResistance,
    GrantLanguage,
    HitPointsPerLevelBonus,
    InitiativeProficiency,
    SkillProficiencyChoice,
    SpeedBonus,
)
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    ClericLevel0Spells,
    ClericLevel1Spells,
    ConjurationLevel1Spells,
    DruidLevel0Spells,
    DruidLevel1Spells,
    EvocationLevel0Spells,
    NecromancyLevel0Spells,
    WarlockLevel1Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from Core.Definitions import Ability, CharacterClass, DamageType, Language, Skill
from Model.Grants import Grants
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import PROFICIENCY_BONUS_GAINED_AT, MAX_PROFICIENCY_BONUS
from Model.View import CharacterView
from Model.CharacterSources import SpellSource


class OriginFeat(Feature):
    # A feat can be taken once, unless it says it's Repeatable (see
    # Character._validate_feats_taken_once).
    repeatable = False

    def get_spell_casting_ability(self) -> Optional[Ability]:
        return None

    def get_spells(self) -> list[str]:
        return []

    def get_spell_source(self) -> Optional[str]:
        """The sheet label for get_spells(): SpellSource.CHOSEN when the
        player picks them, None when the feat names them."""
        return None

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return regained_on_from_uses(self.uses)

    def grant_to(self, data: Grants) -> None:
        """Grant this feat and the spells it comes with (listed under the
        feat)."""
        feat = data.for_origin_feat(self)
        feat.add_feature(self)
        for spell in self.get_spells():
            feat.add_spell(
                spell, self.get_spell_casting_ability(), source=self.get_spell_source()
            )


class Skilled(OriginFeat):
    """Also add proficiency in any combination of three skills or tools of your choice."""

    # 2024 PHB: Repeatable.
    repeatable = True

    def __init__(self, skills: list[Skill]):
        self._choice = SkillProficiencyChoice(
            skills, list(Skill), count=3, error_prefix="Skilled"
        )
        super().__init__(
            name="Skilled", origin="Origin Feat", skippable_in_concise=True
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._choice.apply(ledger_writer)

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

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Luck Points. You have a number of Luck Points equal to your Proficiency Bonus and can spend the points on the benefits below. You regain your expended Luck Points when you finish a Long Rest.\n"
            "Advantage. When you roll a d20 for a D20 Test, you can spend 1 Luck Point to give yourself Advantage on the roll.\n"
            "Disadvantage. When a creature rolls a d20 for an attack roll against you, you can spend 1 Luck Point to impose Disadvantage on that roll."
        )
        return description

    def get_concise_description(self, character: CharacterView) -> str:
        description = (
            "You have a number of Luck Points equal to your Proficiency Bonus and regain them when you finish a Long Rest. "
            "Spend 1 Luck Point to give yourself Advantage on a d20 roll, or spend 1 Luck Point to impose Disadvantage on an attack roll against you."
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

    def get_spells(self) -> list[str]:
        return [self.cantrip_1, self.cantrip_2, self.spell]

    def get_spell_source(self) -> Optional[str]:
        return SpellSource.CHOSEN

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability

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
        super().__init__(name="Tough", origin="Origin Feat", skippable_in_concise=True)

    def apply(self, ledger_writer: LedgerWriter):
        self._hp.apply(ledger_writer)

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

    def get_spells(self) -> list[str]:
        return [DruidLevel1Spells.SPEAK_WITH_ANIMALS]

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability

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

    def get_spells(self) -> list[str]:
        return [ConjurationLevel1Spells.FIND_FAMILIAR]

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability

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

    def get_description(self, character: CharacterView) -> str:
        return (
            "You gain the following benefits.\n"
            "Stand as One. When an ally within 5 feet of you is subjected to an effect that would push or pull it, you can take a Reaction to prevent that ally from being pushed or pulled. To receive this benefit, the ally can’t have the Incapacitated condition.\n"
            "Vigilant. When you take the Ready action, the next attack roll made against you has Disadvantage before the start of your next turn.\n"
        )


class ZhentarimRuffian(OriginFeat):
    def __init__(self):
        super().__init__(name="Zhentarim Ruffian", origin="Origin Feat")

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

    def get_spells(self) -> list[str]:
        return [self._SPELL]

    def get_spell_casting_ability(self) -> Ability:
        return self.spell_casting_ability


class ArcaneArtist(_SpellcastingOriginFeat):
    _NAME = "Arcane Artist"
    _SPELL = BardLevel0Spells.MINOR_ILLUSION
    _USES = FeatureUses(max_uses=1, regain_all_on="long rest")

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

    def get_spells(self) -> list[str]:
        return [self.necromancy_cantrip]

    def get_spell_source(self) -> Optional[str]:
        return SpellSource.CHOSEN

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
