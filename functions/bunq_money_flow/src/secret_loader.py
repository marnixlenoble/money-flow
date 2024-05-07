import logging
from typing import Optional

import google_crc32c
from bunq.sdk.context.api_context import ApiContext
from google.cloud.secretmanager_v1 import SecretManagerServiceClient


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
