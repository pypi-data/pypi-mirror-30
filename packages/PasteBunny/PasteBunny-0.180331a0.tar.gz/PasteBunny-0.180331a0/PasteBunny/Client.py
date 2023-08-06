from .Api import SyncApi, AsyncApi
from .Models import Paste


class SyncClient:

    def __init__(self, dev_key, username, password):
        self.api = SyncApi(dev_key)
        if username is not None and password is not None:
            self.user_key = self.get_user_key(
                username=username,
                password=password
            )

    def get_user_key(self, username, password):
        return self.api.get_user_key(
            username=username,
            password=password
        )

    def create_paste(self, paste=Paste(), private=False):
        if private is False:
            result = self.api.create_paste(
                code=paste.get_code(),
                name=paste.get_name(),
                expiry=paste.get_expiry(),
                privacy=paste.get_privacy(),
                _format=paste.get_format(),
                user_key=self.user_key
            )
        else:
            result = self.api.create_paste(
                code=paste.get_code(),
                name=paste.get_name(),
                expiry=paste.get_expiry(),
                privacy=paste.get_privacy(),
                _format=paste.get_format(),
            )
        paste.set_url(result)
        paste.set_key(result.split("/")[-1])

    def delete_paste(self, paste_key):
        return self.api.delete_paste(
            paste_key=paste_key,
            user_key=self.user_key
        )

    def get_paste(self, paste_key):
        return self.api.get_paste(
                paste_key=paste_key,
                user_key=self.user_key
        )

    def list_pastes(self, limit=50):
        return self.api.list_pastes(
            user_key=self.user_key,
            limit=limit
        )

    def get_trending_pastes(self):
        return self.api.list_trending_pastes()

    def get_user_data(self):
        return self.api.get_user_data(self.user_key)

    def close(self):
        return self.api.session.close()


class AsyncClient:

    def __init__(self, dev_key, username, password):
        self.api = AsyncApi(dev_key)
        if username is not None and password is not None:
            self.username = username
            self.password = password
        self.user_key = None

    async def login(self):
        self.user_key = await self.get_user_key(
            username=self.username,
            password=self.password
        )

    async def get_user_key(self, username, password):
        return await self.api.get_user_key(
            username=username,
            password=password
        )

    async def create_paste(self, paste=Paste(), private=False):
        if private is False:
            result = await self.api.create_paste(
                code=paste.get_code(),
                name=paste.get_name(),
                expiry=paste.get_expiry(),
                privacy=paste.get_privacy(),
                _format=paste.get_format(),
                user_key=self.user_key
            )
        else:
            result = await self.api.create_paste(
                code=paste.get_code(),
                name=paste.get_name(),
                expiry=paste.get_expiry(),
                privacy=paste.get_privacy(),
                _format=paste.get_format(),
            )
        paste.set_url(result)
        paste.set_key(result.split("/")[-1])

    async def delete_paste(self, paste_key):
        return self.api.delete_paste(
            paste_key=paste_key,
            user_key=self.user_key
        )

    async def get_paste(self, paste_key):
        return self.api.get_paste(
                paste_key=paste_key,
                user_key=self.user_key
        )

    async def list_pastes(self, limit=50):
        return self.api.list_pastes(
            user_key=self.user_key,
            limit=limit
        )

    async def get_trending_pastes(self):
        return self.api.list_trending_pastes()

    async def get_user_data(self):
        return self.api.get_user_data(self.user_key)

    async def close(self):
        return await self.api.session.close()
