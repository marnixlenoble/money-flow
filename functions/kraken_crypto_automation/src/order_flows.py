from dataclasses import dataclass

from lib.common_strategies import Flow
from lib.firestore import FireStore


@dataclass
class Order(Flow):
    source_currency: str
    pair: str
    type: str = None  # buy or sell
    order_type: str = None  # limit, market, etc

    @property
    def source(self):
        return self.source_currency

    @property
    def action_label(self):
        return self.type

    @property
    def target_label(self):
        return self.pair


class OrderFlows(FireStore):
    COLLECTION = "crypto_order_flows"

    def create_type(self, **kwargs) -> Order:
        return Order(**kwargs)
