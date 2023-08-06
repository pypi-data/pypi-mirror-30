from .Constants import Constants, Expiry, Privacy
from .Models import PastebinException
import requests
from aiohttp import ClientSession


class SyncApi:

    def __init__(self, dev_key):
        self.dev_key = dev_key
        self.constants = Constants()
        self.session = requests.Session()
        self.session.headers = self.constants.get_headers()

    def do(self, url, parameters):
        with self.session.post(url=url, data=parameters) as r:
            if "Bad API request" in r.text:
                raise PastebinException(r.text.split(", ")[1])
            else:
                return r.text

    def get_user_key(self, username, password):
        return self.do(
            url=self.constants.get_user_url(),
            parameters={
                "api_dev_key": self.dev_key,
                "api_user_name": username,
                "api_user_password": password
            }
        )

    def create_paste(self, code, name, expiry=Expiry.MINUTES_10, privacy=Privacy.PUBLIC, _format='text', user_key=''):
        return self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "paste",
                "api_user_key": user_key,
                "api_paste_privacy": privacy,
                "api_paste_name": name,
                "api_paste_expire_date": expiry,
                "api_paste_format": _format,
                "api_dev_key": self.dev_key,
                "api_paste_code": code
            }
        )

    def delete_paste(self, paste_key, user_key):
        return self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "delete",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
                "api_paste_key": paste_key
            }
        )

    def get_paste(self, paste_key, user_key):
        return self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "show_paste",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
                "api_paste_key": paste_key
            }
        )

    def list_pastes(self, user_key, limit):
        return self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "list",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
                "api_results_limit": limit
            }
        )

    def list_trending_pastes(self):
        return self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "trends",
                "api_dev_key": self.dev_key
            }
        )

    def get_user_data(self, user_key):
        return self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "userdetails",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
            }
        )


class AsyncApi:

    def __init__(self, dev_key):
        self.dev_key = dev_key
        self.constants = Constants()
        self.session = None

    async def do(self, url, parameters):
        if self.session is None:
            self.session = ClientSession(headers=self.constants.get_headers())
        async with await self.session.post(url=url, data=parameters) as r:
            if "Bad API request" in await r.text():
                raise PastebinException(r.text.split(", ")[1])
            else:
                return await r.text()

    async def get_user_key(self, username, password):
        return await self.do(
            url=self.constants.get_user_url(),
            parameters={
                "api_dev_key": self.dev_key,
                "api_user_name": username,
                "api_user_password": password
            }
        )

    async def create_paste(self, code, name, expiry=Expiry.MINUTES_10, privacy=Privacy.PUBLIC, _format='text', user_key=''):
        return await self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "paste",
                "api_user_key": user_key,
                "api_paste_privacy": privacy,
                "api_paste_name": name,
                "api_paste_expire_date": expiry,
                "api_paste_format": _format,
                "api_dev_key": self.dev_key,
                "api_paste_code": code
            }
        )

    async def delete_paste(self, paste_key, user_key):
        return await self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "delete",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
                "api_paste_key": paste_key
            }
        )

    async def get_paste(self, paste_key, user_key):
        return await self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "show_paste",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
                "api_paste_key": paste_key
            }
        )

    async def list_pastes(self, user_key, limit):
        return await self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "list",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
                "api_results_limit": limit
            }
        )

    async def list_trending_pastes(self):
        return await self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "trends",
                "api_dev_key": self.dev_key
            }
        )

    async def get_user_data(self, user_key):
        return await self.do(
            url=self.constants.get_paste_url(),
            parameters={
                "api_option": "userdetails",
                "api_user_key": user_key,
                "api_dev_key": self.dev_key,
            }
        )
