import os
from typing import Optional

from bunq.sdk.context.api_context import ApiContext
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, firestore

from functions.bunq_money_flow.src import FireStore, BunqClient, AutomateAllocations

load_dotenv()

GOOGLE_FIRESTORE_CONFIG = os.getenv("GOOGLE_FIRESTORE_CONFIG")

API_CONTEXT_FILE_PATH = os.getenv("BUNQ_FILE_NAME")
API_KEY = os.getenv("BUNQ_API_KEY")

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEVICE_DESCRIPTION = os.getenv("DESCRIPTION")


class ApiContextFileLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save(self, api_context: ApiContext):
        api_context.save(self.file_path)

    def load(self) -> Optional[ApiContext]:
        try:
            return ApiContext.restore(self.file_path)
        except FileNotFoundError:
            return None


if __name__ == "__main__":
    cred = credentials.Certificate(GOOGLE_FIRESTORE_CONFIG)
    initialize_app(cred)
    client = firestore.client()

    store_ = FireStore(client=client)
    bunq_ = BunqClient(
        api_key=API_KEY,
        environment_type=ENVIRONMENT,
        device_description=DEVICE_DESCRIPTION,
        api_context_loader=ApiContextFileLoader(API_CONTEXT_FILE_PATH),
    )
    bunq_.connect()

    AutomateAllocations(bank_client=bunq_, store=store_).run()
