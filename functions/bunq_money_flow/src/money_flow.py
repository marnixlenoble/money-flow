from decimal import Decimal
from itertools import groupby
from typing import Optional

from .strategies import all_strategies
from .transfer_flow import FireStore, Transfer
from .types import BankClient


class AutomateTransfers:
    def __init__(self, bank_client: BankClient, store: FireStore):
        self.bank_client = bank_client
        self.store = store

    def run(self):
        flows_all = self.store.get_transfer_flows()
        flows_by_source = groupby(flows_all, key=lambda x: x.source_iban)

        for source_iban, group in flows_by_source:
            remainder = self.bank_client.get_balance_by_iban(iban=source_iban)
            flows_per_source = list(group)
            flows_per_source.sort(key=lambda x: x.priority)
            grouped_flows = groupby(flows_per_source, key=lambda x: x.priority)

            for _, group_ in grouped_flows:
                flows = list(group_)
                for flow in filter(lambda a: a.type != "percentage", flows):
                    remainder = self._process_transfer_flow(flow, remainder)

                original_remainder = remainder
                for flow in filter(lambda a: a.type == "percentage", flows):
                    remainder = self._process_transfer_flow(
                        flow,
                        remainder,
                        original_remainder=original_remainder,
                    )

    def _process_transfer_flow(
        self,
        transfer_flow: Transfer,
        remainder: Decimal,
        *,
        original_remainder: Optional[Decimal] = None,
    ):
        strategy = all_strategies.get(transfer_flow.type)
        amount = strategy(
            transfer_flow,
            original_remainder if original_remainder else remainder,
            bank_client=self.bank_client,
        )
        if amount > 0 and transfer_flow.target_iban != transfer_flow.source_iban:
            self.bank_client.make_payment(
                amount=amount,
                description=transfer_flow.description,
                target_iban=transfer_flow.target_iban,
                target_iban_name=transfer_flow.target_iban_name,
                source_iban=transfer_flow.source_iban,
            )

        return remainder - amount
