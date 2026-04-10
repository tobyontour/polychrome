import httpx


class PolychromeAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.client = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {token}"})

    async def get_username(self) -> str:
        response = await self.client.get("/api/me")
        return response.json()["username"]
