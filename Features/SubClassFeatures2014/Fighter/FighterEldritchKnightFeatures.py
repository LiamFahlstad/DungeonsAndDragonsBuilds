from Core.Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class EldritchKnightSpellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Eldritch Knight Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        spell_save_dc = 8 + proficiency_bonus + intelligence_modifier
        spell_attack_modifier = proficiency_bonus + intelligence_modifier

        description = (
            "When you reach 3rd level, you augment your martial prowess with the ability to cast spells.\n"
            "\n"
            "Eldritch Knight Spellcasting\n"
            "Fighter Level\tCantrips Known\tSpells Known\t1st\t2nd\t3rd\t4th\n"
            "3rd\t2\t3\t2\t-\t-\t-\n"
            "4th\t2\t4\t3\t-\t-\t-\n"
            "5th\t2\t4\t3\t-\t-\t-\n"
            "6th\t2\t4\t3\t-\t-\t-\n"
            "7th\t2\t5\t4\t2\t-\t-\n"
            "8th\t2\t6\t4\t2\t-\t-\n"
            "9th\t2\t6\t4\t2\t-\t-\n"
            "10th\t3\t7\t4\t3\t-\t-\n"
            "11th\t3\t8\t4\t3\t-\t-\n"
            "12th\t3\t8\t4\t3\t-\t-\n"
            "13th\t3\t9\t4\t3\t2\t-\n"
            "14th\t3\t10\t4\t3\t2\t-\n"
            "15th\t3\t10\t4\t3\t2\t-\n"
            "16th\t3\t11\t4\t3\t3\t-\n"
            "17th\t3\t11\t4\t3\t3\t-\n"
            "18th\t3\t11\t4\t3\t3\t-\n"
            "19th\t3\t12\t4\t3\t3\t1\n"
            "20th\t3\t13\t4\t3\t3\t1\n"
            "\n"
            "Cantrips. You learn two cantrips of your choice from the wizard spell list. You learn an additional wizard cantrip of your choice at 10th level.\n"
            "\n"
            "Spell Slots. The Eldritch Knight Spellcasting table shows how many spell slots you have to cast your wizard spells of 1st level and higher. To cast one of these spells, you must expend a slot of the spell's level or higher. You regain all expended spell slots when you finish a long rest.\n"
            "\n"
            "For example, if you know the 1st-level spell Shield and have a 1st-level and a 2nd-level spell slot available, you can cast Shield using either slot.\n"
            "\n"
            "Spells Known of 1st Level and Higher. You know three 1st-level wizard spells of your choice, two of which you must choose from the abjuration and evocation spells on the wizard spell list.\n"
            "\n"
            "The Spells Known column of the Eldritch Knight Spellcasting table shows when you learn more wizard spells of 1st level or higher. Each of these spells must be an abjuration or evocation spell of your choice, and must be of a level for which you have spell slots. For instance, when you reach 7th level in this class, you can learn one new spell of 1st or 2nd level.\n"
            "\n"
            "The spells you learn at 8th, 14th, and 20th level can come from any school of magic.\n"
            "\n"
            "Whenever you gain a level in this class, you can replace one of the wizard spells you know with another spell of your choice from the wizard spell list. The new spell must be of a level for which you have spell slots, and it must be an abjuration or evocation spell, unless you're replacing the spell you gained at 3rd, 8th, 14th, or 20th level from any school of magic.\n"
            "\n"
            f"Spellcasting Ability. Intelligence is your spellcasting ability for your wizard spells, since you learn your spells through study and memorization. You use your Intelligence whenever a spell refers to your spellcasting ability. In addition, you use your Intelligence modifier when setting the saving throw DC for a wizard spell you cast and when making an attack roll with one.\n"
            f"Spell save DC = 8 + your proficiency bonus + your Intelligence modifier = {spell_save_dc}\n"
            f"Spell attack modifier = your proficiency bonus + your Intelligence modifier = {spell_attack_modifier}"
        )
        return description


class WeaponBond(Feature):
    def __init__(self):
        super().__init__(name="Weapon Bond", origin="Eldritch Knight Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you learn a ritual that creates a magical bond between yourself and one weapon. You perform the ritual over the course of 1 hour, which can be done during a short rest. The weapon must be within your reach throughout the ritual, at the conclusion of which you touch the weapon and forge the bond.\n"
            "\n"
            "Once you have bonded a weapon to yourself, you can't be disarmed of that weapon unless you are incapacitated. If it is on the same plane of existence, you can summon that weapon as a bonus action on your turn, causing it to teleport instantly to your hand.\n"
            "\n"
            "You can have up to two bonded weapons, but can summon only one at a time with your bonus action. If you attempt to bond with a third weapon, you must break the bond with one of the other two."
        )
        return description


class WarMagic(Feature):
    def __init__(self):
        super().__init__(name="War Magic", origin="Eldritch Knight Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Beginning at 7th level, when you use your action to cast a cantrip, you can make one weapon attack as a bonus action."
        return description


class EldritchStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Eldritch Strike", origin="Eldritch Knight Fighter Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 10th level, you learn how to make your weapon strikes undercut a creature's resistance to your spells. When you hit a creature with a weapon attack, that creature has disadvantage on the next saving throw it makes against a spell you cast before the end of your next turn."
        return description


class ArcaneCharge(Feature):
    def __init__(self):
        super().__init__(
            name="Arcane Charge", origin="Eldritch Knight Fighter Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 15th level, you gain the ability to teleport up to 30 feet to an unoccupied space you can see when you use your Action Surge. You can teleport before or after the additional action."
        return description


class ImprovedWarMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Improved War Magic", origin="Eldritch Knight Fighter Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 18th level, when you use your action to cast a spell, you can make one weapon attack as a bonus action."
        return description
