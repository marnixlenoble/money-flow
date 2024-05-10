from abc import abstractmethod
from decimal import Decimal
from typing import Optional, Union, TypeVar, List

from google.cloud.firestore import Client

T = TypeVar("T")


class FireStore:
    COLLECTION: str

    def __init__(self, client: Client):
        self.client = client

    @abstractmethod
    def create_type(self, **kwargs) -> T:
        ...

    def get_flows(self) -> List[T]:
        data = self.client.collection(self.COLLECTION).stream()

        def transform_data(doc) -> T:
            kwargs: dict = doc.to_dict()
            value = kwargs.pop("value")

            minimum_amount: Optional[Union[str, Decimal]] = kwargs.pop("minimum", None)
            maximum_amount: Optional[Union[str, Decimal]] = kwargs.pop("maximum", None)
            if minimum_amount is not None:
                minimum_amount = Decimal(minimum_amount)

            if maximum_amount is not None:
                maximum_amount = Decimal(maximum_amount)

            return self.create_type(
                **kwargs,
                value=Decimal(value),
                minimum_amount=minimum_amount,
                maximum_amount=maximum_amount,
            )

        return list(map(transform_data, data))
