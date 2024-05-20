from decimal import Decimal

from lib.flow_processor import ClientAdapter
from .kraken_client import KrakenClient
from .order_flows import Order


class KrakenClientAdapter(ClientAdapter):
    def __init__(self, kraken: KrakenClient):
        self.kraken = kraken

    def handle_processed_flow(self, flow: Order, amount: Decimal) -> None:
        if flow.source_currency != flow.pair:
            self.kraken.add_limit_order(
                pair=flow.pair,
                amount=amount,
                type="buy",
            )

    def get_balance(self, source: str) -> Decimal:
        return self.kraken.get_balance(source)
