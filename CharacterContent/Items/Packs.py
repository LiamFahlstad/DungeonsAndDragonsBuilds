from CharacterContent.Items import Items


class Pack:
    def get_items(self) -> list[tuple[Items.Item, int]]:
        raise NotImplementedError("Subclasses must implement get_items method.")


class DungeoneersPack(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Backpack(), 1),
            (Items.Caltrops(), 1),
            (Items.Crowbar(), 1),
            (Items.FlasksOfOil(), 2),
            (Items.Rations(), 10),
            (Items.Rope(), 1),
            (Items.Tinderbox(), 1),
            (Items.Torch(), 10),
            (Items.Waterskin(), 1),
        ]


class Entertainers(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Backpack(), 1),
            (Items.Bedroll(), 1),
            (Items.Bell(), 1),
            (Items.BullseyeLantern(), 1),
            (Items.Costume(), 3),
            (Items.Mirror(), 1),
            (Items.FlasksOfOil(), 8),
            (Items.Rations(), 9),
            (Items.Tinderbox(), 10),
            (Items.Waterskin(), 1),
        ]


class BurglarsPack(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Backpack(), 1),
            (Items.BallBearings(), 1),
            (Items.Bell(), 1),
            (Items.Candle(), 10),
            (Items.Crowbar(), 1),
            (Items.HoodedLantern(), 1),
            (Items.Rations(), 5),
            (Items.Rope(), 1),
            (Items.Tinderbox(), 1),
            (Items.Waterskin(), 1),
        ]


class DiplomatsPack(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Chest(), 1),
            (Items.FineClothes(), 1),
            (Items.Ink(), 1),
            (Items.InkPen(), 5),
            (Items.Lamp(), 1),
            (Items.MapOrScrollCase(), 2),
            (Items.FlasksOfOil(), 4),
            (Items.Paper(), 5),
            (Items.Parchment(), 5),
            (Items.Perfume(), 1),
            (Items.Tinderbox(), 1),
        ]


class ExplorersPack(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Backpack(), 1),
            (Items.Bedroll(), 1),
            (Items.FlasksOfOil(), 2),
            (Items.Rations(), 10),
            (Items.Rope(), 1),
            (Items.Tinderbox(), 1),
            (Items.Torch(), 10),
            (Items.Waterskin(), 1),
        ]


class PriestsPack(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Backpack(), 1),
            (Items.Blanket(), 1),
            (Items.HolyWater(), 1),
            (Items.Lamp(), 1),
            (Items.Rations(), 7),
            (Items.Robe(), 1),
            (Items.Tinderbox(), 1),
        ]


class ScholarsPack(Pack):
    def get_items(self) -> list[tuple[Items.Item, int]]:
        return [
            (Items.Backpack(), 1),
            (Items.Book(), 1),
            (Items.Ink(), 1),
            (Items.InkPen(), 1),
            (Items.Lamp(), 1),
            (Items.FlasksOfOil(), 10),
            (Items.Parchment(), 10),
            (Items.Tinderbox(), 1),
        ]
