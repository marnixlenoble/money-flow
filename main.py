import os

from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, firestore

from functions.bunq_money_flow.src import FireStore, BunqLib, AutomateAllocations

load_dotenv()

GOOGLE_FIRESTORE_CONFIG = os.getenv("GOOGLE_FIRESTORE_CONFIG")

API_CONTEXT_FILE_PATH = os.getenv("BUNQ_FILE_NAME")
API_KEY = os.getenv("BUNQ_API_KEY")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")


if __name__ == "__main__":
    cred = credentials.Certificate(GOOGLE_FIRESTORE_CONFIG)
    initialize_app(cred)
    client = firestore.client()

    store_ = FireStore(client=client)
    bunq_ = BunqLib(
        api_key=API_KEY,
        environment_type=ENVIRONMENT,
        device_description=DEVICE_DESCRIPTION,
        api_context_file_path=API_CONTEXT_FILE_PATH,
    )
    bunq_.connect()

    AutomateAllocations(bunq=bunq_, store=store_).run()
