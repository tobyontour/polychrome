from ..models.menu import Menu, MenuItem
from pydantic import BaseModel
import os
import json

class MenuRepository:
    def __init__(self):
        self.menus = []

    def get_menu(self, keypath: str) -> Menu | None:
        return next((menu for menu in self.menus if menu.keypath == keypath), None)

    def create_menu(self, menu: Menu) -> None:
        self.menus.append(menu)

    def update_menu(self, menu: Menu) -> None:
        self.menus[self.menus.index(menu)] = menu

    def delete_menu(self, menu: Menu) -> None:
        self.menus.remove(menu)

    def get_menu_items(self, keypath: str) -> list[MenuItem]:
        menu = self.get_menu(keypath)
        if menu is None:
            return []
        return menu.items

    def create_menu_item(self, menu: Menu, item: MenuItem) -> None:
        menu.items.append(item)

    def update_menu_item(self, menu: Menu, item: MenuItem) -> None:
        menu.items[menu.items.index(item)] = item

    def delete_menu_item(self, menu: Menu, item: MenuItem) -> None:
        menu.items.remove(item)

class MenuFile(BaseModel):
    menus: dict[str, Menu]

class FileSystemMenuRepository(MenuRepository):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def _load_menus(self, create: bool = False) -> dict[str, Menu]:
        if not os.path.exists(os.path.join(self.base_path, "index.json")):
            return {}
        with open(os.path.join(self.base_path, "index.json"), "r") as f:
            j = json.load(f)
            data = MenuFile.model_validate(j)
        return data.menus

    def _save_menus(self, menus: dict[str, Menu]) -> None:
        with open(os.path.join(self.base_path, "index.json"), "w") as f:
            f.write(MenuFile(menus=menus).model_dump_json(indent=2))

    def get_menu(self, keypath: str) -> Menu | None:
        menus = self._load_menus()
        if keypath in menus:
            return menus[keypath]

    def create_menu(self, menu: Menu) -> None:
        menus = self._load_menus(create=True)
        menus[menu.keypath] = menu
        self._save_menus(menus)

    def update_menu(self, menu: Menu) -> None:
        menus = self._load_menus()
        menus[menu.keypath] = menu
        self._save_menus(menus)

    def delete_menu(self, menu: Menu) -> None:
        menus = self._load_menus()
        menus.pop(menu.keypath)
        self._save_menus(menus)

    def get_menu_items(self, keypath: str) -> list[MenuItem]:
        menus = self._load_menus()
        if keypath in menus:
            return menus[keypath].items
        raise ValueError(f"Menu not found: {keypath}")

    def create_menu_item(self, menu: Menu, item: MenuItem) -> None:
        menus = self._load_menus()
        if menu.keypath not in menus:
            raise ValueError(f"Menu not found: {menu.keypath}")
        menus[menu.keypath].items.append(item)
        self._save_menus(menus)

    def update_menu_item(self, menu: Menu, item: MenuItem) -> None:
        menus = self._load_menus()
        if menu.keypath not in menus:
            raise ValueError(f"Menu not found: {menu.keypath}")
        target_item_index = next((index for index, item in enumerate(menus[menu.keypath].items) if item.key == item.key), None)
        if target_item_index is not None:
            menus[menu.keypath].items[target_item_index] = item
            self._save_menus(menus)

    def delete_menu_item(self, menu: Menu, item: MenuItem) -> None:
        menus = self._load_menus()
        if menu.keypath not in menus:
            raise ValueError(f"Menu not found: {menu.keypath}")
        target_item = next((item for item in menus[menu.keypath].items if item.key == item.key), None)
        if target_item is not None:
            menus[menu.keypath].items.remove(target_item)
            self._save_menus(menus)
