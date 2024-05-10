from dataclasses import dataclass
from typing import Optional

from lib.common_strategies import Flow
from lib.firestore import FireStore


@dataclass
class Order(Flow):
    pair: str
    type: str = None  # buy or sell
    order_type: str = None  # limit, market, etc
    order_priority: Optional[int] = 1

    @property
    def action_label(self):
        return self.type

    @property
    def target_label(self):
        return self.pair


class OrderFlows(FireStore):
    COLLECTION = "order_flows"

    def create_type(self, **kwargs) -> Order:
        return Order(**kwargs)
