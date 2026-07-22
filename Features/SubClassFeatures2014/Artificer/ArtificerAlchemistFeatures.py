from Core.Definitions import ARTIFICER_HIT_DIE, Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class AlchemistToolsOfTheTrade(Feature):
    def __init__(self):
        super().__init__(name="Tool Proficiency", origin="Alchemist Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with alchemist's supplies. If you already have this proficiency, you gain proficiency with one other type of artisan's tools of your choice."
        return description


class AlchemistSpells(Feature):
    def __init__(self):
        super().__init__(name="Alchemist Spells", origin="Alchemist Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 3rd level, you always have certain spells prepared after you reach particular levels in this class, as shown in the Alchemist Spells table. These spells count as artificer spells for you, but they don't count against the number of artificer spells you prepare.\n"
            "Alchemist Spells\n"
            "Artificer Level	Alchemist Spells\n"
            "3rd	Healing Word, Ray of Sickness\n"
            "5th	Flaming Sphere, Melf's Acid Arrow\n"
            "9th	Gaseous Form, Mass Healing Word\n"
            "13th	Blight, Death Ward\n"
            "17th	Cloudkill, Raise Dead"
        )
        return description


class ExperimentalElixir(Feature):
    def __init__(self):
        super().__init__(name="Experimental Elixir", origin="Alchemist Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 3rd level, whenever you finish a long rest, you can magically produce an experimental elixir in an empty flask you touch. Roll on the Experimental Elixir table for the elixir's effect, which is triggered when someone drinks the elixir. As an action, a creature can drink the elixir or administer it to an incapacitated creature.\n"
            "You can create additional experimental elixirs by expending a spell slot of 1st level or higher for each one. When you do so, you use your action to create the elixir in an empty flask you touch, and you choose the elixir's effect from the Experimental Elixir table.\n"
            "Creating an experimental elixir requires you to have alchemist's supplies on your person, and any elixir you create with this feature lasts until it is drunk or until the end of your next long rest.\n"
            "When you reach certain levels in this class, you can make more elixirs at the end of a long rest: two at 6th level and three at 15th level. Roll for each elixir's effect separately. Each elixir requires its own flask.\n"
            "Experimental Elixir\n"
            "D6	Effect\n"
            "1	Healing. The drinker regains a number of hit points equal to 2d4 + your Intelligence modifier.\n"
            "2	Swiftness. The drinker's walking speed increases by 10 feet for 1 hour.\n"
            "3	Resilience. The drinker gains a +1 bonus to AC for 10 minutes.\n"
            "4	Boldness. The drinker can roll a d4 and add the number rolled to every attack roll and saving throw they make for the next minute.\n"
            "5	Flight. The drinker gains a flying speed of 10 feet for 10 minutes.\n"
            "6	Transformation. The drinker's body is transformed as if by the Alter Self spell. The drinker determines the transformation caused by the spell, the effects of which last for 10 minutes."
        )
        return description


class AlchemicalSavant(Feature):
    def __init__(self):
        super().__init__(name="Alchemical Savant", origin="Alchemist Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 5th level, you've developed masterful command of magical chemicals, enhancing the healing and damage you create through them. Whenever you cast a spell using your alchemist's supplies as the spellcasting focus, you gain a bonus to one roll of the spell. That roll must restore hit points or be a damage roll that deals acid, fire, necrotic, or poison damage, and the bonus equals your Intelligence modifier (minimum of +1)."
        return description


class RestorativeReagents(Feature):
    def __init__(self):
        super().__init__(name="Restorative Reagents", origin="Alchemist Artificer Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, intelligence_modifier)
        description = (
            "Starting at 9th level, you can incorporate restorative reagents into some of your works.\n"
            "Whenever a creature drinks an experimental elixir you created, the creature gains temporary hit points equal to 2d6 + your Intelligence modifier (minimum of 1 temporary hit point).\n"
            "You can cast Lesser Restoration without expending a spell slot and without preparing the spell, provided you use alchemist's supplies as the spellcasting focus. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class ChemicalMastery(Feature):
    def __init__(self):
        super().__init__(name="Chemical Mastery", origin="Alchemist Artificer Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "By 15th level, you have been exposed to so many chemicals that they pose little risk to you, and you can use them to quickly end certain ailments.\n"
            "You gain resistance to acid damage and poison damage, and you are now immune to the poisoned condition.\n"
            "You can cast Greater Restoration and Heal without expending a spell slot, without preparing the spell, and without providing the material component, provided you use alchemist's supplies as the spellcasting focus. Once you cast either spell with this feature, you can't cast that spell with it again until you finish a long rest."
        )
        return description
