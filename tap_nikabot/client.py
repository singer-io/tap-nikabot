import requests


BASE_URL = "https://api.nikabot.com"


class Client:
    def __init__(self, access_token, page_size):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {access_token}"})
        self.page_size = page_size

    def fetch_users(self, page):
        params = {"limit": self.page_size, "page": page}
        response = self.session.get(f"{BASE_URL}/api/v1/users", params=params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def fetch_swagger_definition():
        response = requests.get(f"{BASE_URL}/v2/api-docs?group=public")
        response.raise_for_status()
        swagger = response.json()
        return swagger
