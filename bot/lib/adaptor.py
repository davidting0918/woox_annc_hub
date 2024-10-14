import requests as req


class AnnouncementClient:
    BASE_URL = "http://localhost:8000"
    chats_prefix = "/chats"

    def __init__(self, api_key: str, api_secret: str):
        self.base_url = self.BASE_URL
        self.api_key = api_key
        self.api_secret = api_secret
        self.header = {"X-API-KEY": self.api_key, "X-API-SECRET": self.api_secret}
        self.session = req.Session()

    def _request(self, method: str, url: str, params: dict = None):
        if method == "GET":
            return self._handle_response(self.session.get(url, headers=self.header, params=params))
        elif method == "POST":
            return self._handle_response(self.session.post(url, headers=self.header, json=params))
        else:
            raise ValueError(f"Invalid method: {method}")

    @staticmethod
    def _handle_response(response: req.Response):
        if response.status_code == 200:
            return response.json()
        else:
            return response.text

    def _get(self, url: str, params: dict = None):
        return self._request("GET", url, params)

    def _post(self, url: str, params: dict = None):
        return self._request("POST", url, params)

    # chat related
    def create_chat(self, **kwargs):
        url = f"{self.base_url}{self.chats_prefix}/create"
        return self._post(url, params=kwargs)

    def update_chat(self, **kwargs):
        url = f"{self.base_url}{self.chats_prefix}/update"
        return self._post(url, params=kwargs)

    def delete_chat(self, **kwargs):
        url = f"{self.base_url}{self.chats_prefix}/delete"
        return self._post(url, params=kwargs)

    def get_chat_info(self, **kwargs):
        url = f"{self.base_url}{self.chats_prefix}/info"
        return self._get(url, params=kwargs)

    def update_chats_dashboard(self, **kwargs):
        url = f"{self.base_url}{self.chats_prefix}/update_dashboard"
        return self._get(url, params=kwargs)

    # user related
    def create_user(self, **kwargs):
        url = f"{self.base_url}/users/create"
        return self._post(url, params=kwargs)

    def update_user(self, **kwargs):
        url = f"{self.base_url}/users/update"
        return self._post(url, params=kwargs)

    def delete_user(self, **kwargs):
        url = f"{self.base_url}/users/delete"
        return self._post(url, params=kwargs)

    def get_user_info(self, **kwargs):
        url = f"{self.base_url}/users/info"
        return self._get(url, params=kwargs)

    def in_whitelist(self, **kwargs):
        url = f"{self.base_url}/users/in_whitelist"
        return self._get(url, params=kwargs)

    def is_admin(self, **kwargs):
        url = f"{self.base_url}/users/is_admin"
        return self._get(url, params=kwargs)

    # ticket related
    def create_ticket(self, **kwargs):
        url = f"{self.base_url}/tickets/create"
        return self._post(url, params=kwargs)

    def approve_ticket(self, **kwargs):
        url = f"{self.base_url}/tickets/approve"
        return self._post(url, params=kwargs)

    def reject_ticket(self, **kwargs):
        url = f"{self.base_url}/tickets/reject"
        return self._post(url, params=kwargs)

    def delete_ticket(self, **kwargs):
        url = f"{self.base_url}/tickets/delete"
        return self._post(url, params=kwargs)

    def get_ticket_info(self, **kwargs):
        url = f"{self.base_url}/tickets/info"
        return self._get(url, params=kwargs)

    def update_ticket_dashboard(self, **kwargs):
        url = f"{self.base_url}/tickets/update_dashboard"
        return self._get(url, params=kwargs)
