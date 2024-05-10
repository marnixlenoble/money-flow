from dataclasses import dataclass

from lib.common_strategies import Flow
from lib.firestore import FireStore


@dataclass
class Transfer(Flow):
    target_iban: str
    target_iban_name: str
    source_iban: str

    @property
    def target_label(self):
        return self.target_iban_name

    @property
    def action_label(self):
        return "transfer"


class TransferFlows(FireStore):
    COLLECTION = "transfer_flows"

    def create_type(self, **kwargs) -> Transfer:
        return Transfer(**kwargs)
