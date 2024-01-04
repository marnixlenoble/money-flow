import os

from dotenv import load_dotenv
from firebase_admin import initialize_app, firestore
from firebase_functions import scheduler_fn

from src import BunqLib, FireStore, AutomateAllocations

load_dotenv()

API_CONTEXT_FILE_PATH = os.getenv("BUNQ_FILE_NAME")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")

initialize_app()


@scheduler_fn.on_schedule(
    schedule="0 12 22-26 * *", region="europe-west1", secrets=["BUNQ_API_KEY"]
)
def run_sorter(_event: scheduler_fn.ScheduledEvent):
    api_key = os.environ.get("BUNQ_API_KEY")
    client = firestore.client()
    store_ = FireStore(client=client)

    bunq_ = BunqLib(
        api_key=api_key,
        environment_type=ENVIRONMENT,
        device_description=DEVICE_DESCRIPTION,
        api_context_file_path=API_CONTEXT_FILE_PATH,
    )
    bunq_.connect()

    AutomateAllocations(bunq=bunq_, store=store_).run()

    os.remove(API_CONTEXT_FILE_PATH)
