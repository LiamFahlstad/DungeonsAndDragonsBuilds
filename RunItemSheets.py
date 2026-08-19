import importlib
import inspect
import pkgutil

import Builds.ItemSheets


if __name__ == "__main__":
    for module_info in pkgutil.iter_modules(Builds.ItemSheets.__path__):
        module_name = module_info.name
        if module_name.startswith("_"):
            continue
        module = importlib.import_module(f"Builds.ItemSheets.{module_name}")
        for attr_name, attr_value in inspect.getmembers(module, inspect.isfunction):
            if attr_name.endswith("_item_sheet"):
                print(f"Generating {attr_name}...")
                attr_value()
