from datetime import datetime
import pytest
from api.app.models.menu import Menu, MenuItem
from api.app.repositories.menu import FileSystemMenuRepository, MenuRepository


def _menu(keypath: str = "m", title: str = "Main Menu") -> Menu:
    return Menu(
        title=title,
        owner="toby",
        keypath=keypath,
        items=[],
        header="Welcome",
        access_groups=["admin"],
    )


def _menu_item(key: str = "i", title: str = "Settings", keypath: str = "mi") -> MenuItem:
    return MenuItem(
        title=title,
        key=key,
        keypath=keypath,
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
    assert (tmp_path / "index.json").exists()
    assert repo.get_menu(menu.keypath) == menu

    updated = _menu(title="Updated")
    repo.update_menu(updated)
    assert repo.get_menu(updated.keypath) == updated

    repo.delete_menu(updated)
    assert repo.get_menu(updated.keypath) is None


def test_filesystem_menu_repository_missing_menu_items_returns_empty(tmp_path) -> None:
    repo = FileSystemMenuRepository(str(tmp_path))

    with pytest.raises(ValueError):
        repo.get_menu_items("x")


def test_filesystem_menu_repository_menu_item_file_crud(tmp_path) -> None:
    repo = FileSystemMenuRepository(str(tmp_path))
    menu = _menu(keypath="m")
    item = _menu_item()
    item.last_change = None

    repo.create_menu(menu)

    repo.create_menu_item(menu, item)
    returned_item = repo.get_menu_items(menu.keypath)
    assert returned_item[0].key == item.key

    item.title = "Updated Settings"
    repo.update_menu_item(menu, item)
    returned_item = repo.get_menu_items(menu.keypath)
    assert returned_item[0].key == item.key
    assert returned_item[0].title == item.title

    repo.delete_menu_item(menu, item)
    returned_items = repo.get_menu_items(menu.keypath)
    assert len(returned_items) == 0
