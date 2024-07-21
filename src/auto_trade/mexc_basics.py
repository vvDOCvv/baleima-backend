from time import time
from aiohttp import ClientSession
import hmac
import hashlib
from urllib.parse import urlencode, quote
from user.schemas import UserSchema
from .services import retry_request


class MEXCBasics:
    MEXC_URL = "https://api.mexc.com"
    RECV_WINDOW = 20000


    def __init__(self, user: UserSchema) -> None:
        self.mexc_key = user.mexc_api_key
        self.mexc_secret = user.mexc_secret_key
        self.user: UserSchema = user


    async def account_info(self, url_path: str, method: str = "GET", params: dict = None) -> dict:
        timestamp = int(time() * 1000)

        if params:
            params["signature"] = self.make_signature(
                secret_key=self.mexc_secret, timestamp=timestamp, params=params
            )
        else:
            params = {"signature": self.make_signature(secret_key=self.mexc_secret, timestamp=timestamp)}

        headers = {
            "Content-Type": "application/json",
            "x-mexc-apikey": self.mexc_key
        }
        params["timestamp"] = timestamp


        async with ClientSession(base_url=self.MEXC_URL) as session:
            async with session.request(method=method, url=url_path, headers=headers, params=params) as response:
                return await response.json()


    async def get_balance(self, symbol: str | None = None) -> list[dict] | dict | None:
        balances_cor = await self.account_info(method="GET", url_path="/api/v3/account")
        balances = balances_cor.get('balances')

        if not balances:
            return

        if symbol:
            for balance in balances:
                if balance["asset"] == symbol:
                    return balance
            return None

        return balances


    @retry_request
    async def buy(self) -> dict:
        params = {
            "symbol": self.user.symbol_to_trade,
            "side": "BUY",
            "type": "MARKET",
            # "quoteOrderQty": self.user.trade_quantity,
            "quoteOrderQty": 6.5,
            "recvWindow": self.RECV_WINDOW,
        }
        return await self.account_info(method="POST", url_path="/api/v3/order", params=params)


    async def sell(self, sell_price: int | float, executed_qty: int | float) -> dict:
        params = {
            "symbol": self.user.symbol_to_trade,
            "side": "SELL",
            "type": "LIMIT",
            "quantity": executed_qty,
            "price": sell_price,
            "recvWindow": self.RECV_WINDOW,
        }
        return await self.account_info(method="POST", url_path="/api/v3/order", params=params)


    @retry_request
    async def get_order_info(self, order_id: str, symbol: str) -> dict:
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "recvWindow": self.RECV_WINDOW
        }
        return await self.account_info(url_path=f"/api/v3/order", params=params)


    async def get_current_open_orders(self, symbol: str) -> dict:
        return await self.account_info(url_path="/api/v3/openOrders", params={"symbol": symbol})


    async def get_all_orders(self, symbol: str) -> dict:
        return await self.account_info(url_path="/api/v3/allOrders", params={"symbol": symbol})


    @staticmethod
    def make_signature(secret_key: str, timestamp: int, params: dict = None) -> str:
        if params:
            encoded_params = urlencode(params, quote_via=quote)
            msg = f"{encoded_params}&timestamp={timestamp}"
        else:
            msg = f"timestamp={timestamp}"

        secret_key = secret_key.encode("utf-8")
        msg = msg.encode("utf-8")

        return hmac.new(key=secret_key, msg=msg, digestmod=hashlib.sha256).hexdigest()


    @staticmethod
    async def get_current_price_by_symbol(symbol: str) -> dict:
        url = "https://api.mexc.com/api/v3/ticker/price"
        params = {"symbol": symbol}

        async with ClientSession() as session:
            async with session.get(url=url, params=params) as response:
                return await response.json()
