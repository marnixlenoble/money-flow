from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union

from google.cloud.firestore import Client

from lib.common_strategies import Flow


@dataclass
class Transfer(Flow):
    target_iban: str
    target_iban_name: str
    source_iban: str

    def target(self):
        return self.target_iban_name

    def action_label(self):
        return "transfer"


class FireStore:
    def __init__(self, client: Client):
        self.client = client

    def get_transfer_flows(self):
        data = self.client.collection("transfer_flows").stream()

        def transform_data(doc):
            kwargs: dict = doc.to_dict()
            amount = kwargs.pop("value")
            minimum_amount: Optional[Union[str, Decimal]] = kwargs.pop("minimum", None)
            maximum_amount: Optional[Union[str, Decimal]] = kwargs.pop("maximum", None)
            if minimum_amount is not None:
                minimum_amount = Decimal(minimum_amount)

            if maximum_amount is not None:
                maximum_amount = Decimal(maximum_amount)

            return Transfer(
                **kwargs,
                value=Decimal(amount),
                minimum_amount=minimum_amount,
                maximum_amount=maximum_amount,
            )

        return list(map(transform_data, data))
