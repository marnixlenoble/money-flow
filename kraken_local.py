import os

from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, firestore

from functions.kraken_crypto_automation.src.kraken_client import KrakenClient

load_dotenv()

GOOGLE_FIRESTORE_CONFIG = os.getenv("GOOGLE_FIRESTORE_CONFIG")

KRAKEN_PRIVATE_KEY = os.getenv("KRAKEN_PRIVATE_KEY")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")


if __name__ == "__main__":
    cred = credentials.Certificate(GOOGLE_FIRESTORE_CONFIG)
    initialize_app(cred)
    client = firestore.client()

    # store_ = OrderFlows(client=client)
    kraken = KrakenClient(api_key=KRAKEN_API_KEY, private_key=KRAKEN_PRIVATE_KEY)
    balances = kraken.get_balances()
    order = kraken.add_order(pair="XBTUSD", price="2.00", volume="1", type="buy")

    print(balances)
    print(order)
