from Definitions import Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class OriginCharacterFeat(CharacterFeature):
    pass


class OriginTextFeat(TextFeature):
    pass


OriginFeat = OriginCharacterFeat | OriginTextFeat


class Skilled(OriginCharacterFeat):
    """Also add proficiency in any combination of three skills or tools of your choice."""

    def __init__(self, skills: list[Skill]):
        self.skills = skills
        assert len(self.skills) == 3, "Must choose exactly three skills or tools."

    def validate(self, character_stat_block: CharacterStatBlock) -> None:
        if any(
            character_stat_block.skills.is_proficient(skill) for skill in self.skills
        ):
            raise ValueError(
                "Character already has proficiency with the following selected skills: "
                + ", ".join(
                    skill.name
                    for skill in self.skills
                    if character_stat_block.skills.is_proficient(skill)
                )
            )

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        for skill in self.skills:
            character_stat_block.skills.add_skill_proficiency(skill)


class Alert(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Alert", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Initiative Proficiency. When you roll Initiative, you can add your Proficiency Bonus to the roll.\n"
            "Initiative Swap. Immediately after you roll Initiative, you can swap your Initiative with the Initiative of one willing ally in the same combat. You can't make this swap if you or the ally has the Incapacitated condition.\n"
        )


class Crater(OriginTextFeat):
    def __init__(self, artisans_tools: list[str]):
        self.artisans_tools = artisans_tools
        super().__init__(name="Alert", origin="Origin Feat")

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

        return "\n".join(f" * {tool_map[t]}" for t in self.artisans_tools)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Tool Proficiency. You gain proficiency with three different Artisan's Tools of your choice from the Fast Crafting table.\n"
            "Discount. Whenever you buy a nonmagical item, you receive a 20 percent discount on it.\n"
            "Fast Crafting:\n"
            "When you finish a Long Rest, you can craft one piece of gear from the Fast Crafting table,\n"
            "provided you have the Artisan's Tools associated with that item and have proficiency with those tools. \n"
            "The item lasts until you finish another Long Rest, at which point the item falls apart.\n"
            f"{self.get_tool_choices()}"
        )


class Healer(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Healer", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Battle Medic:\n"
            "  If you have a Healer's Kit, you can expend one use of it and tend to a creature within 5 feet of yourself as a Utilize action.\n"
            "  That creature can expend one of its Hit Point Dice, and you then roll that die. The creature regains a number of Hit Points equal to the roll plus your Proficiency Bonus.\n"
            "Healing Rerolls.\n"
            "  Whenever you roll a die to determine the number of Hit Points you restore with a spell or with this feat's Battle Medic benefit,\n"
            "  you can reroll the die if it rolls a 1, and you must use the new roll.\n"
        )


class Lucky(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Lucky", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Luck Points. You have a number of Luck Points equal to your Proficiency Bonus and can spend the points on the benefits below. You regain your expended Luck Points when you finish a Long Rest.\n"
            "Advantage. When you roll a d20 for a D20 Test, you can spend 1 Luck Point to give yourself Advantage on the roll.\n"
            "Disadvantage. When a creature rolls a d20 for an attack roll against you, you can spend 1 Luck Point to impose Disadvantage on that roll.\n"
        )


class MagicInitiate(OriginTextFeat):
    def __init__(self, spell_list: str):
        self.spell_list = spell_list
        super().__init__(name="Magic Initiate", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            f"Spell List: {self.spell_list}\n"
            "Two Cantrips. You learn two cantrips of your choice from the Cleric, Druid, or Wizard spell list.\n"
            "Intelligence, Wisdom, or Charisma is your spellcasting ability for this feat's spells (choose when you select this feat).\n"
            "\n"
            "Level 1 Spell. Choose a level 1 spell from the same list you selected for this feat's cantrips. You always have that spell prepared.\n"
            "You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest.\n"
            "You can also cast the spell using any spell slots you have.\n"
            "\n"
            "Spell Change. Whenever you gain a new level, you can replace one of the spells you chose for this feat with a different spell of the same level from the chosen spell list.\n\n"
            "Repeatable. You can take this feat more than once, but you must choose a different spell list each time."
        )


class Musician(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Musician", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Instrument Training: You gain proficiency with three Musical Instruments of your choice.\n"
            "\n"
            "Encouraging Song: As you finish a Short or Long Rest, you can play a song on a Musical Instrument with which you have proficiency and give Heroic Inspiration to allies who hear the song. The number of allies you can affect in this way equals your Proficiency Bonus.\n"
        )


class SavageAttacker(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Savage Attacker", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You've trained to deal particularly damaging strikes.\n"
            "Once per turn when you hit a target with a weapon, you can roll the weapon's damage dice twice and use either roll against the target.\n"
        )


