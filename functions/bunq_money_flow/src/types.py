from decimal import Decimal
from typing import Optional, Protocol


class BankClient(Protocol):
    def make_payment(
        self,
        *,
        amount: Decimal,
        description: str,
        target_iban: str,
        target_iban_name: str,
        source_iban: str,
    ) -> None:
        ...

    def get_balance_by_iban(self, *, iban: str) -> Optional[Decimal]:
        ...
