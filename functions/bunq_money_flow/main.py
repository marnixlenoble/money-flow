import logging
import os
from typing import Optional

import google_crc32c
from bunq.sdk.context.api_context import ApiContext
from dotenv import load_dotenv
from firebase_admin import initialize_app, firestore
from firebase_functions import scheduler_fn
from firebase_functions.params import StringParam
from google.cloud.secretmanager_v1 import SecretManagerServiceClient

from src import BunqClient, FireStore, AutomateAllocations

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


class ApiContextSecretLoader:
    def __init__(self, project_id: str, secret_name: str, permanent_version: str):
        self.project_id = project_id
        self.secret_name = secret_name
        self.client = SecretManagerServiceClient()
        self.permanent_version = permanent_version

    def _get_secret_version(self, secret_name):
        return self.client.parse_secret_version_path(secret_name).get("secret_version")

    def _delete_previous_versions(self, parent):
        for version in self.client.list_secret_versions(
            request={"parent": parent, "filter": "state:ENABLED"}
        ):
            if self._get_secret_version(version.name) == self.permanent_version:
                logging.info(f"Skipping deletion of permanent version: {version.name}")
                continue

            try:
                logging.info(f"Destroying secret version: {version.name}")
                self.client.destroy_secret_version(request={"name": version.name})
            except Exception as e:
                logging.error(e)

    def save(self, api_context: ApiContext):
        logging.info("Saving api context")
        json_string = api_context.to_json()
        parent = self.client.secret_path(self.project_id, self.secret_name)

        payload_bytes = json_string.encode("UTF-8")
        crc32c = google_crc32c.Checksum()
        crc32c.update(payload_bytes)

        self._delete_previous_versions(parent)
        self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {
                    "data": payload_bytes,
                    "data_crc32c": int(crc32c.hexdigest(), 16),
                },
            }
        )

    def load(self) -> Optional[ApiContext]:
        try:
            name = self.client.secret_version_path(
                self.project_id, self.secret_name, "latest"
            )
            response = self.client.access_secret_version(request={"name": name})

            crc32c = google_crc32c.Checksum()
            crc32c.update(response.payload.data)
            if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
                return None

            payload = response.payload.data.decode("UTF-8")
            return ApiContext.from_json(payload)

        except Exception as e:
            logging.error(e)
            return None


@scheduler_fn.on_schedule(
    schedule="0 12 22-26 * *",
    region=REGION,
    secrets=[BUNQ_API_KEY_SECRET_NAME.value, BUNQ_CONFIG_SECRET_NAME.value],
    ingress="ALLOW_INTERNAL_ONLY",
)
def run_sorter(_event: scheduler_fn.ScheduledEvent):
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
