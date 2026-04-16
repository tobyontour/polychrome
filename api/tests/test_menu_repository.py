from datetime import datetime

from api.app.models.menu import Menu, MenuItem
from api.app.repositories.menu import FileSystemMenuRepository, MenuRepository


def _menu(keypath: str = "menu.json", title: str = "Main Menu") -> Menu:
    return Menu(
        title=title,
        owner="toby",
        keypath=keypath,
        items=[],
        header="Welcome",
        access_groups=["admin"],
    )


def _menu_item(key: str = "settings", title: str = "Settings") -> MenuItem:
    return MenuItem(
        title=title,
        key=key,
        item_type="submenu",
        last_change=datetime(2026, 1, 1),
        owner="toby",
    )


def test_menu_repository_crud_and_lookup_by_keypath() -> None:
    repo = MenuRepository()
    menu = _menu()

    repo.create_menu(menu)

    assert repo.get_menu(menu.keypath) == menu
    assert repo.get_menu("missing.json") is None

    menu.title = "Updated"
    repo.update_menu(menu)
    assert repo.get_menu(menu.keypath) == menu

    repo.delete_menu(menu)
    assert repo.get_menu(menu.keypath) is None


def test_menu_repository_menu_items_crud() -> None:
    repo = MenuRepository()
    menu = _menu()
    item = _menu_item()

    repo.create_menu(menu)
    assert repo.get_menu_items(menu.keypath) == []

    repo.create_menu_item(menu, item)
    assert repo.get_menu_items(menu.keypath) == [item]
    assert repo.get_menu_items("missing.json") == []

    item.title = "Updated Settings"
    repo.update_menu_item(menu, item)
    assert repo.get_menu_items(menu.keypath) == [item]

    repo.delete_menu_item(menu, item)
    assert repo.get_menu_items(menu.keypath) == []


def test_filesystem_menu_repository_round_trip_menu(tmp_path) -> None:
    repo = FileSystemMenuRepository(str(tmp_path))
    menu = _menu()

    repo.create_menu(menu)
    assert (tmp_path / menu.keypath).exists()
    assert repo.get_menu(menu.keypath) == menu

    updated = _menu(title="Updated")
    repo.update_menu(updated)
    assert repo.get_menu(updated.keypath) == updated

    repo.delete_menu(updated)
    assert repo.get_menu(updated.keypath) is None


def test_filesystem_menu_repository_missing_menu_items_returns_empty(tmp_path) -> None:
    repo = FileSystemMenuRepository(str(tmp_path))

    assert repo.get_menu_items("does-not-exist.json") == []


def test_filesystem_menu_repository_menu_item_file_crud(tmp_path) -> None:
    repo = FileSystemMenuRepository(str(tmp_path))
    menu = _menu(keypath="menu-items")
    item = _menu_item()
    item.last_change = None
    item_path = tmp_path / menu.keypath / item.key
    item_path.parent.mkdir(parents=True, exist_ok=True)

    repo.create_menu_item(menu, item)
    assert item_path.exists()
    assert item_path.read_text() != ""

    item.title = "Updated Settings"
    repo.update_menu_item(menu, item)
    assert item_path.exists()
    assert item_path.read_text() != ""

    repo.delete_menu_item(menu, item)
    assert not item_path.exists()
