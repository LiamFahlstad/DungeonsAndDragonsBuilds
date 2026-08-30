from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Core.Definitions import MAX_PROFICIENCY_BONUS


class LunarEmbodiment(Feature):
    def __init__(self):
        super().__init__(name="Lunar Embodiment", origin="Lunar Sorcery Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn additional spells when you reach certain levels in this class, as shown on the Lunar Spells table. Each of these spells counts as a sorcerer spell for you, but it doesn't count against the number of sorcerer spells you know.\n"
            "\n"
            "Lunar Spells\n"
            "Sorcerer Level\tFull Moon Spells\tNew Moon Spells\tCrescent Moon Spells\n"
            "1st\tShield\tRay of Sickness\tColor Spray\n"
            "3rd\tLesser Restoration\tBlindness/Deafness\tAlter Self\n"
            "5th\tDispel Magic\tVampiric Touch\tPhantom Steed\n"
            "7th\tDeath Ward\tConfusion\tHallucinatory Terrain\n"
            "9th\tRary's Telepathic Bond\tHold Monster\tMislead\n"
            "\n"
            "Whenever you finish a long rest, you can choose what lunar phase manifests its power through your magic: Full Moon, New Moon, or Crescent Moon. While in the chosen phase, you can cast one 1st-level spell of the associated phase in the Lunar Spells table once without expending a spell slot. Once you cast a spell in this way, you can't do so again until you finish a long rest.\n"
            "\n"
            "You gained the following spells known at 1st and 3rd level: Shield, Ray of Sickness, Color Spray, Lesser Restoration, Blindness/Deafness, and Alter Self."
        )
        return description


class MoonFire(Feature):
    def __init__(self):
        super().__init__(name="Moon Fire", origin="Lunar Sorcery Sorcerer Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can call down the radiant light of the moon on command. You learn the Sacred Flame spell, which doesn't count against the number of sorcerer cantrips you know. When you cast the spell, you can target one creature as normal or target two creatures within range that are within 5 feet of each other."
        )
        return description


class LunarBoons(Feature):
    def __init__(self):
        super().__init__(name="Lunar Boons", origin="Lunar Sorcery Sorcerer Level 6", usage_tags=["buff"], uses=FeatureUses(max_uses=MAX_PROFICIENCY_BONUS, regain_all_on="long rest", current_formula="Current amount: equal to your proficiency bonus."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The current phase of your Lunar Embodiment can affect your Metamagic feature. Each Lunar Embodiment phase is associated with certain schools of magic, as shown here:\n"
            "\n"
            "    * Full Moon. Abjuration and Divination spells\n"
            "    * New Moon. Enchantment and Necromancy spells\n"
            "    * Crescent Moon. Illusion and Transmutation spells\n"
            "\n"
            "Whenever you use Metamagic on a spell of a school of magic associated with your current Lunar Embodiment phase, you can reduce the sorcery points spent by 1 (minimum 0). You can reduce the sorcery points spent for your Metamagic a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return character_stat_block.get_proficiency_bonus()


class WaxingAndWaning(Feature):
    def __init__(self):
        super().__init__(name="Waxing and Waning", origin="Lunar Sorcery Sorcerer Level 6", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION), usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain greater control over the phases of your lunar magic. As a bonus action, you can spend 1 sorcery point to change your current Lunar Embodiment phase for a different one.\n"
            "\n"
            "You can now cast one 1st-level spell from each lunar phase of the Lunar Spells table once without expending a spell slot, provided your current phase is the same as the lunar phase spell. Once you cast a lunar phase spell in this way, you can't do so again until you finish a long rest."
        )
        return description


class LunarEmpowerment(Feature):
    def __init__(self):
        super().__init__(name="Lunar Empowerment", origin="Lunar Sorcery Sorcerer Level 14", usage_tags=["utility", "buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The power of a lunar phase saturates your being. While you are in a Lunar Embodiment phase, you also gain the following benefit associated with that phase:\n"
            "\n"
            "    * Full Moon: You can use a bonus action to shed bright light in a 10-foot radius and dim light for an additional 10 feet or to douse the light. In addition, you and creatures of your choice have advantage on Intelligence (Investigation) and Wisdom (Perception) checks while within the bright light you shed.\n"
            "    * New Moon: You have advantage on Dexterity (Stealth) checks. In addition, while you are entirely in darkness, attack rolls have disadvantage against you.\n"
            "    * Crescent Moon: You have resistance to necrotic and radiant damage."
        )
        return description


class LunarPhenomenon(Feature):
    def __init__(self):
        super().__init__(name="Lunar Phenomenon", origin="Lunar Sorcery Sorcerer Level 18", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="Until End of Next Turn", range="60 Feet"), usage_tags=["utility", "damage", "control", "heal", "buff"], uses=FeatureUses(max_uses=1, regain_all_on="long rest"))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a bonus action, you can tap into a special power of your current Lunar Embodiment phase. Alternatively, as part of the bonus action you take to change your lunar phase using the Waxing and Waning feature, you can immediately use the power of the lunar phase you are entering:\n"
            "\n"
            "    * Full Moon: You radiate moonlight for a moment. Each creature of your choice within 30 feet of you must succeed on a Constitution saving throw against your spell save DC or be blinded until the end of its next turn. In addition, one creature of your choice in that area regains 3d8 hit points.\n"
            "    * New Moon: You momentarily emanate gloom. Each creature of your choice within 30 feet of you must succeed on a Dexterity saving throw against your spell save DC or take 3d10 necrotic damage and have its speed reduced to 0 until the end of its next turn. In addition, you become invisible until the end of your next turn, or until immediately after you make an attack or cast a spell.\n"
            "    * Crescent Moon: You can magically teleport to an unoccupied space you can see within 60 feet of yourself. You can bring along one willing creature you can see within 5 feet of yourself. That creature teleports to an unoccupied space of your choice that you can see within 5 feet of your destination space. In addition, you and that creature gain resistance to all damage until the start of your next turn.\n"
            "\n"
            "Once you use one of these bonus action benefits, you can't use that benefit again until you finish a long rest, unless you spend 5 sorcery points to use it again."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
