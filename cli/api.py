import httpx
from api.app.models.menu import Menu
from api.app.models.commentfile import CommentFile
class PolychromeAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.client = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {token}"})

    async def get_username(self) -> str:
        response = await self.client.get("/api/me")
        return response.json()["username"]

    async def get_menu(self, keypath: str) -> Menu | None:
        if keypath != "_":
            keypath = keypath.lstrip("_")
        try:
            response = await self.client.get(f"/api/menu/{keypath}")
            response.raise_for_status()
            return Menu.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise e

    async def get_comment_file(self, keypath: str) -> CommentFile | None:
        try:
            response = await self.client.get(f"/api/commentfile/{keypath}")
            response.raise_for_status()
            return CommentFile.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise e