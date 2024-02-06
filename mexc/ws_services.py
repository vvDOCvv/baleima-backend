import asyncio, json
from time import time
from aiohttp import ClientSession
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError
from .trade_services import MakeRequest



class ListenKeys:
    def __init__(self, api_key: str, secret_key: str) -> None:
        self.api_key: str = api_key
        self.secret_key: str = secret_key


    async def get_listen_key(self):
        all_listen_keys = await self.query_all_listen_keys()

        if all_listen_keys:
            return all_listen_keys
        else:
          create_listen_key = await self.create_listen_key()
          return create_listen_key


    async def key_requests(self, method: str, params: dict):
        headers = {"x-mexc-apikey": self.api_key}
        url = "/api/v3/userDataStream"

        async with ClientSession(base_url="https://api.mexc.com") as session:
            async with session.request(method=method, url=url, headers=headers, params=params) as response:
                return await response.json()


    async def create_listen_key(self):
        """Функция для запроса всех ListenKey"""

        timestamp = int(time() * 1000)
        params = {
            "timestamp": timestamp,
            "signature": MakeRequest.make_signature(secret_key=self.secret_key, timestamp=timestamp)
        }

        data = await self.key_requests(method="post", params=params)
        return data.get("listenKey")


    async def query_all_listen_keys(self):
        """Функция для продления ListenKey (Keep-alive)"""

        timestamp = int(time() * 1000)
        params = {
            "timestamp": timestamp,
            "signature": MakeRequest.make_signature(secret_key=self.secret_key, timestamp=timestamp)
        }

        data = await self.key_requests(method="get", params=params)
        return data.get("listenKey")


    async def keep_alive_listen_key(self, listen_key: str):
        """Функция для продления ListenKey (Keep-alive)"""

        timestamp = int(time() * 1000)
        params = {"listenKey": listen_key}
        params["signature"] = MakeRequest.make_signature(secret_key=self.secret_key, params=params, timestamp=timestamp)
        params["timestamp"] = timestamp

        data = await self.key_requests(method="put", params=params)
        return data.get("listenKey")


    async def delete_listen_key(self, listen_key: str):
        """ Функция для закрытия ListenKey"""

        timestamp = int(time() * 1000)

        params = {"listenKey": listen_key}
        params["signature"] = MakeRequest.make_signature(secret_key=self.secret_key, params=params, timestamp=timestamp)
        params["timestamp"] = timestamp

        data = await self.key_requests(method="delete", params=params)
        return data.get("listenKey")




async def connect_to_ws(api_key: str, secret_key: str):
    subscription_message = {
        "method": "SUBSCRIPTION",
        "params": ["spot@private.orders.v3.api"],
    }

    lk = ListenKeys(api_key=api_key, secret_key=secret_key)
    listen_key = await lk.create_listen_key()

    ws_url = f"wss://wbs.mexc.com/ws?listenKey={listen_key}"

    try:
        async with connect(uri=ws_url) as ws:
            if ws.open:
                print("Cpnnection is open")
                await ws.send(json.dumps(subscription_message))

            while True:
                msg = await ws.recv()

                print(msg, '----------')

            await ws.close()
            
    except ConnectionClosedError:
        pass





