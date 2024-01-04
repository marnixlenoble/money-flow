from decimal import Decimal
from typing import Optional

from .allocation import Allocation
from .bunq_lib import BunqLib


def _check_minimum_amount(
    amount: Decimal, *, minimum_amount: Optional[Decimal]
) -> Decimal:
    if amount > (minimum_amount if minimum_amount else 0):
        return amount
    else:
        return Decimal(0)


def _check_maximum_amount(
    amount: Decimal, *, maximum_amount: Optional[Decimal]
) -> Decimal:
    if maximum_amount is not None:
        return min(amount, maximum_amount)
    else:
        return amount


def _check_remainder(amount: Decimal, *, remainder: Decimal) -> Decimal:
    return min(amount, remainder)


def top_up_strategy(
    allocation: Allocation, remainder: Decimal, *, bunq: BunqLib
) -> Decimal:
    balance = bunq.get_balance_by_iban(iban=allocation.iban)
    amount = allocation.value - balance
    amount = _check_remainder(amount, remainder=remainder)
    amount = _check_minimum_amount(amount, minimum_amount=allocation.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=allocation.maximum_amount)

    return amount


def fixed_strategy(allocation: Allocation, remainder: Decimal, *_, **__) -> Decimal:
    amount = allocation.value
    amount = _check_remainder(amount, remainder=remainder)
    amount = _check_minimum_amount(amount, minimum_amount=allocation.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=allocation.maximum_amount)

    return amount


def percentage_strategy(
    allocation: Allocation, remainder: Decimal, *_, **__
) -> Decimal:
    amount = round(remainder * (allocation.value / 100), 2)
    amount = _check_minimum_amount(amount, minimum_amount=allocation.minimum_amount)
    amount = _check_maximum_amount(amount, maximum_amount=allocation.maximum_amount)

    return amount


all_strategies = dict(
    top_up=top_up_strategy,
    fixed=fixed_strategy,
    percentage=percentage_strategy,
)
