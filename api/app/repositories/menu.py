from ..models.menu import Menu, MenuItem
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

class FileSystemMenuRepository(MenuRepository):
    def __init__(self, base_path: str):
        self.base_path = base_path

    def get_menu(self, keypath: str) -> Menu | None:
        path = os.path.join(self.base_path, keypath)
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return Menu.model_validate(json.load(f))

    def create_menu(self, menu: Menu) -> None:
        path = os.path.join(self.base_path, menu.keypath)
        with open(path, "w") as f:
            json.dump(menu.model_dump(), f)

    def update_menu(self, menu: Menu) -> None:
        path = os.path.join(self.base_path, menu.keypath)
        with open(path, "w") as f:
            json.dump(menu.model_dump(), f)

    def delete_menu(self, menu: Menu) -> None:
        path = os.path.join(self.base_path, menu.keypath)
        if os.path.exists(path):
            os.remove(path)

    def get_menu_items(self, keypath: str) -> list[MenuItem]:
        menu = self.get_menu(keypath)
        if menu is None:
            return []
        return menu.items

    def create_menu_item(self, menu: Menu, item: MenuItem) -> None:
        path = os.path.join(self.base_path, menu.keypath, item.key)
        with open(path, "w") as f:
            json.dump(item.model_dump(), f)

    def update_menu_item(self, menu: Menu, item: MenuItem) -> None:
        path = os.path.join(self.base_path, menu.keypath, item.key)
        with open(path, "w") as f:
            json.dump(item.model_dump(), f)

    def delete_menu_item(self, menu: Menu, item: MenuItem) -> None:
        path = os.path.join(self.base_path, menu.keypath, item.key)
        if os.path.exists(path):
            os.remove(path)