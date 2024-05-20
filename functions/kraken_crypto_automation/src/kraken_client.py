import base64
import hashlib
import hmac
import logging
import urllib.parse
from decimal import Decimal
from time import time
from typing import Optional, Dict

import requests

logger = logging.getLogger(__name__)


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


class KrakenClient:
    _BASE_URL = "https://api.kraken.com"
    _BASE_PATH_PRIVATE = "/0/private"
    _BASE_PATH_PUBLIC = "/0/public"
    _HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    _ADD_ORDER_PATH = "/AddOrder"
    _GET_BALANCE_PATH = "/Balance"

    def __init__(self, api_key, private_key, environment="development"):
        self.api_key = api_key
        self.private_key = private_key
        self.environment = environment
        self.balances: Optional[Dict[str, Decimal]] = None

    def _request(
        self,
        url,
        *,
        method="POST",
        params=None,
        headers=None,
        payload=None,
        base_path=_BASE_PATH_PRIVATE,
    ):
        if payload is None:
            payload = {}

        if headers is None:
            headers = {}

        if params is None:
            params = {}

        payload.update({"nonce": int(time() * 1000)})
        full_url = self._BASE_URL + base_path + url
        signature = get_kraken_signature(base_path + url, payload, self.private_key)
        full_headers = {**headers, "API-Key": self.api_key, "API-Sign": signature}

        response = requests.request(
            method, full_url, headers=full_headers, data=payload, params=params
        )
        return response

    def _get_balances(self):
        response = self._request(method="POST", url=self._GET_BALANCE_PATH).json()
        return response.get("result", None)

    def get_balance(self, source: str) -> Optional[Decimal]:
        if self.balances is None:
            self.balances = self._get_balances()

        balance = self.balances.get(source, None)
        if balance is None:
            logger.error(f"\t Balance for {source} not found.")
            return None

        return Decimal(balance)

    def get_price(self, pair) -> Optional[str]:
        response = self._request(
            method="GET",
            url="/Ticker",
            base_path=self._BASE_PATH_PUBLIC,
            params={"pair": pair},
        )
        result = response.json().get("result", {})
        first_result = next(iter(result.values()), {})
        return first_result.get("c", [None])[0]

    def get_pair_information(self, pair: str) -> Optional[Dict]:
        response = self._request(
            method="GET",
            url="/AssetPairs",
            base_path=self._BASE_PATH_PUBLIC,
            params={"pair": pair},
        )
        json = response.json()
        error = json.get("error", [])
        if len(error) > 0:
            logger.error("\t " + error)
            return None

        result = json.get("result", {})
        first_item = next(iter(result.values()), {})
        if first_item.get("altname") != pair:
            return None

        return first_item

    def add_limit_order(self, pair: str, amount: Decimal, *, type="buy") -> None:
        last_closed_price = self.get_price(pair)
        if last_closed_price is None:
            logger.error(f"\t Price for {pair} not found. Skipping order creation")
            return None

        pair_info = self.get_pair_information(pair)
        if pair_info is None:
            logger.error(
                f"\t Pair information for {pair} not found. Skipping order creation"
            )
            return None

        pair_decimals = pair_info.get("pair_decimals")
        modifier = "1.02" if type == "buy" else "0.98"
        price = Decimal(last_closed_price) * Decimal(modifier)
        volume = amount / price

        response = self._request(
            self._ADD_ORDER_PATH,
            method="POST",
            payload={
                "ordertype": "limit",
                "type": type,
                "volume": volume,
                "pair": pair,
                "price": f"{price:.{pair_decimals}f}",
            },
        )
        json_response = response.json()
        error = json_response.get("error")

        if len(error) > 0:
            logger.error("\t " + error)
        else:
            logger.info(f"\t Order created successfully for {pair} at {price}")
