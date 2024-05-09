import base64
import hashlib
import hmac
import urllib.parse
from time import time

import requests


def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


class KrakenClient:
    _BASE_URL = "https://api.kraken.com"
    _BASE_PATH = "/0/private"
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

    def _request(self, url, *, method="POST", headers=None, payload=None):
        if payload is None:
            payload = {}

        if headers is None:
            headers = {}

        payload.update({"nonce": int(time() * 1000)})
        full_url = self._BASE_URL + self._BASE_PATH + url
        signature = get_kraken_signature(
            self._BASE_PATH + url, payload, self.private_key
        )
        full_headers = {**headers, "API-Key": self.api_key, "API-Sign": signature}

        response = requests.request(
            method, full_url, headers=full_headers, data=payload
        )
        return response

    def get_balances(self):
        return self._request(method="POST", url=self._GET_BALANCE_PATH)

    def add_order(
        self, pair, price: str, volume: str, *, type="buy", order_type="limit"
    ):
        payload = {
            "ordertype": order_type,
            "type": type,
            "volume": (volume),
            "pair": pair,
            "price": (price),
        }
        response = self._request(self._ADD_ORDER_PATH, method="POST", payload=payload)
        return response
