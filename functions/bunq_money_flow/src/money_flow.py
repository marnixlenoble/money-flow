from itertools import groupby

from .allocation import FireStore
from .bunq_lib import BunqLib
from .strategies import all_strategies


class AutomateAllocations:
    def __init__(self, bunq: BunqLib, store: FireStore):
        self.bunq = bunq
        self.store = store

    def run(self):
        allocations = self.store.get_allocations()
        grouped_allocations = groupby(allocations, key=lambda x: x.order)

        main_account_settings = self.store.get_main_account_settings()
        cutoff = main_account_settings.minimum
        main_account_balance = self.bunq.get_balance_by_id(id_=main_account_settings.id)
        if main_account_balance < cutoff:
            return

        remainder = main_account_balance - cutoff

        for _, group in grouped_allocations:
            allocations = list(group)
            for allocation in filter(lambda a: a.type != "percentage", allocations):
                remainder = self._process_allocation(
                    allocation, main_account_settings, remainder
                )

            original_remainder = remainder
            for allocation in filter(lambda a: a.type == "percentage", allocations):
                remainder = self._process_allocation(
                    allocation,
                    main_account_settings,
                    remainder,
                    original_remainder=original_remainder,
                )

    def _process_allocation(
        self, allocation, main_account_settings, remainder, *, original_remainder=None
    ):
        strategy = all_strategies.get(allocation.type)
        amount = strategy(
            allocation,
            original_remainder if original_remainder else remainder,
            bunq=self.bunq,
        )
        if amount > 0:
            self.bunq.make_payment(
                amount=amount,
                description=allocation.description,
                iban=allocation.iban,
                iban_name=allocation.iban_name,
                account_id=main_account_settings.id,
            )
            remainder -= amount
        return remainder
