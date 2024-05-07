from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from google.cloud.firestore import Client


@dataclass
class Allocation:
    description: str
    value: Decimal
    type: str
    target_iban: str
    target_iban_name: str
    source_iban: str
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    order: Optional[int] = 1


class FireStore:
    def __init__(self, client: Client):
        self.client = client

    def get_allocations(self):
        data = self.client.collection("allocation").stream()

        def transform_data(doc):
            kwargs: dict = doc.to_dict()
            amount = kwargs.pop("value")
            minimum_amount: Optional[str, Decimal] = kwargs.pop("minimum", None)
            maximum_amount: Optional[str, Decimal] = kwargs.pop("maximum", None)
            if minimum_amount is not None:
                minimum_amount = Decimal(minimum_amount)

            if maximum_amount is not None:
                maximum_amount = Decimal(maximum_amount)

            return Allocation(
                **kwargs,
                value=Decimal(amount),
                minimum_amount=minimum_amount,
                maximum_amount=maximum_amount,
            )

        return list(map(transform_data, data))
