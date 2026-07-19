from Definitions import SORCERER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class WildMagicSurge(Feature):
    def __init__(self):
        super().__init__(name="Wild Magic Surge", origin="Wild Magic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your spellcasting can unleash surges of untamed magic. Once per turn, you can roll 1d20 immediately after you cast a Sorcerer spell with a spell slot. If you roll a 20, roll on the Wild Magic Surge table to create a magical effect.\n"
            "If the magical effect is a spell, it is too wild to be affected by your Metamagic."
        )
        return description


class WildMagicSurgeTable(Feature):
    def __init__(self):
        super().__init__(
            name="Wild Magic Surge Table", origin="Wild Magic Sorcerer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Wild Magic Surge\n"
            "1d100	Effect\n"
            "01-04	Roll on this table at the start of each of your turns for the next minute, ignoring this result on subsequent rolls.\n"
            "05-08	A creature that is Friendly toward you appears in a random unoccupied space within 60 feet of you. The creature is under the DM's control and disappears 1 minute later. Roll 1d4 to determine the creature: on a 1, a Modron Duodrone appears; on a 2, a Flumph appears; on a 3, a Modron Monodrone appears; on a 4, a Unicorn appears.\n"
            "09-12	For the next minute, you regain 5 Hit Points at the start of each of your turns.\n"
            "13-16	Creatures have Disadvantage on saving throws against the next spell you cast in the next minute that involves a saving throw.\n"
            "17-20	You are subjected to an effect that lasts for 1 minute unless its description says otherwise. Roll 1d8 to determine the effect: on a 1, you're surrounded by faint, ethereal music only you and creatures within 5 feet of you can hear; on a 2, your size increases by one size category; on a 3, you grow a long beard made of feathers that remains until you sneeze, at which point the feathers explode from your face and vanish; on a 4, you must shout when you speak; on a 5, illusory butterflies flutter in the air within 10 feet of you; on a 6, an eye appears on your forehead, granting you Advantage on Wisdom (Perception) checks; on a 7, pink bubbles float out of your mouth whenever you speak; on an 8, your skin turns a vibrant shade of blue for 24 hours or until the effect is ended by a Remove Curse spell.\n"
            "21-24	For the next minute, all your spells with a casting time of an action have a casting time of a Bonus Action.\n"
            "25-28	You are transported to the Astral Plane until the end of your next turn. You then return to the space you previously occupied or the nearest unoccupied space if that space is occupied.\n"
            "29-32	The next time you cast a spell that deals damage within the next minute, don't roll the spell's damage dice for the damage. Instead use the highest number possible for each damage die.\n"
            "33-36	You have Resistance to all damage for the next minute.\n"
            "37-40	You turn into a potted plant until the start of your next turn. While you're a plant, you have the Incapacitated condition and have Vulnerability to all damage. If you drop to 0 Hit Points, your pot breaks, and your form reverts.\n"
            "41-44	For the next minute, you can teleport up to 20 feet as a Bonus Action on each of your turns.\n"
            "45-48	You and up to three creatures you choose within 30 feet of you have the Invisible condition for 1 minute. This invisibility ends on a creature immediately after it makes an attack roll, deals damage, or casts a spell.\n"
            "49-52	A spectral shield hovers near you for the next minute, granting you a +2 bonus to AC and immunity to Magic Missile.\n"
            "53-56	You can take one extra action on this turn.\n"
            "57-60	You cast a random spell. If the spell normally requires Concentration, it doesn't require Concentration in this case; the spell lasts for its full duration. Roll 1d10 to determine the spell: on a 1, Confusion; on a 2, Fireball; on a 3, Fog Cloud; on a 4, Fly (cast on a random creature within 60 feet of you); on a 5, Grease; on a 6, Levitate (cast on yourself); on a 7, Magic Missile (cast as a level 5 spell); on an 8, Mirror Image; on a 9, Polymorph (cast on yourself), and if you fail the saving throw, you turn into a Goat; on a 10, See Invisibility.\n"
            "61-64	For the next minute, any flammable, nonmagical object you touch that isn't being worn or carried by another creature bursts into flame, takes 1d4 Fire damage, and is burning.\n"
            "65-68	If you die within the next hour, you immediately revive as if by the Reincarnate spell.\n"
            "69-72	You have the Frightened condition until the end of your next turn. The DM determines the source of your fear.\n"
            "73-76	You teleport up to 60 feet to an unoccupied space you can see.\n"
            "77-80	A random creature within 60 feet of you has the Poisoned condition for 1d4 hours.\n"
            "81-84	You radiate Bright Light in a 30-foot radius for the next minute. Any creature that ends its turn within 5 feet of you has the Blinded condition until the end of its next turn.\n"
            "85-88	Up to three creatures of your choice that you can see within 30 feet of you take 1d10 Necrotic damage. You regain Hit Points equal to the sum of the Necrotic damage dealt.\n"
            "89-92	Up to three creatures of your choice that you can see within 30 feet of you take 4d10 Lightning damage.\n"
            "93-96	You and all creatures within 30 feet of you have Vulnerability to Piercing damage for the next minute.\n"
            "97-00	Roll 1d6: On a 1, you regain 2d10 Hit Points; on a 2, one ally of your choice within 300 feet of you regains 2d10 Hit Points; on a 3, you regain your lowest-level expended spell slot; on a 4, one ally of your choice within 300 feet of you regains their lowest-level expended spell slot; on a 5, you regain all your expended Sorcery Points; on a 6, all the effects of row 17-20 affect you simultaneously."
        )
        return description


class TidesOfChaos(Feature):
    def __init__(self):
        super().__init__(name="Tides of Chaos", origin="Wild Magic Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can manipulate chaos itself to give yourself Advantage on one D20 Test before you roll the d20. Once you do so, you must cast a Sorcerer spell with a spell slot or finish a Long Rest before you can use this feature again.\n"
            "If you do cast a Sorcerer spell with a spell slot before you finish a Long Rest, you automatically roll on the Wild Magic Surge table."
        )
        return description


class BendLuck(Feature):
    def __init__(self):
        super().__init__(name="Bend Luck", origin="Wild Magic Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have the ability to twist fate using your wild magic. Immediately after another creature you can see rolls the d20 for a D20 Test, you can take a Reaction and spend 1 Sorcery Point to roll 1d4 and apply the number rolled as a bonus or penalty (your choice) to the d20 roll."
        return description


class ControlledChaos(Feature):
    def __init__(self):
        super().__init__(name="Controlled Chaos", origin="Wild Magic Sorcerer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a modicum of control over the surges of your wild magic. Whenever you roll on the Wild Magic Surge table, you can roll twice and use either number."
        return description


class TamedSurge(Feature):
    def __init__(self):
        super().__init__(name="Tamed Surge", origin="Wild Magic Sorcerer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Immediately after you cast a Sorcerer spell with a spell slot, you can create an effect of your choice from the Wild Magic Surge table instead of rolling on that table. You can choose any effect in the table except for the final row, and if the chosen effect involves a roll, you must make it.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest."
        )
        return description
