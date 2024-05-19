from decimal import Decimal

from lib.flow_processor import ClientAdapter
from .strategies import top_up_strategy
from .transfer_flows import Transfer
from .types import BankClient


class BankClientAdapter(ClientAdapter):
    def __init__(self, bank_client: BankClient):
        self.bank_client = bank_client

    @property
    def strategies(self):
        return {
            "top_up": lambda flow, remainder: top_up_strategy(
                flow, remainder, self.bank_client
            )
        }

    def handle_processed_flow(self, flow: Transfer, amount: Decimal) -> None:
        if flow.target_iban != flow.source_iban:
            self.bank_client.make_payment(
                amount=amount,
                description=flow.description,
                target_iban=flow.target_iban,
                target_iban_name=flow.target_iban_name,
                source_iban=flow.source_iban,
            )

    def get_balance(self, source: str) -> Decimal:
        return self.bank_client.get_balance_by_iban(iban=source)
