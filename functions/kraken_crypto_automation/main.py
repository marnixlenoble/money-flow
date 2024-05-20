import logging
import os

from dotenv import load_dotenv
from firebase_admin import initialize_app, firestore
from firebase_functions import scheduler_fn
from firebase_functions.params import StringParam

from lib.flow_processor import FlowProcessor
from src.kraken_client import KrakenClient
from src.kraken_client_adapter import KrakenClientAdapter
from src.order_flows import OrderFlows

load_dotenv()

PROJECT_ID = os.getenv("GCLOUD_PROJECT")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")
REGION = StringParam("REGION")
KRAKEN_API_KEY_SECRET_NAME = StringParam("KRAKEN_API_KEY_SECRET_NAME")
KRAKEN_PRIVATE_KEY_SECRET_NAME = StringParam("KRAKEN_PRIVATE_KEY_SECRET_NAME")

initialize_app()


@scheduler_fn.on_schedule(
    schedule="0 0 28 * *",
    region=REGION,
    secrets=[KRAKEN_API_KEY_SECRET_NAME.value, KRAKEN_PRIVATE_KEY_SECRET_NAME.value],
    ingress="ALLOW_INTERNAL_ONLY",
)
def monthly_sorter(_event: scheduler_fn.ScheduledEvent):
    logging.basicConfig(level=logging.INFO)
    api_key = os.environ.get(KRAKEN_API_KEY_SECRET_NAME.value)
    private_key = os.environ.get(KRAKEN_PRIVATE_KEY_SECRET_NAME.value)
    client = firestore.client()
    store = OrderFlows(client=client)

    kraken = KrakenClient(api_key=api_key, private_key=private_key)

    processor = FlowProcessor(client_adapter=KrakenClientAdapter(kraken), store=store)
    processor.run()
