from Items import Items


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
