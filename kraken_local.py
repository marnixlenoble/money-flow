import logging
import os

from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, firestore

from functions.kraken_crypto_automation.src.kraken_client import KrakenClient
from functions.kraken_crypto_automation.src.kraken_client_adapter import (
    KrakenClientAdapter,
)
from functions.kraken_crypto_automation.src.order_flows import OrderFlows
from lib.flow_processor import FlowProcessor

load_dotenv()

GOOGLE_FIRESTORE_CONFIG = os.getenv("GOOGLE_FIRESTORE_CONFIG")

KRAKEN_PRIVATE_KEY = os.getenv("KRAKEN_PRIVATE_KEY")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cred = credentials.Certificate(GOOGLE_FIRESTORE_CONFIG)
    initialize_app(cred)
    client = firestore.client()
    store = OrderFlows(client=client)

    kraken = KrakenClient(api_key=KRAKEN_API_KEY, private_key=KRAKEN_PRIVATE_KEY)

    processor = FlowProcessor(client_adapter=KrakenClientAdapter(kraken), store=store)
    processor.run()
