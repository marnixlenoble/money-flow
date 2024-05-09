from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from google.cloud.firestore import Client


@dataclass
class Order:
    description: str
    pair: str
    value: Decimal
    strategy_type: str

    type: str = None  # buy or sell
    order_type: str = None  # limit, market, etc
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    order_priority: Optional[int] = 1


class FireStore:
    def __init__(self, client: Client):
        self.client = client

    def get_orders(self):
        data = self.client.collection("orders").stream()

        def transform_data(doc):
            kwargs: dict = doc.to_dict()
            value = kwargs.pop("value")

            minimum_amount: Optional[str, Decimal] = kwargs.pop("minimum", None)
            maximum_amount: Optional[str, Decimal] = kwargs.pop("maximum", None)
            if minimum_amount is not None:
                minimum_amount = Decimal(minimum_amount)

            if maximum_amount is not None:
                maximum_amount = Decimal(maximum_amount)

            return Order(
                **kwargs,
                value=Decimal(value),
                minimum_amount=minimum_amount,
                maximum_amount=maximum_amount,
            )

        return list(map(transform_data, data))
