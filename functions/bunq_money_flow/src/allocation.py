from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from google.cloud.firestore import Client


@dataclass
class Allocation:
    description: str
    value: Decimal
    type: str
    iban: str
    iban_name: str
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    order: Optional[int] = None


@dataclass
class Settings:
    minimum: Decimal
    id: int


class FireStore:
    def __init__(self, client: Client):
        self.client = client

    def get_main_account_settings(self):
        data = (
            self.client.collection("settings").document("main_account").get().to_dict()
        )

        return Settings(minimum=Decimal(data.get("minimum")), id=data.get("id"))

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