class TavernBrawler(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Tavern Brawler", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Enhanced Unarmed Strike. When you hit with your Unarmed Strike and deal damage, you can deal Bludgeoning damage equal to 1d4 plus your Strength modifier instead of the normal damage of an Unarmed Strike.\n"
            "\n"
            "Damage Rerolls. Whenever you roll a damage die for your Unarmed Strike, you can reroll the die if it rolls a 1, and you must use the new roll.\n"
            "\n"
            "Improvised Weaponry. You have proficiency with improvised weapons.\n"
            "\n"
            "Push. When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can deal damage to the target and also push it 5 feet away from you. You can use this benefit only once per turn.\n"
        )


class Tough(OriginCharacterFeat):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_level = character_stat_block.character_level
        character_stat_block.combat.hit_points_bonus += 2 * character_level


class CultOfTheDragonInitiate(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Cult of the Dragon Initiate", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Dragon’s Tongue. You know Draconic. If you already know Draconic when you select this feat, you instead learn one language of your choice from the language tables in the Player’s Handbook or chapter 2 of this book.\n"
            "Dragon’s Terror. You can take a Magic action to instill terror in a creature you can see within 30 feet of yourself. The target must succeed on a Wisdom saving throw (DC 8 plus your Wisdom modifier and Proficiency Bonus) or have the Frightened condition until the end of your next turn. If the target succeeds on the save or when the effect ends for a target, the target is immune to this effect for 24 hours.\n"
            "Inspired by Fear. When you cause a creature to have the Frightened condition and you are the source of its fear, you can gain Heroic Inspiration if you lack it. Once you use this benefit, you can’t use it again until you finish a Short or Long Rest.\n"
        )


class EmeraldEnclaveFledgling(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Emerald Enclave Fledgling", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Speak with Animals. You always have the Speak with Animals spell prepared and can cast it with any spell slots you have. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat). When you cast this spell as a Ritual, its duration is 8 hours.\n"
            "\n"
            "Tag Team. When you take the Help action, you can switch places with a willing ally within 5 feet of yourself as part of that same action. This movement doesn’t provoke Opportunity Attacks. You can’t use this benefit if the ally has the Incapacitated condition.\n"
        )


class HarperAgent(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Harper Agent", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Thieves’ Cant. You know Thieves’ Cant.\n"
            "Instrument Training. You gain proficiency with a Musical Instrument of your choice.\n"
            "Distracting Melody. When you take the Help action to assist an ally’s attack roll, the enemy you’re distracting can be within 30 feet of you, rather than within 5 feet of you, provided the enemy can see or hear you.        )\n"
        )


class LordsAllianceAgent(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Lords' Alliance Agent", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Inspiring Strike. Once per turn when you score a Critical Hit against a creature, you can choose an ally within 30 feet of yourself who can see or hear you and who lacks Heroic Inspiration. That ally gains Heroic Inspiration.\n"
            "Reassert Honor. When an enemy you can see deals damage to an ally of yours that is within 5 feet of you, you have Advantage on your next attack roll against that enemy before the end of your next turn.\n"
        )


class PurpleDragonRook(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Lords' Alliance Agent", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Entreat. You gain proficiency in one of the following skills: Insight, Performance, or Persuasion.\n"
            "Rallying Cry. When you roll Initiative and don’t have the Incapacitated condition, you can choose a number of creatures equal to your Proficiency Bonus that you can see within 30 feet of yourself. Those creatures gain Heroic Inspiration.\n"
            "Once you use this benefit, you can’t do so again until you finish a Long Rest.\n"
        )


class SpellfireSpark(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Lords' Alliance Agent", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Magic Absorption. Once per turn, when you take damage from a spell or magical effect, you reduce the total damage taken by 1d4. You can’t use this benefit if you have the Incapacitated condition.\n"
            "\n"
            "Spellfire Flame. You learn the Sacred Flame cantrip. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat). You can also cast this cantrip as a Bonus Action a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
        )


class TyroOfThaGauntlet(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Lords' Alliance Agent", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Stand as One. When an ally within 5 feet of you is subjected to an effect that would push or pull it, you can take a Reaction to prevent that ally from being pushed or pulled. To receive this benefit, the ally can’t have the Incapacitated condition.\n"
            "Vigilant. When you take the Ready action, the next attack roll made against you has Disadvantage before the start of your next turn.\n"
        )


class ZhentarimRuffian(OriginTextFeat):
    def __init__(self):
        super().__init__(name="Lords' Alliance Agent", origin="Origin Feat")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Exploit Opening. When you roll damage for an Opportunity Attack, you can roll the damage dice twice and use either roll against the target.\n"
            "Family First. If you have Heroic Inspiration when you roll Initiative, you can expend it to give yourself and your allies Advantage on that Initiative roll.        \n"
        )
