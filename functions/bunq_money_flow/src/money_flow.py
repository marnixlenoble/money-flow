from decimal import Decimal
from itertools import groupby
from typing import Optional

from .allocation import FireStore, Allocation
from .strategies import all_strategies
from .types import BankClient


class AutomateAllocations:
    def __init__(self, bank_client: BankClient, store: FireStore):
        self.bank_client = bank_client
        self.store = store

    def run(self):
        allocations_all = self.store.get_allocations()
        allocations_by_source = groupby(allocations_all, key=lambda x: x.source_iban)

        for source_iban, group in allocations_by_source:
            remainder = self.bank_client.get_balance_by_iban(iban=source_iban)
            allocations_per_source = list(group)
            allocations_per_source.sort(key=lambda x: x.order)
            grouped_allocations = groupby(allocations_per_source, key=lambda x: x.order)

            for _, group_ in grouped_allocations:
                allocations = list(group_)
                for allocation in filter(lambda a: a.type != "percentage", allocations):
                    remainder = self._process_allocation(allocation, remainder)

                original_remainder = remainder
                for allocation in filter(lambda a: a.type == "percentage", allocations):
                    remainder = self._process_allocation(
                        allocation,
                        remainder,
                        original_remainder=original_remainder,
                    )

    def _process_allocation(
        self,
        allocation: Allocation,
        remainder: Decimal,
        *,
        original_remainder: Optional[Decimal] = None,
    ):
        strategy = all_strategies.get(allocation.type)
        amount = strategy(
            allocation,
            original_remainder if original_remainder else remainder,
            bank_client=self.bank_client,
        )
        if amount > 0 and allocation.target_iban != allocation.source_iban:
            self.bank_client.make_payment(
                amount=amount,
                description=allocation.description,
                target_iban=allocation.target_iban,
                target_iban_name=allocation.target_iban_name,
                source_iban=allocation.source_iban,
            )

        return remainder - amount
