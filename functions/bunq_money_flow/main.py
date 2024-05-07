import logging
import os

from dotenv import load_dotenv
from firebase_admin import initialize_app, firestore
from firebase_functions import scheduler_fn
from firebase_functions.params import StringParam

from src import BunqClient, FireStore, AutomateAllocations, ApiContextSecretLoader

load_dotenv()

PROJECT_ID = os.getenv("GCLOUD_PROJECT")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")

BUNQ_CONFIG_SECRET_NAME = StringParam("BUNQ_CONFIG_SECRET_NAME")
BUNQ_API_KEY_SECRET_NAME = StringParam("BUNQ_API_KEY_SECRET_NAME")
BUNQ_CONFIG_SECRET_PERMANENT_VERSION = StringParam(
    "BUNQ_CONFIG_SECRET_PERMANENT_VERSION"
)
REGION = StringParam("REGION")

initialize_app()



@scheduler_fn.on_schedule(
    schedule="0 0 26 * *",
    region=REGION,
    secrets=[BUNQ_API_KEY_SECRET_NAME.value, BUNQ_CONFIG_SECRET_NAME.value],
    ingress="ALLOW_INTERNAL_ONLY",
)
def monthly_sorter(_event: scheduler_fn.ScheduledEvent):
    logging.basicConfig(level=logging.INFO)
    api_key = os.environ.get(BUNQ_API_KEY_SECRET_NAME.value)
    client = firestore.client()
    store_ = FireStore(client=client)

    bunq_ = BunqClient(
        api_key=api_key,
        environment_type=ENVIRONMENT,
        device_description=DEVICE_DESCRIPTION,
        api_context_loader=ApiContextSecretLoader(
            PROJECT_ID,
            BUNQ_CONFIG_SECRET_NAME.value,
            BUNQ_CONFIG_SECRET_PERMANENT_VERSION.value,
        ),
    )
    bunq_.connect()

    AutomateAllocations(bank_client=bunq_, store=store_).run()
